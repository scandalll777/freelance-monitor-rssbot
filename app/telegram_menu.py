from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from app.filter_presets import FILTER_PRESETS
from app.filter_settings import FilterDraft
from app.i18n import preset_label, t
from app.locale import (
    get_language,
    needs_language_selection,
    set_language,
)
from app.source_settings import source_label
from app.telegram_api import TelegramApi

if TYPE_CHECKING:
    from app.monitor import FlMonitor

logger = logging.getLogger(__name__)

DEFAULT_ONBOARDING_PRESETS = frozenset({"ai", "vibe_coding"})


class TelegramMenuBot:
    """Filter settings menu and first-run onboarding via /start."""

    def __init__(
        self,
        api: TelegramApi,
        allowed_chat_id: str,
        base_dir: Path,
        on_apply: Callable[[FilterDraft, bool], str] | None = None,
        *,
        needs_onboarding: Callable[[], bool] | None = None,
        on_onboarding_complete: Callable[[FilterDraft, str], str] | None = None,
    ) -> None:
        self._api = api
        self._allowed_chat_id = str(allowed_chat_id)
        self._base_dir = base_dir
        self._on_apply = on_apply
        self._needs_onboarding = needs_onboarding
        self._on_onboarding_complete = on_onboarding_complete
        self._draft = FilterDraft.from_yaml()
        self._waiting: str | None = None
        self._onboarding = False
        self._offset = 0
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def _lang(self) -> str:
        return get_language(self._base_dir)

    def _tr(self, key: str, **kwargs) -> str:
        return t(self._lang(), key, **kwargs)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        try:
            self._api._call("deleteWebhook", drop_pending_updates=False)
        except Exception:
            logger.warning("Could not reset Telegram webhook")
        self._thread = threading.Thread(
            target=self._poll_loop, name="telegram-menu", daemon=True
        )
        self._thread.start()
        logger.info("Telegram menu started (/start, /menu, /language)")

    def prompt_onboarding(self, chat_id: int | str) -> None:
        if not self._is_onboarding_required() and not needs_language_selection(
            self._base_dir
        ):
            return
        if needs_language_selection(self._base_dir):
            self._send_language_picker(int(chat_id))
            return
        self._onboarding = True
        self._draft = self._fresh_onboarding_draft()
        self._send_onboarding_step1(int(chat_id))

    def stop(self) -> None:
        self._stop.set()

    def _authorized(self, chat_id: int | str) -> bool:
        return str(chat_id) == self._allowed_chat_id

    def _is_onboarding_required(self) -> bool:
        return bool(self._needs_onboarding and self._needs_onboarding())

    def _fresh_onboarding_draft(self) -> FilterDraft:
        draft = FilterDraft.from_yaml()
        if not draft.preset_ids:
            draft.preset_ids = set(DEFAULT_ONBOARDING_PRESETS)
        return draft

    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                updates = self._api.get_updates(self._offset, timeout=25)
                for update in updates:
                    try:
                        self._handle_update(update)
                    except Exception:
                        logger.exception(
                            "Error handling update %s", update.get("update_id")
                        )
                    finally:
                        self._offset = update["update_id"] + 1
            except Exception:
                logger.exception("Telegram polling error")
                self._stop.wait(3)

    def _handle_update(self, update: dict) -> None:
        if "callback_query" in update:
            self._handle_callback(update["callback_query"])
            return
        message = update.get("message")
        if not message:
            return
        chat_id = message["chat"]["id"]
        if not self._authorized(chat_id):
            logger.warning(
                "Message from unknown chat_id=%s (expected %s)",
                chat_id,
                self._allowed_chat_id,
            )
            return
        text = (message.get("text") or "").strip()
        if text.startswith("/"):
            cmd = text.split()[0].split("@")[0].lower()
            if cmd == "/start":
                self._waiting = None
                logger.info("/start from chat_id=%s", chat_id)
                self._handle_start(chat_id)
            elif cmd in ("/menu", "/help"):
                self._waiting = None
                self._onboarding = False
                self._send_main_menu(chat_id)
            elif cmd == "/language":
                self._waiting = None
                self._onboarding = False
                self._send_language_picker(chat_id)
            return
        if self._waiting:
            self._handle_text_input(chat_id, text)

    def _handle_start(self, chat_id: int) -> None:
        if needs_language_selection(self._base_dir):
            self._send_language_picker(chat_id)
            return
        if self._is_onboarding_required():
            self._onboarding = True
            self._draft = self._fresh_onboarding_draft()
            self._send_onboarding_step1(chat_id)
        else:
            self._onboarding = False
            self._send_main_menu(chat_id)

    def _language_keyboard(self) -> dict:
        return {
            "inline_keyboard": [
                [
                    {"text": self._tr("btn_lang_en"), "callback_data": "l:en"},
                    {"text": self._tr("btn_lang_ru"), "callback_data": "l:ru"},
                ]
            ]
        }

    def _send_language_picker(self, chat_id: int) -> None:
        try:
            self._api.send_message(
                chat_id,
                self._tr("language_title"),
                reply_markup=self._language_keyboard(),
            )
        except Exception:
            logger.exception("Could not send language picker")
            self._api.send_message(
                chat_id,
                "Choose language / Выберите язык",
                parse_mode=None,
                reply_markup=self._language_keyboard(),
            )

    def _after_language_selected(self, chat_id: int, message_id: int | None = None) -> None:
        if self._is_onboarding_required():
            self._onboarding = True
            self._draft = self._fresh_onboarding_draft()
            text = self._onboarding_step1_text()
            keyboard = self._onboarding_step1_keyboard()
        else:
            self._onboarding = False
            self._draft = FilterDraft.from_yaml()
            text = self._main_text()
            keyboard = self._main_keyboard()
        if message_id is not None:
            self._api.edit_message(chat_id, message_id, text, reply_markup=keyboard)
        else:
            self._api.send_message(chat_id, text, reply_markup=keyboard)

    def _send_onboarding_step1(self, chat_id: int) -> None:
        text = self._onboarding_step1_text()
        keyboard = self._onboarding_step1_keyboard()
        try:
            self._api.send_message(chat_id, text, reply_markup=keyboard)
        except Exception:
            logger.exception("HTML message failed, trying plain text")
            self._api.send_message(
                chat_id,
                self._tr("onboarding_plain"),
                parse_mode=None,
                reply_markup=keyboard,
            )

    def _send_main_menu(self, chat_id: int) -> None:
        self._draft = FilterDraft.from_yaml()
        try:
            self._api.send_message(
                chat_id, self._main_text(), reply_markup=self._main_keyboard()
            )
        except Exception:
            logger.exception("Could not send menu")
            self._api.send_message(
                chat_id,
                self._tr("help_menu"),
                parse_mode=None,
                reply_markup=self._main_keyboard(),
            )

    def _handle_callback(self, query: dict) -> None:
        chat_id = query["message"]["chat"]["id"]
        if not self._authorized(chat_id):
            self._api.answer_callback(query["id"], self._tr("access_denied"))
            return

        data = query.get("data", "")
        message_id = query["message"]["message_id"]

        try:
            if data.startswith("l:"):
                lang_code = data[2:]
                set_language(self._base_dir, lang_code)
                saved = self._tr(
                    "language_saved_ru" if lang_code == "ru" else "language_saved_en"
                )
                self._api.answer_callback(query["id"], saved, show_alert=False)
                self._after_language_selected(chat_id, message_id)
            elif data.startswith("o:"):
                self._handle_onboarding_callback(chat_id, message_id, data)
            elif data == "m:lang":
                self._waiting = None
                self._api.edit_message(
                    chat_id,
                    message_id,
                    self._tr("language_title"),
                    reply_markup=self._language_keyboard(),
                )
            elif data == "m:main":
                self._waiting = None
                self._onboarding = False
                self._edit_main_menu(chat_id, message_id)
            elif data == "m:cat":
                self._waiting = None
                self._edit_categories(chat_id, message_id)
            elif data == "m:sources":
                self._waiting = None
                self._edit_sources(chat_id, message_id)
            elif data.startswith("s:"):
                source_id = data[2:]
                self._draft.toggle_source(source_id)
                if self._onboarding:
                    self._edit_onboarding_step1(chat_id, message_id)
                else:
                    self._edit_sources(chat_id, message_id)
            elif data.startswith("t:"):
                preset_id = data[2:]
                self._draft.toggle_preset(preset_id)
                if self._onboarding:
                    self._edit_onboarding_step1(chat_id, message_id)
                else:
                    self._edit_categories(chat_id, message_id)
            elif data == "m:budget":
                self._waiting = "budget"
                self._api.edit_message(
                    chat_id,
                    message_id,
                    self._tr("budget_title", value=self._draft.min_budget),
                    reply_markup=self._back_keyboard(),
                )
            elif data == "m:kw_inc":
                self._waiting = "kw_inc"
                words = ", ".join(self._draft.keywords_include) or "—"
                self._api.edit_message(
                    chat_id,
                    message_id,
                    self._tr("keywords_title", words=words),
                    reply_markup=self._back_keyboard(),
                )
            elif data == "m:kw_exc":
                self._waiting = "kw_exc"
                words = ", ".join(self._draft.keywords_exclude) or "—"
                self._api.edit_message(
                    chat_id,
                    message_id,
                    self._tr("exclude_title", words=words),
                    reply_markup=self._back_keyboard(),
                )
            elif data == "m:show":
                self._waiting = None
                self._api.edit_message(
                    chat_id,
                    message_id,
                    self._draft.summary_html(self._lang()),
                    reply_markup=self._back_keyboard(),
                )
            elif data == "a:save":
                self._waiting = None
                self._apply(chat_id, message_id, reset_db=False)
            elif data == "a:reset":
                self._waiting = None
                self._apply(chat_id, message_id, reset_db=True)
            else:
                self._api.answer_callback(query["id"])
                return
            if not data.startswith("l:"):
                self._api.answer_callback(query["id"])
        except Exception:
            logger.exception("Callback error")
            self._api.answer_callback(query["id"], self._tr("error"))

    def _handle_onboarding_callback(
        self, chat_id: int, message_id: int, data: str
    ) -> None:
        if data == "o:step1":
            self._edit_onboarding_step1(chat_id, message_id)
        elif data == "o:step2":
            err = self._validate_draft()
            if err:
                self._api.edit_message(
                    chat_id, message_id, err, reply_markup=self._onboarding_step1_keyboard()
                )
                return
            self._edit_onboarding_step2(chat_id, message_id)
        elif data == "o:finish:seed":
            self._complete_onboarding(chat_id, message_id, "seed")
        elif data == "o:finish:current":
            self._complete_onboarding(chat_id, message_id, "current")

    def _validate_draft(self) -> str | None:
        enabled_sources = [
            sid
            for sid in self._draft.configured_sources()
            if self._draft.is_source_enabled(sid)
        ]
        if not enabled_sources:
            return self._tr("validate_no_sources")
        if (
            self._draft.is_source_enabled("fl_ru")
            and "fl_ru" in self._draft.configured_sources()
            and not self._draft.preset_ids
        ):
            return self._tr("validate_no_categories")
        return None

    def _complete_onboarding(
        self, chat_id: int, message_id: int, mode: str
    ) -> None:
        err = self._validate_draft()
        if err:
            self._api.edit_message(
                chat_id, message_id, err, reply_markup=self._onboarding_step1_keyboard()
            )
            return
        if not self._on_onboarding_complete:
            return
        try:
            extra = self._on_onboarding_complete(self._draft, mode)
            self._onboarding = False
            text = self._tr(
                "onboarding_done",
                summary=self._draft.summary_html(self._lang()),
                extra=extra,
            )
            self._api.edit_message(
                chat_id, message_id, text, reply_markup=self._main_keyboard()
            )
        except Exception:
            logger.exception("Onboarding completion failed")
            self._api.edit_message(
                chat_id,
                message_id,
                self._tr("onboarding_failed"),
                reply_markup=self._onboarding_step2_keyboard(),
            )

    def _onboarding_step1_text(self) -> str:
        return self._tr(
            "onboarding_step1",
            summary=self._draft.summary_html(self._lang()),
        )

    def _onboarding_step2_text(self) -> str:
        return self._tr("onboarding_step2")

    def _onboarding_step1_keyboard(self) -> dict:
        return {
            "inline_keyboard": [
                [
                    {"text": self._tr("btn_categories"), "callback_data": "m:cat"},
                    {"text": self._tr("btn_sources"), "callback_data": "m:sources"},
                ],
                [{"text": self._tr("btn_next"), "callback_data": "o:step2"}],
            ]
        }

    def _onboarding_step2_keyboard(self) -> dict:
        return {
            "inline_keyboard": [
                [{"text": self._tr("btn_only_new"), "callback_data": "o:finish:seed"}],
                [
                    {
                        "text": self._tr("btn_send_current"),
                        "callback_data": "o:finish:current",
                    }
                ],
                [{"text": self._tr("btn_back_filters"), "callback_data": "o:step1"}],
            ]
        }

    def _edit_onboarding_step1(self, chat_id: int, message_id: int) -> None:
        self._onboarding = True
        self._api.edit_message(
            chat_id,
            message_id,
            self._onboarding_step1_text(),
            reply_markup=self._onboarding_step1_keyboard(),
        )

    def _edit_onboarding_step2(self, chat_id: int, message_id: int) -> None:
        self._api.edit_message(
            chat_id,
            message_id,
            self._onboarding_step2_text(),
            reply_markup=self._onboarding_step2_keyboard(),
        )

    def _handle_text_input(self, chat_id: int, text: str) -> None:
        if self._waiting == "budget":
            try:
                value = int(text.replace(" ", ""))
                if value < 0:
                    raise ValueError
                self._draft.min_budget = value
                self._waiting = None
                msg = (
                    self._tr("budget_any")
                    if not value
                    else self._tr("budget_saved", value=value)
                )
                self._api.send_message(chat_id, msg, reply_markup=self._main_keyboard())
            except ValueError:
                self._api.send_message(chat_id, self._tr("budget_invalid"))
            return

        words = self._parse_words(text)
        if self._waiting == "kw_inc":
            self._draft.keywords_include = [] if text.strip() == "-" else words
            self._waiting = None
            self._api.send_message(
                chat_id,
                self._tr("keywords_saved"),
                reply_markup=self._main_keyboard(),
            )
        elif self._waiting == "kw_exc":
            self._draft.keywords_exclude = [] if text.strip() == "-" else words
            self._waiting = None
            self._api.send_message(
                chat_id,
                self._tr("exclude_saved"),
                reply_markup=self._main_keyboard(),
            )

    def _parse_words(self, text: str) -> list[str]:
        parts = []
        for chunk in text.replace(";", ",").split(","):
            word = chunk.strip()
            if word:
                parts.append(word.lower())
        return parts

    def _apply(self, chat_id: int, message_id: int, *, reset_db: bool) -> None:
        err = self._validate_draft()
        if err:
            self._api.edit_message(
                chat_id, message_id, err, reply_markup=self._main_keyboard()
            )
            return

        try:
            self._draft.save()
            extra = ""
            if self._on_apply:
                extra = self._on_apply(self._draft, reset_db)
            text = self._tr(
                "apply_saved",
                summary=self._draft.summary_html(self._lang()),
                extra=f"\n\n{extra}" if extra else "",
            )
            self._api.edit_message(
                chat_id, message_id, text, reply_markup=self._main_keyboard()
            )
        except Exception:
            logger.exception("Could not apply filters")
            self._api.edit_message(
                chat_id,
                message_id,
                self._tr("apply_failed"),
                reply_markup=self._main_keyboard(),
            )

    def _main_keyboard(self) -> dict:
        return {
            "inline_keyboard": [
                [
                    {"text": self._tr("btn_sources"), "callback_data": "m:sources"},
                    {"text": self._tr("btn_categories"), "callback_data": "m:cat"},
                ],
                [{"text": self._tr("btn_budget"), "callback_data": "m:budget"}],
                [
                    {"text": self._tr("btn_keywords"), "callback_data": "m:kw_inc"},
                    {"text": self._tr("btn_exclude"), "callback_data": "m:kw_exc"},
                ],
                [{"text": self._tr("btn_show"), "callback_data": "m:show"}],
                [{"text": self._tr("btn_apply"), "callback_data": "a:save"}],
                [{"text": self._tr("btn_apply_reset"), "callback_data": "a:reset"}],
                [{"text": self._tr("btn_language"), "callback_data": "m:lang"}],
            ]
        }

    def _back_keyboard(self) -> dict:
        return {
            "inline_keyboard": [[{"text": self._tr("btn_back_menu"), "callback_data": "m:main"}]]
        }

    def _sources_keyboard(self) -> dict:
        rows = []
        for source_id in self._draft.configured_sources():
            mark = "✅" if self._draft.is_source_enabled(source_id) else "⬜"
            rows.append(
                [
                    {
                        "text": f"{mark} {source_label(source_id)}",
                        "callback_data": f"s:{source_id}",
                    }
                ]
            )
        if not rows:
            rows.append(
                [
                    {
                        "text": self._tr("no_sources"),
                        "callback_data": "m:main",
                    }
                ]
            )
        back = "o:step1" if self._onboarding else "m:main"
        rows.append([{"text": self._tr("btn_back"), "callback_data": back}])
        return {"inline_keyboard": rows}

    def _categories_keyboard(self) -> dict:
        lang = self._lang()
        rows = []
        for item in FILTER_PRESETS:
            mark = "✅" if item.id in self._draft.preset_ids else "⬜"
            label = preset_label(lang, item.id, item.label)
            rows.append(
                [
                    {
                        "text": f"{mark} {label}",
                        "callback_data": f"t:{item.id}",
                    }
                ]
            )
        back = "o:step1" if self._onboarding else "m:main"
        rows.append([{"text": self._tr("btn_back"), "callback_data": back}])
        return {"inline_keyboard": rows}

    def _main_text(self) -> str:
        return self._tr(
            "main_menu",
            summary=self._draft.summary_html(self._lang()),
        )

    def _edit_main_menu(self, chat_id: int, message_id: int) -> None:
        self._api.edit_message(
            chat_id,
            message_id,
            self._main_text(),
            reply_markup=self._main_keyboard(),
        )

    def _edit_categories(self, chat_id: int, message_id: int) -> None:
        title = (
            self._tr("categories_onboarding")
            if self._onboarding
            else self._tr("categories_title")
        )
        self._api.edit_message(
            chat_id, message_id, title, reply_markup=self._categories_keyboard()
        )

    def _edit_sources(self, chat_id: int, message_id: int) -> None:
        title = (
            self._tr("sources_onboarding")
            if self._onboarding
            else self._tr("sources_title")
        )
        self._api.edit_message(
            chat_id, message_id, title, reply_markup=self._sources_keyboard()
        )


def create_menu_handlers(monitor: FlMonitor, base_dir) -> tuple:
    from app.config import load_config
    from app.setup_state import is_setup_complete, mark_setup_complete

    base = Path(base_dir)

    def on_apply(draft: FilterDraft, reset_db: bool) -> str:
        monitor.reload_config(load_config(base))
        lang = get_language(base)
        if reset_db:
            count = monitor.reset_and_seed()
            mark_setup_complete(base)
            return t(lang, "apply_reset_extra", count=count)
        return t(lang, "apply_extra")

    def needs_onboarding() -> bool:
        return not is_setup_complete(base)

    def on_onboarding_complete(draft: FilterDraft, mode: str) -> str:
        draft.save()
        monitor.reload_config(load_config(base))
        lang = get_language(base)
        if mode == "current":
            count = monitor.reset_and_notify_current()
            mark_setup_complete(base)
            return t(lang, "finish_current", count=count)
        count = monitor.reset_and_seed()
        mark_setup_complete(base)
        return t(lang, "finish_seed", count=count)

    return on_apply, needs_onboarding, on_onboarding_complete


def create_menu_apply_handler(monitor: FlMonitor, base_dir):
    return create_menu_handlers(monitor, base_dir)[0]

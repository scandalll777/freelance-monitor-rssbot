from __future__ import annotations

import logging

from app.i18n import t
from app.project import Project, is_foreign_source
from app.telegram_api import TelegramApi
from app.translator import localize_project_text

logger = logging.getLogger(__name__)


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class TelegramNotifier:
    def __init__(
        self,
        token: str,
        chat_id: str,
        proxy: str | None = None,
        *,
        translate_foreign: bool = True,
        lang: str = "en",
    ) -> None:
        self._chat_id = chat_id
        self._api = TelegramApi(token, proxy)
        self.translate_foreign = translate_foreign
        self.lang = lang

    def format_project(
        self, project: Project, description_preview_length: int = 200
    ) -> str:
        lang = self.lang
        tr = self.translate_foreign and lang == "ru"
        title = localize_project_text(
            project.source, project.title, enabled=tr, lang=lang
        )
        category = localize_project_text(
            project.source, project.category, enabled=tr, lang=lang
        )
        deadline = localize_project_text(
            project.source, project.deadline, enabled=tr, lang=lang
        )

        lines = [
            f"🆕 <b>{t(lang, 'notify_new_project')} {_escape_html(project.source_label)}</b>",
        ]
        if tr and is_foreign_source(project.source):
            lines.append(f"🌐 <i>{t(lang, 'notify_auto_translate')}</i>")
        lines.extend(
            [
                "",
                f"📌 <b>{_escape_html(title)}</b>",
                f"💰 <b>{t(lang, 'notify_budget')}:</b> {_escape_html(project.budget_text)}",
                f"⏱ <b>{t(lang, 'notify_deadline')}:</b> {_escape_html(deadline)}",
                f"📂 <b>{t(lang, 'notify_category')}:</b> {_escape_html(category)}",
            ]
        )
        if project.published_at:
            lines.append(
                f"🕐 <b>{t(lang, 'notify_published')}:</b> {_escape_html(project.published_at)}"
            )
        if description_preview_length > 0 and project.description:
            preview = project.description[:description_preview_length].strip()
            if len(project.description) > description_preview_length:
                preview += "…"
            preview = localize_project_text(
                project.source, preview, enabled=tr, lang=lang
            )
            lines.extend(["", f"<i>{_escape_html(preview)}</i>"])
        lines.extend(
            ["", f'🔗 <a href="{project.url}">{t(lang, "notify_open")}</a>']
        )
        return "\n".join(lines)

    def notify_project(
        self, project: Project, description_preview_length: int = 200
    ) -> None:
        text = self.format_project(project, description_preview_length)
        logger.info("Отправка в Telegram: %s (%s)", project.title, project.url)
        self.send_message(text)

    def notify_text(self, text: str) -> None:
        self.send_message(text, disable_preview=True)

    def send_message(self, text: str, disable_preview: bool = False) -> None:
        self._api.send_message(
            self._chat_id,
            text,
            disable_preview=disable_preview,
        )


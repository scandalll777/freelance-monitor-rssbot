from __future__ import annotations

import logging
import threading

from pathlib import Path

from app.config import AppConfig
from app.i18n import t
from app.locale import get_language
from app.setup_state import is_setup_complete, mark_setup_complete
from app.sources.registry import collect_from_feeds
from app.storage import ProjectStorage
from app.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

# Защита от спама: не слать десятки объявлений за один опрос
MAX_NOTIFICATIONS_PER_POLL = 5
BACKLOG_SEED_THRESHOLD = 8


def _format_interval(seconds: int, lang: str = "en") -> str:
    if seconds < 60:
        return f"{seconds}s" if lang == "en" else f"{seconds} сек."
    minutes = seconds // 60
    if seconds % 60:
        if lang == "en":
            return f"{minutes} min {seconds % 60} sec"
        return f"{minutes} мин. {seconds % 60} сек."
    return f"{minutes} min" if lang == "en" else f"{minutes} мин."


class FlMonitor:
    def __init__(self, config: AppConfig, base_dir: Path | None = None) -> None:
        self._lock = threading.Lock()
        self._config = config
        self._base_dir = base_dir or config.db_path.parent.parent
        self._storage = ProjectStorage(config.db_path)
        self._notifier = TelegramNotifier(
            config.telegram_token,
            config.telegram_chat_id,
            config.telegram_proxy,
            translate_foreign=config.translate_foreign,
            lang=get_language(self._base_dir),
        )
        self._feeds = config.filters.feeds
        known = self._storage.count()
        logger.info("База заказов: %s (%s записей)", config.db_path, known)
        if known > 0:
            logger.info(
                "Режим: только новые объявления (опрос каждые %s)",
                _format_interval(config.check_interval_seconds),
            )
        elif config.initial_seed:
            logger.info(
                "Первый запуск: текущие заказы запомнятся без уведомлений"
            )

    def reload_config(self, config: AppConfig) -> None:
        with self._lock:
            self._config = config
            self._feeds = config.filters.feeds
            self._notifier.translate_foreign = config.translate_foreign
            self._notifier.lang = get_language(self._base_dir)
            logger.info("Конфигурация мониторинга обновлена")

    def reset_and_notify_current(self) -> int:
        """Сбросить базу и разово прислать все подходящие заказы."""
        with self._lock:
            self._storage.close()
            if self._config.db_path.exists():
                self._config.db_path.unlink()
            self._storage = ProjectStorage(self._config.db_path)
            saved_seed = self._config.initial_seed
            self._config.initial_seed = False
            try:
                return self._run_once_unlocked(force_notify=True)
            finally:
                self._config.initial_seed = saved_seed

    def reset_and_seed(self) -> int:
        """Удалить базу и запомнить текущие проекты без уведомлений."""
        with self._lock:
            self._storage.close()
            if self._config.db_path.exists():
                self._config.db_path.unlink()
            self._storage = ProjectStorage(self._config.db_path)
            saved_seed = self._config.initial_seed
            self._config.initial_seed = True
            try:
                self._run_once_unlocked()
                return self._storage.count()
            finally:
                self._config.initial_seed = saved_seed

    def known_count(self) -> int:
        return self._storage.count()

    def run_once(self) -> int:
        """Проверить RSS и отправить уведомления о новых проектах. Возвращает число новых."""
        with self._lock:
            return self._run_once_unlocked()

    def _can_poll(self) -> bool:
        if is_setup_complete(self._base_dir):
            return True
        if self._storage.count() > 0:
            return True
        logger.info(
            "Пропуск опроса: завершите настройку в Telegram (команда /start)"
        )
        return False

    def _run_once_unlocked(self, *, force_notify: bool = False) -> int:
        if not force_notify and not self._can_poll():
            return 0

        lang = get_language(self._base_dir)
        self._notifier.lang = lang

        projects = collect_from_feeds(self._feeds, self._config.filters)
        logger.info("Получено проектов после фильтров: %s", len(projects))

        is_first_run = (
            not force_notify
            and self._storage.count() == 0
            and self._config.initial_seed
        )
        sent = 0
        failed = 0

        new_projects = [
            project
            for project in sorted(
                projects,
                key=lambda p: p.published_at or p.storage_key,
            )
            if not self._storage.is_seen(project.storage_key)
        ]
        pending = len(new_projects)

        backlog_seed = (
            not force_notify
            and not is_first_run
            and pending >= BACKLOG_SEED_THRESHOLD
        )

        if is_first_run or backlog_seed:
            for project in new_projects:
                self._storage.mark_seen(
                    project.storage_key, project.url, project.title
                )
            if backlog_seed:
                logger.warning(
                    "Защита от спама: %s новых объявлений запомнены без уведомлений",
                    pending,
                )
                try:
                    self._notifier.notify_text(t(lang, "spam_backlog", count=pending))
                except Exception:
                    logger.exception(
                        "Не удалось отправить предупреждение о пакете объявлений"
                    )
        else:
            notify_batch = new_projects
            skipped = 0
            if not force_notify and len(notify_batch) > MAX_NOTIFICATIONS_PER_POLL:
                skipped = len(notify_batch) - MAX_NOTIFICATIONS_PER_POLL
                notify_batch = notify_batch[:MAX_NOTIFICATIONS_PER_POLL]

            for project in notify_batch:
                try:
                    logger.info("Новый заказ: %s [%s]", project.title, project.source)
                    self._notifier.notify_project(
                        project,
                        self._config.filters.description_preview_length,
                    )
                    sent += 1
                except Exception:
                    failed += 1
                    logger.exception(
                        "Не удалось отправить уведомление: %s", project.url
                    )
                    self._storage.mark_seen(
                        project.storage_key, project.url, project.title
                    )
                    continue

                self._storage.mark_notified(
                    project.storage_key, project.url, project.title
                )

            if skipped:
                for project in new_projects[MAX_NOTIFICATIONS_PER_POLL:]:
                    self._storage.mark_seen(
                        project.storage_key, project.url, project.title
                    )
                logger.warning(
                    "Лимит %s уведомлений за опрос — ещё %s запомнены без отправки",
                    MAX_NOTIFICATIONS_PER_POLL,
                    skipped,
                )
                try:
                    self._notifier.notify_text(
                        t(
                            lang,
                            "spam_limit",
                            pending=pending,
                            sent=sent,
                            skipped=skipped,
                        )
                    )
                except Exception:
                    logger.exception("Не удалось отправить сообщение о лимите")

        if is_first_run and self._storage.count() > 0:
            try:
                self._notifier.notify_text(
                    t(
                        lang,
                        "monitor_started",
                        count=self._storage.count(),
                        interval=_format_interval(
                            self._config.check_interval_seconds, lang
                        ),
                    )
                )
            except Exception:
                logger.exception(
                    "База заполнена (%s проектов), но служебное сообщение "
                    "в Telegram не отправлено (проверьте VPN)",
                    self._storage.count(),
                )
            logger.info("Первичное заполнение базы завершено")

        logger.info("Новых уведомлений отправлено: %s", sent)
        if failed:
            logger.error(
                "Не удалось отправить %s из %s новых заказов. "
                "Скорее всего нет доступа к Telegram — включите VPN "
                "и перезапустите start_bot.bat",
                failed,
                pending,
            )
        return sent

    def close(self) -> None:
        self._storage.close()

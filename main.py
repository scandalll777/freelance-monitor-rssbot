#!/usr/bin/env python3
"""Мониторинг фриланс-площадок → Telegram."""

from __future__ import annotations

import argparse
import atexit
import ctypes
import logging
import os
import sys
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import load_config
from app.monitor import FlMonitor
from app.setup_state import is_setup_complete
from app.sources.registry import normalize_feed_items
from app.telegram_api import TelegramApi
from app.telegram_menu import TelegramMenuBot, create_menu_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def _process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        import os

        os.kill(pid, 0)
        return True
    except OSError:
        return False


def ensure_single_instance(base_dir: Path) -> None:
    lock_path = base_dir / "data" / "bot.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if lock_path.is_file():
        try:
            old_pid = int(lock_path.read_text(encoding="utf-8").strip())
        except ValueError:
            old_pid = 0
        if _process_exists(old_pid):
            logger.error(
                "Бот уже запущен (PID %s). Закройте предыдущее окно start_bot.bat.",
                old_pid,
            )
            raise SystemExit(1)

    lock_path.write_text(str(os.getpid()), encoding="utf-8")

    def _release_lock() -> None:
        try:
            if lock_path.is_file() and lock_path.read_text(encoding="utf-8").strip() == str(
                os.getpid()
            ):
                lock_path.unlink(missing_ok=True)
        except OSError:
            pass

    atexit.register(_release_lock)


def run_check(monitor: FlMonitor) -> None:
    try:
        monitor.run_once()
    except Exception:
        logger.exception("Ошибка при проверке проектов")


def main() -> int:
    parser = argparse.ArgumentParser(description="Мониторинг фриланс-площадок")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Выполнить одну проверку и выйти (без планировщика)",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    ensure_single_instance(base_dir)

    try:
        config = load_config(base_dir)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    monitor = FlMonitor(config, base_dir)
    menu_bot: TelegramMenuBot | None = None
    enabled_feeds = [
        f for f in normalize_feed_items(config.filters.feeds) if f.enabled
    ]

    if args.once:
        run_check(monitor)
        monitor.close()
        return 0

    api = TelegramApi(config.telegram_token, config.telegram_proxy)
    on_apply, needs_onboarding, on_onboarding_complete = create_menu_handlers(
        monitor, base_dir
    )
    menu_bot = TelegramMenuBot(
        api,
        config.telegram_chat_id,
        base_dir,
        on_apply=on_apply,
        needs_onboarding=needs_onboarding,
        on_onboarding_complete=on_onboarding_complete,
    )
    menu_bot.start()

    if not is_setup_complete(base_dir):
        if monitor.known_count() > 0:
            from app.setup_state import mark_setup_complete

            mark_setup_complete(base_dir)
            logger.info("Обнаружена старая база — мастер настройки пропущен")
        else:
            menu_bot.prompt_onboarding(config.telegram_chat_id)

    interval_min = max(1, config.check_interval_seconds // 60)
    logger.info(
        "Старт: проверка каждые %s мин., активных лент RSS: %s",
        interval_min,
        len(enabled_feeds),
    )

    if is_setup_complete(base_dir):
        run_check(monitor)
    else:
        logger.info(
            "Первый запуск: отправьте боту /start в Telegram и пройдите настройку"
        )

    scheduler = BlockingScheduler()
    scheduler.add_job(
        lambda: run_check(monitor),
        trigger=IntervalTrigger(seconds=config.check_interval_seconds),
        id="freelance_check",
        replace_existing=True,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка...")
    finally:
        if menu_bot:
            menu_bot.stop()
        monitor.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

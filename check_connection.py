#!/usr/bin/env python3
"""Проверка связи с Telegram перед запуском бота."""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))


def main() -> int:
    try:
        from app.config import load_config
        from app.telegram_api import TelegramApi

        config = load_config(BASE)
        TelegramApi(config.telegram_token, config.telegram_proxy).check_connection()
        print("OK: Telegram доступен, бот может отправлять сообщения.")
        return 0
    except ValueError as exc:
        print(f"ОШИБКА настройки: {exc}")
        return 1
    except Exception:
        print(
            "ОШИБКА: Telegram недоступен (api.telegram.org).\n"
            "Включите VPN и запустите снова.\n"
            "Без VPN объявления находятся, но в Telegram не доходят."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)


def _windows_socks_proxy() -> str | None:
    if sys.platform != "win32":
        return None
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        )
        enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if not enabled:
            return None
        server, _ = winreg.QueryValueEx(key, "ProxyServer")
        if not server:
            return None
        if server.lower().startswith("socks="):
            hostport = server.split("=", 1)[1]
            return f"socks5://{hostport}"
        if "=" not in server and ":" in server:
            return f"socks5://{server}"
    except OSError:
        return None
    return None


def _normalize_proxy(value: str) -> str:
    if value.startswith("socks="):
        return f"socks5://{value.split('=', 1)[1]}"
    return value


def resolve_telegram_proxy(explicit: str | None = None) -> str | None:
    """Прокси из .env, переменных окружения или настроек VPN в Windows."""
    for value in (
        explicit,
        os.getenv("TELEGRAM_PROXY", "").strip() or None,
        os.getenv("ALL_PROXY", "").strip() or None,
        os.getenv("HTTPS_PROXY", "").strip() or None,
        _windows_socks_proxy(),
    ):
        if not value:
            continue
        return _normalize_proxy(value)
    return None


def resolve_rss_proxy(explicit: str | None = None) -> str | None:
    """Прокси для зарубежных RSS (Freelancer, RemoteOK и др.).

    По умолчанию берётся тот же SOCKS, что и для Telegram.
    FL.ru всегда качается напрямую.
    """
    rss = explicit or os.getenv("RSS_PROXY", "").strip() or None
    if rss:
        return _normalize_proxy(rss)
    return resolve_telegram_proxy()

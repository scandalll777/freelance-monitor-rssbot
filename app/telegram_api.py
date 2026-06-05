from __future__ import annotations

import logging
import time
from typing import Any

import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, Timeout

from app.proxy_util import resolve_telegram_proxy

logger = logging.getLogger(__name__)

_RETRY_ERRORS = (ConnectTimeout, ReadTimeout, Timeout, ConnectionError)
_MAX_RETRIES = 3


class TelegramApi:
    def __init__(self, token: str, proxy: str | None = None) -> None:
        self._api = f"https://api.telegram.org/bot{token}"
        self._session = requests.Session()
        resolved = resolve_telegram_proxy(proxy)
        self._session.trust_env = False
        if resolved:
            self._session.proxies.update({"http": resolved, "https": resolved})
            logger.info("Telegram через прокси: %s", resolved)

    def _call(self, method: str, **payload: Any) -> dict:
        last_error: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self._session.post(
                    f"{self._api}/{method}",
                    json=payload,
                    timeout=35,
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("ok"):
                    raise RuntimeError(f"Telegram API error: {data}")
                return data["result"]
            except _RETRY_ERRORS as exc:
                last_error = exc
                if attempt < _MAX_RETRIES:
                    logger.warning(
                        "Telegram %s: попытка %s/%s не удалась, повтор...",
                        method,
                        attempt,
                        _MAX_RETRIES,
                    )
                    time.sleep(2 * attempt)
        assert last_error is not None
        raise last_error

    def check_connection(self) -> None:
        """Проверить доступ к api.telegram.org (нужен VPN в РФ)."""
        self._call("getMe")

    def get_updates(self, offset: int, timeout: int = 25) -> list[dict]:
        return self._call(
            "getUpdates",
            offset=offset,
            timeout=timeout,
            allowed_updates=["message", "callback_query"],
        )

    def send_message(
        self,
        chat_id: str | int,
        text: str,
        *,
        parse_mode: str | None = "HTML",
        reply_markup: dict | None = None,
        disable_preview: bool = False,
    ) -> dict:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_preview,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._call("sendMessage", **payload)

    def edit_message(
        self,
        chat_id: str | int,
        message_id: int,
        text: str,
        *,
        parse_mode: str | None = "HTML",
        reply_markup: dict | None = None,
    ) -> dict:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._call("editMessageText", **payload)

    def answer_callback(self, callback_id: str, text: str = "") -> None:
        self._call("answerCallbackQuery", callback_query_id=callback_id, text=text)

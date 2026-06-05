from __future__ import annotations

import time

import requests

USER_AGENT = "FreelanceMonitorBot/2.0"
RSS_TIMEOUT = 30

_session = requests.Session()
_session.trust_env = False
_session.headers.update(
    {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
)


def fetch_url(
    url: str,
    *,
    timeout: int = RSS_TIMEOUT,
    retries: int = 3,
    proxy: str | None = None,
) -> bytes:
    proxies = {"http": proxy, "https": proxy} if proxy else None
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = _session.get(url, timeout=timeout, proxies=proxies)
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(1 + attempt)
    assert last_error is not None
    raise last_error

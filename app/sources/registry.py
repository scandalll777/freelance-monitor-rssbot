from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

import feedparser

from app.config import DEFAULT_FEED, FilterConfig
from app.http_client import fetch_url
from app.project import Project, is_foreign_source, passes_filters
from app.proxy_util import resolve_rss_proxy
from app.sources.base import parse_entry
from app.sources.fl_ru import parse_fl_ru_entry
from app.sources.freelancer import parse_freelancer_entry
from app.sources.remoteok import parse_remoteok_entry
from app.sources.weworkremotely import parse_weworkremotely_entry

logger = logging.getLogger(__name__)

# Пауза между запросами к разным лентам (сек.) — вежливая нагрузка на сайты
FEED_PAUSE_SEC = 2.0

EntryParser = Callable[[dict], Project | None]

PARSERS: dict[str, EntryParser] = {
    "fl_ru": parse_fl_ru_entry,
    "freelancer": parse_freelancer_entry,
    "remoteok": parse_remoteok_entry,
    "weworkremotely": parse_weworkremotely_entry,
}

UNAVAILABLE_SOURCES: dict[str, str] = {
    "habr_freelance": "Habr Freelance закрыт 28.02.2025",
    "kwork": "Публичного RSS нет — нужен отдельный парсер",
    "upwork": "Официальный RSS отключён с августа 2024",
    "guru": "Официального RSS нет",
    "weblancer": "RSS недоступен (404)",
    "freelansim": "RSS отключён (410 Gone)",
    "craigslist": "RSS по поискам отключён (410 Gone)",
    "avito": "Публичного RSS для объявлений нет",
}


@dataclass
class FeedItem:
    url: str
    source: str
    enabled: bool = True


def detect_source(url: str) -> str:
    host = (urlparse(url).netloc or "").lower()
    if "fl.ru" in host:
        return "fl_ru"
    if "freelancer.com" in host:
        return "freelancer"
    if "remoteok.com" in host:
        return "remoteok"
    if "weworkremotely.com" in host:
        return "weworkremotely"
    return "generic"


def normalize_feed_items(feeds: list[dict]) -> list[FeedItem]:
    items: list[FeedItem] = []
    for raw in feeds or []:
        url = (raw.get("url") or "").strip()
        if not url:
            continue
        enabled = raw.get("enabled", True)
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() not in ("0", "false", "no", "off")
        source = (raw.get("source") or detect_source(url)).strip().lower()
        items.append(FeedItem(url=url, source=source, enabled=bool(enabled)))
    if not items:
        items.append(FeedItem(url=DEFAULT_FEED, source="fl_ru"))
    return items


def _parse_generic_entry(entry: dict) -> Project | None:
    return parse_entry("generic", entry, deadline_lang="ru")


def _rss_proxy(source: str) -> str | None:
    if source == "fl_ru":
        return None
    if is_foreign_source(source) or source == "generic":
        return resolve_rss_proxy()
    return None


def fetch_feed(url: str, source: str) -> list[Project]:
    proxy = _rss_proxy(source)
    if proxy:
        logger.debug("RSS %s через прокси", source)
    content = fetch_url(url, proxy=proxy)
    parsed = feedparser.parse(content)
    if getattr(parsed, "bozo", False) and not parsed.entries:
        exc = getattr(parsed, "bozo_exception", None)
        raise RuntimeError(f"Не удалось разобрать RSS {url}: {exc}")

    parser = PARSERS.get(source, _parse_generic_entry)
    projects: list[Project] = []
    for entry in parsed.entries:
        try:
            project = parser(entry)
        except Exception:
            logger.exception("Ошибка разбора записи RSS (%s): %s", source, url)
            continue
        if project:
            projects.append(project)
    return projects


def collect_from_feeds(
    feeds: list[dict], filters: FilterConfig
) -> list[Project]:
    items = [item for item in normalize_feed_items(feeds) if item.enabled]
    by_key: dict[str, Project] = {}

    for index, item in enumerate(items):
        if index > 0:
            time.sleep(FEED_PAUSE_SEC + random.uniform(0, 1.0))
        try:
            batch = fetch_feed(item.url, item.source)
        except Exception:
            logger.exception("Ошибка загрузки RSS: %s (%s)", item.url, item.source)
            continue
        logger.info(
            "Источник %s: %s записей из %s",
            item.source,
            len(batch),
            item.url,
        )
        for project in batch:
            if passes_filters(project, filters):
                by_key[project.storage_key] = project

    return list(by_key.values())

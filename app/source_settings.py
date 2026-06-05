from __future__ import annotations

from app.project import SOURCE_LABELS
from app.sources.registry import detect_source

MENU_SOURCE_ORDER = ("fl_ru", "freelancer", "remoteok", "weworkremotely", "generic")


def source_label(source_id: str) -> str:
    return SOURCE_LABELS.get(source_id, source_id)


def _feed_enabled(raw: object) -> bool:
    if raw is None:
        return True
    if isinstance(raw, str):
        return raw.strip().lower() not in ("0", "false", "no", "off")
    return bool(raw)


def feed_source(feed: dict) -> str:
    url = (feed.get("url") or "").strip()
    return ((feed.get("source") or detect_source(url)).strip().lower() if url else "")


def detect_sources_enabled(feeds: list[dict]) -> dict[str, bool]:
    """Источник включён, если хотя бы одна его лента активна."""
    by_source: dict[str, list[bool]] = {}
    for feed in feeds:
        source = feed_source(feed)
        if not source:
            continue
        by_source.setdefault(source, []).append(_feed_enabled(feed.get("enabled", True)))
    return {source: any(flags) for source, flags in by_source.items()}


def configured_source_ids(feeds: list[dict]) -> list[str]:
    found = {feed_source(f) for f in feeds if feed_source(f)}
    ordered = [s for s in MENU_SOURCE_ORDER if s in found]
    for s in sorted(found):
        if s not in ordered:
            ordered.append(s)
    return ordered


def apply_source_enabled(
    feeds: list[dict], sources_enabled: dict[str, bool]
) -> list[dict]:
    result: list[dict] = []
    for feed in feeds:
        item = dict(feed)
        source = feed_source(item)
        if source in sources_enabled:
            if sources_enabled[source]:
                item.pop("enabled", None)
            else:
                item["enabled"] = False
        result.append(item)
    return result

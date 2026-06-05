from __future__ import annotations

import html
import re
from email.utils import parsedate_to_datetime

from app.project import Project

GENERIC_ID_RE = re.compile(r"/(\d+)(?:[./?#]|$)")
SLUG_ID_RE = re.compile(r"/([^/]+)\.html?$", re.IGNORECASE)

DEADLINE_PATTERNS_RU = [
    re.compile(
        r"до\s+[\d.:]+\s*(?:по\s+)?(?:мск|msk|utc|gmt)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"в\s+теч(?:ение)?\s+\d+[\wх]*\s*(?:час|дн|нед|месяц)",
        re.IGNORECASE,
    ),
    re.compile(r"срок\s*(?:выполнения)?\s*[:\-]?\s*\d+[\w\s]*", re.IGNORECASE),
    re.compile(r"\d+\s*(?:рабочих?\s+)?(?:дн|дней|дня)\b", re.IGNORECASE),
    re.compile(r"\d+\s*(?:час|часа|часов)\b", re.IGNORECASE),
    re.compile(r"срочн\w*", re.IGNORECASE),
]

DEADLINE_PATTERNS_EN = [
    re.compile(r"\b\d+\s*(?:day|days|week|weeks|month|months)\b", re.IGNORECASE),
    re.compile(r"\b(?:asap|urgent|immediate(?:ly)?)\b", re.IGNORECASE),
    re.compile(r"\bdeadline\b", re.IGNORECASE),
    re.compile(r"\bwithin\s+\d+\s*(?:day|days|hour|hours)\b", re.IGNORECASE),
]


def parse_published(entry: dict) -> str | None:
    if not entry.get("published"):
        return None
    try:
        return parsedate_to_datetime(entry.published).isoformat(timespec="minutes")
    except (TypeError, ValueError, OverflowError):
        return entry.published


def entry_link(entry: dict) -> str:
    return (entry.get("link") or "").strip()


def entry_description(entry: dict) -> str:
    raw = entry.get("description") or entry.get("summary") or ""
    return html.unescape(str(raw))


def entry_title(entry: dict) -> str:
    return html.unescape(str(entry.get("title") or ""))


def entry_category(entry: dict) -> str:
    category = entry.get("category", "") or "не указана"
    if hasattr(category, "term"):
        category = category.term
    return html.unescape(str(category))


def extract_id_from_url(url: str) -> str | None:
    match = GENERIC_ID_RE.search(url)
    if match:
        return match.group(1)
    match = SLUG_ID_RE.search(url)
    if match:
        return match.group(1)
    return None


def extract_deadline(description: str, *, lang: str = "ru") -> str:
    text = html.unescape(description or "").replace("\n", " ")
    patterns = DEADLINE_PATTERNS_RU if lang == "ru" else DEADLINE_PATTERNS_EN
    found: list[str] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            phrase = match.group(0).strip()
            if phrase and phrase not in found:
                found.append(phrase)
    if found:
        return "; ".join(found[:3])

    lowered = text.lower()
    hints = ("срок", "до ", "в теч", "дедлайн", "deadline", "asap", "urgent")
    if any(word in lowered for word in hints):
        snippet = text[:120].strip()
        if snippet:
            return snippet + ("…" if len(text) > 120 else "")
    return "не указаны"


def parse_entry(
    source: str,
    entry: dict,
    *,
    project_id: str | None = None,
    title: str | None = None,
    category: str | None = None,
    budget: int | None = None,
    budget_text: str = "не указан",
    deadline_lang: str = "ru",
) -> Project | None:
    url = entry_link(entry)
    if not url:
        return None

    local_id = project_id or extract_id_from_url(url)
    if not local_id:
        guid = str(entry.get("id") or entry.get("guid") or "").strip()
        if guid:
            local_id = guid
        else:
            local_id = url

    return Project(
        source=source,
        project_id=local_id,
        title=title or entry_title(entry),
        url=url,
        category=category or entry_category(entry),
        budget=budget,
        budget_text=budget_text,
        deadline=extract_deadline(entry_description(entry), lang=deadline_lang),
        description=entry_description(entry),
        published_at=parse_published(entry),
    )

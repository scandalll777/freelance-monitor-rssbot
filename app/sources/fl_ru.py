from __future__ import annotations

import html
import re

from app.project import Project
from app.sources.base import (
    entry_description,
    entry_link,
    entry_title,
    parse_entry,
    parse_published,
)

BUDGET_TITLE_RE = re.compile(
    r"\(?\s*бюджет\s*:\s*([\d\s]+)\s*(?:&#8381;|₽|руб\.?|rub)?\s*\)?",
    re.IGNORECASE,
)
PROJECT_ID_RE = re.compile(r"/projects/(\d+)/")


def extract_project_id(url: str) -> str | None:
    match = PROJECT_ID_RE.search(url)
    return match.group(1) if match else None


def parse_budget_from_title(title: str) -> tuple[int | None, str]:
    clean = html.unescape(title)
    match = BUDGET_TITLE_RE.search(clean)
    if not match:
        return None, "не указан"
    digits = re.sub(r"\s+", "", match.group(1))
    try:
        amount = int(digits)
    except ValueError:
        return None, match.group(0).strip()
    return amount, f"{amount:,}".replace(",", " ") + " ₽"


def clean_title(title: str) -> str:
    clean = html.unescape(title)
    return BUDGET_TITLE_RE.sub("", clean).strip().strip("()").strip()


def parse_fl_ru_entry(entry: dict) -> Project | None:
    url = entry_link(entry)
    project_id = extract_project_id(url)
    if not project_id:
        return None

    raw_title = entry_title(entry)
    budget, budget_text = parse_budget_from_title(raw_title)
    category = entry.get("category", "") or "не указана"
    if hasattr(category, "term"):
        category = category.term

    return parse_entry(
        "fl_ru",
        entry,
        project_id=project_id,
        title=clean_title(raw_title),
        category=html.unescape(str(category)),
        budget=budget,
        budget_text=budget_text,
        deadline_lang="ru",
    )

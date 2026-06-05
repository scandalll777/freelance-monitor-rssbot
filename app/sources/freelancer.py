from __future__ import annotations

import html
import re

from app.project import Project
from app.sources.base import entry_description, entry_link, entry_title, parse_entry

BUDGET_RE = re.compile(
    r"\(Budget:\s*\$?\s*([\d,]+)\s*(?:-\s*\$?\s*([\d,]+))?\s*([A-Z]{3})?",
    re.IGNORECASE,
)
JOBS_RE = re.compile(r"Jobs:\s*([^)]+)\)", re.IGNORECASE)
TITLE_SUFFIX_RE = re.compile(r"\s*--\s*\d+\s*$")


def _parse_amount(raw: str) -> int | None:
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def parse_freelancer_budget(description: str) -> tuple[int | None, str]:
    match = BUDGET_RE.search(description)
    if not match:
        return None, "не указан"

    low = _parse_amount(match.group(1))
    high = _parse_amount(match.group(2) or "")
    currency = (match.group(3) or "USD").upper()

    if low is not None and high is not None:
        return low, f"${low:,}–${high:,} {currency}".replace(",", " ")
    if low is not None:
        return low, f"${low:,} {currency}".replace(",", " ")
    return None, match.group(0).strip()


def parse_freelancer_category(entry: dict, description: str) -> str:
    category = entry.get("category")
    if category:
        if hasattr(category, "term"):
            category = category.term
        return html.unescape(str(category))

    match = JOBS_RE.search(description)
    if match:
        jobs = match.group(1).strip()
        first = jobs.split(",")[0].strip()
        if first:
            return first
    return "не указана"


def clean_freelancer_title(title: str) -> str:
    clean = html.unescape(title)
    clean = clean.replace(" &ndash; ", " — ").replace(" &amp; ", " & ")
    return TITLE_SUFFIX_RE.sub("", clean).strip()


def parse_freelancer_entry(entry: dict) -> Project | None:
    url = entry_link(entry)
    if not url or "freelancer.com" not in url:
        return None

    description = entry_description(entry)
    budget, budget_text = parse_freelancer_budget(description)
    category = parse_freelancer_category(entry, description)

    project_id = url.rstrip("/").split("/")[-1].replace(".html", "")
    if not project_id:
        return None

    return parse_entry(
        "freelancer",
        entry,
        project_id=project_id,
        title=clean_freelancer_title(entry_title(entry)),
        category=category,
        budget=budget,
        budget_text=budget_text,
        deadline_lang="en",
    )

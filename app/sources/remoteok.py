from __future__ import annotations

import re

from app.project import Project
from app.sources.base import entry_description, entry_link, entry_title, parse_entry

BUDGET_TAG_RE = re.compile(r"(\d[\d,]*)\s*(?:USD|\$|€|EUR)", re.IGNORECASE)
JOB_ID_RE = re.compile(r"-(\d+)(?:[/?#]|$)")


def parse_remoteok_entry(entry: dict) -> Project | None:
    url = entry_link(entry)
    if not url:
        return None

    match = JOB_ID_RE.search(url)
    project_id = match.group(1) if match else url.rstrip("/").split("/")[-1]

    description = entry_description(entry)
    budget = None
    budget_text = "не указан"
    budget_match = BUDGET_TAG_RE.search(description)
    if budget_match:
        amount = int(budget_match.group(1).replace(",", ""))
        budget = amount
        budget_text = f"${amount:,}".replace(",", " ")

    tags = entry.get("tags") or []
    category = "Remote"
    if tags:
        tag_labels = []
        for tag in tags[:3]:
            if isinstance(tag, dict):
                tag_labels.append(str(tag.get("term", "")))
            else:
                tag_labels.append(str(tag))
        category = ", ".join(t for t in tag_labels if t) or category

    return parse_entry(
        "remoteok",
        entry,
        project_id=project_id,
        title=entry_title(entry),
        category=category,
        budget=budget,
        budget_text=budget_text,
        deadline_lang="en",
    )

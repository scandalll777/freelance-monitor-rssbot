from __future__ import annotations

from app.project import Project
from app.sources.base import entry_title, parse_entry


def parse_weworkremotely_entry(entry: dict) -> Project | None:
    url = (entry.get("link") or "").strip()
    if not url:
        return None

    project_id = url.rstrip("/").split("/")[-1]
    title = entry_title(entry)
    category = "Remote programming"
    if ":" in title:
        company, role = title.split(":", 1)
        category = company.strip()

    return parse_entry(
        "weworkremotely",
        entry,
        project_id=project_id,
        title=title,
        category=category,
        budget=None,
        budget_text="не указан",
        deadline_lang="en",
    )

from __future__ import annotations

import re
from dataclasses import dataclass

from app.config import FilterConfig

SOURCE_LABELS: dict[str, str] = {
    "fl_ru": "FL.ru",
    "freelancer": "Freelancer.com",
    "remoteok": "RemoteOK",
    "weworkremotely": "We Work Remotely",
    "generic": "RSS",
}

FOREIGN_SOURCES = frozenset(
    {"freelancer", "remoteok", "weworkremotely", "generic"}
)


def is_foreign_source(source: str) -> bool:
    return source in FOREIGN_SOURCES


@dataclass
class Project:
    source: str
    project_id: str
    title: str
    url: str
    category: str
    budget: int | None
    budget_text: str
    deadline: str
    description: str
    published_at: str | None

    @property
    def storage_key(self) -> str:
        return f"{self.source}:{self.project_id}"

    @property
    def source_label(self) -> str:
        return SOURCE_LABELS.get(self.source, self.source)


def keyword_in_text(text: str, keyword: str) -> bool:
    kw = keyword.lower().strip()
    if not kw:
        return False
    lowered = text.lower()
    if " " in kw or len(kw) > 4:
        return kw in lowered
    return bool(re.search(rf"(?<![a-zа-яё]){re.escape(kw)}(?![a-zа-яё])", lowered))


def passes_filters(project: Project, filters: FilterConfig) -> bool:
    if filters.categories_include and project.source == "fl_ru":
        cat = project.category.lower()
        if not any(p.lower() in cat for p in filters.categories_include):
            return False

    haystack = f"{project.title} {project.description} {project.category}".lower()

    if filters.keywords_include:
        if not any(keyword_in_text(haystack, kw) for kw in filters.keywords_include):
            return False

    if is_foreign_source(project.source) and filters.keywords_include_foreign:
        # Зарубежные ленты: ключевое слово должно быть в заголовке или категории,
        # иначе «automation» и др. в длинном описании дают ложные срабатывания.
        title_haystack = f"{project.title} {project.category}".lower()
        if not any(
            keyword_in_text(title_haystack, kw)
            for kw in filters.keywords_include_foreign
        ):
            return False

    if filters.keywords_exclude:
        if any(keyword_in_text(haystack, kw) for kw in filters.keywords_exclude):
            return False

    if filters.min_budget > 0:
        if project.budget is None or project.budget < filters.min_budget:
            return False

    if filters.max_budget > 0:
        if project.budget is not None and project.budget > filters.max_budget:
            return False

    return True

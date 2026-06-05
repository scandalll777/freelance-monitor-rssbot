from __future__ import annotations

from dataclasses import dataclass, field

from app.config_io import (
    apply_preserved_yaml_fields,
    load_yaml_config,
    save_yaml_config,
)
from app.filter_presets import (
    FILTER_PRESETS,
    detect_active_preset_ids,
    extra_feeds,
    merge_presets,
)
from app.i18n import preset_label as localized_preset_label
from app.i18n import t
from app.source_settings import (
    apply_source_enabled,
    configured_source_ids,
    detect_sources_enabled,
    source_label,
)


@dataclass
class FilterDraft:
    preset_ids: set[str] = field(default_factory=set)
    sources_enabled: dict[str, bool] = field(default_factory=dict)
    min_budget: int = 0
    keywords_include: list[str] = field(default_factory=list)
    keywords_exclude: list[str] = field(
        default_factory=lambda: ["бесплатно", "за отзыв"]
    )

    @classmethod
    def from_yaml(cls) -> FilterDraft:
        raw = load_yaml_config()
        feeds = raw.get("feeds", []) or []
        return cls(
            preset_ids=set(
                detect_active_preset_ids(
                    feeds,
                    raw.get("categories_include", []) or [],
                )
            ),
            sources_enabled=detect_sources_enabled(feeds),
            min_budget=int(raw.get("min_budget", 0) or 0),
            keywords_include=list(raw.get("keywords_include", []) or []),
            keywords_exclude=list(
                raw.get("keywords_exclude", []) or ["бесплатно", "за отзыв"]
            ),
        )

    def to_config_dict(self) -> dict:
        raw = load_yaml_config()
        feeds, categories_include = merge_presets(sorted(self.preset_ids))
        feeds = feeds + extra_feeds(raw.get("feeds", []) or [])
        feeds = apply_source_enabled(feeds, self.sources_enabled)
        return apply_preserved_yaml_fields(
            {
                "feeds": feeds,
                "categories_include": categories_include,
                "keywords_include": self.keywords_include,
                "keywords_exclude": self.keywords_exclude,
                "min_budget": self.min_budget,
                "max_budget": 0,
            },
            raw,
        )

    def save(self) -> None:
        save_yaml_config(self.to_config_dict())

    def toggle_preset(self, preset_id: str) -> None:
        if preset_id in self.preset_ids:
            self.preset_ids.remove(preset_id)
        else:
            self.preset_ids.add(preset_id)

    def toggle_source(self, source_id: str) -> None:
        current = self.sources_enabled.get(source_id, True)
        self.sources_enabled[source_id] = not current

    def is_source_enabled(self, source_id: str) -> bool:
        return self.sources_enabled.get(source_id, True)

    def preset_label(self, preset_id: str, lang: str = "en") -> str:
        for preset in FILTER_PRESETS:
            if preset.id == preset_id:
                return localized_preset_label(lang, preset_id, preset.label)
        return preset_id

    def configured_sources(self) -> list[str]:
        raw = load_yaml_config()
        preview_feeds = merge_presets(sorted(self.preset_ids))[0]
        preview_feeds = preview_feeds + extra_feeds(raw.get("feeds", []) or [])
        return configured_source_ids(preview_feeds)

    def summary_html(self, lang: str = "en") -> str:
        def esc(text: str) -> str:
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

        source_ids = self.configured_sources()
        if source_ids:
            source_lines = []
            for sid in source_ids:
                mark = "✅" if self.is_source_enabled(sid) else "⬜"
                source_lines.append(f"{mark} {esc(source_label(sid))}")
            sources_block = "\n".join(source_lines)
        else:
            sources_block = f"<i>{esc(t(lang, 'summary_no_sources'))}</i>"

        if self.preset_ids:
            sections = "\n".join(
                f"• {esc(self.preset_label(pid, lang))}"
                for pid in sorted(self.preset_ids)
            )
        else:
            sections = f"<i>{esc(t(lang, 'summary_no_categories'))}</i>"

        raw = load_yaml_config()
        foreign_kw = raw.get("keywords_include_foreign") or []
        kw_inc = esc(", ".join(self.keywords_include) or "—")
        kw_foreign = esc(", ".join(foreign_kw) or "—")
        kw_exc = esc(", ".join(self.keywords_exclude) or "—")
        if self.min_budget > 0:
            suffix = " ₽" if lang == "ru" else ""
            budget = f"{self.min_budget:,}".replace(",", " ") + suffix
        else:
            budget = t(lang, "summary_budget_any")

        return (
            f"<b>{esc(t(lang, 'summary_title'))}</b>\n\n"
            f"<b>{esc(t(lang, 'summary_sources'))}:</b>\n{sources_block}\n\n"
            f"<b>{esc(t(lang, 'summary_categories'))}:</b>\n{sections}\n\n"
            f"<b>{esc(t(lang, 'summary_budget'))}:</b> {budget}\n"
            f"<b>{esc(t(lang, 'summary_kw_all'))}:</b> {kw_inc}\n"
            f"<b>{esc(t(lang, 'summary_kw_foreign'))}:</b> {kw_foreign}\n"
            f"<b>{esc(t(lang, 'summary_exclude'))}:</b> {kw_exc}"
        )

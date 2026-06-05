from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FilterPreset:
    id: str
    label: str
    hint: str
    feeds: list[dict[str, str]] = field(default_factory=list)
    categories_include: list[str] = field(default_factory=list)


# Готовые разделы FL.ru — пользователь только ставит галочки
FILTER_PRESETS: list[FilterPreset] = [
    FilterPreset(
        id="ai",
        label="AI — искусственный интеллект",
        hint="Весь раздел: нейросети, ChatGPT, n8n, боты и т.д.",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=31"}],
        categories_include=["AI — искусственный интеллект"],
    ),
    FilterPreset(
        id="vibe_coding",
        label="Vibe coding",
        hint="Разработка с помощью ИИ (Cursor, Claude и др.)",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=5"}],
        categories_include=["Vibe coding"],
    ),
    FilterPreset(
        id="web_dev",
        label="Веб-программирование",
        hint="Сайты, backend, frontend",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=5&subcategory=37"}],
        categories_include=[],
    ),
    FilterPreset(
        id="programming",
        label="Программирование (всё)",
        hint="Все подкатегории раздела «Программирование»",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=5"}],
        categories_include=["Программирование"],
    ),
    FilterPreset(
        id="sites",
        label="Разработка сайтов",
        hint="Вёрстка, CMS, лендинги",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=2"}],
        categories_include=["Разработка сайтов"],
    ),
    FilterPreset(
        id="design",
        label="Дизайн и арт",
        hint="Логотипы, баннеры, UI/UX",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=3"}],
        categories_include=["Дизайн"],
    ),
    FilterPreset(
        id="mobile",
        label="Мобильные приложения",
        hint="iOS, Android, кроссплатформа",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=23"}],
        categories_include=["Мобильные приложения"],
    ),
    FilterPreset(
        id="seo",
        label="SEO и продвижение",
        hint="Оптимизация, контекст, маркетинг",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=6"}],
        categories_include=["SEO", "Продвижение"],
    ),
    FilterPreset(
        id="texts",
        label="Тексты",
        hint="Копирайтинг, статьи, переводы текстов",
        feeds=[{"url": "https://www.fl.ru/rss/all.xml?category=8"}],
        categories_include=["Тексты"],
    ),
]


def preset_feed_urls() -> set[str]:
    urls: set[str] = set()
    for preset in FILTER_PRESETS:
        for feed in preset.feeds:
            urls.add(feed["url"])
    return urls


def extra_feeds(feeds: list[dict[str, str]]) -> list[dict[str, str]]:
    """Ленты вне пресетов FL.ru (Freelancer, RemoteOK и т.д.)."""
    known = preset_feed_urls()
    result: list[dict[str, str]] = []
    for feed in feeds:
        url = (feed.get("url") or "").strip()
        if url and url not in known:
            result.append(feed)
    return result


def merge_presets(preset_ids: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    feeds_by_url: dict[str, dict[str, str]] = {}
    categories: list[str] = []

    for preset in FILTER_PRESETS:
        if preset.id not in preset_ids:
            continue
        for feed in preset.feeds:
            feeds_by_url[feed["url"]] = feed
        for cat in preset.categories_include:
            if cat not in categories:
                categories.append(cat)

    if not feeds_by_url:
        raise ValueError("Выберите хотя бы один раздел")

    return list(feeds_by_url.values()), categories


def detect_active_preset_ids(
    feeds: list[dict[str, str]], categories_include: list[str]
) -> list[str]:
    feed_urls = {f.get("url", "") for f in feeds}
    cats = set(categories_include or [])
    active: list[str] = []

    for preset in FILTER_PRESETS:
        preset_urls = {f["url"] for f in preset.feeds}
        if not preset_urls.issubset(feed_urls):
            continue
        if preset.categories_include:
            if not all(c in cats for c in preset.categories_include):
                continue
        active.append(preset.id)

    return active

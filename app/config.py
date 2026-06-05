from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

from app.proxy_util import resolve_telegram_proxy

logger = logging.getLogger(__name__)

DEFAULT_FEED = "https://www.fl.ru/rss/all.xml"
DEFAULT_CHECK_INTERVAL = 300
MIN_CHECK_INTERVAL = 120


@dataclass
class FilterConfig:
    feeds: list[dict[str, str]] = field(default_factory=lambda: [{"url": DEFAULT_FEED}])
    categories_include: list[str] = field(default_factory=list)
    keywords_include: list[str] = field(default_factory=list)
    keywords_include_foreign: list[str] = field(default_factory=list)
    keywords_exclude: list[str] = field(default_factory=list)
    min_budget: int = 0
    max_budget: int = 0
    description_preview_length: int = 200


@dataclass
class AppConfig:
    telegram_token: str
    telegram_chat_id: str
    telegram_proxy: str | None
    check_interval_seconds: int
    initial_seed: bool
    translate_foreign: bool
    filters: FilterConfig
    db_path: Path
    config_path: Path


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    return raw in ("1", "true", "yes", "on")


def load_config(base_dir: Path | None = None) -> AppConfig:
    base = base_dir or Path(__file__).resolve().parent.parent
    load_dotenv(base / ".env")

    config_path = Path(os.getenv("CONFIG_PATH", "config.yaml"))
    if not config_path.is_absolute():
        config_path = base / config_path

    filters = FilterConfig()
    raw: dict = {}
    if config_path.is_file():
        with config_path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        feeds = raw.get("feeds")
        if feeds:
            filters.feeds = feeds
        filters.categories_include = list(raw.get("categories_include", []) or [])
        filters.keywords_include = [s.lower() for s in raw.get("keywords_include", [])]
        filters.keywords_include_foreign = [
            s.lower() for s in raw.get("keywords_include_foreign", []) or []
        ]
        filters.keywords_exclude = [s.lower() for s in raw.get("keywords_exclude", [])]
        filters.min_budget = int(raw.get("min_budget", 0) or 0)
        filters.max_budget = int(raw.get("max_budget", 0) or 0)
        filters.description_preview_length = int(
            raw.get("description_preview_length", 200) or 0
        )

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise ValueError(
            "Задайте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в файле .env "
            "(см. .env.example)"
        )

    proxy = resolve_telegram_proxy(os.getenv("TELEGRAM_PROXY", "").strip() or None)

    translate_foreign = bool(raw.get("translate_foreign", True))
    if os.getenv("TRANSLATE_FOREIGN") is not None:
        translate_foreign = _env_bool("TRANSLATE_FOREIGN", True)

    interval = int(
        os.getenv("CHECK_INTERVAL_SECONDS", str(DEFAULT_CHECK_INTERVAL))
    )
    if interval < MIN_CHECK_INTERVAL:
        logger.warning(
            "CHECK_INTERVAL_SECONDS=%s слишком мало — установлено %s с "
            "(чтобы не перегружать сайты)",
            interval,
            MIN_CHECK_INTERVAL,
        )
        interval = MIN_CHECK_INTERVAL

    return AppConfig(
        telegram_token=token,
        telegram_chat_id=chat_id,
        telegram_proxy=proxy,
        check_interval_seconds=interval,
        initial_seed=_env_bool("INITIAL_SEED", False),
        translate_foreign=translate_foreign,
        filters=filters,
        db_path=base / "data" / "projects.db",
        config_path=config_path,
    )

from __future__ import annotations

from pathlib import Path

import yaml


def config_path(base_dir: Path | None = None) -> Path:
    base = base_dir or Path(__file__).resolve().parent.parent
    return base / "config.yaml"


def load_yaml_config(path: Path | None = None) -> dict:
    path = path or config_path()
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


PRESERVED_YAML_KEYS = (
    "keywords_include_foreign",
    "translate_foreign",
    "description_preview_length",
)


def apply_preserved_yaml_fields(
    data: dict, raw: dict | None = None
) -> dict:
    """Сохранить поля, которые не редактируются через меню Telegram."""
    if raw is None:
        raw = load_yaml_config()
    for key in PRESERVED_YAML_KEYS:
        if key in raw:
            data[key] = raw[key]
    return data


def save_yaml_config(data: dict, path: Path | None = None) -> None:
    path = path or config_path()
    with path.open("w", encoding="utf-8") as fh:
        fh.write(
            "# Настройки фильтров (меню Telegram или setup_filters.bat)\n\n"
        )
        yaml.safe_dump(
            data,
            fh,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

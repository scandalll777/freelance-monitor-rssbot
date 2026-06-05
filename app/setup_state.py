from __future__ import annotations

import json
from pathlib import Path


def _state_path(base_dir: Path) -> Path:
    return base_dir / "data" / "setup_complete.json"


def is_setup_complete(base_dir: Path) -> bool:
    path = _state_path(base_dir)
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return bool(data.get("complete"))
    except (json.JSONDecodeError, OSError):
        return False


def mark_setup_complete(base_dir: Path) -> None:
    path = _state_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"complete": True}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

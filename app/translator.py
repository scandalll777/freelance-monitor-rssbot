from __future__ import annotations

import html
import logging
import re
from functools import lru_cache

from app.project import is_foreign_source

logger = logging.getLogger(__name__)

SKIP_VALUES = frozenset({"не указан", "не указаны"})

_translator = None


def _get_translator():
    global _translator
    if _translator is None:
        try:
            from deep_translator import GoogleTranslator
        except ImportError as exc:
            raise ImportError(
                "Не установлен пакет deep-translator. "
                "Запустите install.bat или: "
                ".venv\\Scripts\\pip install -r requirements.txt"
            ) from exc
        _translator = GoogleTranslator(source="auto", target="ru")
    return _translator


def _looks_russian(text: str) -> bool:
    cyrillic = len(re.findall(r"[а-яёА-ЯЁ]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))
    return cyrillic >= latin


@lru_cache(maxsize=1024)
def _translate_cached(text: str) -> str:
    clean = html.unescape(text).strip()
    if not clean or clean in SKIP_VALUES:
        return text
    if _looks_russian(clean):
        return text
    try:
        chunk = clean[:4500]
        result = _get_translator().translate(chunk)
        if result and len(clean) > 4500:
            return result.rstrip() + "…"
        return result or text
    except ImportError:
        raise
    except Exception:
        logger.warning("Перевод не удался, оставлен оригинал: %s", clean[:80])
        return text


def translate_text(text: str) -> str:
    if not text:
        return text
    return _translate_cached(text.strip())


def localize_project_text(
    source: str, text: str, *, enabled: bool = True, lang: str = "en"
) -> str:
    if lang == "ru" and enabled and is_foreign_source(source):
        return translate_text(text)
    return text

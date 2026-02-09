"""Internationalization module for RF4S.

Provides init_locale() to load translations and t() for string lookup
with named placeholder substitution. Falls back to English if a key
is missing in the current locale.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_strings: dict[str, str] = {}
_fallback: dict[str, str] = {}

LOCALES_DIR = Path(__file__).resolve().parent / "locales"


def init_locale(language: str) -> None:
    """Load the translation file for *language* and the English fallback.

    :param language: Language code (``"en"``, ``"ru"``, ...).
    """
    global _strings, _fallback

    _fallback = _load_json("en")

    if language == "en":
        _strings = _fallback
    else:
        loaded = _load_json(language)
        if loaded:
            _strings = loaded
        else:
            logger.warning("Locale '%s' not found, falling back to English", language)
            _strings = _fallback


def _load_json(language: str) -> dict[str, str]:
    path = LOCALES_DIR / f"{language}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def t(_key: str, **kwargs) -> str:
    """Return the translated string for *_key*.

    Placeholders like ``{name}`` are replaced via ``str.format_map(kwargs)``.
    Falls back to English, then to the raw key itself.
    """
    text = _strings.get(_key) or _fallback.get(_key) or _key
    if kwargs:
        try:
            text = text.format_map(kwargs)
        except KeyError:
            pass
    return text

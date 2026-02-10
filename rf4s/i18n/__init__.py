"""Internationalization module for RF4S."""

import logging
from pathlib import Path

import i18n

logger = logging.getLogger(__name__)

LOCALES_DIR = str(Path(__file__).resolve().parent / "locales")


def init_locale(language: str) -> None:
    i18n.set("load_path", [LOCALES_DIR])
    i18n.set("locale", language)
    i18n.set("fallback", "en")
    i18n.set("file_format", "json")
    i18n.set("skip_locale_root_data", True)
    i18n.set("enable_memoization", True)


def t(_key: str, **kwargs) -> str:
    return i18n.t(_key, default=_key, **kwargs)

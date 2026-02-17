import sys
from pathlib import Path

import i18n

i18n.set("filename_format", "{locale}.{format}")
i18n.set("file_format", "yml")
i18n.set("fallback", "en")
i18n.set("enable_memoization", True)

if "__compiled__" in globals():
    _i18n_dir = Path(sys.executable).parent / "rf4s" / "i18n"
else:
    _i18n_dir = Path(__file__).parent

i18n.load_path.append(str(_i18n_dir))


def setup(language: str = "en") -> None:
    i18n.set("locale", language)


t = i18n.t

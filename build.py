"""Собирает dist/wrap_deck_names.ankiaddon — файл для AnkiWeb и «Install from file».

.ankiaddon — это обычный zip, где файлы дополнения лежат в корне архива
(без папки wrap_deck_names/). Служебное (__pycache__, meta.json с
личными настройками) в архив не попадает.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "wrap_deck_names"
OUT = ROOT / "dist" / "wrap_deck_names.ankiaddon"
SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {"meta.json"}


def build() -> Path:
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SRC.rglob("*")):
            rel = path.relative_to(SRC)
            if path.is_dir() or path.name in SKIP_FILES:
                continue
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            zf.write(path, rel.as_posix())
    return OUT


if __name__ == "__main__":
    out = build()
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    print(f"{out}  ({out.stat().st_size} bytes)")
    for name in names:
        print("  ", name)

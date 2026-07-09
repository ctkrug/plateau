"""Copy the plateau/ package into site/vendor/ so the static site is self-contained.

The site/ directory is what gets published (e.g. to apps.charliekrug.com/plateau), so it
cannot reach outside itself for the Python source Pyodide loads at runtime. This script is
the site's "build step" — run it before serving or deploying:

    python3 scripts/build_site.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "plateau"
DEST = ROOT / "site" / "vendor" / "plateau"
MANIFEST = ROOT / "site" / "vendor" / "manifest.json"


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)

    manifest = []
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(SRC)
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        manifest.append(str(rel).replace("\\", "/"))

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Copied {len(manifest)} file(s) into {DEST}")


if __name__ == "__main__":
    main()

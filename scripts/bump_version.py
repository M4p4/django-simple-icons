"""Set the package version and add a changelog entry for an icon sync.

Usage::

    python scripts/bump_version.py 16.27.0

Rewrites ``version`` in ``pyproject.toml`` and prepends a release section to
``CHANGELOG.md``. The icon count comes from the regenerated bundle, so run
``download_simple_icons.py`` first.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
ZIP_PATH = ROOT / "src" / "django_simple_icons" / "simple-icons.zip"

VERSION_LINE = re.compile(r'^version = "[^"]*"$', re.MULTILINE)
HEADING = "# Changelog\n"


def icon_count(path: Path) -> int:
    with ZipFile(path) as archive:
        return sum(1 for name in archive.namelist() if name.endswith(".svg"))


def set_version(path: Path, version: str) -> None:
    text = path.read_text()
    new_text, count = VERSION_LINE.subn(f'version = "{version}"', text, count=1)
    if count != 1:
        sys.exit(f"Found {count} version lines in {path}, expected exactly 1")
    path.write_text(new_text)


def add_changelog_entry(path: Path, version: str, icons: int, today: date) -> None:
    text = path.read_text()
    if not text.startswith(HEADING):
        sys.exit(f"{path} does not start with {HEADING!r}")
    if f"\n## {version} " in text:
        sys.exit(f"{path} already has an entry for {version}")

    entry = (
        f"## {version} ({today.isoformat()})\n"
        f"\n"
        f"- Bundled Simple Icons {version} ({icons:,} icons).\n"
        f"\n"
    )
    path.write_text(HEADING + "\n" + entry + text[len(HEADING) :].lstrip("\n"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="New package version, e.g. 16.27.0")
    parser.add_argument("--pyproject", type=Path, default=PYPROJECT)
    parser.add_argument("--changelog", type=Path, default=CHANGELOG)
    parser.add_argument("--zip", type=Path, default=ZIP_PATH, dest="zip_path")
    args = parser.parse_args()

    icons = icon_count(args.zip_path)
    set_version(args.pyproject, args.version)
    add_changelog_entry(args.changelog, args.version, icons, date.today())

    print(f"Bumped to {args.version} with {icons:,} icons")


if __name__ == "__main__":
    main()

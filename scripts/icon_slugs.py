"""List the icon slugs in the bundle, or diff them against an earlier listing.

Usage::

    python scripts/icon_slugs.py > before.txt
    python scripts/icon_slugs.py --since before.txt

The bundle is a binary zip, so a pull request that regenerates it has no
reviewable diff. The ``--since`` mode writes a Markdown summary of which slugs
were added and removed, which is the part a human actually needs to check:
a removed slug is a breaking change for anyone rendering it.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = ROOT / "src" / "django_simple_icons" / "simple-icons.zip"

PREFIX = "icons/"
SUFFIX = ".svg"
MAX_LISTED = 50


def slugs(path: Path) -> set[str]:
    with ZipFile(path) as archive:
        return {
            name[len(PREFIX) : -len(SUFFIX)]
            for name in archive.namelist()
            if name.startswith(PREFIX) and name.endswith(SUFFIX)
        }


def _listing(heading: str, names: list[str]) -> list[str]:
    if not names:
        return []
    lines = [f"### {heading} ({len(names)})", ""]
    shown = names[:MAX_LISTED]
    lines.append(", ".join(f"`{name}`" for name in shown))
    if len(names) > MAX_LISTED:
        lines.append("")
        lines.append(f"...and {len(names) - MAX_LISTED} more.")
    lines.append("")
    return lines


def summarise(before: set[str], after: set[str]) -> str:
    added = sorted(after - before)
    removed = sorted(before - after)

    lines = [f"{len(before):,} icons before, {len(after):,} after.", ""]
    if removed:
        lines.append(
            "**Removed slugs are a breaking change** for anyone rendering them."
        )
        lines.append("")
    lines += _listing("Removed", removed)
    lines += _listing("Added", added)
    if not added and not removed:
        lines.append("No slugs added or removed; icon artwork may still have changed.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--since",
        type=Path,
        help="Compare against a slug listing written by an earlier run",
    )
    parser.add_argument("--zip", type=Path, default=ZIP_PATH, dest="zip_path")
    args = parser.parse_args()

    current = slugs(args.zip_path)
    if args.since is None:
        print("\n".join(sorted(current)))
        return

    before = {
        line.strip() for line in args.since.read_text().splitlines() if line.strip()
    }
    print(summarise(before, current), end="")


if __name__ == "__main__":
    main()

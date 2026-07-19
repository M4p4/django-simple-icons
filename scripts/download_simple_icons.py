"""Regenerate the bundled ``simple-icons.zip`` from a Simple Icons npm release.

Usage::

    python scripts/download_simple_icons.py 16.26.0

The generated zip contains ``icons/<slug>.svg`` for every upstream icon plus a
``data.json`` metadata map ``{slug: {"title": ..., "hex": ...}}``. Output is
deterministic: re-running for the same version produces a byte-identical file,
so the committed zip can be verified by regenerating it.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

TARBALL_URL = "https://registry.npmjs.org/simple-icons/-/simple-icons-{version}.tgz"
# The icon-sync workflow runs this unattended, so a stalled endpoint must fail
# rather than hang until the job timeout.
TIMEOUT = 60
ZIP_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "django_simple_icons"
    / "simple-icons.zip"
)

ICON_PREFIX = "package/icons/"
METADATA_MEMBER = "package/data/simple-icons.json"

# Fixed timestamp for every zip entry — the earliest the zip format can store.
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o644 << 16


def download(version: str) -> bytes:
    url = TARBALL_URL.format(version=version)
    print(f"Downloading {url}")
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as response:  # noqa: S310
            data: bytes = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        sys.exit(f"Failed to download {url}: {exc}")
    return data


def extract(tarball: bytes) -> tuple[dict[str, bytes], dict[str, dict[str, str]]]:
    """Return ``{slug: svg_bytes}`` and the slimmed ``{slug: {title, hex}}`` map."""
    icons: dict[str, bytes] = {}
    metadata_raw: bytes | None = None

    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tar:
        for member in tar:
            if not member.isfile():
                continue
            if member.name == METADATA_MEMBER:
                metadata_raw = _read(tar, member)
            elif member.name.startswith(ICON_PREFIX) and member.name.endswith(".svg"):
                slug = member.name[len(ICON_PREFIX) : -len(".svg")]
                icons[slug] = _read(tar, member)

    if metadata_raw is None:
        sys.exit(f"Tarball does not contain {METADATA_MEMBER}")
    if not icons:
        sys.exit(f"Tarball does not contain any {ICON_PREFIX}*.svg files")

    metadata = {
        icon["slug"]: {"title": icon["title"], "hex": icon["hex"]}
        for icon in json.loads(metadata_raw)
    }

    missing = sorted(set(icons) - set(metadata))
    if missing:
        sys.exit(f"No metadata for {len(missing)} icons: {', '.join(missing[:5])}")

    return icons, metadata


def _read(tar: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    handle = tar.extractfile(member)
    if handle is None:
        sys.exit(f"Could not read {member.name} from the tarball")
    with handle:
        return handle.read()


def write_zip(
    icons: dict[str, bytes], metadata: dict[str, dict[str, str]], path: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode()

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        _write_entry(archive, "data.json", payload)
        for slug in sorted(icons):
            _write_entry(archive, f"icons/{slug}.svg", icons[slug])


def _write_entry(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = FILE_MODE
    archive.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Simple Icons release to bundle, e.g. 16.26.0")
    parser.add_argument(
        "--output",
        type=Path,
        default=ZIP_PATH,
        help=f"Where to write the zip (default: {ZIP_PATH})",
    )
    args = parser.parse_args()

    icons, metadata = extract(download(args.version))
    write_zip(icons, metadata, args.output)

    size_mb = args.output.stat().st_size / 1024 / 1024
    print(
        f"Wrote {args.output} — {len(icons)} icons from Simple Icons {args.version} ({size_mb:.1f} MB)"
    )


if __name__ == "__main__":
    main()

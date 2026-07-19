"""Compare the bundled Simple Icons version against the latest npm release.

Usage::

    python scripts/check_upstream_version.py
    python scripts/check_upstream_version.py --upstream 16.27.0

Prints ``bundled``, ``upstream`` and ``sync`` as ``key=value`` lines, and
appends the same lines to ``$GITHUB_OUTPUT`` when running under Actions.

A non-numeric upstream version (a prerelease, say) reports ``sync=false``
rather than failing, so the scheduled run stays green while upstream is
between stable releases.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

LATEST_URL = "https://registry.npmjs.org/simple-icons/latest"
# The daily workflow runs unattended, so a stalled endpoint must fail rather
# than hang until the job timeout.
TIMEOUT = 30
PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
NUMERIC_VERSION = re.compile(r"\A[0-9]+(?:\.[0-9]+)*\Z")


def bundled_version(path: Path) -> str:
    with path.open("rb") as file:
        pyproject = tomllib.load(file)
    version: str = pyproject["project"]["version"]
    return version


def latest_version() -> str:
    try:
        with urllib.request.urlopen(LATEST_URL, timeout=TIMEOUT) as response:  # noqa: S310
            version: str = json.loads(response.read())["version"]
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError) as exc:
        sys.exit(f"Failed to read the latest version from {LATEST_URL}: {exc}")
    return version


def as_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def is_newer(upstream: str, bundled: str) -> bool:
    """Is ``upstream`` a later release than ``bundled``?

    Both are numeric dotted versions. Our own fixes append a fourth segment,
    so 16.26.0.1 is newer than 16.26.0 and upstream 16.26.0 must not trigger a
    sync back down to it.
    """
    return as_tuple(upstream) > as_tuple(bundled)


def emit(**outputs: str) -> None:
    for key, value in outputs.items():
        # A newline would let a crafted --upstream append further key=value
        # lines to $GITHUB_OUTPUT and invent step outputs.
        if "\n" in value or "\r" in value:
            sys.exit(f"Refusing to emit {key} containing a newline: {value!r}")
        print(f"{key}={value}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as file:
            for key, value in outputs.items():
                file.write(f"{key}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upstream",
        help="Version to compare against instead of querying the npm registry",
    )
    parser.add_argument(
        "--pyproject",
        type=Path,
        default=PYPROJECT,
        help=f"Path to pyproject.toml (default: {PYPROJECT})",
    )
    args = parser.parse_args()

    bundled = bundled_version(args.pyproject)
    if not NUMERIC_VERSION.match(bundled):
        sys.exit(f"Bundled version {bundled!r} is not a numeric dotted version")

    upstream = args.upstream or latest_version()
    if not NUMERIC_VERSION.match(upstream):
        print(f"::notice::ignoring non-numeric upstream version {upstream!r}")
        emit(bundled=bundled, upstream=upstream, sync="false")
        return

    emit(
        bundled=bundled,
        upstream=upstream,
        sync="true" if is_newer(upstream, bundled) else "false",
    )


if __name__ == "__main__":
    main()

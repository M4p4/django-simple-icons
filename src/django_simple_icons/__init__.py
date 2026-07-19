from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from difflib import get_close_matches
from functools import lru_cache
from importlib.resources import files
from typing import Any
from xml.etree import ElementTree
from zipfile import ZipFile

__all__ = ["IconDoesNotExist", "get_brand_color"]

_ICONS_URL = "https://simpleicons.org/"


class IconDoesNotExist(Exception):
    pass


@contextmanager
def _zip_file() -> Iterator[ZipFile]:
    resource = files("django_simple_icons").joinpath("simple-icons.zip")
    with resource.open("rb") as file, ZipFile(file) as archive:
        yield archive


@lru_cache(maxsize=1)
def _load_metadata() -> dict[str, dict[str, str]]:
    with _zip_file() as archive:
        data: dict[str, dict[str, str]] = json.loads(archive.read("data.json"))
    return data


def _unknown_icon(name: str) -> IconDoesNotExist:
    matches = get_close_matches(name, _load_metadata(), n=3)
    suggestion = f" Did you mean: {', '.join(matches)}?" if matches else ""
    return IconDoesNotExist(
        f"Icon {name!r} does not exist.{suggestion}"
        f" Browse the available icons at {_ICONS_URL}"
    )


@lru_cache(maxsize=128)
def _load_icon(name: str) -> ElementTree.Element:
    with _zip_file() as archive:
        try:
            svg_bytes = archive.read(f"icons/{name}.svg")
        except KeyError:
            raise _unknown_icon(name) from None

    svg = ElementTree.fromstring(svg_bytes.decode())
    # Parsing resolves the xmlns declaration into '{ns}tag' names; undo that so
    # the icon serializes as plain inline SVG.
    for element in svg.iter():
        _, _, element.tag = element.tag.rpartition("}")
    return svg


def get_brand_color(name: str) -> str:
    """Return the official brand color of ``name`` as ``"#RRGGBB"``."""
    try:
        hex_ = _load_metadata()[name]["hex"]
    except KeyError:
        raise _unknown_icon(name) from None
    return f"#{hex_}"


def _render_icon(
    name: str,
    *,
    size: int | None,
    color: str,
    title: str | bool,
    attrs: dict[str, Any],
) -> str:
    svg = deepcopy(_load_icon(name))

    if size is not None:
        svg.set("width", str(size))
        svg.set("height", str(size))

    if color == "brand":
        svg.set("fill", get_brand_color(name))
    else:
        svg.set("fill", str(color))

    title_element = svg.find("title")
    assert title_element is not None  # every Simple Icon ships a <title>
    if title is False:
        # Decorative by default: no accessible name, hidden from screen readers.
        svg.remove(title_element)
        svg.attrib.pop("role", None)
        svg.set("aria-hidden", "true")
    elif title is not True:
        # str(): markupsafe.Markup overrides replace() to escape its arguments,
        # which would double-escape ElementTree's own serialization.
        title_element.text = str(title)

    for key, value in attrs.items():
        svg.set(key.replace("_", "-"), str(value))

    # Tags carry no namespace after _load_icon(), so no xmlns is serialized —
    # inline SVG inherits it from the surrounding HTML document anyway.
    return ElementTree.tostring(svg, encoding="unicode")

from __future__ import annotations

from markupsafe import Markup

from django_simple_icons import _render_icon


def simple_icon(
    name: str,
    *,
    size: int | None = 24,
    color: str = "currentColor",
    title: str | bool = False,
    **attrs: object,
) -> Markup:
    return Markup(_render_icon(name, size=size, color=color, title=title, attrs=attrs))

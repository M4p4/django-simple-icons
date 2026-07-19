from __future__ import annotations

from django import template
from django.utils.safestring import mark_safe

from django_simple_icons import _render_icon

register = template.Library()


@register.simple_tag
def simple_icon(
    name: str,
    *,
    size: int | None = 24,
    color: str = "currentColor",
    title: str | bool = False,
    **attrs: object,
) -> str:
    # simple_tag marks string literals parsed from the template as safe, but
    # they aren't. No un-marking is needed: the renderer serializes through
    # ElementTree, which escapes str subclasses like any other string, and
    # returns a plain str. test_safe_string_arguments_are_still_escaped guards
    # this.
    return mark_safe(
        _render_icon(name, size=size, color=color, title=title, attrs=attrs)
    )

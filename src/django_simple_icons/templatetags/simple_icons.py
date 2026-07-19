from __future__ import annotations

from django import template
from django.utils.safestring import SafeString, mark_safe

from django_simple_icons import _render_icon

register = template.Library()


def _unsafe[T](value: T) -> T | str:
    # simple_tag's parsing loads passed strings as safe, but they aren't.
    # Cast the SafeString's back to normal strings the only way possible, by
    # concatenating the empty string.
    return value + "" if isinstance(value, SafeString) else value


@register.simple_tag
def simple_icon(
    name: str,
    *,
    size: int | None = 24,
    color: str = "currentColor",
    title: str | bool = False,
    **attrs: object,
) -> str:
    return mark_safe(
        _render_icon(
            _unsafe(name),
            size=size,
            color=_unsafe(color),
            title=_unsafe(title),
            attrs={key: _unsafe(value) for key, value in attrs.items()},
        )
    )

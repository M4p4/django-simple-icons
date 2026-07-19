from __future__ import annotations

import pytest
from markupsafe import Markup

from django_simple_icons import (
    IconDoesNotExist,
    _load_icon,
    _render_icon,
    get_brand_color,
)

DJANGO_HEX = "#092E20"


def render(name="django", *, size=24, color="currentColor", title=False, **attrs):
    return _render_icon(name, size=size, color=color, title=title, attrs=attrs)


class TestLoadIcon:
    def test_unknown_icon_raises(self):
        with pytest.raises(IconDoesNotExist) as excinfo:
            _load_icon("not-an-icon-at-all")

        assert "'not-an-icon-at-all' does not exist" in str(excinfo.value)

    def test_unknown_icon_suggests_close_matches(self):
        with pytest.raises(IconDoesNotExist) as excinfo:
            _load_icon("djngo")

        assert "Did you mean: django" in str(excinfo.value)

    def test_unknown_icon_links_to_the_icon_grid(self):
        with pytest.raises(IconDoesNotExist) as excinfo:
            _load_icon("zzzzzzzzzzzz")

        message = str(excinfo.value)
        assert "Did you mean" not in message
        assert "https://simpleicons.org/" in message

    def test_result_is_cached(self):
        assert _load_icon("django") is _load_icon("django")

    def test_rendering_does_not_mutate_the_cached_element(self):
        cached = _load_icon("github")
        before = len(cached), dict(cached.attrib)

        render("github", size=48, color="brand", title="Changed", class_="mr-2")

        assert (len(cached), dict(cached.attrib)) == before


class TestRender:
    def test_default(self):
        result = render()

        assert result.startswith(
            '<svg viewBox="0 0 24 24" width="24" height="24"'
            ' fill="currentColor" aria-hidden="true">'
        )
        assert "<title>" not in result
        assert "role=" not in result

    def test_no_xmlns_declaration(self):
        assert "xmlns" not in render()

    def test_size(self):
        assert 'width="48" height="48"' in render(size=48)

    def test_size_none_omits_dimensions(self):
        result = render(size=None)

        assert "width=" not in result
        assert "height=" not in result

    def test_color_brand(self):
        assert f'fill="{DJANGO_HEX}"' in render(color="brand")

    def test_color_passed_through(self):
        assert 'fill="rebeccapurple"' in render(color="rebeccapurple")

    def test_title_true_keeps_upstream_title(self):
        result = render(title=True)

        assert "<title>Django</title>" in result
        assert 'role="img"' in result
        assert "aria-hidden" not in result

    def test_title_string_replaces_upstream_title(self):
        result = render(title="Powered by Django")

        assert "<title>Powered by Django</title>" in result
        assert 'role="img"' in result

    def test_title_str_subclass_is_escaped_once(self):
        result = render(title=Markup("a < 2"))

        assert "<title>a &lt; 2</title>" in result

    def test_title_none_leaves_the_title_empty(self):
        result = render(title=None)

        assert "<title />" in result
        assert "None" not in result

    def test_color_none_is_rejected(self):
        with pytest.raises(TypeError):
            render(color=None)

    def test_attrs_underscores_become_dashes(self):
        assert 'data-controller="icon"' in render(data_controller="icon")

    def test_attrs_trailing_underscore_is_stripped(self):
        assert 'class="mr-2"' in render(class_="mr-2")

    def test_attrs_values_are_stringified(self):
        assert 'tabindex="-1"' in render(tabindex=-1)

    def test_attrs_values_are_escaped(self):
        assert 'data-test="a &lt; 2"' in render(data_test="a < 2")


class TestGetBrandColor:
    def test_returns_hex(self):
        assert get_brand_color("django") == DJANGO_HEX

    def test_unknown_icon_raises(self):
        with pytest.raises(IconDoesNotExist) as excinfo:
            get_brand_color("djngo")

        assert "Did you mean: django" in str(excinfo.value)

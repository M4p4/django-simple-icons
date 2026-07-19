from __future__ import annotations

import pytest
from jinja2 import Environment
from markupsafe import Markup

from django_simple_icons import IconDoesNotExist
from django_simple_icons.jinja import simple_icon

DJANGO_HEX = "#092E20"

environment = Environment(autoescape=True)
environment.globals["simple_icon"] = simple_icon


def render(template_string, **context):
    return environment.from_string(template_string).render(**context)


class TestSimpleIcon:
    def test_default(self):
        result = render('{{ simple_icon("django") }}')

        assert result.startswith(
            '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"'
            ' aria-hidden="true"><path d="M11.146 0h3.924'
        )
        assert result.endswith("/></svg>")
        assert "<title>" not in result
        assert "role=" not in result

    def test_result_is_markup(self):
        assert isinstance(simple_icon("django"), Markup)

    def test_size(self):
        result = render('{{ simple_icon("django", size=48) }}')

        assert 'width="48" height="48"' in result

    def test_size_none_omits_dimensions(self):
        result = render('{{ simple_icon("django", size=None) }}')

        assert "width=" not in result
        assert "height=" not in result

    def test_class_attribute(self):
        result = render('{{ simple_icon("django", **{"class": "mr-2 h-6"}) }}')

        assert 'class="mr-2 h-6"' in result

    def test_data_attribute_underscores_become_dashes(self):
        result = render('{{ simple_icon("django", data_controller="icon") }}')

        assert 'data-controller="icon"' in result

    def test_attribute_values_are_escaped(self):
        result = render('{{ simple_icon("django", data_test="a < 2") }}')

        assert 'data-test="a &lt; 2"' in result

    def test_color_brand(self):
        result = render('{{ simple_icon("django", color="brand") }}')

        assert f'fill="{DJANGO_HEX}"' in result

    def test_color_custom(self):
        result = render('{{ simple_icon("django", color="#123456") }}')

        assert 'fill="#123456"' in result

    def test_title_true_keeps_upstream_title(self):
        result = render('{{ simple_icon("django", title=True) }}')

        assert "<title>Django</title>" in result
        assert 'role="img"' in result
        assert "aria-hidden" not in result

    def test_title_string_replaces_upstream_title(self):
        result = render('{{ simple_icon("django", title="View source") }}')

        assert "<title>View source</title>" in result

    def test_unknown_icon_raises(self):
        with pytest.raises(IconDoesNotExist) as excinfo:
            render('{{ simple_icon("djngo") }}')

        assert "Did you mean: django" in str(excinfo.value)

    def test_markup_arguments_are_still_escaped(self):
        result = render(
            "{{ simple_icon(name, color=color, title=title, data_test=attr) }}",
            name=Markup("django"),
            color=Markup("#123456"),
            title=Markup("a < 2"),
            attr=Markup("a < 2"),
        )

        assert 'fill="#123456"' in result
        assert "<title>a &lt; 2</title>" in result
        assert 'data-test="a &lt; 2"' in result

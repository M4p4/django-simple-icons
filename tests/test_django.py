from __future__ import annotations

import django
import pytest
from django.conf import settings
from django.template import Context, Template
from django.utils.safestring import SafeString, mark_safe

from django_simple_icons import IconDoesNotExist

settings.configure(
    INSTALLED_APPS=["django_simple_icons"],
    TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}],
)
django.setup()

DJANGO_HEX = "#092E20"


def render(template_string, **context):
    return Template(template_string).render(Context(context))


class TestSimpleIcon:
    def test_default(self):
        result = render('{% load simple_icons %}{% simple_icon "django" %}')

        assert result.startswith(
            '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"'
            ' aria-hidden="true"><path d="M11.146 0h3.924'
        )
        assert result.endswith("/></svg>")
        assert "<title>" not in result
        assert "role=" not in result

    def test_result_is_marked_safe(self):
        result = render('{% load simple_icons %}{% simple_icon "django" %}')

        assert isinstance(result, SafeString)

    def test_size(self):
        result = render('{% load simple_icons %}{% simple_icon "django" size=48 %}')

        assert 'width="48" height="48"' in result

    def test_size_none_omits_dimensions(self):
        result = render('{% load simple_icons %}{% simple_icon "django" size=None %}')

        assert "width=" not in result
        assert "height=" not in result

    def test_class_attribute(self):
        result = render(
            '{% load simple_icons %}{% simple_icon "django" class="mr-2 h-6" %}'
        )

        assert 'class="mr-2 h-6"' in result

    def test_data_attribute_underscores_become_dashes(self):
        result = render(
            '{% load simple_icons %}{% simple_icon "django" data_controller="icon" %}'
        )

        assert 'data-controller="icon"' in result

    def test_attribute_values_are_escaped(self):
        result = render(
            '{% load simple_icons %}{% simple_icon "django" data_test="a < 2" %}'
        )

        assert 'data-test="a &lt; 2"' in result

    def test_color_brand(self):
        result = render(
            '{% load simple_icons %}{% simple_icon "django" color="brand" %}'
        )

        assert f'fill="{DJANGO_HEX}"' in result

    def test_color_custom(self):
        result = render(
            '{% load simple_icons %}{% simple_icon "django" color="#123456" %}'
        )

        assert 'fill="#123456"' in result

    def test_title_true_keeps_upstream_title(self):
        result = render('{% load simple_icons %}{% simple_icon "django" title=True %}')

        assert "<title>Django</title>" in result
        assert 'role="img"' in result
        assert "aria-hidden" not in result

    def test_title_string_replaces_upstream_title(self):
        result = render(
            '{% load simple_icons %}{% simple_icon "django" title="View source" %}'
        )

        assert "<title>View source</title>" in result

    def test_unknown_icon_raises(self):
        with pytest.raises(IconDoesNotExist) as excinfo:
            render('{% load simple_icons %}{% simple_icon "djngo" %}')

        assert "Did you mean: django" in str(excinfo.value)

    def test_safe_string_arguments_are_still_escaped(self):
        result = render(
            "{% load simple_icons %}"
            "{% simple_icon name color=color title=title data_test=attr %}",
            name=mark_safe("django"),
            color=mark_safe("#123456"),
            title=mark_safe("a < 2"),
            attr=mark_safe("a < 2"),
        )

        assert 'fill="#123456"' in result
        assert "<title>a &lt; 2</title>" in result
        assert 'data-test="a &lt; 2"' in result

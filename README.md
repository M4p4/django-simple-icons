# django-simple-icons

[![PyPI version](https://img.shields.io/pypi/v/django-simple-icons.svg)](https://pypi.org/project/django-simple-icons/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-simple-icons.svg)](https://pypi.org/project/django-simple-icons/)
[![CI](https://github.com/M4p4/django-simple-icons/actions/workflows/main.yml/badge.svg)](https://github.com/M4p4/django-simple-icons/actions/workflows/main.yml)

Use [Simple Icons](https://simpleicons.org/), more than 3,400 SVG brand icons, in your
Django and Jinja templates. The icons ship inside the package, so there is no CDN to
call and no static files to collect. Each icon renders as inline SVG that follows the
surrounding text color.

## Installation

Install with the extra matching your template engine:

```console
python -m pip install 'django-simple-icons[django]'
python -m pip install 'django-simple-icons[jinja]'
```

The package itself has no runtime dependencies and needs Python 3.12 or later.

## Django

Add the app to `INSTALLED_APPS` so the template tag library can be loaded:

```python
INSTALLED_APPS = [
    ...,
    "django_simple_icons",
]
```

Then load the library and render an icon by its slug:

```html
{% load simple_icons %}

{% simple_icon "django" %}
```

That produces a 24x24 inline SVG which inherits the current text color and is hidden
from screen readers:

```html
<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true"><path d="M11.146 0h3.924…"/></svg>
```

### Sizing

`size` sets both `width` and `height` and defaults to 24:

```html
{% simple_icon "django" size=48 %}
```

Pass `size=None` to omit both attributes, which is what you want when CSS classes
control the size:

```html
{% simple_icon "django" size=None class="h-6 w-6" %}
```

### Color

Icons use `fill="currentColor"` by default, so they follow the surrounding text. Pass
`color="brand"` to use the brand's official color, or any CSS color to set it directly:

```html
{% simple_icon "django" color="brand" %}
{% simple_icon "django" color="#ff6600" %}
```

### Extra attributes

Any other keyword argument becomes an attribute on the `<svg>` element, with
underscores converted to dashes:

```html
{% simple_icon "django" class="h-6 w-6 text-green-700" data_controller="icon" %}
```

```html
<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true" class="h-6 w-6 text-green-700" data-controller="icon"><path d="M11.146 0h3.924…"/></svg>
```

Values are escaped, so `data_test="a < 2"` renders as `data-test="a &lt; 2"`.

### Accessibility

Icons are decorative by default, so the upstream `<title>` is removed and
`aria-hidden="true"` is set. An icon next to a text label needs nothing more.

For a standalone icon that carries meaning, pass `title=True` to keep the brand name as
the accessible name, or pass a string to replace it:

```html
{% simple_icon "django" title=True %}
{% simple_icon "django" title="Django framework" %}
```

Either form keeps `role="img"` and drops `aria-hidden`:

```html
<svg role="img" viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><title>Django framework</title><path d="M11.146 0h3.924…"/></svg>
```

## Jinja

Register the function as a global on your environment:

```python
from django_simple_icons.jinja import simple_icon

environment.globals["simple_icon"] = simple_icon
```

Call it with the same arguments as the Django tag:

```jinja
{{ simple_icon("django") }}
{{ simple_icon("django", size=48, color="brand") }}
{{ simple_icon("django", title="Django framework") }}
```

The result is a `markupsafe.Markup`, so it renders unescaped under autoescaping.

Because `class` is a reserved word in Python, spell it `class_` when calling the
function directly. The trailing underscore is stripped:

```jinja
{{ simple_icon("django", class_="h-6 w-6") }}
```

## Arguments

| Argument  | Default          | Description                                                |
| --------- | ---------------- | ---------------------------------------------------------- |
| `name`    | required         | The icon slug, such as `"django"`                           |
| `size`    | `24`             | Sets `width` and `height`; `None` omits both                |
| `color`   | `"currentColor"` | Any CSS color, or `"brand"` for the brand's official color  |
| `title`   | `False`          | `True` keeps the brand name, a string replaces it           |
| `**attrs` | none             | Extra attributes; underscores become dashes                 |

## Brand colors

`get_brand_color` returns a brand's official color, which is useful outside a template:

```pycon
>>> from django_simple_icons import get_brand_color
>>> get_brand_color("django")
'#092E20'
```

## Finding icon slugs

Slugs match the names on [simpleicons.org](https://simpleicons.org/), where you can
search the full set. An unknown slug raises `IconDoesNotExist` with suggestions:

```pycon
>>> from django_simple_icons import get_brand_color
>>> get_brand_color("djngo")
Traceback (most recent call last):
  ...
django_simple_icons.IconDoesNotExist: Icon 'djngo' does not exist. Did you mean: django, deno, fandango? Browse the available icons at https://simpleicons.org/
```

## Supported versions

- Python 3.12, 3.13 and 3.14
- Django 5.2, 6.0 and 6.1 are tested. Django is declared as `>=4.2` because the code
  uses nothing newer, but only the tested versions are supported.
- Jinja2 2.8 and later

## Versioning

The package version mirrors the bundled Simple Icons release, so version 16.26.0
contains Simple Icons 16.26.0. A fix to this package that ships no new icons appends a
fourth segment, such as 16.26.0.1.

## License

The code in this package is MIT licensed. The icons come from Simple Icons and are
[CC0-1.0](https://github.com/simple-icons/simple-icons/blob/master/LICENSE.md).

Brand icons and names are trademarks of their respective owners. Using an icon does not
imply endorsement, and some brands restrict how their marks may be used. Read the
[Simple Icons legal disclaimer](https://github.com/simple-icons/simple-icons/blob/master/DISCLAIMER.md)
before shipping an icon.

# Changelog

## 16.27.0 (2026-07-19)

- Bundled Simple Icons 16.27.0 (3,450 icons).

## 16.26.0 (2026-07-19)

First release, bundling Simple Icons 16.26.0 (3,449 icons).

- `{% simple_icon %}` template tag for Django, with `size`, `color`, `title` and
  arbitrary extra attributes.
- Matching `simple_icon` function for Jinja, returning `markupsafe.Markup`.
- `get_brand_color` for looking up a brand's official color.
- `IconDoesNotExist` carries close-match suggestions for mistyped slugs.
- Icons render as inline SVG with no runtime dependencies, no CDN and no static files.

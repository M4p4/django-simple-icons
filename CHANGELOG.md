# Changelog

## 16.29.0 (2026-08-29)

- Bundled Simple Icons 16.29.0 (3,457 icons).

## 16.28.0 (2026-08-03)

- Bundled Simple Icons 16.28.0 (3,453 icons).

## 16.27.1 (2026-07-30)

- Bundled Simple Icons 16.27.1 (3,450 icons).

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

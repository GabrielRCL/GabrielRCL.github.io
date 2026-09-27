# gabrielrcl.github.io

Personal site of Gabriel Lucas, Odoo developer: <https://gabrielrcl.github.io>.

One HTML page, CSS and a few lines of JavaScript. No framework, no tracking, no cookies.

## Build

```bash
python tools/build_wire.py     # partials/wire.html: the protocol samples (fictitious data)
python tools/build.py          # index.html, with the icon sprite and partials inlined
```

- `page.src.html` is the source of the page; `<!--INCLUDE:...-->` pulls in `partials/`.
- `tools/build_sprite.py` rebuilds `tools/sprite.svg` from Simple Icons (CC0) and Lucide (ISC).
- `tools/build_stack_logos.py` rebuilds the colored logos in `assets/stack/` (Devicon, MIT).
- `cv/cv-en.html` and `cv/cv-pt.html` are printed to `assets/cv/*.pdf`.

Brand logos belong to their owners and are used only to name the technologies and companies I work with.

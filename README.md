# gabrielrcl.dev

Personal site of Gabriel Lucas, Odoo developer: <https://gabrielrcl.dev>.

One HTML page, CSS and a few lines of JavaScript. No framework, no tracking, no cookies.

## Build

```bash
python tools/build.py          # index.html and links/index.html, with the icon sprite and partials inlined
```

- `page.src.html` is the source of the page and `links.src.html` of `/links/`, the link-in-bio page; `<!--INCLUDE:...-->` pulls in `partials/` (`base.css` and `flags.svg` are shared by both).
- `partials/motion.css` and `partials/motion.js` are the scroll scenes: each scene gets a `--p` from 0 to 1 as it enters. Scrolling stays native, and viewers who ask for reduced motion get the static page.
- `tools/build_og.py` renders `assets/og.jpg`, the image shown when the link is shared, and the favicons, from the cartoon portrait in `tools/src/`.
- `tools/build_sprite.py` rebuilds `tools/sprite.svg` from Simple Icons (CC0) and Lucide (ISC).
- `tools/build_stack_logos.py` rebuilds the colored logos in `assets/stack/` (Devicon, MIT).
- `tools/build_icons.py` rebuilds the logo tiles of the work cards and the hero wire: the NX mark, the NFS-e Nacional wordmark (official logo from gov.br/nfse), the bank cluster, the Odoo CRM icon and the coffee mug.
- `cv/cv-en.html` and `cv/cv-pt.html` are printed to `assets/cv/*.pdf`.

Brand logos belong to their owners and are used only to name the technologies and companies I work with.

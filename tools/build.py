"""Build the site pages.

- page.src.html -> index.html (GitHub Pages) and page.html (the Claude artifact preview, images inlined).
- links.src.html -> links/index.html (gabrielrcl.dev/links/, the link-in-bio page).
- --stage DIR: also copy page.html and assets/ into DIR (the artifact tool only publishes from
  the workspace or the session scratchpad).

Fails if a page references an icon id the sprite does not define, or a local file that does not exist.
"""
import argparse
import base64
import os
import re
import shutil
import stat
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (source, output, also write the inlined artifact preview)
PAGES = [("page.src.html", "index.html", True), ("links.src.html", os.path.join("links", "index.html"), False)]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".ico": "image/x-icon"}


def data_uri(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        payload = base64.b64encode(f.read()).decode("ascii")
    return f"data:{MIME[os.path.splitext(rel)[1].lower()]};base64,{payload}"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build(src_name, out_name, sprite):
    src = read(os.path.join(ROOT, src_name))
    src = re.sub(r"<!--INCLUDE:([^>]+?)-->", lambda m: read(os.path.join(ROOT, m.group(1).strip())), src)

    defined = set(re.findall(r'<symbol id="([^"]+)"', sprite)) | set(re.findall(r'<symbol id="([^"]+)"', src))
    used = set(re.findall(r'href="#((?:si|lu|flag)-[^"]+)"', src))
    missing = sorted(used - defined)
    if missing:
        sys.exit(f"{src_name}: missing icons: " + ", ".join(missing))

    # local files, resolved from where the built page is served
    base = os.path.dirname(os.path.join(ROOT, out_name))
    refs = set(re.findall(r'(?:src|href)="((?:\.\./)?assets/[^"#]+)"', src))
    absent = sorted(r for r in refs if not os.path.exists(os.path.normpath(os.path.join(base, r))))
    if absent:
        sys.exit(f"{src_name}: missing files: " + ", ".join(absent))

    head, marker, body = src.partition("<!--ICON_SPRITE-->")
    if not marker:
        sys.exit(f"{src_name}: no <!--ICON_SPRITE--> where the body starts")
    page = head + sprite + body
    # An explicit head and body: LinkedIn's link preview reads the Open Graph tags only inside <head>,
    # and without one it built the preview from a section title and the first logo it found.
    write(os.path.join(ROOT, out_name), '<!doctype html>\n<html lang="en">\n<head>\n' + head.strip() + "\n</head>\n<body>\n" + sprite + body.rstrip() + "\n</body>\n</html>\n")
    print(f"{out_name} {len(page)} bytes, {len(used)} icons, {len(refs)} local files")
    return page


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage")
    args = parser.parse_args()
    sprite = read(os.path.join(ROOT, "tools", "sprite.svg"))

    for src_name, out_name, preview in PAGES:
        page = build(src_name, out_name, sprite)
        if preview:
            # GitHub Pages serves assets/ next to index.html. The artifact preview inlines every image:
            # its phone viewer does not resolve the supporting files, and a self-contained page renders anywhere.
            inlined = re.sub(r'src="(assets/[^"]+)"', lambda m: f'src="{data_uri(m.group(1))}"', page)
            write(os.path.join(ROOT, "page.html"), inlined)
            print(f"page.html {len(inlined)} bytes (images inlined)")

    if args.stage:
        os.makedirs(args.stage, exist_ok=True)
        shutil.copy(os.path.join(ROOT, "page.html"), os.path.join(args.stage, "page.html"))
        dst = os.path.join(args.stage, "assets")
        if os.path.exists(dst):
            # files copied out of OneDrive keep their read-only bit, which stops a plain rmtree
            shutil.rmtree(dst, onexc=lambda func, path, _: (os.chmod(path, stat.S_IWRITE), func(path)))
        shutil.copytree(os.path.join(ROOT, "assets"), dst)
        print("staged in", args.stage, sorted(os.listdir(dst)))


if __name__ == "__main__":
    main()

"""Build the site from page.src.html.

- page.html: the page with the icon sprite inlined (what the Claude artifact preview serves).
- index.html: the same page with a doctype, for GitHub Pages.
- --stage DIR: also copy page.html and assets/ into DIR (the artifact tool only publishes from
  the workspace or the session scratchpad).

Fails if the page references an icon id the sprite does not define.
"""
import argparse
import base64
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".ico": "image/x-icon"}


def data_uri(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        payload = base64.b64encode(f.read()).decode("ascii")
    return f"data:{MIME[os.path.splitext(rel)[1].lower()]};base64,{payload}"


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage")
    args = parser.parse_args()

    src = read(os.path.join(ROOT, "page.src.html"))
    src = re.sub(r"<!--INCLUDE:([^>]+?)-->", lambda m: read(os.path.join(ROOT, m.group(1).strip())), src)
    sprite = read(os.path.join(ROOT, "tools", "sprite.svg"))

    defined = set(re.findall(r'<symbol id="([^"]+)"', sprite)) | set(re.findall(r'<symbol id="([^"]+)"', src))
    used = set(re.findall(r'href="#((?:si|lu|flag)-[^"]+)"', src))
    missing = sorted(used - defined)
    if missing:
        sys.exit("missing icons: " + ", ".join(missing))

    assets = set(re.findall(r'src="(assets/[^"]+)"', src))
    absent = sorted(a for a in assets if not os.path.exists(os.path.join(ROOT, a)))
    if absent:
        sys.exit("missing assets: " + ", ".join(absent))

    page = src.replace("<!--ICON_SPRITE-->", sprite)
    # GitHub Pages serves assets/ next to index.html. The artifact preview inlines every image:
    # its phone viewer does not resolve the supporting files, and a self-contained page renders anywhere.
    write(os.path.join(ROOT, "index.html"), '<!doctype html>\n<html lang="en">\n' + page + "\n</html>\n")
    inlined = re.sub(r'src="(assets/[^"]+)"', lambda m: f'src="{data_uri(m.group(1))}"', page)
    write(os.path.join(ROOT, "page.html"), inlined)
    print(f"page.html {len(inlined)} bytes (images inlined), index.html {len(page)} bytes, {len(used)} icons, {len(assets)} assets")

    if args.stage:
        os.makedirs(args.stage, exist_ok=True)
        shutil.copy(os.path.join(ROOT, "page.html"), os.path.join(args.stage, "page.html"))
        dst = os.path.join(args.stage, "assets")
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(os.path.join(ROOT, "assets"), dst)
        print("staged in", args.stage, sorted(os.listdir(dst)))


if __name__ == "__main__":
    main()

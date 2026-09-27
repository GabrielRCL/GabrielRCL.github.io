"""Download the SVG icons the site uses and write them as one inline sprite.

Brand marks come from Simple Icons (CC0), UI icons from Lucide (ISC), the
library the NexView brand manual recommends. Output: tools/sprite.svg, which
build.py inlines into the page so it needs no external icon library.
"""
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@15/icons/{}.svg"
LUCIDE = "https://cdn.jsdelivr.net/npm/lucide-static@0.544.0/icons/{}.svg"

BRANDS = """
python odoo postgresql fastapi linux docker git claude anthropic stripe bitdefender telegram
whatsapp meta django flask sqlalchemy nextdotjs react nodedotjs javascript tailwindcss mysql
mongodb selenium autohotkey cloudflare railway vercel hetzner googlecloud raspberrypi tailscale
vmware c bitcoin kubernetes argo terraform redis lua xampp openjdk umbrel modelcontextprotocol
github discord gnubash resend pydantic vite express sqlite instagram
""".split()

UI = """
landmark receipt-text file-text activity bot sparkles life-buoy database arrow-right-left mail
linkedin copy check arrow-up-right server gamepad-2 cpu bitcoin zap graduation-cap languages
globe map-pin code-xml terminal shield layers network credit-card key-round users user plug
workflow wallet monitor-cog cloud headset store package briefcase-business house calendar
refresh-cw lock message-square-text layout-dashboard x chevron-left chevron-right file-down book-open-text maximize-2 coffee arrow-up
""".split()


def get(url, attempts=4):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except (TimeoutError, OSError):
            if i == attempts - 1:
                raise
            time.sleep(2 * (i + 1))


def inner(svg):
    body = re.sub(r"^.*?<svg[^>]*>", "", svg, flags=re.S)
    body = re.sub(r"</svg>\s*$", "", body.strip(), flags=re.S)
    return re.sub(r"<title>.*?</title>", "", body, flags=re.S).strip()


def main():
    symbols = []
    for slug in BRANDS:
        svg = get(SIMPLE.format(slug))
        symbols.append(f'<symbol id="si-{slug}" viewBox="0 0 24 24"><g fill="currentColor">{inner(svg)}</g></symbol>')
    for name in UI:
        svg = get(LUCIDE.format(name))
        body = inner(svg)
        symbols.append(
            f'<symbol id="lu-{name}" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{body}</g></symbol>'
        )
    sprite = '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">' + "".join(symbols) + "</svg>"
    path = os.path.join(HERE, "sprite.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(sprite)
    print(len(symbols), "symbols,", len(sprite), "bytes ->", path)


if __name__ == "__main__":
    main()

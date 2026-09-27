"""Build the colored logos of the Stack chips into assets/stack/.

Three sources, one look (a small rounded "app icon" per chip):
- devicon originals (colored, transparent) -> shown on a white tile by CSS (class "logo").
- brand-colored app tiles built from Simple Icons / Lucide paths in tools/sprite.svg ("logo app").
- real favicons of banks and local vendors, via Google's favicon service ("logo app").
"""
import io
import os
import re
import time
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "stack")
DEVICON = "https://cdn.jsdelivr.net/npm/devicon@2.16.0/icons/{}.svg"

DEVICONS = {
    "python": "python/python-original", "postgresql": "postgresql/postgresql-original",
    "fastapi": "fastapi/fastapi-original", "django": "django/django-plain",
    "linux": "linux/linux-original", "docker": "docker/docker-original", "git": "git/git-original",
    "react": "react/react-original", "nodejs": "nodejs/nodejs-original", "sqlite": "sqlite/sqlite-original",
    "cloudflare": "cloudflare/cloudflare-original", "flask": "flask/flask-original",
    "sqlalchemy": "sqlalchemy/sqlalchemy-original", "nextjs": "nextjs/nextjs-original",
    "vite": "vitejs/vitejs-original", "javascript": "javascript/javascript-original",
    "tailwind": "tailwindcss/tailwindcss-original", "mysql": "mysql/mysql-original",
    "mongodb": "mongodb/mongodb-original", "selenium": "selenium/selenium-original",
    "lua": "lua/lua-original", "java": "java/java-original", "googlecloud": "googlecloud/googlecloud-original",
    "c": "c/c-original", "kubernetes": "kubernetes/kubernetes-original", "argocd": "argocd/argocd-original",
    "terraform": "terraform/terraform-original", "redis": "redis/redis-original",
    "aws": "amazonwebservices/amazonwebservices-original-wordmark", "bash": "bash/bash-original",
}

# name: (sprite symbol id, tile background, glyph color)
TILES = {
    "whatsapp": ("si-whatsapp", "#25D366", "#FFFFFF"),
    "stripe": ("si-stripe", "#635BFF", "#FFFFFF"),
    "telegram": ("si-telegram", "#26A5E4", "#FFFFFF"),
    "claude": ("si-claude", "#D97757", "#FFFFFF"),
    "anthropic": ("si-anthropic", "#F0EEE6", "#191919"),
    "bitdefender": ("si-bitdefender", "#ED1C24", "#FFFFFF"),
    "hetzner": ("si-hetzner", "#D50C2D", "#FFFFFF"),
    "vercel": ("si-vercel", "#000000", "#FFFFFF"),
    "railway": ("si-railway", "#0B0D0E", "#FFFFFF"),
    "xampp": ("si-xampp", "#FB7A24", "#FFFFFF"),
    "vmware": ("si-vmware", "#607078", "#FFFFFF"),
    "meta": ("si-meta", "#FFFFFF", "#0668E1"),
    "mcp": ("si-modelcontextprotocol", "#FFFFFF", "#000000"),
    "tailscale": ("si-tailscale", "#FFFFFF", "#242424"),
    "cnab": ("lu-file-text", "#1B4FD8", "#FFFFFF"),
    "nfse": ("lu-receipt-text", "#1B4FD8", "#FFFFFF"),
    "systemd": ("lu-terminal", "#0B1530", "#FFFFFF"),
    "x86": ("lu-cpu", "#0B1530", "#FFFFFF"),
}

FAVICONS = {
    "sicoob": "sicoob.com.br", "inter": "inter.co", "itau": "itau.com.br",
    "webposto": "qualityautomacao.com.br", "highlevel": "gohighlevel.com", "autohotkey": "autohotkey.com",
}


def get(url, binary=False, attempts=4):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                return data if binary else data.decode("utf-8")
        except (TimeoutError, OSError):
            if i == attempts - 1:
                raise
            time.sleep(2 * (i + 1))


def clean_svg(svg):
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    return re.sub(r"<!DOCTYPE[^>]*>", "", svg).strip()


def tile_svg(symbol_body, bg, fg, stroke):
    paint = (f'fill="none" stroke="{fg}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"'
             if stroke else f'fill="{fg}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="5.5" fill="{bg}"/>'
            f'<g transform="translate(4.8 4.8) scale(0.6)"><g {paint}>{symbol_body}</g></g></svg>')


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, path in DEVICONS.items():
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(clean_svg(get(DEVICON.format(path))))

    sprite = open(os.path.join(ROOT, "tools", "sprite.svg"), encoding="utf-8").read()
    for name, (sym, bg, fg) in TILES.items():
        m = re.search(rf'<symbol id="{re.escape(sym)}" viewBox="0 0 24 24"><g [^>]*>(.*?)</g></symbol>', sprite, re.S)
        if not m:
            raise SystemExit(f"symbol {sym} not in sprite")
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(tile_svg(m.group(1), bg, fg, stroke=sym.startswith("lu-")))

    fallback = {"webposto": ("lu-database", "#0B1530", "#FFFFFF"), "highlevel": ("lu-plug", "#0B1530", "#FFFFFF")}
    for name, domain in FAVICONS.items():
        try:
            data = get(f"https://www.google.com/s2/favicons?domain={domain}&sz=128", binary=True, attempts=2)
            im = Image.open(io.BytesIO(data)).convert("RGBA")
            im.thumbnail((64, 64), Image.LANCZOS)
            im.save(os.path.join(OUT, name + ".png"), optimize=True)
            print(name, im.size)
        except OSError as e:
            if name not in fallback:
                raise
            sym, bg, fg = fallback[name]
            m = re.search(rf'<symbol id="{re.escape(sym)}" viewBox="0 0 24 24"><g [^>]*>(.*?)</g></symbol>', sprite, re.S)
            with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
                f.write(tile_svg(m.group(1), bg, fg, stroke=True))
            print(name, "favicon failed, icon tile instead:", e)

    print(len(os.listdir(OUT)), "logos in", OUT)


if __name__ == "__main__":
    main()

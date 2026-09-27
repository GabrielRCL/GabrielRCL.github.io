"""Build the logo tiles used by the work cards and the hero wire.

- assets/nexview-nx.png: the NX mark cropped to its visible pixels, so CSS centering is exact.
- assets/nfse.png: the NFS-e Nacional wordmark, cropped from the official horizontal logo
  (gov.br/nfse, "Logos da NFS-e").
- assets/banks.png: Sicoob, Banco Inter and Itaú as a cluster of round logos.
- assets/odoo-crm.svg: the Odoo CRM app icon, copied from the Odoo source.
- assets/coffee.svg: a white mug of coffee.
"""
import io
import os
import shutil
import urllib.request

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
NFSE_URL = ("https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/logos-da-nfs-e/"
            "Logo%20-%20NFS-e%20-%20Horizontal.png")
ODOO_CRM_ICON = r"D:\GoNexView\workspace\src\odoo\addons\crm\static\description\icon.svg"
BANKS = ["sicoob", "inter", "itau"]

COFFEE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Mug of coffee">
  <defs>
    <linearGradient id="mug" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="0.55" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#dbe2ea"/>
    </linearGradient>
    <radialGradient id="coffee" cx="0.42" cy="0.4" r="0.7">
      <stop offset="0" stop-color="#8a5a3b"/>
      <stop offset="0.6" stop-color="#6b4226"/>
      <stop offset="1" stop-color="#4a2b17"/>
    </radialGradient>
  </defs>
  <style>
    .steam { opacity: 0; animation: steam 2.7s ease-in-out infinite; }
    .steam.b { animation-delay: 0.9s; }
    .steam.c { animation-delay: 1.8s; }
    @keyframes steam { 0% { opacity: 0; transform: translateY(4px); } 45% { opacity: 0.95; } 100% { opacity: 0; transform: translateY(-5px); } }
    @media (prefers-reduced-motion: reduce) { .steam { animation: none; opacity: 0.9; } }
  </style>
  <g fill="none" stroke="#cbd5e1" stroke-width="2.2" stroke-linecap="round">
    <path class="steam" d="M22 17c-2.4-2.6 2.4-4.6 0-8"/>
    <path class="steam b" d="M28.5 16c-2.4-2.8 2.4-5 0-9"/>
    <path class="steam c" d="M35 17c-2.4-2.6 2.4-4.6 0-8"/>
  </g>
  <ellipse cx="30" cy="55.6" rx="24" ry="4.6" fill="#eef2f6" stroke="#c3ccd8" stroke-width="1.2"/>
  <path d="M44 29.5c6.5 0 9.5 3.2 9.5 7.6 0 4.8-3.9 8.4-10.2 8.4" fill="none" stroke="#c3ccd8" stroke-width="6.4" stroke-linecap="round"/>
  <path d="M44 29.5c6.5 0 9.5 3.2 9.5 7.6 0 4.8-3.9 8.4-10.2 8.4" fill="none" stroke="#f8fafc" stroke-width="3.8" stroke-linecap="round"/>
  <path d="M12 23.5v21.5c0 5.5 3.6 9 9 9h14c5.4 0 9-3.5 9-9V23.5z" fill="url(#mug)" stroke="#c3ccd8" stroke-width="1.2"/>
  <ellipse cx="28" cy="23.5" rx="16" ry="4.6" fill="#ffffff" stroke="#c3ccd8" stroke-width="1.2"/>
  <ellipse cx="28" cy="23.9" rx="13.6" ry="3.4" fill="url(#coffee)"/>
  <ellipse cx="24.5" cy="23.2" rx="5" ry="1.1" fill="#b98a5e" opacity="0.55"/>
</svg>
"""


def crop_visible(im, threshold=20):
    alpha = im.getchannel("A").point(lambda a: 255 if a > threshold else 0)
    return im.crop(alpha.getbbox())


def build_nx():
    path = os.path.join(ASSETS, "nexview-nx.png")
    im = Image.open(path).convert("RGBA")
    cropped = crop_visible(im)
    if cropped.size != im.size:
        cropped.save(path, optimize=True)
    print("nexview-nx.png", cropped.size)


def build_nfse():
    # gov.br answers 403 to urllib's default User-Agent.
    req = urllib.request.Request(NFSE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGBA")
    # The wordmark (N F S e) ends where the grey tagline "Nota Fiscal de..." starts.
    px = im.load()
    w, h = im.size
    cut = w
    for x in range(int(w * 0.35), w):
        col = [px[x, y] for y in range(h)]
        if all(a < 20 or (abs(r - g) < 18 and abs(g - b) < 40 and r > 100) for r, g, b, a in col):
            cut = x
            break
    mark = crop_visible(im.crop((0, 0, cut, h)))
    target_h = 96
    mark = mark.resize((round(mark.width * target_h / mark.height), target_h), Image.LANCZOS)
    mark.save(os.path.join(ASSETS, "nfse.png"), optimize=True)
    print("nfse.png", mark.size)


def round_logo(name, size, inset=0.78):
    src = Image.open(os.path.join(ASSETS, "stack", f"{name}.png")).convert("RGBA")
    # Fill the disc with the logo's own background (white for Sicoob and Inter, orange for Itaú) and
    # shrink the logo inside it, so the circle does not clip its corners.
    bg = src.getpixel((src.width // 2, 2))
    disc = Image.new("RGBA", (size, size), bg[:3] + (255,))
    inner = round(size * inset)
    disc.alpha_composite(src.resize((inner, inner), Image.LANCZOS), ((size - inner) // 2, (size - inner) // 2))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    disc.putalpha(mask)
    return disc


def build_banks():
    scale = 4
    canvas = 44 * scale
    d = 22 * scale
    ring = round(1.5 * scale)
    pad = 2 * scale
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    spots = {"itau": ((canvas - d) // 2, pad),
             "sicoob": (pad, canvas - d - pad),
             "inter": (canvas - d - pad, canvas - d - pad)}
    for name in ["itau", "sicoob", "inter"]:
        x, y = spots[name]
        halo = Image.new("L", (d + 2 * ring, d + 2 * ring), 0)
        ImageDraw.Draw(halo).ellipse((0, 0, d + 2 * ring - 1, d + 2 * ring - 1), fill=255)
        white = Image.new("RGBA", halo.size, (255, 255, 255, 255))
        white.putalpha(halo)
        out.alpha_composite(white, (x - ring, y - ring))
        out.alpha_composite(round_logo(name, d), (x, y))
    out = out.resize((132, 132), Image.LANCZOS)
    out.save(os.path.join(ASSETS, "banks.png"), optimize=True)
    print("banks.png", out.size)


def main():
    build_nx()
    build_nfse()
    build_banks()
    shutil.copyfile(ODOO_CRM_ICON, os.path.join(ASSETS, "odoo-crm.svg"))
    with open(os.path.join(ASSETS, "coffee.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(COFFEE_SVG)
    print("odoo-crm.svg, coffee.svg")


if __name__ == "__main__":
    main()

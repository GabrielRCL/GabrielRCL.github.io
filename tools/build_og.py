"""Build the link preview image and the favicons from the cartoon portrait (tools/src/cartoon.jpg).

- assets/og.jpg (1200x630): what WhatsApp, LinkedIn and X show when the link is shared. Rendered
  from an HTML template with headless Edge, so it uses the site's fonts and colors.
- assets/favicon.ico, favicon-32.png, favicon-512.png: the face, round.
- assets/apple-touch-icon.png (180x180): the face, square (iOS rounds the corners itself).
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
SRC = os.path.join(ROOT, "tools", "src", "cartoon.jpg")
FACE = (281, 214, 721, 654)        # head and a little of the collar, square
PORTRAIT = (96, 120, 906, 1200)    # head to the hands, 3:4
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;800;900&family=JetBrains+Mono:wght@500;700&display=block">
<style>
  html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; }
  body { position: relative; font-family: Inter, "Segoe UI", sans-serif; color: #f1f5f9;
    background: radial-gradient(60% 80% at 85% 20%, rgba(0,184,255,.16), transparent 70%),
                radial-gradient(50% 70% at 0% 100%, rgba(248,121,52,.20), transparent 70%),
                linear-gradient(135deg, #050a1c, #0c1633); }
  .grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(148,163,184,.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148,163,184,.07) 1px, transparent 1px); background-size: 32px 32px; }
  .photo { position: absolute; right: 0; top: 0; width: 500px; height: 630px; object-fit: cover; object-position: center top;
    -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 28%); mask-image: linear-gradient(90deg, transparent 0, #000 28%); }
  .content { position: absolute; left: 72px; top: 64px; width: 700px; }
  .site { display: flex; align-items: center; gap: 12px; font: 700 24px "JetBrains Mono", monospace; color: #f87934; }
  .glyph { display: inline-flex; align-items: center; gap: 2px; width: 46px; height: 38px; justify-content: center; border-radius: 10px;
    background: #0b1530; box-shadow: inset 0 0 0 2px rgba(248,121,52,.5); font-size: 20px; }
  .glyph i { width: 11px; height: 3px; margin-top: 12px; background: currentColor; }
  h1 { margin: 34px 0 30px; font-weight: 900; font-size: 118px; line-height: .92; letter-spacing: -5px; }
  h1 span { display: block; background: linear-gradient(120deg, #f15c48 5%, #f87934 50%, #f9b233 95%); -webkit-background-clip: text; color: transparent; }
  .roles { display: flex; flex-wrap: wrap; gap: 10px; max-width: 660px; }
  .roles b { font-weight: 600; font-size: 23px; padding: 9px 16px; border-radius: 10px; background: rgba(16,28,63,.85); border: 1px solid #22335f; }
  .roles b:first-child { border-color: #f87934; }
  .more { margin-top: 26px; font: 500 21px "JetBrains Mono", monospace; color: #7dd3fc; }
</style></head><body>
<div class="grid"></div>
<img class="photo" src="{photo}">
<div class="content">
  <div class="site"><span class="glyph">&gt;<i></i></span>gabrielrcl.dev</div>
  <h1>Gabriel<span>Lucas</span></h1>
  <div class="roles"><b>Full Stack Developer</b><b>Odoo Developer</b><b>Computer Engineering</b></div>
  <div class="more">ERP integrations · banks · NFS-e · WhatsApp · MCP</div>
</div>
</body></html>"""


def round_face(size):
    face = Image.open(SRC).convert("RGBA").crop(FACE).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    face.putalpha(mask.resize((size, size), Image.LANCZOS))
    return face


def build_icons():
    round_face(32).save(os.path.join(ASSETS, "favicon-32.png"), optimize=True)
    round_face(512).save(os.path.join(ASSETS, "favicon-512.png"), optimize=True)
    round_face(256).save(os.path.join(ASSETS, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    square = Image.open(SRC).convert("RGB").crop(FACE).resize((180, 180), Image.LANCZOS)
    square.save(os.path.join(ASSETS, "apple-touch-icon.png"), optimize=True)


def build_og():
    with tempfile.TemporaryDirectory() as tmp:
        photo = os.path.join(tmp, "portrait.jpg")
        Image.open(SRC).convert("RGB").crop(PORTRAIT).resize((600, 800), Image.LANCZOS).save(photo, quality=92)
        page = os.path.join(tmp, "og.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(TEMPLATE.replace("{photo}", "file:///" + photo.replace("\\", "/")))
        png = os.path.join(tmp, "og.png")
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630",
                        "--virtual-time-budget=6000", f"--screenshot={png}", "file:///" + page.replace("\\", "/")],
                       check=True, capture_output=True)
        Image.open(png).convert("RGB").crop((0, 0, 1200, 630)).save(os.path.join(ASSETS, "og.jpg"), quality=86, optimize=True)
    print("og.jpg", os.path.getsize(os.path.join(ASSETS, "og.jpg")) // 1024, "KB")


if __name__ == "__main__":
    build_icons()
    build_og()

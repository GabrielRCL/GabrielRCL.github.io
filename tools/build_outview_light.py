"""assets/outview-symbol-light.png: the OutView symbol with a white lighthouse, for dark backgrounds such as
the hero chip. The white-tile version in the work section keeps the original.

In the original the lighthouse is navy and its stripes are transparent (they show whatever is behind:
white on the white tile, the chip's navy on a dark chip). Here the navy turns white and the stripes stay
transparent. Where the navy meets the sunset, each pixel is split into navy and the sunset behind it (the
sunset rebuilt with OpenCV inpainting) and recombined with white, so the lighthouse gets no dark fringe.

Needs opencv-python-headless, numpy and pillow.
"""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "outview-symbol.png")
OUT = os.path.join(ROOT, "assets", "outview-symbol-light.png")
WHITE = np.array([255.0, 255.0, 255.0])


def main():
    rgba = np.asarray(Image.open(SRC).convert("RGBA")).astype(np.float64)
    rgb, alpha = rgba[..., :3], rgba[..., 3]
    opaque = alpha > 250
    navy_mask = (np.linalg.norm(rgb - [30, 65, 119], axis=2) < 70) & opaque
    navy = np.median(rgb[navy_mask], axis=0)

    region = cv2.dilate(navy_mask.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    sky = cv2.inpaint(rgb.astype(np.uint8), region.astype(np.uint8) * 255, 6, cv2.INPAINT_TELEA).astype(np.float64)

    out = rgb.copy()
    # opaque pixels near the lighthouse: p = t * navy + (1 - t) * sky  ->  t * white + (1 - t) * sky
    d = navy - sky
    t = np.clip(((rgb - sky) * d).sum(2) / np.maximum((d * d).sum(2), 1e-6), 0, 1)
    mix = region & opaque
    out[mix] = (t[..., None] * WHITE + (1 - t[..., None]) * sky)[mix]
    # semi-transparent pixels touching the lighthouse (its edge against the transparent stripes): same
    # alpha, white color. Only those: the circle's own antialiased rim must keep its sunset colors.
    touching = cv2.dilate(navy_mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    edge = touching & (alpha > 0) & ~opaque & (rgb.sum(2) < 3 * 140)
    out[edge] = WHITE

    # The lantern's three windows are holes too, split by thin semi-transparent mullions. The mullions and
    # the window edges become solid white, so the three windows read as dark panes framed in white. Only
    # the first band of holes under the dome, within the lighthouse's width (the gaps between the light
    # beams, beside it, stay as they are).
    ys, _ = np.where(navy_mask)
    band_rows, span = [], None
    for y in range(ys.min(), ys.max()):
        cols = np.where(navy_mask[y])[0]
        if len(cols) > 10:
            span = (cols.min(), cols.max() + 1)  # the lighthouse's width, from the last solid navy row
        if span and (alpha[y, span[0]:span[1]] < 250).mean() > 0.5:
            band_rows.append(y)
            x0, x1 = span
        elif band_rows:
            break
    if band_rows:
        frame = np.zeros_like(opaque)
        frame[band_rows[0] - 1:band_rows[-1] + 2, x0:x1] = True
        frame &= (alpha > 20) & (alpha < 250)
        out[frame] = WHITE
        alpha = alpha.copy()
        alpha[frame] = 255

    result = np.dstack([np.clip(out, 0, 255), alpha]).astype(np.uint8)
    Image.fromarray(result, "RGBA").save(OUT, optimize=True)
    print("outview-symbol-light.png", result.shape[1], "x", result.shape[0], "navy", navy.round())


if __name__ == "__main__":
    main()

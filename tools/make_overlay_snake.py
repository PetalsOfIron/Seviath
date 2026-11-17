#!/usr/bin/env python3
"""Snake overlay: the frame is a band of the painted snake skin (cut from your snake painting) with a gold edge, snake head in the corner, webcam window framed the same way."""
import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_offline as mo

W, H = 1920, 1080
CAM = (80, H - 80 - 300, 80 + 533, H - 80)
GOLD, NAVY = (250, 206, 72, 255), (8, 36, 80, 255)


def skin_tile():
    src = mo.clean_source(Image.open(ROOT / "images" / "Banner snake.png").convert("RGB"))
    tile = src.crop((560, 330, 1060, 620)).convert("RGBA")        # scales on the body
    return tile


def band(w, h, tile):
    out = Image.new("RGBA", (w, h))
    flips = [tile, tile.transpose(Image.FLIP_LEFT_RIGHT), tile.transpose(Image.FLIP_TOP_BOTTOM), tile.transpose(Image.ROTATE_180)]
    for i, x in enumerate(range(0, w, tile.width)):
        for j, y in enumerate(range(0, h, tile.height)):
            out.alpha_composite(flips[(i % 2) + 2 * (j % 2)], (x, y))   # mirrored neighbours: no visible seams
    return out


def frame_layer(inner, outer, radius, tile):
    """Ring between the outer and inner rounded rectangles, filled with snake skin, edged in gold and navy."""
    S = 2
    big = (W * S, H * S)
    mo_ = Image.new("L", big, 0)
    ImageDraw.Draw(mo_).rounded_rectangle([c * S for c in outer], radius=radius * S, fill=255)
    mi = Image.new("L", big, 0)
    ImageDraw.Draw(mi).rounded_rectangle([c * S for c in inner], radius=int(radius * 0.7) * S, fill=255)
    ring = ImageChops.subtract(mo_, mi).resize((W, H), Image.LANCZOS)
    skin = band(W, H, tile)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(skin, (0, 0), ring)
    d = ImageDraw.Draw(layer)
    for box, col, wd in ((outer, NAVY, 5), ((outer[0] + 5, outer[1] + 5, outer[2] - 5, outer[3] - 5), GOLD, 4), (inner, GOLD, 4), ((inner[0] - 5, inner[1] - 5, inner[2] + 5, inner[3] + 5), NAVY, 4)):
        d.rounded_rectangle(box, radius=radius, outline=col, width=wd)
    return layer


def main():
    tile = skin_tile()
    img = frame_layer((70, 70, W - 70, H - 70), (10, 10, W - 10, H - 10), 46, tile)
    x0, y0, x1, y1 = CAM
    cam = frame_layer((x0, y0, x1, y1), (x0 - 54, y0 - 54, x1 + 54, y1 + 54), 26, tile)
    img = Image.alpha_composite(img, cam)
    # head in the top-right corner (from the painting), inside the band
    src = mo.clean_source(Image.open(ROOT / "images" / "Banner snake.png").convert("RGB")).convert("RGBA")
    head = src.crop((780, 330, 1010, 560)).resize((230, 230), Image.LANCZOS)
    m = Image.new("L", (230 * 3, 230 * 3), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 230 * 3 - 1, 230 * 3 - 1), fill=255)
    head.putalpha(m.resize((230, 230), Image.LANCZOS))
    ring = Image.new("RGBA", (254, 254), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, 253, 253), fill=GOLD, outline=NAVY, width=6)
    ring.alpha_composite(head, (12, 12))
    img.alpha_composite(ring, (W - 330, 24))
    # clear the webcam window and the game area inside the main frame
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], cut))
    p = ROOT / "images" / "twitch" / "Snake" / "Overlay" / "overlay_frame.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)
    print("Saved Snake overlay")


if __name__ == "__main__":
    main()

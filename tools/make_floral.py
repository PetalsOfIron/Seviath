#!/usr/bin/env python3
"""
Floral set in the style of the "I will be right back" screen (navy-to-peach gradient, white and violet flowers,
gold scrollwork, sapphire cabochons). The flowers, gold ornaments and gems are cut from your original screen;
the script adds the new text, the offline screen layout, a round logo and a wide banner.

    python tools/make_floral.py
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403

SRC = Path(r"C:\Users\SaphiresSilver\Downloads\art\priekstwitterfiver\2x\1x\I will be right back.png")
OUT = ROOT / "images" / "twitch" / "Floral"
WHITE, GOLD_L, GOLD_D = (252, 250, 255), (255, 226, 130), (176, 122, 30)
NAVY, MAUVE, PEACH = (30, 28, 72), (110, 80, 110), (226, 150, 116)


def src_img():
    return Image.open(SRC).convert("RGB")


def circle_crop(img, center, r, ss=4):
    cx, cy = center
    box = (cx - r, cy - r, cx + r, cy + r)
    crop = img.crop(box).convert("RGBA")
    m = Image.new("L", (crop.width * ss, crop.height * ss), 0)
    ImageDraw.Draw(m).ellipse((0, 0, crop.width * ss - 1, crop.height * ss - 1), fill=255)
    crop.putalpha(m.resize(crop.size, Image.LANCZOS))
    return crop


def erase_text(img, rect):
    """Remove the old text by blending the clean rows above and below it, column by column."""
    a = np.asarray(img).astype(float)
    x0, y0, x1, y1 = rect
    top = a[y0 - 12:y0 - 2, x0:x1].mean(axis=0)       # (w, 3)
    bot = a[y1 + 2:y1 + 12, x0:x1].mean(axis=0)
    t = np.linspace(0, 1, y1 - y0)[:, None, None]
    fill = top[None] * (1 - t) + bot[None] * t
    a[y0:y1, x0:x1] = fill
    out = Image.fromarray(a.clip(0, 255).astype("uint8"))
    # a little grain so the repaired area matches the rest
    noise = np.random.default_rng(3).normal(0, 1.4, (y1 - y0, x1 - x0, 1))
    b = np.asarray(out).astype(float)
    b[y0:y1, x0:x1] += noise
    return Image.fromarray(b.clip(0, 255).astype("uint8"))


def gradient_disc(size, d):
    """Navy to mauve to peach, diagonal - the colours of the screen's background."""
    g = Image.new("RGB", (size, size))
    px = g.load()
    for y in range(size):
        for x in range(size):
            t = (x * 0.8 + y * 0.45) / (size * 1.25)
            t = min(1, max(0, t))
            if t < 0.5:
                u = t / 0.5
                c = tuple(int(NAVY[i] + (MAUVE[i] - NAVY[i]) * u) for i in range(3))
            else:
                u = (t - 0.5) / 0.5
                c = tuple(int(MAUVE[i] + (PEACH[i] - MAUVE[i]) * u) for i in range(3))
            px[x, y] = c
    return g


# ------------------------------------------------------------------------------------------- offline screen

def offline_screen():
    img = erase_text(src_img(), (342, 468, 1742, 712)).convert("RGBA")
    W, H = img.size
    f = font("OLDENGL.TTF", 250)
    m = text_mask((W, H), "Offline", f, (1045, 640), track=6)
    img = shadow(img, m, (0, 10), 14, (10, 6, 30), 0.65)
    img = fill_mask(img, m, WHITE, (226, 214, 244))
    d = ImageDraw.Draw(img)
    y = 700
    d.line([(740, y), (985, y)], fill=GOLD_L + (235,), width=3)
    d.line([(1105, y), (1350, y)], fill=GOLD_L + (235,), width=3)
    diamond(d, 1045, y, 12, GOLD_L + (255,))
    diamond(d, 1012, y, 5, GOLD_L + (255,))
    diamond(d, 1078, y, 5, GOLD_L + (255,))
    f2 = font("georgiai.ttf", 52)
    img = fill_mask(img, text_mask((W, H), "The stream has ended - see you next time", f2, (1045, 790), track=2), (246, 238, 250))
    return grain(img, 6)


# ------------------------------------------------------------------------------------------------- logo

def metal_ring(canvas, center, d_out, width):
    cx, cy = center
    ss = 3
    size = canvas.size

    def disc(dia):
        m = Image.new("L", (size[0] * ss, size[1] * ss), 0)
        r = dia * ss / 2
        ImageDraw.Draw(m).ellipse((cx * ss - r, cy * ss - r, cx * ss + r, cy * ss + r), fill=255)
        return m.resize(size, Image.LANCZOS)

    band = ImageChops.subtract(disc(d_out), disc(d_out - 2 * width))
    grad = Image.new("RGBA", size)
    gd = ImageDraw.Draw(grad)
    for y in range(size[1]):
        for seg in range(1):
            pass
    px = grad.load()
    for y in range(0, size[1]):
        for x in range(0, size[0], 1):
            ang = math.atan2(y - cy, x - cx)
            t = 0.5 + 0.5 * math.sin(ang * 2.0 - 0.6)
            px[x, y] = tuple(int(GOLD_D[i] + (GOLD_L[i] - GOLD_D[i]) * t) for i in range(3)) + (255,)
    grad.putalpha(band)
    return Image.alpha_composite(canvas, grad)


def floral_logo():
    S = 2000
    canvas = radial((S, S), (62, 42, 96), (22, 16, 46), cx=0.5, cy=0.42, spread=0.9).convert("RGBA")
    cx, cy, D = 1000, 740, 1380
    disc = gradient_disc(S, D).convert("RGBA")
    m = Image.new("L", (S * 3, S * 3), 0)
    ImageDraw.Draw(m).ellipse(((cx - D / 2 + 60) * 3, (cy - D / 2 + 60) * 3, (cx + D / 2 - 60) * 3, (cy + D / 2 - 60) * 3), fill=255)
    m = m.resize((S, S), Image.LANCZOS)
    canvas = shadow(canvas, m, (0, 22), 30, (0, 0, 0), 0.6)
    canvas = Image.composite(disc, canvas, m)
    canvas = metal_ring(canvas, (cx, cy), D + 40, 62)
    ring_r = (D + 40) / 2 - 31
    # gems from the screen (top / right / bottom cabochons) placed on the ring at 4 points
    src = src_img()
    gem = circle_crop(src, (1500, 91), 63)
    gem = gem.resize((236, 236), Image.LANCZOS)
    for ang in (-90, 0, 90, 180):
        a = math.radians(ang)
        gx, gy = cx + math.cos(a) * ring_r, cy + math.sin(a) * ring_r
        layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        layer.paste(gem, (round(gx - 118), round(gy - 118)))
        canvas = shadow(canvas, layer.split()[3], (0, 8), 8, (0, 0, 0), 0.5)
        canvas = Image.alpha_composite(canvas, layer)
    # monogram
    fP = font("OLDENGL.TTF", 880)
    mP = text_mask(canvas.size, "P", fP, (cx, cy + 290))
    canvas = shadow(canvas, mP, (0, 16), 20, (8, 4, 26), 0.7)
    canvas = fill_mask(canvas, mP, WHITE, (222, 208, 244))
    canvas = glow(canvas, (cx - 330, cy - 330, cx + 330, cy + 330), (255, 190, 220), blur=140, alpha=40)
    # wordmark
    fW = font("OLDENGL.TTF", 215)
    mW = text_mask(canvas.size, "Petals Of Iron", fW, (cx, 1790))
    canvas = shadow(canvas, mW, (0, 8), 10, (0, 0, 0), 0.6)
    canvas = fill_mask(canvas, mW, WHITE, (222, 208, 244))
    d = ImageDraw.Draw(canvas)
    d.line([(560, 1872), (940, 1872)], fill=GOLD_L + (235,), width=4)
    d.line([(1060, 1872), (1440, 1872)], fill=GOLD_L + (235,), width=4)
    diamond(d, 1000, 1872, 15, GOLD_L + (255,))
    canvas = vignette(canvas, 0.35, (8, 4, 24))
    return grain(canvas, 8)


# ------------------------------------------------------------------------------------------------ banner

def floral_banner():
    W, H = 3000, 1000
    src = erase_text(src_img(), (342, 468, 1742, 712))
    k = H / src.height
    left = src.crop((0, 0, 628, src.height))                 # the flower cluster
    right = src.crop((1625, 0, src.width, src.height))       # gold column with gems and pompoms
    left = left.resize((round(left.width * k), H), Image.LANCZOS)
    right = right.resize((round(right.width * k), H), Image.LANCZOS)
    # background: blend, row by row, from the left crop's edge colours to the right crop's edge colours
    L = np.asarray(left).astype(float)[:, -3:, :].mean(axis=1)      # (H, 3)
    R = np.asarray(right).astype(float)[:, :3, :].mean(axis=1)
    lo, hi = int(205 * k), int(880 * k)                              # rows free of gold: use them above and below
    L[:lo], L[hi:] = L[lo], L[hi - 1]
    R[:lo], R[hi:] = R[lo], R[hi - 1]
    x0, x1 = left.width, W - right.width
    t = (np.arange(x0, x1) - x0) / max(1, x1 - x0)
    t = t * t * (3 - 2 * t) * 0.25 + t * 0.75
    mid = L[:, None, :] * (1 - t)[None, :, None] + R[:, None, :] * t[None, :, None]
    canvas = Image.new("RGB", (W, H))
    canvas.paste(Image.fromarray(mid.clip(0, 255).astype("uint8")), (x0, 0))
    canvas.paste(left, (0, 0))
    canvas.paste(right, (x1, 0))
    canvas = canvas.convert("RGBA")
    # soften the two joins
    for jx in (x0, x1):
        strip = canvas.crop((jx - 6, 0, jx + 6, H)).filter(ImageFilter.GaussianBlur(3))
        canvas.paste(strip, (jx - 6, 0))
    # thin gold rails with diamonds, in the spirit of the scrollwork frame
    d0 = ImageDraw.Draw(canvas)
    for yy in (52, H - 53):
        d0.line([(x0 + 40, yy), (x1 - 40, yy)], fill=GOLD_L + (230,), width=4)
        d0.line([(x0 + 40, yy + (10 if yy < 500 else -10)), (x1 - 40, yy + (10 if yy < 500 else -10))], fill=GOLD_D + (200,), width=2)
        for dx in (x0 + 40, (x0 + x1) // 2, x1 - 40):
            diamond(d0, dx, yy, 14, GOLD_L + (255,))
    # text
    fT = font("OLDENGL.TTF", 330)
    cx = (x0 + x1) / 2
    m = text_mask((W, H), "Petals Of Iron", fT, (cx, 520))
    canvas = shadow(canvas, m, (0, 10), 16, (10, 6, 30), 0.7)
    canvas = fill_mask(canvas, m, WHITE, (226, 214, 244))
    d = ImageDraw.Draw(canvas)
    y = 585
    d.line([(cx - 520, y), (cx - 60, y)], fill=GOLD_L + (235,), width=4)
    d.line([(cx + 60, y), (cx + 520, y)], fill=GOLD_L + (235,), width=4)
    diamond(d, cx, y, 16, GOLD_L + (255,))
    f2 = font("georgiai.ttf", 84)
    canvas = fill_mask(canvas, text_mask((W, H), "Gamer  -  Streamer  -  Artist", f2, (cx, 720), track=4), (248, 240, 252))
    canvas = vignette(canvas, 0.25, (10, 6, 30))
    return grain(canvas, 6)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("petals_floral_offline.png", offline_screen), ("petals_floral_logo.png", floral_logo),
                     ("petals_floral_banner.png", floral_banner)):
        img = fn().convert("RGB")
        img.save(OUT / name, optimize=True)
        print("Saved", OUT / name, img.size)


if __name__ == "__main__":
    main()

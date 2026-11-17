#!/usr/bin/env python3
"""
Logo + banner for the two fictional brand projects, built from the original assets in Downloads/art/assets:
  Tessel  (football boot, palette: pitch green, deep forest, charcoal, volt yellow, off-white)
  Perfum  (rose perfume bottle, pastel pink / cream / gold)

    python tools/make_brands.py
"""
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403

ASSETS = Path(r"C:\Users\SaphiresSilver\Downloads\art\assets")
OUT = ROOT / "images" / "design"

# Tessel palette (from tessel_palette.png)
PITCH, FOREST, CHARCOAL, VOLT, OFFWHITE = (31, 163, 74), (14, 59, 46), (30, 36, 34), (223, 255, 61), (245, 247, 245)
# Perfum colours (from the poster)
PLUM, GOLD, BLUSH, CREAM = (84, 28, 52), (184, 150, 84), (234, 190, 178), (247, 238, 222)


def load(name, scale=None, size=None):
    im = Image.open(ASSETS / name).convert("RGBA")
    if size:
        im = im.resize(size, Image.LANCZOS)
    elif scale:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    return im


def place(canvas, img, xy, shadow_opacity=0.0, shadow_off=(0, 24), blur=26):
    """Alpha-composite img at xy (may be partly outside the canvas), optionally with a soft shadow."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(img, xy)
    if shadow_opacity:
        a = layer.split()[3]
        canvas = shadow(canvas, a, shadow_off, blur, (0, 0, 0), shadow_opacity)
    return Image.alpha_composite(canvas, layer)


def circle_mask(size, box, ss=4):
    big = Image.new("L", (size[0] * ss, size[1] * ss), 0)
    ImageDraw.Draw(big).ellipse([c * ss for c in box], fill=255)
    return big.resize(size, Image.LANCZOS)


def ring(canvas, center, diameter, width, c1, c2):
    cx, cy = center
    r = diameter / 2
    outer = circle_mask(canvas.size, (cx - r, cy - r, cx + r, cy + r))
    inner = circle_mask(canvas.size, (cx - r + width, cy - r + width, cx + r - width, cy + r - width))
    band = ImageChops.subtract(outer, inner)
    grad = Image.new("RGBA", canvas.size)
    d = ImageDraw.Draw(grad)
    for y in range(canvas.height):
        t = 0.5 + 0.5 * math.sin(y / 140.0)
        d.line([(0, y), (canvas.width, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,))
    grad.putalpha(band)
    return Image.alpha_composite(canvas, grad)


def wordmark(canvas, text, fnt, xy, track, fill, grad_to=None, anchor="center", shadow_op=0.0):
    m = text_mask(canvas.size, text, fnt, xy, track=track, anchor=anchor)
    if shadow_op:
        canvas = shadow(canvas, m, (0, 8), 10, (0, 0, 0), shadow_op)
    return fill_mask(canvas, m, fill, grad_to)


# ------------------------------------------------------------------------------------------------ TESSEL

def tessel_bg(size):
    w, h = size
    base = Image.linear_gradient("L").rotate(90).resize(size)          # left (0) -> right (255)
    left = Image.new("RGB", size, FOREST)
    right = Image.new("RGB", size, CHARCOAL)
    bg = Image.composite(right, left, base).convert("RGBA")
    return bg


def tessel_speed_lines(canvas, box, n=14, seed=5):
    import random
    rnd = random.Random(seed)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x = rnd.randint(box[0], box[2])
        y = rnd.randint(box[1], box[3])
        ln = rnd.randint(160, 520)
        d.line([(x, y), (x - ln, y + ln * 0.55)], fill=VOLT + (rnd.randint(30, 90),), width=rnd.randint(2, 5))
    return Image.alpha_composite(canvas, layer.filter(ImageFilter.GaussianBlur(0.8)))


def tessel_banner():
    W, H = 3000, 1000
    canvas = tessel_bg((W, H))
    canvas = glow(canvas, (1500, 40, 2900, 980), PITCH, blur=170, alpha=150)
    canvas = tessel_speed_lines(canvas, (200, 0, 2900, 700))
    boot = load("Footballboot.png", size=(1040, 1040))
    canvas = place(canvas, boot, (1780, -22), shadow_opacity=0.55, shadow_off=(26, 36), blur=34)

    f_big = font("constan.ttf", 235)
    canvas = wordmark(canvas, "TESSEL", f_big, (170, 520), 34, OFFWHITE, (206, 214, 208), anchor="left", shadow_op=0.5)
    d = ImageDraw.Draw(canvas)
    d.rectangle((176, 585, 1030, 592), fill=VOLT + (255,))
    f_sub = font("bahnschrift.ttf", 54)
    canvas = wordmark(canvas, "UNSTOPPABLE BY DESIGN", f_sub, (176, 690), 14, VOLT, anchor="left")
    f_small = font("bahnschrift.ttf", 38)
    canvas = wordmark(canvas, "MOVE WITHOUT LIMITS", f_small, (176, 880), 12, (190, 205, 196), anchor="left")

    d = ImageDraw.Draw(canvas)
    d.rectangle((30, 30, W - 31, H - 31), outline=VOLT + (110,), width=3)
    canvas = vignette(canvas, 0.5, (2, 8, 6))
    return grain(canvas, 12)


def tessel_logo():
    S = 2000
    canvas = radial((S, S), (24, 66, 52), (14, 24, 22), cx=0.5, cy=0.42, spread=0.9).convert("RGBA")
    cx, cy, D = 1000, 780, 1340
    plate = radial((S, S), (22, 96, 62), FOREST, cx=cx / S, cy=cy / S, spread=0.5).convert("RGBA")
    pm = circle_mask((S, S), (cx - D / 2, cy - D / 2, cx + D / 2, cy + D / 2))
    canvas = shadow(canvas, pm, (0, 24), 34, (0, 0, 0), 0.6)
    plate = glow(plate, (cx - 520, cy - 440, cx + 520, cy + 440), PITCH, blur=120, alpha=120)
    boot = load("Footballboot.png", size=(1320, 1320))
    plate = place(plate, boot, (cx - 660 - 20, cy - 660 + 14), shadow_opacity=0.5, shadow_off=(18, 26), blur=24)
    canvas = Image.composite(plate, canvas, pm)
    canvas = ring(canvas, (cx, cy), D + 70, 26, VOLT, (160, 200, 40))
    canvas = ring(canvas, (cx, cy), D + 140, 6, OFFWHITE, (170, 180, 175))
    f = font("constan.ttf", 235)
    canvas = wordmark(canvas, "TESSEL", f, (1000, 1710), 30, OFFWHITE, (206, 214, 208), shadow_op=0.5)
    d = ImageDraw.Draw(canvas)
    d.rectangle((700, 1765, 1300, 1771), fill=VOLT + (255,))
    canvas = wordmark(canvas, "UNSTOPPABLE BY DESIGN", font("bahnschrift.ttf", 52), (1000, 1865), 14, VOLT)
    canvas = vignette(canvas, 0.4, (2, 8, 6))
    return grain(canvas, 10)


# ------------------------------------------------------------------------------------------------ PERFUM

def perfum_scene(size, horizon):
    """Pastel wall fading into a cream table, with a few soft petals in the air."""
    w, h = size
    bg = Image.new("RGBA", size, CREAM + (255,))
    d = ImageDraw.Draw(bg)
    for y in range(horizon):
        t = y / horizon
        col = tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip((228, 172, 166), (243, 214, 202)))
        d.line([(0, y), (w, y)], fill=col + (255,))
    for y in range(horizon, h):
        t = (y - horizon) / max(1, h - horizon)
        col = tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip((246, 236, 218), (238, 224, 202)))
        d.line([(0, y), (w, y)], fill=col + (255,))
    return bg


def soft_petals(canvas, box, n, seed=9, size=(26, 60)):
    import random
    rnd = random.Random(seed)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    for _ in range(n):
        x, y = rnd.randint(box[0], box[2]), rnd.randint(box[1], box[3])
        pw = rnd.randint(*size)
        ph = int(pw * rnd.uniform(0.55, 0.8))
        petal = Image.new("RGBA", (pw * 2, pw * 2), (0, 0, 0, 0))
        ImageDraw.Draw(petal).ellipse((pw // 2, pw // 2 + (pw - ph) // 2, pw // 2 + pw, pw // 2 + (pw - ph) // 2 + ph), fill=(252, 226, 224, rnd.randint(110, 190)))
        petal = petal.rotate(rnd.randint(0, 359), resample=Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
        layer.alpha_composite(petal, (max(0, x), max(0, y))) if 0 <= x < canvas.width - pw * 2 and 0 <= y < canvas.height - pw * 2 else None
    return Image.alpha_composite(canvas, layer)


def bottle_crop(scale):
    """Bottle + table strip + petals from the asset, scaled; returns (image, bottle centre x, base y) in crop pixels."""
    b = load("Bottle.png")
    y0 = 1485
    crop = b.crop((0, y0, b.width, b.height))
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
    return crop, round(2286 * scale), round((3996 - y0) * scale)


def feather_x(img, edge, bottom=0):
    """Fade the left / right (and optionally bottom) edges of img to transparent."""
    a = img.split()[3]
    m = Image.new("L", img.size, 255)
    d = ImageDraw.Draw(m)
    for x in range(edge):
        v = int(255 * x / edge)
        d.line([(x, 0), (x, img.height)], fill=v)
        d.line([(img.width - 1 - x, 0), (img.width - 1 - x, img.height)], fill=v)
    if bottom:
        mb = Image.new("L", img.size, 255)
        db = ImageDraw.Draw(mb)
        for y in range(bottom):
            db.line([(0, img.height - 1 - y), (img.width, img.height - 1 - y)], fill=int(255 * y / bottom))
        m = ImageChops.darker(m, mb)
    img = img.copy()
    img.putalpha(ImageChops.multiply(a, m))
    return img


def perfum_banner():
    W, H = 3000, 1000
    horizon = 800
    canvas = perfum_scene((W, H), horizon)
    canvas = soft_petals(canvas, (1300, 60, 2900, 700), 26, seed=4)
    canvas = glow(canvas, (1500, 120, 2700, 900), (255, 235, 220), blur=150, alpha=130)
    crop, bx, base_y = bottle_crop(0.355)
    crop = feather_x(crop, 220)
    canvas = place(canvas, crop, (2150 - bx, 880 - base_y))
    canvas = soft_petals(canvas, (1200, 700, 2900, 960), 6, seed=21, size=(36, 70))

    f = font("constan.ttf", 235)
    canvas = wordmark(canvas, "PERFUM", f, (180, 470), 60, PLUM, anchor="left")
    d = ImageDraw.Draw(canvas)
    d.rectangle((186, 560, 700, 565), fill=GOLD + (255,))
    canvas = wordmark(canvas, "Scent of quiet luxury", font("constani.ttf", 84), (186, 680), 4, PLUM, anchor="left")
    canvas = wordmark(canvas, "COMING SOON", font("constan.ttf", 44), (186, 880), 18, (140, 92, 98), anchor="left")
    d = ImageDraw.Draw(canvas)
    d.rectangle((30, 30, W - 31, H - 31), outline=GOLD + (140,), width=3)
    canvas = vignette(canvas, 0.22, (90, 40, 40))
    return grain(canvas, 8)


def perfum_logo():
    S = 2000
    canvas = radial((S, S), (250, 240, 228), (234, 205, 190), cx=0.5, cy=0.4, spread=0.9).convert("RGBA")
    cx, cy, D = 1000, 800, 1380
    scene = perfum_scene((S, S), 940)
    scene = soft_petals(scene, (cx - 600, cy - 600, cx + 600, cy + 100), 14, seed=2, size=(22, 48))
    crop, bx, base_y = bottle_crop(0.385)
    scene = place(scene, feather_x(crop, 120, bottom=140), (cx - bx, 1010 - base_y))
    pm = circle_mask((S, S), (cx - D / 2, cy - D / 2, cx + D / 2, cy + D / 2))
    canvas = shadow(canvas, pm, (0, 22), 32, (90, 40, 40), 0.35)
    canvas = Image.composite(scene, canvas, pm)
    canvas = ring(canvas, (cx, cy), D + 70, 24, (226, 190, 120), (172, 128, 62))
    canvas = ring(canvas, (cx, cy), D + 136, 5, (250, 232, 190), (190, 150, 84))
    f = font("constan.ttf", 235)
    canvas = wordmark(canvas, "PERFUM", f, (1000, 1690), 60, PLUM)
    d = ImageDraw.Draw(canvas)
    d.rectangle((760, 1745, 1240, 1750), fill=GOLD + (255,))
    canvas = wordmark(canvas, "Scent of quiet luxury", font("constani.ttf", 76), (1000, 1850), 4, PLUM)
    canvas = vignette(canvas, 0.18, (90, 40, 40))
    return grain(canvas, 8)


def main():
    jobs = [
        (OUT / "Tessel" / "tessel_logo.png", tessel_logo),
        (OUT / "Tessel" / "tessel_banner.png", tessel_banner),
        (OUT / "Perfum" / "perfum_logo.png", perfum_logo),
        (OUT / "Perfum" / "perfum_banner.png", perfum_banner),
    ]
    for path, fn in jobs:
        path.parent.mkdir(parents=True, exist_ok=True)
        img = fn().convert("RGB")
        img.save(path, optimize=True)
        print("Saved", path, img.size)


if __name__ == "__main__":
    main()

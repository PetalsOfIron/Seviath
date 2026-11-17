#!/usr/bin/env python3
"""
Round channel logos (1600x1600, profile-picture ready) in the same designs as the snake offline screen
and the gold helmet screens. The snake and helmet are the original artwork; the script builds the
badge around them (rings, light, details).

    python tools/make_logos.py
"""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
from make_offline import clean_source

S = 1600
OUT_DIR = ROOT / "images" / "twitch" / "Logo"
SILVER_LIGHT, SILVER_DARK = (248, 250, 255), (140, 150, 170)
GOLD, GOLD_LIGHT, GOLD_DARK = (236, 190, 74), (255, 232, 150), (170, 118, 26)


def circle_mask(size, diameter, center=None, ss=4):
    big = Image.new("L", (size * ss, size * ss), 0)
    cx, cy = center or (size / 2, size / 2)
    r = diameter * ss / 2
    ImageDraw.Draw(big).ellipse((cx * ss - r, cy * ss - r, cx * ss + r, cy * ss + r), fill=255)
    return big.resize((size, size), Image.LANCZOS)


def ring(canvas, diameter, width, c1, c2, angle_light=-0.8):
    """A metallic ring: gradient that runs diagonally across the band, plus a thin highlight."""
    outer = circle_mask(S, diameter)
    inner = circle_mask(S, diameter - 2 * width)
    band = ImageChops.subtract(outer, inner)
    grad = Image.new("RGBA", (S, S))
    gp = grad.load()
    for y in range(S):
        for x in range(S):
            t = 0.5 + 0.5 * math.sin((x * math.cos(angle_light) + y * math.sin(angle_light)) / 190.0)
            gp[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)
    grad.putalpha(band)
    return Image.alpha_composite(canvas, grad)


def badge(art, bg_center, bg_edge, ring_a, ring_b, accent, art_scale_center=None):
    """art: RGBA image already sized, drawn in the middle of a round plate with rings and diamonds."""
    canvas = radial((S, S), bg_center, bg_edge, cx=0.5, cy=0.5, spread=0.9).convert("RGBA")
    # soft outer glow
    glow_layer = Image.new("RGBA", (S, S), accent + (0,))
    glow_layer.putalpha(circle_mask(S, 1500).filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.35)))
    canvas = Image.alpha_composite(canvas, glow_layer)
    # plate
    plate_d = 1180
    pm = circle_mask(S, plate_d)
    canvas = shadow(canvas, circle_mask(S, 1330), (0, 18), 28, (0, 0, 0), 0.6)
    canvas = Image.composite(art, canvas, pm) if art.mode == "RGBA" else Image.composite(art.convert("RGBA"), canvas, pm)
    # rings
    canvas = ring(canvas, 1330, 40, ring_a, ring_b)
    canvas = ring(canvas, 1244, 12, accent, tuple(int(c * 0.6) for c in accent), angle_light=0.6)
    d = ImageDraw.Draw(canvas)
    d.ellipse((S / 2 - 1248 / 2, S / 2 - 1248 / 2, S / 2 + 1248 / 2, S / 2 + 1248 / 2), outline=(0, 0, 0, 90), width=2)
    # diamonds on the outer ring
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        cx, cy = S / 2 + math.cos(a) * 665, S / 2 + math.sin(a) * 665
        diamond(d, cx, cy, 22, accent + (255,))
        diamond(d, cx, cy, 11, (30, 20, 20, 255))
    return canvas


def snake_logo():
    src = clean_source(Image.open(ROOT / "images" / "Banner snake.png").convert("RGB"))
    d = 1000                                        # diameter of the crop = full height of the painting
    cx = 1010
    crop = src.crop((cx - d // 2, 0, cx + d // 2, d)).resize((1180, 1180), Image.LANCZOS)
    plate = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    plate.paste(crop, ((S - 1180) // 2, (S - 1180) // 2))
    canvas = badge(plate, (22, 84, 130), (5, 18, 42), SILVER_LIGHT, SILVER_DARK, GOLD)
    return vignette_inside(canvas, (5, 18, 42))


def helmet_logo():
    from make_starting_soon import helmet_emblem
    em = helmet_emblem()                             # 1520 x 880, helmet and swords on the purple gradient
    scale = 1180 * 0.98 / 1360
    em = em.resize((round(em.width * scale), round(em.height * scale)), Image.LANCZOS)
    plate_bg = radial((S, S), (46, 27, 78), (24, 14, 42), cx=0.5, cy=0.5, spread=0.7).convert("RGBA")
    fade = Image.new("L", em.size, 0)
    ImageDraw.Draw(fade).rectangle((40, 40, em.width - 40, em.height - 40), fill=255)
    fade = fade.filter(ImageFilter.GaussianBlur(34))
    plate_bg.paste(em, ((S - em.width) // 2, (S - em.height) // 2 - 10), fade)
    plate_bg = glow(plate_bg, (330, 230, 1270, 1230), (255, 190, 80), blur=110, alpha=55)
    canvas = badge(plate_bg, (40, 22, 70), (8, 5, 16), GOLD_LIGHT, GOLD_DARK, GOLD)
    return vignette_inside(canvas, (6, 3, 12))


def vignette_inside(canvas, color):
    v = Image.new("L", (S, S), 0)
    ImageDraw.Draw(v).ellipse((60, 60, S - 60, S - 60), fill=255)
    v = ImageChops.invert(v.filter(ImageFilter.GaussianBlur(160)))
    dark = Image.new("RGBA", (S, S), color + (0,))
    dark.putalpha(v.point(lambda x: int(x * 0.45)))
    return grain(Image.alpha_composite(canvas, dark), 10)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in (("petals_snake_logo.png", snake_logo), ("petals_helmet_logo.png", helmet_logo)):
        img = fn().convert("RGB")
        img.save(OUT_DIR / name, optimize=True)
        print("Saved", OUT_DIR / name, img.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Watermarked, reduced previews for public posts (nobody can use them as the real files): 1000 px wide JPEG, tiled diagonal
watermark across the whole image.   python tools/make_x_previews.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SRC = Path("C:/Users/SaphiresSilver/Projects/seviathstudio/src/_g_tmp/payhip")
OUT = Path("C:/Users/SaphiresSilver/Projects/seviathstudio/src/_g_tmp/xprev")
FONT = "C:/Windows/Fonts/georgiab.ttf"
SETS = {"Bold_Stripe": "Bold_Stripe_Emote_Pack", "Hooded_Gamer": "Hooded_Gamer_Emote_Pack", "Gold_Knight": "Gold_Knight_Emote_Pack"}


def mark(im):
    w, h = im.size
    big = Image.new("RGBA", (int(w * 1.6), int(h * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    f = ImageFont.truetype(FONT, max(24, w // 28))
    step_y, step_x = max(150, h // 4), max(760, int(w * .8))
    for r, y in enumerate(range(0, big.height, int(step_y))):
        for x in range(-int(step_x) + (r % 2) * int(step_x // 2), big.width, int(step_x)):
            d.text((x, y), "PETALS OF IRON - PREVIEW", font=f, fill=(255, 255, 255, 120), stroke_width=2, stroke_fill=(0, 0, 0, 90))
    big = big.rotate(28, resample=Image.BICUBIC)
    left, top = (big.width - w) // 2, (big.height - h) // 2
    im = im.convert("RGBA")
    im.alpha_composite(big.crop((left, top, left + w, top + h)))
    return im.convert("RGB")


for name, folder in SETS.items():
    for i, f in enumerate(["cover_1.png", "cover_2.png", "cover_3.png", "thumb.png"], 1):
        im = Image.open(SRC / folder / f).convert("RGB")
        k = 1000 / im.width
        im = im.resize((1000, int(im.height * k)), Image.LANCZOS)
        mark(im).save(OUT / f"{name}_{i}.jpg", quality=72)
    print(name)

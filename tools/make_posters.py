#!/usr/bin/env python3
"""Brand posters (A4 portrait, 2480x3508) for the Northbeam and Strikeline (football company) kits.

    python tools/make_posters.py
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_northbeam as nb
import make_football as mf

W, H = 2480, 3508


def beams(canvas, color, n=7, seed=3, strength=46):
    """Soft diagonal light beams falling from the top, like an aurora / stadium light."""
    import random
    rnd = random.Random(seed)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x = rnd.randint(int(canvas.width * 0.1), int(canvas.width * 0.9))
        wd = rnd.randint(90, 330)
        slope = rnd.randint(-420, 420)
        d.polygon([(x, 0), (x + wd, 0), (x + wd + slope + 280, canvas.height * 0.75), (x + slope, canvas.height * 0.75)], fill=color + (rnd.randint(strength // 2, strength),))
    return Image.alpha_composite(canvas, layer.filter(ImageFilter.GaussianBlur(60)))


def north_poster():
    em, wd = (nb.crop_pad(p) for p in nb.split_logo(nb.load_logo()))
    img = nb.dark_bg((W, H), em)
    img = beams(img, nb.CYAN)
    img = glow(img, (W / 2 - 900, 650, W / 2 + 900, 2050), nb.INDIGO, blur=260, alpha=150)
    # emblem
    e = nb.fit(em, 1250, 1450)
    img = nb.put(img, e, center=(W / 2, 1330), shadow_op=0.5)
    # wordmark
    w_ = nb.fit(wd, 1900, 640)
    img = nb.put(img, w_, center=(W / 2, 2330), shadow_op=0.4)
    d = ImageDraw.Draw(img)
    y = 2330 + w_.height / 2 + 90
    c = nb.CYAN + (255,)
    d.line([(W / 2 - 780, y), (W / 2 - 50, y)], fill=c, width=5)
    d.line([(W / 2 + 50, y), (W / 2 + 780, y)], fill=c, width=5)
    diamond(d, W / 2, y, 22, c)
    img = fill_mask(img, text_mask(img.size, nb.TAGLINE.upper(), font("georgia.ttf", 104), (W / 2, y + 190), track=34, anchor="center"), (232, 242, 252))
    # footer
    d = ImageDraw.Draw(img)
    d.line([(280, H - 330), (W - 280, H - 330)], fill=nb.CYAN + (170,), width=3)
    img = fill_mask(img, text_mask(img.size, nb.SITE.upper(), font("segoeui.ttf", 56), (280, H - 250), track=16, anchor="left"), (200, 218, 240))
    img = fill_mask(img, text_mask(img.size, nb.MAIL, font("segoeui.ttf", 56), (W - 280, H - 250), track=4, anchor="right"), (200, 218, 240))
    corner_brackets(img, 90, 220, nb.CYAN + (255,), width=6)
    return grain(vignette(img, 0.4, (2, 6, 20)), 7)


def football_poster():
    fig = mf.figure()
    em = mf.crop_pad(mf.emblem())
    img = radial((W, H), (40, 74, 120), (7, 11, 18), cx=0.5, cy=0.4, spread=1.0).convert("RGBA")
    img = beams(img, (0, 168, 232), n=6, seed=9, strength=40)
    s = mf.stripes(int(W * 0.26), int(H * 0.36))
    s.putalpha(s.split()[3].point(lambda v: int(v * 0.95)))
    img.alpha_composite(s, (0, 1120))
    img.alpha_composite(s.transpose(Image.FLIP_LEFT_RIGHT), (W - s.width, 1120))
    img = glow(img, (W / 2 - 800, 500, W / 2 + 800, 2400), (50, 150, 235), blur=240, alpha=120)
    # figure
    f = mf.fit(fig, 1500, 1850)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(f, ((W - f.width) // 2, 640))
    img = shadow(img, lay.split()[3], (0, 28), 40, (0, 0, 0), 0.6)
    img = Image.alpha_composite(img, lay)
    # headline
    CY = (0, 168, 232)
    sz = 420
    m = text_mask(img.size, "PLAY THE LINE", font("impact.ttf", 330), (W / 2, 430), track=24)
    img = shadow(img, m, (0, 14), 18, (0, 0, 0), 0.6)
    img = fill_mask(img, m, (250, 252, 255), (196, 208, 224))
    d = ImageDraw.Draw(img)
    d.rectangle((W / 2 - 520, 470, W / 2 + 520, 480), fill=CY + (255,))
    # lower plate
    py, ph = 2680, 560
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.polygon([(300, py), (W - 220, py), (W - 300, py + ph), (220, py + ph)], fill=(8, 14, 26, 232))
    pd.polygon([(300, py), (350, py), (270, py + ph), (220, py + ph)], fill=CY + (255,))
    pd.line([(280, py + ph - 3), (W - 300, py + ph - 3)], fill=CY + (210,), width=8)
    img = shadow(img, plate.split()[3], (0, 22), 28, (0, 0, 0), 0.55)
    img = Image.alpha_composite(img, plate)
    e = mf.fit(em, 400, 450)
    img = mf.put(img, e, center=(560, py + ph / 2), shadow_op=0.4)
    img = mf.text(img, mf.NAME, (W / 2 + 230, py + 270), font("impact.ttf", 250), (250, 252, 255), track=16, anchor="center")
    img = mf.text(img, mf.SUB, (W / 2 + 230, py + 430), font("bahnschrift.ttf", 62), CY, track=20, anchor="center")
    # footer strip
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 130, W, H), fill=(4, 8, 14, 245))
    d.line([(0, H - 130), (W, H - 130)], fill=CY + (255,), width=6)
    img = mf.text(img, mf.SITE.upper() + "   -   " + mf.MAIL.upper(), (W / 2, H - 48), font("bahnschrift.ttf", 46), (190, 205, 222), track=10, anchor="center")
    corner_brackets(img, 90, 220, CY + (240,), width=6)
    return grain(vignette(img, 0.45, (2, 4, 10)), 8)


def main():
    out = ROOT / "images" / "design"
    p1 = out / "Northbeam" / "northbeam_poster.png"
    p2 = out / "Football" / "football_poster.png"
    north_poster().convert("RGB").save(p1, optimize=True)
    print("Saved", p1.name, flush=True)
    football_poster().convert("RGB").save(p2, optimize=True)
    print("Saved", p2.name, flush=True)


if __name__ == "__main__":
    main()

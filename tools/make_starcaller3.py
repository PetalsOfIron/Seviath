#!/usr/bin/env python3
"""Starcaller logo and avatar with their own look (crescent moon + porthole, tight face close-up)."""
import math
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.argv = sys.argv[:1]
import make_starcaller2 as s2
from make_starcaller2 import *  # noqa: F401,F403
import make_starcaller as sc
import make_nightwing as nw


def moon(canvas, cx, cy, R, shift, r2):
    S = canvas.size
    m = Image.new("L", (S[0] * 2, S[1] * 2), 0)
    md = ImageDraw.Draw(m)
    md.ellipse(((cx - R) * 2, (cy - R) * 2, (cx + R) * 2, (cy + R) * 2), fill=255)
    md.ellipse(((cx + shift[0] - r2) * 2, (cy + shift[1] - r2) * 2, (cx + shift[0] + r2) * 2, (cy + shift[1] + r2) * 2), fill=0)
    m = m.resize(S, Image.LANCZOS)
    canvas = shadow(canvas, m, (0, 14), 22, (0, 0, 0), 0.5)
    lay = Image.new("RGBA", S, GOLD + (255,))
    g = Image.new("RGBA", S, GOLD_D + (255,))
    gm = Image.new("L", S, 0)
    ImageDraw.Draw(gm).rectangle((0, cy, S[0], S[1]), fill=255)
    lay = Image.composite(g, lay, gm.filter(ImageFilter.GaussianBlur(160)))
    lay.putalpha(m)
    canvas = Image.alpha_composite(canvas, lay)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    hi = Image.new("RGBA", S, (255, 240, 200, 255))
    hi.putalpha(edge.point(lambda v: min(255, v * 2)))
    return Image.alpha_composite(canvas, hi)


def logo(art, S=2000):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx, cy, r = 1000, 800, 500
    img = moon(img, cx - 40, cy + 20, 640, (130, -30), 590)
    img = orbit(img, cx, cy + 20, 780, 250, -16, SKY, 5, 3, 3)
    img = porthole(img, art, (0, 56, 540, 596), cx, cy, r)
    img = orbit(img, cx, cy + 20, 780, 250, 16, GOLD, 4, 2, 5)
    d = ImageDraw.Draw(img)
    for (x, y, rr) in ((1500, 250, 40), (1640, 520, 22), (1560, 1120, 30), (330, 1230, 20), (1380, 180, 18)):
        sparkle(d, x, y, rr, GOLD)
    if nw.LOGO_TEXT:
        img, sz = fit2(img, nw.NAME, (S // 2, 1680), 1500, 160, "center", 20)
        d = ImageDraw.Draw(img)
        d.line([(420, 1760), (900, 1760)], fill=GOLD + (255,), width=5)
        d.line([(1100, 1760), (1580, 1760)], fill=GOLD + (255,), width=5)
        draw_star(d, 1000, 1760, 26, GOLD, ri=11, n=4)
        img = t2(img, nw.TAGLINE, (S // 2, 1850), 52, "center", 22, GOLD, GOLD_D)
    return img


def avatar(art, S=1000):
    img = sc.nebula((S, S), seed=21)
    img = glow(img, (150, 150, 850, 850), COBALT, blur=120, alpha=120)
    cx = cy = S // 2
    r = 400
    d = ImageDraw.Draw(img)
    img = porthole(img, art, (180, 100, 470, 390), cx, cy, r)
    img = orbit(img, cx, cy, 470, 140, -20, SKY, 3, 2, 8)
    d = ImageDraw.Draw(img)
    for (x, y, rr) in ((120, 130, 26), (880, 200, 18), (860, 860, 24), (150, 820, 16)):
        sparkle(d, x, y, rr, GOLD)
    return img


def main():
    art = Image.open(sc.ART).convert("RGBA")
    nw.save(logo(art), "Logo", "starcaller_logo.png")
    nw.save(avatar(art), "Logo", "starcaller_avatar.png")


if __name__ == "__main__":
    main()

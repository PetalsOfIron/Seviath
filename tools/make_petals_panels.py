#!/usr/bin/env python3
"""Redraw the eight Petals of Iron channel panels as crisp high-resolution artwork (same design as the originals):
pill with a red inner line, red medallion with a cream icon, bold serif title, grey-blue leaves and red berries.
Draws at 4x and scales down, so edges stay clean.   python tools/make_petals_panels.py
Writes images/twitch/<name>.png at 2560x800."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
W, H, K = 1280, 400, 4                       # design units, supersampling
DARK = (52, 12, 22)
RED = (186, 32, 48)
RED2 = (214, 66, 76)
CREAM = (234, 218, 208)
GREY = (112, 120, 134)
GREY2 = (150, 158, 170)
TXT = (56, 12, 22)
FONT = "C:/Windows/Fonts/georgiab.ttf"

PANELS = [("about_me", "About Me", "person"), ("addons", "Addons", "gear"), ("chat_rules", "Chat Rules", "list"),
          ("donation", "Donation", "dollar"), ("faq", "FAQ", "question"), ("links", "Links", "link"),
          ("pc_setup", "PC Setup", "monitor"), ("schedule", "Schedule", "clock")]


def s(v):
    return int(round(v * K))


def pts(seq):
    return [(x * K, y * K) for x, y in seq]


def bez(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def leaf(d, base, tip, width, fill=GREY, line=DARK):
    bx, by = base
    tx, ty = tip
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    mid = ((bx + tx) / 2, (by + ty) / 2)
    width *= 1.9
    left = bez(base, (mid[0] + nx * width, mid[1] + ny * width), tip)
    right = bez(tip, (mid[0] - nx * width, mid[1] - ny * width), base)
    poly = pts(left + right)
    d.polygon(poly, fill=fill)
    d.line(poly + [poly[0]], fill=line, width=s(5), joint="curve")
    v = pts([base, tip])
    d.line(v, fill=GREY2, width=s(3))
    for t in (0.35, 0.6):
        px, py = bx + dx * t, by + dy * t
        d.line(pts([(px, py), (px + nx * width * 0.35 + dx * 0.12, py + ny * width * 0.35 + dy * 0.12)]), fill=GREY2, width=s(2))
        d.line(pts([(px, py), (px - nx * width * 0.35 + dx * 0.12, py - ny * width * 0.35 + dy * 0.12)]), fill=GREY2, width=s(2))


def circle(d, c, r, fill=None, line=None, w=0):
    d.ellipse([(c[0] - r) * K, (c[1] - r) * K, (c[0] + r) * K, (c[1] + r) * K], fill=fill, outline=line, width=s(w))


def rrect(d, box, r, fill=None, line=None, w=0):
    d.rounded_rectangle([box[0] * K, box[1] * K, box[2] * K, box[3] * K], radius=r * K, fill=fill, outline=line, width=s(w))


def icon(d, kind, c):
    x, y = c
    f = CREAM
    if kind == "person":
        circle(d, (x, y - 22), 24, fill=f)
        d.pieslice([s(x - 50), s(y + 4), s(x + 50), s(y + 104)], 180, 360, fill=f)
    elif kind == "gear":
        for i in range(8):
            a = math.radians(i * 45)
            cx, cy = x + math.cos(a) * 46, y + math.sin(a) * 46
            d.polygon(pts([(cx + math.cos(a + 1.57) * 13 - math.cos(a) * 10, cy + math.sin(a + 1.57) * 13 - math.sin(a) * 10),
                           (cx - math.cos(a + 1.57) * 13 - math.cos(a) * 10, cy - math.sin(a + 1.57) * 13 - math.sin(a) * 10),
                           (cx - math.cos(a + 1.57) * 10 + math.cos(a) * 9, cy - math.sin(a + 1.57) * 10 + math.sin(a) * 9),
                           (cx + math.cos(a + 1.57) * 10 + math.cos(a) * 9, cy + math.sin(a + 1.57) * 10 + math.sin(a) * 9)]), fill=f)
        circle(d, c, 40, fill=f)
        circle(d, c, 17, fill=RED)
    elif kind == "list":
        for i, yy in enumerate((-34, 0, 34)):
            circle(d, (x - 46, y + yy), 7, fill=f)
            rrect(d, (x - 26, y + yy - 6, x + 52, y + yy + 6), 6, fill=f)
    elif kind == "dollar":
        d.text((x * K, (y + 2) * K), "$", font=ImageFont.truetype(FONT, s(120)), fill=f, anchor="mm")
    elif kind == "question":
        d.text((x * K, (y + 2) * K), "?", font=ImageFont.truetype(FONT, s(124)), fill=f, anchor="mm")
    elif kind == "link":
        rrect(d, (x - 62, y - 24, x + 8, y + 24), 24, line=f, w=11)
        rrect(d, (x - 8, y - 24, x + 62, y + 24), 24, line=f, w=11)
        rrect(d, (x - 20, y - 7, x + 20, y + 7), 6, fill=f)
    elif kind == "monitor":
        rrect(d, (x - 56, y - 50, x + 56, y + 26), 10, line=f, w=10)
        d.line(pts([(x, y + 28), (x, y + 48)]), fill=f, width=s(12))
        rrect(d, (x - 30, y + 44, x + 30, y + 56), 5, fill=f)
    elif kind == "clock":
        circle(d, c, 50, line=f, w=10)
        d.line(pts([(x, y), (x, y - 30)]), fill=f, width=s(10))
        d.line(pts([(x, y), (x + 24, y + 14)]), fill=f, width=s(10))
        circle(d, c, 6, fill=f)


def panel(title, kind):
    im = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # pill body with a vertical gradient
    body = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    g = Image.new("RGBA", (1, H * K))
    for y in range(H * K):
        t = y / (H * K)
        g.putpixel((0, y), (int(236 - 30 * t), int(220 - 52 * t), int(212 - 50 * t), 255))
    g = g.resize((W * K, H * K))
    mask = Image.new("L", (W * K, H * K), 0)
    ImageDraw.Draw(mask).rounded_rectangle([s(14), s(14), s(W - 14), s(H - 14)], radius=s(186), fill=255)
    body.paste(g, (0, 0), mask)
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    rrect(d, (14, 14, W - 14, H - 14), 186, line=DARK, w=9)
    rrect(d, (30, 30, W - 30, H - 30), 170, line=RED, w=4)
    rrect(d, (42, 42, W - 42, H - 42), 158, line=(214, 150, 150), w=2)
    # leaves
    leaf(d, (196, 120), (158, 24), 17)
    leaf(d, (214, 300), (176, 384), 16)
    leaf(d, (236, 300), (292, 388), 15)
    leaf(d, (262, 372), (392, 340), 14)
    leaf(d, (1128, 58), (1250, 30), 12)
    for dx in (0, 40, 80):
        circle(d, (1010 + dx, 70), 9, fill=RED)
    circle(d, (404, 372), 7, fill=RED)
    circle(d, (432, 366), 5, fill=RED)
    # medallion
    cx, cy = 190, 200
    circle(d, (cx + 4, cy + 6), 110, fill=(96, 40, 48))
    circle(d, (cx, cy), 110, fill=RED, line=DARK, w=9)
    circle(d, (cx, cy), 92, line=RED2, w=4)
    icon(d, kind, (cx, cy))
    # title with a cream edge and a soft shadow
    font = ImageFont.truetype(FONT, s(150 if len(title) < 8 else 128))
    tx, ty = 745 * K, 196 * K
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((tx + s(5), ty + s(7)), title, font=font, fill=(40, 6, 14, 150), anchor="mm")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(s(3))))
    d = ImageDraw.Draw(im)
    d.text((tx, ty), title, font=font, fill=TXT, anchor="mm", stroke_width=s(4), stroke_fill=CREAM)
    d.text((tx, ty), title, font=font, fill=TXT, anchor="mm")
    return im


def main():
    big, small = ROOT / "images" / "twitch-large", ROOT / "images" / "twitch"
    for name, title, kind in PANELS:
        im = panel(title, kind)
        # the 2560x800 drawing is the master itself (nothing gets upscaled from a small file, so no blur)
        im.resize((W * 2, H * 2), Image.LANCZOS).save(small / f"{name}.png", optimize=True)
        old = big / f"{name}.png"
        if old.exists():
            old.unlink()
        print(name)


if __name__ == "__main__":
    main()

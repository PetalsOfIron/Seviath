#!/usr/bin/env python3
"""
Redraws the rose / berry Twitch set (panels, sub badges, flair, channel point icon, emotes) at high resolution
in code, so nothing has to be enlarged. Same look as the original set: cream and burgundy, slate leaves,
red berry character.

    python tools/make_rose.py
"""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from art import *  # noqa: F401,F403

OUT = ROOT / "images" / "twitch"
SS = 3

INK = (62, 10, 22)
RED, RED_D, RED_L = (186, 30, 50), (120, 14, 30), (232, 96, 112)
CREAM_A, CREAM_B = (238, 224, 216), (206, 178, 170)
SLATE, SLATE_D = (112, 122, 134), (66, 74, 86)
GOLD, GOLD_D = (255, 214, 96), (214, 150, 40)
BLUSH = (240, 120, 134)


def layer(size, fn):
    im = Image.new("RGBA", (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), SS)
    return im.resize(size, Image.LANCZOS)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def leaf(d, S, cx, cy, length, width, ang, fill=SLATE, outline=INK, lw=6):
    pts = []
    n = 24
    for i in range(n + 1):
        u = i / n
        pts.append((u * length, -width * math.sin(math.pi * u) ** 0.85))
    for i in range(n, -1, -1):
        u = i / n
        pts.append((u * length, width * math.sin(math.pi * u) ** 0.85))
    ca, sa = math.cos(ang), math.sin(ang)
    P = [((cx + x * ca - y * sa) * S, (cy + x * sa + y * ca) * S) for x, y in pts]
    d.polygon(P, fill=fill, outline=outline + (255,), width=int(lw * S / 3))
    a0 = ((cx) * S, (cy) * S)
    a1 = ((cx + length * ca) * S, (cy + length * sa) * S)
    d.line([a0, a1], fill=outline + (255,), width=max(1, int(lw * S / 4)))


def berry_dot(d, S, x, y, r):
    d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=RED + (255,), outline=INK + (255,), width=max(1, int(r * 0.3 * S)))


# ------------------------------------------------------------------------------------------------- panels

def icon_symbol(d, S, kind, cx, cy, r):
    c = (244, 224, 214, 255)
    w = int(r * 0.12 * S)
    if kind == "about":
        d.ellipse(((cx - r * 0.2) * S, (cy - r * 0.5) * S, (cx + r * 0.2) * S, (cy - r * 0.1) * S), fill=c)
        d.pieslice(((cx - r * 0.5) * S, (cy - r * 0.02) * S, (cx + r * 0.5) * S, (cy + r * 0.98) * S), 180, 360, fill=c)
    elif kind == "addons":
        pts = []
        for i in range(16):
            rr = r * (0.52 if i % 2 == 0 else 0.4)
            a = 2 * math.pi * i / 16
            pts.append(((cx + math.cos(a) * rr) * S, (cy + math.sin(a) * rr) * S))
        d.polygon(pts, fill=c)
        d.ellipse(((cx - r * 0.2) * S, (cy - r * 0.2) * S, (cx + r * 0.2) * S, (cy + r * 0.2) * S), fill=RED + (255,))
    elif kind == "rules":
        for i in range(3):
            y = cy + (i - 1) * r * 0.36
            d.ellipse(((cx - r * 0.5) * S, (y - r * 0.07) * S, (cx - r * 0.36) * S, (y + r * 0.07) * S), fill=c)
            d.rounded_rectangle(((cx - r * 0.24) * S, (y - r * 0.06) * S, (cx + r * 0.5) * S, (y + r * 0.06) * S), radius=int(r * 0.06 * S), fill=c)
    elif kind in ("donation", "faq"):
        f = font("georgiab.ttf", int(r * 1.15))
        d.text((cx * S, (cy + r * 0.05) * S), "$" if kind == "donation" else "?", font=ImageFont.truetype(str(FONTS / "georgiab.ttf"), int(r * 1.2 * S)), fill=c, anchor="mm")
    elif kind == "links":
        d.rounded_rectangle(((cx - r * 0.55) * S, (cy - r * 0.2) * S, (cx + r * 0.1) * S, (cy + r * 0.2) * S), radius=int(r * 0.2 * S), outline=c, width=w)
        d.rounded_rectangle(((cx - r * 0.1) * S, (cy - r * 0.2) * S, (cx + r * 0.55) * S, (cy + r * 0.2) * S), radius=int(r * 0.2 * S), outline=c, width=w)
    elif kind == "pc":
        d.rounded_rectangle(((cx - r * 0.55) * S, (cy - r * 0.45) * S, (cx + r * 0.55) * S, (cy + r * 0.2) * S), radius=int(r * 0.08 * S), outline=c, width=w)
        d.rectangle(((cx - r * 0.06) * S, (cy + r * 0.2) * S, (cx + r * 0.06) * S, (cy + r * 0.42) * S), fill=c)
        d.rounded_rectangle(((cx - r * 0.32) * S, (cy + r * 0.4) * S, (cx + r * 0.32) * S, (cy + r * 0.5) * S), radius=int(r * 0.05 * S), fill=c)
    elif kind == "schedule":
        d.ellipse(((cx - r * 0.55) * S, (cy - r * 0.55) * S, (cx + r * 0.55) * S, (cy + r * 0.55) * S), outline=c, width=w)
        d.line([(cx * S, cy * S), (cx * S, (cy - r * 0.34) * S)], fill=c, width=w)
        d.line([(cx * S, cy * S), ((cx + r * 0.26) * S, (cy + r * 0.14) * S)], fill=c, width=w)


PANELS = [("about_me", "About Me", "about"), ("addons", "Addons", "addons"), ("chat_rules", "Chat Rules", "rules"),
          ("donation", "Donation", "donation"), ("faq", "FAQ", "faq"), ("links", "Links", "links"),
          ("pc_setup", "PC Setup", "pc"), ("schedule", "Schedule", "schedule")]


def panel(title, symbol):
    W, H = 1280, 400
    img = Image.new("RGBA", (W, H), (14, 14, 16, 255))
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=lerp(CREAM_A, CREAM_B, y / H) + (255,))

    def pill(d, S):
        d.rounded_rectangle((20 * S, 24 * S, (W - 20) * S, (H - 24) * S), radius=176 * S, fill=(255, 255, 255, 255))
    mask = layer((W, H), pill).split()[3]
    img.paste(grad, (0, 0), mask)

    def deco(d, S):
        d.rounded_rectangle((20 * S, 24 * S, (W - 20) * S, (H - 24) * S), radius=176 * S, outline=INK + (255,), width=int(11 * S))
        d.rounded_rectangle((36 * S, 40 * S, (W - 36) * S, (H - 40) * S), radius=160 * S, outline=RED + (255,), width=int(5 * S))
        for i in range(4):
            d.ellipse(((1030 + i * 44 - 11) * S, (92 - 11) * S, (1030 + i * 44 + 11) * S, (92 + 11) * S), fill=RED + (255,))
        # icon medallion
        cx, cy, r = 205, 200, 104
        d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=RED + (255,), outline=INK + (255,), width=int(11 * S))
        d.ellipse(((cx - r + 18) * S, (cy - r + 18) * S, (cx + r - 18) * S, (cy + r - 18) * S), outline=RED_D + (255,), width=int(5 * S))
        icon_symbol(d, S, symbol, cx, cy, r)
        # leaves and berries around the medallion and the corner
        leaf(d, S, 300, 60, 90, 22, math.radians(115), lw=7)
        leaf(d, S, 330, 372, 120, 26, math.radians(-125), lw=7)
        leaf(d, S, 372, 366, 130, 26, math.radians(-100), lw=7)
        leaf(d, S, 440, 372, 150, 26, math.radians(-12), lw=7)
        berry_dot(d, S, 440, 372, 9)
        leaf(d, S, 1210, 52, 90, 20, math.radians(160), lw=7)
    img = Image.alpha_composite(img, layer((W, H), deco))
    f = font("georgiab.ttf", 150)
    m = text_mask((W, H), title, f, (W / 2 + 150, H / 2 + 56))
    img = shadow(img, m, (0, 5), 3, (255, 255, 255), 0.75)
    img = fill_mask(img, m, INK)
    return img


# ------------------------------------------------------------------------------------------------- roses

_ROSE_CACHE = {}


def user_rose(leaves):
    """The user's own rose drawing (cut from images/Roselogo1.png); with or without its leaves."""
    if leaves not in _ROSE_CACHE:
        full = Image.open(ROOT / "tools" / "assets" / "_rose_cut.png").convert("RGBA")
        if leaves:
            _ROSE_CACHE[leaves] = full
        else:
            w, h = full.size
            only = full.crop((0, int(h * 0.50), int(w * 0.70), h))
            _ROSE_CACHE[leaves] = only.crop(only.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox())
    return _ROSE_CACHE[leaves]


def rose(d, S, cx, cy, r, layers=5, leaves=True, pal=None):
    im = user_rose(leaves)
    h = 2.5 * r * S if leaves else 2.0 * r * S
    k = h / im.height
    img = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    if pal is not None:   # gold variant for the highest badge: shift the red hue to gold, grey leaves stay grey
        hsv = img.convert("RGB").convert("HSV")
        hh, ss, vv = hsv.split()
        hh = hh.point(lambda v: (v + 34) % 256 if v < 40 or v > 235 else v)
        vv = vv.point(lambda v: min(255, int(v * 1.35 + 25)))
        img = Image.merge("HSV", (hh, ss, vv)).convert("RGB").convert("RGBA")
        img.putalpha(im.split()[3].resize(img.size))

    d._image.alpha_composite(img, (int(cx * S - img.width / 2), int(cy * S - img.height / 2)))


def tulip(d, S, cx, cy, r):
    for sx, rot in ((-1, -0.35), (1, 0.35)):
        pts = []
        for i in range(30):
            u = i / 29
            pts.append((cx + sx * r * 0.34 * math.sin(math.pi * u) ** 0.8 + math.sin(rot) * (1 - u) * r * 0.5, cy + r * 0.2 - u * r * 1.5))
        d.polygon([(x * S, y * S) for x, y in pts], fill=RED_D + (255,), outline=INK + (255,), width=max(1, int(r * 0.05 * S)))
    pts = [(cx - r * 0.28, cy + r * 0.2), (cx, cy - r * 1.35), (cx + r * 0.28, cy + r * 0.2), (cx, cy + r * 0.38)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=RED + (255,), outline=INK + (255,), width=max(1, int(r * 0.05 * S)))


def drop(d, S, cx, cy, w, h, fill=RED):
    pts = []
    for i in range(32):
        u = i / 31
        pts.append((cx - w * math.sin(math.pi * u) ** 0.9, cy - h * u))
    for i in range(31, -1, -1):
        u = i / 31
        pts.append((cx + w * math.sin(math.pi * u) ** 0.9, cy - h * u))
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill + (255,), outline=INK + (255,), width=max(1, int(w * 0.16 * S)))


def stem(d, S, cx, y0, y1, w, leaves=True, ls=1.0):
    d.line([(cx * S, y0 * S), (cx * S, y1 * S)], fill=INK + (255,), width=int(w * S))
    if leaves:
        leaf(d, S, cx, y0 - 8, 92 * ls, 24 * ls, math.radians(-150), lw=7)
        leaf(d, S, cx, y0 - 30, 92 * ls, 24 * ls, math.radians(-30), lw=7)


def badge(tier, size=432):
    name, idx, ring = tier
    k = size / 432
    c = size / 2
    gold = idx >= 5
    ring_col = GOLD if gold else (150, 158, 172)

    def fn(d, S):
        d.ellipse((4 * S, 4 * S, (size - 4) * S, (size - 4) * S), fill=INK + (255,))
        d.ellipse((12 * S, 12 * S, (size - 12) * S, (size - 12) * S), fill=ring_col + (255,))
        d.ellipse((52 * S, 52 * S, (size - 52) * S, (size - 52) * S), fill=INK + (255,))
        d.ellipse((61 * S, 61 * S, (size - 61) * S, (size - 61) * S), fill=(240, 230, 224, 255))
        if idx >= 8:  # ring dots: more of them on every higher tier
            n = {8: 12, 9: 16, 10: 20, 11: 24, 12: 30}[idx]
            for i in range(n):
                a = 2 * math.pi * i / n
                berry_dot(d, S, c + math.cos(a) * (size / 2 - 32 * k), c + math.sin(a) * (size / 2 - 32 * k), 8 * k)
        if name == "base":
            leaf(d, S, c, c - 74 * k, 70 * k, 22 * k, math.radians(-155), lw=7)
            leaf(d, S, c, c - 74 * k, 70 * k, 22 * k, math.radians(-25), lw=7)
            d.ellipse(((c - 92 * k) * S, (c - 84 * k) * S, (c + 92 * k) * S, (c + 100 * k) * S), fill=RED + (255,), outline=INK + (255,), width=int(9 * S * k))
            d.arc(((c - 66 * k) * S, (c - 60 * k) * S, (c + 66 * k) * S, (c + 76 * k) * S), 215, 262, fill=RED_L + (255,), width=int(7 * S * k))
        elif name == "2month":
            stem(d, S, c, c + 100 * k, c - 70 * k, 9 * k, ls=0.9 * k)
        elif name == "3month":
            stem(d, S, c + 0, c + 110 * k, c - 10 * k, 9 * k, ls=0.9 * k)
            drop(d, S, c, c - 20 * k, 30 * k, 90 * k)
        elif name == "6month":
            stem(d, S, c, c + 112 * k, c - 4 * k, 9 * k, ls=1.0 * k)
            drop(d, S, c, c - 14 * k, 40 * k, 112 * k)
            drop(d, S, c + 16 * k, c - 24 * k, 22 * k, 90 * k, fill=RED_D)
        elif name == "9month":
            stem(d, S, c, c + 118 * k, c + 6 * k, 9 * k, ls=1.0 * k)
            tulip(d, S, c, c - 6 * k, 96 * k)
        else:
            r_ = 100 * k
            ry = c + (10 * k if idx >= 10 else 0)
            # the rose itself is the same drawing on every year; everything around it grows with the tier
            if idx >= 11:   # 4 years and up: a red band inside the gold ring
                d.ellipse((24 * S, 24 * S, (size - 24) * S, (size - 24) * S), outline=RED + (255,), width=int(8 * S * k))
            rose(d, S, c, ry, r_, layers=4, pal=(1, 2) if idx == 12 else None)
            if idx >= 6:    # 1.5 years: two berries at the bottom
                berry_dot(d, S, c - 100 * k, c + 100 * k, 14 * k)
                berry_dot(d, S, c + 100 * k, c + 100 * k, 14 * k)
            if idx >= 7:    # 2 years: two sparkles at the top
                sparkle(d, S, c - 132 * k, c - 104 * k, 26 * k)
                sparkle(d, S, c + 132 * k, c - 104 * k, 26 * k)
            if idx >= 9:    # 3 years: a leaf wreath at the bottom
                for sx in (-1, 1):
                    for j, ang in enumerate((-35, -10)):
                        a_ = math.radians(180 + ang if sx < 0 else -ang)
                        leaf(d, S, c + sx * (60 + 34 * j) * k, c + (138 - 6 * j) * k, 54 * k, 14 * k, a_, fill=SLATE, lw=5)
            if idx >= 10:   # 3.5 years: a crown (bigger from 4 years)
                cs = 1.0 if idx == 10 else 1.35
                pts = [(c - 52 * cs * k, c - 112 * k), (c - 52 * cs * k, c - 112 * k - 40 * cs * k), (c - 26 * cs * k, c - 112 * k - 20 * cs * k), (c, c - 112 * k - 52 * cs * k),
                       (c + 26 * cs * k, c - 112 * k - 20 * cs * k), (c + 52 * cs * k, c - 112 * k - 40 * cs * k), (c + 52 * cs * k, c - 112 * k)]
                d.polygon([(x * S, y * S) for x, y in pts], fill=(255, 208, 90, 255), outline=INK + (255,), width=int(6 * S * k))
                if idx >= 12:   # 4.5 years: ruby gems on the crown
                    for gx in (-26, 0, 26):
                        berry_dot(d, S, c + gx * cs * k, c - 112 * k - 12 * cs * k, 7 * k)
            if idx >= 11:   # 4 years: two more sparkles lower down
                sparkle(d, S, c - 148 * k, c + 40 * k, 20 * k)
                sparkle(d, S, c + 148 * k, c + 40 * k, 20 * k)
    return layer((size, size), fn)


BADGES = [("base", 0, None), ("2month", 1, None), ("3month", 2, None), ("6month", 3, None), ("9month", 4, None),
          ("1year", 5, None), ("1_5year", 6, None), ("2year", 7, None), ("2_5year", 8, None), ("3year", 9, None),
          ("3_5year", 10, None), ("4year", 11, None), ("4_5year", 12, None)]


def flair(tier, size=432):
    k = size / 432
    c = size / 2

    def fn(d, S):
        d.ellipse((4 * S, 4 * S, (size - 4) * S, (size - 4) * S), fill=INK + (255,))
        d.ellipse((16 * S, 16 * S, (size - 16) * S, (size - 16) * S), fill=(GOLD if tier == 3 else (168, 120, 200)) + (255,))
        d.ellipse((60 * S, 60 * S, (size - 60) * S, (size - 60) * S), fill=INK + (255,))
        d.ellipse((72 * S, 72 * S, (size - 72) * S, (size - 72) * S), fill=(240, 230, 224, 255))
        rose(d, S, c, c, 110 * k, layers=4 if tier == 3 else 2)
    return layer((size, size), fn)


def points_icon(kind, size=432):
    k = size / 432
    c = size / 2

    def fn(d, S):
        d.ellipse((6 * S, 6 * S, (size - 6) * S, (size - 6) * S), fill=RED + (255,), outline=INK + (255,), width=int(14 * S))
        d.ellipse((46 * S, 46 * S, (size - 46) * S, (size - 46) * S), outline=RED_D + (255,), width=int(8 * S))
        if kind == "rose":
            rose(d, S, c, c - 4 * k, 118 * k, layers=4)
        elif kind == "berry":
            berry_face(d, S, c, c + 6 * k, 120 * k, "smile")
        else:
            pts = []
            for i in range(10):
                rr = 130 * k if i % 2 == 0 else 56 * k
                a = -math.pi / 2 + math.pi * i / 5
                pts.append(((c + math.cos(a) * rr) * S, (c + math.sin(a) * rr) * S))
            d.polygon(pts, fill=(255, 226, 150, 255), outline=INK + (255,), width=int(9 * S * k))
    return layer((size, size), fn)


# ------------------------------------------------------------------------------------------------- emotes

def heart(d, S, cx, cy, s, fill=(250, 90, 140)):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        pts.append(((cx + 16 * math.sin(t) ** 3 * s) * S, (cy - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * s) * S))
    d.polygon(pts, fill=fill + (255,), outline=INK + (255,), width=max(1, int(s * 0.5 * S)))


def sparkle(d, S, cx, cy, r, fill=(255, 226, 120)):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.3
        a = -math.pi / 2 + math.pi * i / 4
        pts.append(((cx + math.cos(a) * rr) * S, (cy + math.sin(a) * rr) * S))
    d.polygon(pts, fill=fill + (255,), outline=INK + (255,), width=max(1, int(r * 0.12 * S)))


def eye_open(d, S, x, y, r, look=(0, 0), pupil=0.5):
    d.ellipse(((x - r) * S, (y - r * 1.12) * S, (x + r) * S, (y + r * 1.12) * S), fill=(255, 250, 246, 255), outline=INK + (255,), width=max(1, int(r * 0.2 * S)))
    px, py = x + look[0] * r, y + look[1] * r
    d.ellipse(((px - r * pupil) * S, (py - r * pupil * 1.1) * S, (px + r * pupil) * S, (py + r * pupil * 1.1) * S), fill=INK + (255,))
    d.ellipse(((px - r * 0.22) * S, (py - r * 0.4) * S, (px + r * 0.08) * S, (py - r * 0.08) * S), fill=(255, 255, 255, 255))


def eye_closed(d, S, x, y, r, happy=True):
    box = ((x - r) * S, (y - r * 0.7) * S, (x + r) * S, (y + r * 0.7) * S)
    d.arc(box, 205 if happy else 25, 335 if happy else 155, fill=INK + (255,), width=max(1, int(r * 0.26 * S)))


def brow(d, S, x0, y0, x1, y1, w):
    d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=INK + (255,), width=max(1, int(w * S)))


def mouth_open(d, S, cx, my, w, h, tongue=True, band=False, teeth=False):
    box = ((cx - w) * S, (my - h * 0.55) * S, (cx + w) * S, (my + h) * S)
    if teeth:
        d.rounded_rectangle(((cx - w * 0.85) * S, (my - h * 0.5) * S, (cx + w * 0.85) * S, (my + h * 0.7) * S), radius=int(w * 0.12 * S), fill=(255, 250, 246, 255), outline=INK + (255,), width=max(1, int(w * 0.07 * S)))
        for i in range(1, 6):
            xx = cx - w * 0.85 + w * 1.7 * i / 6
            d.line([(xx * S, (my - h * 0.5) * S), (xx * S, (my + h * 0.7) * S)], fill=INK + (255,), width=max(1, int(w * 0.05 * S)))
        d.line([((cx - w * 0.85) * S, (my + h * 0.1) * S), ((cx + w * 0.85) * S, (my + h * 0.1) * S)], fill=INK + (255,), width=max(1, int(w * 0.05 * S)))
        return
    d.pieslice(box, 0, 180, fill=INK + (255,))
    if band:
        d.rectangle(((cx - w * 0.78) * S, (my - h * 0.5) * S, (cx + w * 0.78) * S, (my - h * 0.5 + h * 0.14) * S), fill=(255, 250, 246, 255))
    if tongue:
        d.pieslice(((cx - w * 0.55) * S, (my + h * 0.1) * S, (cx + w * 0.55) * S, (my + h * 1.35) * S), 180, 360, fill=(250, 120, 140, 255))
        d.pieslice(box, 0, 180, outline=INK + (255,), width=max(1, int(w * 0.07 * S)))


def smile(d, S, cx, my, w, lw):
    d.arc(((cx - w) * S, (my - w * 0.75) * S, (cx + w) * S, (my + w * 0.45) * S), 25, 155, fill=INK + (255,), width=max(1, int(lw * S)))


def frown(d, S, cx, my, w, lw):
    d.arc(((cx - w) * S, (my - w * 0.2) * S, (cx + w) * S, (my + w) * S), 205, 335, fill=INK + (255,), width=max(1, int(lw * S)))


def berry_body(d, S, cx, cy, r, body):
    leaf(d, S, cx - r * 0.04, cy - r * 0.93, r * 0.62, r * 0.2, math.radians(-148), fill=(122, 130, 142), lw=int(r * 0.075))
    leaf(d, S, cx + r * 0.04, cy - r * 0.93, r * 0.62, r * 0.2, math.radians(-32), fill=(122, 130, 142), lw=int(r * 0.075))
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=body + (255,), outline=INK + (255,), width=int(r * 0.095 * S))
    d.arc(((cx - r * 0.8) * S, (cy - r * 0.8) * S, (cx + r * 0.8) * S, (cy + r * 0.8) * S), 212, 262, fill=lerp(body, (255, 200, 205), 0.45) + (255,), width=int(r * 0.075 * S))


def berry_face(d, S, cx, cy, r, mood, t=0.0, dark=False):
    body = {"angry": (150, 22, 38), "mad": (150, 22, 38), "sleepy": (170, 40, 58), "sun": (250, 205, 80)}.get(mood, RED)
    berry_body(d, S, cx, cy, r, body)
    ex, ey = r * 0.4, cy - r * 0.08
    er = r * 0.17
    my = cy + r * 0.34
    blink = 0.45 < t < 0.55
    if mood not in ("angry", "mad", "cool"):
        for sx in (-1, 1):
            d.ellipse(((cx + sx * r * 0.64 - r * 0.2) * S, (cy + r * 0.28 - r * 0.12) * S, (cx + sx * r * 0.64 + r * 0.2) * S, (cy + r * 0.28 + r * 0.12) * S), fill=BLUSH + (210,))
    if mood in ("smile", "hi", "party", "royal", "hype"):
        for sx in (-1, 1):
            if blink:
                eye_closed(d, S, cx + sx * ex, ey, er)
            else:
                eye_open(d, S, cx + sx * ex, ey, er, (0.1, 0.1))
        if mood in ("party", "hype"):
            mouth_open(d, S, cx, my - r * 0.08, r * 0.3, r * 0.4)
        else:
            smile(d, S, cx, my, r * 0.32, r * 0.07)
    elif mood in ("laugh", "laughing", "joyful"):
        for sx in (-1, 1):
            eye_closed(d, S, cx + sx * ex, ey + er * 0.3, er * 1.05)
        mouth_open(d, S, cx, my - r * 0.06, r * 0.36, r * 0.42, band=True)
    elif mood in ("fun", "playful"):
        eye_closed(d, S, cx - ex, ey + er * 0.2, er * 1.05)
        eye_open(d, S, cx + ex, ey, er * 1.15, (0.1, 0.0))
        mouth_open(d, S, cx, my - r * 0.05, r * 0.3, r * 0.3, tongue=False)
        d.rounded_rectangle(((cx + r * 0.02) * S, (my + r * 0.08) * S, (cx + r * 0.22) * S, (my + r * 0.44) * S), radius=int(r * 0.09 * S), fill=(250, 120, 140, 255), outline=INK + (255,), width=int(r * 0.04 * S))
    elif mood == "lovely":
        for sx in (-1, 1):
            heart(d, S, cx + sx * ex, ey, r * 0.021, fill=(255, 150, 175))
        smile(d, S, cx, my, r * 0.3, r * 0.07)
    elif mood == "sparkly":
        for sx in (-1, 1):
            sparkle(d, S, cx + sx * ex, ey, r * 0.27, fill=(255, 250, 246))
        mouth_open(d, S, cx, my - r * 0.04, r * 0.24, r * 0.3)
    elif mood == "surprise":
        for sx in (-1, 1):
            eye_open(d, S, cx + sx * ex, ey, er * 1.35, (0, 0), pupil=0.42)
            brow(d, S, cx + sx * (ex - r * 0.18), ey - er * 2.3, cx + sx * (ex + r * 0.18), ey - er * 2.6, r * 0.05)
        d.ellipse(((cx - r * 0.1) * S, my * S, (cx + r * 0.1) * S, (my + r * 0.28) * S), fill=INK + (255,))
    elif mood == "cry":
        for sx in (-1, 1):
            d.line([((cx + sx * ex - sx * r * 0.2) * S, (ey - er * 0.9) * S), ((cx + sx * ex + sx * r * 0.18) * S, ey * S), ((cx + sx * ex - sx * r * 0.2) * S, (ey + er * 0.9) * S)], fill=INK + (255,), width=int(r * 0.07 * S), joint="curve")
            d.polygon([((cx + sx * ex - r * 0.2) * S, (ey + er * 1.2) * S), ((cx + sx * ex + r * 0.2) * S, (ey + er * 1.2) * S), ((cx + sx * ex + r * 0.26) * S, (cy + r * 0.95) * S), ((cx + sx * ex - r * 0.26) * S, (cy + r * 0.95) * S)], fill=(150, 205, 245, 255), outline=INK + (255,))
        d.pieslice(((cx - r * 0.2) * S, my * S, (cx + r * 0.2) * S, (my + r * 0.5) * S), 180, 360, fill=INK + (255,))
    elif mood == "sad":
        for sx in (-1, 1):
            eye_open(d, S, cx + sx * ex, ey + er * 0.2, er * 1.2, (sx * 0.1, 0.3))
            brow(d, S, cx + sx * (ex + r * 0.2), ey - er * 1.9, cx + sx * (ex - r * 0.2), ey - er * 2.5, r * 0.06)
        d.ellipse(((cx - ex - r * 0.07) * S, (ey + er * 1.4) * S, (cx - ex + r * 0.07) * S, (ey + er * 2.4) * S), fill=(150, 205, 245, 255))
        frown(d, S, cx, my + r * 0.1, r * 0.28, r * 0.07)
    elif mood in ("mad", "angry"):
        for sx in (-1, 1):
            eye_open(d, S, cx + sx * ex, ey + er * 0.4, er * 1.2, (-sx * 0.1, 0.25), pupil=0.45)
            brow(d, S, cx + sx * (ex + r * 0.26), ey - er * 2.4, cx + sx * (ex - r * 0.18), ey - er * 0.9, r * 0.09)
        if mood == "angry":
            mouth_open(d, S, cx, my + r * 0.12, r * 0.34, r * 0.22, teeth=True)
        else:
            d.pieslice(((cx - r * 0.3) * S, (my + r * 0.05) * S, (cx + r * 0.3) * S, (my + r * 0.5) * S), 180, 360, fill=INK + (255,))
    elif mood == "sleepy":
        for sx in (-1, 1):
            eye_closed(d, S, cx + sx * ex, ey + er * 0.4, er * 1.1, happy=False)
        d.ellipse(((cx - r * 0.06) * S, (my + r * 0.04) * S, (cx + r * 0.06) * S, (my + r * 0.2) * S), fill=INK + (255,))
    elif mood == "cool":
        d.rounded_rectangle(((cx - r * 0.82) * S, (ey - er * 1.5) * S, (cx + r * 0.82) * S, (ey + er * 1.7) * S), radius=int(r * 0.12 * S), fill=(18, 6, 12, 255))
        d.arc(((cx - r * 0.3) * S, (my - r * 0.28) * S, (cx + r * 0.3) * S, (my + r * 0.2) * S), 25, 140, fill=INK + (255,), width=int(r * 0.07 * S))
    elif mood == "sun":
        for sx in (-1, 1):
            eye_closed(d, S, cx + sx * ex, ey + er * 0.3, er * 1.05)
        mouth_open(d, S, cx, my - r * 0.06, r * 0.36, r * 0.42)
    elif mood == "bloom":
        for sx in (-1, 1):
            eye_closed(d, S, cx + sx * ex, ey + er * 0.5, er * 1.15)
        smile(d, S, cx, my, r * 0.34, r * 0.07)


EMOTE_SETS = [  # (folder, name, mood, extra)
    ("Emotes", "hi", "hi", "wave"), ("Emotes", "laugh", "laugh", "tear"), ("Emotes", "lovely", "lovely", "hearts"),
    ("Emotes", "pinata_party", "party", "party"), ("Emotes", "sparkly", "sparkly", "sparkles"), ("Emotes", "surprise", "surprise", "lines"),
    ("Emotes/Hype", "hype", "hype", "cap"),
    ("Emotes/Tier1", "cry", "cry", ""), ("Emotes/Tier1", "fun", "fun", "sparkles"), ("Emotes/Tier1", "happycat", "laughing", "cat"),
    ("Emotes/Tier1", "joyful", "joyful", "petals"), ("Emotes/Tier1", "laughing", "laughing", "tear"), ("Emotes/Tier1", "mad", "mad", "steam"),
    ("Emotes/Tier1", "playful", "playful", ""), ("Emotes/Tier1", "sad", "sad", ""), ("Emotes/Tier1", "sleepy", "sleepy", "zzz"),
    ("Emotes/Tier1", "veryangry", "angry", "lines"),
    ("Emotes/Tier2_3_Bits", "bits10k_legend", "sun", "crown"), ("Emotes/Tier2_3_Bits", "bits1k_gem", "sparkly", "gem"),
    ("Emotes/Tier2_3_Bits", "bits5k_cool", "cool", "sparkles"), ("Emotes/Tier2_3_Bits", "tier2_bloom", "bloom", "roses"),
    ("Emotes/Tier2_3_Bits", "tier3_royal", "royal", "crown"),
]
ANIMATED = {"happycat", "laughing", "mad", "playful", "sleepy"}


def emote(mood, extra, size, t=0.0, anim=None):
    k = size / 448

    def fn(d, S):
        cx, cy, r = 224 * k, 252 * k, 148 * k
        dx = dy = 0
        if anim == "bounce":
            dy = -abs(math.sin(math.pi * t * 2)) * 16 * k
        elif anim == "shake":
            dx = math.sin(2 * math.pi * t * 4) * 9 * k
        elif anim == "sway":
            dx = math.sin(2 * math.pi * t) * 8 * k
        x0, y0 = cx + dx, cy + dy
        if mood == "sun":
            for i in range(16):
                a = 2 * math.pi * i / 16
                d.line([((x0 + math.cos(a) * r * 1.12) * S, (y0 + math.sin(a) * r * 1.12) * S), ((x0 + math.cos(a) * r * 1.3) * S, (y0 + math.sin(a) * r * 1.3) * S)], fill=(250, 205, 80, 255), width=int(r * 0.06 * S))
        if extra == "cat":
            for sx in (-1, 1):
                wig = math.sin(2 * math.pi * t) * 8 * k * sx
                pts = [(x0 + sx * r * 0.9, y0 - r * 0.25), (x0 + sx * r * 0.88 + wig, y0 - r * 1.25), (x0 + sx * r * 0.25, y0 - r * 0.86)]
                d.polygon([(x * S, y * S) for x, y in pts], fill=RED + (255,), outline=INK + (255,), width=int(r * 0.08 * S))
                inner = [(x0 + sx * r * 0.78, y0 - r * 0.42), (x0 + sx * r * 0.78 + wig, y0 - r * 1.02), (x0 + sx * r * 0.42, y0 - r * 0.8)]
                d.polygon([(x * S, y * S) for x, y in inner], fill=(250, 150, 170, 255))
                heart(d, S, x0 + sx * r * 0.72 + wig * 0.5, y0 - r * 0.72, r * 0.016)
            for i, yy in enumerate((0.38, 0.5, 0.62)):
                for sx in (-1, 1):
                    d.line([((x0 + sx * r * 0.98) * S, (y0 + r * yy) * S), ((x0 + sx * r * 1.4) * S, (y0 + r * (yy + (i - 1) * 0.08)) * S)], fill=INK + (255,), width=int(r * 0.04 * S))
            berry_face(d, S, x0, y0, r, "laughing", t)
            d.ellipse(((x0 - r * 0.07) * S, (y0 + r * 0.04) * S, (x0 + r * 0.07) * S, (y0 + r * 0.15) * S), fill=(250, 150, 170, 255), outline=INK + (255,), width=int(r * 0.03 * S))
            return
        berry_face(d, S, x0, y0, r, mood, t)
        if extra == "hearts":
            heart(d, S, x0 + r * 0.98, y0 - r * 0.78, r * 0.025)
            heart(d, S, x0 - r * 0.98, y0 - r * 0.5, r * 0.018)
            heart(d, S, x0 + r * 0.85, y0 + r * 0.85, r * 0.018)
        if extra in ("sparkles", "gem"):
            sparkle(d, S, x0 + r * 1.02, y0 - r * 0.62, r * 0.24)
            sparkle(d, S, x0 - r * 1.0, y0 - r * 0.5, r * 0.2)
            sparkle(d, S, x0 + r * 1.0, y0 + r * 0.55, r * 0.13)
        if extra == "gem":
            pts = [(x0 + r * 0.72, y0 - r * 1.0), (x0 + r * 1.0, y0 - r * 1.0), (x0 + r * 1.1, y0 - r * 0.84), (x0 + r * 0.86, y0 - r * 0.6), (x0 + r * 0.62, y0 - r * 0.84)]
            d.polygon([(x * S, y * S) for x, y in pts], fill=(120, 210, 250, 255), outline=INK + (255,), width=int(r * 0.04 * S))
        if extra == "tear":
            for sx in (-1, 1):
                d.ellipse(((x0 + sx * r * 0.96 - r * 0.1) * S, (y0 - r * 0.02) * S, (x0 + sx * r * 0.96 + r * 0.1) * S, (y0 + r * 0.3) * S), fill=(150, 205, 245, 255), outline=INK + (255,), width=int(r * 0.03 * S))
        if extra == "wave":
            wob = math.sin(2 * math.pi * t * 2) * 6 * k
            p0, p1 = ((x0 + r * 0.98) * S, (y0 + r * 0.55) * S), ((x0 + r * 1.2 + wob) * S, (y0 - r * 0.45) * S)
            d.line([p0, p1], fill=INK + (255,), width=int(r * 0.32 * S))
            d.line([p0, p1], fill=RED + (255,), width=int(r * 0.2 * S))
            d.ellipse(((x0 + r * 1.2 + wob - r * 0.17) * S, (y0 - r * 0.62) * S, (x0 + r * 1.2 + wob + r * 0.17) * S, (y0 - r * 0.28) * S), fill=RED + (255,), outline=INK + (255,), width=int(r * 0.06 * S))
        if extra == "lines":
            for i in range(3):
                d.line([((x0 + r * (0.78 + i * 0.12)) * S, (y0 - r * (1.0 + i * 0.1)) * S), ((x0 + r * (0.95 + i * 0.12)) * S, (y0 - r * (1.18 + i * 0.1)) * S)], fill=INK + (255,), width=int(r * 0.05 * S))
        if extra == "steam":
            for bx, by, br in ((0.95, -0.85, 0.1), (1.12, -1.0, 0.07), (0.78, -1.05, 0.06)):
                d.ellipse(((x0 + r * bx - r * br) * S, (y0 + r * by - r * br) * S, (x0 + r * bx + r * br) * S, (y0 + r * by + r * br) * S), outline=INK + (255,), width=int(r * 0.03 * S), fill=(255, 250, 246, 255))
        if extra == "zzz":
            f = ImageFont.truetype(str(FONTS / "georgiab.ttf"), int(r * 0.42 * S))
            for i, (zx, zy) in enumerate(((0.82, -0.62), (1.02, -0.88), (1.2, -1.14))):
                if (t * 3 + i) % 3 < 2.3:
                    d.text(((x0 + r * zx) * S, (y0 + r * zy) * S), "z", font=f, fill=(250, 245, 240, 255), anchor="mm")
        if extra == "crown":
            pts = [(x0 - r * 0.46, y0 - r * 0.98), (x0 - r * 0.46, y0 - r * 1.42), (x0 - r * 0.23, y0 - r * 1.2), (x0, y0 - r * 1.55),
                   (x0 + r * 0.23, y0 - r * 1.2), (x0 + r * 0.46, y0 - r * 1.42), (x0 + r * 0.46, y0 - r * 0.98)]
            d.polygon([(x * S, y * S) for x, y in pts], fill=(255, 208, 90, 255), outline=INK + (255,), width=int(r * 0.06 * S))
            d.rectangle(((x0 - r * 0.46) * S, (y0 - r * 1.08) * S, (x0 + r * 0.46) * S, (y0 - r * 0.98) * S), fill=(214, 150, 40, 255))
        if extra == "party":
            pts = [(x0 - r * 0.32, y0 - r * 0.9), (x0 + r * 0.05, y0 - r * 1.62), (x0 + r * 0.42, y0 - r * 0.9)]
            d.polygon([(x * S, y * S) for x, y in pts], fill=(250, 200, 80, 255), outline=INK + (255,), width=int(r * 0.06 * S))
            for px, py, col in ((1.0, -0.3, (250, 100, 150)), (-1.05, -0.1, (110, 200, 250)), (0.95, 0.5, (250, 225, 100)), (-0.9, 0.65, (170, 130, 250)), (0.2, 1.1, (250, 160, 200))):
                d.rectangle(((x0 + r * px - 8 * k) * S, (y0 + r * py - 14 * k) * S, (x0 + r * px + 8 * k) * S, (y0 + r * py + 14 * k) * S), fill=col + (255,))
        if extra == "roses":
            for i in range(5):
                a = math.radians(200 + i * 35)
                rose(d, S, x0 + math.cos(a) * r * 0.95, y0 + math.sin(a) * r * 0.95, r * 0.24, layers=3, leaves=False)
        if extra == "cap":
            d.pieslice(((x0 - r * 0.9) * S, (y0 - r * 1.2) * S, (x0 + r * 0.9) * S, (y0 - r * 0.1) * S), 180, 360, fill=(30, 36, 70, 255), outline=INK + (255,), width=int(r * 0.07 * S))
            d.rectangle(((x0 - r * 1.0) * S, (y0 - r * 0.68) * S, (x0 + r * 1.0) * S, (y0 - r * 0.56) * S), fill=(30, 36, 70, 255), outline=INK + (255,), width=int(r * 0.05 * S))
            for i in range(3):
                d.line([((x0 - r * 1.4) * S, (y0 + (i - 1) * r * 0.2) * S), ((x0 - r * 1.1) * S, (y0 + (i - 1) * r * 0.2) * S)], fill=(250, 200, 70, 255), width=int(r * 0.05 * S))
        if extra == "petals":
            for px, py in ((-1.0, -0.3), (1.0, 0.1), (-0.9, 0.6)):
                d.ellipse(((x0 + r * px - r * 0.12) * S, (y0 + r * py - r * 0.07) * S, (x0 + r * px + r * 0.12) * S, (y0 + r * py + r * 0.07) * S), fill=(250, 150, 175, 255))
    return layer((size, size), fn)


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    print("Saved", path.relative_to(ROOT))


def main():
    for name, title, sym in PANELS:
        save(panel(title, sym).convert("RGB"), OUT / f"{name}.png")
    for tier in BADGES:
        save(badge(tier), OUT / "Badges" / f"{tier[0]}_432.png")
    for t in (2, 3):
        save(flair(t), OUT / "Flair" / f"tier{t}_flair_432.png")
    for kind in ("berry", "rose", "star"):
        name = "channel_points" if kind == "berry" else f"channel_points_{kind}"
        save(points_icon(kind), OUT / f"{name}_432.png")
    for folder, name, mood, extra in EMOTE_SETS:
        for size in (448, 112, 56, 28):
            if name in ANIMATED:
                anim = {"happycat": "sway", "laughing": "bounce", "mad": "shake", "playful": "sway", "sleepy": "sway"}[name]
                frames = [emote(mood, extra, size, i / 20, anim) for i in range(20)]
                p = OUT / folder / f"{name}_{size}.gif"
                p.parent.mkdir(parents=True, exist_ok=True)
                frames[0].save(p, save_all=True, append_images=frames[1:], duration=60, disposal=2, loop=0, optimize=False)
                print("Saved", p.relative_to(ROOT))
            else:
                save(emote(mood, extra, size), OUT / folder / f"{name}_{size}.png")


if __name__ == "__main__":
    main()

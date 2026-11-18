#!/usr/bin/env python3
"""Exhibition kit for "Urban Dictionary - Student Exhibition" (New Media Arts), built from the poster's look:
soft grey-lilac to peach gradient, white grid lines, hand-painted skyline of cream / grey-green / charcoal towers with pink stripes,
hot pink title, sans for names and mono for dates.
Output: C:/Users/SaphiresSilver/Documents/twitch/UrbanDictionary/<Category>/<name>.png   (not used by the portfolio site)

    python tools/make_exhibition.py            # everything
    python tools/make_exhibition.py poster social
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONTS = Path("C:/Windows/Fonts")
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/UrbanDictionary")

# ---- editable event details ------------------------------------------------------------------------------
TITLE, SUB, FIELD = "URBAN DICTIONARY", "STUDENT EXHIBITION", "NEW MEDIA ARTS"
SCHED = [("27.01.17", "19:00", "OPENING AND AFTERPARTY"), ("27.01.17", "12:00-18:00", "EXHIBITION DAY"), ("29.01.17", "12:00-18:00", "EXHIBITION DAY AND CLOSING")]
SUPPORT, ORG = "Brumma Records", "Tilvane Print"
VENUE = "[VENUE NAME]  ·  [ADDRESS]"
BLURB = "A student exhibition of new media works about the city, its signs, its noise and its language."

# ---- palette and type ----------------------------------------------------------------------------------
PINK = (240, 20, 140)
INK = (26, 24, 32)
CREAM = (224, 222, 204)
GREYGREEN = (128, 150, 150)
CHAR = (30, 28, 38)
WHITE = (255, 255, 255)
GREY = (96, 96, 108)
BOLD, REG, MONO = "segoeuib.ttf", "segoeui.ttf", "consola.ttf"
if not (FONTS / MONO).exists():
    MONO = "cour.ttf"


# ================================================================================================ helpers
def tw(text, fname, size, track=0):
    f = ImageFont.truetype(str(FONTS / fname), int(size * 2))
    d = ImageDraw.Draw(Image.new("L", (4, 4)))
    return (sum(d.textlength(c, font=f) for c in text) + track * 2 * (len(text) - 1)) / 2 if track else d.textlength(text, font=f) / 2


def T(img, text, x, y, size, fname=REG, col=INK, anchor="left", track=0, alpha=255):
    """Draw text with its baseline at y (anchor left / center / right), supersampled 2x on a small tile."""
    size = max(4, size)
    f = ImageFont.truetype(str(FONTS / fname), int(size * 2))
    d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    total = (sum(d0.textlength(c, font=f) for c in text) + track * 2 * (len(text) - 1)) if track else d0.textlength(text, font=f)
    pad = int(size * 0.6)
    asc = int(size * 2 * 1.2)
    tile = Image.new("L", (int(total) + 2 * pad * 2, int(size * 2 * 1.75)), 0)
    td = ImageDraw.Draw(tile)
    cx = pad * 2
    if track:
        for c in text:
            td.text((cx, asc), c, font=f, fill=255, anchor="ls")
            cx += d0.textlength(c, font=f) + track * 2
    else:
        td.text((cx, asc), text, font=f, fill=255, anchor="ls")
    tile = tile.resize((tile.width // 2, tile.height // 2), Image.LANCZOS)
    wpx = total / 2
    px = x - (wpx / 2 if anchor == "center" else wpx if anchor == "right" else 0) - pad
    py = y - asc / 2
    layer = Image.new("RGBA", tile.size, tuple(col) + (255,))
    layer.putalpha(tile.point(lambda v: v * alpha // 255))
    img.alpha_composite(layer, (int(round(px)), int(round(py)))) if (px >= 0 and py >= 0 and px + tile.width <= img.width and py + tile.height <= img.height) else img.paste(layer, (int(round(px)), int(round(py))), layer)
    return img


def Tfit(img, text, x, y, size, maxw, fname=REG, col=INK, anchor="left", track=0):
    while size > 8 and tw(text, fname, size, track) > maxw:
        size -= 2
    return T(img, text, x, y, size, fname, col, anchor, track), size


def rough(poly, amp, step, rnd):
    out = []
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L / step))
        for j in range(k):
            t = j / k
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp), y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
    return out


def noise_tex(size, strength=0.22, scale=7, seed=1):
    w, h = size
    n = Image.effect_noise((max(8, w // scale), max(8, h // scale)), 60).filter(ImageFilter.GaussianBlur(1.2))
    n = n.resize(size, Image.BICUBIC)
    return n.point(lambda v: int(255 * (1 - strength) + v * strength))


# ================================================================================================ artwork
def background(W, H, seed=3, lines=True, flat=False):
    top, mid, bot = np.array((188, 188, 198)), np.array((212, 196, 206)), np.array((238, 192, 184))
    t = np.linspace(0, 1, H)[:, None]
    col = np.where(t < 0.55, top + (mid - top) * (t / 0.55), mid + (bot - mid) * ((t - 0.55) / 0.45))
    arr = np.repeat(col[:, None, :], W, axis=1).astype("uint8")
    img = Image.fromarray(arr.reshape(H, W, 3), "RGB").convert("RGBA")
    rnd = random.Random(seed)
    lay = Image.new("RGBA", (max(8, W // 8), max(8, H // 8)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(9):
        cx, cy = rnd.randint(0, lay.width), rnd.randint(0, lay.height)
        r = rnd.randint(lay.width // 6, lay.width // 2)
        c = rnd.choice(((200, 200, 214), (226, 206, 214), (174, 178, 192), (240, 214, 206)))
        d.ellipse((cx - r, cy - r * 1.4, cx + r, cy + r * 1.4), fill=c + (70,))
    lay = lay.filter(ImageFilter.GaussianBlur(lay.width / 12)).resize((W, H), Image.BICUBIC)
    img = Image.alpha_composite(img, lay)
    if lines:
        d = ImageDraw.Draw(img)
        lw = max(2, int(W / 330))
        wh = (255, 255, 255, 235)
        d.line([(0, H * 0.123), (W * 0.68, H * 0.123)], fill=wh, width=lw)
        d.line([(W * 0.68, 0), (W * 0.68, H * 0.5)], fill=wh, width=lw)
        d.line([(W * 0.69, H * 0.047), (W, H * 0.047)], fill=wh, width=lw)
        d.line([(W * 0.70, H * 0.047), (W * 0.70, H * 0.5)], fill=wh, width=lw)
        pk = (240, 130, 150, 220)
        d.line([(0, H * 0.505), (W * 0.18, H * 0.505)], fill=pk, width=lw)
        d.line([(W * 0.09, H * 0.505), (W * 0.09, H * 0.66)], fill=pk, width=lw)
        d.line([(W * 0.68, H * 0.485), (W * 0.82, H * 0.485)], fill=pk, width=lw)
    return img


def skyline(img, y_top, seed=5, n=11, strength=1.0, pink=0.55):
    """Hand-painted towers from y_top to the bottom of the image."""
    W, H = img.size
    rnd = random.Random(seed)
    band = H - y_top
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    amp, step = max(1.5, W / 420), max(8, W / 55)
    # hazy far towers
    for i in range(n + 3):
        w = rnd.uniform(0.05, 0.11) * W
        x0 = rnd.uniform(-0.02, 1.0) * W
        h = band * rnd.uniform(0.22, 0.62)
        top = H - h
        col = rnd.choice(((184, 184, 200), (200, 196, 208), (176, 182, 190)))
        d.polygon(rough([(x0, top), (x0 + w, top + rnd.uniform(-4, 4)), (x0 + w, H + 5), (x0, H + 5)], amp, step, rnd), fill=col + (150,))
    # near towers
    xs = sorted(rnd.uniform(-0.03, 0.97) * W for _ in range(n))
    tall = set(rnd.sample(range(n), max(2, n // 4)))
    for i, x0 in enumerate(xs):
        w = rnd.uniform(0.065, 0.13) * W
        h = band * (rnd.uniform(0.72, 1.0) if i in tall else rnd.uniform(0.28, 0.66))
        top = H - h
        front = rnd.choices((CREAM, (212, 210, 190), GREYGREEN, (238, 236, 226)), (4, 2, 2, 1))[0]
        side = int(w * rnd.uniform(0.2, 0.3))
        tl, tr = top + rnd.uniform(-0.01, 0.01) * band, top + rnd.uniform(-0.01, 0.01) * band
        d.polygon(rough([(x0, tl), (x0 + w, tr), (x0 + w, H + 5), (x0, H + 5)], amp, step, rnd), fill=front + (255,))
        d.polygon(rough([(x0 + w, tr), (x0 + w + side, tr + rnd.uniform(-0.02, 0.02) * band), (x0 + w + side, H + 5), (x0 + w, H + 5)], amp, step, rnd), fill=CHAR + (255,))
        if rnd.random() < pink:
            sx = x0 + w * rnd.uniform(0.08, 0.7)
            sw = w * rnd.uniform(0.07, 0.13)
            sy = tl + rnd.uniform(0.02, 0.2) * h
            d.polygon(rough([(sx, sy), (sx + sw, sy), (sx + sw, H + 5), (sx, H + 5)], amp * 0.6, step, rnd), fill=PINK + (255,))
        if rnd.random() < 0.55:
            sx = x0 + w * rnd.uniform(0.15, 0.75)
            sw = w * rnd.uniform(0.05, 0.1)
            sy = tl + rnd.uniform(0.15, 0.5) * h
            d.polygon(rough([(sx, sy), (sx + sw, sy), (sx + sw, sy + rnd.uniform(0.15, 0.4) * h), (sx, sy + rnd.uniform(0.15, 0.4) * h)], amp * 0.6, step, rnd), fill=CHAR + (255,))
        if rnd.random() < 0.45:
            ax = x0 + w * rnd.uniform(0.3, 0.8)
            d.line([(ax, tl), (ax + rnd.uniform(-3, 3), tl - h * rnd.uniform(0.04, 0.09))], fill=CHAR + (255,), width=max(2, int(W / 260)))
    rgb = lay.convert("RGB")
    tex = noise_tex(lay.size, 0.26, 6)
    rgb = ImageChops.multiply(rgb, Image.merge("RGB", (tex, tex, tex)))
    alpha = lay.split()[3].filter(ImageFilter.GaussianBlur(max(0.6, W / 2600)))
    if strength < 1:
        alpha = alpha.point(lambda v: int(v * strength))
    rgb.putalpha(alpha)
    return Image.alpha_composite(img, rgb)


def art(W, H, y_top_frac=0.45, seed=3, n=11, lines=True, strength=1.0):
    return skyline(background(W, H, seed, lines), int(H * y_top_frac), seed + 2, n, strength)


# ================================================================================================ blocks
def lockup(img, x, y, s, align="left", track=0):
    """FIELD / TITLE / SUB with baseline of the title at y. s = size of the title."""
    anchor = align
    img = T(img, FIELD, x, y - s * 1.05, s * 0.3, MONO, INK, anchor, track=1)
    img = T(img, TITLE, x, y, s, BOLD, PINK, anchor, track=0)
    img = T(img, SUB, x, y + s * 0.62, s * 0.46, REG, INK, anchor, track=0)
    return img


def schedule(img, x, y, s, gap=None, short=False):
    gap = gap or s * 2.1
    for i, (d_, t_, l_) in enumerate(SCHED):
        yy = y + i * gap
        img = T(img, d_, x, yy, s, BOLD, INK)
        img = T(img, t_, x + s * 4.2, yy, s * 0.78, MONO, INK)
        img = T(img, l_, x + s * 4.2 + (s * 7.4 if not short else s * 6.4), yy, s * 0.78, MONO, INK)
    return img


def schedule_stack(img, cx, y, s, anchor="center"):
    """Centered, one block per day: DATE, then time and label under it."""
    for i, (d_, t_, l_) in enumerate(SCHED):
        yy = y + i * s * 3.4
        img = T(img, d_, cx, yy, s * 1.25, BOLD, INK, anchor)
        img = T(img, t_ + "  " + l_, cx, yy + s * 1.2, s * 0.62, MONO, INK, anchor)
    return img


def credits(img, cx, y, s, anchor="center", both=True):
    img = T(img, "SUPPORTED BY", cx, y, s * 0.62, MONO, PINK, anchor)
    img = T(img, SUPPORT, cx, y + s * 1.2, s, REG, INK, anchor)
    if both:
        img = T(img, "ORGANIZED BY", cx, y + s * 2.9, s * 0.62, MONO, PINK, anchor)
        img = T(img, ORG, cx, y + s * 4.1, s, REG, INK, anchor)
    return img


def save(img, cat, name):
    p = OUT / cat / (name + ".png")
    p.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(p, optimize=True)
    print("saved", cat + "/" + name, flush=True)


# ================================================================================================ the poster (reference layout 540x960)
def poster_layout(img, s, ox=0, oy=0):
    """Draws the poster text with the original proportions (reference width 540 px, scale s)."""
    X = lambda v: ox + v * s
    Y = lambda v: oy + v * s
    img = T(img, "SUPPORTED BY", X(30), Y(37), 13 * s, MONO, PINK)
    img = T(img, SUPPORT, X(148), Y(38), 20 * s, REG, INK)
    img = T(img, FIELD, X(459), Y(113), 14 * s, MONO, INK, "right")
    img = T(img, TITLE, X(36), Y(160), 47 * s, BOLD, PINK)
    img = T(img, SUB, X(66), Y(192), 22 * s, REG, INK)
    for i, (d_, t_, l_) in enumerate(SCHED):
        yy = 248 + i * 43
        img = T(img, d_, X(63), Y(yy), 20 * s, BOLD, INK)
        img = T(img, t_, X(159), Y(yy), 15 * s, MONO, INK)
        img = T(img, l_, X(254), Y(yy), 15 * s, MONO, INK)
    img = T(img, "ORGANIZED BY", X(287), Y(366), 14 * s, MONO, PINK, "center")
    img = T(img, ORG, X(287), Y(402), 20 * s, REG, INK, "center")
    return img


def poster(W, H, name_cat=("Print", "poster")):
    s = W / 540
    img = art(W, H, max(0.45, 425 * s / H), seed=3, n=12)
    return poster_layout(img, s)


# ================================================================================================ PRINT
def a3_poster():
    return poster(3508, 4961)


def flyer_front():
    return poster(1748, 2480)


def flyer_back():
    W, H = 1748, 2480
    img = background(W, H, 11)
    s = W / 540
    img = T(img, FIELD, 70 * s, 70 * s, 14 * s, MONO, INK)
    img = T(img, TITLE, 68 * s, 120 * s, 40 * s, BOLD, PINK)
    img = T(img, SUB, 70 * s, 148 * s, 20 * s, REG, INK)
    # blurb, wrapped by hand
    words, lines, cur = BLURB.split(), [], ""
    for w_ in words:
        if tw(cur + " " + w_, REG, 20 * s) > W - 160 * s and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    for i, l in enumerate(lines):
        img = T(img, l, 70 * s, (200 + i * 28) * s, 20 * s, REG, INK)
    img = schedule(img, 70 * s, 330 * s, 18 * s, gap=44 * s)
    img = T(img, "WHERE", 70 * s, 500 * s, 14 * s, MONO, PINK)
    img = T(img, VENUE, 70 * s, 530 * s, 20 * s, REG, INK)
    img = T(img, "FREE ENTRY", 70 * s, 590 * s, 14 * s, MONO, PINK)
    img = T(img, "Come to the opening night or any exhibition day.", 70 * s, 620 * s, 20 * s, REG, INK)
    d = ImageDraw.Draw(img)
    d.rectangle((70 * s, 650 * s, 70 * s + 76 * s, 650 * s + 76 * s), outline=INK + (255,), width=int(2.5 * s))
    img = T(img, "QR", 70 * s + 38 * s, 695 * s, 14 * s, MONO, GREY, "center")
    img = T(img, "SUPPORTED BY  " + SUPPORT, 170 * s, 678 * s, 13 * s, MONO, INK)
    img = T(img, "ORGANIZED BY  " + ORG, 170 * s, 698 * s, 13 * s, MONO, INK)
    return skyline(img, int(H * 0.935), 17, 10, 1.0)


def invitation_front():
    W, H = 1500, 2100
    img = art(W, H, 0.55, seed=21, n=10)
    s = W / 540
    img = T(img, "YOU ARE INVITED", W / 2, 150 * s, 17 * s, MONO, PINK, "center", track=3)
    img = T(img, FIELD, W / 2, 235 * s, 14 * s, MONO, INK, "center")
    img = T(img, "URBAN", W / 2, 290 * s, 56 * s, BOLD, PINK, "center")
    img = T(img, "DICTIONARY", W / 2, 345 * s, 56 * s, BOLD, PINK, "center")
    img = T(img, SUB, W / 2, 380 * s, 22 * s, REG, INK, "center")
    return img


def invitation_back():
    W, H = 1500, 2100
    s = W / 540
    img = background(W, H, 23)
    img = T(img, "OPENING AND AFTERPARTY", W / 2, 150 * s, 15 * s, MONO, PINK, "center", track=2)
    img = T(img, "27.01.17", W / 2, 215 * s, 54 * s, BOLD, INK, "center")
    img = T(img, "19:00", W / 2, 250 * s, 26 * s, MONO, INK, "center")
    img = T(img, VENUE, W / 2, 310 * s, 18 * s, REG, INK, "center")
    img = T(img, "EXHIBITION DAYS", W / 2, 400 * s, 15 * s, MONO, PINK, "center", track=2)
    img = T(img, "27.01.17  12:00-18:00", W / 2, 435 * s, 20 * s, MONO, INK, "center")
    img = T(img, "29.01.17  12:00-18:00  (closing)", W / 2, 465 * s, 20 * s, MONO, INK, "center")
    img = T(img, "Please confirm your visit: [EMAIL / PHONE]", W / 2, 540 * s, 17 * s, REG, INK, "center")
    img = credits(img, W / 2, 580 * s, 17 * s)
    return skyline(img, int(H * 0.88), 25, 9, 1.0)


def program_cover():
    return poster(1748, 2480)


def program_schedule():
    W, H = 2480, 3508
    s = W / 540
    img = background(W, H, 31)
    img = T(img, "PROGRAM", 60 * s, 90 * s, 48 * s, BOLD, PINK)
    img = T(img, TITLE + "  ·  " + SUB, 62 * s, 120 * s, 17 * s, MONO, INK)
    y = 190
    days = [("FRIDAY  27.01.17", [("19:00", "Opening and afterparty"), ("12:00-18:00", "Exhibition day")]), ("SUNDAY  29.01.17", [("12:00-18:00", "Exhibition day and closing")])]
    for head, items in days:
        img = T(img, head, 60 * s, y * s, 26 * s, BOLD, INK)
        d = ImageDraw.Draw(img)
        d.line([(60 * s, (y + 8) * s), (480 * s, (y + 8) * s)], fill=PINK + (255,), width=int(2 * s))
        for i, (t_, l_) in enumerate(items):
            img = T(img, t_, 60 * s, (y + 42 + i * 34) * s, 18 * s, MONO, PINK)
            img = T(img, l_, 190 * s, (y + 42 + i * 34) * s, 20 * s, REG, INK)
        y += 40 + len(items) * 34 + 38
    img = T(img, "EXHIBITING STUDENTS", 60 * s, (y + 8) * s, 15 * s, MONO, PINK)
    for i in range(4):
        img = T(img, "[Student name]  -  [work title]", 60 * s, (y + 42 + i * 30) * s, 18 * s, REG, INK)
    img = T(img, "WHERE", 60 * s, (y + 190) * s, 15 * s, MONO, PINK)
    img = T(img, VENUE, 60 * s, (y + 218) * s, 20 * s, REG, INK)
    img = T(img, "SUPPORTED BY  " + SUPPORT, 60 * s, (y + 262) * s, 13 * s, MONO, INK)
    img = T(img, "ORGANIZED BY  " + ORG, 60 * s, (y + 282) * s, 13 * s, MONO, INK)
    return skyline(img, int(H * 0.9), 33, 12, 1.0)


def wall_label():
    W, H = 1200, 800
    img = Image.new("RGBA", (W, H), (250, 249, 246, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 26, H), fill=PINK + (255,))
    img = T(img, "[ARTIST NAME]", 80, 130, 54, BOLD, INK)
    img = T(img, "[Work title], 2017", 80, 200, 38, REG, INK)
    img = T(img, "[Medium  ·  dimensions  ·  duration]", 80, 255, 26, MONO, GREY)
    for i, l in enumerate(("Two or three lines about the work: what it is,", "what it shows and why it belongs in the", "Urban Dictionary exhibition.")):
        img = T(img, l, 80, 360 + i * 48, 32, REG, INK)
    img = T(img, "URBAN DICTIONARY  ·  " + FIELD, 80, 700, 22, MONO, PINK)
    return img


def statement_panel():
    W, H = 2480, 3508
    s = W / 540
    img = background(W, H, 37, lines=False)
    img = T(img, FIELD, 60 * s, 80 * s, 14 * s, MONO, INK)
    img = T(img, "[ARTIST NAME]", 58 * s, 150 * s, 50 * s, BOLD, PINK)
    img = T(img, "Artist statement", 60 * s, 185 * s, 22 * s, REG, INK)
    for i in range(8):
        img = T(img, "Write the statement here. Two or three short paragraphs", 60 * s, (270 + i * 34) * s, 18 * s, REG, INK, alpha=190 if i > 2 else 255)
    img = T(img, TITLE + "  ·  " + SUB, 60 * s, 640 * s, 14 * s, MONO, PINK)
    return skyline(img, int(H * 0.86), 39, 10, 1.0)


# ================================================================================================ SIGNAGE
def entrance_sign():
    W, H = 3508, 2480
    img = art(W, H, 0.6, seed=41, n=13)
    s = H / 540
    img = T(img, "WELCOME TO", W / 2, 105 * s, 17 * s, MONO, PINK, "center", track=3)
    img = T(img, TITLE, W / 2, 190 * s, 58 * s, BOLD, PINK, "center")
    img = T(img, SUB + "  ·  " + FIELD, W / 2, 228 * s, 18 * s, REG, INK, "center")
    img = T(img, "OPEN 12:00-18:00", W / 2, 285 * s, 24 * s, MONO, INK, "center")
    return img


def arrow_sign(direction):
    W, H = 3508, 2480
    img = background(W, H, 43, lines=False)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 0.38
    L, hw = W * 0.28, H * 0.17
    if direction in ("left", "right"):
        sgn = -1 if direction == "left" else 1
        pts = [(cx - sgn * L, cy - hw * 0.45), (cx + sgn * L * 0.35, cy - hw * 0.45), (cx + sgn * L * 0.35, cy - hw), (cx + sgn * L, cy), (cx + sgn * L * 0.35, cy + hw), (cx + sgn * L * 0.35, cy + hw * 0.45), (cx - sgn * L, cy + hw * 0.45)]
    else:
        pts = [(cx - hw * 0.45, cy + hw * 1.5), (cx - hw * 0.45, cy - hw * 0.3), (cx - hw, cy - hw * 0.3), (cx, cy - hw * 1.7), (cx + hw, cy - hw * 0.3), (cx + hw * 0.45, cy - hw * 0.3), (cx + hw * 0.45, cy + hw * 1.5)]
    d.polygon(pts, fill=PINK + (255,))
    s = H / 540
    img = T(img, "EXHIBITION", W / 2, 400 * s, 60 * s, BOLD, INK, "center")
    img = T(img, TITLE + "  ·  " + SUB, W / 2, 440 * s, 18 * s, MONO, PINK, "center")
    return skyline(img, int(H * 0.88), 45, 14, 1.0)


def opening_sign():
    W, H = 3508, 2480
    img = art(W, H, 0.55, seed=47, n=13)
    s = H / 540
    img = T(img, "TONIGHT", W / 2, 120 * s, 20 * s, MONO, PINK, "center", track=4)
    img = T(img, "OPENING", W / 2, 215 * s, 78 * s, BOLD, PINK, "center")
    img = T(img, "AND AFTERPARTY  ·  19:00", W / 2, 262 * s, 24 * s, MONO, INK, "center")
    return img


def thank_you_board():
    W, H = 3508, 2480
    img = art(W, H, 0.7, seed=51, n=12)
    s = H / 540
    img = T(img, "THANK YOU", W / 2, 150 * s, 66 * s, BOLD, PINK, "center")
    img = T(img, "to everyone who made " + TITLE.title() + " happen", W / 2, 188 * s, 20 * s, REG, INK, "center")
    img = credits(img, W / 2, 232 * s, 20 * s)
    return img


def rollup():
    W, H = 2125, 5000
    s = W / 540
    img = art(W, H, 0.7, seed=53, n=14)
    img = T(img, FIELD, W / 2, 130 * s, 15 * s, MONO, INK, "center", track=2)
    img = T(img, "URBAN", W / 2, 215 * s, 66 * s, BOLD, PINK, "center")
    img = T(img, "DICTIONARY", W / 2, 285 * s, 66 * s, BOLD, PINK, "center")
    img = T(img, SUB, W / 2, 335 * s, 28 * s, REG, INK, "center")
    img = schedule_stack(img, W / 2, 405 * s, 22 * s)
    img = credits(img, W / 2, 700 * s, 20 * s)
    return img


# ================================================================================================ WEARABLES & TICKETS
def badge(role, color):
    W, H = 1013, 1500
    img = background(W, H, 61, lines=False)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 330), fill=color + (255,))
    img = T(img, FIELD, 60, 90, 30, MONO, WHITE if color != CREAM else INK)
    img = T(img, TITLE, 60, 175, 84, BOLD, WHITE if color != CREAM else PINK, track=0)
    img = T(img, SUB, 62, 235, 44, REG, WHITE if color != CREAM else INK)
    img = T(img, role, W / 2, 640, 128, BOLD, INK, "center")
    d.line([(120, 800), (W - 120, 800)], fill=INK + (255,), width=4)
    img = T(img, "NAME", W / 2, 860, 30, MONO, PINK, "center")
    d.line([(120, 1000), (W - 120, 1000)], fill=GREY + (255,), width=3)
    return skyline(img, 1180, 63, 8, 1.0)


def ticket(kind):
    W, H = 2000, 760
    img = art(W, H, 0.45, seed=71, n=12, lines=False)
    d = ImageDraw.Draw(img)
    d.rectangle((1400, 0, W, H), fill=(255, 255, 255, 215))
    for y in range(20, H, 40):
        d.ellipse((1392, y - 5, 1408, y + 11), fill=(190, 190, 200, 255))
    img = T(img, FIELD, 70, 100, 26, MONO, INK)
    img = T(img, TITLE, 66, 190, 90, BOLD, PINK)
    img = T(img, SUB, 70, 245, 40, REG, INK)
    if kind == "opening":
        img = T(img, "OPENING AND AFTERPARTY", 70, 360, 34, MONO, INK)
        img = T(img, "27.01.17  19:00", 70, 430, 60, BOLD, INK)
    else:
        img = T(img, "EXHIBITION DAY", 70, 360, 34, MONO, INK)
        img = T(img, "27.01  or  29.01.17   12:00-18:00", 70, 430, 50, BOLD, INK)
    img = T(img, VENUE, 70, 500, 28, REG, INK)
    img = T(img, "ADMIT ONE", 1700, 220, 54, BOLD, INK, "center")
    img = T(img, "No. 0000", 1700, 300, 34, MONO, PINK, "center")
    d.rectangle((1600, 400, 1800, 600), outline=INK + (255,), width=4)
    img = T(img, "QR", 1700, 515, 34, MONO, GREY, "center")
    return img


def pin_button():
    S = 1000
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    m = Image.new("L", (S * 2, S * 2), 0)
    ImageDraw.Draw(m).ellipse((0, 0, S * 2 - 1, S * 2 - 1), fill=255)
    m = m.resize((S, S), Image.LANCZOS)
    inner = skyline(background(S, S, 81, lines=False), int(S * 0.45), 83, 7, 1.0)
    inner = T(inner, "UD", S / 2, 410, 250, BOLD, PINK, "center")
    inner = T(inner, "'17", S / 2, 520, 90, BOLD, INK, "center")
    inner = T(inner, "STUDENT EXHIBITION", S / 2, 190, 52, MONO, INK, "center")
    img.paste(inner, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.ellipse((6, 6, S - 7, S - 7), outline=PINK + (255,), width=14)
    return img


def sticker():
    W, H = 1500, 600
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, W * 2 - 1, H * 2 - 1), radius=120, fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    inner = skyline(background(W, H, 91, lines=False), int(H * 0.4), 93, 9, 1.0)
    inner, _ = Tfit(inner, TITLE, W / 2, 250, 150, W - 160, BOLD, PINK, "center")
    inner = T(inner, SUB, W / 2, 320, 62, REG, INK, "center")
    img.paste(inner, (0, 0), m)
    return img


# ================================================================================================ SOCIAL & DIGITAL
def story():
    return poster(1080, 1920)


def post_square():
    W = H = 1080
    img = art(W, H, 0.5, seed=101, n=11)
    s = W / 540
    img = lockup(img, 60 * s, 118 * s, 38 * s)
    img = T(img, "27.01.17  ·  19:00  ·  OPENING", 62 * s, 200 * s, 15 * s, MONO, INK)
    return img


def post_4x5(kind):
    W, H = 1080, 1350
    img = art(W, H, 0.52, seed=111 + len(kind), n=11)
    s = W / 540
    if kind == "save":
        img = T(img, "SAVE THE DATE", W / 2, 95 * s, 15 * s, MONO, PINK, "center", track=4)
        img = T(img, "27.01.17", W / 2, 195 * s, 76 * s, BOLD, INK, "center")
        img = T(img, "19:00  OPENING AND AFTERPARTY", W / 2, 232 * s, 17 * s, MONO, INK, "center")
        img = T(img, TITLE, W / 2, 295 * s, 36 * s, BOLD, PINK, "center")
        img = T(img, SUB + "  ·  " + FIELD, W / 2, 322 * s, 15 * s, REG, INK, "center")
    elif kind == "opening":
        img = T(img, "THIS FRIDAY", W / 2, 95 * s, 15 * s, MONO, PINK, "center", track=4)
        img = T(img, "OPENING", W / 2, 180 * s, 72 * s, BOLD, PINK, "center")
        img = T(img, "AND AFTERPARTY  ·  19:00", W / 2, 218 * s, 18 * s, MONO, INK, "center")
        img = T(img, TITLE + "  ·  " + SUB, W / 2, 275 * s, 15 * s, REG, INK, "center")
    elif kind == "days":
        img = T(img, "EXHIBITION DAYS", W / 2, 95 * s, 15 * s, MONO, PINK, "center", track=4)
        img = T(img, "27 + 29", W / 2, 180 * s, 72 * s, BOLD, INK, "center")
        img = T(img, "JANUARY  ·  12:00-18:00", W / 2, 218 * s, 18 * s, MONO, INK, "center")
        img = T(img, TITLE, W / 2, 275 * s, 30 * s, BOLD, PINK, "center")
    else:
        img = T(img, "THANK YOU", W / 2, 150 * s, 68 * s, BOLD, PINK, "center")
        img = T(img, "for visiting " + TITLE.title(), W / 2, 188 * s, 20 * s, REG, INK, "center")
        img = credits(img, W / 2, 245 * s, 17 * s)
    return img


def wide(W, H, seed, big=1.0):
    """Wide banner: title left, skyline along the right side and bottom."""
    img = background(W, H, seed, lines=False)
    sk = skyline(Image.new("RGBA", (W, H), (0, 0, 0, 0)), int(H * 0.15), seed + 4, 12, 1.0)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(W * 0.52, 0), (W, 0), (W, H), (W * 0.40, H)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(W / 80))
    sk.putalpha(ImageChops.multiply(sk.split()[3], mask))
    img = Image.alpha_composite(img, sk)
    s = H / 500 * big
    ls = 62 * s
    while tw(TITLE, BOLD, ls) > W * 0.40:
        ls -= 2
    img = lockup(img, W * 0.05, H * 0.5, ls)
    img = T(img, "27.01.17  19:00  OPENING AND AFTERPARTY", W * 0.052, H * 0.5 + ls * 1.35, min(17 * s, ls * 0.3), MONO, INK)
    img = T(img, "27 + 29.01.17  12:00-18:00  EXHIBITION DAYS", W * 0.052, H * 0.5 + ls * 1.7, min(17 * s, ls * 0.3), MONO, INK)
    return img


def fb_cover():
    return wide(1920, 1005, 121)


def x_header():
    return wide(1500, 500, 123, 0.9)


def linkedin_cover():
    img = wide(1584, 396, 125, 0.75)
    return img


def email_header():
    return wide(1200, 400, 127, 0.7)


def web_banner():
    return wide(1920, 600, 129, 0.8)


def avatar():
    S = 1000
    img = skyline(background(S, S, 131, lines=False), int(S * 0.42), 133, 7, 1.0)
    img = T(img, "UD", S / 2, 400, 330, BOLD, PINK, "center")
    img = T(img, "'17", S / 2, 500, 100, BOLD, INK, "center")
    return img


def slide(kind):
    W, H = 1920, 1080
    s = W / 540
    if kind == "title":
        img = art(W, H, 0.5, seed=141, n=13)
        img = lockup(img, 120, 330, 132)
        img = T(img, "27.01.17 - 29.01.17", 124, 470, 44, MONO, INK)
    elif kind == "schedule":
        img = background(W, H, 143)
        img = T(img, "SCHEDULE", 120, 180, 100, BOLD, PINK)
        img = schedule(img, 120, 340, 44, gap=140)
        img = credits(img, 120, 800, 44, "left")
        img = skyline(img, int(H * 0.8), 145, 12, 1.0)
    elif kind == "credits":
        img = background(W, H, 147)
        img = T(img, "THE STUDENTS", 120, 180, 100, BOLD, PINK)
        for i in range(10):
            img = T(img, "[Student name]", 120 + (i % 2) * 800, 330 + (i // 2) * 110, 52, REG, INK)
        img = skyline(img, int(H * 0.8), 149, 12, 1.0)
    else:
        img = art(W, H, 0.55, seed=151, n=13)
        img = T(img, "THANK YOU", W / 2, 260, 150, BOLD, PINK, "center")
        img = credits(img, W / 2, 400, 48)
    return img


def certificate():
    W, H = 3508, 2480
    img = art(W, H, 0.78, seed=161, n=14)
    s = H / 540
    d = ImageDraw.Draw(img)
    d.rectangle((120, 120, W - 120, H - 120), outline=PINK + (255,), width=10)
    img = T(img, TITLE + "  ·  " + SUB, W / 2, 120 * s, 16 * s, MONO, INK, "center", track=3)
    img = T(img, "CERTIFICATE OF PARTICIPATION", W / 2, 190 * s, 44 * s, BOLD, PINK, "center")
    img = T(img, "This certifies that", W / 2, 255 * s, 20 * s, REG, INK, "center")
    img = T(img, "[STUDENT NAME]", W / 2, 320 * s, 52 * s, BOLD, INK, "center")
    d.line([(W * 0.25, 332 * s), (W * 0.75, 332 * s)], fill=GREY + (255,), width=4)
    img = T(img, "took part in the exhibition with the work  [WORK TITLE]", W / 2, 370 * s, 20 * s, REG, INK, "center")
    img = T(img, "27 - 29.01.17  ·  " + FIELD, W / 2, 405 * s, 17 * s, MONO, INK, "center")
    return img


def guidelines():
    W, H = 3000, 2000
    img = Image.new("RGBA", (W, H), (250, 249, 246, 255))
    s = W / 1500
    img = T(img, "URBAN DICTIONARY - visual identity", 90 * s, 110 * s, 40 * s, BOLD, INK)
    img = T(img, "COLOUR, TYPE AND THE SKYLINE MOTIF", 92 * s, 150 * s, 14 * s, MONO, PINK)
    d = ImageDraw.Draw(img)
    cols = [("Hot Pink", PINK), ("Ink", INK), ("Cream", CREAM), ("Grey-Green", GREYGREEN), ("Charcoal", CHAR), ("Haze Grey", (188, 188, 198)), ("Peach", (238, 192, 184))]
    for i, (n_, c) in enumerate(cols):
        x = 90 * s + i * 195 * s
        d.rounded_rectangle((x, 220 * s, x + 170 * s, 380 * s), radius=int(12 * s), fill=c + (255,), outline=(200, 200, 205, 255), width=2)
        img = T(img, n_, x, 410 * s, 15 * s, BOLD, INK)
        img = T(img, "#%02X%02X%02X" % c, x, 434 * s, 13 * s, MONO, GREY)
    img = T(img, "TYPE", 90 * s, 520 * s, 14 * s, MONO, PINK)
    img = T(img, "Segoe UI Bold", 90 * s, 600 * s, 56 * s, BOLD, PINK)
    img = T(img, "Headlines and dates", 92 * s, 636 * s, 16 * s, REG, GREY)
    img = T(img, "Segoe UI Regular", 90 * s, 710 * s, 40 * s, REG, INK)
    img = T(img, "Names, subtitles and body text", 92 * s, 744 * s, 16 * s, REG, GREY)
    img = T(img, "Consolas - times, labels, 27.01.17", 90 * s, 820 * s, 34 * s, MONO, INK)
    img = T(img, "Small labels and schedule lines", 92 * s, 854 * s, 16 * s, REG, GREY)
    # lockups
    lk = background(620, 380, 171, lines=False)
    lk = lockup(lk, 40, 190, 60)
    img.paste(lk.convert("RGBA").resize((int(620 * s * 0.9), int(380 * s * 0.9))), (int(800 * s), int(520 * s)))
    sk = skyline(background(1320, 330, 175, lines=False), 40, 177, 12, 1.0)
    img.paste(sk.convert("RGBA").resize((int(1320 * s * 0.95), int(330 * s * 0.95))), (int(90 * s), int(940 * s)))
    img = T(img, "Skyline motif: hand-painted towers in cream, grey-green and charcoal with hot pink stripes. Always bleeding off the bottom edge.", 90 * s, 1300 * s, 16 * s, REG, INK)
    return img


ASSETS = {
    "poster": [("Print", "poster_A3", a3_poster), ("Print", "flyer_A5_front", flyer_front), ("Print", "flyer_A5_back", flyer_back),
               ("Print", "invitation_front", invitation_front), ("Print", "invitation_back", invitation_back), ("Print", "program_cover_A5", program_cover),
               ("Print", "program_schedule_A4", program_schedule), ("Print", "wall_label_template", wall_label), ("Print", "artist_statement_panel_A4", statement_panel)],
    "signage": [("Signage", "entrance_sign_A3", entrance_sign), ("Signage", "arrow_left_A3", lambda: arrow_sign("left")), ("Signage", "arrow_right_A3", lambda: arrow_sign("right")),
                ("Signage", "arrow_up_A3", lambda: arrow_sign("up")), ("Signage", "opening_night_sign_A3", opening_sign), ("Signage", "thank_you_board_A3", thank_you_board),
                ("Signage", "roll_up_banner", rollup)],
    "wearables": [("Wearables", "badge_visitor", lambda: badge("VISITOR", PINK)), ("Wearables", "badge_student", lambda: badge("STUDENT", CHAR)),
                  ("Wearables", "badge_organizer", lambda: badge("ORGANIZER", CREAM)), ("Tickets", "ticket_opening_night", lambda: ticket("opening")),
                  ("Tickets", "ticket_exhibition_day", lambda: ticket("day")), ("Wearables", "pin_button", pin_button), ("Wearables", "sticker", sticker)],
    "social": [("Social", "instagram_story", story), ("Social", "instagram_post_square", post_square), ("Social", "post_save_the_date", lambda: post_4x5("save")),
               ("Social", "post_opening_night", lambda: post_4x5("opening")), ("Social", "post_exhibition_days", lambda: post_4x5("days")),
               ("Social", "post_thank_you", lambda: post_4x5("thanks")), ("Social", "facebook_event_cover", fb_cover), ("Social", "x_header", x_header),
               ("Social", "linkedin_cover", linkedin_cover), ("Social", "profile_avatar", avatar), ("Digital", "email_header", email_header), ("Digital", "web_banner", web_banner)],
    "digital": [("Digital", "slide_title", lambda: slide("title")), ("Digital", "slide_schedule", lambda: slide("schedule")), ("Digital", "slide_students", lambda: slide("credits")),
                ("Digital", "slide_thank_you", lambda: slide("thanks")), ("Print", "certificate_A4", certificate), ("Brand", "brand_guidelines", guidelines)],
}


def main():
    groups = [a for a in sys.argv[1:] if a in ASSETS] or list(ASSETS)
    for g in groups:
        for cat, name, fn in ASSETS[g]:
            try:
                save(fn(), cat, name)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print("  FAILED", name, repr(e), flush=True)


if __name__ == "__main__":
    main()

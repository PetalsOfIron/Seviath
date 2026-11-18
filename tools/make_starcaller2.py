#!/usr/bin/env python3
"""Starcaller kit, round 2: its own look (portholes, orbits, stars, capsules) instead of the Nightwing shapes.
Run make_starcaller.py first, then this script (it replaces emotes, badges, overlay, screens, alerts, panels)."""
import math
import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.argv = sys.argv[:1]
import make_nightwing as nw
import make_nightwing2 as n2
import make_starcaller as sc
from art import *  # noqa: F401,F403

OUT = sc.OUT
GOLD, GOLD_D, COBALT, SKY, DEEP, NIGHT, SILVER, SILVER_D, PINK = sc.GOLD, sc.GOLD_D, sc.COBALT, sc.SKY, sc.DEEP, sc.NIGHT, sc.SILVER, sc.SILVER_D, sc.PINK
CYAN = (110, 214, 240)
HEADF = "bahnschrift.ttf"
LINE = (16, 10, 36)
SKIN, SKIN_D = (244, 176, 210), (206, 118, 172)
HAIRB, HAIRD, WHITE = (24, 108, 204), (8, 44, 118), (238, 246, 255)
BLK = (22, 22, 34)


def save(img, *parts):
    nw.save(img, *parts)


# ---------------------------------------------------------------- little shapes
def star_pts(cx, cy, ro, ri, n=5, rot=-90):
    out = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180 / n)
        r = ro if i % 2 == 0 else ri
        out.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return out


def draw_star(d, cx, cy, ro, col, ri=None, n=5, outline=None, w=0):
    pts = star_pts(cx, cy, ro, ri or ro * 0.45, n)
    d.polygon(pts, fill=col + (255,), outline=(outline + (255,)) if outline else None)
    if outline and w:
        d.line(pts + [pts[0]], fill=outline + (255,), width=w)


def sparkle(d, cx, cy, r, col):
    d.polygon([(cx, cy - r), (cx + r * 0.2, cy - r * 0.2), (cx + r, cy), (cx + r * 0.2, cy + r * 0.2), (cx, cy + r), (cx - r * 0.2, cy + r * 0.2), (cx - r, cy), (cx - r * 0.2, cy - r * 0.2)], fill=col + (255,))


def orbit(canvas, cx, cy, rx, ry, tilt, col, width=3, dots=3, seed=1):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    pts = []
    for i in range(181):
        a = math.radians(i * 2)
        x, y = math.cos(a) * rx, math.sin(a) * ry
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    d.line(pts, fill=col + (200,), width=width)
    rnd = random.Random(seed)
    for _ in range(dots):
        a = math.radians(rnd.randint(0, 359))
        x, y = math.cos(a) * rx, math.sin(a) * ry
        sparkle(d, cx + x * c - y * s, cy + x * s + y * c, 14, GOLD)
    return Image.alpha_composite(canvas, lay)


def constellation(canvas, pts, col=SKY, width=2):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line(pts, fill=col + (150,), width=width)
    for x, y in pts:
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=GOLD + (255,))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 250, 220, 255))
    return Image.alpha_composite(canvas, lay)


def t2(canvas, text, xy, size, anchor="left", track=10, c1=SILVER, c2=SKY):
    m = text_mask(canvas.size, text, font(HEADF, size), xy, track=track, anchor=anchor)
    canvas = shadow(canvas, m, (0, max(2, size // 22)), max(4, size // 24), (0, 0, 0), 0.7)
    return fill_mask(canvas, m, c1, c2)


def fit2(canvas, text, xy, maxw, size, anchor="left", track=10, c1=SILVER, c2=SKY):
    while size > 30:
        m = text_mask(canvas.size, text, font(HEADF, size), xy, track=track, anchor=anchor)
        b = m.getbbox()
        if b and b[2] - b[0] <= maxw:
            break
        size -= 6
    return t2(canvas, text, xy, size, anchor, track, c1, c2), size


def porthole(canvas, art, box, cx, cy, r, ring=GOLD, dim=0.0):
    """Round window with the artwork inside, double ring and a soft glow."""
    S = canvas.size
    canvas = glow(canvas, (cx - r - 60, cy - r - 60, cx + r + 60, cy + r + 60), COBALT, blur=90, alpha=110)
    m = Image.new("L", S, 0)
    ImageDraw.Draw(m).ellipse((cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22), fill=255)
    canvas = shadow(canvas, m, (0, 18), 26, (0, 0, 0), 0.6)
    d = ImageDraw.Draw(canvas)
    d.ellipse((cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22), fill=DEEP + (255,))
    d.ellipse((cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16), outline=ring + (255,), width=6)
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), outline=COBALT + (255,), width=5)
    pic = art.crop(box).resize((2 * r, 2 * r), Image.LANCZOS).convert("RGBA")
    if dim:
        pic = Image.blend(pic, Image.new("RGBA", pic.size, DEEP + (255,)), dim)
    mm = Image.new("L", (2 * r * 3, 2 * r * 3), 0)
    ImageDraw.Draw(mm).ellipse((0, 0, 2 * r * 3 - 1, 2 * r * 3 - 1), fill=255)
    pic.putalpha(mm.resize((2 * r, 2 * r), Image.LANCZOS))
    canvas.alpha_composite(pic, (cx - r, cy - r))
    d = ImageDraw.Draw(canvas)
    for k in range(36):
        a = math.radians(k * 10)
        rr = r + 30
        (draw_star if False else (lambda *a_, **k_: None))
        sparkle(d, cx + math.cos(a) * rr, cy + math.sin(a) * rr, 7 if k % 3 else 12, ring)
    return canvas


# ---------------------------------------------------------------- screens
def screen2(art, kind, big, small, note):
    W, H = 1920, 1080
    img = sc.nebula((W, H), seed={"start": 3, "brb": 5, "end": 8, "off": 11}[kind])
    face = (30, 20, 570, 560)
    if kind == "start":
        img = orbit(img, 1400, 540, 640, 230, -24, SKY, 3, 4, 2)
        img = porthole(img, art, face, 1400, 540, 400)
        img = orbit(img, 1400, 540, 640, 230, 24, GOLD, 3, 3, 4)
        X, Y, anc, maxw = 110, 470, "left", 600
    elif kind == "brb":
        img = orbit(img, 520, 540, 620, 220, 20, SKY, 3, 4, 3)
        img = porthole(img, art, (0, 56, 540, 596), 520, 540, 400)
        img = orbit(img, 520, 540, 620, 220, -20, GOLD, 3, 3, 6)
        X, Y, anc, maxw = 1130, 470, "left", 740
    elif kind == "end":
        img = orbit(img, 960, 380, 520, 160, -8, SKY, 3, 4, 1)
        img = porthole(img, art, (60, 10, 520, 470), 960, 380, 290)
        img = orbit(img, 960, 380, 520, 160, 8, GOLD, 3, 3, 5)
        X, Y, anc, maxw = 960, 840, "center", 1500
    else:
        img = orbit(img, 1500, 600, 520, 190, -18, SKY, 2, 3, 9)
        img = porthole(img, art, face, 1500, 600, 300, ring=SILVER_D, dim=0.45)
        X, Y, anc, maxw = 110, 470, "left", 720
    img = constellation(img, [(130, 160), (230, 110), (360, 170), (460, 120)] if anc == "left" and X < 900 else [(1450, 150), (1560, 100), (1690, 160), (1800, 110)])
    img, sz = fit2(img, big, (X, Y), maxw, 140, anc, 16)
    cx = X if anc == "left" else X
    d = ImageDraw.Draw(img)
    if anc == "left":
        d.line([(X, Y + 40), (X + 300, Y + 40)], fill=GOLD + (255,), width=4)
        draw_star(d, X + 330, Y + 40, 14, GOLD)
        img = t2(img, small, (X, Y + 120), 40, "left", 12, GOLD, GOLD_D)
        img = t2(img, note, (X, Y + 178), 28, "left", 6, SILVER_D, SILVER_D)
    else:
        d.line([(X - 320, Y + 40), (X - 40, Y + 40)], fill=GOLD + (255,), width=4)
        d.line([(X + 40, Y + 40), (X + 320, Y + 40)], fill=GOLD + (255,), width=4)
        draw_star(d, X, Y + 40, 16, GOLD)
        img = t2(img, small, (X, Y + 120), 38, "center", 12, GOLD, GOLD_D)
        img = t2(img, note, (X, Y + 170), 26, "center", 6, SILVER_D, SILVER_D)
    img = t2(img, nw.NAME, (70, 90), 30, "left", 14, SILVER, SILVER)
    return img


# ---------------------------------------------------------------- overlay
def overlay2(W=1920, H=1080):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # thin top and bottom horizon lines with stars
    for y in (46, H - 46):
        d.line([(120, y), (W - 120, y)], fill=SKY + (120,), width=2)
        for x in range(200, W - 200, 240):
            sparkle(d, x, y, 10, GOLD)
    for (x, y) in ((70, 70), (W - 70, 70), (70, H - 70), (W - 70, H - 70)):
        draw_star(d, x, y, 26, GOLD, ri=10, n=4)
    # round webcam porthole
    cx, cy, r = 300, H - 310, 230
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26), fill=255)
    img = shadow(img, m, (0, 14), 18, (0, 0, 0), 0.6)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26), fill=DEEP + (255,))
    d.ellipse((cx - r - 20, cy - r - 20, cx + r + 20, cy + r + 20), outline=GOLD + (255,), width=6)
    d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), outline=COBALT + (255,), width=6)
    img = orbit(img, cx, cy, r + 120, 70, -18, SKY, 3, 2, 3)
    hole = Image.new("L", (W, H), 255)
    ImageDraw.Draw(hole).ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], hole))
    # name pill
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((560, H - 160, 1110, H - 96), radius=32, fill=DEEP + (225,), outline=GOLD + (255,), width=4)
    img = Image.alpha_composite(img, pill)
    img = t2(img, nw.NAME, (836, H - 112), 30, "center", 12, SILVER, SKY)
    # latest follower / sub pills
    for x0, txt in ((1140, "LATEST FOLLOWER"), (1500, "LATEST SUB")):
        pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(pl).rounded_rectangle((x0, H - 160, x0 + 330, H - 96), radius=32, fill=DEEP + (225,), outline=SKY + (255,), width=3)
        img = Image.alpha_composite(img, pl)
        img = t2(img, txt, (x0 + 165, H - 112), 20, "center", 8, GOLD, GOLD)
    # chat: glass rounded panel
    cb = (W - 540, 120, W - 70, H - 300)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle(cb, radius=40, fill=DEEP + (205,), outline=SKY + (255,), width=3)
    gd.rounded_rectangle((cb[0] + 10, cb[1] + 10, cb[2] - 10, cb[3] - 10), radius=32, outline=GOLD + (170,), width=2)
    img = Image.alpha_composite(img, gl)
    img = t2(img, "CHAT", ((cb[0] + cb[2]) // 2, cb[1] + 62), 34, "center", 18, SILVER, SKY)
    d = ImageDraw.Draw(img)
    d.line([(cb[0] + 120, cb[1] + 84), (cb[2] - 120, cb[1] + 84)], fill=GOLD + (255,), width=2)
    draw_star(d, (cb[0] + cb[2]) // 2, cb[1] + 84, 9, GOLD)
    return img


# ---------------------------------------------------------------- alerts (capsules)
def alert2(art, head, sub, ring, W=1000, H=320):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle((90, 50, W - 20, H - 50), radius=110, fill=255)
    img = shadow(img, m, (0, 10), 14, (0, 0, 0), 0.6)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90, 50, W - 20, H - 50), radius=110, fill=DEEP + (255,))
    for k in range(10, 200):  # soft cobalt wash to the right
        pass
    wash = Image.new("RGBA", (W, H), COBALT + (0,))
    wd = ImageDraw.Draw(wash)
    for x in range(90, W - 20):
        t = (x - 90) / (W - 110)
        wd.line([(x, 50), (x, H - 50)], fill=COBALT + (int(120 * t),))
    cap = Image.new("L", (W, H), 0)
    ImageDraw.Draw(cap).rounded_rectangle((90, 50, W - 20, H - 50), radius=110, fill=255)
    wash.putalpha(ImageChops.multiply(wash.split()[3], cap))
    img = Image.alpha_composite(img, wash)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90, 50, W - 20, H - 50), radius=110, outline=ring + (255,), width=5)
    d.rounded_rectangle((100, 60, W - 30, H - 60), radius=100, outline=SKY + (120,), width=2)
    # portrait porthole overlapping the left end
    cx, cy, r = 150, H // 2, 118
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=DEEP + (255,), outline=ring + (255,), width=6)
    pic = art.crop((30, 6, 600, 576)).resize((2 * r, 2 * r), Image.LANCZOS).convert("RGBA")
    mm = Image.new("L", (2 * r * 3, 2 * r * 3), 0)
    ImageDraw.Draw(mm).ellipse((0, 0, 2 * r * 3 - 1, 2 * r * 3 - 1), fill=255)
    pic.putalpha(mm.resize((2 * r, 2 * r), Image.LANCZOS))
    img.alpha_composite(pic, (cx - r, cy - r))
    d = ImageDraw.Draw(img)
    sparkle(d, W - 80, 86, 14, ring)
    sparkle(d, W - 120, H - 80, 9, ring)
    img = t2(img, head, (310, 122), 28, "left", 14, ring, ring)
    img, _ = fit2(img, sub, (310, 224), W - 380, 84, "left", 6, SILVER, SKY)
    return img


ALERTS = [("NEW FOLLOWER", "{name}", "follow", CYAN), ("NEW SUBSCRIBER", "{name}", "subscribe", GOLD), ("INCOMING RAID", "{name}", "raid", PINK),
          ("DONATION", "{amount}", "donation", (120, 230, 170)), ("BITS", "{amount}", "bits", (170, 150, 255))]


# ---------------------------------------------------------------- panels (capsules with star ends)
def panel2(text, sub, W=640, H=200):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle((30, 40, W - 30, H - 40), radius=60, fill=255)
    img = shadow(img, m, (0, 8), 10, (0, 0, 0), 0.55)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((30, 40, W - 30, H - 40), radius=60, fill=DEEP + (255,), outline=GOLD + (255,), width=4)
    d.rounded_rectangle((40, 50, W - 40, H - 50), radius=52, outline=COBALT + (255,), width=3)
    img = glow(img, (140, 60, W - 140, H - 60), COBALT, blur=36, alpha=90)
    d = ImageDraw.Draw(img)
    for cx in (62, W - 62):
        d.ellipse((cx - 36, H // 2 - 36, cx + 36, H // 2 + 36), fill=NIGHT + (255,), outline=GOLD + (255,), width=4)
        draw_star(d, cx, H // 2, 22, GOLD, ri=9, n=4)
    img = t2(img, text, (W // 2, H // 2 + 6 - (10 if sub else 0)), 52, "center", 12, SILVER, SKY)
    if sub:
        img = t2(img, sub, (W // 2, H // 2 + 44), 19, "center", 8, GOLD, GOLD)
    return img


# ---------------------------------------------------------------- emotes: a different chibi
def chibi2(expr):
    pen = n2.Pen()
    sm, mir = n2.sm, n2.mir
    # hair behind
    pen.poly(sm([(300, 112), (372, 152), (420, 232), (438, 332), (420, 414), (392, 360), (366, 300), (330, 222)]), HAIRB, LINE, 4)
    pen.line([(372, 170), (404, 250), (410, 340)], (70, 170, 240), 4, smooth=True)
    pen.poly(sm([(150, 130), (96, 200), (76, 300), (90, 392), (132, 422), (142, 322), (150, 230)]), HAIRB, LINE, 4)
    # horns, swept back
    for sgn in (1, -1):
        def P(x, y):
            return (224 + sgn * (x - 224), y)
        for w, col in ((44, LINE), (32, sc.n2.HORN), (10, sc.n2.HORN_L)):
            nw.blade(pen.d, tuple(v * n2.K for v in P(158, 120)), tuple(v * n2.K for v in P(136, 36)), tuple(v * n2.K for v in P(78, 18)), w * n2.K, col + (255,))
    # long ears
    for pts, inn in (([(120, 224), (40, 176), (2, 134), (112, 266)], [(112, 228), (48, 182), (26, 156), (110, 256)]),):
        pen.poly(pts, SKIN, LINE, 4, smooth=True)
        pen.poly(inn, SKIN_D)
        pen.poly(mir(pts), SKIN, LINE, 4, smooth=True)
        pen.poly(mir(inn), SKIN_D)
    # neck and collar
    pen.poly([(196, 316), (252, 316), (254, 380), (194, 380)], SKIN_D, LINE, 3)
    for sg in (1, -1):
        def Q(x, y):
            return (224 + sg * (x - 224), y)
        pen.poly([Q(72, 448), Q(58, 372), Q(108, 336), Q(180, 326), Q(206, 376), Q(224, 448)], BLK, LINE, 4)
        pen.line([Q(112, 340), Q(180, 330), Q(206, 378), Q(224, 446)], (200, 208, 230), 4, smooth=True)
    pen.poly([(224, 380), (238, 398), (224, 420), (210, 398)], (120, 214, 244), LINE, 3)
    # face
    pen.ell(224, 236, 108, 98, SKIN, LINE, 4)
    pen.ell(224, 318, 62, 14, SKIN_D)
    pen.ell(224, 236, 105, 94, SKIN)
    # fringe: white lock on the left, blue on the right
    def fringe():
        pen.poly(sm([(114, 172), (124, 112), (224, 74), (324, 112), (334, 172), (290, 122), (224, 104), (160, 122)]), HAIRB, LINE, 4)
        pen.poly(sm([(224, 108), (160, 116), (118, 172), (104, 262), (124, 338), (146, 262), (166, 196), (208, 150)]), WHITE, LINE, 4)
        pen.line([(150, 124), (118, 190), (112, 270)], (150, 200, 250), 4, smooth=True)
        pen.poly(sm([(224, 108), (290, 120), (338, 172), (346, 252), (334, 322), (312, 248), (286, 190), (242, 150)]), HAIRB, LINE, 4)
        pen.line([(296, 136), (330, 190), (338, 262)], (86, 180, 244), 4, smooth=True)
        pen.poly([(116, 264), (126, 264), (120, 310)], GOLD, LINE, 2)
        pen.poly([(332, 264), (342, 264), (336, 310)], GOLD, LINE, 2)
    fringe()
    L, R, EY = 168, 282, 244

    def shadow_(cx):
        pen.arc(cx, EY - 6, 34, 26, 200, 340, (236, 96, 184), 10)

    def eye(cx, ry=28, pupil=1.0, look=0):
        pen.ell(cx, EY, 32, ry, (255, 255, 255), LINE, 3.5)
        pen.ell(cx + look, EY + 2, 22, ry * 0.86, (36, 84, 200))
        pen.ell(cx + look, EY + 8, 19, ry * 0.5, (130, 190, 255))
        pen.ell(cx + look, EY + 1, 10 * pupil, 13 * pupil, (14, 18, 44))
        pen.ell(cx + look - 8, EY - 8, 6, 6, (255, 255, 255))
        shadow_(cx)
        pen.arc(cx, EY + 1, 34, ry + 2, 196, 344, LINE, 7)

    if expr == "happy":
        for cx in (L, R):
            pen.arc(cx, EY + 8, 30, 28, 200, 340, LINE, 8)
            shadow_(cx)
        n2.mouth_open(pen, 224, 304, 34, 32)
        n2.blush(pen)
    elif expr == "love":
        for cx in (L, R):
            pen.heart(cx, EY, 40, (244, 70, 110))
        pen.arc(224, 296, 26, 20, 20, 160, LINE, 6)
        n2.blush(pen, big=1.2)
        pen.heart(396, 100, 24, (246, 100, 132))
    elif expr == "cry":
        eye(L, 30, 1.2)
        eye(R, 30, 1.2)
        for cx in (L - 8, R + 8):
            pen.poly([(cx - 9, EY + 32), (cx + 9, EY + 32), (cx + 15, 366), (cx - 15, 366)], (140, 210, 255))
            pen.ell(cx, 370, 16, 12, (140, 210, 255))
        pen.line([(196, 314), (210, 303), (238, 303), (252, 314)], LINE, 6, smooth=True)
    elif expr == "rage":
        for cx in (L, R):
            pen.ell(cx, EY + 4, 30, 24, (255, 255, 255), LINE, 3.5)
            pen.ell(cx, EY + 6, 18, 17, (36, 84, 200))
            pen.ell(cx, EY + 6, 9, 11, (14, 18, 44))
        pen.poly([(L - 40, EY - 40), (L + 40, EY - 6), (L + 40, EY - 50), (L - 40, EY - 60)], SKIN)
        pen.poly([(R + 40, EY - 40), (R - 40, EY - 6), (R - 40, EY - 50), (R + 40, EY - 60)], SKIN)
        pen.line([(L - 42, EY - 26), (L + 42, EY - 6)], LINE, 8)
        pen.line([(R + 42, EY - 26), (R - 42, EY - 6)], LINE, 8)
        fringe()  # hair in front of the lid patches and brow lines
        pen.line([(194, 312), (208, 300), (240, 300), (254, 312)], LINE, 6, smooth=True)
        for dx, dy in ((0, 0), (14, 10)):
            pen.line([(352 + dx, 118 + dy), (368 + dx, 102 + dy)], (230, 40, 60), 7)
            pen.line([(352 + dx, 102 + dy), (368 + dx, 118 + dy)], (230, 40, 60), 7)
    elif expr == "smirk":
        for cx in (L, R):
            eye(cx, 28, 1.0, 6)
            pen.poly([(cx - 40, EY - 44), (cx + 40, EY - 44), (cx + 40, EY - 2), (cx - 40, EY - 2)], SKIN)
            pen.line([(cx - 38, EY - 2), (cx + 38, EY - 2)], LINE, 8)
            shadow_(cx)
        pen.line([(186, 306), (224, 312), (270, 292)], LINE, 7, smooth=True)
        pen.poly([(262, 294), (284, 284), (278, 302)], (246, 246, 246), LINE, 3)
    elif expr == "wink":
        eye(L, 28)
        pen.line([(R - 30, EY - 14), (R + 24, EY + 4), (R - 30, EY + 22)], LINE, 8, smooth=True)
        shadow_(R)
        n2.mouth_open(pen, 224, 300, 30, 28)
        pen.poly([(236, 316), (258, 316), (254, 342), (240, 342)], (240, 110, 124), LINE, 3)
        n2.blush(pen)
        pen.text("*", 392, 120, 54, (255, 220, 120))
    elif expr == "sleepy":
        for cx in (L, R):
            pen.arc(cx, EY - 4, 30, 22, 20, 160, LINE, 8)
            shadow_(cx)
        pen.ell(224, 304, 11, 13, (230, 110, 126), LINE, 3.5)
        n2.blush(pen, big=0.9)
        pen.text("Z", 384, 126, 52, (255, 255, 255))
        pen.text("z", 414, 88, 34, (255, 255, 255))
    elif expr == "shock":
        eye(L, 34, 0.55)
        eye(R, 34, 0.55)
        pen.ell(224, 316, 24, 32, (120, 20, 44), LINE, 4)
        pen.ell(224, 330, 14, 12, (240, 110, 124))
        pen.poly([(382, 150), (400, 188), (364, 188)], (140, 210, 255), LINE, 3)
        pen.ell(382, 190, 17, 17, (140, 210, 255), LINE, 3)
    im = nw.outlined(pen.done(), None, 12)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sm_ = im.resize((int(im.width * 0.88), int(im.height * 0.88)), Image.LANCZOS)
    out.alpha_composite(sm_, ((im.width - sm_.width) // 2, int(im.height * 0.07)))
    return out


EXPR2 = ["happy", "love", "cry", "rage", "smirk", "wink", "sleepy", "shock"]


def emote_star(S=448):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S // 2
    draw_star(d, c, c + 8, 190, GOLD, ri=84)
    draw_star(d, c, c + 8, 150, (255, 226, 140), ri=66)
    d.polygon([(c, c - 170), (c + 60, c - 40), (c, c + 8)], fill=(255, 246, 200, 255))
    sparkle(d, c + 150, c - 150, 34, (255, 250, 230))
    sparkle(d, c - 160, c + 140, 22, (255, 250, 230))
    return nw.outlined(img, None, 12)


def emote_moon(S=448):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    m = Image.new("L", (S * 3, S * 3), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((60 * 3, 50 * 3, 390 * 3, 380 * 3), fill=255)
    md.ellipse((140 * 3, 20 * 3, 440 * 3, 330 * 3), fill=0)
    m = m.resize((S, S), Image.LANCZOS)
    lay = Image.new("RGBA", (S, S), GOLD + (255,))
    lay.putalpha(m)
    img = Image.alpha_composite(img, lay)
    d = ImageDraw.Draw(img)
    draw_star(d, 330, 250, 56, (255, 230, 150), ri=24)
    sparkle(d, 380, 110, 26, (255, 250, 230))
    return nw.outlined(img, None, 12)


def emote_heart2(S=448):
    pen = n2.Pen()
    pen.heart(224, 230, 190, (236, 76, 160))
    pen.poly([(130, 140), (190, 120), (160, 170)], (255, 168, 214))
    pen.ell(150, 150, 22, 14, (255, 220, 240))
    d = pen.d
    sparkle(d, 360 * 3, 120 * 3, 44 * 3, (255, 244, 200))
    return nw.outlined(pen.done(), None, 12)


def emote_gg(S=448):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    m = text_mask((S, S), "GG", font(HEADF, 230), (S // 2, S // 2 + 80), track=2)
    big = m.filter(ImageFilter.MaxFilter(25))
    ol = Image.new("RGBA", (S, S), DEEP + (255,))
    ol.putalpha(big)
    img = Image.alpha_composite(img, ol)
    img = fill_mask(img, m, (200, 232, 255), SKY)
    d = ImageDraw.Draw(img)
    sparkle(d, 392, 118, 30, GOLD)
    sparkle(d, 60, 330, 20, GOLD)
    return img


# ---------------------------------------------------------------- badges: stars and moons
def star_badge(tier):
    S = 360
    img = nw.badge_base(S)
    d = ImageDraw.Draw(img)
    cols = [(110, 214, 240), (130, 160, 255), GOLD, (240, 90, 150), SILVER, (255, 214, 120)]
    c = S // 2
    m = Image.new("L", (S * 3, S * 3), 0)
    md = ImageDraw.Draw(m)
    md.ellipse(((c - 130) * 3, (c - 130) * 3, (c + 130) * 3, (c + 130) * 3), fill=255)
    md.ellipse(((c - 98) * 3, (c - 150) * 3, (c + 160) * 3, (c + 108) * 3), fill=0)
    m = m.resize((S, S), Image.LANCZOS)
    cres = Image.new("RGBA", (S, S), GOLD + (255,))
    cres.putalpha(m)
    img = Image.alpha_composite(img, cres)
    d = ImageDraw.Draw(img)
    draw_star(d, c + 16, c + 4, 78 + tier * 3, cols[tier], ri=34 + tier, outline=DEEP, w=5)
    draw_star(d, c + 16, c + 4, 40, (255, 255, 255), ri=17)
    for i in range(tier):
        a = math.radians(-70 + i * 28)
        sparkle(d, c + math.cos(a) * 140, c + math.sin(a) * 140, 12, GOLD)
    return img


def bits_badge2(tier):
    S = 360
    img = nw.badge_base(S)
    d = ImageDraw.Draw(img)
    cols = [(150, 150, 176), (110, 214, 240), (130, 160, 255), (240, 90, 150)]
    c = S // 2
    n = 4
    sparkle(d, c, c, 120 + tier * 14, cols[tier])
    d.ellipse((c - 26, c - 26, c + 26, c + 26), fill=(255, 255, 255, 255), outline=DEEP + (255,), width=5)
    return img


def main():
    art = Image.open(sc.ART).convert("RGBA")
    for sub in ("Emotes", "Badges", "Screens", "Overlay", "Alerts", "Panels", "ChannelPoints"):
        p = OUT / sub
        if p.exists():
            shutil.rmtree(p)
    for t, s in nw.PANELS:
        sub = {"DONATE": "support the stars", "DISCORD": "join the constellation", "SCHEDULE": "when the stars rise"}.get(t, s)
        save(panel2(t, sub), "Panels", t.lower() + ".png")
    for kind, big, small, note, fn in (("start", "STARTING SOON", "THE STARS ARE ALIGNING", "grab a drink and settle in", "starting_soon"),
                                       ("brb", "BE RIGHT BACK", "LOST IN THE NEBULA", "back in a moment", "brb"),
                                       ("end", "THANKS FOR WATCHING", "SEE YOU AMONG THE STARS", "follow so you never miss a stream", "ending"),
                                       ("off", "OFFLINE", "NOT STREAMING RIGHT NOW", "see you at the next stream", "offline")):
        save(screen2(art, kind, big, small, note).convert("RGB"), "Screens", fn + ".png")
    save(overlay2(), "Overlay", "stream_overlay.png")
    for head, sub, fn, ring in ALERTS:
        save(alert2(art, head, sub, ring), "Alerts", fn + ".png")
    for i, m in enumerate((1, 3, 6, 12, 24, 36)):
        b = star_badge(i)
        for s in (72, 36, 18):
            save(b.resize((s, s), Image.LANCZOS), "Badges", "Subscriber", "%dmonth_%d.png" % (m, s))
    for i, n in enumerate((1, 100, 1000, 10000)):
        b = bits_badge2(i)
        for s in (72, 36, 18):
            save(b.resize((s, s), Image.LANCZOS), "Badges", "Bits", "bits%d_%d.png" % (n, s))
    emos = {n: chibi2(n) for n in EXPR2}
    emos.update(star=emote_star(), moon=emote_moon(), heart=emote_heart2(), gg=emote_gg())
    for n, im in emos.items():
        save(im, "Emotes", "sc_%s_448.png" % n)
        for s in (112, 56, 28):
            save(im.resize((s, s), Image.LANCZOS), "Emotes", "sc_%s_%d.png" % (n, s))
    for n in ("happy", "love", "smirk"):
        save(emos[n].resize((112, 112), Image.LANCZOS), "ChannelPoints", n + ".png")
    print("done")


if __name__ == "__main__":
    main()

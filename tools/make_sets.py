#!/usr/bin/env python3
"""
Gives every style its own character and its own frames, so nothing is shared between sets:
  - a mascot with its own body (hood, helmet, slash ball, snake, flower, football, shield, perfume bottle, triangle)
    wearing the same 22 expressions -> all emotes (animated ones loop),
  - sub badges, flair and channel point icons built around that mascot,
  - its own frame design for overlay, alert, animated corner and panels,
  - its own starting soon / be right back / offline screens (for the sets that did not have unique ones yet).

    python tools/make_sets.py Tessel        # one set
    python tools/make_sets.py               # all
"""
import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_rose as mr

TW = ROOT / "images" / "twitch"
W3 = (255, 255, 255)

SETS = {
    "Hood": dict(shape="circle", pshape=None, main=(112, 6, 8), dark=(58, 2, 4), accent=(250, 238, 228), accent2=(150, 14, 20), fill=(252, 250, 248), text=(120, 4, 6), text2=(80, 0, 2),
                 font="OLDENGL.TTF", frame=None, mascot="hood", anim="shine", screens=False, blush=(236, 130, 130), ink=(58, 2, 4)),
    "Helmet": dict(shape="shield", pshape='chamfer', main=(236, 190, 74), dark=(28, 16, 56), accent=(255, 232, 150), accent2=(140, 40, 70), fill=(40, 22, 70), text=(255, 240, 200), text2=(236, 196, 100),
                   font="georgiab.ttf", frame="gold", mascot="helmet", anim="shine", screens=False, blush=(230, 130, 120), ink=(36, 18, 60)),
    "Slash": dict(shape="octagon", pshape='slant', main=(255, 150, 60), dark=(30, 0, 10), accent=(255, 255, 255), accent2=(210, 18, 64), fill=(130, 8, 36), text=(255, 255, 255), text2=(255, 214, 170),
                  font="impact.ttf", frame="slash", mascot="slash", anim="runner", screens=False, blush=(255, 120, 110), ink=(30, 0, 10)),
    "Snake": dict(shape="scallop", pshape='pill', main=(40, 130, 210), dark=(8, 40, 90), accent=(250, 206, 72), accent2=(60, 200, 180), fill=(96, 206, 236), text=(10, 44, 100), text2=(6, 28, 70),
                  font="OLDENGL.TTF", frame="scales", mascot="snake", anim="pulse", screens=False, blush=(250, 170, 120), ink=(8, 36, 80)),
    "Floral": dict(shape="flower", pshape='cartouche', main=(176, 110, 214), dark=(30, 28, 72), accent=(246, 208, 104), accent2=(214, 140, 112), fill=(52, 44, 100), text=(252, 250, 255), text2=(226, 214, 244),
                   font="OLDENGL.TTF", frame="petals", mascot="flower", anim="pulse", screens=True, blush=(240, 130, 170), ink=(60, 20, 90)),
    "Tessel": dict(shape="hex", pshape='notch', main=(31, 163, 74), dark=(10, 40, 30), accent=(223, 255, 61), accent2=(14, 59, 46), fill=(16, 64, 46), text=(250, 252, 250), text2=(206, 214, 208),
                   font="constan.ttf", frame="pitch", mascot="football", anim="runner", screens=True, blush=(240, 150, 140), ink=(10, 40, 30)),
    "Perfum": dict(shape="oval", pshape='oval', main=(234, 170, 160), dark=(84, 28, 52), accent=(226, 190, 120), accent2=(130, 70, 100), fill=(247, 238, 222), text=(96, 34, 60), text2=(70, 22, 44),
                   font="constan.ttf", frame="petalgold", mascot="bottle", anim="shine", screens=True, blush=(240, 140, 150), ink=(84, 28, 52)),
    "Northbeam": dict(shape="triangle", pshape='arrow', main=(88, 100, 214), dark=(14, 24, 52), accent=(125, 235, 240), accent2=(40, 60, 140), fill=(24, 40, 96), text=(240, 248, 252), text2=(190, 214, 240),
                      font="OLDENGL.TTF", frame="triangle", mascot="triangle", anim="runner", screens=True, blush=(150, 190, 240), ink=(14, 24, 70)),
    "Strikeline": dict(shape="rsquare", pshape='stripebar', main=(0, 168, 232), dark=(16, 24, 32), accent=(232, 232, 232), accent2=(31, 58, 95), fill=(31, 58, 95), text=(250, 252, 255), text2=(200, 214, 228),
                       font="impact.ttf", frame="stripes", mascot="shield", anim="runner", screens=True, blush=(120, 190, 230), ink=(16, 24, 32)),
}


def ell_poly(cx, cy, rx, ry, ang, n=28):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + math.cos(2 * math.pi * i / n) * rx * ca - math.sin(2 * math.pi * i / n) * ry * sa,
             cy + math.cos(2 * math.pi * i / n) * rx * sa + math.sin(2 * math.pi * i / n) * ry * ca) for i in range(n)]


# ---------------------------------------------------------------------------------------------- mascots


# ------------------------------------------------------------------------- portraits cut from the user's own art
ART = ROOT / "images"
DL = Path("C:/Users/SaphiresSilver/Downloads/art")
_PORTRAIT_CACHE = {}


def _crop_circle(img, cx, cy, r, px=480):
    box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    im = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    src = img.crop(box)
    im.paste(src, (0, 0))
    return im.resize((px, px), Image.LANCZOS)


def portrait(kind, C):
    """Returns an RGBA square (the face zone is centred, as make_rose draws faces around its centre)."""
    if kind in _PORTRAIT_CACHE:
        return _PORTRAIT_CACHE[kind]
    px = 480
    if kind == "hood":
        im = _crop_circle(Image.open(ART / "LogoGaming.png").convert("RGBA"), 1507, 1023, 380, px)
        patch = None
    elif kind == "helmet":
        im = _crop_circle(Image.open(ART / "Gamerstreamer.png").convert("RGBA"), 1524, 435, 362, px)
        patch = None
    elif kind == "snake":
        im = _crop_circle(Image.open(ART / "Banner snake.png").convert("RGBA"), 1160, 480, 300, px)
        patch = ((250, 232, 150), 0.88, 0.0, 0.05, 0.8, 0.62)
    elif kind == "flower":
        src = Image.open(DL / "priekstwitterfiver" / "2x" / "1x" / "I will be right back.png").convert("RGBA")
        im = _crop_circle(src, 235, 330, 200, px)
        patch = ((252, 244, 255), 0.82, 0.0, 0.05, 0.74, 0.58)
    elif kind == "triangle":
        import nb_extract
        cut = nb_extract.cutout().crop((300, 240, 2700, 2150))
        base = Image.new("RGBA", (px, px), C["dark"] + (255,))
        e = cut.resize((int(px * 1.5), int(px * 1.5 * cut.height / cut.width)), Image.LANCZOS)
        base.alpha_composite(e, ((px - e.width) // 2, int(px * 0.5 - e.height * 0.58)))
        im = base
        patch = ((228, 244, 250), 0.9, 0.0, 0.22, 0.7, 0.55)
    elif kind == "shield":
        import fb_extract
        cut = fb_extract.cutout()
        base = Image.new("RGBA", (px, px), C["dark"] + (255,))
        part = cut.crop((320 - 120, 110 - 120, 320 + 120, 110 + 120)).resize((px, px), Image.LANCZOS)
        for k in range(4):
            ImageDraw.Draw(base).rectangle((0, int(px * (0.1 + k * 0.08)), int(px * 0.16), int(px * (0.15 + k * 0.08))), fill=C["main"] + (255,))
            ImageDraw.Draw(base).rectangle((int(px * 0.84), int(px * (0.1 + k * 0.08)), px, int(px * (0.15 + k * 0.08))), fill=C["main"] + (255,))
        base.alpha_composite(part)
        im = base
        patch = None
    elif kind == "bottle":
        src = Image.open(DL / "assets" / "Bottle.png").convert("RGBA")
        im = _crop_circle(src, 2290, 3226, 700, px)
        patch = ((255, 236, 236), 0.55, 0.0, 0.0, 0.8, 0.66)
    elif kind == "football":
        src = Image.open(DL / "assets" / "Footballboot.png").convert("RGBA")
        src = src.crop(src.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
        base = radial((px, px), (30, 110, 70), (10, 44, 32), cx=0.5, cy=0.5, spread=0.9).convert("RGBA")
        k = px * 0.84 / max(src.size)
        boot = src.resize((max(1, round(src.width * k)), max(1, round(src.height * k))), Image.LANCZOS)
        base.alpha_composite(boot, ((px - boot.width) // 2, (px - boot.height) // 2))
        im = base
        patch = None
    else:
        im = None
        patch = None
    _PORTRAIT_CACHE[kind] = (im, patch)
    return im, patch


def make_body(kind, C):
    ink = C["ink"] + (255,)

    def circle(d, S, cx, cy, r, fill, wd=0.095):
        d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=fill + (255,), outline=ink, width=int(r * wd * S))

    def face_disc(d, S, cx, cy, r, fill=(250, 232, 214)):
        d.ellipse(((cx - r * 0.82) * S, (cy - r * 0.62) * S, (cx + r * 0.82) * S, (cy + r * 0.74) * S), fill=fill + (255,))

    def body(d, S, cx, cy, r, tint):
        dark = tint in ((150, 22, 38), (170, 40, 58))
        if kind in ("hood", "helmet", "snake", "flower", "triangle", "shield", "bottle", "football"):
            im, patch = portrait(kind, C)
            n = int(2 * r * S)
            pic = im.resize((n, n), Image.LANCZOS)
            m = Image.new("L", (n, n), 0)
            ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
            if dark:
                pic = Image.blend(pic.convert("RGB"), Image.new("RGB", pic.size, (60, 0, 0)), 0.35).convert("RGBA")
            pic.putalpha(ImageChops.multiply(pic.split()[3], m))
            d._image.alpha_composite(pic, (int((cx - r) * S), int((cy - r) * S)))
            if patch:
                col, al, ox, oy, rx, ry = patch
                lay = Image.new("RGBA", pic.size, (0, 0, 0, 0))
                ImageDraw.Draw(lay).ellipse((n * (0.5 + ox - rx / 2), n * (0.5 + oy - ry / 2), n * (0.5 + ox + rx / 2), n * (0.5 + oy + ry / 2)), fill=col + (int(255 * al),))
                lay.putalpha(ImageChops.multiply(lay.split()[3], m))
                d._image.alpha_composite(lay, (int((cx - r) * S), int((cy - r) * S)))
            d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), outline=ink, width=int(r * 0.07 * S))
            return
        if kind == "hood":
            m = tuple(int(c * (0.7 if dark else 1)) for c in C["main"])
            d.polygon([((cx - r * 0.95) * S, (cy + r * 0.2) * S), (cx * S, (cy - r * 1.25) * S), ((cx + r * 0.95) * S, (cy + r * 0.2) * S)], fill=m + (255,), outline=ink, width=int(r * 0.09 * S))
            circle(d, S, cx, cy + r * 0.05, r * 0.98, m)
            face_disc(d, S, cx, cy, r)
        elif kind == "helmet":
            circle(d, S, cx, cy, r, C["main"])
            d.polygon([((cx - r * 0.12) * S, (cy - r * 0.98) * S), ((cx + r * 0.12) * S, (cy - r * 0.98) * S), ((cx + r * 0.22) * S, (cy - r * 1.3) * S), ((cx - r * 0.22) * S, (cy - r * 1.3) * S)], fill=C["accent2"] + (255,), outline=ink, width=int(r * 0.06 * S))
            d.rounded_rectangle(((cx - r * 0.86) * S, (cy - r * 0.62) * S, (cx + r * 0.86) * S, (cy + r * 0.62) * S), radius=int(r * 0.3 * S), fill=(250, 232, 214, 255), outline=ink, width=int(r * 0.07 * S))
            d.line([(cx * S, (cy - r * 0.98) * S), (cx * S, (cy - r * 0.64) * S)], fill=ink, width=int(r * 0.07 * S))
        elif kind == "slash":
            circle(d, S, cx, cy, r, C["main"])
            for off, col in ((-0.7, (255, 255, 255)), (-0.2, (30, 0, 10)), (0.5, (255, 255, 255))):
                pts = [(cx + off * r - 0.25 * r, cy - r), (cx + off * r + 0.15 * r, cy - r), (cx + off * r - 0.45 * r, cy + r), (cx + off * r - 0.85 * r, cy + r)]
                lay = Image.new("L", (int(2 * r * S) + 4, int(2 * r * S) + 4), 0)
                ImageDraw.Draw(lay).polygon([((x - cx + r) * S, (y - cy + r) * S) for x, y in pts], fill=255)
                msk = Image.new("L", lay.size, 0)
                ImageDraw.Draw(msk).ellipse((int(r * 0.05 * S), int(r * 0.05 * S), int(r * 1.95 * S), int(r * 1.95 * S)), fill=255)
                a = ImageChops.multiply(lay, msk)
                col_img = Image.new("RGBA", lay.size, col + (255,))
                col_img.putalpha(a)
                d._image.alpha_composite(col_img, (int((cx - r) * S), int((cy - r) * S)))
            d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), outline=ink, width=int(r * 0.095 * S))
            if not C.get("_noface"):
                face_disc(d, S, cx, cy, r, (252, 240, 226))
        elif kind == "snake":
            circle(d, S, cx, cy, r, tuple(int(c * (0.75 if dark else 1)) for c in C["main"]))
            for i in range(-3, 4):
                for j in range(-3, 4):
                    px, py = cx + i * r * 0.3 + (r * 0.15 if j % 2 else 0), cy + j * r * 0.28
                    if (px - cx) ** 2 + (py - cy) ** 2 < (r * 0.86) ** 2 and abs(px - cx) > r * 0.46:
                        d.arc(((px - r * 0.12) * S, (py - r * 0.12) * S, (px + r * 0.12) * S, (py + r * 0.12) * S), 180, 360, fill=(120, 190, 240, 255), width=max(1, int(r * 0.03 * S)))
            d.ellipse(((cx - r * 0.7) * S, (cy - r * 0.45) * S, (cx + r * 0.7) * S, (cy + r * 0.85) * S), fill=C["accent"] + (255,))
            d.polygon([((cx - r * 0.12) * S, (cy - r * 0.98) * S), (cx * S, (cy - r * 1.18) * S), ((cx + r * 0.12) * S, (cy - r * 0.98) * S)], fill=C["accent2"] + (255,))
        elif kind == "flower":
            for i in range(10):
                a = 2 * math.pi * i / 10
                col = (252, 250, 255) if i % 2 == 0 else (240, 200, 240)
                pts = ell_poly(cx + math.cos(a) * r * 0.72, cy + math.sin(a) * r * 0.72, r * 0.44, r * 0.2, a)
                d.polygon([(x * S, y * S) for x, y in pts], fill=col + (255,), outline=ink, width=int(r * 0.05 * S))
            circle(d, S, cx, cy, r * 0.72, C["accent"], 0.07)
        elif kind == "football":
            circle(d, S, cx, cy, r, (248, 248, 248))
            for i in range(5):
                a = -math.pi / 2 + 2 * math.pi * i / 5 + 0.3
                px, py = cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82
                pts = [(px + math.cos(a + math.pi + 2 * math.pi * k / 5) * r * 0.26, py + math.sin(a + math.pi + 2 * math.pi * k / 5) * r * 0.26) for k in range(5)]
                d.polygon([(x * S, y * S) for x, y in pts], fill=C["main"] + (255,), outline=ink, width=int(r * 0.03 * S))
            d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), outline=ink, width=int(r * 0.095 * S))
        elif kind == "bottle":
            d.rounded_rectangle(((cx - r * 0.2) * S, (cy - r * 1.2) * S, (cx + r * 0.2) * S, (cy - r * 0.8) * S), radius=int(r * 0.05 * S), fill=C["accent"] + (255,), outline=ink, width=int(r * 0.06 * S))
            circle(d, S, cx, cy - r * 1.28, r * 0.24, C["accent"], 0.07)
            circle(d, S, cx, cy + r * 0.05, r, tuple(int(c * (0.85 if dark else 1)) for c in C["main"]))
            d.arc(((cx - r * 0.8) * S, (cy - r * 0.75) * S, (cx + r * 0.8) * S, (cy + r * 0.85) * S), 212, 262, fill=(255, 235, 235, 255), width=int(r * 0.07 * S))
            face_disc(d, S, cx, cy, r * 0.9, (252, 226, 222))
        elif kind == "triangle":
            pts = [(cx, cy - r * 1.15), (cx + r * 1.1, cy + r * 0.85), (cx - r * 1.1, cy + r * 0.85)]
            d.polygon([(x * S, y * S) for x, y in pts], fill=tuple(int(c * (0.8 if dark else 1)) for c in C["main"]) + (255,), outline=ink, width=int(r * 0.095 * S), )
            d.polygon([(x * S, y * S) for x, y in [(cx, cy - r * 1.15), (cx + r * 0.55, cy - r * 0.15), (cx - r * 0.55, cy - r * 0.15)]], fill=C["accent"] + (255,))
            d.ellipse(((cx - r * 0.74) * S, (cy - r * 0.5) * S, (cx + r * 0.74) * S, (cy + r * 0.72) * S), fill=(228, 244, 250, 255))
        elif kind == "shield":
            pts = [(cx - r * 0.95, cy - r * 0.95), (cx + r * 0.95, cy - r * 0.95), (cx + r * 0.95, cy + r * 0.1)] + \
                  [(cx + r * 0.95 * math.cos(math.pi * t / 14), cy + r * 0.1 + r * 0.95 * math.sin(math.pi * t / 14)) for t in range(1, 14)] + [(cx - r * 0.95, cy + r * 0.1)]
            d.polygon([(x * S, y * S) for x, y in pts], fill=C["accent2"] + (255,), outline=ink, width=int(r * 0.095 * S))
            for k in range(3):
                y0 = cy - r * 0.6 + k * r * 0.3
                d.rectangle(((cx - r * 0.9) * S, y0 * S, (cx - r * 0.55) * S, (y0 + r * 0.1) * S), fill=C["main"] + (255,))
                d.rectangle(((cx + r * 0.55) * S, y0 * S, (cx + r * 0.9) * S, (y0 + r * 0.1) * S), fill=C["main"] + (255,))
            d.ellipse(((cx - r * 0.64) * S, (cy - r * 0.55) * S, (cx + r * 0.64) * S, (cy + r * 0.75) * S), fill=(228, 232, 236, 255))
    return body


def apply_set(C):
    mr.INK, mr.RED, mr.RED_D, mr.RED_L, mr.BLUSH = C["ink"], C["main"], tuple(int(c * 0.6) for c in C["main"]), tuple(min(255, int(c * 1.25 + 30)) for c in C["main"]), C["blush"]
    mr.GOLD = C["accent"]
    mr.berry_body = make_body(C["mascot"], C)


# ----------------------------------------------------------------------------------------------- frames

def border(size, style, C, sc=1.0):
    w, h = size
    S = 2
    L = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    a, a2, m, dk = C["accent"], C["accent2"], C["main"], C["dark"]

    def R(inset, wd, col, r=0):
        d.rounded_rectangle((inset * S, inset * S, (w - inset) * S, (h - inset) * S), radius=int(r * S), outline=col + (255,), width=max(1, int(wd * S)))

    def corners(fn):
        for sx, sy, ox, oy in ((1, 1, 0, 0), (-1, 1, w, 0), (1, -1, 0, h), (-1, -1, w, h)):
            fn(sx, sy, ox, oy)

    if style == "gold":
        R(6 * sc, 6 * sc, a, 10 * sc); R(24 * sc, 3 * sc, m, 4 * sc)
        def f(sx, sy, ox, oy):
            L2 = 90 * sc
            d.line([(ox + sx * 14 * sc) * S, (oy + sy * 14 * sc + sy * L2) * S, (ox + sx * 14 * sc) * S, (oy + sy * 14 * sc) * S] if False else [((ox + sx * 14 * sc) * S, (oy + sy * (14 * sc + L2)) * S), ((ox + sx * 14 * sc) * S, (oy + sy * 14 * sc) * S), ((ox + sx * (14 * sc + L2)) * S, (oy + sy * 14 * sc) * S)], fill=a + (255,), width=int(8 * sc * S), joint="curve")
        corners(f)
        for x, y in ((w / 2, 6 * sc), (w / 2, h - 6 * sc), (6 * sc, h / 2), (w - 6 * sc, h / 2)):
            d.polygon([((x - 12 * sc) * S, y * S), (x * S, (y - 12 * sc) * S), ((x + 12 * sc) * S, y * S), (x * S, (y + 12 * sc) * S)], fill=a + (255,), outline=dk + (255,))
    elif style == "slash":
        R(0, 30 * sc, dk); R(26 * sc, 12 * sc, W3, 0); R(40 * sc, 6 * sc, a2, 0)
        def f(sx, sy, ox, oy):
            for k, (wd, col) in enumerate(((46, m), (20, W3), (30, dk))):
                o = 60 * sc + k * 70 * sc
                pts = [(ox + sx * 0, oy + sy * o), (ox + sx * wd * sc, oy + sy * o), (ox + sx * (o + wd * sc), oy + sy * 0), (ox + sx * o, oy + sy * 0)]
                d.polygon([(x * S, y * S) for x, y in pts], fill=col + (255,))
        corners(f)
    elif style == "scales":
        sp = int(46 * sc)
        for x in range(0, w, sp):
            col = a if (x // sp) % 2 == 0 else m
            d.arc((x * S, (-sp // 2 + 8 * sc) * S, (x + sp) * S, (sp // 2 + 8 * sc) * S), 0, 180, fill=col + (255,), width=int(7 * sc * S))
            d.arc((x * S, (h - sp // 2 - 8 * sc) * S, (x + sp) * S, (h + sp // 2 - 8 * sc) * S), 180, 360, fill=col + (255,), width=int(7 * sc * S))
        for y in range(0, h, sp):
            col = a if (y // sp) % 2 == 0 else m
            d.arc(((-sp // 2 + 8 * sc) * S, y * S, (sp // 2 + 8 * sc) * S, (y + sp) * S), 270, 450, fill=col + (255,), width=int(7 * sc * S))
            d.arc(((w - sp // 2 - 8 * sc) * S, y * S, (w + sp // 2 - 8 * sc) * S, (y + sp) * S), 90, 270, fill=col + (255,), width=int(7 * sc * S))
        R(20 * sc, 4 * sc, dk, 10 * sc); R(30 * sc, 2 * sc, a2, 8 * sc)
    elif style == "petals":
        R(10 * sc, 4 * sc, a, 14 * sc); R(24 * sc, 2 * sc, a2, 8 * sc)
        def f(sx, sy, ox, oy):
            cx, cy = ox + sx * 44 * sc, oy + sy * 44 * sc
            for k in range(8):
                ang = 2 * math.pi * k / 8
                pts = ell_poly(cx + math.cos(ang) * 22 * sc, cy + math.sin(ang) * 22 * sc, 22 * sc, 10 * sc, ang)
                d.polygon([(x * S, y * S) for x, y in pts], fill=(m if k % 2 else (240, 200, 240)) + (255,), outline=dk + (255,))
            d.ellipse(((cx - 14 * sc) * S, (cy - 14 * sc) * S, (cx + 14 * sc) * S, (cy + 14 * sc) * S), fill=a + (255,), outline=dk + (255,))
        corners(f)
        for x in range(int(110 * sc), int(w - 90 * sc), int(40 * sc)):
            for y in (14 * sc, h - 14 * sc):
                d.ellipse(((x - 4 * sc) * S, (y - 4 * sc) * S, (x + 4 * sc) * S, (y + 4 * sc) * S), fill=a + (255,))
    elif style == "pitch":
        R(8 * sc, 5 * sc, a, 0); R(22 * sc, 2 * sc, m, 0)
        def f(sx, sy, ox, oy):
            L2 = 110 * sc
            d.line([((ox + sx * 8 * sc) * S, (oy + sy * (8 * sc + L2)) * S), ((ox + sx * 8 * sc) * S, (oy + sy * 8 * sc) * S), ((ox + sx * (8 * sc + L2)) * S, (oy + sy * 8 * sc) * S)], fill=a + (255,), width=int(14 * sc * S), joint="curve")
        corners(f)
        for y, s0 in ((8 * sc, 0), (h - 8 * sc, 180)):
            d.arc(((w / 2 - 46 * sc) * S, (y - 46 * sc) * S, (w / 2 + 46 * sc) * S, (y + 46 * sc) * S), 0 if s0 == 0 else 180, 180 if s0 == 0 else 360, fill=a + (255,), width=int(5 * sc * S))
    elif style == "petalgold":
        R(10 * sc, 3 * sc, a, 26 * sc); R(20 * sc, 1.5 * sc, a2, 20 * sc)
        def f(sx, sy, ox, oy):
            for k, (dx, dy, rot) in enumerate(((46, 30, 0.3), (30, 50, 1.2), (62, 56, 0.8))):
                pts = ell_poly(ox + sx * dx * sc, oy + sy * dy * sc, 24 * sc, 11 * sc, rot * sx * sy)
                d.polygon([(x * S, y * S) for x, y in pts], fill=(m if k != 1 else (244, 200, 190)) + (255,), outline=a2 + (255,))
        corners(f)
        for x, y in ((w / 2, 10 * sc), (w / 2, h - 10 * sc)):
            d.polygon([((x - 12 * sc) * S, y * S), (x * S, (y - 12 * sc) * S), ((x + 12 * sc) * S, y * S), (x * S, (y + 12 * sc) * S)], fill=a + (255,))
    elif style == "triangle":
        R(8 * sc, 4 * sc, a, 0); R(30 * sc, 2 * sc, m, 0)
        tw = int(34 * sc)
        for i, x in enumerate(range(int(40 * sc), int(w - 40 * sc), tw)):
            up = i % 2 == 0
            for yb, flip in ((14 * sc, 1), (h - 14 * sc, -1)):
                if up:
                    pts = [(x, yb + flip * 12 * sc), (x + tw / 2, yb - flip * 12 * sc), (x + tw, yb + flip * 12 * sc)]
                    d.polygon([(px * S, py * S) for px, py in pts], fill=(a if i % 4 == 0 else m) + (255,))
        def f(sx, sy, ox, oy):
            d.polygon([((ox + sx * 8 * sc) * S, (oy + sy * 8 * sc) * S), ((ox + sx * 90 * sc) * S, (oy + sy * 8 * sc) * S), ((ox + sx * 8 * sc) * S, (oy + sy * 90 * sc) * S)], fill=a + (255,))
        corners(f)
    elif style == "stripes":
        R(8 * sc, 3 * sc, a, 0)
        pattern = [(0.00, 0.03), (0.07, 0.05), (0.17, 0.03), (0.25, 0.09), (0.38, 0.04), (0.47, 0.09), (0.6, 0.03), (0.68, 0.05), (0.78, 0.03), (0.86, 0.04)]
        for y, t in pattern:
            y0 = h * 0.2 + y * h * 0.6
            d.rectangle((0, y0 * S, w * 0.1 * S, (y0 + t * h * 0.6) * S), fill=m + (255,))
            d.rectangle((w * 0.9 * S, y0 * S, w * S, (y0 + t * h * 0.6) * S), fill=m + (255,))
    return L.resize((w, h), Image.LANCZOS)


def panel_base(size, C, sc=1.0):
    w, h = size
    img = Image.new("RGBA", (w, h), C["dark"] + (255,))
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((8, 8, w * 2 - 8, h * 2 - 8), radius=int(34 * sc * 2), fill=255)
    img.paste(Image.new("RGBA", (w, h), C["fill"] + (255,)), (0, 0), m.resize((w, h), Image.LANCZOS))
    return Image.alpha_composite(img, border(size, C["frame"], C, sc))


def title_text(img, text, center, size, C, fontname=None, track=0):
    f = font(fontname or C["font"], size)
    m = text_mask(img.size, text, f, center, track=track)
    return fill_mask(img, m, C["text"], C["text2"])


def fit_size(text, fontname, target_w, start, track=0):
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    size = start
    while size > 16 and spaced_width(probe, text, font(fontname, size), track) / SS > target_w:
        size -= 2
    return size


PANELS = [("about_me", "About me"), ("schedule", "Schedule"), ("chat_rules", "Chat rules"), ("donation", "Donation"), ("faq", "FAQ"), ("pc_setup", "PC setup"), ("links", "Links"), ("socials", "Socials")]


def mascot_icon(C, mood, size):
    apply_set(C)
    return mr.emote(mood, "", size)



def shape_pts(kind, cx, cy, r, n=96):
    if kind == "oval":
        return [(cx + math.cos(2 * math.pi * i / n) * r * 0.86, cy + math.sin(2 * math.pi * i / n) * r) for i in range(n)]
    if kind in ("scallop", "flower"):
        lobes, amp = (7, 0.06) if kind == "scallop" else (4, 0.14)
        pts = []
        for i in range(n * 2):
            a = 2 * math.pi * i / (n * 2)
            rr = r * ((1 - amp) + amp * abs(math.cos(a * lobes)))
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        return pts
    if kind == "hex":
        return [(cx + math.cos(math.radians(-90 + 60 * i)) * r, cy + math.sin(math.radians(-90 + 60 * i)) * r) for i in range(6)]
    if kind == "octagon":
        return [(cx + math.cos(math.radians(22.5 + 45 * i)) * r * 1.04, cy + math.sin(math.radians(22.5 + 45 * i)) * r * 1.04) for i in range(8)]
    if kind == "triangle":
        return [(cx, cy - r * 1.02), (cx + r * 1.0, cy + r * 0.8), (cx - r * 1.0, cy + r * 0.8)]
    if kind == "rsquare":
        k = r * 0.7
        pts = []
        for (px, py, a0) in ((cx + k, cy - k, -90), (cx + k, cy + k, 0), (cx - k, cy + k, 90), (cx - k, cy - k, 180)):
            for t in range(0, 91, 10):
                pts.append((px + math.cos(math.radians(a0 + t)) * r * 0.3, py + math.sin(math.radians(a0 + t)) * r * 0.3))
        return pts
    if kind == "shield":
        pts = [(cx - r * 0.86, cy - r * 0.9), (cx + r * 0.86, cy - r * 0.9), (cx + r * 0.86, cy + r * 0.1)]
        for t in range(1, 21):
            a = math.pi / 2 * t / 20
            pts.append((cx + r * 0.86 * math.cos(a), cy + r * 0.1 + r * 0.9 * math.sin(a)))
        for t in range(20, 0, -1):
            a = math.pi / 2 * t / 20
            pts.append((cx - r * 0.86 * math.cos(a), cy + r * 0.1 + r * 0.9 * math.sin(a)))
        return pts
    return [(cx + math.cos(2 * math.pi * i / n) * r, cy + math.sin(2 * math.pi * i / n) * r) for i in range(n)]


def panel_poly(kind, w, h, m):
    if kind == "chamfer":
        c = 70
        return [(m + c, m), (w - m - c, m), (w - m, m + c), (w - m, h - m - c), (w - m - c, h - m), (m + c, h - m), (m, h - m - c), (m, m + c)]
    if kind == "slant":
        return [(m + 70, m), (w - m, m), (w - m - 70, h - m), (m, h - m)]
    if kind == "slantL":
        return [(m, m), (w - m - 70, m), (w - m, h - m), (m + 70, h - m)]
    if kind == "arrow":
        return [(m + 70, m), (w - m - 70, m), (w - m, h / 2), (w - m - 70, h - m), (m + 70, h - m), (m, h / 2)]
    if kind == "pill":
        r = (h - 2 * m) / 2
        pts = [(w - m - r + math.sin(math.radians(t)) * r, h / 2 - math.cos(math.radians(t)) * r) for t in range(0, 181, 6)]
        pts += [(m + r - math.sin(math.radians(t)) * r, h / 2 + math.cos(math.radians(t)) * r) for t in range(0, 181, 6)]
        return pts
    if kind == "notch":
        r = min(56, h // 6)
        pts = [(m, m), (w - m, m), (w - m, h / 2 - r)]
        pts += [(w - m - math.sin(math.radians(t)) * r, h / 2 - r * math.cos(math.radians(t))) for t in range(0, 181, 10)]
        pts += [(w - m, h - m), (m, h - m), (m, h / 2 + r)]
        pts += [(m + math.sin(math.radians(t)) * r, h / 2 + r * math.cos(math.radians(t))) for t in range(0, 181, 10)]
        return pts
    if kind == "oval":
        return [(w / 2 + math.cos(2 * math.pi * i / 90) * (w / 2 - m), h / 2 + math.sin(2 * math.pi * i / 90) * (h / 2 - m)) for i in range(90)]
    if kind == "cartouche":
        r = 60
        pts = []
        for (cx_, cy_, a0) in ((m, m, 0), (w - m, m, 90), (w - m, h - m, 180), (m, h - m, 270)):
            for t in range(0, 91, 10):
                a = math.radians(a0 + t)
                pts.append((cx_ + math.cos(a) * r, cy_ + math.sin(a) * r))
        return pts
    return [(m, m), (w - m, m), (w - m, h - m), (m, h - m)]


def shaped_panel(C, size):
    w, h = size
    S = 2

    def mask(poly):
        im = Image.new("L", (w * S, h * S), 0)
        ImageDraw.Draw(im).polygon([(x * S, y * S) for x, y in poly], fill=255)
        return im.resize((w, h), Image.LANCZOS)
    outer = mask(panel_poly(C["pshape"], w, h, 10))
    p = C["pshape"]
    bands = ((outer, C["dark"]), (outer.filter(ImageFilter.MinFilter(15)), C["accent"]),
             (outer.filter(ImageFilter.MinFilter(21)), C["main"] if p in ("slant", "slantL") else C["accent2"]), (outer.filter(ImageFilter.MinFilter(29)), C["fill"]))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for m_, col in bands:
        lay = Image.new("RGBA", (w, h), col + (255,))
        lay.putalpha(m_)
        img = Image.alpha_composite(img, lay)
    orn = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(orn)
    sc = h / 400.0
    if p in ("slant", "slantL"):
        for k in range(3):
            x = (60 + k * 26) * sc if p == "slant" else w - (130 + k * 26) * sc
            if p == "slant":
                poly = [(x, 38 * sc), (x + 12 * sc, 38 * sc), (x - 22 * sc, h - 38 * sc), (x - 34 * sc, h - 38 * sc)]
            else:
                poly = [(x, 38 * sc), (x + 12 * sc, 38 * sc), (x + 46 * sc, h - 38 * sc), (x + 34 * sc, h - 38 * sc)]
            od.polygon(poly, fill=(C["main"] if k != 1 else C["accent"]) + (255,))
    elif p == "chamfer":
        for sx in (80 * sc, w - 80 * sc):
            for sy in (50 * sc, h - 50 * sc):
                od.polygon([(sx - 12 * sc, sy), (sx, sy - 12 * sc), (sx + 12 * sc, sy), (sx, sy + 12 * sc)], fill=C["accent"] + (255,))
    elif p == "pill":
        step = int(40 * sc)
        for x in range(int(150 * sc), int(w - 150 * sc), step):
            od.arc((x, 32 * sc, x + step, 72 * sc), 0, 180, fill=C["accent"] + (255,), width=max(2, int(4 * sc)))
            od.arc((x, h - 72 * sc, x + step, h - 32 * sc), 180, 360, fill=C["accent"] + (255,), width=max(2, int(4 * sc)))
    elif p == "notch":
        od.line([(w / 2, 36 * sc), (w / 2, h - 36 * sc)], fill=C["accent"] + (110,), width=max(2, int(3 * sc)))
        od.arc((w / 2 - 60 * sc, h / 2 - 60 * sc, w / 2 + 60 * sc, h / 2 + 60 * sc), 0, 360, fill=C["accent"] + (110,), width=max(2, int(3 * sc)))
    elif p == "cartouche":
        for sy in (30 * sc, h - 30 * sc):
            od.polygon([(w / 2 - 14 * sc, sy), (w / 2, sy - 14 * sc), (w / 2 + 14 * sc, sy), (w / 2, sy + 14 * sc)], fill=C["accent"] + (255,))
    elif p == "stripebar":
        pat = [(0.00, 0.03), (0.07, 0.05), (0.17, 0.03), (0.25, 0.09), (0.38, 0.04), (0.47, 0.09), (0.6, 0.03), (0.68, 0.05), (0.78, 0.03), (0.86, 0.04)]
        for yy, tt in pat:
            y0 = h * 0.12 + yy * h * 0.76
            od.rectangle((18, y0, w * 0.1, y0 + tt * h * 0.76), fill=C["main"] + (255,))
            od.rectangle((w * 0.9, y0, w - 18, y0 + tt * h * 0.76), fill=C["main"] + (255,))
    elif p == "arrow":
        for k in range(5):
            od.polygon([((150 + k * 26) * sc, h - 44 * sc), ((163 + k * 26) * sc, h - 70 * sc), ((176 + k * 26) * sc, h - 44 * sc)], fill=C["accent"] + (255,))
            od.polygon([(w - (150 + k * 26) * sc, 44 * sc), (w - (163 + k * 26) * sc, 70 * sc), (w - (176 + k * 26) * sc, 44 * sc)], fill=C["accent"] + (255,))
    orn.putalpha(ImageChops.multiply(orn.split()[3], outer.filter(ImageFilter.MinFilter(25))))
    return Image.alpha_composite(img, orn)


def panel(C, title):
    W, H = 1280, 400
    if C.get("mascot") == "hood":
        import make_hood as mh
        img = mh.paper_panel((W, H), scale=1.2, seed=11)
        return mh.lettered(img, title, (W / 2, H / 2 + 52), fit_size(title, C["font"], 900, 150))
    img = shaped_panel(C, (W, H)) if C.get("pshape") else panel_base((W, H), C, 1.2)
    sz = fit_size(title, C["font"], 900, 150)
    return title_text(img, title, (W / 2, H / 2 + sz * 0.34), sz, C)


def overlay(C):
    W, H = 1920, 1080
    img = border((W, H), C["frame"], C, 1.7)
    cx0, cy0, cx1, cy1 = 80, H - 80 - 300, 80 + 533, H - 80
    cam = border((cx1 - cx0 + 150, cy1 - cy0 + 150), C["frame"], C, 0.55)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(cam, (cx0 - 75, cy0 - 75))
    img = Image.alpha_composite(img, layer)
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rectangle((cx0 + 6, cy0 + 6, cx1 - 6, cy1 - 6), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], cut))
    return img


def perimeter_point(w, h, t, inset):
    per = 2 * (w + h - 4 * inset)
    p = (t % 1.0) * per
    x0, y0, x1, y1 = inset, inset, w - inset, h - inset
    if p < x1 - x0:
        return x0 + p, y0
    p -= x1 - x0
    if p < y1 - y0:
        return x1, y0 + p
    p -= y1 - y0
    if p < x1 - x0:
        return x1 - p, y1
    p -= x1 - x0
    return x0, y1 - p


def animated(C, size, text, tsize, sc, n=28):
    w, h = size
    base = shaped_panel(C, size) if C.get("pshape") else panel_base(size, C, sc)
    sz = fit_size(text, C["font"], w - 200 * sc, tsize)
    base = title_text(base, text, (w / 2, h / 2 + sz * 0.34), sz, C)
    tm = Image.new("L", size, 0)
    ImageDraw.Draw(tm).rectangle((50 * sc, 50 * sc, w - 50 * sc, h - 50 * sc), fill=255)
    frames = []
    for i in range(n):
        t = i / n
        fr = base.copy()
        if C["anim"] == "shine":
            x = -80 + (w + 160) * t
            sh = Image.new("RGBA", size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(x, 0), (x + 46, 0), (x - 28, h), (x - 74, h)], fill=(255, 255, 255, 140))
            sh = sh.filter(ImageFilter.GaussianBlur(6))
            wh = Image.new("RGBA", size, (255, 255, 255, 0))
            wh.putalpha(ImageChops.multiply(sh.split()[3], tm))
            fr = Image.alpha_composite(fr, wh)
        elif C["anim"] == "static":
            pass
        elif C["anim"] == "runner":
            glow_l = Image.new("RGBA", size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_l)
            for k in range(10):
                px, py = perimeter_point(w, h, t - k * 0.008, 10 * sc)
                r = (13 - k) * sc
                gd.ellipse((px - r, py - r, px + r, py + r), fill=C["accent"] + (int(255 * (1 - k / 10)),))
            fr = Image.alpha_composite(fr, glow_l.filter(ImageFilter.GaussianBlur(2)))
        else:
            k = 0.5 + 0.5 * math.sin(2 * math.pi * t)
            bd = base
            wh = Image.new("RGBA", size, (255, 255, 255, 0))
            wh.putalpha(bd.split()[3].point(lambda v: int(v * 0.35 * k)))
            fr = Image.alpha_composite(fr, wh)
        frames.append(fr)
    return frames


# --------------------------------------------------------------------------------------- icons and screens

def medallion(C, size, inner_fn, ring_col, dots=0, crown=False, stars=0):
    k = size / 432
    kind = C["shape"]
    plate = C["fill"] if sum(C["fill"]) > 500 else tuple(min(255, c + 34) for c in C["accent2"])

    def fn(d, S):
        c = size / 2
        for r, col in ((c - 4, C["dark"]), (c - 12, ring_col), (c - 50, C["dark"]), (c - 59, plate)):
            cy = c + (8 * k if kind == "triangle" else 0)
            d.polygon([(x * S, y * S) for x, y in shape_pts(kind, c, cy, r * (0.93 if kind == "triangle" else 1))], fill=col + (255,))
        if kind in ("circle", "oval", "scallop", "flower"):
            for i in range(dots):
                a = 2 * math.pi * i / max(dots, 1)
                px, py = c + math.cos(a) * (c - 31 * k) * (0.86 if kind == "oval" else 1), c + math.sin(a) * (c - 31 * k)
                d.ellipse(((px - 8 * k) * S, (py - 8 * k) * S, (px + 8 * k) * S, (py + 8 * k) * S), fill=C["accent"] + (255,))
    return mr.layer((size, size), fn)


def badge_img(C, idx, size=432):
    ring = tuple(int(c * 0.55 + 100) for c in C["accent2"]) if idx < 3 else (C["main"] if idx < 5 else C["accent"])
    img = medallion(C, size, None, ring, dots=(idx - 1) * 4 if idx >= 4 else 0)
    ic = mr.emote("smile" if idx else "sleepy", "", int(size * (0.5 if C["shape"] == "triangle" else 0.62)))
    img.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2 + int(size * 0.02)))
    if idx >= 5:
        def fn(d, S):
            k = size / 432
            pts = [(size / 2 - 56 * k, 92 * k), (size / 2 - 56 * k, 50 * k), (size / 2 - 28 * k, 70 * k), (size / 2, 36 * k), (size / 2 + 28 * k, 70 * k), (size / 2 + 56 * k, 50 * k), (size / 2 + 56 * k, 92 * k)]
            d.polygon([(x * S, y * S) for x, y in pts], fill=C["accent"] + (255,), outline=C["ink"] + (255,), width=int(5 * k * S))
        img = Image.alpha_composite(img, mr.layer((size, size), fn))
    return img


def flair_img(C, tier, size=432):
    img = medallion(C, size, None, C["accent"] if tier == 3 else C["main"], dots=12 if tier == 3 else 0)
    ic = mr.emote("cool" if tier == 3 else "joyful", "crown" if tier == 3 else "", int(size * (0.5 if C["shape"] == "triangle" else 0.64)))
    img.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2 + 8))
    return img


def points_img(C, mood, extra, size=432):
    img = medallion(C, size, None, C["main"])
    ic = mr.emote(mood, extra, int(size * (0.5 if C["shape"] == "triangle" else 0.64)))
    img.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2 + 8))
    return img


def screen(C, title, sub, mood, extra):
    W, H = 1920, 1080
    img = radial((W, H), C["fill"] if sum(C["fill"]) < 500 else C["accent2"], C["dark"], cx=0.35, cy=0.5, spread=1.0).convert("RGBA")
    img = Image.alpha_composite(img, border((W, H), C["frame"], C, 2.2))
    ic = mr.emote(mood, extra, 640)
    img = shadow(img, ic.split()[3].point(lambda v: v), (0, 0), 1, (0, 0, 0), 0.0) if False else img
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(ic, (200, (H - 640) // 2))
    img = shadow(img, lay.split()[3], (0, 16), 24, (0, 0, 0), 0.5)
    img = Image.alpha_composite(img, lay)
    cx = 1330
    tcol = (C["text"], C["text2"]) if sum(C["fill"]) < 500 else ((250, 250, 250), (220, 220, 230))
    sz = fit_size(title, C["font"], 800, 190)
    m = text_mask((W, H), title, font(C["font"], sz), (cx, 520))
    img = shadow(img, m, (0, 8), 10, (0, 0, 0), 0.6)
    img = fill_mask(img, m, tcol[0] if sum(C["fill"]) < 500 else (250, 250, 250), tcol[1])
    d = ImageDraw.Draw(img)
    d.line([(cx - 320, 600), (cx + 320, 600)], fill=C["accent"] + (255,), width=5)
    for k, ln in enumerate(sub if isinstance(sub, list) else [sub]):
        szs = fit_size(ln, "georgiai.ttf", 700, 52)
        img = fill_mask(img, text_mask((W, H), ln, font("georgiai.ttf", szs), (cx, 676 + k * 64)), (240, 240, 240))
    return grain(img, 8)


# -------------------------------------------------------------------------------------------------- driver

def gif(frames, path, dur=50):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=dur, disposal=2, loop=0, optimize=False)


def build(name, only=None):
    C = dict(SETS[name])
    out = TW / name
    apply_set(C)
    print("==", name, flush=True)
    # emotes: new character set (drop the old shared gem set first)
    em_dir = out / "Emotes"
    if em_dir.exists() and not only:
        shutil.rmtree(em_dir)
    for folder, nm, mood, extra in ([] if only else mr.EMOTE_SETS):
        for size in (448, 112, 56, 28):
            p = out / folder / f"{nm}_{size}.{'gif' if nm in mr.ANIMATED else 'png'}"
            p.parent.mkdir(parents=True, exist_ok=True)
            if nm in mr.ANIMATED:
                anim = {"happycat": "sway", "laughing": "bounce", "mad": "shake", "playful": "sway", "sleepy": "sway"}[nm]
                gif([mr.emote(mood, extra, size, i / 20, anim) for i in range(20)], p, 60)
            else:
                mr.emote(mood, extra, size).save(p, optimize=True)
    for sub in ("Badges", "Flair", "Points"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    tiers = ["base", "3month", "6month", "9month", "1year", "2year", "3year"]
    for i, t in enumerate(tiers):
        p = out / "Badges" / f"{t}_432.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        badge_img(C, i).save(p, optimize=True)
    for t in (2, 3):
        p = out / "Flair" / f"tier{t}_flair_432.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        flair_img(C, t).save(p, optimize=True)
    for k, (mood, extra) in {"smile": ("smile", ""), "love": ("lovely", "hearts"), "sparkle": ("sparkly", "sparkles")}.items():
        p = out / "Points" / f"points_{k}_432.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        points_img(C, mood, extra).save(p, optimize=True)
    if C["frame"] and not only:
        overlay(C).save(out / "Overlay" / "overlay_frame.png", optimize=True) if (out / "Overlay").mkdir(parents=True, exist_ok=True) is None else None
        gif(animated(C, (800, 360), "Thanks for the follow!", 100, 1.0), out / "Alert" / "alert.gif")
        gif(animated(C, (440, 200), "Petals Of Iron" if name in ("Helmet", "Slash", "Snake", "Floral", "Hood") else name, 64, 0.5, 30), out / "Corner" / "corner.gif")
    if C["frame"] or C.get("pshape"):
        for fn_, t in PANELS:
            p = out / "Panels" / f"{fn_}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            panel(C, t).convert("RGB").save(p, optimize=True)
    if C["screens"] and not only:
        for fn_, t, s, mood, extra in (("starting_soon", "Starting soon", ["The stream begins shortly"], "party", "party"),
                                       ("be_right_back", "Be right back", ["I will be back", "in a moment"], "hi", "wave"),
                                       ("offline", "Offline", ["Thank you for watching,", "see you next time"], "sleepy", "zzz")):
            p = out / "Screens" / f"{fn_}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            screen(C, t, s, mood, extra).convert("RGB").save(p, optimize=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for n in (args or list(SETS)):
        build(n, only="--icons" in sys.argv)
    print("done")

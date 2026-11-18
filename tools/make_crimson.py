#!/usr/bin/env python3
"""Crimson Twitch kit: blonde vampire elf in black and red. Gothic arches, bats and a blood moon.
Output: C:/Users/SaphiresSilver/Documents/twitch/Crimson/   (not used by the portfolio site)"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.argv = sys.argv[:1]
import make_nightwing as nw
import make_nightwing2 as n2
from art import *  # noqa: F401,F403

ART = Path("C:/Users/SaphiresSilver/Documents/twitch/character3.png")
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Crimson")
nw.OUT = OUT

DEEP, NIGHT = (14, 5, 9), (44, 10, 20)
BLOOD, ROSE = (170, 22, 42), (222, 70, 86)
GOLD, GOLD_D = (228, 186, 98), (150, 104, 40)
BONE, BONE_D = (244, 234, 224), (176, 156, 152)
for k, v in dict(DEEP=DEEP, NIGHT=NIGHT, INDIGO=BLOOD, VIOLET=ROSE, AMBER=GOLD, AMBER_D=GOLD_D, WINE=(196, 24, 46), TEAL=(240, 190, 170),
                 SILVER=BONE, SILVER_D=BONE_D, HEAD="timesbd.ttf", BODY="timesbd.ttf").items():
    setattr(nw, k, v)
for k, v in dict(SKIN=(252, 232, 220), SKIN_D=(230, 190, 180), HAIR=(226, 196, 144), HAIR_D=(150, 108, 62), HAIR_L=(255, 240, 204),
                 EYE_A=(176, 20, 34), EYE_B=(244, 110, 110), RIB=BLOOD, LINE=(32, 12, 16)).items():
    setattr(n2, k, v)


# ---------------------------------------------------------------- bats
def bat_wings(size, cx, cy, scale, flip=False, alpha=255):
    """Bat-wing ornament: three bones and a scalloped membrane."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = scale * (-1 if flip else 1)
    P = lambda p: (cx + p[0] * s, cy + p[1] * scale)
    tips = [(380, -250), (470, -40), (400, 170), (230, 230)]
    pts = [(0, 0), tips[0]]
    for a, b in zip(tips, tips[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        for t in [i / 8 for i in range(1, 8)]:   # scallop curving back to the body
            bx = a[0] * (1 - t) ** 2 + 2 * (1 - t) * t * (mx - 60) + b[0] * t * t
            by = a[1] * (1 - t) ** 2 + 2 * (1 - t) * t * (my - 10) + b[1] * t * t
            pts.append((bx, by))
        pts.append(b)
    mem = [P(p) for p in pts]
    d.polygon(mem, fill=(70, 10, 22, alpha))
    d.line(mem + [mem[0]], fill=GOLD + (alpha,), width=max(2, int(9 * abs(scale))), joint="curve")
    for t in tips:
        d.line([P((0, 0)), P(t)], fill=GOLD_D + (alpha,), width=max(2, int(11 * abs(scale))))
        d.line([P((0, -3)), P((t[0], t[1] - 4))], fill=BLOOD + (alpha,), width=max(1, int(5 * abs(scale))))
    return layer


nw.wings = bat_wings


def bat(d, cx, cy, w, col, alpha=255):
    pts = [(0, -0.12), (0.12, -0.28), (0.18, -0.12), (0.26, -0.18), (0.55, -0.34), (1.0, -0.18), (0.8, 0.02), (0.64, 0.0), (0.5, 0.18), (0.36, 0.04), (0.18, 0.2), (0.08, 0.04), (0, 0.1)]
    full = [(cx + x * w, cy + y * w) for x, y in pts] + [(cx - x * w, cy + y * w) for x, y in reversed(pts)]
    d.polygon(full, fill=col + (alpha,))


def bats_layer(size, n, seed, col=(8, 2, 5), wmin=30, wmax=90, box=None):
    rnd = random.Random(seed)
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    b = box or (0, 0, size[0], size[1])
    for _ in range(n):
        bat(d, rnd.randint(b[0], b[2]), rnd.randint(b[1], b[3]), rnd.randint(wmin, wmax), col, rnd.randint(160, 255))
    return lay


def moon_bg(size, seed=1, mx=0.7, my=0.42, mr=0.3):
    w, h = size
    img = radial(size, (70, 14, 28), (10, 3, 8), mx, my, 1.1).convert("RGBA")
    m = Image.new("L", size, 0)
    r = int(min(w, h) * mr)
    ImageDraw.Draw(m).ellipse((w * mx - r, h * my - r, w * mx + r, h * my + r), fill=255)
    img = glow(img, (w * mx - r * 1.5, h * my - r * 1.5, w * mx + r * 1.5, h * my + r * 1.5), (190, 30, 50), blur=int(r * 0.7), alpha=150)
    disc = radial(size, (226, 70, 80), (150, 18, 36), mx, my, 0.6).convert("RGBA")
    disc.putalpha(m)
    img = Image.alpha_composite(img, disc)
    img = Image.alpha_composite(img, bats_layer(size, max(6, int(w / 140)), seed, box=(0, 0, w, int(h * 0.7)), wmin=int(w / 70), wmax=int(w / 22)))
    return grain(vignette(img, 0.55, (3, 0, 2)), 6)


def arch(canvas, box, fill, outline=None, w=0, peak=0.22):
    """Gothic lancet window: straight sides, pointed arch top."""
    x0, y0, x1, y1 = box
    ph = (x1 - x0) * peak
    pts = [(x0, y1), (x0, y0 + ph), ((x0 + x1) / 2, y0), (x1, y0 + ph), (x1, y1)]
    S = 3
    m = Image.new("L", (canvas.width * S, canvas.height * S), 0)
    md = ImageDraw.Draw(m)
    md.polygon([(x * S, y * S) for x, y in pts], fill=255)
    lay = Image.new("RGBA", canvas.size, fill + (255,))
    lay.putalpha(m.resize(canvas.size, Image.LANCZOS))
    out = Image.alpha_composite(canvas, lay)
    if outline:
        d = ImageDraw.Draw(out)
        d.line(pts + [pts[0]], fill=outline + (255,), width=w, joint="curve")
    return out


def cut_rect(canvas, box, fill, outline, w, cut=26, alpha=255):
    x0, y0, x1, y1 = box
    pts = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut)]
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon(pts, fill=fill + (alpha,))
    canvas = Image.alpha_composite(canvas, lay)
    if outline:
        ImageDraw.Draw(canvas).line(pts + [pts[0]], fill=outline + (255,), width=w, joint="curve")
    return canvas


def drop_shape(d, cx, cy, h, col, outline=DEEP, ow=6):
    pts = []
    for i in range(60):
        t = math.pi * i / 59
        pts.append((cx + math.sin(t) * h * 0.38 * (0.35 + 0.65 * math.sin(t / 2 + 0.3) ** 0.5), cy - h * 0.1 + math.cos(t) * h * 0.38 + h * 0.1))
    circ = [(cx + math.cos(a) * h * 0.38, cy + h * 0.14 + math.sin(a) * h * 0.38) for a in [math.pi * 2 * i / 80 for i in range(80)]]
    tip = [(cx - h * 0.33, cy + h * 0.02), (cx, cy - h * 0.5), (cx + h * 0.33, cy + h * 0.02)]
    d.polygon(circ, fill=col + (255,))
    d.polygon(tip, fill=col + (255,))
    d.ellipse((cx - h * 0.22, cy + h * 0.04, cx - h * 0.08, cy + h * 0.2), fill=(255, 190, 190, 200))


# ---------------------------------------------------------------- art
def figure(art_cut):
    return art_cut


def face_hack(art):
    face = art.crop((300, 70, 620, 390)).resize((368, 368), Image.LANCZOS).convert("RGBA")
    h = Image.new("RGBA", (1000, 1600), (0, 0, 0, 0))
    h.alpha_composite(face, (322, 70))
    return h


def place_char(img, cut, scale, cx_char, bottom=None, top=None, dim=0.0):
    s = scale
    im = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
    x = int(cx_char - 455 * s)
    y = (img.height - im.height) if bottom is not None else int(top)
    if dim:
        im = Image.blend(im, Image.new("RGBA", im.size, (20, 4, 10, 255)), dim).copy()
        im.putalpha(cut.resize(im.size, Image.LANCZOS).split()[3])
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (x, y), (max(0, -x), max(0, -y)))
    img = shadow(img, lay.split()[3], (0, 14), 26, (0, 0, 0), 0.6)
    return Image.alpha_composite(img, lay)


def title(img, t, xy, size, anchor="left", track=8, hue=(BONE, BONE_D)):
    return nw.title(img, t, xy, size, anchor, track, hue)


def lines(img, y, cx, half, col=GOLD):
    d = ImageDraw.Draw(img)
    d.line([(cx - half, y), (cx - 24, y)], fill=col + (255,), width=3)
    d.line([(cx + 24, y), (cx + half, y)], fill=col + (255,), width=3)
    bat(d, cx, y, 18, col)


# ---------------------------------------------------------------- pieces
def screen(cut, kind, big, small, note):
    W, H = 1920, 1080
    cfg = {"start": (0.76, 0.42, 1.36, 1400), "brb": (0.28, 0.42, 1.36, 520), "end": (0.5, 0.62, 1.0, 960), "off": (0.72, 0.42, 1.36, 1400)}[kind]
    img = moon_bg((W, H), {"start": 3, "brb": 5, "end": 8, "off": 11}[kind], cfg[0], cfg[1], 0.28)
    if kind == "end":
        img = place_char(img, cut, cfg[2], cfg[3], bottom=True)
        img, _ = nw.fit_title(img, big, (960, 130), 1500, 110, "center", 12)
        lines(img, 190, 960, 380)
        img = nw.label(img, small, (960, 250), 36, GOLD, "center", 10)
    else:
        img = place_char(img, cut, cfg[2], cfg[3], bottom=True, dim=0.35 if kind == "off" else 0)
        X = 110 if kind in ("start", "off") else 1000
        img, _ = nw.fit_title(img, big, (X, 520), 800, 118, "left", 10)
        d = ImageDraw.Draw(img)
        d.line([(X, 570), (X + 520, 570)], fill=GOLD + (255,), width=4)
        bat(d, X + 560, 570, 22, GOLD)
        img = nw.label(img, small, (X, 640), 36, GOLD, "left", 10)
        img = nw.label(img, note, (X, 700), 26, BONE_D, "left", 5)
    img = ImageDraw.Draw(img) and img
    nw.corner_brackets(img, 44, 110, GOLD + (255,), width=4)
    img = nw.label(img, nw.NAME, (960 if kind == "end" else 70, 60 if kind == "end" else 100), 26, BONE, "center" if kind == "end" else "left", 12)
    return img


def banner(cut, W=1200, H=480):
    img = moon_bg((W, H), 2, 0.8, 0.45, 0.4)
    img = place_char(img, cut, 0.82, 960, top=-26)
    img, _ = nw.fit_title(img, nw.NAME, (60, 224), 560, 70, "left", 10)
    d = ImageDraw.Draw(img)
    d.line([(60, 256), (420, 256)], fill=GOLD + (255,), width=3)
    bat(d, 450, 256, 16, GOLD)
    img = nw.label(img, "WOW  ·  ART  ·  STREAMS", (60, 312), 22, GOLD, "left", 9)
    return img


def logo(art, S=2000):
    img = nw.emblem(face_hack(art), S, with_name=False)
    rb = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rb)
    y0, y1 = 1550, 1740
    poly = [(250, y0), (S - 250, y0), (S - 170, (y0 + y1) / 2), (S - 250, y1), (250, y1), (170, (y0 + y1) / 2)]
    rd.polygon(poly, fill=DEEP + (255,))
    img = shadow(img, rb.split()[3], (0, 12), 16, (0, 0, 0), 0.55)
    rd.polygon(poly, outline=GOLD + (255,), width=7)
    img = Image.alpha_composite(img, rb)
    img, _ = nw.fit_title(img, nw.NAME, (S // 2, 1686), 1260, 130, "center", 14)
    return img


def panel(text, sub, W=640, H=200):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(60, 24), (W - 60, 24), (W - 24, 60), (W - 24, H - 60), (W - 60, H - 24), (60, H - 24), (24, H - 60), (24, 60)], fill=255)
    img = shadow(img, m, (0, 8), 10, (0, 0, 0), 0.55)
    img = cut_rect(img, (24, 24, W - 24, H - 24), DEEP, GOLD, 4, 38)
    img = cut_rect(img, (36, 36, W - 36, H - 36), NIGHT, BLOOD, 3, 30)
    d = ImageDraw.Draw(img)
    bat(d, 80, H // 2, 34, BLOOD)
    bat(d, W - 80, H // 2, 34, BLOOD)
    img = nw.title(img, text, (W // 2, H // 2 + 14 - (10 if sub else 0)), 56, "center", 8)
    if sub:
        img = nw.label(img, sub, (W // 2, H // 2 + 48), 19, GOLD, "center", 6)
    return img


def overlay(W=1920, H=1080):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), outline=DEEP + (255,), width=34)
    d.rectangle((30, 30, W - 30, H - 30), outline=BLOOD + (255,), width=5)
    d.line([(200, 30), (W - 200, 30)], fill=GOLD + (255,), width=3)
    for (x, y, fx) in ((110, 76, 1), (W - 110, 76, -1)):
        bat(d, x, y, 44, GOLD)
    for (x, y) in ((70, H - 70), (W - 70, H - 70)):
        bat(d, x, y, 30, BLOOD)
    # arched webcam window
    cx0, cy0, cw, ch = 70, H - 520, 520, 420
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    plate = arch(plate, (cx0 - 20, cy0 - 20, cx0 + cw + 20, cy0 + ch + 20), DEEP, GOLD, 5, 0.35)
    img = shadow(img, plate.split()[3], (0, 10), 14, (0, 0, 0), 0.6)
    img = Image.alpha_composite(img, plate)
    hole = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hole = arch(hole, (cx0, cy0, cx0 + cw, cy0 + ch), (255, 255, 255), None, 0, 0.35)
    img.putalpha(ImageChops.multiply(img.split()[3], ImageChops.invert(hole.split()[3])))
    img = nw.title(img, nw.NAME, (cx0 + cw // 2, cy0 + ch + 74), 34, "center", 10)
    # chat: cut-corner box
    cb = (W - 540, 110, W - 70, H - 180)
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pl = cut_rect(pl, cb, DEEP, GOLD, 4, 36, 215)
    img = Image.alpha_composite(img, pl)
    img = nw.title(img, "CHAT", ((cb[0] + cb[2]) // 2, cb[1] + 60), 36, "center", 16)
    lines(img, cb[1] + 86, (cb[0] + cb[2]) // 2, 150)
    # latest bar
    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bar = cut_rect(bar, (700, H - 140, W - 70, H - 64), DEEP, BLOOD, 3, 22, 225)
    img = Image.alpha_composite(img, bar)
    img = nw.label(img, "LATEST FOLLOWER", (760, H - 92), 22, GOLD, "left", 6)
    img = nw.label(img, "LATEST SUB", (1260, H - 92), 22, GOLD, "left", 6)
    return img


def alert(art, head, sub, col, W=1000, H=320):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [(70, 50), (W - 70, 50), (W - 20, H // 2), (W - 70, H - 50), (70, H - 50), (20, H // 2)]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    img = shadow(img, m, (0, 10), 14, (0, 0, 0), 0.6)
    img = cut_rect(img, (24, 46, W - 24, H - 46), DEEP, col, 5, 60)
    img = cut_rect(img, (38, 60, W - 38, H - 60), NIGHT, GOLD, 2, 48)
    r = 108
    d = ImageDraw.Draw(img)
    d.ellipse((120 - r - 10, H // 2 - r - 10, 120 + r + 10, H // 2 + r + 10), fill=DEEP + (255,), outline=col + (255,), width=6)
    pic = art.crop((300, 70, 620, 390)).resize((2 * r, 2 * r), Image.LANCZOS).convert("RGBA")
    mm = Image.new("L", (2 * r * 3, 2 * r * 3), 0)
    ImageDraw.Draw(mm).ellipse((0, 0, 2 * r * 3 - 1, 2 * r * 3 - 1), fill=255)
    base = radial((2 * r, 2 * r), (120, 20, 40), (30, 6, 12), 0.5, 0.4, 0.9).convert("RGBA")
    base.alpha_composite(pic)
    base.putalpha(mm.resize((2 * r, 2 * r), Image.LANCZOS))
    img.alpha_composite(base, (120 - r, H // 2 - r))
    img = nw.label(img, head, (290, 128), 28, col, "left", 12)
    img, _ = nw.fit_title(img, sub, (290, 226), W - 380, 80, "left", 6)
    bat(ImageDraw.Draw(img), W - 100, 96, 24, col)
    return img


ALERTS = [("NEW FOLLOWER", "{name}", "follow", (240, 190, 170)), ("NEW SUBSCRIBER", "{name}", "subscribe", GOLD), ("INCOMING RAID", "{name}", "raid", (230, 60, 76)),
          ("DONATION", "{amount}", "donation", (120, 220, 160)), ("BITS", "{amount}", "bits", (190, 150, 255))]


# ---------------------------------------------------------------- badges and emotes
def sub_badge(tier):
    S = 360
    img = nw.badge_base(S)
    d = ImageDraw.Draw(img)
    c = S // 2
    cols = [(240, 190, 170), (214, 72, 84), GOLD, (230, 40, 70), BONE, (255, 214, 120)]
    d.ellipse((c - 150, c - 150, c + 150, c + 150), fill=NIGHT + (255,))
    for k in range(tier + 1):                         # more bats around the rim for higher tiers
        a = math.radians(-90 + (k - tier / 2) * 30)
        bat(d, c + math.cos(a) * 124, c + math.sin(a) * 124, 24, GOLD)
    drop_shape(d, c, c + 6, 210, cols[tier])
    return img


def bits_badge(tier):
    S = 360
    img = nw.badge_base(S)
    d = ImageDraw.Draw(img)
    c = S // 2
    cols = [(150, 140, 150), (240, 190, 170), (230, 40, 70), GOLD]
    bat(d, c, c + 6, 112 + tier * 8, cols[tier])
    d.ellipse((c - 12, c - 12, c + 12, c + 12), fill=(255, 255, 255, 255))
    return img


def emote_drop():
    img = Image.new("RGBA", (448, 448), (0, 0, 0, 0))
    drop_shape(ImageDraw.Draw(img), 224, 230, 400, (210, 24, 48))
    return nw.outlined(img, None, 12)


def emote_bat():
    img = Image.new("RGBA", (448, 448), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bat(d, 224, 230, 200, (34, 12, 20))
    d.ellipse((196, 196, 214, 214), fill=(230, 40, 60, 255))
    d.ellipse((234, 196, 252, 214), fill=(230, 40, 60, 255))
    return nw.outlined(img, None, 12, BONE)


def emote_heart():
    return nw.emote_heart()


# ---------------------------------------------------------------- showcase
def showcase():
    from make_nightwing2 import fit
    K = OUT
    OD = K / "Showcase"
    OD.mkdir(exist_ok=True)
    W, H = 1600, 900
    ld = lambda p: Image.open(K / p).convert("RGBA")

    def drp(c, im, xy, blur=16, op=0.5):
        lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
        c = shadow(c, lay.split()[3], (0, 12), blur, (0, 0, 0), op)
        return Image.alpha_composite(c, lay)

    def board(seed, t, s):
        img = moon_bg((W, H), seed, 0.9, 0.12, 0.2)
        img = nw.title(img, t, (90, 112), 50, "left", 12)
        img = nw.label(img, s, (90, 156), 20, GOLD, "left", 7)
        ImageDraw.Draw(img).line([(90, 180), (420, 180)], fill=GOLD + (255,), width=3)
        return img

    img = board(51, "CRIMSON", "TWITCH STREAM KIT  ·  LOGO, BANNER, AVATAR")
    img = drp(img, fit(ld("Logo/crimson_logo.png"), 640, 640), (90, 205))
    img = drp(img, fit(ld("Banner/profile_banner_1200x480.png"), 760, 304), (780, 214))
    av = fit(ld("Logo/crimson_avatar.png"), 300, 300)
    for sz, x, y in ((300, 860, 540), (150, 1200, 620), (72, 1390, 660)):
        img = drp(img, av.resize((sz, sz), Image.LANCZOS), (x, y), 8, 0.4)
    img.convert("RGB").save(OD / "board_1.png")
    img = board(52, "SCREENS", "STARTING SOON  ·  BE RIGHT BACK  ·  ENDING  ·  OFFLINE")
    for i, n in enumerate(["starting_soon", "brb", "ending", "offline"]):
        img = drp(img, fit(ld("Screens/%s.png" % n), 560, 315), (210 + (i % 2) * 620, 210 + (i // 2) * 343), 14)
    img.convert("RGB").save(OD / "board_2.png")
    img = board(53, "PANELS, ALERTS & OVERLAY", "NINE PANELS  ·  FIVE ALERTS  ·  STREAM OVERLAY")
    for i, n in enumerate(["about", "schedule", "rules", "socials", "donate", "commands"]):
        img = drp(img, fit(ld("Panels/%s.png" % n), 400, 125), (90 + (i % 2) * 420, 215 + (i // 2) * 135), 8)
    for i, n in enumerate(["follow", "subscribe", "raid"]):
        img = drp(img, fit(ld("Alerts/%s.png" % n), 520, 166), (960, 205 + i * 140), 10)
    img = drp(img, fit(ld("Overlay/stream_overlay.png"), 520, 292).convert("RGBA"), (960, 630), 10) if False else img
    ov = moon_bg((1920, 1080), 9, 0.3, 0.4, 0.2)
    ov.alpha_composite(ld("Overlay/stream_overlay.png"))
    img = drp(img, ov.resize((480, 270), Image.LANCZOS), (90, 625), 10)
    img.convert("RGB").save(OD / "board_3.png")
    img = board(54, "EMOTES & BADGES", "TEN EMOTES  ·  SIX SUB BADGES  ·  FOUR BITS BADGES")
    em = ["happy", "love", "cry", "angry", "smug", "wink", "sleep", "shock", "heart", "gg", "drop", "bat"]
    for i, n in enumerate(em):
        img = drp(img, fit(ld("Emotes/cr_%s_448.png" % n), 170, 170), (100 + (i % 6) * 235, 215 + (i // 6) * 205), 8, 0.4)
    x = 130
    for i in range(6):
        img = drp(img, sub_badge(i).resize((104, 104), Image.LANCZOS), (x, 670), 6, 0.4)
        x += 128
    x += 40
    for i in range(4):
        img = drp(img, bits_badge(i).resize((104, 104), Image.LANCZOS), (x, 670), 6, 0.4)
        x += 128
    img.convert("RGB").save(OD / "board_4.png")
    print("showcase done")


def main():
    art = Image.open(ART).convert("RGBA")
    cut = nw.cutout(ART)
    OUT.mkdir(parents=True, exist_ok=True)
    cut.save(OUT / "character_cutout.png")
    nw.save(logo(cut), "Logo", "crimson_logo.png")
    nw.save(nw.emblem(face_hack(cut), 1000), "Logo", "crimson_avatar.png")
    nw.save(banner(cut), "Banner", "profile_banner_1200x480.png")
    sub = {"DONATE": "feed the night", "DISCORD": "join the coven", "SCHEDULE": "when the night falls", "ABOUT": "who is she"}
    for t, s in nw.PANELS:
        nw.save(panel(t, sub.get(t, s)), "Panels", t.lower() + ".png")
    for kind, big, small, note, fn in (("start", "STARTING SOON", "THE NIGHT AWAKENS", "grab a drink and settle in", "starting_soon"),
                                       ("brb", "BE RIGHT BACK", "GONE HUNTING", "back in a moment", "brb"),
                                       ("end", "THANKS FOR WATCHING", "SEE YOU AFTER DARK", "follow so you never miss a stream", "ending"),
                                       ("off", "OFFLINE", "RESTING IN THE DARK", "see you at the next stream", "offline")):
        nw.save(screen(cut, kind, big, small, note).convert("RGB"), "Screens", fn + ".png")
    nw.save(overlay(), "Overlay", "stream_overlay.png")
    for head, sb, fn, col in ALERTS:
        nw.save(alert(cut, head, sb, col), "Alerts", fn + ".png")
    for i, m in enumerate((1, 3, 6, 12, 24, 36)):
        b = sub_badge(i)
        for s in (72, 36, 18):
            nw.save(b.resize((s, s), Image.LANCZOS), "Badges", "Subscriber", "%dmonth_%d.png" % (m, s))
    for i, n in enumerate((1, 100, 1000, 10000)):
        b = bits_badge(i)
        for s in (72, 36, 18):
            nw.save(b.resize((s, s), Image.LANCZOS), "Badges", "Bits", "bits%d_%d.png" % (n, s))
    keep = nw.blade
    nw.blade = lambda *a, **k: None                   # no horns on this character
    emos = {n: n2.chibi(n) for n in n2.EXPR}
    nw.blade = keep
    emos.update(heart=emote_heart(), gg=nw.emote_text("GG", GOLD, GOLD_D), drop=emote_drop(), bat=emote_bat())
    for n, im in emos.items():
        nw.save(im, "Emotes", "cr_%s_448.png" % n)
        for s in (112, 56, 28):
            nw.save(im.resize((s, s), Image.LANCZOS), "Emotes", "cr_%s_%d.png" % (n, s))
    for n in ("happy", "love", "smug", "drop"):
        nw.save(emos[n].resize((112, 112), Image.LANCZOS), "ChannelPoints", n + ".png")
    showcase()


if __name__ == "__main__":
    main()

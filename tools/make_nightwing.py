#!/usr/bin/env python3
"""Nightwing Twitch kit built around the indigo/burgundy winged character art.
Output: C:/Users/SaphiresSilver/Documents/twitch/Nightwing/...   (not used by the portfolio site)

    python tools/make_nightwing.py [path to character art]
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from scipy import ndimage

from art import *  # noqa: F401,F403

ART = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/Users/SaphiresSilver/Documents/twitch/character.png")
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Nightwing")
NAME = "PETALS OF IRON"

DEEP = (16, 12, 38)
NIGHT = (30, 22, 70)
INDIGO = (78, 66, 162)
VIOLET = (140, 120, 214)
WINE = (150, 40, 66)
AMBER = (238, 168, 84)
AMBER_D = (170, 104, 44)
TEAL = (116, 206, 214)
SILVER = (214, 218, 236)
SILVER_D = (150, 156, 184)
HEAD = "georgiab.ttf"
BODY = "segoeuib.ttf"


# ---------------------------------------------------------------- the character
def cutout(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    white = (a[..., 0] > 241) & (a[..., 1] > 241) & (a[..., 2] > 241)
    lab, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(white, lab, range(1, n + 1))
    big = {i + 1 for i, v in enumerate(sizes) if v > 1500}
    bg = np.isin(lab, list(border | big))
    alpha = Image.fromarray(((~bg) * 255).astype("uint8"))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.9))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def crop_art(art, box, size):
    return art.crop(box).resize(size, Image.LANCZOS)


# ---------------------------------------------------------------- ornaments
def blade(draw, p0, p1, p2, w0, col, n=60):
    """Tapering curved thorn along a quadratic bezier."""
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        j0, j1 = max(i - 1, 0), min(i + 1, n)
        dx, dy = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = w0 * (1 - i / n) ** 0.85 / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    draw.polygon(left + right[::-1], fill=col)


def wings(size, cx, cy, scale, flip=False, alpha=255):
    """A set of three thorn-wings in indigo with amber edge, like the character's."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = scale * (-1 if flip else 1)
    specs = [((0, 0), (260, -70), (390, -230), 46), ((0, 14), (310, 26), (450, -30), 40), ((0, 26), (250, 130), (370, 170), 36)]
    for (a, b, c, w) in specs:
        P = lambda p: (cx + p[0] * s, cy + p[1] * scale)
        blade(d, P((a[0], a[1] + 7)), P((b[0], b[1] + 8)), P((c[0], c[1] + 8)), w * scale * 1.2, AMBER_D + (alpha,))
        blade(d, P(a), P(b), P(c), w * scale * 1.12, AMBER + (alpha,))
        blade(d, P((a[0], a[1] - 2)), P((b[0], b[1] - 2)), P((c[0], c[1] - 3)), w * scale * 0.9, INDIGO + (alpha,))
        blade(d, P((a[0], a[1] - 5)), P((b[0], b[1] - 6)), P((c[0], c[1] - 8)), w * scale * 0.42, VIOLET + (alpha,))
    return layer


def divider(canvas, cx, y, half, col=AMBER):
    d = ImageDraw.Draw(canvas)
    d.line([(cx - half, y), (cx - 22, y)], fill=col + (255,), width=3)
    d.line([(cx + 22, y), (cx + half, y)], fill=col + (255,), width=3)
    diamond(d, cx, y, 11, col + (255,))
    diamond(d, cx - 36, y, 5, col + (255,))
    diamond(d, cx + 36, y, 5, col + (255,))


def bg(size, seed=4):
    w, h = size
    img = radial(size, (52, 38, 108), DEEP, 0.62, 0.45, 0.95).convert("RGBA")
    for sgn, x in ((1, w * 0.04), (-1, w * 0.96)):
        img = Image.alpha_composite(img, wings(size, x, h * 0.52, h / 1300 * 1.05, flip=(sgn == -1), alpha=40))
    img = sparkles(img, (0, 0, w, h), int(w * h / 26000), AMBER, seed=seed, max_r=3.2)
    return grain(vignette(img, 0.55, (4, 2, 14)), 6)


def title(canvas, text, xy, size, anchor="center", track=10, hue=(SILVER, SILVER_D)):
    m = text_mask(canvas.size, text, font(HEAD, size), xy, track=track, anchor=anchor)
    canvas = shadow(canvas, m, (0, int(size * 0.05)), max(4, size // 28), (0, 0, 0), 0.7)
    return fill_mask(canvas, m, *hue)


def fit_title(canvas, text, xy, maxw, size=150, anchor="left", track=12):
    while size > 40:
        m = text_mask(canvas.size, text, font(HEAD, size), xy, track=track, anchor=anchor)
        b = m.getbbox()
        if b and b[2] - b[0] <= maxw:
            break
        size -= 6
    return title(canvas, text, xy, size, anchor=anchor, track=track), size


def label(canvas, text, xy, size, col=AMBER, anchor="center", track=8):
    return fill_mask(canvas, text_mask(canvas.size, text, font(BODY, size), xy, track=track, anchor=anchor), col)


def put(canvas, im, xy, glow_col=None):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
    canvas = shadow(canvas, lay.split()[3], (0, 22), 26, (0, 0, 0), 0.55)
    return Image.alpha_composite(canvas, lay)


def save(img, *parts):
    p = OUT.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)
    print("saved", "/".join(parts), flush=True)


def fit(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


# ---------------------------------------------------------------- emblem / logo
def circle_art(art, box, d):
    c = crop_art(art, box, (d, d))
    m = Image.new("L", (d * 3, d * 3), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d * 3 - 1, d * 3 - 1), fill=255)
    m = m.resize((d, d), Image.LANCZOS)
    base = radial((d, d), (92, 78, 176), (30, 22, 70), 0.5, 0.4, 0.9).convert("RGBA")
    c = c.convert("RGBA")
    base.alpha_composite(c)
    base.putalpha(m)
    return base


def emblem(art, S=1400, with_name=False):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx, cy = S // 2, S // 2 - (60 if with_name else 0)
    R = int(S * 0.34)
    for flip in (False, True):
        img = Image.alpha_composite(img, wings((S, S), cx + (R * 0.62 if not flip else -R * 0.62), cy + R * 0.05, S / 2000 * 1.7, flip=flip))
    d = ImageDraw.Draw(img)
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30), fill=255)
    img = shadow(img, m, (0, 14), 22, (0, 0, 0), 0.6)
    d = ImageDraw.Draw(img)
    for r, col in ((R + 30, DEEP), (R + 22, AMBER), (R + 12, AMBER_D), (R + 6, DEEP)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
    pic = circle_art(art, (322, 70, 690, 438), 2 * R)
    img.alpha_composite(pic, (cx - R, cy - R))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=SILVER + (255,), width=5)
    for ang in (90, 270):
        x = cx + math.cos(math.radians(ang)) * (R + 30)
        y = cy + math.sin(math.radians(ang)) * (R + 30)
        diamond(d, x, y + (12 if ang == 90 else -12), 15, AMBER + (255,))
    if with_name:
        img = title(img, NAME, (cx, S - 150), 150, track=14)
    return img


# ---------------------------------------------------------------- panels
def panel(text, sub, W=640, H=200):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    plate = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(plate)
    pts = [(46, 22), (W - 46, 22), (W - 16, H // 2), (W - 46, H - 22), (46, H - 22), (16, H // 2)]
    pd.polygon(pts, fill=255)
    img = shadow(img, plate, (0, 8), 10, (0, 0, 0), 0.5)
    for k, col in ((0, AMBER), (4, DEEP), (7, NIGHT)):
        lay = Image.new("RGBA", (W, H), col + (255,))
        m = Image.new("L", (W, H), 0)
        inset = k
        ImageDraw.Draw(m).polygon([(46 + inset, 22 + inset), (W - 46 - inset, 22 + inset), (W - 16 - inset, H // 2), (W - 46 - inset, H - 22 - inset), (46 + inset, H - 22 - inset), (16 + inset, H // 2)], fill=255)
        lay.putalpha(m)
        img = Image.alpha_composite(img, lay)
    img = Image.alpha_composite(img, wings((W, H), 70, H // 2, 0.16, flip=True, alpha=170))
    img = Image.alpha_composite(img, wings((W, H), W - 70, H // 2, 0.16, alpha=170))
    img = glow(img, (W // 2 - 220, H // 2 - 40, W // 2 + 220, H // 2 + 40), INDIGO, blur=40, alpha=90)
    img = title(img, text, (W // 2, H // 2 + 16 - (12 if sub else 0)), 58, track=8)
    if sub:
        img = label(img, sub, (W // 2, H // 2 + 50), 20, AMBER, track=6)
    return img


PANELS = [("ABOUT", "who is she"), ("SCHEDULE", "when i stream"), ("RULES", "be kind"), ("SOCIALS", "find me"), ("DONATE", "support the nest"),
          ("COMMANDS", "chat commands"), ("FAQ", "good to know"), ("DISCORD", "join the coven"), ("SPECS", "the machine")]


# ---------------------------------------------------------------- screens
def screen(art_cut, big, small, note=None, W=1920, H=1080):
    img = bg((W, H))
    fig = fit(art_cut, 900, 1100)
    img = put(img, fig, (W - fig.width - 30, H - fig.height + 30))
    img, _ = fit_title(img, big, (120, 520), 1000)
    divider(img, 120 + 360, 580, 360)
    img = label(img, small, (120, 650), 44, AMBER, anchor="left", track=12)
    if note:
        img = label(img, note, (120, 730), 30, SILVER_D, anchor="left", track=6)
    corner_brackets(img, 44, 120, AMBER + (255,), width=4)
    img = label(img, NAME, (120, 112), 34, SILVER, anchor="left", track=14)
    return img


# ---------------------------------------------------------------- overlay (cam + frame), transparent
def overlay(W=1920, H=1080):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), outline=DEEP + (255,), width=30)
    d.rectangle((26, 26, W - 26, H - 26), outline=AMBER + (255,), width=4)
    d.rectangle((34, 34, W - 34, H - 34), outline=INDIGO + (255,), width=3)
    corner_brackets(img, 56, 90, AMBER + (255,), width=4)
    # webcam
    cx0, cy0, cw, ch = 70, H - 500, 586, 330
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rectangle((cx0 - 18, cy0 - 18, cx0 + cw + 18, cy0 + ch + 18), fill=DEEP + (255,))
    pd.rectangle((cx0 - 18, cy0 - 18, cx0 + cw + 18, cy0 + ch + 18), outline=AMBER + (255,), width=5)
    pd.rectangle((cx0 - 8, cy0 - 8, cx0 + cw + 8, cy0 + ch + 8), outline=INDIGO + (255,), width=4)
    img = shadow(img, plate.split()[3], (0, 10), 14, (0, 0, 0), 0.6)
    img = Image.alpha_composite(img, plate)
    d = ImageDraw.Draw(img)
    d.rectangle((cx0, cy0, cx0 + cw, cy0 + ch), fill=(0, 0, 0, 0))
    hole = Image.new("L", (W, H), 255)
    ImageDraw.Draw(hole).rectangle((cx0, cy0, cx0 + cw, cy0 + ch), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], hole))
    # name plate under cam
    img = title(img, NAME, (cx0 + cw // 2, cy0 + ch + 78), 36, track=10)
    # chat box right
    chat = (W - 70 - 460, 120, W - 70, H - 250)
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(pl).rectangle((chat[0] - 12, chat[1] - 12, chat[2] + 12, chat[3] + 12), fill=DEEP + (210,), outline=AMBER + (255,), width=4)
    img = Image.alpha_composite(img, pl)
    img = title(img, "CHAT", (chat[0] + (chat[2] - chat[0]) // 2, chat[1] + 54), 36, track=16)
    divider(img, chat[0] + (chat[2] - chat[0]) // 2, chat[1] + 78, 150)
    # bottom bar
    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(bar).rectangle((720, H - 120, W - 70, H - 56), fill=DEEP + (225,), outline=AMBER + (255,), width=3)
    img = Image.alpha_composite(img, bar)
    img = label(img, "LATEST FOLLOWER", (750, H - 80), 22, AMBER, anchor="left", track=6)
    img = label(img, "LATEST SUB", (1200, H - 80), 22, AMBER, anchor="left", track=6)
    return img


# ---------------------------------------------------------------- banner 1200x480
def banner(art_cut, W=1200, H=480):
    img = bg((W, H))
    fig = fit(art_cut, 900, 540)
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    big = art_cut.resize((int(art_cut.width * 0.64), int(art_cut.height * 0.64)), Image.LANCZOS)
    lay.alpha_composite(big, (W - big.width + 120, -30))
    img = Image.alpha_composite(img, lay)
    img, _ = fit_title(img, NAME, (60, 230), 470, size=70, track=10)
    divider(img, 60 + 250, 266, 250)
    img = label(img, "WOW  ·  ART  ·  STREAMS", (60, 322), 24, AMBER, anchor="left", track=10)
    return img


# ---------------------------------------------------------------- alerts
def alert(art, head, sub, W=1000, H=340):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    plate = Image.new("L", (W, H), 0)
    ImageDraw.Draw(plate).polygon([(60, 30), (W - 40, 30), (W - 10, H // 2), (W - 40, H - 30), (60, H - 30), (30, H // 2)], fill=255)
    img = shadow(img, plate, (0, 10), 14, (0, 0, 0), 0.55)
    for inset, col in ((0, AMBER), (5, DEEP), (9, NIGHT)):
        lay = Image.new("RGBA", (W, H), col + (255,))
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([(60 + inset, 30 + inset), (W - 40 - inset, 30 + inset), (W - 10 - inset, H // 2), (W - 40 - inset, H - 30 - inset), (60 + inset, H - 30 - inset), (30 + inset, H // 2)], fill=255)
        lay.putalpha(m)
        img = Image.alpha_composite(img, lay)
    pic = circle_art(art, (322, 70, 690, 438), 230)
    ring = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((0, 0, 259, 259), fill=AMBER + (255,))
    rd.ellipse((6, 6, 253, 253), fill=DEEP + (255,))
    img.alpha_composite(ring, (62, 40))
    img.alpha_composite(pic, (77, 55))
    img = label(img, head, (350, 140), 30, AMBER, anchor="left", track=12)
    img = title(img, sub, (350, 226), 74 if len(sub) < 14 else 58, anchor="left", track=6)
    return img


# ---------------------------------------------------------------- badges and small icons
def badge_base(S=360):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S // 2
    for r, col in ((172, DEEP), (164, AMBER), (152, NIGHT)):
        d.ellipse((c - r, c - r, c + r, c + r), fill=col + (255,))
    return img


def gem(img, cx, cy, r, col):
    d = ImageDraw.Draw(img)
    hi = tuple(min(255, int(v * 1.35) + 25) for v in col)
    lo = tuple(int(v * 0.55) for v in col)
    d.polygon([(cx, cy - r), (cx + r * 0.8, cy - r * 0.1), (cx, cy + r), (cx - r * 0.8, cy - r * 0.1)], fill=col + (255,))
    d.polygon([(cx, cy - r), (cx + r * 0.8, cy - r * 0.1), (cx, cy - r * 0.1)], fill=hi + (255,))
    d.polygon([(cx, cy + r), (cx + r * 0.8, cy - r * 0.1), (cx, cy - r * 0.1)], fill=lo + (255,))
    d.polygon([(cx, cy - r), (cx + r * 0.8, cy - r * 0.1), (cx, cy + r), (cx - r * 0.8, cy - r * 0.1)], outline=DEEP + (255,), width=max(2, int(r * 0.06)))
    return img


def sub_badge(tier):
    S = 360
    img = badge_base(S)
    cols = [TEAL, VIOLET, AMBER, (222, 70, 96), SILVER, (255, 214, 120)]
    n = tier  # 0..5
    wl = wings((S, S), 190, 190, 0.3 + 0.0 * n, flip=True, alpha=255)
    wr = wings((S, S), S - 190, 190, 0.3)
    img = Image.alpha_composite(img, wl)
    img = Image.alpha_composite(img, wr)
    d = ImageDraw.Draw(img)
    c = S // 2
    d.ellipse((c - 58, c - 58, c + 58, c + 58), fill=DEEP + (255,), outline=AMBER + (255,), width=6)
    gem(img, c, c, 40, cols[n])
    for i in range(n):
        a = math.radians(-90 + (i - (n - 1) / 2) * 24)
        diamond(d, c + math.cos(a) * 128, c + math.sin(a) * 128 + 6, 9, AMBER + (255,))
    return img


def bits_badge(tier):
    S = 360
    img = badge_base(S)
    cols = [(150, 150, 170), TEAL, VIOLET, (222, 70, 96)]
    c = S // 2
    gem(img, c, c, 98 + tier * 6, cols[tier])
    return img


def emote_canvas(S=448):
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def outlined(img, mask_src, thick=14, col=DEEP):
    a = img.split()[3]
    big = a.filter(ImageFilter.MaxFilter(thick * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new("RGBA", img.size, col + (255,))
    base.putalpha(big)
    return Image.alpha_composite(base, img)


def emote_heart(S=448):
    img = emote_canvas(S)
    d = ImageDraw.Draw(img)
    c = S // 2
    pts = []
    for i in range(200):
        t = math.pi * 2 * i / 200
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((c + x * 9.4, c + 6 + y * 9.4))
    d.polygon(pts, fill=WINE + (255,))
    hl = [(c + (x - c) * 0.72, c + 6 + (y - c - 6) * 0.72 - 6) for x, y in pts]
    d.polygon(hl, fill=(190, 56, 88, 255))
    d.ellipse((c - 90, c - 98, c - 36, c - 62), fill=(236, 150, 170, 255))
    return outlined(img, None)


def emote_text(text, col1, col2, S=448, size=190):
    img = emote_canvas(S)
    m = text_mask((S, S), text, font(HEAD, size), (S // 2, S // 2 + size // 3), track=4)
    big = m.filter(ImageFilter.MaxFilter(25))
    ol = Image.new("RGBA", (S, S), DEEP + (255,))
    ol.putalpha(big)
    img = Image.alpha_composite(img, ol)
    img = fill_mask(img, m, col1, col2)
    return img


def emote_from_art(art, box, S=448):
    im = art.crop(box)
    im = fit(im, S - 40, S - 40).convert("RGBA")
    out = emote_canvas(S)
    out.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
    return outlined(out, None, 10)


def emote_gem(S=448, col=TEAL):
    img = emote_canvas(S)
    gem(img, S // 2, S // 2, 170, col)
    return outlined(img, None, 12)


def downsized(img, base):
    for s in (112, 56, 28):
        yield s, img.resize((s, s), Image.LANCZOS)


# ---------------------------------------------------------------- main
def main():
    art_cut = cutout(ART)
    art = art_cut
    OUT.mkdir(parents=True, exist_ok=True)
    art_cut.save(OUT / "character_cutout.png")
    # logo / emblem
    save(emblem(art, 2000, with_name=True), "Logo", "nightwing_logo.png")
    save(emblem(art, 1000), "Logo", "nightwing_emblem.png")
    # banner
    save(banner(art).convert("RGB"), "Banner", "profile_banner_1200x480.png")
    # panels
    for t, s in PANELS:
        save(panel(t, s), "Panels", t.lower() + ".png")
    # screens
    scr = [("STARTING SOON", "THE NIGHT BEGINS", "grab a drink and settle in", "starting_soon"), ("BE RIGHT BACK", "BACK IN A MOMENT", "stretching my wings", "brb"),
           ("THANKS FOR WATCHING", "SEE YOU NEXT TIME", "follow so you never miss a stream", "ending"), ("OFFLINE", "NOT STREAMING RIGHT NOW", "see you at the next stream", "offline")]
    for big, small, note, fn in scr:
        save(screen(art_cut, big, small, note).convert("RGB"), "Screens", fn + ".png")
    # overlay
    save(overlay(), "Overlay", "stream_overlay.png")
    # alerts
    for head, sub, fn in (("NEW FOLLOWER", "{name}", "follow"), ("NEW SUBSCRIBER", "{name}", "subscribe"), ("INCOMING RAID", "{name}", "raid"), ("DONATION", "{amount}", "donation"), ("BITS", "{amount}", "bits")):
        save(alert(art, head, sub), "Alerts", fn + ".png")
    # badges
    for i, m in enumerate((1, 3, 6, 12, 24, 36)):
        b = sub_badge(i)
        for s in (72, 36, 18):
            save(b.resize((s, s), Image.LANCZOS), "Badges", "Subscriber", "%dmonth_%d.png" % (m, s))
    for i, n in enumerate((1, 100, 1000, 10000)):
        b = bits_badge(i)
        for s in (72, 36, 18):
            save(b.resize((s, s), Image.LANCZOS), "Badges", "Bits", "bits%d_%d.png" % (n, s))
    # emotes
    emo = {"nw_heart": emote_heart(), "nw_gg": emote_text("GG", AMBER, AMBER_D), "nw_hype": emote_text("HYPE", SILVER, SILVER_D, size=130),
           "nw_eyes": emote_from_art(art, (425, 228, 590, 285)), "nw_lips": emote_from_art(art, (468, 288, 538, 306)),
           "nw_horns": emote_from_art(art, (320, 85, 640, 215)), "nw_gem": emote_gem(), "nw_wing": outlined(Image.alpha_composite(Image.alpha_composite(emote_canvas(), wings((448, 448), 224, 250, 0.52, flip=True)), wings((448, 448), 224, 250, 0.52)), None)}
    for n, im in emo.items():
        for s in (112, 56, 28):
            save(im.resize((s, s), Image.LANCZOS), "Emotes", "%s_%d.png" % (n, s))
    # channel points
    for n, im in (("gem", emote_gem(col=VIOLET)), ("heart", emote_heart()), ("wing", emo["nw_wing"])):
        save(im.resize((112, 112), Image.LANCZOS), "ChannelPoints", n + ".png")
    print("done")


if __name__ == "__main__":
    main()

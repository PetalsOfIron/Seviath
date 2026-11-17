#!/usr/bin/env python3
"""
Complete Twitch channel set in the style of the "Starting soon" screen: purple gradient, nested pink / violet
diamond lines, silver chains and strings of faceted gems. Everything is drawn here in code (no raster source),
so it stays sharp at any size.

    python tools/make_purple.py
"""
import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageSequence

from art import *  # noqa: F401,F403

OUT = ROOT / "images" / "twitch" / "Purple"
SS = 2

# palette (sampled from the Starting soon screen)
P_DARK, P_MID, P_LIGHT = (42, 8, 108), (74, 12, 138), (96, 20, 160)
PINK, MAGENTA, VIOLET, BLUE_V = (255, 70, 140), (236, 60, 190), (140, 40, 255), (96, 40, 220)
LAV, SILVER, SILVER_D = (236, 230, 252), (226, 222, 244), (150, 140, 190)
CORAL, CORAL_D, ROSE_BEAD = (236, 100, 84), (150, 40, 60), (244, 206, 214)
INK = (28, 4, 66)


def gradient_bg(size, left=P_DARK, right=P_LIGHT, glow=0.16):
    w, h = size
    t = np.linspace(0, 1, w)[None, :, None]
    base = np.array(left)[None, None, :] * (1 - t) + np.array(right)[None, None, :] * t
    base = np.repeat(base, h, axis=0)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w * 0.6)) ** 2 + ((yy - h / 2) / (h * 0.75)) ** 2)
    base = base + (np.clip(1 - r, 0, 1)[..., None] ** 2) * glow * 255 * np.array([0.35, 0.1, 0.6])
    return Image.fromarray(base.clip(0, 255).astype("uint8")).convert("RGBA")


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ---------------------------------------------------------------------------------------------- shapes

def on_layer(size, fn):
    """Draw fn(draw, S) on a transparent layer at SS x and return it at normal size."""
    layer = Image.new("RGBA", (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer), SS)
    return layer.resize(size, Image.LANCZOS)


def poly_pts(cx, cy, r, n, rot=0.0, sx=1.0, sy=1.0):
    return [(cx + math.cos(rot + 2 * math.pi * i / n) * r * sx, cy + math.sin(rot + 2 * math.pi * i / n) * r * sy) for i in range(n)]


def gem(d, cx, cy, r, base=CORAL, dark=CORAL_D, S=1):
    """Faceted octagonal gem lit from the upper left."""
    cx, cy, r = cx * S, cy * S, r * S
    rot = math.radians(22.5)
    outer = poly_pts(cx, cy, r, 8, rot)
    inner = poly_pts(cx, cy, r * 0.55, 8, rot)
    d.polygon(outer, fill=lerp(dark, base, 0.4), outline=INK + (255,), width=max(1, int(r * 0.06)))
    for i in range(8):
        a = rot + 2 * math.pi * (i + 0.5) / 8
        light = 0.5 + 0.5 * math.cos(a + math.radians(135))
        col = lerp(dark, (255, 220, 200), light * 0.9)
        d.polygon([outer[i], outer[(i + 1) % 8], inner[(i + 1) % 8], inner[i]], fill=col)
    d.polygon(inner, fill=lerp(base, (255, 235, 220), 0.35), outline=lerp(dark, base, 0.5) + (255,))
    for i in range(8):
        d.line([inner[i], outer[i]], fill=lerp(dark, base, 0.2) + (255,), width=max(1, int(r * 0.03)))
    d.ellipse((cx - r * 0.36, cy - r * 0.46, cx - r * 0.1, cy - r * 0.24), fill=(255, 255, 255, 190))
    d.polygon(outer, outline=INK + (255,), width=max(1, int(r * 0.07)))


def diamond_bead(d, cx, cy, w, h, col=ROSE_BEAD, S=1):
    cx, cy, w, h = cx * S, cy * S, w * S, h * S
    pts = [(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)]
    d.polygon(pts, fill=col, outline=(120, 70, 100, 255), width=max(1, int(w * 0.08)))
    d.polygon([pts[0], pts[1], (cx, cy)], fill=lerp(col, (255, 255, 255), 0.45))
    d.polygon([pts[3], pts[0], (cx, cy)], fill=lerp(col, (255, 255, 255), 0.25))
    d.polygon([pts[2], pts[3], (cx, cy)], fill=lerp(col, (90, 40, 70), 0.35))
    d.polygon([pts[1], pts[2], (cx, cy)], fill=lerp(col, (90, 40, 70), 0.2))


def ruby_oval(d, cx, cy, w, h, ang, S=1):
    cx, cy, w, h = cx * S, cy * S, w * S, h * S
    pts = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        x, y = math.cos(t) * w, math.sin(t) * h
        pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
    d.polygon(pts, fill=(214, 40, 90), outline=INK + (255,), width=max(1, int(w * 0.12)))
    d.ellipse((cx - w * 0.4, cy - h * 0.5, cx - w * 0.05, cy - h * 0.1), fill=(255, 190, 210, 200))


def chain(d, p0, p1, link=26, color=SILVER, edge=SILVER_D, width=5, S=1):
    """A silver chain between two points: long open links alternating with narrow edge-on links."""
    x0, y0, x1, y1 = p0[0] * S, p0[1] * S, p1[0] * S, p1[1] * S
    dist = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(dist / (link * S * 0.62)))
    ang = math.atan2(y1 - y0, x1 - x0)
    for i in range(n + 1):
        t = i / n
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if i % 2 == 0:
            a, b = link * S * 0.62, link * S * 0.34
            pts = []
            for k in range(28):
                u = 2 * math.pi * k / 28
                x, y = math.cos(u) * a, math.sin(u) * b
                pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
            d.line(pts + [pts[0]], fill=edge + (255,), width=int(width * S + 2 * S), joint="curve")
            d.line(pts + [pts[0]], fill=color + (255,), width=int(width * S), joint="curve")
        else:
            a, b = link * S * 0.36, link * S * 0.12
            ex, ey = math.cos(ang) * a, math.sin(ang) * a
            d.line([(cx - ex, cy - ey), (cx + ex, cy + ey)], fill=edge + (255,), width=int(width * S + 2 * S))
            d.line([(cx - ex, cy - ey), (cx + ex, cy + ey)], fill=color + (255,), width=int(width * S * 0.8))


def rhombus_pts(c, half):
    cx, cy = c
    return [(cx - half, cy), (cx, cy - half), (cx + half, cy), (cx, cy + half)]


def diamond_lines(canvas, center, half, specs, squash=1.0):
    """Nested rhombus outlines. specs = [(inset, width, colour)], drawn from outside in."""
    def fn(d, S):
        for inset, width, col in specs:
            pts = [((x - center[0]) * 1 + center[0], (y - center[1]) * squash + center[1]) for x, y in rhombus_pts(center, half - inset)]
            pts = [(x * S, y * S) for x, y in pts]
            d.line(pts + [pts[0], pts[1]], fill=col + (255,), width=int(width * S), joint="curve")
    return Image.alpha_composite(canvas, on_layer(canvas.size, fn))


FRAME_SPECS = [  # pink thin lines on the outside, thick violet lines inside - like the reference screen
    (0, 5, PINK), (11, 5, PINK), (22, 6, MAGENTA), (36, 5, (200, 60, 210)),
    (50, 22, VIOLET), (80, 14, BLUE_V), (100, 20, VIOLET), (130, 8, (176, 120, 255)),
]


def bead_string(canvas, p0, p1, gap=64, S0=1.0):
    """A thread with gems, diamond beads and rubies along it."""
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(dist / gap))
    ang = math.atan2(y1 - y0, x1 - x0)
    pattern = ["gem", "dia", "ruby", "dia"]

    def fn(d, S):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=(150, 100, 80, 255), width=int(2 * S * S0 + 1))
        for i in range(n + 1):
            t = i / n
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            kind = pattern[i % 4]
            if kind == "gem":
                gem(d, cx, cy, 26 * S0, S=S)
            elif kind == "dia":
                diamond_bead(d, cx, cy, 14 * S0, 22 * S0, S=S)
            else:
                ruby_oval(d, cx, cy, 9 * S0, 17 * S0, ang + math.pi / 2, S=S)

    return Image.alpha_composite(canvas, on_layer(canvas.size, fn))


def text_blackletter(canvas, text, center, size, fill=(238, 232, 252), grad_to=(200, 190, 240), track=0):
    f = font("OLDENGL.TTF", size)
    m = text_mask(canvas.size, text, f, center, track=track)
    canvas = shadow(canvas, m, (0, max(4, size // 24)), max(6, size // 20), (12, 0, 40), 0.7)
    return fill_mask(canvas, m, fill, grad_to)


def pill_text(canvas, text, center, size, fnt="georgiai.ttf", fill=LAV, track=2):
    return fill_mask(canvas, text_mask(canvas.size, text, font(fnt, size), center, track=track), fill)


# ----------------------------------------------------------------------------------------------- screens

def screen(title, subtitle):
    W, H = 1920, 1080
    canvas = gradient_bg((W, H))
    c = (W // 2, H // 2)
    canvas = diamond_lines(canvas, c, 880, FRAME_SPECS)

    def chains(d, S):
        for off in (0, 20):
            pts = rhombus_pts(c, 560 - off)
            pts = [(x * S, y * S) for x, y in pts]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                chain(d, (a[0] / S, a[1] / S), (b[0] / S, b[1] / S), link=24, width=4, S=S)
    canvas = Image.alpha_composite(canvas, on_layer(canvas.size, chains))
    for p0, p1 in (((0, 400), (400, 0)), ((W - 400, 0), (W, 400)), ((0, H - 400), (400, H)), ((W - 400, H), (W, H - 400))):
        canvas = bead_string(canvas, p0, p1)
    canvas = text_blackletter(canvas, title, (c[0], c[1] + 70), 170 if len(title) < 12 else 150)
    canvas = pill_text(canvas, subtitle, (c[0], c[1] + 190), 46)
    return grain(canvas, 8)


def banner():
    W, H = 3000, 1000
    canvas = gradient_bg((W, H))
    for cx in (330, W - 330):
        canvas = diamond_lines(canvas, (cx, H // 2), 700, FRAME_SPECS)
    canvas = glow(canvas, (700, 100, 2300, 900), (130, 60, 255), blur=170, alpha=70)
    for p0, p1 in (((900, 0), (500, 400)), ((W - 500, 600), (W - 900, 1000)), ((900, 1000), (1300, 600)), ((W - 900, 0), (W - 1300, 400))):
        canvas = bead_string(canvas, p0, p1, gap=70, S0=0.9)

    def chains(d, S):
        for y in (86, H - 86):
            chain(d, (860, y), (W - 860, y), link=26, width=4, S=S)
    canvas = Image.alpha_composite(canvas, on_layer(canvas.size, chains))
    canvas = text_blackletter(canvas, "Petals Of Iron", (W // 2, 520), 300)
    d = ImageDraw.Draw(canvas)
    diamond(d, W // 2, 610, 16, PINK + (255,))
    d.line([(W // 2 - 520, 610), (W // 2 - 40, 610)], fill=PINK + (255,), width=4)
    d.line([(W // 2 + 40, 610), (W // 2 + 520, 610)], fill=PINK + (255,), width=4)
    canvas = pill_text(canvas, "Gamer  -  Streamer  -  Artist", (W // 2, 740), 84, track=6)
    return grain(canvas, 8)


def logo():
    S = 2000
    canvas = gradient_bg((S, S), P_DARK, P_MID, glow=0.2)
    cx, cy, D = 1000, 800, 1400
    disc = gradient_bg((S, S), P_MID, P_LIGHT, glow=0.3)
    m = Image.new("L", (S * 3, S * 3), 0)
    ImageDraw.Draw(m).ellipse(((cx - D / 2) * 3, (cy - D / 2) * 3, (cx + D / 2) * 3, (cy + D / 2) * 3), fill=255)
    m = m.resize((S, S), Image.LANCZOS)
    canvas = shadow(canvas, m, (0, 22), 30, (0, 0, 20), 0.6)
    canvas = Image.composite(disc, canvas, m)
    canvas = diamond_lines(canvas, (cx, cy), 560, [(0, 6, PINK), (16, 6, MAGENTA), (32, 18, VIOLET), (62, 10, BLUE_V)])

    def rings(d, S_):
        for r, w, col in ((D / 2 - 6, 12, PINK), (D / 2 - 30, 8, MAGENTA), (D / 2 - 58, 20, VIOLET)):
            d.ellipse(((cx - r) * S_, (cy - r) * S_, (cx + r) * S_, (cy + r) * S_), outline=col + (255,), width=int(w * S_))
        n = 120
        for ring_r, off in ((D / 2 - 100, 0), (D / 2 - 126, 0)):
            pts = [(cx + math.cos(2 * math.pi * i / n) * ring_r, cy + math.sin(2 * math.pi * i / n) * ring_r) for i in range(n + 1)]
            for a, b in zip(pts[:-1:2], pts[1::2]):
                chain(d, a, b, link=22, width=4, S=S_)
        for ang in (-90, 0, 90, 180):
            a = math.radians(ang)
            gem(d, cx + math.cos(a) * (D / 2 - 10), cy + math.sin(a) * (D / 2 - 10), 68, S=S_)
    canvas = Image.alpha_composite(canvas, on_layer(canvas.size, rings))
    canvas = text_blackletter(canvas, "P", (cx, cy + 270), 720, fill=(246, 242, 255), grad_to=(206, 196, 246))
    canvas = text_blackletter(canvas, "Petals Of Iron", (cx, 1790), 215)
    d = ImageDraw.Draw(canvas)
    d.line([(560, 1872), (940, 1872)], fill=PINK + (255,), width=4)
    d.line([(1060, 1872), (1440, 1872)], fill=PINK + (255,), width=4)
    diamond(d, 1000, 1872, 15, PINK + (255,))
    return grain(canvas, 8)


# ----------------------------------------------------------------------------------------------- panels

PANELS = ["About me", "Schedule", "Chat rules", "Donation", "FAQ", "PC setup", "Links", "Socials"]


def panel(title):
    W, H = 1280, 400
    canvas = gradient_bg((W, H), P_DARK, P_LIGHT, glow=0.1)

    def fn(d, S):
        d.rounded_rectangle((14 * S, 14 * S, (W - 14) * S, (H - 14) * S), radius=56 * S, outline=PINK + (255,), width=int(6 * S))
        d.rounded_rectangle((34 * S, 34 * S, (W - 34) * S, (H - 34) * S), radius=40 * S, outline=VIOLET + (255,), width=int(16 * S))
        for off in (0, 14):
            chain(d, (110, 62 + off * 0), (W - 110, 62), link=22, width=3, S=S) if off == 0 else None
            chain(d, (110, H - 62), (W - 110, H - 62), link=22, width=3, S=S) if off == 0 else None
        gem(d, 150, H / 2, 70, S=S)
        diamond_bead(d, W - 150, H / 2, 26, 44, S=S)
    canvas = Image.alpha_composite(canvas, on_layer(canvas.size, fn))
    canvas = text_blackletter(canvas, title, (W / 2 + 20, H / 2 + 52), 150)
    return grain(canvas, 6)


# ----------------------------------------------------------------------------------------------- emotes etc.

def heart_pts(cx, cy, s, n=80):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s, cy + y * s))
    return pts


def sparkle_pts(cx, cy, r, n=4, inner=0.28):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = -math.pi / 2 + math.pi * i / n
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


def shaded_poly(d, pts, base, dark, S, cx, cy):
    d.polygon([(x * S, y * S) for x, y in pts], fill=lerp(dark, base, 0.6), outline=INK + (255,), width=int(5 * S))


def emote(kind, size=448):
    def fn(d, S):
        k = size / 448
        cx, cy = 224 * k, 224 * k
        if kind == "gem":
            gem(d, cx, cy, 190 * k, S=S)
        elif kind == "ruby":
            gem(d, cx, cy, 190 * k, base=(230, 40, 90), dark=(110, 10, 50), S=S)
        elif kind == "amethyst":
            gem(d, cx, cy, 190 * k, base=(170, 90, 255), dark=(70, 20, 150), S=S)
        elif kind == "diamond":
            diamond_bead(d, cx, cy, 130 * k, 190 * k, col=(222, 214, 252), S=S)
        elif kind == "heart":
            pts = [(x * S, y * S) for x, y in heart_pts(cx, cy + 6 * k, 11.4 * k)]
            d.polygon(pts, fill=(236, 70, 150), outline=INK + (255,), width=int(9 * k * S))
            d.polygon([(x * S, y * S) for x, y in heart_pts(cx - 8 * k, cy - 6 * k, 8.4 * k)], fill=(255, 130, 190))
            d.ellipse(((cx - 110 * k) * S, (cy - 100 * k) * S, (cx - 60 * k) * S, (cy - 62 * k) * S), fill=(255, 235, 245, 210))
            d.polygon(pts, outline=INK + (255,), width=int(9 * k * S))
        elif kind == "sparkle":
            d.polygon([(x * S, y * S) for x, y in sparkle_pts(cx, cy, 200 * k)], fill=(255, 226, 150), outline=INK + (255,), width=int(9 * k * S))
            d.polygon([(x * S, y * S) for x, y in sparkle_pts(cx, cy, 120 * k)], fill=(255, 250, 220))
            d.polygon([(x * S, y * S) for x, y in sparkle_pts(cx + 130 * k, cy - 130 * k, 50 * k)], fill=(255, 226, 150), outline=INK + (255,), width=int(5 * k * S))
        elif kind == "crown":
            pts = [(70, 330), (70, 150), (146, 230), (224, 110), (302, 230), (378, 150), (378, 330)]
            pts = [(x * k * S, y * k * S) for x, y in pts]
            d.polygon(pts, fill=(255, 205, 90), outline=INK + (255,), width=int(9 * k * S))
            d.rectangle((70 * k * S, 300 * k * S, 378 * k * S, 350 * k * S), fill=(214, 150, 40), outline=INK + (255,), width=int(9 * k * S))
            for gx in (146, 224, 302):
                gem(d, gx * k, 322 * k, 18 * k, S=S)
            for gx, gy in ((70, 150), (224, 110), (378, 150)):
                d.ellipse(((gx - 20) * k * S, (gy - 20) * k * S, (gx + 20) * k * S, (gy + 20) * k * S), fill=(255, 120, 190), outline=INK + (255,), width=int(5 * k * S))
        elif kind in ("gg", "hype"):
            d.ellipse((24 * k * S, 24 * k * S, 424 * k * S, 424 * k * S), fill=(96, 20, 160), outline=INK + (255,), width=int(10 * k * S))
            d.ellipse((46 * k * S, 46 * k * S, 402 * k * S, 402 * k * S), outline=PINK + (255,), width=int(8 * k * S))
            d.ellipse((72 * k * S, 72 * k * S, 376 * k * S, 376 * k * S), outline=VIOLET + (255,), width=int(14 * k * S))
    layer = on_layer((size, size), fn)
    if kind in ("gg", "hype"):
        t = "GG" if kind == "gg" else "HYPE"
        f = font("OLDENGL.TTF", int(170 * size / 448) if kind == "gg" else int(112 * size / 448))
        m = text_mask((size, size), t, f, (size / 2, size * 0.64))
        layer = shadow(layer, m, (0, 4), 4, (10, 0, 30), 0.7)
        layer = fill_mask(layer, m, (246, 242, 255), (206, 196, 246))
    return layer


EMOTES = ["gem", "ruby", "amethyst", "diamond", "heart", "sparkle", "crown", "gg", "hype"]


def medallion(inner, ring_cols, size=432, beads=0):
    """Round badge: purple plate, coloured rings, optional beads, and an inner symbol drawn by `inner`."""
    def fn(d, S):
        k = size / 432
        c = size / 2
        d.ellipse((6 * S, 6 * S, (size - 6) * S, (size - 6) * S), fill=(70, 12, 140), outline=INK + (255,), width=int(8 * k * S))
        for i, col in enumerate(ring_cols):
            r = size / 2 - (14 + i * 18) * k
            d.ellipse(((c - r) * S, (c - r) * S, (c + r) * S, (c + r) * S), outline=col + (255,), width=int(10 * k * S))
        for i in range(beads):
            a = 2 * math.pi * i / beads - math.pi / 2
            r = size / 2 - 14 * k
            gem(d, c + math.cos(a) * r, c + math.sin(a) * r, 11 * k, S=S)
        inner(d, S, c, k)
    return on_layer((size, size), fn)


BADGES = [("base", 0, [SILVER]), ("3month", 3, [PINK]), ("6month", 6, [PINK, VIOLET]), ("9month", 9, [MAGENTA, VIOLET]),
          ("1year", 12, [PINK, VIOLET, SILVER]), ("2year", 12, [(255, 214, 120), PINK, VIOLET]), ("3year", 12, [(255, 214, 120), (255, 214, 120), PINK])]


def badge(tier):
    name, beads, rings = tier
    n_gems = {"base": 1, "3month": 1, "6month": 1, "9month": 1, "1year": 1, "2year": 1, "3year": 1}[name]
    base = {"base": (200, 190, 240), "3month": CORAL, "6month": (236, 70, 150), "9month": (170, 90, 255),
            "1year": (230, 40, 90), "2year": (255, 200, 90), "3year": (255, 230, 150)}[name]
    dark = tuple(int(c * 0.4) for c in base)

    def inner(d, S, c, k):
        gem(d, c, c, 120 * k, base=base, dark=dark, S=S)
    return medallion(inner, rings, beads=max(beads // 1, 0) if beads else 0)


POINTS = ["heart", "sparkle", "crown", "gem"]


def point_icon(kind):
    def inner(d, S, c, k):
        pts = None
        if kind == "heart":
            d.polygon([(x * S, y * S) for x, y in heart_pts(c, c + 4 * k, 6.6 * k)], fill=(236, 70, 150), outline=INK + (255,), width=int(6 * k * S))
        elif kind == "sparkle":
            d.polygon([(x * S, y * S) for x, y in sparkle_pts(c, c, 124 * k)], fill=(255, 226, 150), outline=INK + (255,), width=int(6 * k * S))
        elif kind == "crown":
            p = [(c - 110 * k, c + 80 * k), (c - 110 * k, c - 60 * k), (c - 55 * k, c + 5 * k), (c, c - 90 * k), (c + 55 * k, c + 5 * k), (c + 110 * k, c - 60 * k), (c + 110 * k, c + 80 * k)]
            d.polygon([(x * S, y * S) for x, y in p], fill=(255, 205, 90), outline=INK + (255,), width=int(6 * k * S))
        else:
            gem(d, c, c, 110 * k, S=S)
    return medallion(inner, [PINK, VIOLET])


def flair(tier):
    def inner(d, S, c, k):
        if tier == 2:
            gem(d, c, c, 110 * k, base=(170, 90, 255), dark=(70, 20, 150), S=S)
        else:
            p = [(c - 110 * k, c + 80 * k), (c - 110 * k, c - 60 * k), (c - 55 * k, c + 5 * k), (c, c - 90 * k), (c + 55 * k, c + 5 * k), (c + 110 * k, c - 60 * k), (c + 110 * k, c + 80 * k)]
            d.polygon([(x * S, y * S) for x, y in p], fill=(255, 205, 90), outline=INK + (255,), width=int(6 * k * S))
    return medallion(inner, [(255, 214, 120), PINK] if tier == 3 else [PINK, VIOLET], beads=8)


# ------------------------------------------------------------------------------------------- alert + overlay

def alert_frames(text="Thanks for the follow!", n=24):
    W, H = 800, 360
    base = gradient_bg((W, H), P_DARK, P_LIGHT, glow=0.12)

    def fn(d, S):
        d.rounded_rectangle((8 * S, 8 * S, (W - 8) * S, (H - 8) * S), radius=40 * S, outline=PINK + (255,), width=int(5 * S))
        d.rounded_rectangle((22 * S, 22 * S, (W - 22) * S, (H - 22) * S), radius=30 * S, outline=VIOLET + (255,), width=int(12 * S))
        chain(d, (70, 52), (W - 70, 52), link=20, width=3, S=S)
        chain(d, (70, H - 52), (W - 70, H - 52), link=20, width=3, S=S)
        gem(d, 80, H / 2, 38, S=S)
        gem(d, W - 80, H / 2, 38, S=S)
    base = Image.alpha_composite(base, on_layer(base.size, fn))
    f = font("OLDENGL.TTF", 96)
    m = text_mask((W, H), text, f, (W / 2, H / 2 + 34))
    base = shadow(base, m, (0, 4), 6, (10, 0, 30), 0.7)
    base = fill_mask(base, m, (246, 242, 255), (206, 196, 246))
    frames = []
    for i in range(n):
        shine = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x = -200 + (W + 400) * i / (n - 1)
        ImageDraw.Draw(shine).polygon([(x, 0), (x + 70, 0), (x - 70, H), (x - 140, H)], fill=(255, 255, 255, 90))
        shine = shine.filter(ImageFilter.GaussianBlur(10))
        text_only = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        text_only.putalpha(m)
        sh = ImageChops.multiply(shine.split()[3], Image.new("L", (W, H), 255))
        frame = Image.alpha_composite(base, Image.composite(shine, Image.new("RGBA", (W, H), (0, 0, 0, 0)), m.point(lambda v: 255 if v > 20 else 0)))
        frames.append(frame)
    return frames


def overlay_frame():
    W, H = 1920, 1080
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def fn(d, S):
        d.rounded_rectangle((10 * S, 10 * S, (W - 10) * S, (H - 10) * S), radius=40 * S, outline=PINK + (255,), width=int(6 * S))
        d.rounded_rectangle((26 * S, 26 * S, (W - 26) * S, (H - 26) * S), radius=30 * S, outline=VIOLET + (255,), width=int(18 * S))
        d.rounded_rectangle((46 * S, 46 * S, (W - 46) * S, (H - 46) * S), radius=22 * S, outline=BLUE_V + (255,), width=int(6 * S))
        for x, y in ((10, 10), (W - 10, 10), (10, H - 10), (W - 10, H - 10)):
            gem(d, x, y, 40, S=S)
        for x in (W // 2,):
            diamond_bead(d, x, 12, 22, 34, S=S)
            diamond_bead(d, x, H - 12, 22, 34, S=S)
        # webcam window, bottom left
        cx0, cy0, cx1, cy1 = 60, H - 60 - 300, 60 + 533, H - 60
        d.rounded_rectangle((cx0 * S, cy0 * S, cx1 * S, cy1 * S), radius=24 * S, outline=PINK + (255,), width=int(6 * S))
        d.rounded_rectangle(((cx0 - 12) * S, (cy0 - 12) * S, (cx1 + 12) * S, (cy1 + 12) * S), radius=30 * S, outline=VIOLET + (255,), width=int(10 * S))
        chain(d, (cx0 + 30, cy0 - 26), (cx1 - 30, cy0 - 26), link=20, width=3, S=S)
        gem(d, cx0 - 4, cy0 - 4, 24, S=S)
        gem(d, cx1 + 4, cy0 - 4, 24, S=S)
    layer = on_layer(canvas.size, fn)
    # cut the webcam window out so the camera shows through
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rounded_rectangle((60, H - 360, 593, H - 60), radius=24, fill=0)
    a = ImageChops.multiply(layer.split()[3], cut)
    layer.putalpha(ImageChops.lighter(a, layer.split()[3].point(lambda v: v)) if False else a)
    return layer


def save(img, path, rgba=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    (img if rgba else img.convert("RGB")).save(path, optimize=True)
    print("Saved", path.relative_to(ROOT))


def main():
    save(screen("Be right back", "I will be back in a moment"), OUT / "Screens" / "purple_be_right_back.png")
    save(screen("Offline", "Thank you for watching - see you next stream"), OUT / "Screens" / "purple_offline.png")
    save(logo(), OUT / "Logo" / "purple_logo.png")
    save(banner(), OUT / "Banner" / "purple_banner.png")
    for t in PANELS:
        save(panel(t), OUT / "Panels" / f"{t.lower().replace(' ', '_')}.png")
    for e in EMOTES:
        for s in (448, 112, 56, 28):
            save(emote(e, s), OUT / "Emotes" / f"{e}_{s}.png", rgba=True)
    for t in BADGES:
        save(badge(t), OUT / "Badges" / f"{t[0]}_432.png", rgba=True)
    for k in POINTS:
        save(point_icon(k), OUT / "Points" / f"points_{k}_432.png", rgba=True)
    for t in (2, 3):
        save(flair(t), OUT / "Flair" / f"tier{t}_flair_432.png", rgba=True)
    save(overlay_frame(), OUT / "Overlay" / "purple_overlay_frame.png", rgba=True)
    frames = alert_frames()
    p = OUT / "Alert" / "purple_alert.gif"
    p.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=50, disposal=2, loop=0, optimize=False)
    print("Saved", p.relative_to(ROOT))


if __name__ == "__main__":
    main()

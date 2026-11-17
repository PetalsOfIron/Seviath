#!/usr/bin/env python3
"""
Themed emotes: every set gets its OWN list of emotes (different ideas, not the same faces recoloured).
Each emote is the set's mascot (cut from that set's artwork) plus a prop that belongs to the set's world.
Replaces the generic emote files of the nine sets. Three emotes per set animate (loop).

    python tools/make_emotes.py            # all sets
    python tools/make_emotes.py Tessel
"""
import math
import shutil
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

from art import *  # noqa: F401,F403
import make_rose as mr
import make_sets as ms

TW = ROOT / "images" / "twitch"

# (file name, mood, prop, animation)
THEMES = {
    "Hood": [("hype", "party", "headset", "bounce"), ("controller", "smile", "controller", None), ("sword_up", "angry", "sword", "shake"), ("shield_up", "cool", "shield", None),
             ("coffee_break", "sleepy", "coffee", None), ("headset", "party", "headset", "bounce"), ("lightning", "surprise", "bolt", None),
             ("night_owl", "sleepy", "moon", None), ("gg_hood", "laughing", "gg", None), ("heart_hood", "lovely", "heart", "sway")],
    "Helmet": [("hype", "party", "flame", "bounce"), ("sword_salute", "angry", "sword", "shake"), ("crown_gold", "cool", "crown", None), ("shield_wall", "smile", "shield", None),
               ("victory", "party", "trophy", "bounce"), ("war_cry", "laughing", "flame", None), ("gold_coin", "lovely", "coin", None),
               ("horn", "surprise", "horn", None), ("rest_knight", "sleepy", "moon", "sway"), ("gg_helmet", "smile", "gg", None)],
    "Slash": [("hype", "party", "burst", "bounce"), ("speed", "angry", "bolt", "shake"), ("flame_on", "laughing", "flame", None), ("boom", "surprise", "burst", None),
              ("star_hit", "party", "star", "bounce"), ("cool_slash", "cool", "headset", None), ("slash_heart", "lovely", "heart", None),
              ("knocked_out", "cry", "stars", None), ("rage", "angry", "flame", None), ("gg_slash", "smile", "gg", "sway")],
    "Snake": [("hype", "party", "sun", "bounce"), ("hiss", "angry", "tongue", "shake"), ("coil_hug", "lovely", "heart", None), ("shed_skin", "surprise", "leaf", None),
              ("sun_nap", "sleepy", "sun", "sway"), ("egg_hatch", "party", "egg", "bounce"), ("venom", "mad", "drop", None),
              ("scale_shine", "cool", "star", None), ("tongue_flick", "laughing", "tongue", None), ("gg_snake", "smile", "gg", None)],
    "Floral": [("hype", "party", "flower", "bounce"), ("bloom", "joyful", "flower", "bounce"), ("petal_rain", "lovely", "petals", None), ("bee", "smile", "bee", "sway"),
               ("water_me", "cry", "drop", None), ("sunbathe", "cool", "sun", None), ("bouquet", "party", "bouquet", None),
               ("sleepy_bud", "sleepy", "moon", None), ("wilted", "sad", "leaf", None), ("gg_flower", "laughing", "gg", None)],
    "Tessel": [("hype", "party", "trophy", "bounce"), ("goal", "party", "ball", "bounce"), ("red_card", "angry", "redcard", "shake"), ("whistle", "surprise", "whistle", None),
               ("trophy_tessel", "laughing", "trophy", None), ("boot_up", "cool", "boot", None), ("tired_legs", "sleepy", "coffee", "sway"),
               ("corner_flag", "smile", "flag", None), ("cheer", "joyful", "heart", None), ("gg_pitch", "smile", "gg", None)],
    "Perfum": [("hype", "party", "sparkle", "bounce"), ("spritz", "party", "spray", "bounce"), ("rose_gift", "lovely", "rose", None), ("sparkle_scent", "sparkly", "sparkle", None),
               ("sweet_dreams", "sleepy", "moon", "sway"), ("gold_cap", "cool", "crown", None), ("blush_pink", "joyful", "petals", None),
               ("fresh", "laughing", "drop", None), ("luxury", "smile", "gem", None), ("gg_perfum", "smile", "gg", None)],
    "Northbeam": [("hype", "party", "beam", "bounce"), ("beam_on", "party", "beam", "bounce"), ("north_star", "sparkly", "star", None), ("compass", "smile", "compass", "sway"),
                  ("aurora", "joyful", "aurora", None), ("frost", "cool", "snow", None), ("summit", "laughing", "flag", None),
                  ("lost", "surprise", "question", None), ("night_watch", "sleepy", "moon", None), ("gg_north", "smile", "gg", None)],
    "Strikeline": [("hype", "party", "scoreboard", "bounce"), ("strike", "angry", "ball", "shake"), ("offside", "surprise", "flag", None), ("captain", "cool", "armband", None),
                   ("score", "party", "scoreboard", "bounce"), ("whistle_s", "laughing", "whistle", None), ("sub_in", "joyful", "arrow", None),
                   ("final_whistle", "sleepy", "whistle", "sway"), ("crest_love", "lovely", "heart", None), ("gg_strike", "smile", "gg", None)],
}


def prop(d, S, kind, cx, cy, r, C):
    """Draw a prop around the mascot (face centre cx, cy and radius r), set colours from C."""
    ink = C["ink"] + (255,)
    a, m = C["accent"] + (255,), C["main"] + (255,)
    w = max(1, int(r * 0.05 * S))
    X = lambda x: x * S
    gold, white = (255, 214, 96, 255), (255, 255, 255, 255)

    def poly(pts, fill):
        d.polygon([(X(x), X(y)) for x, y in pts], fill=fill, outline=ink, width=w)

    def disc(x, y, rr, fill):
        d.ellipse((X(x - rr), X(y - rr), X(x + rr), X(y + rr)), fill=fill, outline=ink, width=w)

    rx, ry = cx + r * 0.98, cy - r * 0.62
    if kind == "heart":
        mr.heart(d, S, rx, ry, r * 0.026)
    elif kind in ("star", "sparkle"):
        mr.sparkle(d, S, rx, ry, r * 0.34)
        mr.sparkle(d, S, cx - r * 1.0, cy - r * 0.5, r * 0.2)
    elif kind == "stars":
        for i in range(3):
            mr.sparkle(d, S, cx + (i - 1) * r * 0.5, cy - r * 1.18 + abs(i - 1) * 8, r * 0.16)
    elif kind == "moon":
        d.pieslice((X(rx - r * 0.22), X(ry - r * 0.3), X(rx + r * 0.3), X(ry + r * 0.3)), 90, 270, fill=gold, outline=ink, width=w)
        mr.sparkle(d, S, rx + r * 0.1, ry + r * 0.45, r * 0.1)
    elif kind == "sun":
        for i in range(10):
            ang = 2 * math.pi * i / 10
            d.line([(X(rx + math.cos(ang) * r * 0.32), X(ry + math.sin(ang) * r * 0.32)), (X(rx + math.cos(ang) * r * 0.46), X(ry + math.sin(ang) * r * 0.46))], fill=gold, width=w)
        disc(rx, ry, r * 0.26, gold)
    elif kind == "bolt":
        poly([(rx, ry - r * 0.4), (rx - r * 0.24, ry + r * 0.06), (rx - r * 0.02, ry + r * 0.06), (rx - r * 0.12, ry + r * 0.46), (rx + r * 0.26, ry - r * 0.1), (rx + r * 0.04, ry - r * 0.1)], gold)
    elif kind in ("flame", "burst"):
        pts = []
        for i in range(14):
            ang = 2 * math.pi * i / 14
            rr = r * (0.42 if i % 2 == 0 else 0.22)
            pts.append((rx + math.cos(ang) * rr, ry + math.sin(ang) * rr))
        poly(pts, (255, 140, 40, 255) if kind == "flame" else (255, 226, 96, 255))
    elif kind == "sword":
        poly([(cx + r * 0.9, cy + r * 0.9), (cx + r * 1.0, cy - r * 0.95), (cx + r * 1.12, cy + r * 0.9)], (226, 230, 238, 255))
        d.rectangle((X(cx + r * 0.78), X(cy + r * 0.86), X(cx + r * 1.24), X(cy + r * 0.96)), fill=a, outline=ink, width=w)
        d.rectangle((X(cx + r * 0.96), X(cy + r * 0.96), X(cx + r * 1.06), X(cy + r * 1.2)), fill=m, outline=ink, width=w)
    elif kind == "shield":
        pts = [(rx - r * 0.3, ry - r * 0.1), (rx + r * 0.3, ry - r * 0.1), (rx + r * 0.3, ry + r * 0.2), (rx, ry + r * 0.55), (rx - r * 0.3, ry + r * 0.2)]
        poly(pts, m)
        d.line([(X(rx), X(ry - r * 0.05)), (X(rx), X(ry + r * 0.45))], fill=a, width=w * 2)
    elif kind == "crown":
        poly([(cx - r * 0.46, cy - r * 0.98), (cx - r * 0.46, cy - r * 1.42), (cx - r * 0.23, cy - r * 1.2), (cx, cy - r * 1.55), (cx + r * 0.23, cy - r * 1.2), (cx + r * 0.46, cy - r * 1.42), (cx + r * 0.46, cy - r * 0.98)], gold)
    elif kind == "trophy":
        d.pieslice((X(rx - r * 0.3), X(ry - r * 0.3), X(rx + r * 0.3), X(ry + r * 0.3)), 0, 180, fill=gold, outline=ink, width=w)
        d.rectangle((X(rx - r * 0.05), X(ry), X(rx + r * 0.05), X(ry + r * 0.3)), fill=gold, outline=ink, width=w)
        d.rectangle((X(rx - r * 0.2), X(ry + r * 0.3), X(rx + r * 0.2), X(ry + r * 0.4)), fill=gold, outline=ink, width=w)
    elif kind == "coin":
        disc(rx, ry + r * 0.1, r * 0.28, gold)
        d.ellipse((X(rx - r * 0.16), X(ry + r * 0.1 - r * 0.16), X(rx + r * 0.16), X(ry + r * 0.1 + r * 0.16)), outline=ink, width=w)
    elif kind == "horn":
        poly([(rx - r * 0.35, ry + r * 0.35), (rx + r * 0.35, ry - r * 0.35), (rx + r * 0.42, ry - r * 0.05), (rx - r * 0.05, ry + r * 0.4)], (240, 228, 200, 255))
    elif kind == "controller":
        d.rounded_rectangle((X(rx - r * 0.45), X(ry - r * 0.18), X(rx + r * 0.45), X(ry + r * 0.2)), radius=int(r * 0.2 * S), fill=(110, 80, 120, 255), outline=ink, width=w)
        disc(rx - r * 0.24, ry, r * 0.07, white); disc(rx + r * 0.2, ry - r * 0.05, r * 0.05, white); disc(rx + r * 0.3, ry + r * 0.05, r * 0.05, white)
    elif kind == "headset":
        d.arc((X(cx - r * 0.98), X(cy - r * 1.0), X(cx + r * 0.98), X(cy + r * 0.8)), 190, 350, fill=ink, width=int(r * 0.1 * S))
        for sx in (-1, 1):
            d.rounded_rectangle((X(cx + sx * r * 0.98 - r * 0.12), X(cy - r * 0.2), X(cx + sx * r * 0.98 + r * 0.12), X(cy + r * 0.28)), radius=int(r * 0.06 * S), fill=m, outline=ink, width=w)
    elif kind == "coffee":
        d.rounded_rectangle((X(rx - r * 0.25), X(ry), X(rx + r * 0.2), X(ry + r * 0.42)), radius=int(r * 0.06 * S), fill=(250, 244, 236, 255), outline=ink, width=w)
        d.arc((X(rx + r * 0.1), X(ry + r * 0.08), X(rx + r * 0.36), X(ry + r * 0.32)), 270, 90, fill=ink, width=w)
        d.arc((X(rx - r * 0.12), X(ry - r * 0.28), X(rx + r * 0.0), X(ry - r * 0.04)), 90, 270, fill=ink, width=w)
    elif kind == "gg":
        f = font("impact.ttf", int(r * 0.5)) if False else ImageFont.truetype(str(FONTS / "impact.ttf"), int(r * 0.5 * S))
        d.rounded_rectangle((X(rx - r * 0.32), X(ry - r * 0.22), X(rx + r * 0.32), X(ry + r * 0.22)), radius=int(r * 0.08 * S), fill=m, outline=ink, width=w)
        d.text((X(rx), X(ry)), "GG", font=f, fill=white, anchor="mm")
    elif kind in ("tongue",):
        d.rounded_rectangle((X(cx - r * 0.06), X(cy + r * 0.42), X(cx + r * 0.06), X(cy + r * 0.86)), radius=int(r * 0.05 * S), fill=(236, 70, 110, 255))
        poly([(cx, cy + r * 0.86), (cx - r * 0.12, cy + r * 1.02), (cx, cy + r * 0.94), (cx + r * 0.12, cy + r * 1.02)], (236, 70, 110, 255))
    elif kind == "leaf":
        mr.leaf(d, S, rx - r * 0.2, ry + r * 0.2, r * 0.6, r * 0.18, math.radians(-40), fill=(90, 190, 110), outline=C["ink"], lw=int(r * 0.05))
    elif kind == "drop":
        pts = [(rx, ry - r * 0.36)] + [(rx + math.sin(t) * r * 0.22, ry + r * 0.04 - math.cos(t) * r * 0.2) for t in [i * math.pi / 8 for i in range(1, 16)]]
        poly(pts, (110, 190, 245, 255))
    elif kind == "egg":
        d.ellipse((X(rx - r * 0.22), X(ry - r * 0.3), X(rx + r * 0.22), X(ry + r * 0.28)), fill=(250, 244, 226, 255), outline=ink, width=w)
        d.line([(X(rx - r * 0.2), X(ry)), (X(rx - r * 0.08), X(ry - r * 0.1)), (X(rx + r * 0.02), X(ry + r * 0.02)), (X(rx + r * 0.14), X(ry - r * 0.08)), (X(rx + r * 0.2), X(ry))], fill=ink, width=w)
    elif kind in ("flower", "bouquet"):
        for i in range(6):
            ang = 2 * math.pi * i / 6
            disc(rx + math.cos(ang) * r * 0.2, ry + math.sin(ang) * r * 0.2, r * 0.13, (252, 214, 240, 255))
        disc(rx, ry, r * 0.12, gold)
        if kind == "bouquet":
            d.line([(X(rx), X(ry + r * 0.3)), (X(rx - r * 0.1), X(ry + r * 0.8))], fill=(60, 140, 80, 255), width=w * 2)
    elif kind == "petals":
        for (px, py) in ((rx - r * 0.1, ry - r * 0.1), (rx + r * 0.1, ry + r * 0.25), (cx - r * 1.0, cy + r * 0.3)):
            d.ellipse((X(px - r * 0.14), X(py - r * 0.08), X(px + r * 0.14), X(py + r * 0.08)), fill=(250, 160, 190, 255))
    elif kind == "bee":
        d.ellipse((X(rx - r * 0.22), X(ry - r * 0.14), X(rx + r * 0.22), X(ry + r * 0.14)), fill=gold, outline=ink, width=w)
        for k in (-1, 0, 1):
            d.line([(X(rx + k * r * 0.1), X(ry - r * 0.14)), (X(rx + k * r * 0.1), X(ry + r * 0.14))], fill=ink, width=w)
        d.ellipse((X(rx - r * 0.1), X(ry - r * 0.36), X(rx + r * 0.1), X(ry - r * 0.12)), fill=(220, 240, 250, 200), outline=ink, width=1)
    elif kind == "ball":
        disc(rx, ry + r * 0.3, r * 0.3, (248, 248, 248, 255))
        pts = [(rx + math.cos(math.radians(-90 + 72 * i)) * r * 0.12, ry + r * 0.3 + math.sin(math.radians(-90 + 72 * i)) * r * 0.12) for i in range(5)]
        poly(pts, ink)
    elif kind == "redcard":
        d.rounded_rectangle((X(rx - r * 0.2), X(ry - r * 0.28), X(rx + r * 0.2), X(ry + r * 0.28)), radius=int(r * 0.04 * S), fill=(220, 30, 40, 255), outline=ink, width=w)
    elif kind == "whistle":
        d.rounded_rectangle((X(rx - r * 0.3), X(ry - r * 0.1), X(rx + r * 0.22), X(ry + r * 0.16)), radius=int(r * 0.1 * S), fill=(226, 230, 238, 255), outline=ink, width=w)
        disc(rx + r * 0.1, ry + r * 0.08, r * 0.15, (226, 230, 238, 255))
    elif kind == "boot":
        poly([(rx - r * 0.3, ry - r * 0.3), (rx - r * 0.05, ry - r * 0.3), (rx, ry + r * 0.05), (rx + r * 0.38, ry + r * 0.18), (rx + r * 0.38, ry + r * 0.34), (rx - r * 0.3, ry + r * 0.34)], (30, 30, 34, 255))
        for k in range(4):
            d.rectangle((X(rx - r * 0.24 + k * r * 0.18), X(ry + r * 0.34), X(rx - r * 0.18 + k * r * 0.18), X(ry + r * 0.44)), fill=a)
    elif kind == "flag":
        d.line([(X(rx - r * 0.2), X(ry + r * 0.5)), (X(rx - r * 0.2), X(ry - r * 0.35))], fill=ink, width=w * 2)
        poly([(rx - r * 0.2, ry - r * 0.35), (rx + r * 0.32, ry - r * 0.2), (rx - r * 0.2, ry - r * 0.04)], m)
    elif kind == "spray":
        d.rounded_rectangle((X(rx - r * 0.18), X(ry - r * 0.05), X(rx + r * 0.18), X(ry + r * 0.45)), radius=int(r * 0.08 * S), fill=(250, 214, 220, 255), outline=ink, width=w)
        d.rectangle((X(rx - r * 0.08), X(ry - r * 0.22), X(rx + r * 0.08), X(ry - r * 0.05)), fill=a, outline=ink, width=w)
        for k in range(3):
            d.ellipse((X(rx - r * 0.4 - k * r * 0.08), X(ry - r * 0.22 + (k - 1) * r * 0.1 - 3), X(rx - r * 0.4 - k * r * 0.08 + 8), X(ry - r * 0.22 + (k - 1) * r * 0.1 + 5)), fill=(255, 255, 255, 200))
    elif kind == "rose":
        for k, col in enumerate(((200, 40, 70), (230, 80, 100), (250, 130, 140))):
            disc(rx, ry, r * (0.26 - k * 0.07), col + (255,))
        d.line([(X(rx), X(ry + r * 0.26)), (X(rx - r * 0.05), X(ry + r * 0.7))], fill=(60, 140, 80, 255), width=w * 2)
    elif kind == "gem":
        mr_gem = [(rx - r * 0.2, ry - r * 0.1), (rx + r * 0.2, ry - r * 0.1), (rx + r * 0.3, ry + r * 0.04), (rx, ry + r * 0.4), (rx - r * 0.3, ry + r * 0.04)]
        poly(mr_gem, (160, 220, 250, 255))
    elif kind == "beam":
        d.polygon([(X(cx), X(cy - r * 1.55)), (X(cx - r * 0.1), X(cy - r * 1.0)), (X(cx + r * 0.1), X(cy - r * 1.0))], fill=a)
        for k in (-1, 0, 1):
            d.line([(X(cx + k * r * 0.35), X(cy - r * 1.55)), (X(cx + k * r * 0.65), X(cy - r * 1.05))], fill=a, width=w * 2)
    elif kind == "compass":
        disc(rx, ry + r * 0.1, r * 0.3, (240, 246, 252, 255))
        poly([(rx, ry - r * 0.12), (rx - r * 0.07, ry + r * 0.1), (rx + r * 0.07, ry + r * 0.1)], (220, 50, 60, 255))
        poly([(rx, ry + r * 0.32), (rx - r * 0.07, ry + r * 0.1), (rx + r * 0.07, ry + r * 0.1)], ink)
    elif kind == "aurora":
        for k, col in enumerate(((80, 230, 200), (110, 150, 250), (200, 120, 250))):
            d.arc((X(rx - r * 0.6), X(ry - r * 0.2 + k * r * 0.14), X(rx + r * 0.4), X(ry + r * 0.5 + k * r * 0.14)), 200, 340, fill=col + (255,), width=int(r * 0.09 * S))
    elif kind == "snow":
        for i in range(6):
            ang = math.pi * i / 3
            d.line([(X(rx + math.cos(ang) * r * 0.3), X(ry + math.sin(ang) * r * 0.3)), (X(rx - math.cos(ang) * r * 0.3), X(ry - math.sin(ang) * r * 0.3))], fill=(230, 245, 255, 255), width=w * 2)
    elif kind == "question":
        d.text((X(rx), X(ry)), "?", font=ImageFont.truetype(str(FONTS / "georgiab.ttf"), int(r * 0.9 * S)), fill=a, anchor="mm", stroke_width=int(r * 0.04 * S), stroke_fill=ink)
    elif kind == "armband":
        d.rounded_rectangle((X(rx - r * 0.3), X(ry - r * 0.12), X(rx + r * 0.3), X(ry + r * 0.2)), radius=int(r * 0.05 * S), fill=a, outline=ink, width=w)
        d.text((X(rx), X(ry + r * 0.04)), "C", font=ImageFont.truetype(str(FONTS / "impact.ttf"), int(r * 0.34 * S)), fill=ink, anchor="mm")
    elif kind == "scoreboard":
        d.rounded_rectangle((X(rx - r * 0.42), X(ry - r * 0.2), X(rx + r * 0.42), X(ry + r * 0.22)), radius=int(r * 0.05 * S), fill=(20, 28, 40, 255), outline=ink, width=w)
        d.text((X(rx), X(ry + r * 0.01)), "1 - 0", font=ImageFont.truetype(str(FONTS / "impact.ttf"), int(r * 0.3 * S)), fill=a, anchor="mm")
    elif kind == "arrow":
        poly([(rx - r * 0.3, ry - r * 0.1), (rx + r * 0.08, ry - r * 0.1), (rx + r * 0.08, ry - r * 0.3), (rx + r * 0.4, ry), (rx + r * 0.08, ry + r * 0.3), (rx + r * 0.08, ry + r * 0.1), (rx - r * 0.3, ry + r * 0.1)], (110, 220, 130, 255))


def emote_img(C, mood, kind, size, t=0.0, anim=None):
    mr.EMOTE_SETS_NONE = None
    k = size / 448

    def fn(d, S):
        cx, cy, r = 224 * k, 258 * k, 138 * k
        dx = dy = 0
        if anim == "bounce":
            dy = -abs(math.sin(math.pi * t * 2)) * 14 * k
        elif anim == "shake":
            dx = math.sin(2 * math.pi * t * 4) * 8 * k
        elif anim == "sway":
            dx = math.sin(2 * math.pi * t) * 7 * k
        x0, y0 = cx + dx, cy + dy
        mr.berry_face(d, S, x0, y0, r, mood, t)
        prop(d, S, kind, x0, y0, r, C)
    return mr.layer((size, size), fn)


def build(name):
    C = dict(ms.SETS[name])
    ms.apply_set(C)
    out = TW / name / "Emotes"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for fn_, mood, kind, anim in THEMES[name]:
        for size in (448, 112, 56, 28):
            if anim:
                frames = [emote_img(C, mood, kind, size, i / 20, anim) for i in range(20)]
                frames[0].save(out / f"{fn_}_{size}.gif", save_all=True, append_images=frames[1:], duration=60, disposal=2, loop=0, optimize=False)
            else:
                emote_img(C, mood, kind, size).save(out / f"{fn_}_{size}.png", optimize=True)
    print("Saved", name, flush=True)


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(THEMES)):
        build(n)
    print("done")

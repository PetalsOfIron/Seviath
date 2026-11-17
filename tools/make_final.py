#!/usr/bin/env python3
"""
Themed badges, flair and overlays for every set (each tier / overlay carries props from that set's own world),
plus distinct banners for Hood and Slash.

    python tools/make_final.py            # everything
    python tools/make_final.py Tessel     # one set
"""
import math
import shutil
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from art import *  # noqa: F401,F403
import make_rose as mr
import make_sets as ms
import make_emotes as me
import make_hood as mh
import make_unique as mu

TW = ROOT / "images" / "twitch"

# badge tiers: (file, mood, prop) - the story of a growing fan in the set's world
BADGES = {
    "Hood": [("base", "smile", "controller"), ("3month", "smile", "headset"), ("6month", "cool", "shield"), ("9month", "angry", "sword"), ("1year", "party", "bolt"), ("2year", "laughing", "trophy"), ("3year", "cool", "crown")],
    "Helmet": [("base", "smile", "shield"), ("3month", "smile", "sword"), ("6month", "angry", "flame"), ("9month", "cool", "horn"), ("1year", "party", "coin"), ("2year", "laughing", "trophy"), ("3year", "cool", "crown")],
    "Slash": [("base", "smile", "bolt"), ("3month", "angry", "burst"), ("6month", "laughing", "flame"), ("9month", "party", "star"), ("1year", "cool", "headset"), ("2year", "laughing", "trophy"), ("3year", "angry", "crown")],
    "Snake": [("base", "sleepy", "egg"), ("3month", "smile", "leaf"), ("6month", "smile", "drop"), ("9month", "angry", "tongue"), ("1year", "party", "sun"), ("2year", "cool", "star"), ("3year", "laughing", "crown")],
    "Floral": [("base", "sleepy", "leaf"), ("3month", "smile", "drop"), ("6month", "smile", "bee"), ("9month", "joyful", "flower"), ("1year", "lovely", "petals"), ("2year", "party", "bouquet"), ("3year", "cool", "crown")],
    "Tessel": [("base", "smile", "flag"), ("3month", "smile", "whistle"), ("6month", "joyful", "boot"), ("9month", "party", "ball"), ("1year", "laughing", "scoreboard"), ("2year", "cool", "trophy"), ("3year", "party", "crown")],
    "Perfum": [("base", "sleepy", "drop"), ("3month", "smile", "petals"), ("6month", "joyful", "rose"), ("9month", "sparkly", "spray"), ("1year", "lovely", "gem"), ("2year", "cool", "sparkle"), ("3year", "party", "crown")],
    "Northbeam": [("base", "sleepy", "snow"), ("3month", "smile", "compass"), ("6month", "joyful", "aurora"), ("9month", "sparkly", "star"), ("1year", "party", "beam"), ("2year", "laughing", "flag"), ("3year", "cool", "crown")],
    "Strikeline": [("base", "smile", "armband"), ("3month", "joyful", "arrow"), ("6month", "surprise", "whistle"), ("9month", "angry", "ball"), ("1year", "party", "scoreboard"), ("2year", "laughing", "trophy"), ("3year", "cool", "crown")],
}
FLAIR = {  # (file, mood, prop)
    "Hood": [("tier2_flair", "cool", "headset"), ("tier3_flair", "angry", "sword")], "Helmet": [("tier2_flair", "cool", "shield"), ("tier3_flair", "angry", "crown")],
    "Slash": [("tier2_flair", "angry", "bolt"), ("tier3_flair", "laughing", "flame")], "Snake": [("tier2_flair", "cool", "star"), ("tier3_flair", "angry", "tongue")],
    "Floral": [("tier2_flair", "smile", "bee"), ("tier3_flair", "lovely", "bouquet")], "Tessel": [("tier2_flair", "joyful", "boot"), ("tier3_flair", "party", "trophy")],
    "Perfum": [("tier2_flair", "joyful", "rose"), ("tier3_flair", "sparkly", "spray")], "Northbeam": [("tier2_flair", "sparkly", "star"), ("tier3_flair", "party", "beam")],
    "Strikeline": [("tier2_flair", "cool", "armband"), ("tier3_flair", "party", "scoreboard")],
}
POINTS = {
    "Hood": [("points_controller", "smile", "controller"), ("points_sword", "angry", "sword"), ("points_heart", "lovely", "heart"), ("points_bolt", "party", "bolt")],
    "Helmet": [("points_coin", "lovely", "coin"), ("points_sword", "angry", "sword"), ("points_crown", "cool", "crown"), ("points_horn", "surprise", "horn")],
    "Slash": [("points_bolt", "angry", "bolt"), ("points_flame", "laughing", "flame"), ("points_star", "party", "star"), ("points_boom", "surprise", "burst")],
    "Snake": [("points_egg", "smile", "egg"), ("points_tongue", "laughing", "tongue"), ("points_sun", "sleepy", "sun"), ("points_drop", "mad", "drop")],
    "Floral": [("points_flower", "joyful", "flower"), ("points_bee", "smile", "bee"), ("points_petals", "lovely", "petals"), ("points_drop", "cry", "drop")],
    "Tessel": [("points_ball", "party", "ball"), ("points_boot", "cool", "boot"), ("points_whistle", "surprise", "whistle"), ("points_flag", "smile", "flag")],
    "Perfum": [("points_spray", "party", "spray"), ("points_rose", "lovely", "rose"), ("points_gem", "smile", "gem"), ("points_sparkle", "sparkly", "sparkle")],
    "Northbeam": [("points_star", "sparkly", "star"), ("points_compass", "smile", "compass"), ("points_beam", "party", "beam"), ("points_snow", "cool", "snow")],
    "Strikeline": [("points_ball", "angry", "ball"), ("points_score", "party", "scoreboard"), ("points_arrow", "joyful", "arrow"), ("points_whistle", "laughing", "whistle")],
}
OVERLAY_PROPS = {  # props placed on the frame: (prop, mood) at four corners + top centre
    "Hood": ["sword", "shield", "controller", "headset", "bolt"], "Helmet": ["sword", "shield", "crown", "horn", "flame"],
    "Slash": ["bolt", "flame", "burst", "star", "bolt"], "Snake": ["tongue", "leaf", "egg", "sun", "star"],
    "Floral": ["flower", "bee", "petals", "bouquet", "flower"], "Tessel": ["ball", "flag", "whistle", "boot", "trophy"],
    "Perfum": ["rose", "spray", "gem", "petals", "sparkle"], "Northbeam": ["star", "compass", "snow", "aurora", "beam"],
    "Strikeline": ["ball", "flag", "armband", "whistle", "scoreboard"],
}


def medal(C, mood, prop, size, tier_ring):
    img = ms.medallion(C, size, None, tier_ring)
    inner = int(size * (0.62 if C["shape"] != "triangle" else 0.52))
    icon = me.emote_img(C, mood, prop, inner)
    img.alpha_composite(icon, ((size - inner) // 2, (size - inner) // 2 + int(size * 0.03)))
    return img


def save(img, p, rgba=True):
    p.parent.mkdir(parents=True, exist_ok=True)
    (img if rgba else img.convert("RGB")).save(p, optimize=True)


def overlay(C, name):
    W, H = 1920, 1080
    img = ms.border((W, H), C["frame"], C, 1.7)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pim, _patch = ms.portrait(C["mascot"], C)
    if pim is not None:
        for (x, y, sz) in ((130, 130, 230), (W - 130, 130, 230), (W - 130, H - 130, 230), (130, 640, 150)):
            n = sz
            pic = pim.resize((n, n), Image.LANCZOS)
            mk = Image.new("L", (n * 3, n * 3), 0)
            ImageDraw.Draw(mk).ellipse((0, 0, n * 3 - 1, n * 3 - 1), fill=255)
            pic.putalpha(ImageChops.multiply(pic.split()[3], mk.resize((n, n), Image.LANCZOS)))
            ring = Image.new("RGBA", (n + 24, n + 24), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse((0, 0, n + 23, n + 23), fill=C["accent"] + (255,), outline=C["dark"] + (255,), width=6)
            ring.alpha_composite(pic, (12, 12))
            ov.alpha_composite(ring, (int(x - n / 2 - 12), int(y - n / 2 - 12)))
    ps = OVERLAY_PROPS[name]
    spots = [(380, 130), (W - 380, 130), (W - 380, H - 120), (W - 130, H / 2), (W / 2, 120)]
    for prop_name, (x, y) in zip([ps[0], ps[1], ps[2], ps[3], ps[4]], spots):
        ic = me.emote_img(C, "smile", prop_name, 200)
        ov.alpha_composite(ic, (int(x - 100), int(y - 100)))
    ov = shadow(ov, ov.split()[3], (0, 6), 8, (0, 0, 0), 0.45) if False else ov
    img = Image.alpha_composite(img, ov)
    cx0, cy0, cx1, cy1 = 80, H - 80 - 300, 80 + 533, H - 80
    cam = ms.border((cx1 - cx0 + 150, cy1 - cy0 + 150), C["frame"], C, 0.55)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(cam, (cx0 - 75, cy0 - 75))
    img = Image.alpha_composite(img, layer)
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rectangle((cx0 + 6, cy0 + 6, cx1 - 6, cy1 - 6), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], cut))
    return img


def build(name):
    C = dict(ms.SETS[name])
    ms.apply_set(C)
    out = TW / name
    for sub in ("Badges", "Flair", "Points"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    rings = [tuple(int(c * 0.55 + 100) for c in C["accent2"])] * 3 + [C["main"]] * 2 + [C["accent"]] * 2
    for (fn_, mood, prop), ring in zip(BADGES[name], rings):
        save(medal(C, mood, prop, 432, ring), out / "Badges" / f"{fn_}_432.png")
    for (fn_, mood, prop), ring in zip(FLAIR[name], (C["main"], C["accent"])):
        save(medal(C, mood, prop, 432, ring), out / "Flair" / f"{fn_}_432.png")
    for fn_, mood, prop in POINTS[name]:
        save(medal(C, mood, prop, 432, C["main"]), out / "Points" / f"{fn_}_432.png")
    save(overlay(C, name), out / "Overlay" / "overlay_frame.png")
    print("Saved", name, flush=True)


# ------------------------------------------------------------------------------------------ banners

def hood_banner():
    W, H = 3000, 1000
    base = Image.new("RGBA", (W, H), mh.DARK + (255,))
    frame, paper = mh.rough_frame((W, H), 0, 4, 1.5)
    inner = Image.new("RGBA", (W, H), mh.PAPER + (255,))
    base.paste(inner, (0, 0), paper)
    img = Image.alpha_composite(base, frame)
    logo = Image.open(ROOT / "images" / "LogoGaming.png").convert("RGBA").resize((760, 760), Image.LANCZOS)
    img.alpha_composite(logo, (150, 120))
    img.alpha_composite(logo.transpose(Image.FLIP_LEFT_RIGHT), (W - 150 - 760, 120))
    img = mh.lettered(img, "Petals Of Iron", (W / 2, 520), mh.fit_size("Petals Of Iron", "OLDENGL.TTF", 1250, 260), color=(120, 4, 6), grad=(80, 0, 2))
    d = ImageDraw.Draw(img)
    d.line([(W / 2 - 520, 610), (W / 2 + 520, 610)], fill=mh.RED + (255,), width=6)
    img = fill_mask(img, text_mask(img.size, "Gamer  -  Streamer  -  Artist", font("georgiai.ttf", 84), (W / 2, 730), track=4), (110, 6, 8))
    return grain(img, 6)


def slash_banner():
    W, H = 3000, 1000
    img = mu.slash_bg(W, H, seed=12)
    cut = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cut).polygon([(0, 0), (W * 0.62, 0), (W * 0.62 - 380, H), (0, H)], fill=(20, 0, 8, 215))
    img = Image.alpha_composite(img, cut)
    for k, word in enumerate(("PETALS", "OF IRON")):
        m = text_mask((W, H), word, font("impact.ttf", 330), (W * 0.31 - k * 60, 400 + k * 330), track=14)
        img = mu.outlined(img, m, mu.ORANGE if k == 0 else (255, 255, 255), mu.ORANGE_D if k == 0 else (225, 225, 225), width=12)
    C = dict(ms.SETS["Slash"])
    ms.apply_set(C)
    ball = me.emote_img(C, "angry", "bolt", 880)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(ball, (int(W * 0.68), 70))
    img = shadow(img, lay.split()[3], (0, 14), 20, (0, 0, 0), 0.6)
    img = Image.alpha_composite(img, lay)
    return grain(img, 8)


def main():
    args = sys.argv[1:]
    for n in (args or list(BADGES)):
        build(n)
    if not args:
        save(hood_banner(), TW / "Hood" / "Banner" / "banner.png", rgba=False)
        save(slash_banner(), TW / "Slash" / "Banner" / "banner.png", rgba=False)
    print("done")


if __name__ == "__main__":
    main()

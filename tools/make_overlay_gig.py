#!/usr/bin/env python3
"""Gig gallery images (1280x769) for a stream-overlay gig. 13 different overlays, none repeated across the three images.
Output: C:/Users/SaphiresSilver/Documents/twitch/OverlayGig/overlay_1_cover.png, overlay_2_styles.png, overlay_3_layouts.png"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_banner_gig as g
from art import *  # noqa: F401,F403

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/OverlayGig")
P = g.P / "twitch"
W, H = g.W, g.H

OV = {
    "slash": P / "Slash/Overlay/overlay_frame.png", "northbeam": P / "Northbeam/Overlay/overlay_frame.png", "hood": P / "Hood/Overlay/overlay_frame.png",
    "floral": P / "Floral/Overlay/overlay_frame.png", "purple": P / "Purple/Overlay/purple_overlay_frame.png", "perfum": P / "Perfum/Overlay/overlay_frame.png",
    "tessel": P / "Tessel/Overlay/overlay_frame.png", "snake": P / "Snake/Overlay/overlay_frame.png", "helmet": P / "Helmet/Overlay/overlay_frame.png",
    "nightwing": P / "Nightwing/Overlay/nightwing_overlay.png", "starcaller": P / "Starcaller/Overlay/starcaller_overlay.png",
    "strikeline": P / "Strikeline/Overlay/overlay_frame.png", "wow": P / "Overlay/wow_layout_1920x1080.png",
}

_SCENES = {}


def scene(seed):
    """A stand-in for gameplay: dusk sky, sun glow and layered hills, tinted differently per overlay."""
    if seed in _SCENES:
        return _SCENES[seed]
    rnd = random.Random(seed)
    top = [(40, 60, 110), (70, 40, 100), (20, 80, 100), (90, 50, 70), (30, 50, 70)][seed % 5]
    bot = [(220, 140, 110), (240, 170, 120), (140, 200, 220), (230, 160, 150), (200, 190, 140)][seed % 5]
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t ** 1.4) for i in range(3)))
    img = glow(img.convert("RGBA"), (w * 0.55, h * 0.18, w * 0.85, h * 0.55), (255, 230, 170), blur=120, alpha=170).convert("RGB")
    d = ImageDraw.Draw(img)
    base = [(30, 40, 66), (22, 28, 50), (14, 18, 34)]
    for k, col in enumerate(base):
        y0 = h * (0.55 + 0.12 * k)
        pts = [(0, h)]
        for x in range(0, w + 60, 60):
            pts.append((x, y0 + math.sin(x / (240 + 90 * k) + seed + k) * 70 + rnd.randint(-18, 18)))
        pts.append((w, h))
        d.polygon(pts, fill=col)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    _SCENES[seed] = img.convert("RGBA")
    return _SCENES[seed]


def ov_card(key, w, h, seed, radius=14):
    base = scene(seed).copy()
    base.alpha_composite(Image.open(OV[key]).convert("RGBA"))
    base = base.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w * 3, h * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), radius=radius * 3, fill=255)
    base.putalpha(m.resize((w, h), Image.LANCZOS))
    return base


def title(img, t):
    img = g.txt(img, t, (W // 2, 76), 46, g.SILVER, (150, 168, 210), "center", 14)
    ImageDraw.Draw(img).line([(W // 2 - 180, 100), (W // 2 + 180, 100)], fill=g.GOLD + (255,), width=3)
    return img


def any_card(path, w, h, bgcol=(16, 18, 34), frame=None, radius=14):
    """Screens (png), alerts and corners (png or gif): letterboxed on a dark card."""
    im = Image.open(path)
    if getattr(im, "is_animated", False):
        im.seek(frame if frame is not None else im.n_frames // 2)
    im = im.convert("RGBA")
    out = Image.new("RGBA", (w, h), bgcol + (255,))
    s = min((w - 12) / im.width, (h - 12) / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    m = Image.new("L", (w * 3, h * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), radius=radius * 3, fill=255)
    out.putalpha(m.resize((w, h), Image.LANCZOS))
    return out


def cover():
    img = g.bg()
    x0 = 64
    img = g.txt(img, "CUSTOM", (x0, 238), 40, g.GOLD, (200, 140, 60), track=18)
    img = g.txt(img, "STREAM", (x0, 340), 84, g.SILVER, (150, 168, 210), track=3)
    img = g.txt(img, "OVERLAYS", (x0, 430), 84, g.SILVER, (150, 168, 210), track=3)
    ImageDraw.Draw(img).line([(x0, 462), (x0 + 300, 462)], fill=g.GOLD + (255,), width=4)
    for i, s in enumerate(("OVERLAYS  ·  SCREENS", "WEBCAM  ·  CHAT  ·  GAME FRAMES", "TWITCH  ·  YOUTUBE  ·  KICK")):
        img = g.txt(img, s, (x0, 520 + i * 36), 17, g.TEAL, g.TEAL, track=4)
    img = g.txt(img, "DESIGNED AROUND YOUR BRAND", (x0, 670), 16, (170, 180, 210), (170, 180, 210), track=5)
    img = g.put(img, ov_card("slash", 700, 394, 1), (530, 40))
    img = g.put(img, any_card(P / "Floral/Screens/starting_soon.png", 340, 191), (530, 462))
    img = g.put(img, any_card(P / "Hood/Screens/offline.png", 340, 191), (890, 462))
    img = g.chip(img, "STREAM OVERLAY", (546, 56), 15)
    img = g.chip(img, "SCREEN", (546, 478), 15)
    img = g.chip(img, "SCREEN", (906, 478), 15)
    return img


def overlays():
    img = title(g.bg(), "STREAM OVERLAYS")
    keys = ["hood", "northbeam", "purple", "perfum", "tessel", "snake", "helmet", "nightwing", "starcaller", "strikeline", "floral", "wow"]
    for i, k in enumerate(keys):
        x = 30 + (i % 4) * 310
        y = 126 + (i // 4) * 183
        img = g.put(img, ov_card(k, 290, 163, i + 4), (x, y), 0.5)
    x = 60
    for s_ in ("WEBCAM FRAME", "CHAT BOX", "ALERT AREA", "LATEST FOLLOWER", "GAME FRAME"):
        img = g.chip(img, s_, (x, 690), 16, g.TEAL)
        x += g.twidth(img, s_, 16) + 28 + 12
    return img


def screens():
    img = title(g.bg(), "STREAM SCREENS")
    S_ = lambda set_, f: P / set_ / "Screens" / f
    items = [
        (S_("Perfum", "starting_soon.png"), "STARTING SOON"), (S_("Tessel", "starting_soon.png"), "STARTING SOON"),
        (S_("Strikeline", "starting_soon.png"), "STARTING SOON"), (S_("Helmet", "starting_soon.png"), "STARTING SOON"),
        (S_("Northbeam", "be_right_back.png"), "BE RIGHT BACK"), (S_("Slash", "be_right_back.png"), "BE RIGHT BACK"),
        (S_("Purple", "be_right_back.png"), "BE RIGHT BACK"), (S_("Starcaller", "starcaller_be_right_back.png"), "BE RIGHT BACK"),
        (S_("Nightwing", "nightwing_ending.png"), "ENDING"), (S_("Snake", "offline.png"), "OFFLINE"),
        (S_("Rose", "offline.png"), "OFFLINE"), (S_("Starcaller", "starcaller_ending.png"), "ENDING"),
    ]
    for i, (path, label) in enumerate(items):
        x = 30 + (i % 4) * 310
        y = 126 + (i // 4) * 183
        img = g.put(img, any_card(path, 290, 163), (x, y), 0.5)
        img = g.chip(img, label, (x + 8, y + 8), 14)
    x = 150
    for s_ in ("STARTING SOON", "BE RIGHT BACK", "ENDING", "OFFLINE"):
        img = g.chip(img, s_, (x, 690), 16, g.TEAL)
        x += g.twidth(img, s_, 16) + 28 + 12
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, f in (("overlay_1_cover", cover), ("overlay_2_overlays", overlays), ("overlay_3_screens", screens)):
        im = f().convert("RGB")
        try:
            im.save(OUT / (name + ".png"), optimize=True)
            print("saved", name)
        except OSError:
            im.save(OUT / (name + "_new.png"), optimize=True)
            print("saved", name + "_new")


if __name__ == "__main__":
    main()

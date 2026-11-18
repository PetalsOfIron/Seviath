#!/usr/bin/env python3
"""Four 16:9 showcase boards of the Nightwing kit for social posts.
Output: C:/Users/SaphiresSilver/Documents/twitch/Nightwing/Showcase/board_1..4.png"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

sys.argv = sys.argv[:1]
import make_nightwing as nw
from art import *  # noqa: F401,F403

K = Path("C:/Users/SaphiresSilver/Documents/twitch/Nightwing")
OUTD = K / "Showcase"
W, H = 1600, 900


def load(p):
    return Image.open(K / p).convert("RGBA")


def fit(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def drop(canvas, im, xy, blur=18, op=0.55):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
    canvas = shadow(canvas, lay.split()[3], (0, 12), blur, (0, 0, 0), op)
    return Image.alpha_composite(canvas, lay)


def board(seed, title, sub):
    img = nw.bg((W, H), seed=seed)
    img = nw.title(img, title, (90, 112), 50, anchor="left", track=12)
    img = nw.label(img, sub, (90, 156), 20, nw.AMBER, anchor="left", track=7)
    d = ImageDraw.Draw(img)
    d.line([(90, 180), (420, 180)], fill=nw.AMBER + (255,), width=3)
    nw.diamond(d, W - 110, 96, 14, nw.AMBER + (255,))
    return img


def board1():
    img = board(41, "NIGHTWING", "TWITCH STREAM KIT  ·  LOGO, BANNER, AVATAR")
    img = drop(img, fit(load("Logo/nightwing_logo.png"), 640, 640), (90, 205))
    img = drop(img, fit(load("Banner/profile_banner_1200x480.png"), 760, 304), (780, 214))
    av = fit(load("Logo/nightwing_avatar.png"), 300, 300)
    img = drop(img, av, (860, 540))
    img = drop(img, av.resize((150, 150), Image.LANCZOS), (1200, 620))
    img = drop(img, av.resize((72, 72), Image.LANCZOS), (1390, 660), 8)
    return img


def board2():
    img = board(42, "SCREENS", "STARTING SOON  ·  BE RIGHT BACK  ·  ENDING  ·  OFFLINE")
    cw, ch = 560, 315
    for i, n in enumerate(["starting_soon", "brb", "ending", "offline"]):
        img = drop(img, fit(load("Screens/%s.png" % n), cw, ch), (210 + (i % 2) * (cw + 60), 210 + (i // 2) * (ch + 28)), 14, 0.5)
    return img


def board3():
    img = board(43, "PANELS & ALERTS", "NINE CHANNEL PANELS  ·  FIVE STREAM ALERTS")
    for i, n in enumerate(["about", "schedule", "rules", "socials", "donate", "commands"]):
        img = drop(img, fit(load("Panels/%s.png" % n), 420, 131), (90 + (i % 2) * 440, 215 + (i // 2) * 150), 8, 0.5)
    for i, n in enumerate(["follow", "subscribe", "raid", "donation"]):
        img = drop(img, fit(load("Alerts/%s.png" % n), 520, 177), (960, 205 + i * 150), 10, 0.5)
    return img


def board4():
    img = board(44, "EMOTES & BADGES", "ELEVEN EMOTES  ·  SIX SUB BADGES  ·  FOUR BITS BADGES")
    em = ["happy", "love", "cry", "angry", "smug", "wink", "sleep", "shock", "heart", "gg", "gem"]
    for i, n in enumerate(em):
        e = fit(load("Emotes/nw_%s_448.png" % n), 170, 170)
        img = drop(img, e, (100 + (i % 6) * 235, 215 + (i // 6) * 205), 8, 0.4)
    x = 130
    for i in range(6):
        img = drop(img, nw.sub_badge(i).resize((104, 104), Image.LANCZOS), (x, 670), 6, 0.4)
        x += 128
    x += 40
    for i in range(4):
        img = drop(img, nw.bits_badge(i).resize((104, 104), Image.LANCZOS), (x, 670), 6, 0.4)
        x += 128
    return img


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate((board1, board2, board3, board4), 1):
        f().convert("RGB").save(OUTD / ("board_%d.png" % i), optimize=True)
        print("saved board", i)


if __name__ == "__main__":
    main()

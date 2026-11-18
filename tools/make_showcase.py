#!/usr/bin/env python3
"""Four 16:9 showcase boards of the Starcaller kit for social posts (nothing near the edges, so X does not crop anything).
Output: C:/Users/SaphiresSilver/Documents/twitch/Starcaller/Showcase/board_1..4.png"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.argv = sys.argv[:1]
import make_starcaller2 as s2
from make_starcaller2 import *  # noqa: F401,F403
import make_starcaller as sc

K = Path("C:/Users/SaphiresSilver/Documents/twitch/Starcaller")
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
    img = sc.nebula((W, H), seed=seed)
    img = t2(img, title, (90, 96), 44, "left", 14, SILVER, SKY)
    img = t2(img, sub, (90, 142), 24, "left", 8, GOLD, GOLD_D)
    d = ImageDraw.Draw(img)
    d.line([(90, 166), (420, 166)], fill=GOLD + (255,), width=3)
    sparkle(d, W - 110, 90, 18, GOLD)
    return img


def board1():
    img = board(31, "STARCALLER", "TWITCH STREAM KIT  ·  LOGO, BANNER, AVATAR")
    logo = fit(load("Logo/starcaller_logo.png"), 640, 640)
    img = drop(img, logo, (90, 200))
    ban = fit(load("Banner/profile_banner_1200x480.png"), 760, 304)
    img = drop(img, ban, (780, 214))
    av = fit(load("Logo/starcaller_avatar.png"), 300, 300)
    m = Image.new("L", av.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, av.width - 1, av.height - 1), fill=255)
    av.putalpha(ImageChops.multiply(av.split()[3], m))
    img = drop(img, av, (860, 540))
    sm_ = av.resize((150, 150), Image.LANCZOS)
    img = drop(img, sm_, (1200, 620))
    sm2 = av.resize((72, 72), Image.LANCZOS)
    img = drop(img, sm2, (1390, 660), 8)
    return img


def board2():
    img = board(32, "SCREENS", "STARTING SOON  ·  BE RIGHT BACK  ·  ENDING  ·  OFFLINE")
    names = ["starting_soon", "brb", "ending", "offline"]
    cw, ch = 560, 315
    for i, n in enumerate(names):
        s = fit(load("Screens/%s.png" % n), cw, ch)
        x = 210 + (i % 2) * (cw + 60)
        y = 200 + (i // 2) * (ch + 30)
        img = drop(img, s, (x, y), 14, 0.5)
    return img


def board3():
    img = board(33, "PANELS & ALERTS", "NINE CHANNEL PANELS  ·  FIVE STREAM ALERTS")
    pn = ["about", "schedule", "rules", "socials", "donate", "commands"]
    for i, n in enumerate(pn):
        p = fit(load("Panels/%s.png" % n), 420, 131)
        img = drop(img, p, (90 + (i % 2) * 440, 210 + (i // 2) * 150), 8, 0.5)
    al = ["follow", "subscribe", "raid", "donation", "bits"]
    for i, n in enumerate(al[:4]):
        a = fit(load("Alerts/%s.png" % n), 560, 179)
        img = drop(img, a, (950, 200 + i * 150), 10, 0.5)
    return img


def board4():
    img = board(34, "EMOTES & BADGES", "TWELVE EMOTES  ·  SIX SUB BADGES  ·  FOUR BITS BADGES")
    em = ["happy", "love", "cry", "rage", "smirk", "wink", "sleepy", "shock", "star", "moon", "heart", "gg"]
    for i, n in enumerate(em):
        e = fit(load("Emotes/sc_%s_448.png" % n), 170, 170)
        img = drop(img, e, (100 + (i % 6) * 235, 210 + (i // 6) * 205), 8, 0.4)
    x = 130
    for i in range(6):
        img = drop(img, s2.star_badge(i).resize((104, 104), Image.LANCZOS), (x, 670), 6, 0.4)
        x += 128
    x += 40
    for i in range(4):
        img = drop(img, s2.bits_badge2(i).resize((104, 104), Image.LANCZOS), (x, 670), 6, 0.4)
        x += 128
    return img


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate((board1, board2, board3, board4), 1):
        f().convert("RGB").save(OUTD / ("board_%d.png" % i), optimize=True)
        print("saved board", i)


if __name__ == "__main__":
    main()

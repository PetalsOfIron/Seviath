#!/usr/bin/env python3
"""Starcaller Twitch kit: blue-haired horned elf in a galaxy. Reuses the Nightwing kit machinery with a new palette.
Output: C:/Users/SaphiresSilver/Documents/twitch/Starcaller/   (not used by the portfolio site)"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.argv = sys.argv[:1]
import make_nightwing as nw
import make_nightwing2 as n2
from art import *  # noqa: F401,F403

ART = Path("C:/Users/SaphiresSilver/Documents/twitch/character2.png")
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Starcaller")
nw.OUT = OUT

DEEP = (6, 10, 36)
NIGHT = (14, 28, 92)
COBALT = (34, 76, 200)
SKY = (110, 170, 250)
GOLD = (238, 192, 98)
GOLD_D = (166, 120, 50)
PINK = (222, 92, 168)
SILVER = (226, 234, 248)
SILVER_D = (150, 164, 198)

# palette for the reused code
for k, v in dict(DEEP=DEEP, NIGHT=NIGHT, INDIGO=COBALT, VIOLET=SKY, AMBER=GOLD, AMBER_D=GOLD_D, WINE=(214, 60, 150), TEAL=(110, 214, 240),
                 SILVER=SILVER, SILVER_D=SILVER_D).items():
    setattr(nw, k, v)
for k, v in dict(SKIN=(244, 176, 210), SKIN_D=(206, 118, 172), HAIR=(24, 108, 204), HAIR_D=(8, 44, 118), HAIR_L=(232, 244, 255),
                 HORN=(92, 84, 176), HORN_L=(158, 156, 238), EYE_A=(36, 84, 200), EYE_B=(130, 190, 255), RIB=GOLD, LINE=(16, 10, 36)).items():
    setattr(n2, k, v)


# ---------------------------------------------------------------- ornament: curved horns instead of wings
def horns(size, cx, cy, scale, flip=False, alpha=255):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = scale * (-1 if flip else 1)
    specs = [((0, 0), (230, -10), (350, -260), 52), ((0, 24), (200, 70), (400, -40), 40), ((0, 44), (150, 130), (290, 120), 30)]
    for (a, b, c, w) in specs:
        P = lambda p: (cx + p[0] * s, cy + p[1] * scale)
        nw.blade(d, P((a[0], a[1] + 7)), P((b[0], b[1] + 8)), P((c[0], c[1] + 8)), w * scale * 1.2, GOLD_D + (alpha,))
        nw.blade(d, P(a), P(b), P(c), w * scale * 1.12, GOLD + (alpha,))
        nw.blade(d, P((a[0], a[1] - 2)), P((b[0], b[1] - 2)), P((c[0], c[1] - 3)), w * scale * 0.9, COBALT + (alpha,))
        nw.blade(d, P((a[0], a[1] - 5)), P((b[0], b[1] - 6)), P((c[0], c[1] - 8)), w * scale * 0.42, SKY + (alpha,))
    return layer


nw.wings = horns


# ---------------------------------------------------------------- background: nebula + stars
def nebula(size, seed=2):
    w, h = size
    rnd = random.Random(seed)
    base = Image.new("RGB", size, DEEP)
    for col, n, rad, op in (((20, 48, 160), 9, 0.34, 110), ((60, 40, 150), 6, 0.3, 80), ((10, 90, 190), 5, 0.26, 70)):
        lay = Image.new("RGB", size, (0, 0, 0))
        d = ImageDraw.Draw(lay)
        for _ in range(n):
            x, y = rnd.randint(0, w), rnd.randint(0, h)
            r = int(min(w, h) * rad * rnd.uniform(0.6, 1.2))
            d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(c * op / 255) for c in col))
        base = ImageChops.screen(base, lay.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12)))
    img = base.convert("RGBA")
    st = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    for _ in range(int(w * h / 2600)):
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        r = rnd.choice((0.7, 0.9, 1.2, 1.6, 2.2))
        a = rnd.randint(110, 255)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(220, 232, 255, a))
    img = Image.alpha_composite(img, st.filter(ImageFilter.GaussianBlur(0.4)))
    return grain(vignette(img, 0.45, (2, 4, 16)), 5)


def gradient_x(size, x0, x1, col=DEEP, a0=0, a1=235):
    w, h = size
    g = Image.new("L", size, 0)
    d = ImageDraw.Draw(g)
    for x in range(w):
        t = min(1, max(0, (x - x0) / max(1, x1 - x0)))
        d.line([(x, 0), (x, h)], fill=int(a0 + (a1 - a0) * t))
    lay = Image.new("RGBA", size, col + (255,))
    lay.putalpha(g)
    return lay


def scene(art, W, H, align="left"):
    s = H / art.height
    im = art.resize((int(art.width * s), H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 70, 2))
    out = Image.new("RGBA", (W, H), DEEP + (255,))
    out.alpha_composite(im.convert("RGBA"), (0 if align == "left" else W - im.width, 0))
    return out


# ---------------------------------------------------------------- pieces
def screen(art, big, small, note):
    W, H = 1920, 1080
    img = scene(art, W, H)
    img = Image.alpha_composite(img, gradient_x((W, H), 760, 1180, DEEP, 0, 232))
    img = glow(img, (1050, 250, 1850, 900), COBALT, blur=140, alpha=70)
    X = 1180
    img, _ = nw.fit_title(img, big, (X, 520), 660, size=120, track=10)
    nw.divider(img, X + 250, 590, 250)
    img = nw.label(img, small, (X, 660), 36, GOLD, anchor="left", track=10)
    img = nw.label(img, note, (X, 722), 26, SILVER_D, anchor="left", track=5)
    nw.corner_brackets(img, 44, 120, GOLD + (255,), width=4)
    img = nw.label(img, nw.NAME, (X, 112), 30, SILVER, anchor="left", track=12)
    return img


def banner(art, W=1200, H=480):
    im = art.crop((0, 56, art.width, 56 + int(art.width * H / W))).resize((W, H), Image.LANCZOS)
    img = im.convert("RGBA")
    img = Image.alpha_composite(img, gradient_x((W, H), 560, 820, DEEP, 0, 225))
    img, _ = nw.fit_title(img, nw.NAME, (640, 226), 520, size=66, track=10)
    nw.divider(img, 640 + 260, 262, 260)
    img = nw.label(img, nw.TAGLINE, (640, 318), 22, GOLD, anchor="left", track=9)
    return img


def logo(art, S=2000):
    face = art.crop((30, 6, 600, 576))
    hack = Image.new("RGBA", (1000, 1600), (0, 0, 0, 0))
    hack.alpha_composite(face.resize((368, 368), Image.LANCZOS).convert("RGBA"), (322, 70))
    img = nw.emblem(hack, S, with_name=False)
    # name ribbon
    rb = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rb)
    y0, y1 = 1550, 1740
    poly = [(250, y0), (S - 250, y0), (S - 190, (y0 + y1) / 2), (S - 250, y1), (250, y1), (190, (y0 + y1) / 2)]
    rd.polygon(poly, fill=DEEP + (255,))
    img = shadow(img, rb.split()[3], (0, 12), 16, (0, 0, 0), 0.55)
    rd.polygon(poly, outline=GOLD + (255,), width=7)
    rd.polygon([(268, y0 + 16), (S - 268, y0 + 16), (S - 214, (y0 + y1) / 2), (S - 268, y1 - 16), (268, y1 - 16), (214, (y0 + y1) / 2)], outline=COBALT + (255,), width=4)
    img = Image.alpha_composite(img, rb)
    img, _ = nw.fit_title(img, nw.NAME, (S // 2, 1686), 1260, size=130, anchor="center", track=14)
    return img


def alert(art, head, sub):
    face = art.crop((30, 6, 600, 576))
    hack = Image.new("RGBA", (1000, 1600), (0, 0, 0, 0))
    hack.alpha_composite(face.resize((368, 368), Image.LANCZOS).convert("RGBA"), (322, 70))
    return nw.alert(hack, head, sub)


def main():
    art = Image.open(ART).convert("RGBA")
    OUT.mkdir(parents=True, exist_ok=True)
    nw.save(logo(art), "Logo", "starcaller_logo.png")
    face = art.crop((30, 6, 600, 576))
    hack = Image.new("RGBA", (1000, 1600), (0, 0, 0, 0))
    hack.alpha_composite(face.resize((368, 368), Image.LANCZOS), (322, 70))
    nw.save(nw.emblem(hack, 1000), "Logo", "starcaller_avatar.png")
    nw.save(banner(art), "Banner", "profile_banner_1200x480.png")
    sub = {"DONATE": "support the stars", "DISCORD": "join the constellation", "SCHEDULE": "when the stars rise"}
    for t, s in nw.PANELS:
        nw.save(nw.panel(t, sub.get(t, s)), "Panels", t.lower() + ".png")
    for big, small, note, fn in (("STARTING SOON", "THE STARS ARE ALIGNING", "grab a drink and settle in", "starting_soon"),
                                 ("BE RIGHT BACK", "LOST IN THE NEBULA", "back in a moment", "brb"),
                                 ("THANKS FOR WATCHING", "SEE YOU AMONG THE STARS", "follow so you never miss a stream", "ending"),
                                 ("OFFLINE", "NOT STREAMING RIGHT NOW", "see you at the next stream", "offline")):
        nw.save(screen(art, big, small, note).convert("RGB"), "Screens", fn + ".png")
    nw.save(nw.overlay(), "Overlay", "stream_overlay.png")
    for head, sub, fn in (("NEW FOLLOWER", "{name}", "follow"), ("NEW SUBSCRIBER", "{name}", "subscribe"), ("INCOMING RAID", "{name}", "raid"),
                          ("DONATION", "{amount}", "donation"), ("BITS", "{amount}", "bits")):
        nw.save(alert(art, head, sub), "Alerts", fn + ".png")
    for i, m in enumerate((1, 3, 6, 12, 24, 36)):
        b = nw.sub_badge(i)
        for s in (72, 36, 18):
            nw.save(b.resize((s, s), Image.LANCZOS), "Badges", "Subscriber", "%dmonth_%d.png" % (m, s))
    for i, n in enumerate((1, 100, 1000, 10000)):
        b = nw.bits_badge(i)
        for s in (72, 36, 18):
            nw.save(b.resize((s, s), Image.LANCZOS), "Badges", "Bits", "bits%d_%d.png" % (n, s))
    emos = {n: n2.chibi(n) for n in n2.EXPR}
    emos["heart"] = nw.emote_heart()
    emos["gg"] = nw.emote_text("GG", GOLD, GOLD_D)
    emos["gem"] = nw.emote_gem(col=(110, 170, 250))
    for n, im in emos.items():
        nw.save(im, "Emotes", "sc_%s_448.png" % n)
        for s in (112, 56, 28):
            nw.save(im.resize((s, s), Image.LANCZOS), "Emotes", "sc_%s_%d.png" % (n, s))
    for n in ("happy", "love", "smug"):
        nw.save(emos[n].resize((112, 112), Image.LANCZOS), "ChannelPoints", n + ".png")
    print("done")


if __name__ == "__main__":
    main()

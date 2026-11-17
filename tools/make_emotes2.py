#!/usr/bin/env python3
"""Emotes without a drawn-on face: each emote is an object from the set's world (some shown with the set's own art crop)."""
import math
import shutil
import sys

from PIL import Image, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_sets as ms
import make_emotes as me
import make_redo as rd

TW = ROOT / "images" / "twitch"


def base_emote(C, kind, with_art, size):
    big = 448
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    if with_art:
        pic = rd.portrait_disc(C, 330)
        ring = Image.new("RGBA", (352, 352), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((0, 0, 351, 351), fill=C["accent"] + (255,), outline=C["dark"] + (255,), width=8)
        ring.alpha_composite(pic, (11, 11))
        img.alpha_composite(ring, (22, 22))
        pr = rd.prop_img(C, kind, 190)
        img.alpha_composite(pr, (big - 205, big - 205))
    else:
        glow_l = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        ImageDraw.Draw(glow_l).ellipse((40, 40, big - 40, big - 40), fill=C["accent"] + (70,))
        img.alpha_composite(glow_l.filter(ImageFilter.GaussianBlur(26)))
        pr = rd.prop_img(C, kind, 360)
        sh = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        sh.alpha_composite(pr, (44, 52))
        img = shadow(img, sh.split()[3], (0, 8), 8, (0, 0, 0), 0.4)
        img.alpha_composite(pr, (44, 44))
    return img


def frame(img, t, anim):
    if not anim:
        return img
    big = img.width
    dx = dy = 0
    if anim == "bounce":
        dy = -abs(math.sin(math.pi * t * 2)) * 22
    elif anim == "shake":
        dx = math.sin(2 * math.pi * t * 4) * 12
    elif anim == "sway":
        dx = math.sin(2 * math.pi * t) * 10
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(img.rotate(math.sin(2 * math.pi * t) * (6 if anim == "sway" else 0), resample=Image.BICUBIC), (int(dx), int(dy)))
    return out


def build(name):
    C = dict(ms.SETS[name]); C["_name"] = name
    ms.apply_set(C)
    out = TW / name / "Emotes"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for i, (fn_, mood, kind, anim) in enumerate(me.THEMES[name]):
        base = base_emote(C, kind, with_art=(i % 3 == 0 and C["mascot"] != "slash"), size=448)
        for size in (448, 112, 56, 28):
            if anim:
                frames = [frame(base, k / 20, anim).resize((size, size), Image.LANCZOS) for k in range(20)]
                frames[0].save(out / f"{fn_}_{size}.gif", save_all=True, append_images=frames[1:], duration=60, disposal=2, loop=0, optimize=False)
            else:
                base.resize((size, size), Image.LANCZOS).save(out / f"{fn_}_{size}.png", optimize=True)
    print("Saved", name, flush=True)


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(me.THEMES)):
        build(n)
    print("done")

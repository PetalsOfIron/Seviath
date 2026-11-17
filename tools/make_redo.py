#!/usr/bin/env python3
"""Redo flair, sub badges and overlays so no two sets look alike.
Badges / flair: the set's own object drawn BIG in the set's medallion (no mascot face), tiers get more ornaments.
Flair: the set's own artwork crop. Overlays: each set has its own layout of its own art and props."""
import math
import shutil
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_rose as mr
import make_sets as ms
import make_emotes as me
import make_final as mf

TW = ROOT / "images" / "twitch"


def prop_img(C, kind, size):
    """A prop alone, centred, large."""
    big = size * 4
    r = big * 0.26

    def fn(d, S):
        me.prop(d, S, kind, big * 0.4, big * 0.62, r, C)
    im = mr.layer((big, big), fn)
    box = im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
    if not box:
        return Image.new("RGBA", (size, size))
    im = im.crop(box)
    k = min(size / im.width, size / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return out


def portrait_disc(C, size):
    pim, patch = ms.portrait(C["mascot"], C)
    if pim is None:
        return Image.new("RGBA", (size, size))
    pic = pim.resize((size, size), Image.LANCZOS)
    mk = Image.new("L", (size * 3, size * 3), 0)
    ImageDraw.Draw(mk).ellipse((0, 0, size * 3 - 1, size * 3 - 1), fill=255)
    pic.putalpha(ImageChops.multiply(pic.split()[3], mk.resize((size, size), Image.LANCZOS)))
    return pic


def badge(C, name, tier_idx, prop, size=432):
    ring = tuple(int(c * 0.55 + 100) for c in C["accent2"]) if tier_idx < 3 else (C["main"] if tier_idx < 5 else C["accent"])
    img = ms.medallion(C, size, None, ring)
    inner = int(size * 0.56)
    ic = prop_img(C, prop, inner)
    img.alpha_composite(ic, ((size - inner) // 2, (size - inner) // 2 + 6))
    d = ImageDraw.Draw(img)
    for i in range(tier_idx + 1 if tier_idx > 2 else 0):   # stars along the bottom grow with the tier
        x = size / 2 + (i - tier_idx / 2.0) * 34
        mr.sparkle(d, 1, x, size - 62, 13, fill=C["accent"])
    return img


def flair(C, tier, size=432):
    img = ms.medallion(C, size, None, C["main"] if tier == 2 else C["accent"], dots=14 if tier == 3 else 0)
    pic = portrait_disc(C, int(size * 0.66 if tier == 2 else size * 0.74))
    img.alpha_composite(pic, ((size - pic.width) // 2, (size - pic.height) // 2))
    if tier == 3:
        top = prop_img(C, "crown", int(size * 0.5))
        img.alpha_composite(top, ((size - top.width) // 2, 8))
    else:
        bot = prop_img(C, mf.FLAIR[C["_name"]][0][2], int(size * 0.34))
        img.alpha_composite(bot, (size - bot.width - 36, size - bot.height - 34))
    return img


LAYOUT = {  # kind: ("portrait", x, y, size) | ("prop", name, x, y, size)
    "Hood": [("prop", "sword", 150, 150, 260), ("prop", "sword", 1770, 150, 260), ("prop", "shield", 1770, 930, 240), ("prop", "controller", 960, 70, 200)],
    "Slash": [("prop", "bolt", 200, 170, 300), ("prop", "flame", 1720, 170, 300), ("prop", "burst", 1720, 910, 280)],
    "Helmet": [("portrait", 960, 140, 300), ("prop", "shield", 140, 930, 230), ("prop", "sword", 1780, 930, 230)],
    "Snake": [("portrait", 1700, 880, 320), ("prop", "leaf", 160, 150, 240), ("prop", "tongue", 1760, 150, 220), ("prop", "egg", 960, 80, 160)],
    "Floral": [("portrait", 150, 150, 330), ("portrait", 1770, 150, 280), ("portrait", 1770, 930, 330), ("prop", "bee", 960, 90, 170)],
    "Tessel": [("prop", "flag", 150, 150, 240), ("prop", "flag", 1770, 150, 240), ("prop", "ball", 1760, 920, 260), ("prop", "whistle", 960, 80, 170)],
    "Perfum": [("prop", "rose", 150, 150, 300), ("prop", "rose", 1770, 930, 300), ("prop", "sparkle", 1780, 160, 220), ("portrait", 1810, 540, 200)],
    "Northbeam": [("portrait", 960, 150, 260), ("prop", "snow", 160, 170, 230), ("prop", "compass", 1770, 930, 240), ("prop", "aurora", 1770, 170, 230)],
    "Strikeline": [("portrait", 1740, 540, 380), ("prop", "armband", 170, 160, 220), ("prop", "scoreboard", 960, 80, 260), ("prop", "ball", 160, 930, 200)],
}


def overlay(C, name):
    W, H = 1920, 1080
    if name == "Hood":
        import make_hood as mh
        img = mh.overlay_frame()
    else:
        img = ms.border((W, H), C["frame"], C, 1.7)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for item in LAYOUT[name]:
        if item[0] == "portrait":
            _, x, y, sz = item
            pic = portrait_disc(C, sz)
            ring = Image.new("RGBA", (sz + 26, sz + 26), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse((0, 0, sz + 25, sz + 25), fill=C["accent"] + (255,), outline=C["dark"] + (255,), width=7)
            ring.alpha_composite(pic, (13, 13))
            ov.alpha_composite(ring, (int(x - sz / 2 - 13), int(y - sz / 2 - 13)))
        else:
            _, kind, x, y, sz = item
            ov.alpha_composite(prop_img(C, kind, sz), (int(x - sz / 2), int(y - sz / 2)))
    img = Image.alpha_composite(img, ov)
    cx0, cy0, cx1, cy1 = 80, H - 80 - 300, 80 + 533, H - 80
    if name != "Hood":
        cam = ms.border((cx1 - cx0 + 150, cy1 - cy0 + 150), C["frame"], C, 0.55)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.alpha_composite(cam, (cx0 - 75, cy0 - 75))
        img = Image.alpha_composite(img, layer)
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rectangle((cx0 + 6, cy0 + 6, cx1 - 6, cy1 - 6), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], cut))
    return img


def build(name):
    C = dict(ms.SETS[name]); C["_name"] = name
    ms.apply_set(C)
    out = TW / name
    for sub in ("Badges", "Flair"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
        (out / sub).mkdir(parents=True)
    for i, (fn_, mood, prop) in enumerate(mf.BADGES[name]):
        badge(C, name, i, prop).save(out / "Badges" / f"{fn_}_432.png", optimize=True)
    for t in (2, 3):
        flair(C, t).save(out / "Flair" / f"tier{t}_flair_432.png", optimize=True)
    if (out / "Points").exists():
        shutil.rmtree(out / "Points")
    (out / "Points").mkdir(parents=True)
    for fn_, mood, prop in mf.POINTS[name]:
        img = ms.medallion(C, 432, None, C["main"])
        ic = prop_img(C, prop, int(432 * (0.5 if C["shape"] == "triangle" else 0.58)))
        img.alpha_composite(ic, ((432 - ic.width) // 2, (432 - ic.height) // 2 + 8))
        img.save(out / "Points" / f"{fn_}_432.png", optimize=True)
    (out / "Overlay").mkdir(parents=True, exist_ok=True)
    overlay(C, name).save(out / "Overlay" / "overlay_frame.png", optimize=True)
    print("Saved", name, flush=True)


def corner(name):
    C = dict(ms.SETS[name]); C["_name"] = name
    ms.apply_set(C)
    out = TW / name / "Corner" / "corner.gif"
    if name == "Hood":
        import make_hood as mh
        mh.gif(mh.corner_frames(), out)
        return
    label = "Petals Of Iron" if name in ("Helmet", "Slash", "Snake", "Floral") else name
    frames = ms.animated(C, (440, 200), "", 64, 0.5, 30)
    icon = portrait_disc(C, 120)
    sz = ms.fit_size(label, C["font"], 230, 60)
    tl = ms.title_text(Image.new("RGBA", (440, 200), (0, 0, 0, 0)), label, (292, 100 + sz * 0.34), sz, C)
    outf = []
    for f in frames:
        f = f.copy()
        f.alpha_composite(icon, (44, 40))
        f.alpha_composite(tl)
        outf.append(f)
    ms.gif(outf, out)
    print("corner", name, flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["corners"]:
        for n in mf.BADGES:
            corner(n)
        print("done"); raise SystemExit
    for n in (sys.argv[1:] or list(mf.BADGES)):
        build(n)
    print("done")

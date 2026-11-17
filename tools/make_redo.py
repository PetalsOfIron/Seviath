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


ART_BADGE = ("Snake", "Tessel", "Perfum", "Northbeam", "Floral")


def art_icon(C, size, tier_idx):
    """The set's own artwork, shown larger and brighter on higher tiers (a closer crop each time)."""
    if C["_name"] == "Tessel":
        import make_brands as mb
        b = mb.load("Footballboot.png")
        b = b.crop(b.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
        k = 0.66 + 0.05 * tier_idx
        b.thumbnail((int(size * k), int(size * k)))
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.alpha_composite(b, ((size - b.width) // 2, (size - b.height) // 2))
        return out
    pim, _ = ms.portrait(C["mascot"], C)
    k = 0.92 - 0.07 * tier_idx                       # visible share of the crop; smaller = closer
    n = pim.width
    box = int(n * (1 - k) / 2)
    pic = pim.crop((box, box, n - box, n - box)).resize((size, size), Image.LANCZOS)
    mk = Image.new("L", (size * 3, size * 3), 0)
    ImageDraw.Draw(mk).ellipse((0, 0, size * 3 - 1, size * 3 - 1), fill=255)
    pic.putalpha(ImageChops.multiply(pic.split()[3], mk.resize((size, size), Image.LANCZOS)))
    return pic


SIG = {"Hood": "sword", "Helmet": "crown", "Slash": "bolt", "Snake": "egg", "Floral": "flower", "Tessel": "boot", "Perfum": "rose", "Northbeam": "snow", "Strikeline": "arrow"}
RING = [(150, 150, 160), (176, 140, 110), (200, 200, 210), (110, 190, 230), (250, 206, 72), (250, 150, 60), (230, 80, 120)]


def badge(C, name, tier_idx, prop, size=432):
    """Same object on every tier of a set; it grows and gains ornaments as the tier goes up."""
    ring = RING[tier_idx] if tier_idx < 3 else (C["main"] if tier_idx < 5 else C["accent"])
    img = ms.medallion(C, size, None, ring)
    inner = int(size * (0.40 + 0.04 * tier_idx))
    tri = C["shape"] == "triangle"
    if tri:
        inner = int(size * (0.30 + 0.02 * tier_idx))
    if name in ART_BADGE:
        ic = art_icon(C, inner, tier_idx)
    else:
        ic = prop_img(C, SIG[name], inner)
    img.alpha_composite(ic, ((size - inner) // 2, (size - inner) // 2 + (34 if tri else 4)))
    d = ImageDraw.Draw(img)
    for i in range(tier_idx):                     # one star per tier along the bottom
        x = size / 2 + (i - (tier_idx - 1) / 2.0) * 36
        mr.sparkle(d, 1, x, size - (92 if tri else 70), 13 if tri else 15, fill=C["accent"])
    if tier_idx >= 4 and name not in ART_BADGE:   # two small companions from tier 5
        for sx in (-1, 1):
            sm = prop_img(C, SIG[name], int(size * 0.16))
            img.alpha_composite(sm, (int(size / 2 + sx * size * 0.30 - sm.width / 2), int(size * 0.2)))
    return img


FLAIR_MODE = {"Hood": "cross", "Slash": "cross", "Helmet": "above", "Tessel": "below", "Strikeline": "below"}


def tessel_boot(size):
    import make_brands as mb
    b = mb.load("Footballboot.png")
    b = b.crop(b.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
    b.thumbnail((size, size))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(b, ((size - b.width) // 2, (size - b.height) // 2))
    return out


def tessel_flair(C, tier, size=432):
    img = ms.medallion(C, size, None, C["main"] if tier == 2 else C["accent"], dots=0)
    big = tessel_boot(int(size * (0.62 if tier == 2 else 0.7)))
    img.alpha_composite(big, ((size - big.width) // 2, int(size * 0.2)))
    d = ImageDraw.Draw(img)
    if tier == 3:
        for i in range(3):
            mr.sparkle(d, 1, size / 2 + (i - 1) * 40, size * 0.17, 14, fill=C["accent"])
    small = tessel_boot(int(size * 0.16))
    for sx in (-1, 1):
        img.alpha_composite(small, (int(size / 2 + sx * size * 0.2 - small.width / 2), int(size * 0.68)))
    return img


def flair(C, tier, size=432):
    name = C["_name"]
    if name == "Tessel":
        return tessel_flair(C, tier, size)
    mode = FLAIR_MODE.get(name, "flank")
    sig = SIG[name]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    big = int(size * 0.5)
    if mode == "cross":
        for a in (-38, 38):
            p = prop_img(C, sig, int(size * 0.8)).rotate(a, resample=Image.BICUBIC)
            img.alpha_composite(p, ((size - p.width) // 2, (size - p.height) // 2))
    plate = ms.medallion(C, size, None, C["main"] if tier == 2 else C["accent"], dots=14 if tier == 3 else 0)
    pic = portrait_disc(C, int(size * 0.5 if mode in ("cross", "flank") else size * 0.56))
    off = (0, 0)
    if mode == "above":
        off = (0, 30)
    elif mode == "below":
        off = (0, -20)
    if mode == "cross":
        shrink = ms.medallion(C, int(size * 0.62), None, C["main"] if tier == 2 else C["accent"])
        shrink.alpha_composite(portrait_disc(C, int(size * 0.62 * 0.62)), ((shrink.width - int(size * 0.62 * 0.62)) // 2,) * 2)
        img.alpha_composite(shrink, ((size - shrink.width) // 2, (size - shrink.height) // 2))
    else:
        img.alpha_composite(plate)
        img.alpha_composite(pic, ((size - pic.width) // 2 + off[0], (size - pic.height) // 2 + off[1]))
    n = 1 if tier == 2 else 2
    if mode == "flank":
        for sx in (-1, 1):
            p = prop_img(C, sig, int(size * (0.26 if tier == 2 else 0.34)))
            img.alpha_composite(p, (int(size / 2 + sx * size * 0.34 - p.width / 2), int(size * 0.62)))
    elif mode == "above":
        p = prop_img(C, sig, int(size * (0.34 if tier == 2 else 0.46)))
        img.alpha_composite(p, ((size - p.width) // 2, 4))
    elif mode == "below":
        p = prop_img(C, sig, int(size * (0.3 if tier == 2 else 0.4)))
        img.alpha_composite(p, ((size - p.width) // 2, size - p.height - 6))
    elif tier == 3:
        p = prop_img(C, "star", int(size * 0.2))
        img.alpha_composite(p, ((size - p.width) // 2, 6))
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
    pim, _p = ms.portrait(C["mascot"], C)
    if pim is not None:
        icon = portrait_disc(C, 120)
    else:
        icon = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        ImageDraw.Draw(icon).ellipse((0, 0, 119, 119), fill=C["main"] + (255,), outline=C["dark"] + (255,), width=5)
        pr = prop_img(C, SIG[name], 80)
        icon.alpha_composite(pr, (20, 20))
    inset = {"slant": 40, "arrow": 20}.get(C.get("pshape"), 0)
    sz = ms.fit_size(label, C["font"], 200 - inset, 56)
    tl = ms.title_text(Image.new("RGBA", (440, 200), (0, 0, 0, 0)), label, (292 + inset // 2 - 10, 100 + sz * 0.34), sz, C)
    outf = []
    for f in frames:
        f = f.copy()
        f.alpha_composite(icon, (60 if C.get('pshape') == 'slant' else 44, 40))
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

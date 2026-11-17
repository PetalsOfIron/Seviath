#!/usr/bin/env python3
"""
Starting soon / Be right back / Offline screens that belong to each set's own artwork, each with its own composition:
  starting soon - the set's character big in the middle, title under it
  be right back - character on the left waving, text on the right
  offline       - character asleep on the right, dimmed scene, text on the left

Backgrounds come from each set's art: Floral = your gold-and-flower screen, Snake = your painting,
Tessel = a pitch, Perfum = pink wall and cream table with petals, Northbeam = indigo with its triangle,
Strikeline = navy with the banner's cyan stripes, Hood = maroon with the paper card.

    python tools/make_screens.py            # all
    python tools/make_screens.py Tessel
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_rose as mr
import make_sets as ms

W, H = 1920, 1080
TW = ROOT / "images" / "twitch"
DL = Path("C:/Users/SaphiresSilver/Downloads/art")

TEXT = {"starting": ("Starting soon", ["The stream begins shortly"], "party", "party"),
        "brb": ("Be right back", ["I will be back", "in a moment"], "hi", "wave"),
        "offline": ("Offline", ["Thank you for watching,", "see you next time"], "sleepy", "zzz")}



def bottle_clean():
    """Whole bottle, stopper to foot, with the table around the foot removed."""
    from PIL import ImageDraw
    import make_brands as mb
    b = mb.load("Bottle.png").crop((1650, 1560, 2930, 3958))
    m = Image.new("L", b.size, 255)
    d = ImageDraw.Draw(m)
    d.rectangle((0, 2200, 300, b.height), fill=0)
    d.rectangle((960, 2200, b.width, b.height), fill=0)
    d.rectangle((0, 2395, b.width, b.height), fill=0) if False else None
    b.putalpha(ImageChops.multiply(b.split()[3], m))
    return b

def bg_tessel():
    base = radial((W, H), (28, 120, 72), (8, 34, 26), cx=0.5, cy=0.5, spread=1.0).convert("RGBA")
    d = ImageDraw.Draw(base)
    for i in range(0, W, 240):
        if (i // 240) % 2 == 0:
            d.rectangle((i, 0, i + 240, H), fill=(255, 255, 255, 12))
    L = (240, 250, 240, 90)
    d.rectangle((70, 70, W - 70, H - 70), outline=L, width=6)
    d.line([(W // 2, 70), (W // 2, H - 70)], fill=L, width=6)
    d.ellipse((W // 2 - 190, H // 2 - 190, W // 2 + 190, H // 2 + 190), outline=L, width=6)
    d.rectangle((70, H // 2 - 270, 380, H // 2 + 270), outline=L, width=6)
    d.rectangle((W - 380, H // 2 - 270, W - 70, H // 2 + 270), outline=L, width=6)
    for cx, cy, a in ((70, 70, 0), (W - 70, 70, 90), (W - 70, H - 70, 180), (70, H - 70, 270)):
        d.arc((cx - 60, cy - 60, cx + 60, cy + 60), a, a + 90, fill=(223, 255, 61, 255), width=10)
    return base


def bg_perfum():
    import make_brands as mb
    base = mb.perfum_scene((W, H), 700)
    base = mb.soft_petals(base, (0, 0, W - 80, H - 80), 40, seed=5, size=(24, 70))
    return glow(base, (300, 100, 1600, 900), (255, 236, 222), blur=220, alpha=90)


def bg_northbeam():
    base = radial((W, H), (36, 56, 130), (8, 14, 36), cx=0.5, cy=0.45, spread=1.0).convert("RGBA")
    d = ImageDraw.Draw(base)
    cx, cy = W // 2, H // 2 + 60
    for k in range(9):
        s = 150 + k * 120
        d.polygon([(cx, cy - s), (cx + s * 1.05, cy + s * 0.8), (cx - s * 1.05, cy + s * 0.8)], outline=(125, 235, 240, max(14, 70 - k * 7)), width=4)
    return base


def bg_strikeline():
    import make_football as mf
    base = radial((W, H), (31, 58, 95), (10, 14, 20), cx=0.5, cy=0.5, spread=1.0).convert("RGBA")
    s = mf.stripes(int(W * 0.2), int(H * 0.5))
    base.alpha_composite(s, (0, int(H * 0.25)))
    base.alpha_composite(s.transpose(Image.FLIP_LEFT_RIGHT), (W - s.width, int(H * 0.25)))
    return base


def bg_hood():
    return radial((W, H), (108, 8, 12), (36, 0, 2), cx=0.35, cy=0.5, spread=1.0).convert("RGBA")


BG = {"Tessel": bg_tessel, "Perfum": bg_perfum, "Northbeam": bg_northbeam, "Strikeline": bg_strikeline, "Hood": bg_hood}
DARK_TEXT = {"Perfum"}



_HERO = {}


def hero_art(name, px):
    """The set's own artwork, fitted into a square of px (transparent background)."""
    key = (name, px)
    if key in _HERO:
        return _HERO[key]
    art = None
    if name == "Northbeam":
        import make_northbeam as nb
        em, wd = (nb.crop_pad(p) for p in nb.split_logo(nb.load_logo()))
        art = nb.fit(nb.lockup(em, wd), px, px)
    elif name == "Strikeline":
        import make_football as mf
        art = mf.fit(mf.figure(), px, px)
    elif name == "Tessel":
        import make_brands as mb
        art = mb.load("Footballboot.png", size=(1400, 1400))
    elif name == "Perfum":
        import make_brands as mb
        b = mb.load("Bottle.png")
        art = bottle_clean()
    elif name == "Hood":
        art = Image.open(ROOT / "images" / "LogoGaming.png").convert("RGBA").resize((px, px), Image.LANCZOS)
    if art is not None:
        box = art.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox()
        if box:
            art = art.crop(box)
        k = min(px / art.width, px / art.height)
        art = art.resize((max(1, round(art.width * k)), max(1, round(art.height * k))), Image.LANCZOS)
    _HERO[key] = art
    return art


def compose(name, kind):
    C = dict(ms.SETS[name])
    ms.apply_set(C)
    title, sub, mood, extra = TEXT[kind]
    img = BG[name]()
    hero_px = {"starting": 400, "brb": 620, "offline": 500}[kind]
    art = hero_art(name, hero_px)
    hero = art if art is not None else mr.emote(mood, extra, hero_px)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hw, hh = hero.size
    mirror = name in ("Perfum", "Strikeline") and kind != "starting"
    if kind == "starting":
        lay.alpha_composite(hero, ((W - hw) // 2, 70 + (400 - hh) // 2))
        tpos, align = (W / 2, 800), "center"
    elif (kind == "brb") != mirror:
        lay.alpha_composite(hero, (150 + (hero_px - hw) // 2, (H - hh) // 2))
        tpos, align = (1330, 500), "center"
    else:
        lay.alpha_composite(hero, (W - hw - 190, (H - hh) // 2 + 20))
        tpos, align = (640, 500), "center"
    if kind == "offline":
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 90)))
    img = shadow(img, lay.split()[3], (0, 16), 24, (0, 0, 0), 0.5)
    img = Image.alpha_composite(img, lay)
    dark = name in DARK_TEXT
    t1, t2 = ((C["text"], C["text2"]) if dark else (C["text"] if sum(C["text"]) > 600 else (250, 250, 250), C["text2"] if sum(C["text"]) > 600 else (214, 224, 236)))
    if dark:
        t1, t2 = (96, 34, 60), (70, 22, 44)
    sz = ms.fit_size(title, C["font"], 900 if kind != "starting" else 1300, 190 if kind != "starting" else 150)
    m = text_mask((W, H), title, font(C["font"], sz), (tpos[0], tpos[1] + (0 if kind != "starting" else 0)))
    if not dark:
        img = shadow(img, m, (0, 8), 10, (0, 0, 0), 0.6)
    img = fill_mask(img, m, t1, t2)
    ly = tpos[1] + sz * 0.55 + 20
    d = ImageDraw.Draw(img)
    d.line([(tpos[0] - 320, ly), (tpos[0] + 320, ly)], fill=C["accent"] + (255,) if not dark else (184, 150, 84, 255), width=5)
    for k, ln in enumerate(sub):
        szs = ms.fit_size(ln, "georgiai.ttf", 820, 54)
        img = fill_mask(img, text_mask((W, H), ln, font("georgiai.ttf", szs), (tpos[0], ly + 70 + k * 66)), (240, 240, 240) if not dark else (96, 34, 60))
    return grain(img, 8)


def floral(kind):
    """Your own gold-and-flowers screen, re-lettered."""
    import make_floral as mf
    title, sub, _, _ = TEXT[kind]
    src = Image.open(mf.SRC).convert("RGB")
    img = mf.erase_text(src, (342, 468, 1742, 712)).convert("RGBA")
    sz = ms.fit_size(title, "OLDENGL.TTF", 1250, 250)
    m = text_mask(img.size, title, font("OLDENGL.TTF", sz), (1045, 640 if kind != "starting" else 640), track=6)
    img = shadow(img, m, (0, 10), 14, (10, 6, 30), 0.65)
    img = fill_mask(img, m, mf.WHITE, (226, 214, 244))
    d = ImageDraw.Draw(img)
    d.line([(740, 700), (985, 700)], fill=mf.GOLD_L + (235,), width=3)
    d.line([(1105, 700), (1350, 700)], fill=mf.GOLD_L + (235,), width=3)
    diamond(d, 1045, 700, 12, mf.GOLD_L + (255,))
    line = {"starting": "The stream begins shortly", "brb": "I will be back in a moment", "offline": "Thank you for watching, see you next time"}[kind]
    img = fill_mask(img, text_mask(img.size, line, font("georgiai.ttf", ms.fit_size(line, "georgiai.ttf", 1000, 52)), (1045, 790), track=2), (246, 238, 250))
    return grain(img, 6)


def snake(kind):
    """Three different compositions of your snake painting."""
    import make_offline as mo
    src = mo.clean_source(Image.open(ROOT / "images" / "Banner snake.png").convert("RGB"))
    if kind == "starting":
        crop = src.crop((0, 0, 1778, 1000))                      # the whole coil
        img = crop.resize((W, int(W * 1000 / 1778)), Image.LANCZOS).crop((0, 0, W, H))
        side = "right"
    elif kind == "brb":
        crop = src.crop((300, 60, 1500, 735))                    # head close-up
        img = crop.resize((W, H), Image.LANCZOS)
        side = "right"
    else:
        crop = src.crop((0, 120, 1500, 965))
        img = crop.resize((W, H), Image.LANCZOS)
        img = Image.blend(img, Image.new("RGB", img.size, (10, 40, 90)), 0.55)
        side = "left"
    img = img.convert("RGBA")
    title, sub, _, _ = TEXT[kind]
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px0 = 1130 if side == "right" else 80
    ImageDraw.Draw(panel).rounded_rectangle((px0, 250, px0 + 710, 800), radius=44, fill=(8, 40, 90, 170), outline=(250, 206, 72, 255), width=6)
    img = Image.alpha_composite(img, panel)
    cx = px0 + 355
    sz = ms.fit_size(title, "OLDENGL.TTF", 620, 150)
    m = text_mask((W, H), title, font("OLDENGL.TTF", sz), (cx, 470))
    img = fill_mask(shadow(img, m, (0, 8), 10, (0, 0, 0), 0.6), m, (250, 252, 255), (210, 226, 246))
    d = ImageDraw.Draw(img)
    d.line([(cx - 250, 540), (cx + 250, 540)], fill=(250, 206, 72, 255), width=5)
    for k, ln in enumerate(sub):
        img = fill_mask(img, text_mask((W, H), ln, font("georgiai.ttf", ms.fit_size(ln, "georgiai.ttf", 600, 48)), (cx, 612 + k * 60)), (240, 246, 255))
    return grain(img, 8)



def strikeline(kind):
    """Broadcast-style Strikeline screen: spotlight on the centred figure, cyan stripe bundles, lower-third title plate, brand strip."""
    import make_football as mf
    CY, NAVY_D = (0, 168, 232), (8, 14, 24)
    title, sub, _, _ = TEXT[kind]
    img = radial((W, H), (36, 66, 108), NAVY_D, cx=0.5, cy=0.38, spread=0.95).convert("RGBA")
    img = glow(img, (W / 2 - 520, 20, W / 2 + 520, 700), (60, 150, 230), blur=170, alpha=95)
    sb = mf.stripes(int(W * 0.2), int(H * 0.5))
    sb.putalpha(sb.split()[3].point(lambda v: int(v * (0.35 if kind == "offline" else 0.9))))
    img.alpha_composite(sb, (0, int(H * 0.15)))
    img.alpha_composite(sb.transpose(Image.FLIP_LEFT_RIGHT), (W - sb.width, int(H * 0.15)))
    fig = mf.fit(mf.figure(), 520, {"starting": 520, "brb": 500, "offline": 460}[kind])
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(fig, ((W - fig.width) // 2, 70))
    img = shadow(img, lay.split()[3], (0, 18), 26, (0, 0, 0), 0.6)
    img = Image.alpha_composite(img, lay)
    if kind == "offline":
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 90)))
    # lower-third plate
    pw, ph, py = 1240, 250, 650
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.polygon([(W / 2 - pw / 2 + 50, py), (W / 2 + pw / 2, py), (W / 2 + pw / 2 - 50, py + ph), (W / 2 - pw / 2, py + ph)], fill=(10, 18, 32, 215))
    pd.polygon([(W / 2 - pw / 2 + 50, py), (W / 2 - pw / 2 + 74, py), (W / 2 - pw / 2 + 24, py + ph), (W / 2 - pw / 2, py + ph)], fill=CY + (255,))
    pd.line([(W / 2 - pw / 2 + 60, py + ph - 2), (W / 2 + pw / 2 - 50, py + ph - 2)], fill=CY + (200,), width=4)
    img = shadow(img, plate.split()[3], (0, 12), 16, (0, 0, 0), 0.5)
    img = Image.alpha_composite(img, plate)
    sz = ms.fit_size(title.upper(), "impact.ttf", 1060, 128, track=12)
    m = text_mask((W, H), title.upper(), font("impact.ttf", sz), (W / 2 + 12, py + 22 + sz * 0.84), track=12)
    img = fill_mask(img, m, (250, 252, 255), (200, 212, 226))
    line = " ".join(sub)
    szs = ms.fit_size(line.upper(), "bahnschrift.ttf", 1040, 34, track=8)
    img = fill_mask(img, text_mask((W, H), line.upper(), font("bahnschrift.ttf", szs), (W / 2 + 12, py + ph - 44), track=8), CY)
    # brand strip + corner brackets
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 56, W, H), fill=(6, 10, 18, 235))
    d.line([(0, H - 56), (W, H - 56)], fill=CY + (255,), width=3)
    img = fill_mask(img, text_mask((W, H), "STRIKELINE   -   FOOTBALL COMPANY", font("bahnschrift.ttf", 24), (W / 2, H - 20), track=10), (190, 205, 222))
    corner_brackets(img, 36, 90, CY + (230,), width=4)
    return grain(img, 8)


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, optimize=True)
    print("Saved", path.relative_to(ROOT), flush=True)


FILES = {"starting": "starting_soon", "brb": "be_right_back", "offline": "offline"}


def main():
    sets = sys.argv[1:] or ["Floral", "Snake", "Hood", "Tessel", "Perfum", "Northbeam", "Strikeline"]
    for name in sets:
        for kind, fn in FILES.items():
            if name == "Floral":
                img = floral(kind)
            elif name == "Snake":
                img = snake(kind)
            elif name == "Strikeline":
                img = strikeline(kind)
            elif name == "Hood":
                import make_hood as mh
                t, sb, _, _ = TEXT[kind]
                img = mh.screen(t, " ".join(sb))
            else:
                img = compose(name, kind)
            save(img, TW / name / "Screens" / (fn + ".png"))
    print("done")


if __name__ == "__main__":
    main()

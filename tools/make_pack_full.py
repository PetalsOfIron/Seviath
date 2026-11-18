#!/usr/bin/env python3
"""Stream graphics packs, sold separately from the emote/badge/panel packs. Name-free logo (if the set has one), X profile and header versions,
banner (if the set has one), screens, overlay and ONE animated alert with sound.
Reads  Documents/twitch/Neutral/<Set>/  (made by make_neutral.py / make_neutral_old.py)
Writes Documents/twitch/Gumroad/<Set>/graphics_*.zip (each under 10 MB), graphics_thumb.png (1000x1000), graphics_cover_1..3.png (1280x720)
    python tools/make_pack_full.py [Set ...]"""
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

import make_banner_gig as g
import make_gumroad as mg
import make_set_showcases as ss
from art import *  # noqa: F401,F403

NEUTRAL = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral")
GUM = mg.OUT
W, H = 1280, 720


def sources(name):
    root = NEUTRAL / name
    if not root.is_dir():
        return {}
    pick = lambda sub, pats=("*.png",): sorted(f for p in pats for f in (root / sub).glob(p)) if (root / sub).is_dir() else []
    return {"Logo": pick("Logo"), "Banner": pick("Banner"), "Screens": pick("Screens"), "Overlay": pick("Overlay"),
            "Alert": pick("Alerts", ("*.gif", "*.wav", "*.txt", "*.png"))}


def build(name, alerts_label="ALERT"):
    src = {k: v for k, v in sources(name).items() if v}
    if not src:
        print("no neutral sources for", name)
        return None
    zdir = GUM / name
    zdir.mkdir(parents=True, exist_ok=True)
    for old in zdir.glob("graphics*.zip"):
        old.unlink()
    label = mg.SETS[name].replace(" ", "_") + "_Stream_Graphics"
    parts = {"graphics_logo_banner.zip": ("Logo", "Banner", "Overlay", "Alert"), "graphics_screens.zip": ("Screens",)}
    made = []
    for zname, folders in parts.items():
        files = [(f, fo) for fo in folders for f in src.get(fo, [])]
        if not files:
            continue
        with zipfile.ZipFile(zdir / zname, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for f, fo in files:
                z.write(f, "%s/%s/%s" % (label, fo, f.name))
        made.append(zname)
    counts = {"logo": any("logo" in f.name and "x_" not in f.name for f in src.get("Logo", [])), "banner": bool(src.get("Banner")),
              "screens": len(src.get("Screens", [])), "overlay": bool(src.get("Overlay"))}
    covers(name, src, counts)
    print(name, counts, [(n, round((zdir / n).stat().st_size / 1e6, 1)) for n in made])
    return counts


def pal(name):
    main = mg.COLORS[name]
    return main, tuple(min(255, int(c * 0.45 + 150)) for c in main)


def base(name, w, h):
    main, _ = pal(name)
    dark = tuple(int(c * 0.17) for c in main)
    mid = tuple(int(c * 0.44) for c in main)
    img = radial((w, h), mid, dark, 0.35, 0.3, 1.1).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(-h, w, 52):
        d.line([(x, h), (x + h, 0)], fill=(255, 255, 255, 6), width=2)
    return grain(vignette(img, 0.4, (2, 2, 8)), 4)


def card(im, path, box, back=(8, 10, 22)):
    x, y, w, h = box
    pic = ss.fit(mg.load(path), w, h)
    plate = Image.new("RGBA", (pic.width, pic.height), back + (255,))
    plate.alpha_composite(pic)
    return mg.put(im, plate, (x + (w - pic.width) // 2, y + (h - pic.height) // 2), 8, 0.5)


def tt(im, s, xy, size, col=g.SILVER, c2=(170, 180, 205), anchor="left", track=10):
    return g.txt(im, s, xy, size, col, c2, anchor, track)


def byname(files, key):
    return next((f for f in files if key in f.name), None)


def contents_line(counts):
    parts = []
    if counts["logo"]:
        parts += ["LOGO"]
    if counts["banner"]:
        parts += ["BANNER"]
    parts += ["%d SCREENS" % counts["screens"]]
    if counts["overlay"]:
        parts += ["OVERLAY"]
    parts += ["ANIMATED ALERT + SOUND"]
    return " · ".join(parts)


def covers(name, src, counts):
    style = mg.SETS[name].upper()
    _, acc = pal(name)
    logos = src.get("Logo", [])
    logo = byname(logos, "logo.png") or byname(logos, "_logo.png")
    xlogo = byname(logos, "x_profile_logo")
    xprof = byname(logos, "x_profile_400")
    banner = byname(src.get("Banner", []), "profile_banner")
    xhead = byname(src.get("Banner", []), "x_header")
    screens = src.get("Screens", [])
    overlay = src["Overlay"][0] if src.get("Overlay") else None
    alert = byname(src.get("Alert", []), ".gif") or byname(src.get("Alert", []), ".png")
    line = contents_line(counts)

    # cover 1: everything that is in the pack
    img = base(name, W, H)
    img = tt(img, style + " - STREAM GRAPHICS", (60, 100), 42)
    img = tt(img, line + " · READY FOR ANY CHANNEL", (62, 144), 16, acc, acc, track=4)
    if logo:
        img = card(img, logo, (60, 190, 300, 300))
        if xprof:
            img = card(img, xprof, (60, 510, 150, 150))
    if banner:
        img = card(img, banner, (390, 190, 480, 192))
        if overlay:
            img = card(img, overlay, (390, 400, 480, 270))
    elif overlay:
        img = card(img, overlay, (60 if not logo else 390, 190, 480, 270)) if not logo else card(img, overlay, (390, 190, 480, 270))
    for i, p in enumerate(screens[:4]):
        img = card(img, p, (905 + (i % 2) * 185, 190 + (i // 2) * 105, 175, 98))
    if alert:
        img = card(img, alert, (905, 420, 360, 162))
        img = tt(img, "1 ANIMATED ALERT · USE IT FOR EVERY EVENT", (905, 600), 13, acc, acc, track=2)
    img.convert("RGB").save(GUM / name / "graphics_cover_1.png", optimize=True)

    # cover 2: the screens large
    img = base(name, W, H)
    img = tt(img, style + " - STREAM SCREENS", (60, 100), 42)
    img = tt(img, "STARTING SOON · BE RIGHT BACK · OFFLINE" + (" · ENDING" if counts["screens"] > 3 else "") + " · 1920×1080 · READY FOR ANY CHANNEL", (62, 144), 16, acc, acc, track=4)
    n = min(4, len(screens))
    if n == 3:
        for i, p in enumerate(screens[:3]):
            pos = [(60, 190), (660, 190), (360, 450)][i]
            img = card(img, p, (pos[0], pos[1], 580, 245))
    else:
        for i, p in enumerate(screens[:4]):
            img = card(img, p, (60 + (i % 2) * 600, 190 + (i // 2) * 260, 580, 245))
    img.convert("RGB").save(GUM / name / "graphics_cover_2.png", optimize=True)

    # cover 3: logo and banner with the X versions, or overlay and alert when the set has neither
    img = base(name, W, H)
    if logo or banner:
        img = tt(img, style + " - LOGO & BANNER" if (logo and banner) else (style + (" - LOGO" if logo else " - BANNER")), (60, 100), 42)
        img = tt(img, "NO LETTERING ON THE LOGO · ALSO AS X (TWITTER) PROFILE PICTURE AND HEADER" if logo else "ALSO AS X (TWITTER) HEADER", (62, 144), 16, acc, acc, track=4)
        if logo:
            img = card(img, logo, (60, 190, 330, 330))
            if xlogo:
                img = card(img, xlogo, (60, 540, 130, 130))
            if xprof:
                img = card(img, xprof, (210, 540, 130, 130))
        if banner:
            bx = 430 if logo else 60
            bw = 790 if logo else 1160
            img = card(img, banner, (bx, 190, bw, min(316, int(bw / 2.5))))
            if xhead:
                img = card(img, xhead, (bx, 540, bw, 130))
    else:
        img = tt(img, style + " - OVERLAY & ALERT", (60, 100), 42)
        img = tt(img, "STREAM OVERLAY · ONE ANIMATED ALERT · ALERT SOUND", (62, 144), 16, acc, acc, track=4)
        if overlay:
            img = card(img, overlay, (60, 190, 760, 428))
        if alert:
            img = card(img, alert, (850, 250, 370, 167))
    img.convert("RGB").save(GUM / name / "graphics_cover_3.png", optimize=True)

    # square thumbnail
    S = 1000
    img = base(name, S, S)
    img = tt(img, style, (S // 2, 120), 56, anchor="center")
    img = tt(img, "TWITCH STREAM GRAPHICS", (S // 2, 176), 24, acc, acc, anchor="center", track=12)
    if logo:
        img = card(img, logo, (80, 230, 380, 380))
        if banner:
            img = card(img, banner, (480, 230, 440, 176))
        else:
            img = card(img, overlay, (480, 230, 440, 247)) if overlay else img
        for i, p in enumerate(screens[:4]):
            img = card(img, p, (480 + (i % 2) * 225, 420 + (i // 2) * 110, 215, 100))
    else:
        for i, p in enumerate(screens[:3]):
            pos = [(80, 230), (510, 230), (295, 430)][i]
            img = card(img, p, (pos[0], pos[1], 410, 190))
        if overlay:
            img = card(img, overlay, (80, 650, 300, 169)) if False else img
    if alert:
        img = card(img, alert, (80, 650, 380, 171)) if logo else card(img, alert, (80, 650, 380, 171))
        if overlay:
            img = card(img, overlay, (540, 650, 380, 214)) if False else img
    img = tt(img, line, (S // 2, 900), 20, (210, 214, 228), (210, 214, 228), anchor="center", track=5)
    img.convert("RGB").save(GUM / name / "graphics_thumb.png", optimize=True)


def main():
    names = [a for a in sys.argv[1:] if a in mg.SETS] or list(mg.SETS)
    for n in names:
        build(n)


if __name__ == "__main__":
    main()

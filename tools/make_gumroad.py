#!/usr/bin/env python3
"""Gumroad packs: one zip per style (finished PNG/GIF files only, no sources) plus three 1280x720 product images and a text.
Pieces with a name written on them (logos, banners, screens, overlays) are left out; emotes, sub badges, channel point icons
and panels carry no brand or channel name.
Output: C:/Users/SaphiresSilver/Documents/twitch/Gumroad/<Set>/  (pack.zip, cover_1..3.png, listing.txt)
    python tools/make_gumroad.py [Set ...]"""
import re
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_banner_gig as g
import make_set_showcases as ss
from art import *  # noqa: F401,F403

T = g.P / "twitch"
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Gumroad")
W, H = 1280, 720

SETS = {  # folder: product style name
    "Purple": "Purple Gothic", "Floral": "Floral", "Snake": "Mosaic Snake", "Slash": "Bold Stripe", "Helmet": "Gold Knight", "Hood": "Hooded Gamer",
    "Tessel": "Football Boot", "Perfum": "Luxury Pink", "Northbeam": "Aurora Indigo", "Strikeline": "Navy Football", "Rose": "Rose and Berry",
    "Nightwing": "Winged Elf", "Starcaller": "Galaxy Elf", "Crimson": "Vampire Elf",
}


COLORS = {"Purple": (120, 60, 200), "Floral": (140, 80, 180), "Snake": (30, 130, 160), "Slash": (200, 40, 70), "Helmet": (170, 120, 40), "Hood": (160, 40, 50),
          "Tessel": (30, 140, 80), "Perfum": (205, 125, 145), "Northbeam": (60, 80, 180), "Strikeline": (30, 115, 190), "Rose": (175, 45, 65),
          "Nightwing": (90, 70, 180), "Starcaller": (40, 95, 210), "Crimson": (175, 30, 55)}


def sdir(name):
    return T if name == "Rose" else T / name


def base_of(stem):
    return re.sub(r"_(\d+|small|preview)$", "", stem)


def size_of(stem):
    m = re.search(r"_(\d+)$", stem)
    return int(m.group(1)) if m else 0


def collect(name):
    """-> dict kind -> {base: {size: Path}}"""
    d = sdir(name)
    kinds = {"Emotes": {}, "Sub_Badges": {}, "Channel_Point_Icons": {}, "Panels": {}, "Chat_Flair": {}}

    def add(kind, f):
        if f.suffix.lower() not in (".png", ".gif") or "preview" in f.stem or f.stem.endswith("_small"):
            return
        b = base_of(f.stem)
        kinds[kind].setdefault(b, {})[(size_of(f.stem), f.suffix.lower())] = f

    for f in (d / "Emotes").rglob("*"):
        if f.is_file():
            add("Emotes", f)
    for f in (d / "Badges").rglob("*"):
        if f.is_file():
            add("Sub_Badges", f)
    if name == "Rose":
        for f in T.glob("channel_points*"):
            add("Channel_Point_Icons", f)
        for f in T.glob("*.png"):
            if not f.stem.startswith("channel_points"):
                add("Panels", f)
    else:
        for f in (d / "Points").glob("*"):
            add("Channel_Point_Icons", f)
        for f in (d / "Panels").glob("*"):
            add("Panels", f)
    for f in (d / "Flair").glob("*") if (d / "Flair").is_dir() else []:
        add("Chat_Flair", f)
    return {k: v for k, v in kinds.items() if v}


def best(files):
    """largest file of a design"""
    return files[max(files, key=lambda k: (k[0], k[1] == ".gif"))]


def load(path):
    im = Image.open(path)
    if getattr(im, "is_animated", False):
        im.seek(im.n_frames // 2)
    return im.convert("RGBA")


def build_zip(name, kinds):
    zdir = OUT / name
    zdir.mkdir(parents=True, exist_ok=True)
    zp = zdir / "pack.zip"
    label = SETS[name].replace(" ", "_")
    n = {}
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for kind, designs in kinds.items():
            n[kind] = len(designs)
            for base, files in sorted(designs.items()):
                nice = re.sub(r"^(tier\d+_|bits?\d+k?_)", "", base)
                top = best(files)
                if top.suffix.lower() == ".gif":
                    for (sz, ext), f in sorted(files.items()):
                        if ext == ".gif":
                            z.write(f, "%s/%s/%s_%d.gif" % (label + "_Pack", kind, base, sz or 448))
                    for (sz, ext), f in sorted(files.items()):
                        if ext == ".png" and not any(k[1] == ".gif" and k[0] == sz for k in files):
                            z.write(f, "%s/%s/%s_%d.png" % (label + "_Pack", kind, base, sz or 448))
                    continue
                im = ss.clean_black(load(top))
                px = max(im.size)
                if kind == "Emotes":
                    sizes = (448, 112, 56, 28)
                elif kind == "Sub_Badges" or kind == "Chat_Flair":
                    sizes = (432, 72, 36, 18)
                elif kind == "Channel_Point_Icons":
                    sizes = (448, 112)
                else:
                    sizes = (None,)
                for s in sizes:
                    out = im if s is None else im.resize((s, s), Image.LANCZOS) if im.width == im.height else im
                    if s is not None and s > px:
                        continue
                    tmp = zdir / "_t.png"
                    out.save(tmp, optimize=True)
                    z.write(tmp, "%s/%s/%s%s.png" % (label + "_Pack", kind, base, "" if s is None else "_%d" % s))
        tmp = zdir / "_t.png"
        if tmp.exists():
            tmp.unlink()
    return zp, n


def put(canvas, im, xy, blur=14, op=0.5):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
    canvas = shadow(canvas, lay.split()[3], (0, 8), blur, (0, 0, 0), op)
    return Image.alpha_composite(canvas, lay)


def icon(path, s):
    im = ss.clean_black(load(path))
    return ss.fit(im, s, s)


def panel_card(path, w):
    im = ss.clean_black(load(path))
    return ss.fit(im, w, w)


def diverse(paths, thr=34):
    """Keep only emotes that look clearly different from the ones already chosen."""
    import numpy as np
    keep, sigs = [], []
    for p in paths:
        im = ss.clean_black(load(p))
        bg_ = Image.new("RGBA", im.size, (128, 128, 128, 255))
        bg_.alpha_composite(im)
        v = np.asarray(bg_.convert("RGB").resize((24, 24), Image.LANCZOS)).astype(float)
        if all(np.abs(v - o).mean() > thr for o in sigs):
            keep.append(p)
            sigs.append(v)
    return keep


def make_covers(name, kinds):
    zdir = OUT / name
    style = SETS[name]
    emotes_all = [best(f) for _, f in sorted(kinds["Emotes"].items())]
    emotes = diverse(emotes_all)
    PICK = {"Northbeam": ["aurora", "compass", "frost", "gg_north", "lost", "north_star", "summit", "night_watch"]}
    if name in PICK:                                      # hand-picked, clearly different designs
        byb = {base_of(p.stem): p for p in emotes_all}
        emotes = [byb[k] for k in PICK[name] if k in byb]
    for t in (22, 14):                                    # not enough clearly different ones: relax
        if len(emotes) < 6:
            emotes = diverse(emotes_all, t)
    if len(emotes) < 6:                                   # still too few: spread evenly over the whole set
        step = max(1, len(emotes_all) // 8)
        emotes = emotes_all[::step][:8]
    badges = [best(f) for _, f in sorted(kinds["Sub_Badges"].items()) if not re.search(r"bits|bit", _)]
    badges = ss.sort_badges(badges)
    points = [best(f) for _, f in sorted(kinds.get("Channel_Point_Icons", {}).items())]
    panels = [best(f) for _, f in sorted(kinds.get("Panels", {}).items())]
    main = COLORS[name]
    pal = (main, tuple(min(255, int(c * 0.45 + 150)) for c in main))
    nE, nB, nP, nC = len(kinds["Emotes"]), len(kinds["Sub_Badges"]), len(kinds.get("Panels", {})), len(kinds.get("Channel_Point_Icons", {}))

    def base(seed):
        dark = tuple(int(c * 0.17) for c in main)
        mid = tuple(int(c * 0.44) for c in main)
        img = radial((W, H), mid, dark, 0.35, 0.3, 1.1).convert("RGBA")
        d = ImageDraw.Draw(img)
        for x in range(-H, W, 52):
            d.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 6), width=2)
        return grain(vignette(img, 0.4, (2, 2, 8)), 4)

    def tt(img, s_, xy, size, col=g.SILVER, c2=(170, 180, 205), anchor="left", track=10):
        return g.txt(img, s_, xy, size, col, c2, anchor, track)

    emotes_full = emotes_all

    def grid(img, items, x0, y0, cols, cw, ch, fitw, fith, kind):
        for i, p in enumerate(items):
            e = ss.fit(ss.clean_black(load(p)), fitw, fith)
            img = put(img, e, (x0 + (i % cols) * cw + (cw - e.width) // 2, y0 + (i // cols) * ch + (ch - e.height) // 2), 7, 0.4)
        return img

    # cover 1: title and EVERY emote
    img = base(1)
    img = tt(img, style.upper() + " - EMOTES", (60, 100), 46)
    img = tt(img, "%d EMOTES  ·  EACH IN 448, 112, 56 AND 28 PX  ·  TRANSPARENT PNG" % nE, (62, 146), 18, pal[1], pal[1], track=5)
    n = len(emotes_full)
    cols = 6 if n > 10 else 5
    rows = (n + cols - 1) // cols
    cw = int((W - 120) / cols)
    ch = min(int((H - 230) / rows), cw)
    img = grid(img, emotes_full, 60, 200, cols, cw, ch, ch - 20, ch - 20, "e")
    img.convert("RGB").save(zdir / "cover_1.png", optimize=True)

    # cover 2: EVERY panel
    img = base(2)
    img = tt(img, style.upper() + " - PANELS", (60, 100), 46)
    img = tt(img, "%d CHANNEL PANELS  ·  READY TO UPLOAD" % nP, (62, 146), 18, pal[1], pal[1], track=5)
    n = len(panels)
    cols = 3 if n > 6 else 2
    rows = (n + cols - 1) // cols
    cw = int((W - 100) / cols)
    ch = min(int((H - 230) / rows), 150)
    img = grid(img, panels, 50, 200, cols, cw, ch, cw - 24, ch - 14, "p")
    img.convert("RGB").save(zdir / "cover_2.png", optimize=True)

    # cover 3: EVERY badge and channel point icon
    img = base(3)
    img = tt(img, style.upper() + " - BADGES & ICONS", (60, 100), 46)
    img = tt(img, "%d SUB BADGES (432, 72, 36, 18 PX)  ·  %d CHANNEL POINT ICONS" % (nB, nC), (62, 146), 18, pal[1], pal[1], track=5)
    allb = badges + [best(f) for _, f in sorted(kinds["Sub_Badges"].items()) if re.search(r"bits|bit", _)]
    n = len(allb)
    cols = 5
    rows = (n + cols - 1) // cols
    cw = 150
    img = grid(img, allb, (W - cols * cw) // 2 - 260, 210, cols, cw, 150, 126, 126, "b")
    img = grid(img, points, 960, 210, 2, 150, 150, 126, 126, "c")
    img.convert("RGB").save(zdir / "cover_3.png", optimize=True)

    # square thumbnail: its own design (big emote grid + badge row), not a crop of cover 1
    S_ = 1000
    img = base(4).resize((S_, S_), Image.LANCZOS)
    img = tt(img, style.upper(), (S_ // 2, 130), 64, anchor="center")
    img = tt(img, "TWITCH EMOTE PACK", (S_ // 2, 186), 26, pal[1], pal[1], anchor="center", track=12)
    pick = (emotes[::-1] + emotes)[:6]
    for i, p in enumerate(pick):
        e = icon(p, 250)
        img = put(img, e, (110 + (i % 3) * 270 + (250 - e.width) // 2, 250 + (i // 3) * 270 + (250 - e.height) // 2), 10, 0.45)
    nb = min(len(badges), 6)
    gx = (S_ - nb * 120) // 2
    for i, p in enumerate(badges[:nb]):
        b = icon(p, 96)
        img = put(img, b, (gx + i * 120 + (96 - b.width) // 2, 810), 6, 0.4)
    img = tt(img, "%d EMOTES · %d BADGES · %d PANELS" % (nE, nB, nP), (S_ // 2, 940), 22, (210, 214, 228), (210, 214, 228), anchor="center", track=6)
    img.convert("RGB").save(zdir / "thumb.png", optimize=True)
    return nE, nB, nP, nC


def listing(name, counts, zp):
    nE, nB, nP, nC = counts
    style = SETS[name]
    title = "%s Twitch Emote, Badge & Panel Pack — Stream Graphics, Digital Download" % style
    desc = """%s Twitch pack: ready-to-upload stream graphics in one consistent style.

WHAT YOU GET
- %d emotes, each as a transparent PNG in 4 sizes (448, 112, 56 and 28 px) - animated emotes as GIF where the design is animated
- %d sub badge designs (432 px plus the Twitch sizes 72, 36 and 18 px)
- %d channel point icons (448 and 112 px)
- %d channel panels (About, Rules, Links and more, ready to upload)

HOW TO USE
Download the zip, open the folder you need and upload the files to Twitch, Discord or YouTube. Emotes and badges already come in the sizes Twitch asks for.

PERSONAL USE: use the images on your own channel, server and community. Do not resell or redistribute the files.

Finished image files only. No source or project files are included.""" % (style, nE, nB, nC, nP)
    (OUT / name / "listing.txt").write_text(title + "\n\n" + desc, encoding="utf-8")
    return title


def main():
    names = [a for a in sys.argv[1:] if a in SETS] or list(SETS)
    for name in names:
        kinds = collect(name)
        zp, n = build_zip(name, kinds)
        counts = make_covers(name, kinds)
        title = listing(name, counts, zp)
        print(name, counts, "%.1f MB" % (zp.stat().st_size / 1e6), "-", title[:50], flush=True)


if __name__ == "__main__":
    main()

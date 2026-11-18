#!/usr/bin/env python3
"""Four showcase boards (1600x900) for every Twitch set in the portfolio, coloured from each set's own art.
Output: C:/Users/SaphiresSilver/Documents/twitch/Showcases/<Set>/board_1_brand.png .. board_4_emotes_badges.png
    python tools/make_set_showcases.py            # all
    python tools/make_set_showcases.py Snake Hood"""
import colorsys
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_banner_gig as g
from art import *  # noqa: F401,F403

T = g.P / "twitch"
D = g.P / "design"
OUTROOT = Path("C:/Users/SaphiresSilver/Documents/twitch/Showcases")
W, H = 1600, 900

SETS = {  # name: (display, brand folder in design/ or None)
    "Purple": ("PURPLE GOTHIC", None), "Floral": ("FLORAL", None), "Snake": ("SNAKE", None), "Slash": ("SLASH", None),
    "Helmet": ("HELMET", None), "Hood": ("HOODED GAMER", None), "Tessel": ("TESSEL", "Tessel"), "Perfum": ("PERFUM", "Perfum"),
    "Northbeam": ("NORTHBEAM", "Northbeam"), "Strikeline": ("STRIKELINE", "Football"), "Rose": ("ROSE", None),
}


# ------------------------------------------------------------------ finding the pieces
def first(*pats):
    for p in pats:
        for f in sorted(Path(p).parent.glob(Path(p).name)) if "*" in p else ([Path(p)] if Path(p).exists() else []):
            if f.exists():
                return f
    return None


def base_of(stem):
    return re.sub(r"_(\d+|small|preview)$", "", stem)


def size_of(stem):
    m = re.search(r"_(\d+)$", stem)
    return int(m.group(1)) if m else 0


def largest(files):
    """One file per design (the biggest size)."""
    best = {}
    for f in files:
        if f.suffix.lower() not in (".png", ".gif"):
            continue
        k = base_of(f.stem)
        if k not in best or size_of(f.stem) > size_of(best[k].stem):
            best[k] = f
    return [best[k] for k in sorted(best)]


def pieces(name):
    s = T / name
    brand = SETS[name][1]
    P = {}
    if name == "Rose":
        P["logo"] = g.P / "Roselogo1.png"
        P["banner"] = g.P / "TreesBanner.png"
        P["avatar"] = None
        P["screens"] = [s / "Screens" / n for n in ("starting_soon.png", "be_right_back.png", "offline.png")]
        P["overlay"] = T / "Overlay" / "wow_layout_1920x1080.png"
        P["panels"] = [f for f in sorted(T.glob("*.png")) if not f.stem.startswith("channel_points")]
        P["alert"] = first(str(T / "Alert" / "petals_alert.gif"))
        P["corner"] = first(str(T / "Corner" / "petals_corner.gif"))
        P["emotes"] = largest([f for f in (T / "Emotes").rglob("*") if f.is_file()])
        P["badges"] = largest([f for f in (T / "Badges").glob("*")])
        P["points"] = largest(list(T.glob("channel_points*")))
        return P
    if brand:
        P["logo"] = D / brand / (brand.lower() + "_logo.png")
        P["logo_bg"] = (246, 228, 222)
        if brand in ("Tessel", "Football"):
            P["logo"] = D / brand / (brand.lower() + "_logo_white.png")
            P["logo_bg"] = (14, 16, 30)
        elif brand == "Northbeam":
            P["logo_bg"] = (14, 16, 30)
        P["banner"] = D / brand / (brand.lower() + "_banner_twitch.png")
        P["avatar"] = D / brand / (brand.lower() + "_avatar.png")
    else:
        logos = {"Hood": g.P / "LogoGaming.png", "Floral": s / "Logo" / "logo.png"}
        P["logo"] = logos.get(name) or first(str(s / "Logo" / "*.png"))
        banners = {"Floral": s / "banner.png", "Snake": T / "Banner" / "snake_banner.png", "Helmet": T / "Banner" / "gamer_streamer_banner.png"}
        P["banner"] = banners.get(name) or first(str(s / "Banner" / "*.png"))
        P["avatar"] = None
    scr = s / "Screens"
    P["screens"] = [scr / n for n in ("starting_soon.png", "be_right_back.png", "offline.png")]
    P["overlay"] = first(str(s / "Overlay" / "*overlay_frame.png"), str(s / "Overlay" / "overlay_frame.png"), str(s / "Overlay" / "*.png"))
    P["panels"] = largest(list((s / "Panels").glob("*.png")))
    P["alert"] = first(str(s / "Alert" / "snake_alert.gif")) if name == "Snake" else first(str(s / "Alert" / "*.gif"))
    P["corner"] = first(str(s / "Corner" / "*.gif"))
    P["emotes"] = largest([f for f in (s / "Emotes").rglob("*") if f.is_file()])
    P["badges"] = largest(list((s / "Badges").glob("*")))
    P["points"] = largest(list((s / "Points").glob("*")))
    return P


# ------------------------------------------------------------------ colours
def palette(path):
    im = Image.open(path).convert("RGB").resize((96, 96))
    cnt = {}
    for r, g_, b in list(im.getdata()):
        h, s, v = colorsys.rgb_to_hsv(r / 255, g_ / 255, b / 255)
        if s < 0.25 or v < 0.2 or v > 0.97:
            continue
        k = (int(h * 12), int(s * 3))
        cnt[k] = cnt.get(k, 0) + 1 + s
    if not cnt:
        return (110, 150, 230), (240, 200, 110)
    k = max(cnt, key=cnt.get)
    h = (k[0] + 0.5) / 12
    main = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.7, 0.85))
    acc = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.35, 1.0))
    return main, acc


def bg(main, seed):
    dark = tuple(int(c * 0.16) for c in main)
    mid = tuple(int(c * 0.42) for c in main)
    img = radial((W, H), mid, dark, 0.35, 0.35, 1.1).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(-H, W, 56):
        d.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 6), width=2)
    return grain(vignette(img, 0.45, (2, 2, 8)), 4)


# ------------------------------------------------------------------ drawing helpers
def clean_black(im):
    """Older emotes/panels were saved with an opaque black square around them: make that border-connected black transparent."""
    import numpy as np
    from scipy import ndimage
    a = np.asarray(im)
    if a[0, 0, 3] != 255 or a[0, 0, :3].max() > 12:
        return im
    dark = (a[..., :3].max(axis=2) < 14) & (a[..., 3] == 255)
    lab, n = ndimage.label(dark)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(border))
    out = a.copy()
    out[bgm, 3] = 0
    alpha = Image.fromarray(out[..., 3]).filter(ImageFilter.GaussianBlur(0.6))
    res = Image.fromarray(out)
    res.putalpha(alpha)
    return res


def frame_of(path, mid=True, clean=False):
    im = Image.open(path)
    if getattr(im, "is_animated", False):
        im.seek(im.n_frames // 2 if mid else 0)
    im = im.convert("RGBA")
    return clean_black(im) if clean else im


def rounded(im, radius):
    m = Image.new("L", (im.width * 3, im.height * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width * 3 - 1, im.height * 3 - 1), radius=radius * 3, fill=255)
    im = im.copy()
    im.putalpha(ImageChops.multiply(im.split()[3], m.resize(im.size, Image.LANCZOS)))
    return im


def fit(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def card(path_or_im, w, h, back=(14, 16, 30), radius=14, frame=True, pad=6):
    im = frame_of(path_or_im) if not isinstance(path_or_im, Image.Image) else path_or_im
    out = Image.new("RGBA", (w, h), back + (255,))
    im = fit(im, w - 2 * pad, h - 2 * pad)
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return rounded(out, radius)


def drop(canvas, im, xy, blur=16, op=0.55, outline=(255, 255, 255, 40)):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
    canvas = shadow(canvas, lay.split()[3], (0, 10), blur, (0, 0, 0), op)
    canvas = Image.alpha_composite(canvas, lay)
    return canvas


def scene_overlay(path, w, h, seed=1):
    import make_overlay_gig as og
    base = og.scene(seed).copy()
    base.alpha_composite(Image.open(path).convert("RGBA"))
    return base.resize((w, h), Image.LANCZOS)


def head(img, title, sub, acc):
    img = g.txt(img, title, (90, 112), 48, g.SILVER, (160, 170, 200), "left", 12)
    img = g.txt(img, sub, (90, 156), 19, acc, acc, "left", 7)
    d = ImageDraw.Draw(img)
    d.line([(90, 178), (90 + 330, 178)], fill=acc + (255,), width=3)
    return img


# ------------------------------------------------------------------ boards
def board1(name, P, pal):
    main, acc = pal
    img = head(bg(main, 1), SETS[name][0], "TWITCH STREAM KIT  ·  LOGO, BANNER, AVATAR", acc)
    if P["logo"]:
        img = drop(img, card(P["logo"], 600, 600, P.get("logo_bg", (14, 16, 30)), 22, pad=18), (90, 200))
    if P["banner"]:
        img = drop(img, card(P["banner"], 780, 312, (14, 16, 30), 16, pad=0), (730, 214))
    av = None
    if P["avatar"]:
        av = frame_of(P["avatar"])
    elif P["logo"]:
        av = frame_of(P["logo"])
        bb = av.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox()
        av = av.crop(bb)
    if av is not None:
        for (sz, x, y) in ((300, 770, 560), (150, 1120, 640), (72, 1310, 680)):
            c = card(av, sz, sz, (14, 16, 30), sz // 2, pad=max(4, sz // 14))
            img = drop(img, c, (x, y), 8, 0.4)
    return img


def board2(name, P, pal):
    main, acc = pal
    img = head(bg(main, 2), "SCREENS & OVERLAY", "STARTING SOON  ·  BE RIGHT BACK  ·  OFFLINE  ·  STREAM OVERLAY", acc)
    cw, ch = 560, 315
    items = [card(p, cw, ch, pad=0) for p in P["screens"] if p and p.exists()]
    if P["overlay"]:
        items.append(rounded(scene_overlay(P["overlay"], cw, ch, 3), 14))
    for i, c in enumerate(items[:4]):
        img = drop(img, c, (210 + (i % 2) * (cw + 60), 210 + (i // 2) * (ch + 28)), 14, 0.5)
    return img


def board3(name, P, pal):
    main, acc = pal
    img = head(bg(main, 3), "PANELS & ALERTS", "CHANNEL PANELS  ·  ANIMATED ALERT  ·  CORNER ANIMATION", acc)
    panels = P["panels"][:6]
    for i, p in enumerate(panels):
        im = frame_of(p, clean=True)
        c = card(im, 430, 145, (14, 16, 30), 12, pad=4)
        img = drop(img, c, (90 + (i % 2) * 450, 215 + (i // 2) * 165), 8, 0.45)
    y = 210
    if P["alert"]:
        img = drop(img, card(P["alert"], 560, 252, pad=0), (1000, y), 12, 0.5)
        y += 280
    if P["corner"]:
        img = drop(img, card(P["corner"], 560, 254, pad=0), (1000, y), 12, 0.5)
    return img


def sort_badges(files):
    def key(f):
        m = re.match(r"(\d+(?:_\d+)?)(month|year)", f.stem)
        if not m:
            return -1
        n = float(m.group(1).replace("_", "."))
        return n / 12 if m.group(2) == "month" else n
    return sorted(files, key=key)


def board4(name, P, pal):
    main, acc = pal
    img = head(bg(main, 4), "EMOTES & BADGES", "EMOTES  ·  SUB BADGES  ·  CHANNEL POINTS", acc)
    em = P["emotes"]
    if len(em) > 12:
        step = len(em) / 12
        em = [em[int(i * step)] for i in range(12)]
    for i, f in enumerate(em):
        e = fit(frame_of(f, clean=True), 160, 160)
        img = drop(img, e, (100 + (i % 6) * 235 + (160 - e.width) // 2, 205 + (i // 6) * 180 + (160 - e.height) // 2), 8, 0.4, None)
    x = 100
    for f in sort_badges(P["badges"])[:7]:
        b = fit(frame_of(f, clean=True), 104, 104)
        img = drop(img, b, (x, 585), 6, 0.4)
        x += 124
    x += 40
    for f in P["points"][:4]:
        b = fit(frame_of(f, clean=True), 104, 104)
        img = drop(img, b, (x, 585), 6, 0.4)
        x += 124
    img = g.txt(img, "SUB BADGES", (100, 725), 15, acc, acc, "left", 6)
    img = g.txt(img, "CHANNEL POINTS", (100 + 7 * 124 + 40, 725), 15, acc, acc, "left", 6)
    return img


def main():
    names = [a for a in sys.argv[1:] if a in SETS] or list(SETS)
    for name in names:
        P = pieces(name)
        src = P["banner"] or P["logo"]
        pal = palette(src)
        out = OUTROOT / name
        out.mkdir(parents=True, exist_ok=True)
        for fn, f in (("board_1_brand", board1), ("board_2_screens", board2), ("board_3_panels_alerts", board3), ("board_4_emotes_badges", board4)):
            try:
                f(name, P, pal).convert("RGB").save(out / (fn + ".png"), optimize=True)
            except Exception as e:  # a missing piece should not stop the other sets
                print("  FAILED", name, fn, repr(e))
        print("done", name, "emotes", len(P["emotes"]), "panels", len(P["panels"]), "badges", len(P["badges"]), flush=True)


if __name__ == "__main__":
    main()

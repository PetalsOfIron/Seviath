#!/usr/bin/env python3
"""Four showcase boards (1600x900) for each company brand kit (Tessel, Perfum, Northbeam, Strikeline).
Output: C:/Users/SaphiresSilver/Documents/twitch/CompanyKits/<Brand>/board_1_identity.png .. board_4_print_presentation.png
    python tools/make_company_showcases.py [Tessel Perfum Northbeam Strikeline]"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

import make_banner_gig as g
import make_set_showcases as ss
from art import *  # noqa: F401,F403

D = g.P / "design"
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/CompanyKits")
W, H = 1600, 900
KITS = {"Tessel": ("TESSEL", "Tessel", "tessel", "FOOTBALL BOOTS"), "Perfum": ("PERFUM", "Perfum", "perfum", "LUXURY FRAGRANCE"),
        "Northbeam": ("NORTHBEAM", "Northbeam", "northbeam", "CONSULTING"), "Strikeline": ("STRIKELINE", "Football", "football", "FOOTBALL COMPANY")}
LIGHT = (240, 240, 244)
DARK = (14, 16, 30)


def f(folder, key, name):
    p = D / folder / ("%s_%s.png" % (key, name))
    return p if p.exists() else None


def card(path, w, h, back=DARK, radius=12, pad=8):
    return ss.card(path, w, h, back, radius, pad=pad)


def auto_back(path):
    """Light card for dark artwork, dark card for light artwork (by the brightness of the visible pixels)."""
    import numpy as np
    a = np.asarray(Image.open(path).convert("RGBA")).astype(float)
    if a.shape[0] > a.shape[1] * 1.05:          # tall logo: judge the text at the bottom, not the emblem
        a = a[int(a.shape[0] * 0.74):]
    m = a[..., 3] > 128
    if not m.any():
        return LIGHT
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[m].mean()
    return DARK if lum > 150 else LIGHT


def swatches(img, path, xy, acc, n=5):
    plate = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle((xy[0] - 14, xy[1] - 12, xy[0] + 5 * 82 - 4, xy[1] + 112), radius=14, fill=(236, 238, 244, 255))
    img = Image.alpha_composite(img, plate)
    im = Image.open(path).convert("RGB").resize((120, 120))
    q = im.quantize(colors=n + 3, method=Image.MEDIANCUT)
    pal = q.getpalette()
    cnt = sorted(q.getcolors(), reverse=True)
    cols = []
    for c, idx in cnt:
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        if all(sum(abs(rgb[i] - o[i]) for i in range(3)) > 60 for o in cols):
            cols.append(rgb)
        if len(cols) == n:
            break
    d = ImageDraw.Draw(img)
    x, y = xy
    for rgb in cols:
        d.ellipse((x, y, x + 64, y + 64), fill=rgb + (255,), outline=(120, 124, 140, 255), width=2)
        x += 82
    x = xy[0]
    for rgb in cols:
        img = g.txt(img, "#%02X%02X%02X" % rgb, (x + 32, y + 90), 12, (40, 44, 60), (40, 44, 60), "center", 2)
        x += 82
    return img


def b1(kit, pal):
    title, folder, key, tag = KITS[kit]
    main, acc = pal
    img = ss.head(ss.bg(main, 1), title + " BRAND KIT", "BRAND IDENTITY  ·  LOGO, VERSIONS, ICONS, COLORS", acc)
    logo = f(folder, key, "logo")
    light_card = kit in ("Tessel", "Perfum", "Strikeline")
    img = ss.drop(img, card(logo, 500, 520, auto_back(logo), 18, 22), (90, 200))
    # versions
    versions = [("logo_white", main_dark(main), "WHITE"), ("logo_black", LIGHT, "BLACK"), ("logo_dark", None, "DARK")]
    x = 630
    for name, back, label in versions:
        p = f(folder, key, name)
        if p:
            img = ss.drop(img, card(p, 215, 215, back or DARK, 12, 14), (x, 200), 10, 0.45)
            img = g.chip(img, label, (x + 8, 208), 13, acc)
        x += 235
    wm = f(folder, key, "wordmark")
    if wm:
        img = ss.drop(img, card(wm, 685, 190, auto_back(wm), 12, 20), (630, 440), 10, 0.45)
        img = g.chip(img, "WORDMARK", (638, 448), 13, acc)
    img = swatches(img, f(folder, key, "banner_twitch"), (630, 665), acc)
    av = f(folder, key, "avatar")
    xx = 1090
    for sz in (100, 64, 36):
        img = ss.drop(img, ss.rounded(ss.fit(Image.open(av).convert("RGBA"), sz, sz), sz // 2), (xx, 690 + (100 - sz) // 2), 6, 0.4)
        xx += sz + 24
    fav = f(folder, key, "favicon_192")
    if fav:
        img = ss.drop(img, ss.fit(Image.open(fav).convert("RGBA"), 64, 64), (xx, 700), 6, 0.4)
    return img


def main_dark(main):
    return tuple(int(c * 0.35) for c in main)


def b2(kit, pal):
    title, folder, key, tag = KITS[kit]
    main, acc = pal
    img = ss.head(ss.bg(main, 2), "GUIDELINES & STATIONERY", "BRAND GUIDELINES  ·  BUSINESS CARDS  ·  EMAIL SIGNATURE  ·  FAVICON", acc)
    img = ss.drop(img, card(f(folder, key, "brand_guidelines"), 700, 467, DARK, 12, 0), (90, 210))
    img = ss.drop(img, card(f(folder, key, "business_card_front"), 330, 188, DARK, 10, 0), (830, 210))
    img = ss.drop(img, card(f(folder, key, "business_card_back"), 330, 188, DARK, 10, 0), (1180, 210))
    img = ss.drop(img, card(f(folder, key, "email_signature"), 680, 204, LIGHT, 10, 8), (830, 430))
    x = 830
    for name in ("favicon_512", "favicon_192", "favicon_32"):
        p = f(folder, key, name)
        sz = {"favicon_512": 120, "favicon_192": 84, "favicon_32": 32}[name]
        img = ss.drop(img, ss.fit(Image.open(p).convert("RGBA"), sz, sz), (x, 670 + (120 - sz) // 2), 6, 0.4)
        x += sz + 28
    og = f(folder, key, "og_image")
    if og:
        img = ss.drop(img, card(og, 300, 158, DARK, 10, 0), (1210, 664))
    img = g.txt(img, "FAVICONS", (830, 820), 14, acc, acc, "left", 6)
    img = g.txt(img, "SHARE IMAGE", (1210, 840), 14, acc, acc, "left", 6)
    return img


def b3(kit, pal):
    title, folder, key, tag = KITS[kit]
    main, acc = pal
    img = ss.head(ss.bg(main, 3), "SOCIAL MEDIA KIT", "BANNERS FOR EVERY PLATFORM  ·  POST  ·  STORY  ·  YOUTUBE", acc)
    items = [("banner_twitter", 640, 213, "X"), ("banner_linkedin", 640, 160, "LINKEDIN"), ("banner_facebook", 640, 243, "FACEBOOK")]
    y = 205
    for name, w, h, label in items:
        p = f(folder, key, name)
        img = ss.drop(img, card(p, w, h, DARK, 10, 0), (90, y), 10, 0.45)
        img = g.chip(img, label, (98, y + 8), 13, acc)
        y += h + 18
    img = ss.drop(img, card(f(folder, key, "post_square"), 300, 300, DARK, 10, 0), (790, 205))
    img = ss.drop(img, card(f(folder, key, "story"), 169, 300, DARK, 10, 0), (1110, 205))
    img = g.chip(img, "POST", (798, 213), 13, acc)
    img = g.chip(img, "STORY", (1118, 213), 13, acc)
    yt = f(folder, key, "banner_youtube")
    img = ss.drop(img, card(yt, 355, 200, DARK, 10, 0), (790, 540))
    img = g.chip(img, "YOUTUBE", (798, 548), 13, acc)
    tw = f(folder, key, "banner_twitch")
    img = ss.drop(img, card(tw, 360, 144, DARK, 10, 0), (1170, 540))
    img = g.chip(img, "TWITCH", (1178, 548), 13, acc)
    return img


def b4(kit, pal):
    title, folder, key, tag = KITS[kit]
    main, acc = pal
    img = ss.head(ss.bg(main, 4), "PRINT & PRESENTATION", "POSTERS  ·  LETTERHEAD  ·  SLIDES" + ("  ·  TICKET & SCARF" if kit == "Strikeline" else ""), acc)
    portraits = [f(folder, key, n) for n in ("poster", "product_poster", "match_day_poster", "product_tag", "letterhead")]
    portraits = [p for p in portraits if p][:4]
    ars = [Image.open(p).width / Image.open(p).height for p in portraits]
    h = int(min(380, (1000 - 20 * (len(portraits) - 1)) / sum(ars)))     # the row must end before the slides at x=1130
    x = 90
    for p, ar in zip(portraits, ars):
        w = int(ar * h)
        img = ss.drop(img, card(p, w, h, DARK, 8, 0), (x, 205 + (380 - h) // 2), 12, 0.5)
        x += w + 20
    sx = max(x, 1100)
    img = ss.drop(img, card(f(folder, key, "slide_title"), 380, 214, DARK, 10, 0), (1130, 205))
    img = ss.drop(img, card(f(folder, key, "slide_content"), 380, 214, DARK, 10, 0), (1130, 439))
    if kit == "Strikeline":
        img = ss.drop(img, card(f(folder, key, "ticket"), 430, 163, DARK, 10, 0), (90, 625))
        img = ss.drop(img, card(f(folder, key, "scarf"), 560, 140, DARK, 10, 0), (540, 635))
    return img


def main():
    names = [a for a in sys.argv[1:] if a in KITS] or list(KITS)
    for kit in names:
        title, folder, key, tag = KITS[kit]
        pal = ss.palette(f(folder, key, "banner_twitch"))
        out = OUT / kit
        out.mkdir(parents=True, exist_ok=True)
        for fn, fun in (("board_1_identity", b1), ("board_2_guidelines_stationery", b2), ("board_3_social", b3), ("board_4_print_presentation", b4)):
            try:
                fun(kit, pal).convert("RGB").save(out / (fn + ".png"), optimize=True)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print("  FAILED", kit, fn, repr(e))
        print("done", kit, flush=True)


if __name__ == "__main__":
    main()

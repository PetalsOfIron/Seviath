#!/usr/bin/env python3
"""Gig gallery images (1280x769) for a banner-design gig, built from the best banners in the portfolio.
Output: C:/Users/SaphiresSilver/Documents/twitch/BannerGig/gig_1_cover.png, gig_2_styles.png, gig_3_brands.png"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/BannerGig")
W, H = 1280, 769
GOLD, TEAL = (240, 190, 96), (110, 214, 240)
SILVER = (230, 236, 248)
HEAD = "bahnschrift.ttf"
P = ROOT / "images"

BANNERS = {
    "starcaller": P / "twitch/Starcaller/Banner/starcaller_banner.png",
    "snake": P / "twitch/Banner/snake_banner.png",
    "floral": P / "twitch/Floral/banner.png",
    "purple": P / "twitch/Purple/Banner/purple_banner.png",
    "slash": P / "twitch/Slash/Banner/banner.png",
    "nightwing": P / "twitch/Nightwing/Banner/nightwing_banner.png",
    "strikeline": P / "design/Football/football_banner_twitch.png",
    "northbeam": P / "design/Northbeam/northbeam_banner_twitch.png",
    "perfum": P / "design/Perfum/perfum_banner_twitch.png",
    "tessel": P / "design/Tessel/tessel_banner_twitch.png",
    "hooded": P / "twitch/Banner/petals_gamer_banner.png",
    "trees": P / "TreesBanner.png",
    "clean": P / "twitch/Hood/Banner/banner.png",
}


def bg():
    img = radial((W, H), (34, 40, 72), (9, 11, 24), 0.35, 0.4, 1.0).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(-H, W, 46):  # faint diagonal lines
        d.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 7), width=2)
    return grain(vignette(img, 0.4, (2, 3, 10)), 4)


def card(path, w, h, radius=16, pad=0):
    im = Image.open(path).convert("RGBA")
    s = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (14, 16, 30, 255))
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    m = Image.new("L", (w * 3, h * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), radius=radius * 3, fill=255)
    out.putalpha(m.resize((w, h), Image.LANCZOS))
    return out


def put(img, im, xy, op=0.6):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
    img = shadow(img, lay.split()[3], (0, 14), 18, (0, 0, 0), op)
    img = Image.alpha_composite(img, lay)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((xy[0], xy[1], xy[0] + im.width - 1, xy[1] + im.height - 1), radius=16, outline=(255, 255, 255, 40), width=2)
    return img


def txt(img, s, xy, size, col=SILVER, col2=None, anchor="left", track=8):
    m = text_mask(img.size, s, font(HEAD, size), xy, track=track, anchor=anchor)
    img = shadow(img, m, (0, max(2, size // 20)), max(3, size // 22), (0, 0, 0), 0.6)
    return fill_mask(img, m, col, col2)


def twidth(img, s, size, track=4):
    m = text_mask(img.size, s, font(HEAD, size), (10, 100), track=track, anchor="left")
    b = m.getbbox()
    return b[2] - b[0]


def chip(img, s, xy, size=18, col=GOLD):
    wdt = twidth(img, s, size) + 28
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle((xy[0], xy[1], xy[0] + wdt, xy[1] + size + 16), radius=(size + 16) // 2, fill=(8, 10, 22, 230), outline=col + (255,), width=2)
    img = Image.alpha_composite(img, lay)
    return txt(img, s, (xy[0] + 14, xy[1] + size + 4), size, col, col, "left", 4)


def cover():
    img = bg()
    x0 = 64
    img = txt(img, "CUSTOM", (x0, 238), 40, GOLD, (200, 140, 60), track=18)
    img = txt(img, "STREAM", (x0, 340), 84, SILVER, (150, 168, 210), track=3)
    img = txt(img, "BANNERS", (x0, 430), 84, SILVER, (150, 168, 210), track=3)
    d = ImageDraw.Draw(img)
    d.line([(x0, 462), (x0 + 300, 462)], fill=GOLD + (255,), width=4)
    for i, s in enumerate(("TWITCH  ·  YOUTUBE", "X  ·  FACEBOOK  ·  LINKEDIN")):
        img = txt(img, s, (x0, 520 + i * 40), 21, TEAL, TEAL, track=6)
    img = txt(img, "DESIGNED AROUND YOUR BRAND", (x0, 670), 16, (170, 180, 210), (170, 180, 210), track=5)
    cw, ch = 640, 213
    for i, (k, dx) in enumerate((("starcaller", 30), ("snake", 0), ("nightwing", 30))):
        img = put(img, card(BANNERS[k], cw, ch), (590 + dx, 26 + i * (ch + 40)))
    return img


def styles():
    img = bg()
    img = txt(img, "BANNER EXAMPLES", (W // 2, 76), 46, SILVER, (150, 168, 210), "center", 14)
    d = ImageDraw.Draw(img)
    d.line([(W // 2 - 180, 100), (W // 2 + 180, 100)], fill=GOLD + (255,), width=3)
    cw, ch = 500, 200
    items = [("floral", "FLORAL"), ("purple", "GOTHIC"), ("slash", "BOLD"), ("hooded", "CHARACTER"), ("trees", "BOTANICAL"), ("clean", "CLASSIC")]
    for i, (k, label) in enumerate(items):
        x = 130 + (i % 2) * (cw + 20)
        y = 126 + (i // 2) * (ch + 18)
        img = put(img, card(BANNERS[k], cw, ch), (x, y), 0.5)
        img = chip(img, label, (x + cw - twidth(img, label, 16) - 28 - 14, y + 14), 16)
    return img


def brands():
    img = bg()
    img = txt(img, "BRAND BANNERS", (W // 2, 76), 46, SILVER, (150, 168, 210), "center", 14)
    d = ImageDraw.Draw(img)
    d.line([(W // 2 - 180, 100), (W // 2 + 180, 100)], fill=GOLD + (255,), width=3)
    cw, ch = 560, 224
    items = [("strikeline", "FOOTBALL"), ("northbeam", "CONSULTING"), ("perfum", "LUXURY"), ("tessel", "SPORTSWEAR")]
    for i, (k, label) in enumerate(items):
        x = 70 + (i % 2) * (cw + 20)
        y = 136 + (i // 2) * (ch + 22)
        img = put(img, card(BANNERS[k], cw, ch), (x, y), 0.5)
        img = chip(img, label, (x + cw - twidth(img, label, 16) - 28 - 14, y + 14), 16)
    sizes = ["TWITCH 1200×480", "YOUTUBE 2560×1440", "X 1500×500", "FACEBOOK 820×312", "LINKEDIN 1584×396"]
    x = 70
    for s in sizes:
        img = chip(img, s, (x, 668), 16, TEAL)
        x += twidth(img, s, 16) + 28 + 12
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, f in (("gig_1_cover", cover), ("gig_2_styles", styles), ("gig_3_brands", brands)):
        f().convert("RGB").save(OUT / (name + ".png"), optimize=True)
        print("saved", name)


if __name__ == "__main__":
    main()

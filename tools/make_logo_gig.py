#!/usr/bin/env python3
"""Gig gallery images (1280x769) for a logo-design gig. 13 different logos, none repeated across the three images.
Output: C:/Users/SaphiresSilver/Documents/twitch/LogoGig/logo_1_cover.png, logo_2_mascots.png, logo_3_brands.png"""
from pathlib import Path

from PIL import Image, ImageDraw

import make_banner_gig as g
from art import *  # noqa: F401,F403

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/LogoGig")
P = g.P
W, H = g.W, g.H


def logo_img(path, size):
    im = Image.open(path).convert("RGBA")
    bb = im.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    s = min(size[0] / im.width, size[1] / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def tile(path, w, h, bgcol=(16, 18, 34), pad=26, radius=18):
    src = Image.open(path).convert("RGBA")
    if src.getpixel((2, 2))[3] == 255 and src.getpixel((src.width - 3, src.height - 3))[3] == 255:
        bgcol = src.getpixel((2, 2))[:3]        # opaque logo: let the card take its own background colour
    out = Image.new("RGBA", (w, h), bgcol + (255,))
    im = logo_img(path, (w - 2 * pad, h - 2 * pad))
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    m = Image.new("L", (w * 3, h * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), radius=radius * 3, fill=255)
    out.putalpha(m.resize((w, h), Image.LANCZOS))
    return out


def cover():
    img = g.bg()
    x0 = 64
    img = g.txt(img, "CUSTOM", (x0, 238), 40, g.GOLD, (200, 140, 60), track=18)
    img = g.txt(img, "LOGO", (x0, 340), 96, g.SILVER, (150, 168, 210), track=4)
    img = g.txt(img, "DESIGN", (x0, 436), 96, g.SILVER, (150, 168, 210), track=4)
    d = ImageDraw.Draw(img)
    d.line([(x0, 468), (x0 + 300, 468)], fill=g.GOLD + (255,), width=4)
    for i, s in enumerate(("MASCOT  ·  EMBLEM  ·  WORDMARK", "FOR STREAMERS AND BRANDS")):
        img = g.txt(img, s, (x0, 524 + i * 40), 17, g.TEAL, g.TEAL, track=5)
    img = g.txt(img, "DESIGNED AROUND YOUR BRAND", (x0, 670), 16, (170, 180, 210), (170, 180, 210), track=5)
    for path, size, xy in ((P / "twitch/Starcaller/Logo/starcaller_logo.png", 390, (830, 14)),
                           (P / "twitch/Nightwing/Logo/nightwing_logo.png", 310, (500, 370)),
                           (P / "twitch/Helmet/Logo/logo.png", 300, (880, 440))):
        im = logo_img(path, (size, size))
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        lay.alpha_composite(im, xy)
        img = shadow(img, lay.split()[3], (0, 14), 20, (0, 0, 0), 0.5)
        img = Image.alpha_composite(img, lay)
    return img


def grid(title, items, cols, cw, ch, x0, y0, gx, gy, chips=True):
    img = g.bg()
    img = g.txt(img, title, (W // 2, 76), 46, g.SILVER, (150, 168, 210), "center", 14)
    d = ImageDraw.Draw(img)
    d.line([(W // 2 - 180, 100), (W // 2 + 180, 100)], fill=g.GOLD + (255,), width=3)
    for i, (path, label, bgc) in enumerate(items):
        x = x0 + (i % cols) * (cw + gx)
        y = y0 + (i // cols) * (ch + gy)
        img = g.put(img, tile(path, cw, ch, bgc), (x, y), 0.5)
        if chips:
            img = g.chip(img, label, (x + 12, y + 12), 15)
    return img


def mascots():
    dark = (16, 18, 34)
    items = [(P / "twitch/Floral/Logo/logo.png", "FLORAL", dark), (P / "twitch/Snake/Logo/logo.png", "PAINTED", dark),
             (P / "twitch/Purple/Logo/purple_logo.png", "GOTHIC", dark), (P / "twitch/Slash/Logo/logo.png", "BOLD", dark),
             (P / "LogoGaming.png", "CHARACTER", dark), (P / "Roselogo1.png", "BOTANICAL", dark)]
    return grid("MASCOT & STREAMER LOGOS", items, 3, 290, 290, 185, 130, 20, 20)


def circle_logo(icon_path, c1, c2, ring, name, d=1000):
    """Round emblem: gradient disc, double ring, the brand's own icon in the middle."""
    S = 3
    big = d * S
    disc = radial((big, big), c1, c2, 0.5, 0.4, 0.9).convert("RGBA")
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    m = Image.new("L", (big, big), 0)
    ImageDraw.Draw(m).ellipse((0, 0, big - 1, big - 1), fill=255)
    out.paste(disc, (0, 0), m)
    dr = ImageDraw.Draw(out)
    dr.ellipse((0, 0, big - 1, big - 1), outline=ring + (255,), width=18 * S // 3)
    dr.ellipse((46 * S, 46 * S, big - 46 * S, big - 46 * S), outline=ring + (140,), width=6 * S // 3)
    icon = logo_img(icon_path, (int(big * 0.58), int(big * 0.58)))
    out.alpha_composite(icon, ((big - icon.width) // 2, (big - icon.height) // 2))
    out = out.resize((d, d), Image.LANCZOS)
    p = OUT / "_src" / (name + ".png")
    p.parent.mkdir(parents=True, exist_ok=True)
    out.save(p)
    return p


def brands():
    D = P / "design"
    circ = [circle_logo(D / "Football/football_crest.png", (26, 64, 110), (8, 22, 44), (0, 168, 232), "strikeline"),
            circle_logo(D / "Northbeam/northbeam_icon.png", (46, 56, 140), (14, 20, 66), (130, 190, 255), "northbeam"),
            D / "Perfum/perfum_emblem.png", D / "Tessel/tessel_emblem.png"]
    names = [("Football", "football", "STRIKELINE", (12, 34, 60)), ("Northbeam", "northbeam", "NORTHBEAM", (22, 30, 84)),
             ("Perfum", "perfum", "PERFUM", (246, 228, 222)), ("Tessel", "tessel", "TESSEL", (10, 56, 38))]
    items = [(circ[i], names[i][2], (16, 18, 34)) for i in range(4)]
    img = grid("BRAND LOGOS", items, 4, 270, 270, 70, 126, 20, 20)
    for i, (folder, key, label, col) in enumerate(names):
        x = 70 + i * 290
        path = D / folder / ("perfum_logo.png" if folder == "Perfum" else key + "_logo_white.png")
        img = g.put(img, tile(path, 270, 270, col, pad=22, radius=18), (x, 416), 0.45)
    x = 70
    for s_ in ("ROUND EMBLEM", "FULL LOGO", "WHITE VERSION", "BLACK VERSION", "AVATAR"):
        img = g.chip(img, s_, (x, 706), 16, g.TEAL)
        x += g.twidth(img, s_, 16) + 28 + 12
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, f in (("logo_1_cover", cover), ("logo_2_mascots", mascots), ("logo_3_brands", brands)):
        im = f().convert("RGB")
        try:
            im.save(OUT / (name + ".png"), optimize=True)
            print("saved", name)
        except OSError:                     # file is open in a viewer: save next to it instead
            im.save(OUT / (name + "_new.png"), optimize=True)
            print("saved", name + "_new (original is open in another program)")


if __name__ == "__main__":
    main()

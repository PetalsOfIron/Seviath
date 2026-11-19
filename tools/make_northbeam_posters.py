#!/usr/bin/env python3
"""Better Northbeam posters (event, sale, new arrival) in the kit's own look: blue gradient, light beams, colour logo,
cyan corner brackets, silver title.   python tools/make_northbeam_posters.py"""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Missing/Northbeam")
LOGO = ROOT / "images/design/Northbeam/northbeam_logo.png"
ICON = ROOT / "images/design/Northbeam/northbeam_icon.png"
SER = "C:/Windows/Fonts/georgiab.ttf"
SAN = "C:/Windows/Fonts/bahnschrift.ttf"
CY = (120, 226, 240)
W, H = 2480, 3508


def f(p, s):
    x = ImageFont.truetype(p, s)
    if p == SAN:
        try:
            x.set_variation_by_name("Bold")
        except Exception:
            pass
    return x


def bg():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(46 - 30 * t), int(66 - 44 * t), int(150 - 90 * t)))
    img = img.convert("RGBA")
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    rnd = random.Random(7)
    for x in (480, 900, 1300, 1700, 2050):
        bd.polygon([(x - 60, 0), (x + 60, 0), (x + 420 + rnd.randint(-80, 80), H * 0.75), (x - 420, H * 0.75)], fill=(160, 210, 255, 26))
    img.alpha_composite(beams.filter(ImageFilter.GaussianBlur(40)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W // 2 - 900, 700, W // 2 + 900, 2300], fill=(110, 160, 255, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(220)))
    return img


def brackets(d):
    m, L, w = 150, 260, 10
    for sx in (m, W - m):
        for sy in (m, H - m):
            dx = L if sx < W / 2 else -L
            dy = L if sy < H / 2 else -L
            d.line([(sx, sy), (sx + dx, sy)], fill=CY, width=w)
            d.line([(sx, sy), (sx, sy + dy)], fill=CY, width=w)


def silver(img, text, cx, cy, size):
    font = f(SER, size)
    d = ImageDraw.Draw(img)
    tw = d.textlength(text, font=font)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((cx, cy), text, font=font, fill=255, anchor="mm")
    g = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(g)
    top, bot = cy - size // 2, cy + size // 2
    for y in range(max(0, top), min(H, bot)):
        t = (y - top) / max(1, bot - top)
        v = int(250 - 90 * abs(t - 0.4))
        gd.line([(0, y), (W, y)], fill=(v, v, min(255, v + 12), 255))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste((0, 8, 40, 170), (6, 10), mask)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    img.paste(g, (0, 0), mask)


def poster(name, title, line, extra):
    img = bg()
    d = ImageDraw.Draw(img)
    brackets(d)
    lg = Image.open(LOGO).convert("RGBA")
    k = 1250 / lg.width
    lg = lg.resize((int(lg.width * k), int(lg.height * k)), Image.LANCZOS)
    img.alpha_composite(lg, (W // 2 - lg.width // 2, 330))
    d = ImageDraw.Draw(img)
    silver(img, title, W // 2, 2080, 330 if len(title) < 11 else 250)
    d = ImageDraw.Draw(img)
    d.line([(520, 2330), (W // 2 - 60, 2330)], fill=CY, width=6)
    d.line([(W // 2 + 60, 2330), (W - 520, 2330)], fill=CY, width=6)
    d.polygon([(W // 2, 2306), (W // 2 + 24, 2330), (W // 2, 2354), (W // 2 - 24, 2330)], fill=CY)
    t = line
    tx = " ".join(t.upper())
    d.text((W // 2, 2490), tx, font=f(SER, 84), fill=(228, 238, 255), anchor="mm")
    d.text((W // 2, 2700), extra, font=f(SAN, 74), fill=CY, anchor="mm")
    d.line([(300, 3190), (W - 300, 3190)], fill=(120, 170, 230), width=3)
    d.text((300, 3290), "NORTHBEAM.EXAMPLE", font=f(SAN, 56), fill=(200, 220, 250), anchor="lm")
    d.text((W - 300, 3290), "hello@northbeam.example", font=f(SAN, 56), fill=(200, 220, 250), anchor="rm")
    img.convert("RGB").save(OUT / name, optimize=True)


OUT.mkdir(parents=True, exist_ok=True)
poster("event_poster_A3.png", "Big Event", "Guided by light", "00 / 00 / 0000  -  YOUR VENUE, YOUR CITY")
poster("sale_poster_A3.png", "Winter Sale", "Up to 00% off", "THIS WEEK ONLY  -  IN STORE AND ONLINE")
poster("product_poster_A3.png", "New Arrival", "Now available", "DISCOVER THE NEW COLLECTION")
print("ok")

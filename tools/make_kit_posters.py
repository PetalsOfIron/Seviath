#!/usr/bin/env python3
"""Event / sale / new-arrival posters (A3) for the Tessel, Perfum and Strikeline kits in their own look: brand gradient, light beams,
logo, corner brackets, shadowed title. Light brands get a light poster.   python tools/make_kit_posters.py"""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import make_company_extras as e

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Missing")
W, H = 2480, 3508
KITS = {"Tessel": ("Tessel", "TESSEL.EXAMPLE", "hello@tessel.example"), "Perfum": ("Perfum", "PERFUM.EXAMPLE", "hello@perfum.example"), "Strikeline": ("Football", "STRIKELINE.EXAMPLE", "hello@strikeline.example")}


def theme(brand):
    src = Image.open(e.pick(brand, "banner_twitter", "banner_youtube")).convert("RGB").resize((120, 40))
    mean = sum(e.lum(p) for p in src.getdata()) / 4800
    dark, acc = e.palette(e.pick(brand, "banner_twitter", "banner_youtube"))
    return mean > 150, dark, acc


def clamp(c):
    return tuple(max(0, min(255, int(v))) for v in c)


def background(light, dark, acc):
    top = clamp(tuple(v * 1.0 + (255 - v) * 0.88 for v in acc)) if light else clamp(tuple(v * 0.9 + 25 for v in dark))
    bot = clamp(tuple(v * 1.0 + (255 - v) * 0.7 for v in acc)) if light else clamp(tuple(v * 0.35 for v in dark))
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))
    img = img.convert("RGBA")
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    for x in (480, 900, 1300, 1700, 2050):
        bd.polygon([(x - 60, 0), (x + 60, 0), (x + 420, H * 0.75), (x - 420, H * 0.75)], fill=(255, 255, 255, 40 if light else 22))
    img.alpha_composite(beams.filter(ImageFilter.GaussianBlur(40)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W // 2 - 900, 700, W // 2 + 900, 2300], fill=(255, 255, 255, 90 if light else 40))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(220)))
    return img


def make(kit, brand, site, mail):
    light, dark, acc = theme(brand)
    ink = clamp(tuple(v * 0.35 for v in dark)) if light else (255, 255, 255)
    line = clamp(tuple(v * 0.7 for v in acc)) if light else clamp(tuple(v + (255 - v) * 0.5 for v in acc)) if e.lum(acc) < 150 else acc
    logo = e.Image.open(e.pick(brand, "logo_black", "logo") if light else e.pick(brand, "logo_white", "logo")).convert("RGBA")
    for title, sub, extra, name in [("Big Event", "Join us", "00 / 00 / 0000  -  YOUR VENUE, YOUR CITY", "event_poster_A3.png"),
                                    ("Winter Sale", "Up to 00% off", "THIS WEEK ONLY  -  IN STORE AND ONLINE", "sale_poster_A3.png"),
                                    ("New Arrival", "Now available", "DISCOVER THE NEW COLLECTION", "product_poster_A3.png")]:
        img = background(light, dark, acc)
        d = ImageDraw.Draw(img)
        m, L = 150, 260
        for sx in (m, W - m):
            for sy in (m, H - m):
                dx, dy = (L if sx < W / 2 else -L), (L if sy < H / 2 else -L)
                d.line([(sx, sy), (sx + dx, sy)], fill=line, width=10)
                d.line([(sx, sy), (sx, sy + dy)], fill=line, width=10)
        e.paste_fit(img, logo, (W // 2 - 750, 330, 1500, 1500), "ct")
        d = ImageDraw.Draw(img)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((W // 2 + 6, 2090), title, font=e.font(e.SERIF, 330 if len(title) < 11 else 270), fill=(0, 0, 0, 110), anchor="mm")
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(img)
        d.text((W // 2, 2080), title, font=e.font(e.SERIF, 330 if len(title) < 11 else 270), fill=ink, anchor="mm")
        d.line([(520, 2330), (W // 2 - 60, 2330)], fill=line, width=6)
        d.line([(W // 2 + 60, 2330), (W - 520, 2330)], fill=line, width=6)
        d.polygon([(W // 2, 2306), (W // 2 + 24, 2330), (W // 2, 2354), (W // 2 - 24, 2330)], fill=line)
        d.text((W // 2, 2490), " ".join(sub.upper()), font=e.font(e.SERIF, 84), fill=ink, anchor="mm")
        d.text((W // 2, 2700), extra, font=e.font(e.SANS, 74), fill=line, anchor="mm")
        d.line([(300, 3190), (W - 300, 3190)], fill=line, width=3)
        d.text((300, 3290), site, font=e.font(e.SANS, 56), fill=ink, anchor="lm")
        d.text((W - 300, 3290), mail, font=e.font(e.SANS, 56), fill=ink, anchor="rm")
        img.convert("RGB").save(OUT / kit / name, optimize=True)


for k, (b, s, m) in KITS.items():
    make(k, b, s, m)
    print(k)

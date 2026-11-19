#!/usr/bin/env python3
"""Everything the four company kits were missing, made in Documents/twitch/Missing/<Kit>/ : the kit-specific gaps (posters,
event poster, product tag, ticket) plus the extra company pieces (invoice, envelope, thank-you card, name badge, gift voucher,
sticker, app icon). Placeholders only.    python tools/make_company_missing.py"""
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

import make_company_extras as e

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Missing")


def poster(brand, out, title, sub, name, size=(2480, 3508)):
    dark, acc = e.palette(e.pick(brand, "banner_twitter", "banner_youtube"))
    bg = dark if e.lum(dark) < 110 else tuple(int(v * 0.35) for v in dark)
    acc2 = tuple(int(v + (255 - v) * 0.5) for v in acc) if e.lum(acc) < 140 else acc
    W, H = size
    im = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(im)
    for i in range(0, W + H, 140):
        d.line([(i, 0), (i - H, H)], fill=(255, 255, 255, 10), width=4)
    d.rectangle([90, 90, W - 90, H - 90], outline=acc2, width=10)
    e.paste_fit(im, e.logo(brand, False), (W // 2 - 600, 260, 1200, 700), "ct")
    d = ImageDraw.Draw(im)
    d.text((W // 2, H // 2 - 150), title, font=e.font(e.SERIF, 300), fill=(255, 255, 255), anchor="mm")
    d.line([(W // 2 - 500, H // 2 + 50), (W // 2 + 500, H // 2 + 50)], fill=acc2, width=10)
    d.text((W // 2, H // 2 + 200), sub, font=e.font(e.SANS, 100), fill=acc2, anchor="mm")
    d.text((W // 2, H - 520), "00 / 00 / 0000  -  Your venue, Your city", font=e.font(e.SERIF, 90), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, H - 360), "www.yourcompany.com", font=e.font(e.SANS, 80), fill=acc2, anchor="mm")
    im.convert("RGB").save(out / name, optimize=True)


def ticket(brand, out):
    dark, acc = e.palette(e.pick(brand, "banner_twitter", "banner_youtube"))
    bg = dark if e.lum(dark) < 110 else tuple(int(v * 0.35) for v in dark)
    acc2 = tuple(int(v + (255 - v) * 0.5) for v in acc) if e.lum(acc) < 140 else acc
    W, H = 2400, 900
    im = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([30, 30, W - 30, H - 30], outline=acc2, width=6)
    d.line([(1700, 60), (1700, H - 60)], fill=acc2, width=4)
    e.paste_fit(im, e.logo(brand, False), (120, 100, 560, 200))
    d = ImageDraw.Draw(im)
    d.text((120, 480), "ADMIT ONE", font=e.font(e.SERIF, 170), fill=(255, 255, 255), anchor="lm")
    d.text((120, 680), "00 / 00 / 0000   00:00   Your venue", font=e.font(e.SANS, 60), fill=acc2, anchor="lm")
    d.text((2050, 400), "No.", font=e.font(e.SANS, 60), fill=acc2, anchor="mm")
    d.text((2050, 520), "0000", font=e.font(e.SERIF, 150), fill=(255, 255, 255), anchor="mm")
    im.convert("RGB").save(out / "ticket.png", optimize=True)


def tag(brand, out):
    dark, acc = e.palette(e.pick(brand, "banner_twitter", "banner_youtube"))
    bg = dark if e.lum(dark) < 110 else tuple(int(v * 0.35) for v in dark)
    acc2 = tuple(int(v + (255 - v) * 0.5) for v in acc) if e.lum(acc) < 140 else acc
    W, H = 900, 1500
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=80, fill=bg + (255,))
    d.ellipse([W // 2 - 60, 90, W // 2 + 60, 210], fill=(0, 0, 0, 0), outline=acc2, width=8)
    e.paste_fit(im, e.logo(brand, False), (150, 320, 600, 400), "ct")
    d = ImageDraw.Draw(im)
    d.text((W // 2, 860), "Product name", font=e.font(e.SERIF, 80), fill=(255, 255, 255), anchor="mm")
    d.line([(200, 960), (W - 200, 960)], fill=acc2, width=5)
    d.text((W // 2, 1100), "0.00", font=e.font(e.SERIF, 170), fill=acc2, anchor="mm")
    d.text((W // 2, 1340), "www.yourcompany.com", font=e.font(e.SANS, 46), fill=(255, 255, 255), anchor="mm")
    im.save(out / "product_tag.png", optimize=True)


for kit, brand in e.MAP.items():
    out = OUT / kit
    out.mkdir(parents=True, exist_ok=True)
    e.make(brand, out)
    poster(brand, out, "Big Event", "A SHORT LINE ABOUT THE EVENT", "event_poster_A3.png")
    poster(brand, out, "Sale", "UP TO 00% OFF  -  THIS WEEK ONLY", "sale_poster_A3.png")
    poster(brand, out, "New Arrival", "AVAILABLE NOW IN STORE AND ONLINE", "product_poster_A3.png")
    ticket(brand, out)
    tag(brand, out)
    old = e.KITS / kit / "Extra company pieces"
    if old.exists():
        shutil.rmtree(old)
    print(kit, len(list(out.iterdir())), "pieces")

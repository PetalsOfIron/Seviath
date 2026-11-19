#!/usr/bin/env python3
"""Preview cards (1280x720) for Ko-fi commission listings, in the shop look (cream, burgundy, rowan leaves). No names, no links.
    python tools/make_commission_cards.py"""
from pathlib import Path
from PIL import Image, ImageDraw
import make_shop_designs as m

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Shops/commissions")
CARDS = {
    "poster": ("Custom Poster", ["Print-ready PNG + PDF", "A3, A4 or social sizes", "2 rounds of revisions"], "POSTER DESIGN"),
    "brochure": ("Brochure & Flyer", ["Front and back layouts", "Print-ready PDF + PNG", "2 rounds of revisions"], "PRINT DESIGN"),
    "event": ("Event Design Set", ["Poster, invitation, social posts", "Signage and tickets", "One consistent look"], "EVENT IDENTITY"),
    "stationery": ("Business Cards & Stationery", ["Card front and back", "Letterhead and signature", "Print-ready files"], "STATIONERY"),
}


def card(title, bullets, tag):
    w, h = 1280, 720
    img = m.cover_crop(m.LEAVES, w, h)
    img.alpha_composite(Image.new("RGBA", (w, h), m.CREAM + (222,)))
    d = ImageDraw.Draw(img)
    d.text((80, 110), tag, font=m.sans(34), fill=m.WINE, anchor="lm")
    m.headline(img, 80, 160, 88 if len(title) < 20 else 70, (title,))
    d = ImageDraw.Draw(img)
    for i, b in enumerate(bullets):
        y = 380 + i * 76
        d.ellipse([84, y - 12, 108, y + 12], fill=m.WINE)
        d.text((130, y), b, font=m.sans(40), fill=m.INK, anchor="lm")
    m.chips(img, ["CUSTOM", "FAST DELIVERY", "REVISIONS"], 80, 620, 22)
    return img.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for k, (t, b, tag) in CARDS.items():
        card(t, b, tag).save(OUT / f"{k}.png", optimize=True)
        print(k)

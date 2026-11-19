#!/usr/bin/env python3
"""Fill the company kits in Documents/twitch/CompanyKits/<Kit>/ : copies every existing kit file into Assets/, then makes the
company pieces the kits did not have (invoice, envelope, thank-you card, name badge, gift voucher, round label, app icon).
Colours come from each kit's own banner and logo, placeholders only (Company Name, 000 ...).    python tools/make_company_extras.py"""
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DES = ROOT / "images" / "design"
KITS = Path("C:/Users/SaphiresSilver/Documents/twitch/CompanyKits")
MAP = {"Tessel": "Tessel", "Perfum": "Perfum", "Northbeam": "Northbeam", "Strikeline": "Football"}
F = "C:/Windows/Fonts/"
SANS = F + "bahnschrift.ttf"
SERIF = F + "georgiab.ttf"


def font(path, size):
    f = ImageFont.truetype(path, size)
    if path == SANS:
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f


def palette(src):
    """Two brand colours from the kit banner: a dark one and the most saturated one."""
    im = Image.open(src).convert("RGB").resize((200, 80))
    cols = im.quantize(8).convert("RGB").getcolors(16000)
    cols.sort(reverse=True)
    dark = min(cols[:4], key=lambda c: sum(c[1]))[1]

    def sat(c):
        r, g, b = c[1]
        return (max(r, g, b) - min(r, g, b)) * 2 + max(r, g, b) * 0.2
    acc = max(cols, key=sat)[1]
    return dark, acc


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def pick(brand, *names):
    for n in names:
        p = DES / brand / f"{brand.lower()}_{n}.png"
        if p.exists():
            return p
    raise FileNotFoundError(names)


def logo(brand, light_bg):
    p = pick(brand, "logo_black", "logo") if light_bg else pick(brand, "logo_white", "logo")
    return Image.open(p).convert("RGBA")


def paste_fit(img, lg, box, anchor="lt"):
    x, y, w, h = box
    k = min(w / lg.width, h / lg.height)
    t = lg.resize((int(lg.width * k), int(lg.height * k)), Image.LANCZOS)
    px = x if "l" in anchor else x + (w - t.width) // 2
    py = y if "t" in anchor else y + (h - t.height) // 2
    img.alpha_composite(t, (px, py))


def make(brand, out):
    dark, acc = palette(pick(brand, "banner_twitter", "banner_youtube"))
    ink = (30, 32, 40)
    bg_dark = dark if lum(dark) < 110 else tuple(int(v * 0.35) for v in dark)
    name = "Company Name"
    if lum(acc) < 140:      # accent colour used on dark pieces must stay readable
        acc_dark = tuple(int(v + (255 - v) * 0.55) for v in acc)
    else:
        acc_dark = acc
    acc_light = acc if lum(acc) < 170 else tuple(int(v * 0.6) for v in acc)

    # invoice A4
    W, H = 2480, 3508
    im = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 90], fill=bg_dark)
    paste_fit(im, logo(brand, True), (180, 220, 760, 300))
    d.text((W - 180, 300), "INVOICE", font=font(SERIF, 150), fill=bg_dark, anchor="rm")
    d.text((W - 180, 420), "No. 0000", font=font(SANS, 56), fill=acc_light, anchor="rm")
    for i, t in enumerate(["Billed to", "Client Name", "Street 1, City", "client@email.com"]):
        d.text((180, 680 + i * 80), t, font=font(SANS, 52) if i == 0 else font(SERIF, 56), fill=acc_light if i == 0 else ink)
    for i, t in enumerate(["Date: 00 / 00 / 0000", "Due: 00 / 00 / 0000"]):
        d.text((W - 180, 700 + i * 90), t, font=font(SERIF, 56), fill=ink, anchor="rm")
    d.rectangle([180, 1050, W - 180, 1170], fill=bg_dark)
    for x, t, a in [(220, "DESCRIPTION", "lm"), (1650, "QTY", "mm"), (1950, "PRICE", "mm"), (W - 220, "TOTAL", "rm")]:
        d.text((x, 1110), t, font=font(SANS, 50), fill=(255, 255, 255), anchor=a)
    for r in range(6):
        y = 1170 + r * 150
        d.line([(180, y + 150), (W - 180, y + 150)], fill=(220, 222, 228), width=3)
        d.text((220, y + 75), "Item or service %d" % (r + 1), font=font(SERIF, 52), fill=ink, anchor="lm")
        for x, t, a in [(1650, "0", "mm"), (1950, "0.00", "mm"), (W - 220, "0.00", "rm")]:
            d.text((x, y + 75), t, font=font(SERIF, 52), fill=ink, anchor=a)
    d.text((W - 640, 2300), "Total", font=font(SANS, 62), fill=acc_light, anchor="lm")
    d.text((W - 220, 2300), "0.00", font=font(SERIF, 90), fill=bg_dark, anchor="rm")
    d.text((180, 3250), name + " - Street 1, Your City - hello@yourcompany.com", font=font(SANS, 46), fill=acc_light)
    im.convert("RGB").save(out / "invoice_template.png", optimize=True)

    # DL envelope
    W, H = 2598, 1299
    im = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    paste_fit(im, logo(brand, True), (140, 120, 620, 220))
    d = ImageDraw.Draw(im)
    d.line([(140, 380), (W - 140, 380)], fill=acc, width=6)
    for i, t in enumerate([name, "Street 1", "Your City, 00000"]):
        d.text((140, 440 + i * 70), t, font=font(SERIF, 46), fill=ink)
    for i, t in enumerate(["Recipient Name", "Street 1", "City, 00000"]):
        d.text((W // 2 + 100, 700 + i * 90), t, font=font(SERIF, 62), fill=ink)
    d.rectangle([W - 380, 90, W - 140, 330], outline=(190, 192, 200), width=5)
    im.convert("RGB").save(out / "envelope_DL.png", optimize=True)

    # thank-you card A6 landscape
    W, H = 1748, 1240
    im = Image.new("RGBA", (W, H), bg_dark + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([40, 40, W - 40, H - 40], outline=acc_dark, width=6)
    paste_fit(im, logo(brand, False), (W // 2 - 280, 120, 560, 300), "ct")
    d = ImageDraw.Draw(im)
    d.text((W // 2, 640), "Thank you", font=font(SERIF, 170), fill=(255, 255, 255), anchor="mm")
    d.line([(W // 2 - 260, 780), (W // 2 + 260, 780)], fill=acc_dark, width=6)
    d.text((W // 2, 880), "We appreciate your order.", font=font(SANS, 56), fill=acc_dark, anchor="mm")
    d.text((W // 2, 1060), "www.yourcompany.com", font=font(SANS, 46), fill=(255, 255, 255), anchor="mm")
    im.convert("RGB").save(out / "thank_you_card_A6.png", optimize=True)

    # name badge
    W, H = 1200, 800
    im = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 190], fill=bg_dark)
    paste_fit(im, logo(brand, False), (60, 30, 360, 130), "lt")
    d = ImageDraw.Draw(im)
    d.text((W // 2, 430), "Full Name", font=font(SERIF, 130), fill=bg_dark, anchor="mm")
    d.text((W // 2, 570), "JOB TITLE", font=font(SANS, 54), fill=acc_light, anchor="mm")
    d.rectangle([0, H - 40, W, H], fill=acc)
    im.convert("RGB").save(out / "name_badge.png", optimize=True)

    # gift voucher
    W, H = 2100, 900
    im = Image.new("RGBA", (W, H), bg_dark + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([40, 40, W - 40, H - 40], outline=acc, width=6)
    d.line([(1400, 80), (1400, H - 80)], fill=acc_dark, width=4)
    paste_fit(im, logo(brand, False), (140, 110, 600, 200))
    d = ImageDraw.Draw(im)
    d.text((140, 520), "GIFT VOUCHER", font=font(SERIF, 130), fill=(255, 255, 255), anchor="lm")
    d.text((140, 680), "For: ____________    From: ____________", font=font(SANS, 52), fill=acc_dark, anchor="lm")
    d.text((1750, 380), "0", font=font(SERIF, 280), fill=(255, 255, 255), anchor="mm")
    d.text((1750, 600), "VALUE", font=font(SANS, 56), fill=acc_dark, anchor="mm")
    im.convert("RGB").save(out / "gift_voucher.png", optimize=True)

    # round label / sticker
    S = 1500
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([20, 20, S - 20, S - 20], fill=bg_dark + (255,))
    d.ellipse([90, 90, S - 90, S - 90], outline=acc_dark, width=8)
    paste_fit(im, logo(brand, False), (330, 330, 840, 840), "cc")
    im.save(out / "label_round_sticker.png", optimize=True)

    # app icon when the kit has none
    if not (DES / brand / (brand.lower() + "_icon.png")).exists():
        S = 1024
        im = Image.new("RGBA", (S, S), bg_dark + (255,))
        fav = Image.open(DES / brand / (brand.lower() + "_favicon_512.png")).convert("RGBA")
        paste_fit(im, fav, (200, 200, 624, 624), "cc")
        m = Image.new("L", (S, S), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], radius=230, fill=255)
        im.putalpha(m)
        im.save(out / "app_icon_1024.png", optimize=True)


def run():
    for kit, brand in MAP.items():
        assets, extras = KITS / kit / "Assets", KITS / kit / "Extra company pieces"
        assets.mkdir(parents=True, exist_ok=True)
        extras.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in sorted((DES / brand).iterdir()):
            shutil.copy2(f, assets / f.name)
            n += 1
        make(brand, extras)
        print(kit, n, "assets copied;", len(list(extras.iterdir())), "extra pieces")


if __name__ == "__main__":
    run()

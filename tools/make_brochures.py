#!/usr/bin/env python3
"""Bi-fold brochure designs (A4 landscape, 3508x2480), one distinct layout and typeface pair per Twitch style, in that style's
palette and with its own logo. Placeholder text only (no names, no links).
Writes Documents/twitch/Brochures/<Style>/outside.png + inside.png    python tools/make_brochures.py [Style ...]"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NEUTRAL = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral")
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Brochures")
FT = "C:/Windows/Fonts/"
W, H = 3508, 2480
HW = W // 2
SANS = FT + "bahnschrift.ttf"
LOREM = ("Write a short introduction about your business, event or project here. Tell visitors who you are, what you do and "
         "why they should choose you. Keep it clear, friendly and easy to read.")
ITEMS = [("Service One", "A short line about this service."), ("Service Two", "A short line about this service."), ("Service Three", "A short line about this service.")]
CONTACT = ["www.yourwebsite.com", "hello@yourbrand.com", "+00 000 000 0000", "Street 1, Your City"]


def font(path, size):
    f = ImageFont.truetype(FT + path if not path.startswith("C:") else path, size)
    if path.endswith("bahnschrift.ttf"):
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f


def grad(top, bot, vertical=True):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))
    return img.convert("RGBA")


def scale(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def logo(set_, file, size):
    im = Image.open(NEUTRAL / set_ / "Logo" / file).convert("RGBA")
    k = size / max(im.size)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    if im.getchannel("A").getextrema()[0] > 250:
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
        im.putalpha(m)
    return im


def put(img, im, cx, cy):
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def txt(d, s, xy, f, fill, anchor="mm", maxw=None):
    if maxw and d.textlength(s, font=f) > maxw:
        f = ImageFont.truetype(f.path, int(f.size * maxw / d.textlength(s, font=f)))
        if f.path.endswith("bahnschrift.ttf"):
            f.set_variation_by_name("Bold")
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def wrap(d, text, f, width):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            out.append(cur)
            cur = w
    return out + [cur]


def para(d, text, x, y, f, fill, width, lead):
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill)
        y += lead
    return y


def diamond(d, cx, cy, r, **kw):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], **kw)


def layer(draw_fn):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    return lay


# ------------------------------------------------------------------ 1. Vampire Elf: arched windows, blackletter
def vampire_out(c):
    img = grad((74, 12, 28), (22, 4, 10))
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for _ in range(26):                                  # bats
        x, y, s = rnd.randrange(W), rnd.randrange(H), rnd.randrange(24, 60)
        d.polygon([(x - s * 2, y), (x - s, y - s), (x, y - s // 3), (x + s, y - s), (x + s * 2, y), (x + s, y + s // 2), (x, y + s // 4), (x - s, y + s // 2)], fill=(10, 0, 4, 255))
    cx = HW + HW // 2
    d.rounded_rectangle([cx - 640, 180, cx + 640, 1760], radius=640, outline=c["gold"], width=10)      # arch window
    d.rounded_rectangle([cx - 600, 220, cx + 600, 1720], radius=600, outline=scale(c["gold"], 0.6), width=4)
    put(img, logo(c["set"], c["logo"], 1000), cx, 900)
    d = ImageDraw.Draw(img)
    txt(d, "Your Brand Name", (cx, 2000), font("OLDENGL.TTF", 230), (250, 236, 232), maxw=1500)
    txt(d, "~ A SHORT TAGLINE GOES HERE ~", (cx, 2160), font("times.ttf", 70), c["gold"])
    bx = HW // 2
    txt(d, "Come and visit", (bx, 700), font("OLDENGL.TTF", 190), c["gold"], maxw=1300)
    for i, t in enumerate(CONTACT):
        txt(d, t, (bx, 1000 + i * 150), font("times.ttf", 84), (250, 236, 232))
    return img


def vampire_in(c):
    img = grad((60, 10, 24), (18, 3, 8))
    d = ImageDraw.Draw(img)
    d.rectangle([140, 140, W - 140, H - 140], outline=c["gold"], width=8)
    d.line([(HW, 220), (HW, H - 220)], fill=scale(c["gold"], 0.5), width=4)
    d.text((330, 300), "A", font=font("OLDENGL.TTF", 720), fill=c["gold"])
    d.text((880, 470), "bout us", font=font("OLDENGL.TTF", 250), fill=(250, 236, 232))
    para(d, LOREM, 330, 1230, font("times.ttf", 84), (250, 236, 232), HW - 560, 130)
    x = HW + 260
    for i, (t, s) in enumerate(ITEMS):
        y = 300 + i * 640
        d.polygon([(x, y), (x + 1300, y), (x + 1400, y + 250), (x + 1300, y + 500), (x, y + 500), (x + 100, y + 250)], fill=scale(c["base"], 0.55), outline=c["gold"])
        d.text((x + 210, y + 150), t, font=font("OLDENGL.TTF", 130), fill=c["gold"])
        d.text((x + 210, y + 330), s, font=font("times.ttf", 62), fill=(250, 236, 232))
    return img


# ------------------------------------------------------------------ 2. Purple Gothic: diamonds, diagonal bands
def purple_out(c):
    img = grad((48, 18, 92), (16, 6, 36))
    img.alpha_composite(layer(lambda d: [d.polygon([(W * 0.52, 0), (W * 0.78, 0), (W * 0.46, H), (W * 0.2, H)], fill=(255, 255, 255, 14)), d.polygon([(W * 0.8, 0), (W, 0), (W, H), (W * 0.54, H)], fill=(0, 0, 0, 40))]))
    cx, cy = W * 3 // 4, 1000
    for k, r in enumerate([980, 800, 620]):
        img.alpha_composite(layer(lambda d, r=r, k=k: diamond(d, cx, cy, r, outline=c["accent"] + (200 - k * 40,), width=8)))
    put(img, logo(c["set"], c["logo"], 780), cx, cy)
    d = ImageDraw.Draw(img)
    txt(d, "Your Brand Name", (cx, 2160), font("GOUDOSB.TTF", 210), (248, 240, 255), maxw=1500)
    txt(d, "A SHORT TAGLINE GOES HERE", (cx, 2300), font(SANS, 56), c["accent"])
    bx = 330
    d.text((bx, 420), "Say hello", font=font("GOUDOSB.TTF", 230), fill=c["accent"])
    for i, t in enumerate(CONTACT):
        d.polygon([(bx, 900 + i * 190), (bx + 40, 920 + i * 190), (bx, 940 + i * 190), (bx - 40, 920 + i * 190)], fill=c["accent"])
        d.text((bx + 90, 920 + i * 190), t, font=font(SANS, 84), fill=(248, 240, 255), anchor="lm")
    return img


def purple_in(c):
    img = grad((42, 16, 84), (14, 5, 32))
    img.alpha_composite(layer(lambda d: [diamond(d, W * 0.12 + i * 740, H - 150, 330, outline=c["accent"] + (70,), width=5) for i in range(5)]))
    d = ImageDraw.Draw(img)
    d.text((330, 260), "About us", font=font("GOUDOSB.TTF", 250), fill=c["accent"])
    para(d, LOREM, 330, 640, font("GOUDOS.TTF", 88), (248, 240, 255), HW - 600, 140)
    for i, (t, s) in enumerate(ITEMS):
        cx, cy = HW + 330, 520 + i * 590
        img.alpha_composite(layer(lambda d, cx=cx, cy=cy: diamond(d, cx, cy, 230, fill=scale(c["base"], 0.7) + (255,), outline=c["accent"], width=8)))
        d = ImageDraw.Draw(img)
        d.text((cx, cy), str(i + 1), font=font("GOUDOSB.TTF", 190), fill=c["accent"], anchor="mm")
        d.text((cx + 340, cy - 70), t, font=font("GOUDOSB.TTF", 130), fill=(248, 240, 255), anchor="lm")
        d.text((cx + 340, cy + 80), s, font=font("GOUDOS.TTF", 66), fill=c["accent"], anchor="lm")
    return img


# ------------------------------------------------------------------ 3. Floral: soft circles, script, cream card
def floral_out(c):
    img = grad((86, 54, 118), (34, 22, 56))
    img.alpha_composite(layer(lambda d: [d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 214, 170, 26)) for x, y, r in [(W * 0.9, 300, 620), (W * 0.62, 2200, 520), (W * 0.1, 400, 480), (W * 0.35, 2300, 700)]]))
    cx = W * 3 // 4
    img.alpha_composite(layer(lambda d: d.rounded_rectangle([cx - 760, 230, cx + 760, 2250], radius=140, fill=(252, 244, 236, 238))))
    put(img, logo(c["set"], c["logo"], 900), cx, 880)
    d = ImageDraw.Draw(img)
    txt(d, "Your Brand Name", (cx, 1680), font("FREESCPT.TTF", 250), (82, 44, 98), maxw=1380)
    d.line([(cx - 300, 1830), (cx + 300, 1830)], fill=(190, 130, 150), width=6)
    txt(d, "a short tagline goes here", (cx, 1950), font("GOUDOS.TTF", 80), (120, 80, 130))
    bx = HW // 2
    txt(d, "Let's talk", (bx, 650), font("FREESCPT.TTF", 280), (255, 224, 190), maxw=1300)
    for i, t in enumerate(CONTACT):
        txt(d, t, (bx, 1000 + i * 150), font("GOUDOS.TTF", 90), (252, 244, 250))
    return img


def floral_in(c):
    img = grad((92, 58, 124), (36, 24, 60))
    img.alpha_composite(layer(lambda d: [d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 214, 170, 22)) for x, y, r in [(W * 0.78, 700, 900), (W * 0.1, 2300, 600)]]))
    cx, cy = HW // 2, 1000
    img.alpha_composite(layer(lambda d: [d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 224, 190, a), width=10) for r, a in [(720, 230), (800, 120)]]))
    put(img, logo(c["set"], c["logo"], 1100), cx, cy)
    d = ImageDraw.Draw(img)
    txt(d, "a little about us", (cx, 1980), font("FREESCPT.TTF", 170), (255, 224, 190))
    x = HW + 330
    d.text((x, 280), "Our story", font=font("FREESCPT.TTF", 300), fill=(255, 224, 190))
    para(d, LOREM, x, 740, font("GOUDOS.TTF", 80), (252, 244, 250), HW - 650, 125)
    for i, t in enumerate(["Friendly, reliable service", "Made with care and attention", "Fast delivery, fair prices"]):
        y = 1700 + i * 170
        d.ellipse([x, y - 30, x + 60, y + 30], outline=(255, 224, 190), width=8)
        d.ellipse([x + 18, y - 12, x + 42, y + 12], fill=(255, 224, 190))
        d.text((x + 120, y), t, font=font("GOUDOS.TTF", 80), fill=(252, 244, 250), anchor="lm")
    return img


# ------------------------------------------------------------------ 4. Gold Knight: heraldic shield, roman numerals
def knight_out(c):
    img = grad((64, 44, 10), (20, 14, 4))
    cx = W * 3 // 4
    sh = [(cx - 700, 220), (cx + 700, 220), (cx + 700, 1100), (cx, 1900), (cx - 700, 1100)]
    img.alpha_composite(layer(lambda d: [d.polygon(sh, fill=(0, 0, 0, 80), outline=c["gold"]), d.line(sh + [sh[0]], fill=c["gold"], width=12)]))
    put(img, logo(c["set"], c["logo"], 960), cx, 900)
    d = ImageDraw.Draw(img)
    txt(d, "YOUR BRAND NAME", (cx, 2110), font("CASTELAR.TTF", 190), (255, 246, 226), maxw=1600)
    txt(d, "A  SHORT  TAGLINE  GOES  HERE", (cx, 2280), font("timesbd.ttf", 66), c["gold"])
    bx = HW // 2
    img.alpha_composite(layer(lambda d: [d.polygon([(bx - 520 + i * 20, 330 + j * 0), (bx + 520 - i * 20, 330)], fill=None) for i in range(0)]))
    txt(d, "CONTACT", (bx, 520), font("CASTELAR.TTF", 170), c["gold"])
    d.line([(bx - 420, 640), (bx + 420, 640)], fill=c["gold"], width=8)
    for i, t in enumerate(CONTACT):
        txt(d, t, (bx, 860 + i * 170), font("timesbd.ttf", 86), (255, 246, 226))
    return img


def knight_in(c):
    img = grad((60, 42, 10), (18, 12, 4))
    d = ImageDraw.Draw(img)
    d.rectangle([140, 140, W - 140, H - 140], outline=c["gold"], width=10)
    d.rectangle([190, 190, W - 190, H - 190], outline=scale(c["gold"], 0.5), width=3)
    cols = [("I", "About Us", LOREM), ("II", "Services", "Service One, Service Two and Service Three. A short line about what you offer and how it helps."), ("III", "Why Us", "Friendly, reliable service. Made with care and attention. Fast delivery and fair prices.")]
    cw = (W - 500) // 3
    for i, (n, t, p) in enumerate(cols):
        x = 250 + i * cw + (cw - 800) // 2
        d.text((x + 400, 400), n, font=font("CASTELAR.TTF", 320), fill=c["gold"], anchor="mm")
        d.line([(x, 640), (x + 800, 640)], fill=c["gold"], width=6)
        d.text((x + 400, 780), t, font=font("CASTELAR.TTF", 130), fill=(255, 246, 226), anchor="mm")
        para(d, p, x, 960, font("timesbd.ttf", 70), (255, 246, 226), 800, 112)
        if i:
            d.line([(250 + i * cw, 330), (250 + i * cw, H - 330)], fill=scale(c["gold"], 0.5), width=3)
    return img


# ------------------------------------------------------------------ 5. Hooded Gamer: bold diagonals, impact, tilted blocks
def hood_out(c):
    img = Image.new("RGBA", (W, H), c["base"] + (255,))
    img.alpha_composite(layer(lambda d: [d.polygon([(HW + 500, 0), (W, 0), (W, H), (HW - 200, H)], fill=(20, 4, 8, 255)), d.polygon([(HW + 380, 0), (HW + 500, 0), (HW - 200, H), (HW - 320, H)], fill=(255, 255, 255, 255))]))
    d = ImageDraw.Draw(img)
    f = font("impact.ttf", 380)
    for i, t in enumerate(["YOUR", "BRAND", "NAME"]):
        d.text((HW + 640 + 8, 300 + i * 440 + 8), t, font=f, fill=(0, 0, 0, 255), anchor="la")
        d.text((HW + 640, 300 + i * 440), t, font=f, fill=(255, 255, 255, 255), anchor="la")
    d.text((HW + 640, 1760), "A SHORT TAGLINE", font=font(SANS, 70), fill=(255, 220, 220), anchor="la")
    d.text((HW + 640, 1860), "GOES HERE", font=font(SANS, 70), fill=(255, 220, 220), anchor="la")
    put(img, logo(c["set"], c["logo"], 760), HW // 2 + 60, 1900)
    d = ImageDraw.Draw(img)
    d.text((280, 360), "CONTACT", font=font("impact.ttf", 330), fill=(255, 255, 255, 255))
    for i, t in enumerate(CONTACT):
        d.text((290, 820 + i * 190), t, font=font(SANS, 96), fill=(255, 246, 244, 255))
    return img


def hood_in(c):
    img = Image.new("RGBA", (W, H), (26, 6, 10, 255))
    img.alpha_composite(layer(lambda d: [d.polygon([(x, 0), (x + 220, 0), (x - 480, H), (x - 700, H)], fill=(160, 40, 50, 60)) for x in range(900, W + 900, 900)]))
    d = ImageDraw.Draw(img)
    d.text((240, 200), "ABOUT US", font=font("impact.ttf", 420), fill=(255, 255, 255, 255))
    para(d, LOREM, 250, 760, font(SANS, 88), (255, 236, 234), HW - 520, 140)
    for i, (t, s) in enumerate(ITEMS):
        y = 330 + i * 640
        img.alpha_composite(layer(lambda d, y=y: d.polygon([(HW + 330, y + 40), (W - 240, y), (W - 240, y + 500), (HW + 330, y + 540)], fill=c["base"] + (255,), outline=(255, 255, 255, 255))))
        d = ImageDraw.Draw(img)
        d.text((HW + 400, y + 270), "0%d" % (i + 1), font=font("impact.ttf", 330), fill=(255, 255, 255, 255), anchor="lm")
        d.text((HW + 960, y + 190), t.upper(), font=font("impact.ttf", 105), fill=(255, 255, 255, 255), anchor="lm")
        d.text((HW + 960, y + 360), s, font=font(SANS, 44), fill=(255, 220, 220, 255), anchor="lm")
    return img


# ------------------------------------------------------------------ 6. Galaxy Elf: orbits and stars, Bodoni
def stars(img, seed):
    rnd = random.Random(seed)
    img.alpha_composite(layer(lambda d: [d.ellipse([x, y, x + s, y + s], fill=(255, 255, 255, rnd.choice([60, 120, 200]))) for x, y, s in [(rnd.randrange(W), rnd.randrange(H), rnd.choice([3, 4, 6, 9])) for _ in range(380)]]))


def galaxy_out(c):
    img = grad((18, 36, 96), (4, 8, 28))
    stars(img, 1)
    cx, cy = W * 3 // 4, 1000
    img.alpha_composite(layer(lambda d: [d.ellipse([cx - a, cy - b, cx + a, cy + b], outline=c["gold"] + (150 - k * 30,), width=5) for k, (a, b) in enumerate([(760, 760), (980, 620), (1180, 880)])]))
    put(img, logo(c["set"], c["logo"], 1000), cx, cy)
    d = ImageDraw.Draw(img)
    txt(d, "Y O U R   B R A N D   N A M E", (cx, 2100), font("BOD_B.TTF", 130), (240, 246, 255), maxw=1500)
    txt(d, "A short tagline goes here", (cx, 2250), font("timesi.ttf", 82), c["gold"])
    bx = HW // 2
    img.alpha_composite(layer(lambda d: d.ellipse([bx - 560, 560, bx + 560, 1680], outline=c["gold"] + (120,), width=5)))
    d = ImageDraw.Draw(img)
    txt(d, "Find us", (bx, 780), font("BOD_B.TTF", 200), c["gold"])
    for i, t in enumerate(CONTACT):
        txt(d, t, (bx, 1020 + i * 130), font("times.ttf", 76), (240, 246, 255))
    return img


def galaxy_in(c):
    img = grad((16, 32, 88), (4, 8, 26))
    stars(img, 2)
    cx, cy = HW // 2, 1240
    img.alpha_composite(layer(lambda d: [d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c["gold"] + (110,), width=4) for r in (420, 700, 980)]))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=c["gold"] + (255,))
    for i, (r, ang, t) in enumerate([(420, -40, "Service One"), (700, 200, "Service Two"), (980, 60, "Service Three")]):
        x, y = cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))
        d.ellipse([x - 70, y - 70, x + 70, y + 70], fill=(30, 60, 140), outline=c["gold"], width=6)
        d.text((x, y), str(i + 1), font=font("BOD_B.TTF", 80), fill=c["gold"], anchor="mm")
    d.text((cx, 330), "Our universe", font=font("BOD_B.TTF", 190), fill=c["gold"], anchor="mm")
    x = HW + 330
    d.text((x, 330), "About us", font=font("BOD_B.TTF", 220), fill=c["gold"])
    para(d, LOREM, x, 700, font("times.ttf", 82), (240, 246, 255), HW - 650, 128)
    for i, (t, s) in enumerate(ITEMS):
        y = 1760 + i * 230
        d.ellipse([x, y - 40, x + 80, y + 40], outline=c["gold"], width=6)
        d.text((x + 40, y), str(i + 1), font=font("BOD_B.TTF", 50), fill=c["gold"], anchor="mm")
        d.text((x + 140, y - 36), t, font=font("BOD_B.TTF", 72), fill=(240, 246, 255), anchor="lm")
        d.text((x + 140, y + 44), s, font=font("times.ttf", 54), fill=c["gold"], anchor="lm")
    return img


STYLES = {
    "Vampire_Elf": (dict(set="Crimson", logo="crimson_logo.png", base=(175, 30, 55), gold=(222, 186, 120)), vampire_out, vampire_in),
    "Purple_Gothic": (dict(set="Purple", logo="logo.png", base=(120, 60, 200), accent=(240, 190, 255)), purple_out, purple_in),
    "Floral": (dict(set="Floral", logo="logo.png", base=(140, 80, 180)), floral_out, floral_in),
    "Gold_Knight": (dict(set="Helmet", logo="logo.png", base=(170, 120, 40), gold=(255, 214, 120)), knight_out, knight_in),
    "Hooded_Gamer": (dict(set="Hood", logo="logo.png", base=(190, 36, 48)), hood_out, hood_in),
    "Galaxy_Elf": (dict(set="Starcaller", logo="starcaller_logo.png", base=(40, 95, 210), gold=(255, 224, 150)), galaxy_out, galaxy_in),
}


def main():
    names = [a for a in sys.argv[1:] if a in STYLES] or list(STYLES)
    for n in names:
        c, out_fn, in_fn = STYLES[n]
        (OUT / n).mkdir(parents=True, exist_ok=True)
        out_fn(c).convert("RGB").save(OUT / n / "outside.png", optimize=True)
        in_fn(c).convert("RGB").save(OUT / n / "inside.png", optimize=True)
        print(n)


if __name__ == "__main__":
    main()

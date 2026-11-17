#!/usr/bin/env python3
"""
Unique screens, logo and banner for two styles that were sharing the diamond-and-chain design:
  Slash  - crimson with white / black diagonal bars, big orange condensed lettering (like the "I AM OFFLINE" art)
  Helmet - deep purple with your gold helmet and crossed swords, gold frame, serif capitals

    python tools/make_unique.py
"""
import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
from make_starting_soon import helmet_emblem

TW = ROOT / "images" / "twitch"
ORANGE, ORANGE_D = (255, 150, 60), (240, 108, 24)
GOLD, GOLD_L, GOLD_D = (236, 190, 74), (255, 232, 150), (176, 122, 28)
CREAM = (250, 244, 232)


def save(img, path, rgba=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    (img if rgba else img.convert("RGB")).save(path, optimize=True)
    print("Saved", path.relative_to(ROOT))


def fit_size(text, fontname, target_w, start, track=0):
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    size = start
    while size > 16 and spaced_width(probe, text, font(fontname, size), track) / SS > target_w:
        size -= 2
    return size


# ============================================================================================ SLASH

def slash_bg(W, H, seed=2):
    t = np.linspace(0, 1, W)[None, :, None]
    stops = [(0.0, (40, 0, 8)), (0.3, (176, 8, 46)), (0.62, (246, 30, 84)), (1.0, (50, 0, 10))]
    arr = np.zeros((1, W, 3))
    xs = np.linspace(0, 1, W)
    for c in range(3):
        arr[0, :, c] = np.interp(xs, [s[0] for s in stops], [s[1][c] for s in stops])
    base = Image.fromarray(np.repeat(arr, H, axis=0).astype("uint8")).convert("RGBA")
    S = 2
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    slope = H * 1.05
    specs = []
    for _ in range(34):
        x = rnd.randint(-int(slope), W)
        wd = rnd.choice((7, 9, 12, 16, 22, 36, 60, 120))
        col = rnd.choice(((255, 255, 255, 245), (255, 255, 255, 245), (14, 0, 4, 245), (14, 0, 4, 245), (255, 255, 255, 130)))
        specs.append((x, wd, col))
    for x, wd, col in specs:
        d.polygon([(x * S, 0), ((x + wd) * S, 0), ((x + wd - slope) * S, H * S), ((x - slope) * S, H * S)], fill=col)
    base.alpha_composite(layer.resize((W, H), Image.LANCZOS))
    return base


def outlined(canvas, mask, fill, grad, outline=(14, 0, 4), width=9, shade=True):
    big = mask.filter(ImageFilter.MaxFilter(width * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    canvas = fill_mask(canvas, big, outline)
    return fill_mask(canvas, mask, fill, grad)


def slash_screen(title, sub):
    W, H = 1920, 1080
    img = slash_bg(W, H)
    size = fit_size(title, "impact.ttf", 1560, 400, track=10)
    img = outlined(img, text_mask((W, H), title, font("impact.ttf", size), (W / 2, H / 2 + size * 0.32), track=10), ORANGE, ORANGE_D, width=10)
    sz = fit_size(sub, "bahnschrift.ttf", 1300, 62, track=14)
    img = outlined(img, text_mask((W, H), sub.upper(), font("bahnschrift.ttf", sz), (W / 2, H / 2 + size * 0.32 + 120), track=14), (255, 255, 255), (230, 230, 230), width=6)
    return grain(img, 8)


def slash_banner():
    W, H = 3000, 1000
    img = slash_bg(W, H, seed=5)
    size = fit_size("PETALS OF IRON", "impact.ttf", 2500, 400, track=14)
    img = outlined(img, text_mask((W, H), "PETALS OF IRON", font("impact.ttf", size), (W / 2, H / 2 + size * 0.2), track=14), ORANGE, ORANGE_D, width=12)
    sz = 70
    img = outlined(img, text_mask((W, H), "GAMER  -  STREAMER  -  ARTIST", font("bahnschrift.ttf", sz), (W / 2, H / 2 + size * 0.2 + 130), track=18), (255, 255, 255), (230, 230, 230), width=7)
    return grain(img, 8)


def slash_logo():
    S = 2000
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = 1500
    cx = cy = S // 2
    disc = slash_bg(S, S, seed=9)
    m = Image.new("L", (S * 3, S * 3), 0)
    ImageDraw.Draw(m).ellipse(((cx - d / 2) * 3, (cy - d / 2) * 3, (cx + d / 2) * 3, (cy + d / 2) * 3), fill=255)
    m = m.resize((S, S), Image.LANCZOS)
    img = shadow(img, m, (0, 22), 30, (0, 0, 0), 0.55)
    img.paste(disc, (0, 0), m)
    for dia, wd, col in ((d + 40, 40, (14, 0, 4)), (d + 120, 22, (255, 255, 255)), (d + 190, 10, ORANGE)):
        r = dia / 2
        ring = Image.new("RGBA", (S * 3, S * 3), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse(((cx - r) * 3, (cy - r) * 3, (cx + r) * 3, (cy + r) * 3), outline=col + (255,), width=wd * 3)
        img = Image.alpha_composite(img, ring.resize((S, S), Image.LANCZOS))
    size = 1050
    mask = text_mask((S, S), "P", font("impact.ttf", size), (cx, cy + size * 0.36))
    img = outlined(img, mask, ORANGE, ORANGE_D, width=16)
    img = outlined(img, text_mask((S, S), "PETALS OF IRON", font("impact.ttf", 150), (cx, cy + 640), track=12), (255, 255, 255), (230, 230, 230), width=8)
    return img


# =========================================================================================== HELMET

def purple_bg(W, H):
    return radial((W, H), (46, 26, 78), (12, 6, 24), cx=0.5, cy=0.4, spread=0.75).convert("RGBA")


def gold_frame(img, inset=26):
    W, H = img.size
    d = ImageDraw.Draw(img)
    d.rectangle((inset, inset, W - inset - 1, H - inset - 1), outline=GOLD + (110,), width=2)
    corner_brackets(img, inset + 18, int(min(W, H) * 0.11), GOLD + (255,), width=4)
    return img


def helmet_img(height):
    em = helmet_emblem()
    s = height / em.height
    em = em.resize((round(em.width * s), height), Image.LANCZOS)
    fade = Image.new("L", em.size, 0)
    ImageDraw.Draw(fade).rectangle((60, 60, em.width - 60, em.height - 60), fill=255)
    out = Image.new("RGBA", em.size, (0, 0, 0, 0))
    out.paste(em.convert("RGBA"), (0, 0), fade.filter(ImageFilter.GaussianBlur(40)))
    return out


def helmet_screen(title, sub, bar=None):
    W, H = 1920, 1080
    img = purple_bg(W, H)
    he = helmet_img(640)
    img.alpha_composite(he, ((W - he.width) // 2, 14))
    img = glow(img, (560, 40, 1360, 620), (255, 190, 80), blur=120, alpha=60)
    img = sparkles(img, (120, 100, W - 120, 640), 50, GOLD_L, seed=21, max_r=3)
    f = font("georgiab.ttf", fit_size(title, "georgiab.ttf", 1500, 140, track=14))
    m = text_mask((W, H), title.upper(), f, (W / 2, 770), track=14)
    img = shadow(img, m, (0, 10), 14, (0, 0, 0), 0.7)
    img = fill_mask(img, m, GOLD_L, GOLD_D)
    d = ImageDraw.Draw(img)
    d.line([(560, 826), (900, 826)], fill=GOLD + (230,), width=3)
    d.line([(1020, 826), (1360, 826)], fill=GOLD + (230,), width=3)
    diamond(d, 960, 826, 14, GOLD + (255,))
    img = fill_mask(img, text_mask((W, H), sub, font("georgiai.ttf", 52), (W / 2, 912), track=2), CREAM)
    if bar is not None:
        bx0, bx1, by = 610, 1310, 984
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((bx0, by, bx1, by + 14), radius=7, fill=(255, 255, 255, 30), outline=GOLD + (140,), width=2)
        d.rounded_rectangle((bx0 + 3, by + 3, bx0 + 3 + bar * (bx1 - bx0), by + 11), radius=4, fill=GOLD + (255,))
    img = gold_frame(img)
    return grain(vignette(img, 0.5, (4, 2, 10)), 12)


def helmet_banner():
    W, H = 3000, 1000
    img = purple_bg(W, H)
    he = helmet_img(940)
    img.alpha_composite(he, ((W - he.width) // 2, 30))
    img = glow(img, (1000, 40, 2000, 900), (255, 190, 80), blur=160, alpha=50)
    for side, word in ((-1, "PETALS"), (1, "OF IRON")):
        x = W / 2 + side * 900
        sz = fit_size(word, "georgiab.ttf", 720, 200, track=10)
        m = text_mask((W, H), word, font("georgiab.ttf", sz), (x, 470), track=10)
        img = shadow(img, m, (0, 8), 10, (0, 0, 0), 0.7)
        img = fill_mask(img, m, GOLD_L, GOLD_D)
        d = ImageDraw.Draw(img)
        d.line([(x - 300, 380), (x + 300, 380)], fill=(140, 40, 70, 255), width=6)
    img = fill_mask(img, text_mask((W, H), "GAMER  -  STREAMER  -  ARTIST", font("georgiai.ttf", 64), (W / 2, 940), track=6), CREAM)
    img = gold_frame(img, 30)
    return grain(vignette(img, 0.45, (4, 2, 10)), 10)


def helmet_logo():
    S = 2000
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx = cy = S // 2
    d = 1520
    plate = purple_bg(S, S)
    he = helmet_img(1500)
    plate.alpha_composite(he, ((S - he.width) // 2, (S - he.height) // 2 - 20))
    plate = glow(plate, (260, 200, 1740, 1500), (255, 190, 80), blur=140, alpha=55)
    m = Image.new("L", (S * 3, S * 3), 0)
    ImageDraw.Draw(m).ellipse(((cx - d / 2) * 3, (cy - d / 2) * 3, (cx + d / 2) * 3, (cy + d / 2) * 3), fill=255)
    m = m.resize((S, S), Image.LANCZOS)
    img = shadow(img, m, (0, 22), 30, (0, 0, 0), 0.55)
    img.paste(plate, (0, 0), m)
    for dia, wd, col in ((d + 40, 36, GOLD), (d + 120, 8, GOLD_L)):
        r = dia / 2
        ring = Image.new("RGBA", (S * 3, S * 3), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse(((cx - r) * 3, (cy - r) * 3, (cx + r) * 3, (cy + r) * 3), outline=col + (255,), width=wd * 3)
        img = Image.alpha_composite(img, ring.resize((S, S), Image.LANCZOS))
    m2 = text_mask((S, S), "PETALS OF IRON", font("georgiab.ttf", 120), (cx, 1870), track=12)
    img = fill_mask(shadow(img, m2, (0, 6), 8, (0, 0, 0), 0.7), m2, GOLD_L, GOLD_D)
    return img


def main():
    sw = TW / "Slash"
    for n, t, s in (("starting_soon", "STARTING SOON", "The stream begins shortly"), ("be_right_back", "BE RIGHT BACK", "I will be back in a moment"),
                    ("offline", "I AM OFFLINE", "Thank you for watching")):
        save(slash_screen(t, s), sw / "Screens" / (n + ".png"))
    save(slash_banner(), sw / "Banner" / "banner.png")
    save(slash_logo(), sw / "Logo" / "logo.png", rgba=True)
    hw = TW / "Helmet"
    for n, t, s, b in (("starting_soon", "Starting soon", "The stream begins shortly", 0.4), ("be_right_back", "Be right back", "I will be back in a moment", None),
                       ("offline", "Offline", "Thank you for watching, see you next time", None)):
        save(helmet_screen(t, s, b), hw / "Screens" / (n + ".png"))
    save(helmet_banner(), hw / "Banner" / "banner.png")
    save(helmet_logo(), hw / "Logo" / "logo.png", rgba=True)
    print("done")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Starting soon / Be right back / Offline screens in the rose (berry) set style: cream and burgundy, slate leaf frame,
the red berry character from the set's emotes. Output goes to C:/Users/SaphiresSilver/Documents/twitch/Rose/Screens (not the site yet)."""
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_rose as mr

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Rose/Screens")
W, H = 1920, 1080
WINE = (92, 12, 30)
WINE_L = (150, 34, 54)
CREAM_A, CREAM_B = (246, 236, 228), (214, 186, 178)
INK = mr.INK
SSF = 2


def background(dim=0.0):
    img = radial((W, H), CREAM_A, CREAM_B, 0.5, 0.45, 1.0).convert("RGBA")
    # faint damask-like dots and petals
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    import random
    rnd = random.Random(7)
    for _ in range(60):
        x, y = rnd.randint(60, W - 60), rnd.randint(60, H - 60)
        r = rnd.randint(6, 14)
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(236, 140, 156, rnd.randint(30, 70)))
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(1)))
    img = vignette(img, 0.25, (92, 30, 40))
    if dim:
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (60, 20, 34, int(255 * dim))))
    return grain(img, 5)


def frame(img):
    S = 3
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((22 * S, 22 * S, (W - 22) * S, (H - 22) * S), radius=46 * S, outline=INK + (255,), width=9 * S)
    d.rounded_rectangle((44 * S, 44 * S, (W - 44) * S, (H - 44) * S), radius=34 * S, outline=mr.RED + (255,), width=4 * S)
    L, Wd = 78, 19
    for x in range(130, W - 100, 230):                      # top and bottom pairs
        for y, sgn in ((26, 1), (H - 26, -1)):
            mr.leaf(d, S, x, y, L, Wd, math.radians(8 * sgn), lw=7)
            mr.leaf(d, S, x, y, L, Wd, math.radians(180 - 8 * sgn), lw=7)
        for y in (30, H - 30):
            d.ellipse(((x + 115) * S - 9 * S, y * S - 9 * S, (x + 115) * S + 9 * S, y * S + 9 * S), fill=mr.RED + (255,), outline=INK + (255,), width=3 * S)
    for y in range(170, H - 120, 210):                      # sides
        for x, sgn in ((26, 1), (W - 26, -1)):
            mr.leaf(d, S, x, y, L, Wd, math.radians(90 - 8 * sgn * -1) if sgn == 1 else math.radians(90 + 8), lw=7)
            mr.leaf(d, S, x, y, L, Wd, math.radians(-90 + 8) if sgn == 1 else math.radians(-90 - 8), lw=7)
        for x in (30, W - 30):
            d.ellipse((x * S - 9 * S, (y + 105) * S - 9 * S, x * S + 9 * S, (y + 105) * S + 9 * S), fill=mr.RED + (255,), outline=INK + (255,), width=3 * S)
    lay = lay.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(img, lay)


def rose_img(height, angle=0, leaves=True):
    im = mr.user_rose(leaves)
    k = height / im.height
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    return im


def petals(img, box, n, seed):
    import random
    rnd = random.Random(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for _ in range(n):
        x, y = rnd.randint(box[0], box[2]), rnd.randint(box[1], box[3])
        w, h = rnd.randint(22, 38), rnd.randint(14, 24)
        p = Image.new("RGBA", (w * 4, h * 4), (0, 0, 0, 0))
        pd = ImageDraw.Draw(p)
        pd.ellipse((4, 4, w * 4 - 4, h * 4 - 4), fill=(186, 34, 56, 255), outline=INK + (255,), width=9)
        pd.arc((w * 0.6, h * 0.5, w * 3.2, h * 2.6), 200, 290, fill=(236, 120, 134, 255), width=7)
        p = p.resize((w, h), Image.LANCZOS).rotate(rnd.randint(0, 359), expand=True, resample=Image.BICUBIC)
        lay.alpha_composite(p, (x, y))
    return Image.alpha_composite(img, lay)


def corner_roses(img):
    small = rose_img(150, 0, False)
    for (x, y) in ((70, 70), (W - 70, 70), (70, H - 70), (W - 70, H - 70)):
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        lay.alpha_composite(small, (x - small.width // 2, y - small.height // 2))
        img = shadow(img, lay.split()[3], (0, 6), 8, (60, 10, 24), 0.4)
        img = Image.alpha_composite(img, lay)
    return img


def paste_shadow(img, im, xy):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(im, xy)
    img = shadow(img, lay.split()[3], (0, 26), 30, (60, 10, 24), 0.38)
    return Image.alpha_composite(img, lay)


def headline(img, text, xy, size, anchor="center"):
    m = text_mask(img.size, text, font("georgiab.ttf", size), xy, track=2, anchor=anchor)
    img = shadow(img, m, (0, 4), 6, (255, 255, 255), 0.5)
    return fill_mask(img, m, WINE_L, WINE)


def underline(img, cx, y, half):
    d = ImageDraw.Draw(img)
    d.line([(cx - half, y), (cx + half, y)], fill=mr.RED + (255,), width=5)
    for dx in (-half, half):
        d.ellipse((cx + dx - 8, y - 8, cx + dx + 8, y + 8), fill=mr.RED + (255,), outline=INK + (255,), width=3)
    return img


def sub(img, lines, cx, y, size, anchor="center"):
    for i, t in enumerate(lines):
        m = text_mask(img.size, t, font("georgiai.ttf", size), (cx, y + i * int(size * 1.35)), track=1, anchor=anchor)
        img = fill_mask(img, m, WINE)
    return img


def starting():
    img = frame(background())
    r = rose_img(700)
    img = petals(img, (560, 120, 1360, 760), 9, 3)
    img = paste_shadow(img, r, (960 - r.width // 2, 70))
    img = corner_roses(img)
    img = headline(img, "Starting soon", (960, 880), 150)
    img = underline(img, 960, 922, 300)
    img = sub(img, ["The stream begins shortly"], 960, 986, 46)
    return img


def brb():
    img = frame(background())
    r = rose_img(780, -14)
    img = paste_shadow(img, r, (500 - r.width // 2, 140))
    img = petals(img, (260, 760, 800, 960), 8, 5)
    img = corner_roses(img)
    img = headline(img, "Be right back", (1330, 520), 128)
    img = underline(img, 1330, 566, 330)
    img = sub(img, ["I will be back", "in a moment"], 1330, 648, 50)
    return img


def offline():
    img = frame(background(dim=0.1))
    r = rose_img(740, 14)
    img = paste_shadow(img, r, (1440 - r.width // 2, 120))
    img = petals(img, (1080, 780, 1760, 960), 12, 8)
    img = corner_roses(img)
    img = headline(img, "Offline", (590, 520), 150)
    img = underline(img, 590, 566, 250)
    img = sub(img, ["Thank you for watching,", "see you next time"], 590, 648, 50)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fn, f in (("starting_soon", starting), ("be_right_back", brb), ("offline", offline)):
        f().convert("RGB").save(OUT / (fn + ".png"), optimize=True)
        print("saved", fn)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Twitch "Starting soon" screen (1920x1080) built around the gold helmet from images/Gamerstreamer.png.
The helmet and swords are the original artwork; the script re-composes them with new typography,
light, frame and details.

    python tools/make_starting_soon.py
"""
from PIL import Image, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403

SRC = ROOT / "images" / "Gamerstreamer.png"
OUT = ROOT / "images" / "twitch" / "Starting" / "petals_starting_soon.png"
W, H = 1920, 1080
GOLD = (236, 190, 74)
GOLD_LIGHT = (255, 232, 150)
GOLD_DARK = (176, 122, 28)
CREAM = (250, 244, 232)
BG_CENTER, BG_EDGE = (37, 21, 63), (10, 6, 20)


def helmet_emblem():
    """Crop helmet + swords from the banner and remove the 'GAMER STREAMER' lettering around it."""
    src = Image.open(SRC).convert("RGB")
    row = src.crop((0, 960, src.width, 961))                    # plain background gradient (changes left to right only)
    plain = row.resize(src.size, Image.NEAREST)
    for box in ((740, 380, 1180, 660), (1830, 380, 2260, 660)):  # the two words and the red lines above them
        src.paste(plain.crop(box), box[:2])
    return src.crop((740, 20, 2260, 900))


def main():
    canvas = radial((W, H), BG_CENTER, BG_EDGE, cx=0.5, cy=0.42, spread=0.62).convert("RGBA")

    # helmet, feathered into the background so no edge shows
    em = helmet_emblem()
    scale = 0.6
    em = em.resize((round(em.width * scale), round(em.height * scale)), Image.LANCZOS)
    fade = Image.new("L", em.size, 0)
    ImageDraw.Draw(fade).rectangle((60, 60, em.width - 60, em.height - 60), fill=255)
    fade = fade.filter(ImageFilter.GaussianBlur(45))
    ex, ey = (W - em.width) // 2, 20
    canvas.paste(em, (ex, ey), fade)

    # warm light behind the helmet, sparkles
    canvas = glow(canvas, (560, 60, 1360, 640), (255, 190, 80), blur=120, alpha=60)
    canvas = sparkles(canvas, (120, 100, W - 120, 640), 55, GOLD_LIGHT, seed=11, max_r=3.2)

    # title
    f_title = font("georgiab.ttf", 138)
    m = text_mask((W, H), "STARTING SOON", f_title, (W / 2, 745), track=16)
    canvas = shadow(canvas, m, (0, 10), 14, (0, 0, 0), 0.7)
    canvas = fill_mask(canvas, m, GOLD_LIGHT, GOLD_DARK)
    # fine light edge on the letters
    rim = m.filter(ImageFilter.MaxFilter(3))
    edge = Image.new("L", (W, H), 0)
    edge.paste(rim, (0, 0))
    canvas = fill_mask(canvas, ImageChopsSubtract(rim, m), (255, 245, 205))

    # divider with diamonds
    d = ImageDraw.Draw(canvas)
    y = 800
    d.line([(560, y), (900, y)], fill=GOLD + (230,), width=3)
    d.line([(1020, y), (1360, y)], fill=GOLD + (230,), width=3)
    diamond(d, 960, y, 14, GOLD + (255,))
    diamond(d, 920, y, 6, GOLD + (255,))
    diamond(d, 1000, y, 6, GOLD + (255,))

    f_sub = font("georgiai.ttf", 50)
    canvas = fill_mask(canvas, text_mask((W, H), "The stream begins shortly", f_sub, (W / 2, 880), track=2), CREAM)

    # progress bar (decorative)
    bx0, bx1, by = 610, 1310, 960
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((bx0, by, bx1, by + 14), radius=7, fill=(255, 255, 255, 30), outline=GOLD + (140,), width=2)
    d.rounded_rectangle((bx0 + 3, by + 3, bx0 + 3 + 0.4 * (bx1 - bx0), by + 11), radius=4, fill=GOLD + (255,))
    f_small = font("segoeui.ttf", 26)
    canvas = fill_mask(canvas, text_mask((W, H), "PETALS OF IRON", f_small, (W / 2, 1022), track=12), (214, 196, 160))

    # frame
    d = ImageDraw.Draw(canvas)
    d.rectangle((22, 22, W - 23, H - 23), outline=GOLD + (95,), width=2)
    corner_brackets(canvas, 42, 110, GOLD + (255,), width=4)

    canvas = vignette(canvas, 0.5, (4, 2, 10))
    canvas = grain(canvas, 12)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, optimize=True)
    print("Saved", OUT, canvas.size)


def ImageChopsSubtract(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)


if __name__ == "__main__":
    main()

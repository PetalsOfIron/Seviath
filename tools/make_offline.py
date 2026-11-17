#!/usr/bin/env python3
"""
Builds the Twitch "offline screen" (1920x1080) from the snake artwork in images/Banner snake.png.

The snake is the original painting; this script only re-composes it: cinematic top / bottom bars,
a matching blue gradient, a clean blackletter title, gold details, soft light and fine grain.

    python tools/make_offline.py
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "Banner snake.png"
OUT = ROOT / "images" / "twitch" / "Offline" / "petals_offline_screen.png"
FONTS = Path("C:/Windows/Fonts")

W, H = 1920, 1080
BAR = 96                      # height of the top and bottom bars
NAVY = (9, 30, 64)
DEEP = (6, 18, 40)
GOLD = (244, 200, 74)
CREAM = (240, 250, 255)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def vertical_fade(w, h, top, bottom):
    """Mask that is 0 at the edges (top / bottom px) and 255 inside - used to blend the art into the bars."""
    m = Image.new("L", (w, h), 255)
    px = m.load()
    for y in range(h):
        a = min(1, y / top) if top else 1
        b = min(1, (h - 1 - y) / bottom) if bottom else 1
        v = int(255 * min(a, b))
        for x in range(w):
            px[x, y] = v
    return m


def text_layer(draw_fn, blur=0):
    layer = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    layer = layer.resize((W, H), Image.LANCZOS)
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return layer


def gradient_text(text, fnt, xy, c1, c2, anchor="ma"):
    """Text filled with a vertical gradient, drawn at 2x and returned as an RGBA layer."""
    mask = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(mask).text((xy[0] * 2, xy[1] * 2), text, font=fnt, fill=255, anchor=anchor)
    box = mask.getbbox()
    fill = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    fp = fill.load()
    top, bot = box[1], box[3]
    for y in range(top, bot):
        t = (y - top) / max(1, bot - top)
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)
        for x in range(box[0], box[2]):
            fp[x, y] = col
    fill.putalpha(mask)
    return fill.resize((W, H), Image.LANCZOS), mask.resize((W, H), Image.LANCZOS)


def clean_source(src):
    """The banner has text on its right side. Keep the snake (left part) and rebuild the plain gradient there."""
    cut, feather = 1880, 70
    row = src.crop((0, 985, src.width, 986))                  # a clean row: the gradient only changes left-to-right
    plain = row.resize((src.width, src.height), Image.NEAREST)
    mask = Image.new("L", src.size, 0)
    md = ImageDraw.Draw(mask)
    for x in range(feather):                                   # 255 left of the cut, fading to 0 across the feather
        md.line([(cut - feather + x, 0), (cut - feather + x, src.height)], fill=int(255 * (1 - x / feather)))
    md.rectangle((0, 0, cut - feather - 1, src.height), fill=255)
    out = Image.composite(src, plain, mask)

    # the grass tuft at the top is clipped by a straight edge in the original painting: remove it
    box = (1595, 0, 1775, 160)
    part = out.crop(box)
    pp = part.load()
    green = Image.new("L", part.size, 0)
    gp = green.load()
    for y in range(part.height):
        for x in range(part.width):
            r, g, b = pp[x, y]
            if g > b + 4 and g > r + 14:
                gp[x, y] = 255
    green = green.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(2.5))
    out.paste(plain.crop(box), box[:2], green)
    return out


def main():
    src = Image.open(SRC).convert("RGB")
    src = clean_source(src)

    # --- art window: the snake painting, scaled so it fills the space between the bars -----------------
    art_h = H - 2 * BAR + 40                      # a little taller than the window, bars overlap its edges
    scale = art_h / src.height
    art = src.resize((round(src.width * scale), art_h), Image.LANCZOS)
    ox = -300                                     # push the snake left to leave room for the title
    canvas = Image.new("RGB", (W, H), DEEP)
    canvas.paste(art, (ox, BAR - 20))

    # --- bars ------------------------------------------------------------------------------------------------------
    bars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bars)
    for y in range(BAR + 24):                     # top bar with a soft lower edge
        a = 255 if y < BAR - 8 else int(255 * (1 - (y - (BAR - 8)) / 32))
        bd.line([(0, y), (W, y)], fill=DEEP + (max(0, a),))
        yy = H - 1 - y
        bd.line([(0, yy), (W, yy)], fill=DEEP + (max(0, a),))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), bars)

    # --- soft light on the right and vignette ------------------------------------------------------------
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((1180, 200, 2000, 880), fill=(255, 255, 255, 70))
    canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(120)))
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-380, -300, W + 380, H + 300), fill=255)
    vig = ImageChops.invert(vig.filter(ImageFilter.GaussianBlur(220)))
    dark = Image.new("RGBA", (W, H), DEEP + (0,))
    dark.putalpha(vig.point(lambda v: int(v * 0.55)))
    canvas = Image.alpha_composite(canvas, dark)

    # --- gold frame lines on the bars --------------------------------------------------------------------------
    fr = ImageDraw.Draw(canvas)
    for y in (BAR - 2, H - BAR + 1):
        fr.line([(0, y), (W, y)], fill=GOLD + (230,), width=2)
    fr.rectangle((14, 14, W - 15, H - 15), outline=GOLD + (120,), width=2)

    # --- text ------------------------------------------------------------------------------------------------------
    cx = 1650                                     # centre of the text column
    title_font = ImageFont.truetype(str(FONTS / "OLDENGL.TTF"), 300)
    shadow_src = text_layer(lambda d: d.text((cx * 2 + 6, 480 * 2 + 10), "Offline", font=ImageFont.truetype(
        str(FONTS / "OLDENGL.TTF"), 300), fill=(0, 20, 50, 150), anchor="ms"), blur=7)
    canvas = Image.alpha_composite(canvas, shadow_src)
    title, tmask = gradient_text("Offline", title_font, (cx, 480), (6, 24, 58), (14, 70, 120), anchor="ms")
    # thin light rim so the letters stay readable on the light part of the gradient
    rim = tmask.filter(ImageFilter.MaxFilter(5)).point(lambda v: int(v * 0.85))
    rim_layer = Image.new("RGBA", (W, H), CREAM + (0,))
    rim_layer.putalpha(rim)
    canvas = Image.alpha_composite(canvas, rim_layer)
    canvas = Image.alpha_composite(canvas, title)

    # divider with a diamond
    d = ImageDraw.Draw(canvas)
    y = 530
    d.line([(cx - 230, y), (cx - 24, y)], fill=GOLD + (255,), width=3)
    d.line([(cx + 24, y), (cx + 230, y)], fill=GOLD + (255,), width=3)
    d.polygon([(cx, y - 13), (cx + 13, y), (cx, y + 13), (cx - 13, y)], fill=GOLD + (255,))

    def centered(text, fnt, y, fill, spacing=0):
        layer = text_layer(lambda dd: dd.text((cx * 2, y * 2), text, font=fnt, fill=fill, anchor="mm"))
        return layer

    sub = ImageFont.truetype(str(FONTS / "georgiab.ttf"), 80)
    canvas = Image.alpha_composite(canvas, centered("The stream has ended", sub, 600, NAVY + (255,)))
    small = ImageFont.truetype(str(FONTS / "georgia.ttf"), 68)
    canvas = Image.alpha_composite(canvas, centered("Thank you for stopping by", small, 660, (10, 50, 95, 255)))
    canvas = Image.alpha_composite(canvas, centered("See you next stream", small, 706, (10, 50, 95, 255)))

    # bar texts
    brand = ImageFont.truetype(str(FONTS / "OLDENGL.TTF"), 56)
    canvas = Image.alpha_composite(canvas, text_layer(
        lambda dd: dd.text((80 * 2, (BAR // 2) * 2), "Petals Of Iron", font=ImageFont.truetype(
            str(FONTS / "OLDENGL.TTF"), 112), fill=GOLD + (255,), anchor="lm")))
    tag = ImageFont.truetype(str(FONTS / "segoeui.ttf"), 44)

    def spaced(dd, x, y, text, fnt, fill, track, anchor_right=False):
        widths = [dd.textlength(c, font=fnt) for c in text]
        total = sum(widths) + track * (len(text) - 1)
        cx0 = x - total if anchor_right else x
        for c, wch in zip(text, widths):
            dd.text((cx0, y), c, font=fnt, fill=fill, anchor="lm")
            cx0 += wch + track

    canvas = Image.alpha_composite(canvas, text_layer(
        lambda dd: spaced(dd, (W - 80) * 2, (BAR // 2) * 2, "ART @SMADNA", ImageFont.truetype(
            str(FONTS / "segoeui.ttf"), 56), CREAM + (255,), 10, anchor_right=True)))
    canvas = Image.alpha_composite(canvas, text_layer(
        lambda dd: spaced(dd, 960 * 2 - 640, (H - BAR // 2) * 2, "FOLLOW FOR STREAM NOTIFICATIONS", ImageFont.truetype(
            str(FONTS / "segoeui.ttf"), 56), CREAM + (255,), 8)))

    # --- fine grain so gradients do not band ---------------------------------------------------------------
    rnd = random.Random(7)
    noise = Image.effect_noise((W, H), 12).convert("L")
    grain = Image.merge("RGBA", (noise, noise, noise, Image.new("L", (W, H), 14)))
    canvas = Image.alpha_composite(canvas, grain)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, optimize=True)
    print("Saved", OUT, canvas.size)


if __name__ == "__main__":
    main()

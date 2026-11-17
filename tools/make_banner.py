#!/usr/bin/env python3
"""
Twitch channel banner (2400x960, shown at 1200x480) for the red hooded gamer logo images/LogoGaming.png.
The logo is the original artwork; the script builds the banner around it.

    python tools/make_banner.py
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403

SRC = ROOT / "images" / "LogoGaming.png"
OUT = ROOT / "images" / "twitch" / "Banner" / "petals_gamer_banner.png"
W, H = 2400, 960
CREAM = (255, 232, 214)
SILVER_LIGHT, SILVER_DARK = (246, 248, 252), (150, 156, 172)
MAROON = (122, 6, 8)


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out, mask


def streaks(canvas):
    """A few soft diagonal light bands, like light falling across steel."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x0, wd, a in ((900, 120, 22), (1180, 40, 26), (1500, 220, 14), (2000, 70, 18)):
        d.polygon([(x0, 0), (x0 + wd, 0), (x0 + wd - 420, H), (x0 - 420, H)], fill=(255, 255, 255, a))
    return Image.alpha_composite(canvas, layer.filter(ImageFilter.GaussianBlur(14)))


def fit_font(name, text, target_w, track=0):
    size = 100
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    f = font(name, size)
    width = spaced_width(probe, text, f, track) / SS
    return font(name, max(10, int(size * target_w / width)))


def main():
    canvas = radial((W, H), (112, 9, 13), (22, 2, 4), cx=0.3, cy=0.5, spread=0.75).convert("RGBA")
    canvas = streaks(canvas)

    # logo tile with soft shadow and a silver edge
    size = 770
    logo = Image.open(SRC).convert("RGB").resize((size, size), Image.LANCZOS)
    tile, tmask = rounded(logo, 44)
    tx, ty = 250, (H - size) // 2
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    big = Image.new("L", canvas.size, 0)
    big.paste(tmask, (tx + 14, ty + 26))
    sh.putalpha(big.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.7)))
    canvas = Image.alpha_composite(canvas, sh)
    canvas.alpha_composite(tile, (tx, ty))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((tx - 2, ty - 2, tx + size + 1, ty + size + 1), radius=46, outline=SILVER_LIGHT + (235,), width=4)
    d.rounded_rectangle((tx - 16, ty - 16, tx + size + 15, ty + size + 15), radius=58, outline=SILVER_DARK + (130,), width=2)

    # title block
    cx = 1640
    f_title = fit_font("OLDENGL.TTF", "Petals Of Iron", 1180)
    m = text_mask((W, H), "Petals Of Iron", f_title, (cx, 470))
    canvas = shadow(canvas, m, (0, 12), 16, (0, 0, 0), 0.75)
    canvas = fill_mask(canvas, m, (255, 244, 232), (236, 190, 160))

    d = ImageDraw.Draw(canvas)
    y = 545
    d.line([(cx - 470, y), (cx - 40, y)], fill=SILVER_LIGHT + (220,), width=3)
    d.line([(cx + 40, y), (cx + 470, y)], fill=SILVER_LIGHT + (220,), width=3)
    diamond(d, cx, y, 15, SILVER_LIGHT + (255,))
    diamond(d, cx - 36, y, 6, SILVER_LIGHT + (255,))
    diamond(d, cx + 36, y, 6, SILVER_LIGHT + (255,))

    f_sub = fit_font("georgiab.ttf", "GAMER  ·  STREAMER", 1000, track=16)
    m2 = text_mask((W, H), "GAMER  ·  STREAMER", f_sub, (cx, 650), track=16)
    canvas = shadow(canvas, m2, (0, 6), 8, (0, 0, 0), 0.6)
    canvas = fill_mask(canvas, m2, SILVER_LIGHT, SILVER_DARK)

    # "live on twitch" pill
    f_pill = font("segoeui.ttf", 40)
    label = "LIVE ON TWITCH"
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    tw = spaced_width(probe, label, f_pill, 8) / SS
    px0, px1, py0, py1 = cx - tw / 2 - 52, cx + tw / 2 + 52, 722, 806
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((px0, py0, px1, py1), radius=42, fill=MAROON + (255,), outline=SILVER_LIGHT + (235,), width=3)
    canvas = fill_mask(canvas, text_mask((W, H), label, f_pill, (cx, 777), track=8), CREAM)

    # frame
    d = ImageDraw.Draw(canvas)
    d.rectangle((26, 26, W - 27, H - 27), outline=SILVER_LIGHT + (150,), width=3)
    d.rectangle((44, 44, W - 45, H - 45), outline=SILVER_DARK + (90,), width=1)

    canvas = vignette(canvas, 0.55, (8, 0, 0))
    canvas = grain(canvas, 12)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, optimize=True)
    print("Saved", OUT, canvas.size)


if __name__ == "__main__":
    main()

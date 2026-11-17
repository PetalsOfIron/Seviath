#!/usr/bin/env python3
"""Rose set: its own screens, overlay, alert and corner (cream paper, slate leaves, red berry) - not the purple look."""
import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_rose as mr

OUT = ROOT / "images" / "twitch" / "Rose"
W, H = 1920, 1080


def leafy_border(size, step=150, scale=1.0):
    w, h = size
    layer = mr.layer(size, lambda d, S: [
        (mr.leaf(d, S, x, y, 120 * scale, 30 * scale, math.radians(a), lw=8), mr.berry_dot(d, S, x + 6, y + 4, 12 * scale)) if k % 3 == 0 else mr.leaf(d, S, x, y, 120 * scale, 30 * scale, math.radians(a), lw=8)
        for k, (x, y, a) in enumerate(
            [(x, 40, 20 if (x // step) % 2 else 160) for x in range(90, w - 60, step)] +
            [(x, h - 40, -20 if (x // step) % 2 else -160) for x in range(90, w - 60, step)] +
            [(40, y, 70 if (y // step) % 2 else 110) for y in range(220, h - 150, step)] +
            [(w - 40, y, 110 if (y // step) % 2 else 70) for y in range(220, h - 150, step)])])
    return layer


def paper(size):
    img = radial(size, (246, 232, 224), (214, 190, 182), cx=0.5, cy=0.5, spread=1.0).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((22, 22, size[0] - 22, size[1] - 22), radius=60, outline=mr.INK + (255,), width=10)
    d.rounded_rectangle((40, 40, size[0] - 40, size[1] - 40), radius=48, outline=mr.RED + (255,), width=5)
    return Image.alpha_composite(img, leafy_border(size))


def screen(title, lines, mood, extra, side):
    img = paper((W, H))
    ur = mr.user_rose(True)
    hh = 500 if side == 'center' else 640
    k = hh / ur.height
    hero = ur.resize((round(ur.width * k), hh), Image.LANCZOS)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hx = 190 if side == "left" else W - 790 if side == "right" else (W - 600) // 2
    lay.alpha_composite(hero, (hx + (600 - hero.width) // 2, 130 if side == "center" else 220))
    img = shadow(img, lay.split()[3], (0, 14), 20, (60, 10, 20), 0.3)
    img = Image.alpha_composite(img, lay)
    cx = W - 520 if side == "left" else 520 if side == "right" else W / 2
    cy = 520 if side != "center" else 800
    sz = 150
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    while sz > 60 and probe.textlength(title, font=font("georgiab.ttf", sz)) / SS > 860:
        sz -= 6
    m = text_mask((W, H), title, font("georgiab.ttf", sz), (cx, cy))
    img = fill_mask(img, m, mr.INK, (110, 14, 30))
    d = ImageDraw.Draw(img)
    d.line([(cx - 300, cy + 40), (cx + 300, cy + 40)], fill=mr.RED + (255,), width=6)
    for k, ln in enumerate(lines):
        img = fill_mask(img, text_mask((W, H), ln, font("georgiai.ttf", 56), (cx, cy + 110 + k * 66)), (100, 20, 34))
    return grain(img, 6)


def overlay():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 10, W - 10, H - 10), radius=60, outline=mr.INK + (255,), width=14)
    d.rounded_rectangle((28, 28, W - 28, H - 28), radius=48, outline=(250, 236, 228, 255), width=18)
    d.rounded_rectangle((52, 52, W - 52, H - 52), radius=36, outline=mr.RED + (255,), width=6)
    img = Image.alpha_composite(img, leafy_border((W, H), 170, 1.1))
    for (x, y) in ((140, 130), (W - 140, 130), (W - 140, H - 130)):
        r = mr.user_rose(False)
        r = r.resize((250, round(250 * r.height / r.width)), Image.LANCZOS)
        img.alpha_composite(r, (x - 125, y - r.height // 2))
    cx0, cy0, cx1, cy1 = 90, H - 90 - 300, 90 + 533, H - 90
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rounded_rectangle((cx0, cy0, cx1, cy1), radius=30, fill=0)
    cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cam).rounded_rectangle((cx0 - 14, cy0 - 14, cx1 + 14, cy1 + 14), radius=40, outline=(250, 236, 228, 255), width=14)
    ImageDraw.Draw(cam).rounded_rectangle((cx0 - 2, cy0 - 2, cx1 + 2, cy1 + 2), radius=32, outline=mr.RED + (255,), width=6)
    img = Image.alpha_composite(img, cam)
    img.putalpha(ImageChops.multiply(img.split()[3], cut))
    return img


def shine(base, n=26):
    w, h = base.size
    frames = []
    for i in range(n):
        x = -80 + (w + 160) * i / (n - 1)
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).polygon([(x, 0), (x + 46, 0), (x - 28, h), (x - 74, h)], fill=(255, 255, 255, 130))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        wm = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        wm.putalpha(ImageChops.multiply(sh.split()[3], base.split()[3]))
        frames.append(Image.alpha_composite(base, wm))
    return frames


def gif(frames, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=50, disposal=2, loop=0, optimize=False)


def main():
    for fn, t, ls, mood, extra, side in (("starting_soon", "Starting soon", ["The stream begins shortly"], "party", "party", "center"),
                                        ("be_right_back", "Be right back", ["I will be back", "in a moment"], "hi", "wave", "left"),
                                        ("offline", "Offline", ["Thank you for watching,", "see you next time"], "sleepy", "zzz", "right")):
        p = OUT / "Screens" / (fn + ".png")
        p.parent.mkdir(parents=True, exist_ok=True)
        screen(t, ls, mood, extra, side).convert("RGB").save(p, optimize=True)
    (OUT / "Overlay").mkdir(parents=True, exist_ok=True)
    overlay().save(OUT / "Overlay" / "overlay_frame.png", optimize=True)
    a = mr.panel("Thanks for the follow!", "about").resize((800, 250), Image.LANCZOS).convert("RGBA")
    gif(shine(a), OUT / "Alert" / "alert.gif")
    c = mr.panel("Petals Of Iron", "links").resize((440, 138), Image.LANCZOS).convert("RGBA")
    gif(shine(c, 30), OUT / "Corner" / "corner.gif")
    print("done")


if __name__ == "__main__":
    main()

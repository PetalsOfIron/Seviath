#!/usr/bin/env python3
"""A different animation for every set's alert and corner (the card designs stay as they are).
Hood: paper sway - Helmet: gold glints - Slash: diagonal slash flash - Snake: travelling wave - Floral: falling petals -
Tessel: bouncing ball - Perfum: rising mist - Northbeam: sweeping light beam - Strikeline: sliding stripes -
Purple: glow breathing - Rose: slow zoom. The set supplied by the user (Petals alert / corner) is never touched."""
import math
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_sets as ms
import make_redo as rd

TW = ROOT / "images" / "twitch"
N = 28
KEEP_FRAME0 = ("Hood", "Purple", "Rose")     # their first frame has no effect on it yet


def base_alert(name):
    p = TW / name / "Alert" / "alert.gif"
    if name in KEEP_FRAME0:
        im = Image.open(p)
        im.seek(0)
        return im.convert("RGBA")
    C = dict(ms.SETS[name])
    C["anim"] = "static"
    C["_name"] = name
    ms.apply_set(C)
    return ms.animated(C, (800, 360), "Thanks for the follow!", 100, 1.0, 1)[0]


def base_corner(name):
    p = TW / name / "Corner" / "corner.gif"
    if name not in KEEP_FRAME0:
        old = ms.SETS[name]["anim"]
        ms.SETS[name]["anim"] = "static"
        try:
            rd.corner(name)
        finally:
            ms.SETS[name]["anim"] = old
    im = Image.open(p)
    im.seek(0)
    return im.convert("RGBA")


def clip(layer, base):
    layer.putalpha(ImageChops.multiply(layer.split()[3], base.split()[3]))
    return layer


def star(d, x, y, r, col):
    if r < 1:
        return
    d.polygon([(x, y - r), (x + r * 0.28, y - r * 0.28), (x + r, y), (x + r * 0.28, y + r * 0.28), (x, y + r), (x - r * 0.28, y + r * 0.28), (x - r, y), (x - r * 0.28, y - r * 0.28)], fill=col)


def fx(name, base, t):
    w, h = base.size
    C = ms.SETS[name]
    acc = C["accent"]
    out = base.copy()
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    u = h / 360.0
    if name == "Hood":
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out.alpha_composite(base.rotate(2.4 * math.sin(2 * math.pi * t), resample=Image.BICUBIC))
        return out
    if name == "Helmet":
        rnd = random.Random(5)
        for i in range(8):
            x = rnd.uniform(0.06, 0.94) * w
            y = rnd.choice((rnd.uniform(0.04, 0.16), rnd.uniform(0.84, 0.96))) * h
            ph = (t * 2 + i / 8.0) % 1.0
            star(d, x, y, 22 * u * max(0.0, math.sin(math.pi * ph)) ** 2, (255, 240, 170, 255))
        return Image.alpha_composite(out, ov)
    if name == "Slash":
        x = -0.3 * w + 1.6 * w * t
        d.polygon([(x, 0), (x + 40 * u, 0), (x - 0.35 * w + 40 * u, h), (x - 0.35 * w, h)], fill=(255, 255, 255, 235))
        d.polygon([(x + 80 * u, 0), (x + 96 * u, 0), (x - 0.35 * w + 96 * u, h), (x - 0.35 * w + 80 * u, h)], fill=(255, 150, 60, 235))
        out = Image.alpha_composite(out, clip(ov, base))
        if 0.45 < t < 0.55:
            fl = Image.new("RGBA", (w, h), (255, 255, 255, 70))
            out = Image.alpha_composite(out, clip(fl, base))
        return out
    if name == "Snake":
        for yy, col in ((0.9, acc), (0.1, C["accent2"])):
            pts = [(x, yy * h + 9 * u * math.sin(2 * math.pi * (x / (150 * u) - t))) for x in range(0, w, 4)]
            d.line(pts, fill=col + (255,), width=max(2, int(6 * u)), joint="curve")
        return Image.alpha_composite(out, clip(ov, base))
    if name == "Floral":
        rnd = random.Random(2)
        for i in range(9):
            x0, sp, ph = rnd.uniform(0.05, 0.95) * w, rnd.uniform(0.8, 1.3), rnd.random()
            y = ((t * sp + ph) % 1.0) * (h + 40 * u) - 20 * u
            x = x0 + 16 * u * math.sin(2 * math.pi * (t + ph))
            pts = [(x + math.cos(a) * 11 * u * (1 + 0.5 * math.cos(a)), y + math.sin(a) * 6 * u) for a in [j * math.pi / 8 for j in range(16)]]
            d.polygon(pts, fill=(250, 170, 210, 235))
        return Image.alpha_composite(out, ov)
    if name == "Tessel":
        x = (t * 1.2 - 0.1) * w
        y = 0.9 * h - abs(math.sin(2 * math.pi * t * 3)) * 0.22 * h
        r = 20 * u
        d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 250, 250, 255), outline=(10, 40, 30, 255), width=max(1, int(2 * u)))
        d.polygon([(x + math.cos(math.radians(-90 + 72 * i)) * r * 0.45, y + math.sin(math.radians(-90 + 72 * i)) * r * 0.45) for i in range(5)], fill=(10, 40, 30, 255))
        return Image.alpha_composite(out, ov)
    if name == "Perfum":
        rnd = random.Random(8)
        for i in range(12):
            x0, ph = rnd.uniform(0.08, 0.92) * w, rnd.random()
            f = (t + ph) % 1.0
            y = (1.05 - 1.15 * f) * h
            r = (14 + 22 * f) * u
            a = int(150 * math.sin(math.pi * f))
            dx = 12 * u * math.sin(6 * f)
            d.ellipse((x0 - r + dx, y - r, x0 + r + dx, y + r), fill=(255, 245, 240, a))
        ov = ov.filter(ImageFilter.GaussianBlur(3 * u))
        out = Image.alpha_composite(out, clip(ov, base))
        sp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sp)
        for i in range(5):
            ph = (t * 2 + i / 5.0) % 1.0
            star(sd, (0.15 + 0.17 * i) * w, (0.2 + 0.6 * ((i * 37) % 10) / 10.0) * h, 14 * u * max(0, math.sin(math.pi * ph)) ** 2, (255, 230, 170, 255))
        return Image.alpha_composite(out, clip(sp, base))
    if name == "Northbeam":
        ang = math.radians(-28 + 56 * (0.5 - 0.5 * math.cos(2 * math.pi * t)))
        cx, cy = w / 2, -0.05 * h
        L = 1.6 * h
        for wd, a in ((0.32, 50), (0.16, 80)):
            d.polygon([(cx, cy), (cx + L * math.tan(ang - wd), cy + L), (cx + L * math.tan(ang + wd), cy + L)], fill=(125, 235, 240, a))
        ov = ov.filter(ImageFilter.GaussianBlur(4 * u))
        return Image.alpha_composite(out, clip(ov, base))
    if name == "Strikeline":
        for k, (yy, hh) in enumerate(((0.28, 0.07), (0.46, 0.14), (0.7, 0.07))):
            f = (t + k * 0.18) % 1.0
            x = w * (1.2 - 2.4 * f)
            d.rectangle((x, yy * h, x + 0.5 * w, (yy + hh) * h), fill=(0, 168, 232, 190))
        return Image.alpha_composite(out, clip(ov, base))
    if name == "Purple":
        k = 0.5 + 0.5 * math.sin(2 * math.pi * t)
        a = base.split()[3].filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(10 * u))
        gl = Image.new("RGBA", (w, h), (255, 90, 190, 0))
        gl.putalpha(a.point(lambda v: int(v * 0.8 * k)))
        return Image.alpha_composite(gl, out)
    if name == "Rose":
        s_ = 1 + 0.045 * math.sin(2 * math.pi * t) ** 2
        big = base.resize((round(w * s_), round(h * s_)), Image.LANCZOS)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out.alpha_composite(big, ((w - big.width) // 2, (h - big.height) // 2))
        return out
    return out


def gif(frames, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=50, disposal=2, loop=0, optimize=False)


def main():
    names = sys.argv[1:] or ["Hood", "Helmet", "Slash", "Snake", "Floral", "Tessel", "Perfum", "Northbeam", "Strikeline", "Purple", "Rose"]
    for n in names:
        for kind, getb, fn in (("Alert", base_alert, "alert.gif"), ("Corner", base_corner, "corner.gif")):
            b = getb(n)
            gif([fx(n, b, i / N) for i in range(N)], TW / n / kind / fn)
        print("Saved", n, flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Shop branding for Ko-fi, Payhip and Gumroad in the same look as the existing page cover (cream, burgundy, rowan leaves):
wide headers, a 2:1 share preview and a square mark. No links, no personal info.
Reads Documents/twitch/Gumroad/<Set>/thumb.png and the rowan banner artwork, writes Documents/twitch/Shops/<channel>/*.png
    python tools/make_shop_designs.py"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
GUM = Path("C:/Users/SaphiresSilver/Documents/twitch/Gumroad")
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Shops")
LEAVES = ROOT / "images" / "twitch" / "Banner" / "petals_rowan_trees_banner.png"
MARK = ROOT / "images" / "twitch" / "Logo" / "rose_logo.png"
FONT = "C:/Windows/Fonts/georgiab.ttf"
SANS = "C:/Windows/Fonts/bahnschrift.ttf"
INK, WINE, SUB, CREAM = (58, 12, 24), (150, 30, 50), (88, 64, 72), (240, 230, 223)
SETS = ["Crimson", "Purple", "Floral", "Helmet", "Hood", "Starcaller", "Nightwing", "Slash", "Strikeline", "Snake"]   # multi-sale packs only


def sans(size):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    return f


def cover_crop(path, w, h):
    im = Image.open(path).convert("RGB")
    k = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h)).convert("RGBA")


def wash(img, solid=0.45, fade=0.62, strength=238):
    """Cream wash so text stays readable: opaque up to `solid` of the width, fading out by `fade`."""
    w, h = img.size
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x in range(w):
        t = x / w
        a = strength if t <= solid else (int(strength * (1 - (t - solid) / (fade - solid))) if t < fade else 0)
        d.line([(x, 0), (x, h)], fill=CREAM + (a,))
    img.alpha_composite(lay)


def thumb(name, size, radius=0.07):
    im = Image.open(GUM / name / "thumb.png").convert("RGBA").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius), fill=255)
    im.putalpha(m)
    return im


def shadowed(base, im, xy, blur=16, alpha=120, angle=0):
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.paste((40, 8, 16, alpha), (xy[0] + 6, xy[1] + 12), im.split()[3])
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(im, xy)


def chips(img, labels, x, y, size):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = sans(size)
    for s in labels:
        tw = d.textlength(s, font=f)
        pad = int(size * 0.7)
        d.rounded_rectangle([x, y, x + tw + pad * 2, y + size * 2], radius=size, fill=(255, 255, 255, 120), outline=WINE + (220,), width=max(2, size // 12))
        d.text((x + pad, y + size), s, font=f, fill=INK, anchor="lm")
        x += tw + pad * 2 + int(size * 0.7)
    img.alpha_composite(lay)


def headline(img, x, y, size, lines):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size)
    for i, s in enumerate(lines):
        d.text((x + 2, y + i * size * 1.12 + 3), s, font=f, fill=(255, 255, 255, 170))
        d.text((x, y + i * size * 1.12), s, font=f, fill=INK if i == 0 else WINE)


def header(w, h, tagline):
    img = cover_crop(LEAVES, w, h)
    wash(img, solid=0.42, fade=0.64)
    pad = int(h * 0.16)
    size = int(h * 0.15)
    headline(img, pad, int(h * 0.15), size, ("Twitch & VTuber", "Assets"))
    d = ImageDraw.Draw(img)
    d.text((pad, int(h * 0.15 + size * 2.5)), tagline, font=sans(int(h * 0.058)), fill=SUB, anchor="lm")
    chips(img, ["EMOTE PACKS", "STREAM GRAPHICS", "BRAND KITS", "VROID"], pad, int(h * 0.74), int(h * 0.038))
    n, t, x0 = 5, int(h * 0.60), int(w * 0.57)
    step = (w - x0 - pad - t) // (n - 1)
    for i, s in enumerate(SETS[:n]):
        shadowed(img, thumb(s, t), (x0 + i * step, int(h * 0.19) + abs(2 - i) * int(h * 0.025)), angle=[8, 3, 0, -3, -8][i])
    return img.convert("RGB")


def preview(w, h):
    img = cover_crop(LEAVES, w, h)
    img.alpha_composite(Image.new("RGBA", (w, h), CREAM + (205,)))
    pad = int(w * 0.05)
    size = int(h * 0.115)
    headline(img, pad, int(h * 0.085), size, ("Twitch & VTuber Assets",))
    d = ImageDraw.Draw(img)
    d.text((pad, int(h * 0.085 + size * 1.55)), "Emote packs · Stream graphics · Brand kits · VRoid assets", font=sans(int(h * 0.04)), fill=SUB, anchor="lm")
    n, gap = 5, int(w * 0.02)
    t = int(h * 0.27)
    x0 = (w - (n * t + (n - 1) * gap)) // 2
    for r in range(2):
        for i in range(n):
            shadowed(img, thumb(SETS[r * n + i], t), (x0 + i * (t + gap), int(h * 0.385) + r * (t + gap)), blur=10, alpha=110)
    return img.convert("RGB")


def mark(size):
    """Square mark: the same rose as the profile picture."""
    return Image.open(MARK).convert("RGB").resize((size, size), Image.LANCZOS)


def main():
    tag = "Ready-to-use art for streamers and VTubers"
    jobs = {
        "kofi/preview_2000x1000.png": preview(2000, 1000),
        "kofi/cover_1500x500.png": header(1500, 500, tag),
        "payhip/header_1920x600.png": header(1920, 600, tag),
        "payhip/preview_2000x1000.png": preview(2000, 1000),
        "payhip/mark_500.png": mark(500),
        "gumroad/cover_1600x500.png": header(1600, 500, tag),
        "gumroad/preview_2000x1000.png": preview(2000, 1000),
        "gumroad/mark_500.png": mark(500),
    }
    for name, im in jobs.items():
        (OUT / name).parent.mkdir(parents=True, exist_ok=True)
        im.save(OUT / name, optimize=True)
        print(name, im.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One logo per set, shaped like the set (shield, hexagon, oval, triangle, octagon...) around that set's own artwork."""
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import make_rose as mr
import make_sets as ms

TW = ROOT / "images" / "twitch"
NAMES = {"Snake": "Petals Of Iron", "Floral": "Petals Of Iron", "Slash": "PETALS OF IRON", "Tessel": "Tessel", "Perfum": "Perfum",
         "Northbeam": "Northbeam", "Strikeline": "STRIKELINE"}


def poly_mask(pts, size, ss=2):
    m = Image.new("L", (size[0] * ss, size[1] * ss), 0)
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in pts], fill=255)
    return m.resize(size, Image.LANCZOS)


def logo(name):
    C = dict(ms.SETS[name])
    ms.apply_set(C)
    S = 2000
    cx, cy, R = S // 2, 820, 700
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    kind = C["shape"]
    outer = ms.shape_pts(kind, cx, cy + (30 if kind == "triangle" else 0), R * 1.12)
    layers = [(outer, C["dark"]), (ms.shape_pts(kind, cx, cy + (30 if kind == "triangle" else 0), R * 1.05), C["accent"]),
              (ms.shape_pts(kind, cx, cy + (30 if kind == "triangle" else 0), R * 0.99), C["dark"])]
    m0 = poly_mask(outer, (S, S))
    img = shadow(img, m0, (0, 22), 30, (0, 0, 0), 0.5)
    for pts, col in layers:
        lay = Image.new("RGBA", (S, S), col + (255,))
        lay.putalpha(poly_mask(pts, (S, S)))
        img = Image.alpha_composite(img, lay)
    inner = ms.shape_pts(kind, cx, cy + (30 if kind == "triangle" else 0), R * 0.94)
    if name == "Slash":
        art = Image.new("RGBA", (S, S), (0, 0, 0, 255))
        ad = ImageDraw.Draw(art)
        for i, (x, wd, col) in enumerate(((-300, 160, (230, 20, 70)), (-60, 90, (255, 255, 255)), (130, 200, (255, 150, 60)), (420, 70, (255, 255, 255)), (560, 150, (230, 20, 70)), (800, 90, (255, 255, 255)))):
            ad.polygon([(cx + x, cy - 800), (cx + x + wd, cy - 800), (cx + x + wd - 700, cy + 800), (cx + x - 700, cy + 800)], fill=col + (255,))
    else:
        pim, patch = ms.portrait(C["mascot"], C)
        px = int(R * (2.3 if C["mascot"] == "flower" else 1.9))
        art = Image.new("RGBA", (S, S), C["fill"] + (255,) if sum(C["fill"]) < 500 else C["accent2"] + (255,))
        pic = pim.resize((px, px), Image.LANCZOS)
        art.alpha_composite(pic, (cx - px // 2, cy + (30 if kind == "triangle" else 0) - px // 2))
    lay = art.copy()
    lay.putalpha(ImageChops.multiply(art.split()[3], poly_mask(inner, (S, S))))
    img = Image.alpha_composite(img, lay)
    font_name = C["font"]
    txt = NAMES[name]
    sz = ms.fit_size(txt, font_name, 1500, 230)
    m = text_mask((S, S), txt, font(font_name, sz), (cx, 1790))
    img = shadow(img, m, (0, 8), 10, (0, 0, 0), 0.7)
    tc = (C["accent"], tuple(int(c * 0.8) for c in C["accent"])) if name in ("Slash",) else ((250, 250, 250), (210, 214, 224))
    img = fill_mask(img, m, tc[0], tc[1])
    return img


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(NAMES)):
        p = TW / n / "Logo" / "logo.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        logo(n).save(p, optimize=True)
        print("Saved", n, flush=True)
    print("done")

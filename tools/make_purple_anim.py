#!/usr/bin/env python3
"""Animated (looping GIF) versions of some purple-set emotes: heart beats, sparkle spins, gems and crown shine."""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_purple as mp

N = 24
KINDS = ("heart", "sparkle", "gem", "crown", "hype")


def shine(size, t, strength=130):
    """A soft diagonal white band that sweeps across the emote."""
    w = h = size
    x = -0.4 * size + 1.8 * size * t
    band = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(band)
    d.polygon([(x, 0), (x + 0.16 * size, 0), (x - 0.34 * size, h), (x - 0.5 * size, h)], fill=strength)
    return band.filter(ImageFilter.GaussianBlur(size * 0.03))


def frame(kind, base, t):
    size = base.width
    img = base
    if kind == "heart":
        s = 1 + 0.12 * max(0, math.sin(2 * math.pi * t * 2)) ** 2
        img = base.resize((round(size * s), round(size * s)), Image.LANCZOS)
    elif kind == "sparkle":
        s = 1 + 0.06 * math.sin(2 * math.pi * t)
        img = base.rotate(90 * t, resample=Image.BICUBIC, center=(size / 2, size / 2))
        img = img.resize((round(size * s), round(size * s)), Image.LANCZOS)
    elif kind == "crown":
        dy = -abs(math.sin(math.pi * t * 2)) * size * 0.05
        canvas = Image.new("RGBA", base.size, (0, 0, 0, 0))
        canvas.alpha_composite(base, (0, round(dy)))
        img = canvas
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    out.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    if kind in ("gem", "crown", "hype"):
        a = out.split()[3]
        sh = ImageChops.multiply(shine(size, t), a)
        white = Image.new("RGBA", base.size, (255, 255, 255, 0))
        white.putalpha(sh)
        out = Image.alpha_composite(out, white)
    return out


def main():
    for kind in KINDS:
        for size in (448, 112, 56, 28):
            base = mp.emote(kind, size)
            frames = [frame(kind, base, i / N) for i in range(N)]
            path = mp.OUT / "Emotes" / f"{kind}_{size}.gif"
            path.parent.mkdir(parents=True, exist_ok=True)
            frames[0].save(path, save_all=True, append_images=frames[1:], duration=45, disposal=2, loop=0, optimize=False)
            print("Saved", path.relative_to(mp.ROOT))


if __name__ == "__main__":
    main()

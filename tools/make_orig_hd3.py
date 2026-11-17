#!/usr/bin/env python3
"""Smooth animated-PNG versions of the user's own Petals alert and corner (same frames, same animation, higher quality).
Saved in images/twitch-large/; the original GIFs are never changed."""
import sys
from PIL import Image, ImageFilter, ImageSequence

import vecup
from art import ROOT

SRC = ROOT / "images" / "twitch"
LARGE = ROOT / "images" / "twitch-large"


def smooth_up(f, out):
    """Same picture, bigger: Lanczos enlargement in premultiplied alpha, edge transparency smoothed (no blotches, no stair steps)."""
    ow = out
    oh = round(f.height * out / f.width)
    prem = f.convert("RGBa").resize((ow, oh), Image.LANCZOS).convert("RGBA")
    r, g, b, _ = prem.split()
    rgb = Image.merge("RGB", (r, g, b)).filter(ImageFilter.UnsharpMask(radius=1.6, percent=95, threshold=2))
    a = f.split()[3].resize((ow, oh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.3))
    a = a.point(lambda v: 0 if v < 70 else 255 if v > 185 else int((v - 70) * 255 / 115))
    r, g, b = rgb.split()
    return Image.merge("RGBA", (r, g, b, a))


def run(rel, out):
    with Image.open(SRC / rel) as im:
        frames, dur = [], []
        for f in ImageSequence.Iterator(im):
            dur.append(f.info.get("duration", 60))
            frames.append(f.convert("RGBA"))
    big = [smooth_up(f, out) for f in frames]
    dest = (LARGE / rel).with_suffix(".png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    big[0].save(dest, format="PNG", save_all=True, append_images=big[1:], duration=dur, loop=0, disposal=1)
    print("Saved", dest, flush=True)


if __name__ == "__main__":
    run("Alert/petals_alert.gif", 1200)
    run("Corner/petals_corner.gif", 880)

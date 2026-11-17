#!/usr/bin/env python3
"""Smooth animated-PNG versions of the user's own Petals alert and corner (same frames, same animation, higher quality).
Saved in images/twitch-large/; the original GIFs are never changed."""
import sys
from PIL import Image, ImageSequence

import vecup
from art import ROOT

SRC = ROOT / "images" / "twitch"
LARGE = ROOT / "images" / "twitch-large"


def run(rel, out):
    with Image.open(SRC / rel) as im:
        frames = [f.convert("RGBA") for f in ImageSequence.Iterator(im)]
        dur = im.info.get("duration", 60)
    pal = vecup.palette(frames, k=14)
    big = [vecup.enlarge(f, pal, out=out) for f in frames]
    dest = (LARGE / rel).with_suffix(".png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    big[0].save(dest, format="PNG", save_all=True, append_images=big[1:], duration=dur, loop=0, disposal=1)
    print("Saved", dest, flush=True)


if __name__ == "__main__":
    run("Alert/petals_alert.gif", 1200)
    run("Corner/petals_corner.gif", 880)

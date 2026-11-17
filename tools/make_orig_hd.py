#!/usr/bin/env python3
"""High-quality redraws of the original emotes: the same faces and props, drawn natively at 448 px (no enlarging).
They go to images/twitch-large/ next to their originals; the original files in images/twitch/ are never changed."""
import sys
from PIL import Image

import make_rose as mr

LARGE = mr.ROOT / "images" / "twitch-large"


def main():
    mr.SS = 6          # draw at 6x and shrink: smooth, non-pixelated lines
    for folder, name, mood, extra in mr.EMOTE_SETS:
        d = LARGE / folder
        d.mkdir(parents=True, exist_ok=True)
        if name in mr.ANIMATED:
            anim = {"happycat": "sway", "laughing": "bounce", "mad": "shake", "playful": "sway", "sleepy": "sway"}[name]
            frames = [mr.emote(mood, extra, 448, i / 20, anim) for i in range(20)]
            # animated PNG: full smooth edges (a GIF can only have hard-edged transparency, which looks pixelated)
            frames[0].save(d / f"{name}_112.png", format="PNG", save_all=True, append_images=frames[1:], duration=60, loop=0, disposal=1)
            g = d / f"{name}_112.gif"
            if g.exists():
                g.unlink()
        else:
            mr.emote(mood, extra, 448).save(d / f"{name}_112.png", optimize=True)
        print("Saved", folder, name, flush=True)


if __name__ == "__main__":
    main()

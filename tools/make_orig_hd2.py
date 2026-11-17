#!/usr/bin/env python3
"""High-quality redraws of the original sub badges, flair and channel point icon (drawn natively at 432 px, no enlarging).
Saved in images/twitch-large/ next to the originals, which are never changed."""
import make_rose as mr

LARGE = mr.ROOT / "images" / "twitch-large"


def main():
    mr.SS = 6
    (LARGE / "Badges").mkdir(parents=True, exist_ok=True)
    (LARGE / "Flair").mkdir(parents=True, exist_ok=True)
    for t in mr.BADGES:
        mr.badge(t).save(LARGE / "Badges" / f"{t[0]}_72.png", optimize=True)
        print("badge", t[0], flush=True)
    for tier in (2, 3):
        mr.flair(tier).save(LARGE / "Flair" / f"tier{tier}_flair_72.png", optimize=True)
    mr.points_icon("berry").save(LARGE / "channel_points_112.png", optimize=True)
    print("done")


if __name__ == "__main__":
    main()

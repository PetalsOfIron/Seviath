#!/usr/bin/env python3
"""Name-free versions of the three character kits (no brand, no tagline) for the sold packs.
Usage: py make_neutral.py Nightwing|Starcaller|Crimson
Output: Documents/twitch/Neutral/<Kit>/..."""
import sys
from pathlib import Path

kit = sys.argv[1]
sys.argv = sys.argv[:1]
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral") / kit
OUT.mkdir(parents=True, exist_ok=True)

import make_nightwing as nw

nw.NAME = "LIVE STREAM"
nw.TAGLINE = "GAMING  ·  ART  ·  CHAT"
nw.LOGO_TEXT = False   # logos carry no lettering at all


def finish(out, kit):
    """Center the lettering-free logo on a square, then add X (Twitter) profile picture and header versions."""
    import math
    from PIL import Image
    import make_gumroad as mg
    main = mg.COLORS[kit]
    bg = tuple(int(c * 0.22) for c in main) + (255,)
    logos = sorted((out / "Logo").glob("*_logo.png"))
    avs = sorted((out / "Logo").glob("*_avatar.png"))
    for p in logos:
        im = Image.open(p).convert("RGBA")
        box = im.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()
        im = im.crop(box)
        w, h = im.size
        side = int(max(w, h) * 1.10)
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.alpha_composite(im, ((side - w) // 2, (side - h) // 2))
        sq = sq.resize((2000, 2000), Image.LANCZOS)
        sq.save(p, optimize=True)
        # X profile picture: the whole logo inside the circle X crops to
        k = 372 / math.hypot(w, h)
        small = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
        card = Image.new("RGBA", (400, 400), bg)
        card.alpha_composite(small, ((400 - small.width) // 2, (400 - small.height) // 2))
        card.convert("RGB").save(out / "Logo" / "x_profile_logo_400.png", optimize=True)
    for p in avs:
        im = Image.open(p).convert("RGBA").resize((400, 400), Image.LANCZOS)
        card = Image.new("RGBA", (400, 400), bg)
        card.alpha_composite(im)
        card.convert("RGB").save(out / "Logo" / "x_profile_400.png", optimize=True)
    ban = out / "Banner" / "profile_banner_1200x480.png"
    if ban.exists():
        im = Image.open(ban).convert("RGB")
        k = 1500 / im.width
        im = im.resize((1500, int(im.height * k)), Image.LANCZOS)
        top = (im.height - 500) // 2
        im.crop((0, top, 1500, top + 500)).save(out / "Banner" / "x_header_1500x500.png", optimize=True)

if kit == "Nightwing":
    import make_nightwing2 as n2
    nw.OUT = OUT
    n2.OUT = OUT
    nw.main()
    n2.main()
elif kit == "Starcaller":
    import make_starcaller as sc
    import make_starcaller2 as s2
    import make_starcaller3 as s3
    nw.OUT = sc.OUT = s2.OUT = OUT
    if hasattr(s3, "OUT"):
        s3.OUT = OUT
    sc.main()
    s2.main()
    s3.main()
elif kit == "Crimson":
    import make_crimson as cr
    nw.OUT = cr.OUT = OUT
    cr.main()
finish(OUT, kit)
print("neutral done", kit)

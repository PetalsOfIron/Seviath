#!/usr/bin/env python3
"""Panels with each set's own icon (a crop of its artwork, or its main prop) but no drawn face."""
import sys
from PIL import Image, ImageDraw

from art import *  # noqa: F401,F403
import make_sets as ms
import make_redo as rd
import make_final as mf

TW = ROOT / "images" / "twitch"
ICON_PROP = {"Slash": "bolt"}


def icon(C, name, size):
    pim, _ = ms.portrait(C["mascot"], C)
    if pim is not None:
        ring = Image.new("RGBA", (size + 24, size + 24), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((0, 0, size + 23, size + 23), fill=C["accent"] + (255,), outline=C["dark"] + (255,), width=6)
        ring.alpha_composite(rd.portrait_disc(C, size), (12, 12))
        return ring
    disc = Image.new("RGBA", (size + 24, size + 24), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse((0, 0, size + 23, size + 23), fill=C["main"] + (255,), outline=C["dark"] + (255,), width=6)
    p = rd.prop_img(C, ICON_PROP.get(name, "star"), int(size * 0.7))
    disc.alpha_composite(p, ((size + 24 - p.width) // 2, (size + 24 - p.height) // 2))
    return disc


def build(name):
    C = dict(ms.SETS[name]); C["_name"] = name
    ms.apply_set(C)
    W, H = 1280, 400
    ic = icon(C, name, 230)
    for fn_, title in ms.PANELS:
        if name == "Hood":
            import make_hood as mh
            img = mh.paper_panel((W, H), scale=1.2, seed=11)
        else:
            img = ms.shaped_panel(C, (W, H)) if C.get("pshape") else ms.panel_base((W, H), C, 1.2)
        img.alpha_composite(ic, (110 if C.get("pshape") not in ("slant", "arrow", "cartouche") else 150, (H - ic.height) // 2))
        sz = ms.fit_size(title, C["font"], 700, 150)
        if name == "Hood":
            img = mh.lettered(img, title, (W / 2 + 140, H / 2 + sz * 0.34), sz)
        else:
            img = ms.title_text(img, title, (W / 2 + 140, H / 2 + sz * 0.34), sz, C)
        p = TW / name / "Panels" / f"{fn_}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(p, optimize=True)
    print("Saved", name, flush=True)


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(mf.BADGES)):
        build(n)
    print("done")

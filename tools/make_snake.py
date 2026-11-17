#!/usr/bin/env python3
"""
Full Twitch set in the snake style (cyan and blue gradient, yellow / orange / blue accents, navy gothic lettering).
The panels, emotes, badges, flair, channel point icons, overlay and alert come from the same drawing code as the
purple set, re-coloured with the snake painting's palette. The "starting soon / be right back / offline" screens use
your snake painting itself.

    python tools/make_snake.py
"""
import re
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ------------------------------------------------------------------------------------------ palette
NAVY, NAVY_D = "(12, 44, 100)", "(6, 24, 64)"
PALETTE_LINES = {
    "P_DARK, P_MID, P_LIGHT = (42, 8, 108), (74, 12, 138), (96, 20, 160)":
        "P_DARK, P_MID, P_LIGHT = (96, 206, 236), (80, 178, 232), (60, 140, 220)",
    "PINK, MAGENTA, VIOLET, BLUE_V = (255, 70, 140), (236, 60, 190), (140, 40, 255), (96, 40, 220)":
        "PINK, MAGENTA, VIOLET, BLUE_V = (246, 204, 70), (236, 150, 66), (30, 96, 204), (14, 60, 150)",
    "LAV, SILVER, SILVER_D = (236, 230, 252), (226, 222, 244), (150, 140, 190)":
        "LAV, SILVER, SILVER_D = (10, 44, 100), (250, 252, 255), (30, 84, 150)",
    "CORAL, CORAL_D, ROSE_BEAD = (236, 100, 84), (150, 40, 60), (244, 206, 214)":
        "CORAL, CORAL_D, ROSE_BEAD = (250, 206, 72), (170, 108, 18), (210, 244, 250)",
    "INK = (28, 4, 66)": "INK = (8, 32, 76)",
}
LITERALS = {
    "fill=(70, 12, 140)": "fill=(44, 122, 206)",          # medallion plate
    "fill=(96, 20, 160)": "fill=(44, 122, 206)",          # gg / hype plate
    "(236, 70, 150)": "(60, 190, 200)", "(255, 130, 190)": "(150, 230, 236)",   # heart, 6-month badge -> teal
    "(200, 190, 240)": "(200, 214, 236)",
    "text_blackletter(canvas, \"P\"": "text_blackletter(canvas, \"P\"",
    "(214, 40, 90)": "(40, 170, 220)",                    # beads
    "(246, 242, 255)": NAVY, "(206, 196, 246)": NAVY_D,   # light text -> navy text (the background is light)
    "(238, 232, 252)": NAVY, "(200, 190, 240)": NAVY_D,
    "(170, 90, 255)": "(60, 200, 180)", "(70, 20, 150)": "(10, 90, 90)",     # amethyst emote -> teal
    "(230, 40, 90), dark=(110, 10, 50)": "(240, 150, 60), dark=(130, 60, 10)",  # ruby emote -> amber
    "(10, 0, 30)": "(255, 255, 255)", "(12, 0, 40)": "(255, 255, 255)",   # text shadow -> soft light halo
}


def load_theme_module():
    src = (HERE / "make_purple.py").read_text(encoding="utf-8")
    for a, b in PALETTE_LINES.items():
        assert a in src, a
        src = src.replace(a, b)
    for a, b in LITERALS.items():
        src = src.replace(a, b)
    src = src.replace('OUT = ROOT / "images" / "twitch" / "Purple"', 'OUT = ROOT / "images" / "twitch" / "Snake"')
    src = src.replace("layer = fill_mask(layer, m, (246, 242, 255), (206, 196, 246))", "layer = fill_mask(layer, m, (255, 255, 255), (214, 232, 250))")
    src = src.replace("layer = fill_mask(layer, m, " + NAVY + ", " + NAVY_D + ")", "layer = fill_mask(layer, m, (255, 255, 255), (214, 232, 250))")
    mod = types.ModuleType("make_purple")
    mod.__file__ = str(HERE / "make_purple.py")
    sys.modules["make_purple"] = mod            # make_purple_anim imports this name
    exec(compile(src, "make_snake_theme", "exec"), mod.__dict__)
    return mod


def screens():
    """Starting soon / Be right back / Offline built on the snake painting (make_offline layout)."""
    off = (HERE / "make_offline.py").read_text(encoding="utf-8")
    jobs = [
        ("snake_starting_soon.png", "Starting soon", 150, "The stream begins shortly", "Grab a drink and get comfy", "Back in a few minutes"),
        ("snake_be_right_back.png", "Be right back", 150, "I will be back in a moment", "Stretch your legs", "Don't go far"),
        ("snake_offline.png", "Offline", 300, "The stream has ended", "Thank you for stopping by", "See you next stream"),
    ]
    out_dir = HERE.parent / "images" / "twitch" / "Snake" / "Screens"
    for fname, title, size, l1, l2, l3 in jobs:
        s = off
        s = s.replace('OUT = ROOT / "images" / "twitch" / "Offline" / "petals_offline_screen.png"', f'OUT = ROOT / "images" / "twitch" / "Snake" / "Screens" / "{fname}"')
        s = s.replace('"Offline"', f'"{title}"')
        s = s.replace('"OLDENGL.TTF"), 300)', f'"OLDENGL.TTF"), {size})')
        s = s.replace('"The stream has ended"', f'"{l1}"').replace('"Thank you for stopping by"', f'"{l2}"').replace('"See you next stream"', f'"{l3}"')
        s = s.replace("cx = 1650", "cx = 1560").replace("cx = 1585", "cx = 1560")
        mod = types.ModuleType("mo_" + fname)
        mod.__file__ = str(HERE / "make_offline.py")
        exec(compile(s, "make_snake_screen", "exec"), mod.__dict__)
        mod.main()
    return out_dir


def main():
    screens()
    mp = load_theme_module()
    OUT = mp.OUT
    for t in mp.PANELS:
        mp.save(mp.panel(t), OUT / "Panels" / f"{t.lower().replace(' ', '_')}.png")
    for e in mp.EMOTES:
        for s in (448, 112, 56, 28):
            mp.save(mp.emote(e, s), OUT / "Emotes" / f"{e}_{s}.png", rgba=True)
    for t in mp.BADGES:
        mp.save(mp.badge(t), OUT / "Badges" / f"{t[0]}_432.png", rgba=True)
    for k in mp.POINTS:
        mp.save(mp.point_icon(k), OUT / "Points" / f"points_{k}_432.png", rgba=True)
    for t in (2, 3):
        mp.save(mp.flair(t), OUT / "Flair" / f"tier{t}_flair_432.png", rgba=True)
    mp.save(mp.overlay_frame(), OUT / "Overlay" / "snake_overlay_frame.png", rgba=True)
    frames = mp.alert_frames("Thanks for the follow!")
    p = OUT / "Alert" / "snake_alert.gif"
    p.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=50, disposal=2, loop=0, optimize=False)
    print("Saved", p)
    import make_purple_anim
    make_purple_anim.main()
    print("done")


if __name__ == "__main__":
    main()

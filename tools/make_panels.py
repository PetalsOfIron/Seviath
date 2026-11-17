#!/usr/bin/env python3
"""
Panels (About Me, Schedule, Chat rules, Donation, FAQ, PC setup, Links, Socials) in the styles that did not have them:
floral (navy to peach with gold and sapphire), slash (crimson with white / orange / black diagonals),
helmet (deep purple with gold and burgundy) and hood (maroon with cream and steel).

    python tools/make_panels.py
"""
import re
import sys
import types
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parent

STYLES = {
    "Floral": dict(
        P="(30, 28, 72), (110, 74, 108), (214, 140, 112)", PINK="(255, 226, 130)", MAGENTA="(214, 160, 70)", VIOLET="(176, 110, 214)",
        BLUE_V="(110, 70, 170)", SILVER="(246, 208, 104)", SILVER_D="(176, 122, 30)", CORAL="(78, 92, 140)", CORAL_D="(22, 28, 60)",
        ROSE="(252, 236, 200)", INK="(20, 14, 52)", text=("(252, 250, 255)", "(226, 214, 244)")),
    "Slash": dict(
        P="(58, 4, 20), (170, 14, 56), (236, 40, 92)", PINK="(255, 255, 255)", MAGENTA="(255, 150, 60)", VIOLET="(255, 162, 62)",
        BLUE_V="(24, 0, 8)", SILVER="(250, 250, 250)", SILVER_D="(120, 110, 114)", CORAL="(255, 150, 60)", CORAL_D="(150, 60, 10)",
        ROSE="(255, 240, 230)", INK="(30, 0, 10)", text=("(255, 255, 255)", "(255, 220, 180)")),
    "Helmet": dict(
        P="(26, 14, 52), (36, 20, 66), (56, 32, 96)", PINK="(226, 184, 80)", MAGENTA="(150, 44, 76)", VIOLET="(236, 196, 92)",
        BLUE_V="(124, 36, 66)", SILVER="(244, 214, 128)", SILVER_D="(176, 130, 40)", CORAL="(180, 52, 84)", CORAL_D="(70, 14, 36)",
        ROSE="(252, 238, 200)", INK="(16, 6, 34)", text=("(252, 244, 222)", "(236, 206, 130)")),
    "Hood": dict(
        P="(48, 2, 4), (96, 6, 8), (140, 12, 14)", PINK="(250, 240, 234)", MAGENTA="(190, 60, 60)", VIOLET="(236, 226, 216)",
        BLUE_V="(96, 12, 14)", SILVER="(206, 206, 216)", SILVER_D="(110, 110, 130)", CORAL="(156, 156, 176)", CORAL_D="(54, 54, 76)",
        ROSE="(250, 236, 230)", INK="(30, 4, 6)", text=("(252, 244, 238)", "(226, 206, 196)")),
    "Tessel": dict(
        P="(10, 40, 30), (16, 64, 46), (24, 96, 60)", PINK="(223, 255, 61)", MAGENTA="(31, 163, 74)", VIOLET="(31, 163, 74)",
        BLUE_V="(14, 59, 46)", SILVER="(245, 247, 245)", SILVER_D="(120, 140, 130)", CORAL="(223, 255, 61)", CORAL_D="(90, 120, 10)",
        ROSE="(245, 247, 245)", INK="(6, 24, 18)", text=("(250, 252, 250)", "(206, 214, 208)")),
    "Perfum": dict(
        P="(84, 28, 52), (120, 52, 82), (170, 90, 110)", PINK="(226, 190, 120)", MAGENTA="(234, 190, 178)", VIOLET="(184, 150, 84)",
        BLUE_V="(130, 70, 100)", SILVER="(250, 232, 190)", SILVER_D="(184, 150, 84)", CORAL="(234, 170, 160)", CORAL_D="(120, 50, 60)",
        ROSE="(247, 238, 222)", INK="(54, 16, 34)", text=("(252, 244, 236)", "(234, 205, 190)")),
    "Northbeam": dict(
        P="(14, 24, 52), (24, 40, 96), (40, 60, 140)", PINK="(125, 235, 240)", MAGENTA="(88, 100, 214)", VIOLET="(88, 100, 214)",
        BLUE_V="(24, 40, 110)", SILVER="(240, 248, 252)", SILVER_D="(120, 150, 190)", CORAL="(125, 235, 240)", CORAL_D="(30, 90, 140)",
        ROSE="(224, 255, 251)", INK="(8, 14, 36)", text=("(240, 248, 252)", "(190, 214, 240)")),
    "Strikeline": dict(
        P="(16, 24, 32), (31, 58, 95), (1, 52, 94)", PINK="(0, 168, 232)", MAGENTA="(0, 168, 232)", VIOLET="(0, 110, 170)",
        BLUE_V="(31, 58, 95)", SILVER="(232, 232, 232)", SILVER_D="(120, 130, 140)", CORAL="(0, 168, 232)", CORAL_D="(0, 70, 110)",
        ROSE="(232, 232, 232)", INK="(6, 10, 16)", text=("(250, 252, 255)", "(200, 214, 228)")),
    "Rose": dict(
        P="(96, 12, 28), (140, 22, 44), (186, 44, 66)", PINK="(255, 214, 96)", MAGENTA="(240, 120, 134)", VIOLET="(255, 214, 96)",
        BLUE_V="(112, 18, 36)", SILVER="(244, 224, 214)", SILVER_D="(150, 130, 124)", CORAL="(186, 30, 50)", CORAL_D="(90, 8, 20)",
        ROSE="(244, 224, 214)", INK="(52, 6, 14)", text=("(250, 238, 230)", "(226, 196, 190)")),
}


def load_theme(st):
    src = (HERE / "make_purple.py").read_text(encoding="utf-8")
    src = src.replace("P_DARK, P_MID, P_LIGHT = (42, 8, 108), (74, 12, 138), (96, 20, 160)", f"P_DARK, P_MID, P_LIGHT = {st['P']}")
    src = src.replace("PINK, MAGENTA, VIOLET, BLUE_V = (255, 70, 140), (236, 60, 190), (140, 40, 255), (96, 40, 220)",
                      f"PINK, MAGENTA, VIOLET, BLUE_V = {st['PINK']}, {st['MAGENTA']}, {st['VIOLET']}, {st['BLUE_V']}")
    src = src.replace("LAV, SILVER, SILVER_D = (236, 230, 252), (226, 222, 244), (150, 140, 190)", f"LAV, SILVER, SILVER_D = {st['text'][0]}, {st['SILVER']}, {st['SILVER_D']}")
    src = src.replace("CORAL, CORAL_D, ROSE_BEAD = (236, 100, 84), (150, 40, 60), (244, 206, 214)", f"CORAL, CORAL_D, ROSE_BEAD = {st['CORAL']}, {st['CORAL_D']}, {st['ROSE']}")
    src = src.replace("INK = (28, 4, 66)", f"INK = {st['INK']}")
    src = src.replace("fill=(238, 232, 252), grad_to=(200, 190, 240)", f"fill={st['text'][0]}, grad_to={st['text'][1]}")
    src = src.replace("(12, 0, 40), 0.7", f"{st['INK']}, 0.75")
    mod = types.ModuleType("theme_" + st["P"][:6])
    mod.__file__ = str(HERE / "make_purple.py")
    sys.modules.setdefault("make_purple", mod)   # make_purple's own imports need nothing else
    exec(compile(src, "panels_theme", "exec"), mod.__dict__)
    return mod


def slash_bg(mod):
    orig = mod.gradient_bg

    def bg(size, left=None, right=None, glow=0.16):
        img = orig(size, mod.P_DARK, mod.P_LIGHT, glow)
        w, h = size
        layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        import random
        rnd = random.Random(3)
        for i in range(26):
            x = rnd.randint(-h, w)
            wd = rnd.choice((8, 10, 14, 26, 40))
            col = rnd.choice(((255, 255, 255, 235), (20, 0, 8, 235), (255, 255, 255, 150), (255, 150, 60, 200)))
            d.polygon([((x) * 2, 0), ((x + wd) * 2, 0), ((x + wd - h) * 2, h * 2), ((x - h) * 2, h * 2)], fill=col)
        img.alpha_composite(layer.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.4)))
        # dark veil so the lettering stays readable
        veil = Image.new("RGBA", (w, h), (30, 0, 10, 120))
        img.alpha_composite(veil)
        return img
    mod.gradient_bg = bg


def main():
    names = sys.argv[1:] or list(STYLES)
    for style in names:
        mod = load_theme(STYLES[style])
        if style == "Slash":
            slash_bg(mod)
        out = ROOT / "images" / "twitch" / style / "Panels"
        out.mkdir(parents=True, exist_ok=True)
        for t in mod.PANELS:
            mod.save(mod.panel(t), out / f"{t.lower().replace(' ', '_')}.png")
    print("done")


if __name__ == "__main__":
    main()

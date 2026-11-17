#!/usr/bin/env python3
"""
Full sets (screens, logo, banner, overlay frame, alert, animated corner, sub badges, channel point icons, flair,
all emotes incl. animated ones, panels) for the styles that only had panels: Floral, Slash, Helmet, Hood.
Also adds the animated corner to Purple.

    python tools/make_styles.py Slash        # one style
    python tools/make_styles.py              # all
    python tools/make_styles.py corners      # just the Purple corner
"""
import math
import sys
import types
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_panels as mpn  # noqa: E402

EXTRA = {   # per-style colours for the parts make_panels does not touch
    "Floral": dict(plate="(76, 52, 124)", heart="(214, 120, 200)", bead="(244, 206, 100)", ame=("(176, 110, 214)", "(70, 40, 120)"), base="(220, 208, 240)", skip=("offline", "logo", "banner")),
    "Slash": dict(plate="(120, 8, 40)", heart="(255, 255, 255)", bead="(255, 160, 60)", ame=("(255, 160, 60)", "(130, 50, 10)"), base="(240, 240, 240)", skip=()),
    "Helmet": dict(plate="(70, 30, 90)", heart="(190, 56, 92)", bead="(240, 200, 96)", ame=("(236, 196, 92)", "(110, 76, 14)"), base="(224, 190, 100)", skip=()),
    "Hood": dict(plate="(110, 10, 12)", heart="(250, 240, 234)", bead="(206, 206, 216)", ame=("(206, 206, 216)", "(80, 80, 100)"), base="(206, 206, 216)", skip=()),
}


def themed(style):
    st = dict(mpn.STYLES[style])
    ex = EXTRA[style]
    src = (HERE / "make_purple.py").read_text(encoding="utf-8")
    reps = [
        ("P_DARK, P_MID, P_LIGHT = (42, 8, 108), (74, 12, 138), (96, 20, 160)", "P_DARK, P_MID, P_LIGHT = " + st["P"]),
        ("PINK, MAGENTA, VIOLET, BLUE_V = (255, 70, 140), (236, 60, 190), (140, 40, 255), (96, 40, 220)",
         "PINK, MAGENTA, VIOLET, BLUE_V = %s, %s, %s, %s" % (st["PINK"], st["MAGENTA"], st["VIOLET"], st["BLUE_V"])),
        ("LAV, SILVER, SILVER_D = (236, 230, 252), (226, 222, 244), (150, 140, 190)",
         "LAV, SILVER, SILVER_D = %s, %s, %s" % (st["text"][0], st["SILVER"], st["SILVER_D"])),
        ("CORAL, CORAL_D, ROSE_BEAD = (236, 100, 84), (150, 40, 60), (244, 206, 214)",
         "CORAL, CORAL_D, ROSE_BEAD = %s, %s, %s" % (st["CORAL"], st["CORAL_D"], st["ROSE"])),
        ("INK = (28, 4, 66)", "INK = " + st["INK"]),
        ("fill=(238, 232, 252), grad_to=(200, 190, 240)", "fill=%s, grad_to=%s" % (st["text"][0], st["text"][1])),
        ("(12, 0, 40), 0.7", st["INK"] + ", 0.75"),
        ("fill=(70, 12, 140)", "fill=" + ex["plate"]), ("fill=(96, 20, 160)", "fill=" + ex["plate"]),
        ("(214, 40, 90)", ex["bead"]), ("(236, 70, 150)", ex["heart"]), ("(255, 130, 190)", ex["heart"]),
        ("(200, 190, 240)", ex["base"]),
        ("(170, 90, 255)", ex["ame"][0]), ("(70, 20, 150)", ex["ame"][1]),
        ("(246, 242, 255), (206, 196, 246)", "%s, %s" % (st["text"][0], st["text"][1])),
        ('OUT = ROOT / "images" / "twitch" / "Purple"', 'OUT = ROOT / "images" / "twitch" / "%s"' % style),
    ]
    for a, b in reps:
        src = src.replace(a, b)
    mod = types.ModuleType("make_purple")
    mod.__file__ = str(HERE / "make_purple.py")
    sys.modules["make_purple"] = mod
    exec(compile(src, "theme_" + style, "exec"), mod.__dict__)
    if style == "Slash":
        mpn.slash_bg(mod)
    return mod


def corner_frames(mod, n=30):
    """Animated lower-third corner badge: frame, gem and name with a shine sweeping across."""
    W, H = 440, 200
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def fn(d, S):
        d.rounded_rectangle((6 * S, 6 * S, (W - 6) * S, (H - 6) * S), radius=34 * S, fill=tuple(mod.P_MID) + (235,), outline=tuple(mod.PINK) + (255,), width=int(5 * S))
        d.rounded_rectangle((20 * S, 20 * S, (W - 20) * S, (H - 20) * S), radius=22 * S, outline=tuple(mod.VIOLET) + (255,), width=int(9 * S))
        mod.chain(d, (60, 36), (W - 60, 36), link=16, width=3, S=S)
        mod.chain(d, (60, H - 36), (W - 60, H - 36), link=16, width=3, S=S)
    base = Image.alpha_composite(base, mod.on_layer((W, H), fn))
    f = mod.font("OLDENGL.TTF", 54)
    m = mod.text_mask((W, H), "Petals Of Iron", f, (W / 2 + 34, H / 2 + 20))
    base = mod.shadow(base, m, (0, 3), 4, mod.INK, 0.7)
    base = mod.fill_mask(base, m, (252, 250, 255), (222, 214, 240))
    text_alpha = m.point(lambda v: 255 if v > 20 else 0)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)
        fr = base.copy()

        def gem_fn(d, S):
            mod.gem(d, 62, H / 2 + 2, 24 + 2 * pulse, S=S)
        fr = Image.alpha_composite(fr, mod.on_layer((W, H), gem_fn))
        x = -80 + (W + 160) * t
        shine = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shine).polygon([(x, 0), (x + 40, 0), (x - 30, H), (x - 70, H)], fill=(255, 255, 255, 120))
        shine = shine.filter(ImageFilter.GaussianBlur(6))
        a = ImageChops.multiply(shine.split()[3], text_alpha)
        white = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        white.putalpha(a)
        frames.append(Image.alpha_composite(fr, white))
    return frames


def write_gif(frames, path, dur=50):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=dur, disposal=2, loop=0, optimize=False)
    print("Saved", path)


def build(style):
    mod = themed(style)
    skip = EXTRA[style]["skip"]
    out = mod.OUT
    save = mod.save
    for t in mod.PANELS:
        save(mod.panel(t), out / "Panels" / (t.lower().replace(" ", "_") + ".png"))
    screens = [("starting_soon", "Starting soon", "The stream begins shortly"), ("be_right_back", "Be right back", "I will be back in a moment"),
               ("offline", "Offline", "Thank you for watching, see you next time")]
    for name, title, sub in screens:
        if name in skip:
            continue
        save(mod.screen(title, sub), out / "Screens" / (name + ".png"))
    if "logo" not in skip:
        save(mod.logo(), out / "Logo" / "logo.png")
    if "banner" not in skip:
        save(mod.banner(), out / "Banner" / "banner.png")
    save(mod.overlay_frame(), out / "Overlay" / "overlay_frame.png", rgba=True)
    write_gif(mod.alert_frames("Thanks for the follow!"), out / "Alert" / "alert.gif")
    write_gif(corner_frames(mod), out / "Corner" / "corner.gif")
    for t in mod.BADGES:
        save(mod.badge(t), out / "Badges" / (t[0] + "_432.png"), rgba=True)
    for k in mod.POINTS:
        save(mod.point_icon(k), out / "Points" / ("points_" + k + "_432.png"), rgba=True)
    for t in (2, 3):
        save(mod.flair(t), out / "Flair" / ("tier%d_flair_432.png" % t), rgba=True)
    for e in mod.EMOTES:
        for s in (448, 112, 56, 28):
            save(mod.emote(e, s), out / "Emotes" / ("%s_%d.png" % (e, s)), rgba=True)
    anim = types.ModuleType("make_purple_anim")
    anim.__file__ = str(HERE / "make_purple_anim.py")
    exec(compile((HERE / "make_purple_anim.py").read_text(encoding="utf-8"), "anim_" + style, "exec"), anim.__dict__)
    anim.main()


def purple_corner():
    mod = types.ModuleType("make_purple")
    mod.__file__ = str(HERE / "make_purple.py")
    sys.modules["make_purple"] = mod
    exec(compile((HERE / "make_purple.py").read_text(encoding="utf-8"), "theme_purple", "exec"), mod.__dict__)
    write_gif(corner_frames(mod), mod.OUT / "Corner" / "corner.gif")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["corners"]:
        purple_corner()
    else:
        for s in (args or list(EXTRA)):
            build(s)
    print("done")

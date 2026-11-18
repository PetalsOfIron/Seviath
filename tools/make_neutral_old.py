#!/usr/bin/env python3
"""Name-free stream graphics for the older sets (no brand, no tagline, no lettering on logos, X-ready).
Each generator is loaded from its source with the lettering swapped out, then its logo/banner functions are called.
    python make_neutral_old.py Purple Floral Slash Hood Helmet Snake ...
Output: Documents/twitch/Neutral/<Set>/{Logo,Banner,Screens,Overlay,Alerts}"""
import math
import re
import shutil
import sys
import types
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PORT = HERE.parent / "images" / "twitch"
NEUTRAL = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral")
NAME, TAG = "Live Stream", "Gaming  -  Art  -  Chat"


def patched(fname, edits, regex_edits=()):
    src = (HERE / fname).read_text(encoding="utf-8")
    for old, new in edits:
        assert old in src, (fname, old)
        src = src.replace(old, new)
    for pat, new in regex_edits:
        src = re.sub(pat, new, src, flags=re.M)
    mod = types.ModuleType("n_" + fname)
    mod.__file__ = str(HERE / fname)
    sys.argv = sys.argv[:1]
    exec(compile(src, fname, "exec"), mod.__dict__)
    return mod


def trim_square(im, pad=1.10, size=2000, crop_to=None):
    im = im.convert("RGBA")
    if crop_to:
        im = im.crop(crop_to)
    box = im.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()
    im = im.crop(box)
    w, h = im.size
    side = int(max(w, h) * pad)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(im, ((side - w) // 2, (side - h) // 2))
    return sq.resize((size, size), Image.LANCZOS), im


def emblem_only(path):
    """Keep the emblem of a logo that has a wordmark under it: the first block of non-empty rows."""
    im = Image.open(path).convert("RGBA")
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    w, h = im.size
    rows = [a.crop((0, y, w, y + 1)).getbbox() is not None for y in range(h)]
    runs, start = [], None
    for y, on in enumerate(rows + [False]):
        if on and start is None:
            start = y
        if not on and start is not None:
            runs.append((start, y))
            start = None
    # merge runs separated by small gaps (emblem details), keep the biggest block
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < 40:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    big = max(merged, key=lambda r: r[1] - r[0])
    return im.crop((0, big[0], w, big[1]))


def strip_wordmark(path, cut=None, circle_above=None):
    """Remove the lettering under a badge: cut everything below row `cut`, or keep only a circle fitted to the badge found above row `circle_above`."""
    from PIL import ImageDraw
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    if cut:
        im.paste((0, 0, 0, 0), (0, cut, w, h))
        return im
    x0, y0, x1, y1 = a.crop((0, 0, w, circle_above)).getbbox()
    R = (x1 - x0) / 2
    cx, cy = (x0 + x1) / 2, y0 + R
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((cx - R + 38, cy - R + 38, cx + R - 38, cy + R - 38), fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    return out


def finish(out, kit, logo_img=None):
    """Center the logo, add X profile pictures and the X header."""
    import make_gumroad as mg
    main = mg.COLORS[kit]
    bg = tuple(int(c * 0.22) for c in main) + (255,)
    (out / "Logo").mkdir(parents=True, exist_ok=True)
    if logo_img is not None:
        sq, im = trim_square(logo_img)
        sq.save(out / "Logo" / "logo.png", optimize=True)
        w, h = im.size
        k = 372 / math.hypot(w, h)
        small = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
        card = Image.new("RGBA", (400, 400), bg)
        card.alpha_composite(small, ((400 - small.width) // 2, (400 - small.height) // 2))
        card.convert("RGB").save(out / "Logo" / "x_profile_logo_400.png", optimize=True)
        # round avatar: the logo inside a circle, on the set colour
        av = Image.new("RGBA", (1000, 1000), bg)
        s2, _ = trim_square(logo_img, pad=1.28, size=1000)
        av.alpha_composite(s2)
        av.convert("RGB").resize((400, 400), Image.LANCZOS).save(out / "Logo" / "x_profile_400.png", optimize=True)
    ban = out / "Banner"
    for p in ban.glob("banner.png"):
        im = Image.open(p).convert("RGB").resize((1200, 400 if False else 480), Image.LANCZOS)
        im.save(ban / "profile_banner_1200x480.png", optimize=True)
        big = Image.open(p).convert("RGB")
        k = 1500 / big.width
        big = big.resize((1500, int(big.height * k)), Image.LANCZOS)
        top = max(0, (big.height - 500) // 2)
        big.crop((0, top, 1500, top + 500)).save(ban / "x_header_1500x500.png", optimize=True)
        p.unlink()


def copy_common(kit, out, screens=None, overlay=None, alerts=None):
    """Copy the generic (name-free) screens, overlay and alert files of the set."""
    d = PORT / kit
    names = screens or ["starting_soon.png", "be_right_back.png", "offline.png"]
    (out / "Screens").mkdir(parents=True, exist_ok=True)
    for n in names:
        src = n if isinstance(n, Path) else d / "Screens" / n
        if src.exists():
            shutil.copy(src, out / "Screens" / src.name)
    (out / "Overlay").mkdir(parents=True, exist_ok=True)
    ov = overlay or d / "Overlay" / "overlay_frame.png"
    if ov.exists():
        shutil.copy(ov, out / "Overlay" / "overlay_frame.png")
    alerts_for(kit, out)


# per set: title font (for the alert text), text colour, chime root note (Hz) and notes
STYLE = {"Purple": ("OLDENGL.TTF", "Old English Text MT", "#F6F2FF", 392), "Floral": ("OLDENGL.TTF", "Old English Text MT", "#FCFAFF", 523),
         "Slash": ("impact.ttf", "Impact", "#FFFFFF", 349), "Hood": ("OLDENGL.TTF", "Old English Text MT", "#780406", 440),
         "Helmet": ("georgiab.ttf", "Georgia Bold", "#FFF0C8", 330), "Snake": ("OLDENGL.TTF", "Old English Text MT", "#0A2C64", 466),
         "Tessel": ("georgia.ttf", "Georgia", "#FAFCFA", 587), "Perfum": ("georgia.ttf", "Georgia", "#60223C", 494)}


def chime(path, root, minor=False):
    """A short bell-like chime (original, synthesised): three rising notes with soft decay."""
    import wave
    import numpy as np
    sr = 44100
    steps = [1.0, 1.25 if not minor else 1.2, 1.5]
    out = np.zeros(int(sr * 1.9))
    for i, k in enumerate(steps):
        t = np.arange(int(sr * 1.4)) / sr
        f = root * k
        tone = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) + 0.25 * np.sin(2 * np.pi * 3.01 * f * t)) * np.exp(-3.2 * t)
        tone *= np.minimum(1, t * 200)
        st = int(sr * 0.16 * i)
        out[st:st + len(tone)] += tone
    out = out / max(1e-6, np.abs(out).max()) * 0.8
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((out * 32767).astype("<i2").tobytes())


def alerts_for(kit, out):
    """ONE animated alert with an empty text area (the alert tool writes the text for follower, subscriber, raid, donation and bits),
    a chime for the sound slot and a short setup note."""
    ad = out / "Alerts"
    if ad.exists():
        shutil.rmtree(ad)
    ad.mkdir(parents=True, exist_ok=True)
    if kit == "Purple":
        mp = patched("make_purple.py", [])
        make = lambda t: mp.alert_frames(t)
    elif kit == "Hood":
        mh = patched("make_hood.py", [('banner_panel((800, 360), "Thanks for the follow!", 96)', "banner_panel((800, 360), ALERT_TEXT, 96)")])

        def make(t):
            mh.ALERT_TEXT = t
            return mh.alert_frames()
    elif kit == "Snake":
        import make_snake
        th = make_snake.load_theme_module()
        make = lambda t: th.alert_frames(t)
    else:
        import make_sets as ms
        C = dict(ms.SETS[kit])
        ms.apply_set(C)
        make = lambda t: ms.animated(C, (800, 360), t, 100, 1.0)
    frames = make(" ")
    if kit == "Hood" or len({f.tobytes() for f in frames}) < 3:      # blank text area left nothing to animate: add a soft moving shine over the panel
        from PIL import ImageChops, ImageDraw, ImageFilter
        base = frames[0].convert("RGBA")
        shc = (190, 20, 30) if kit == "Hood" else (255, 255, 255)
        W_, H_ = base.size
        a = base.split()[3]
        frames = []
        for i in range(26):
            x = -120 + (W_ + 240) * i / 25
            sh = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(x, 0), (x + 70, 0), (x - 50, H_), (x - 120, H_)], fill=(shc + (120,)))
            sh = sh.filter(ImageFilter.GaussianBlur(8))
            wh = Image.new("RGBA", (W_, H_), shc + (0,))
            wh.putalpha(ImageChops.multiply(sh.split()[3], a))
            frames.append(Image.alpha_composite(base, wh))
    frames[0].save(ad / "alert.gif", save_all=True, append_images=frames[1:], duration=50, disposal=2, loop=0, optimize=False)
    _, fname, col, root = STYLE[kit]
    chime(ad / "alert_sound.wav", root, minor=kit in ("Hood", "Slash", "Snake"))
    NL = chr(10)
    text = NL.join([
        "ALERT SETUP", "",
        "alert.gif is one animated alert image with an empty text area. In your alert tool (Streamlabs, StreamElements or similar) use it as the image for each event you want (new follower, subscriber, raid, donation, bits) - you only need this one image.",
        "Add the text yourself in the alert tool's text layer, centred in the empty area. Most tools write the event text for you with variables such as {name}, {amount} and {message} (check the names in your tool).", "",
        f"Suggested text font: {fname} (install it on the streaming PC if it is not there)",
        f"Suggested text colour: {col}",
        "Suggested alert size: 800 x 360 px", "",
        "alert_sound.wav is a short chime you can put into the sound slot of the same alert.", ""])
    (ad / "ALERT_SETUP.txt").write_text(text, encoding="utf-8")


def kit_dir(kit):
    out = NEUTRAL / kit
    for sub in ("Logo", "Banner", "Screens", "Overlay", "Alerts"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    out.mkdir(parents=True, exist_ok=True)
    (out / "Banner").mkdir(exist_ok=True)
    return out


# ------------------------------------------------------------------ sets
LOGO_LINES = [(r"^\s*(d\.line\(\[\(\d+, 1872\).*|diamond\(d, 1000, 1872.*)$", "    pass")]


def purple():
    out = kit_dir("Purple")
    b = patched("make_purple.py", [('"Petals Of Iron", (W // 2, 520), 300', f'"{NAME}", (W // 2, 520), 300'),
                                   ('"Gamer  -  Streamer  -  Artist"', f'"{TAG}"')])
    b.banner().convert("RGB").save(out / "Banner" / "banner.png", optimize=True)
    lg = patched("make_purple.py", [('"P", (cx, cy + 270), 720', '" ", (cx, cy + 270), 720'), ('"Petals Of Iron", (cx, 1790), 215', '" ", (cx, 1790), 215')], LOGO_LINES)
    finish(out, "Purple", lg.logo())
    copy_common("Purple", out, ["starting_soon.png", "be_right_back.png", "offline.png"], PORT / "Purple" / "Overlay" / "purple_overlay_frame.png")


def floral():
    out = kit_dir("Floral")
    bm = patched("make_floral.py", [('fT = font("OLDENGL.TTF", 330)', 'fT = font("FREESCPT.TTF", 400)'),
                                    ('text_mask((W, H), "Petals Of Iron", fT, (cx, 520))', 'text_mask((W, H), "Welcome", fT, (cx, 520))'),
                                    ('"Gamer  -  Streamer  -  Artist"', '"Chat  -  Create  -  Play"')])
    bm.floral_banner().convert("RGB").save(out / "Banner" / "banner.png", optimize=True)
    lg = patched("make_floral.py", [('text_mask(canvas.size, "P", fP, (cx, cy + 290))', 'text_mask(canvas.size, " ", fP, (cx, cy + 290))'),
                                    ('text_mask(canvas.size, "Petals Of Iron", fW, (cx, 1790))', 'text_mask(canvas.size, " ", fW, (cx, 1790))')], LOGO_LINES)
    finish(out, "Floral", lg.floral_logo())
    copy_common("Floral", out)


def slash():
    out = kit_dir("Slash")
    b = patched("make_unique.py", [('"PETALS OF IRON"', '"GAME ON"'), ('"GAMER  -  STREAMER  -  ARTIST"', '"STREAMING  -  LIVE  -  NOW"')])
    b.slash_banner().convert("RGB").save(out / "Banner" / "banner.png", optimize=True)
    lg = patched("make_unique.py", [('"PETALS OF IRON", font("impact.ttf", 150)', '" ", font("impact.ttf", 150)'), ('"P", font("impact.ttf", size)', '" ", font("impact.ttf", size)')])
    finish(out, "Slash", lg.slash_logo())
    copy_common("Slash", out)


def hood():
    out = kit_dir("Hood")
    b = patched("make_hood.py", [('font("OLDENGL.TTF", size)', 'font("ROCKB.TTF", size)'), ('"Petals Of Iron"', '"Stream Time"'), ('"Gamer  -  Streamer  -  Artist"', '"Gaming  -  Art  -  Chat"'),
                                 ('fit_size("Stream Time", "OLDENGL.TTF", 1700, 300)', 'fit_size("Stream Time", "ROCKB.TTF", 1350, 300)'),
                                 ('fit_size(title, "OLDENGL.TTF", 760, 200)', 'fit_size(title, "OLDENGL.TTF", 600, 200)'), ('cx = 1400', 'cx = 1500'),
                                 ('fit_size(ln, "georgiai.ttf", 700, 52)', 'fit_size(ln, "georgiai.ttf", 560, 52)'), ('cx = 1950', 'cx = 2000')])
    b.banner().convert("RGB").save(out / "Banner" / "banner.png", optimize=True)
    finish(out, "Hood", b.logo_round())
    copy_common("Hood", out, [])
    (out / "Screens").mkdir(parents=True, exist_ok=True)
    for fn, t_, s_ in (("starting_soon.png", "Starting soon", "The stream begins shortly"), ("be_right_back.png", "Be right back", "I will be back in a moment"), ("offline.png", "Offline", "Thank you for watching, see you next time")):
        b.screen(t_, s_).convert("RGB").save(out / "Screens" / fn, optimize=True)


def helmet():
    out = kit_dir("Helmet")
    finish(out, "Helmet", strip_wordmark(PORT / "Helmet" / "Logo" / "logo.png", circle_above=1740))
    st = patched("make_starting_soon.py", [('"PETALS OF IRON"', '" "'),
                                           ('OUT = ROOT / "images" / "twitch" / "Starting" / "petals_starting_soon.png"', 'OUT = Path(r"%s")' % (out / "Screens" / "starting_soon.png"))])
    st.main()
    copy_common("Helmet", out, ["be_right_back.png", "offline.png"])


def snake():
    out = kit_dir("Snake")
    finish(out, "Snake", strip_wordmark(PORT / "Snake" / "Logo" / "logo.png", cut=1595))
    off = (HERE / "make_offline.py").read_text(encoding="utf-8")
    jobs = [("starting_soon.png", "Starting soon", 150, "The stream begins shortly", "Grab a drink and get comfy", "Back in a few minutes"),
            ("be_right_back.png", "Be right back", 150, "I will be back in a moment", "Stretch your legs", "Don't go far"),
            ("offline.png", "Offline", 300, "The stream has ended", "Thank you for stopping by", "See you next stream")]
    (out / "Screens").mkdir(parents=True, exist_ok=True)
    for fname, title, size, l1, l2, l3 in jobs:
        t = off
        t = t.replace('OUT = ROOT / "images" / "twitch" / "Offline" / "petals_offline_screen.png"', 'OUT = Path(r"%s")' % (out / "Screens" / fname))
        t = t.replace('"Offline"', f'"{title}"')
        t = t.replace('"OLDENGL.TTF"), 300)', f'"OLDENGL.TTF"), {size})')
        t = t.replace('"The stream has ended"', f'"{l1}"').replace('"Thank you for stopping by"', f'"{l2}"').replace('"See you next stream"', f'"{l3}"')
        t = t.replace("cx = 1650", "cx = 1560").replace("cx = 1585", "cx = 1560")
        t = t.replace('"Petals Of Iron"', '"Live Stream"').replace('"ART @SMADNA"', '"GAMING  -  ART  -  CHAT"')
        mod = types.ModuleType("mo_" + fname)
        mod.__file__ = str(HERE / "make_offline.py")
        sys.argv = sys.argv[:1]
        exec(compile(t, "snake_screen", "exec"), mod.__dict__)
        mod.main()
    copy_common("Snake", out, [])


def tessel():
    out = kit_dir("Tessel")
    copy_common("Tessel", out)


def perfum():
    out = kit_dir("Perfum")
    copy_common("Perfum", out)


SETS = {"Purple": purple, "Floral": floral, "Slash": slash, "Hood": hood, "Helmet": helmet, "Snake": snake, "Tessel": tessel, "Perfum": perfum}

if __name__ == "__main__":
    for n in (sys.argv[1:] or list(SETS)):
        SETS[n]()
        print("neutral done", n, flush=True)

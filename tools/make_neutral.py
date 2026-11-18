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

def blank_alert(mod):
    """alert panels are made with an empty text area; the alert tool writes the event text itself"""
    name = "alert2" if hasattr(mod, "alert2") else "alert"
    orig = getattr(mod, name)
    setattr(mod, name, lambda art, head, sub, *a, **k: orig(art, " ", " ", *a, **k))


def one_alert(out, kit):
    """keep ONE alert: soft moving shine over the empty panel as an 800 px animated GIF, a chime and a setup note"""
    import shutil
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    import make_neutral_old as mo
    ad = out / "Alerts"
    base = Image.open(ad / "follow.png").convert("RGBA")
    base.thumbnail((800, 800), Image.LANCZOS)
    W_, H_ = base.size
    a = base.split()[3]
    frames = []
    for i in range(26):
        x = -120 + (W_ + 240) * i / 25
        sh = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
        ImageDraw.Draw(sh).polygon([(x, 0), (x + 70, 0), (x - 50, H_), (x - 120, H_)], fill=(255, 255, 255, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        wh = Image.new("RGBA", (W_, H_), (255, 255, 255, 0))
        wh.putalpha(ImageChops.multiply(sh.split()[3], a))
        frames.append(Image.alpha_composite(base, wh))
    shutil.rmtree(ad)
    ad.mkdir()
    frames[0].save(ad / "alert.gif", save_all=True, append_images=frames[1:], duration=50, disposal=2, loop=0, optimize=False)
    fname, col, root = {"Nightwing": ("Georgia Bold", "#D6DAEC", 440), "Starcaller": ("Bahnschrift", "#E2EAF8", 523), "Crimson": ("Times New Roman Bold", "#F0E6D2", 392)}[kit]
    mo.chime(ad / "alert_sound.wav", root, minor=kit == "Crimson")
    NL = chr(10)
    (ad / "ALERT_SETUP.txt").write_text(NL.join([
        "ALERT SETUP", "",
        "alert.gif is one animated alert image with an empty text area. In your alert tool (Streamlabs, StreamElements or similar) use it as the image for each event you want (new follower, subscriber, raid, donation, bits) - you only need this one image.",
        "Add the text yourself in the alert tool's text layer, centred in the empty area. Most tools write the event text for you with variables such as {name}, {amount} and {message} (check the names in your tool).", "",
        "Suggested text font: %s (install it on the streaming PC if it is not there)" % fname,
        "Suggested text colour: %s" % col,
        "Suggested alert size: %d x %d px" % (W_, H_), "",
        "alert_sound.wav is a short chime you can put into the sound slot of the same alert.", ""]), encoding="utf-8")


if kit == "Nightwing":
    import make_nightwing2 as n2
    nw.OUT = OUT
    n2.OUT = OUT
    blank_alert(nw)
    nw.main()
    n2.main()
elif kit == "Starcaller":
    import make_starcaller as sc
    import make_starcaller2 as s2
    import make_starcaller3 as s3
    nw.OUT = sc.OUT = s2.OUT = OUT
    blank_alert(sc)
    blank_alert(s2)
    if hasattr(s3, "OUT"):
        s3.OUT = OUT
    sc.main()
    s2.main()
    s3.main()
elif kit == "Crimson":
    import make_crimson as cr
    nw.OUT = cr.OUT = OUT
    blank_alert(cr)
    cr.main()
finish(OUT, kit)
one_alert(OUT, kit)
print("neutral done", kit)

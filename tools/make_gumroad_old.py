#!/usr/bin/env python3
"""Professional preview covers (3 per product, 1280x720) for the older Gumroad products, built from their own artwork.
Input: C:/Users/SaphiresSilver/Documents/twitch/GumroadOld/*.bin (downloaded current covers)
Output: C:/Users/SaphiresSilver/Documents/twitch/GumroadOld/new/<id>/cover_1..3.png + thumb.png"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_banner_gig as g
import make_set_showcases as ss
from art import *  # noqa: F401,F403

SRC = Path("C:/Users/SaphiresSilver/Documents/twitch/GumroadOld")
OUT = SRC / "new"
W, H = 1280, 720
HEAD = "bahnschrift.ttf"

P = {  # id: (file, title, subtitle, bullets, kind, second image for model packs)
    "hbmoqy": ("brb_b", "FLORAL BRB SCREEN", "TWITCH STREAM SCREEN", ["Ornate gold frame with purple flowers", "Gothic \"I will be right back\" lettering", "High-resolution PNG, ready to upload"], "wide"),
    "uvcaj": ("start_b", "STARTING SOON SCREEN", "TWITCH STREAM SCREEN", ["Layered purple and pink diamond design", "Gothic \"Starting soon\" lettering", "High-resolution PNG, ready to upload"], "wide"),
    "mtambf": ("off_b", "I AM OFFLINE SCREEN", "TWITCH STREAM SCREEN", ["Bold red and white dynamic stripes", "Orange \"I am offline\" lettering", "High-resolution PNG, ready to upload"], "wide"),
    "nfhzh": ("hood_b", "HOODED CHARACTER LOGO", "GAMING AVATAR BADGE", ["Red cloak warrior with controller", "Works as a profile picture or channel logo", "High-resolution PNG, ready to upload"], "square"),
    "aomldx": ("knight_b", "KNIGHT HELMET BANNER", "ESPORTS HEADER BANNER", ["Gold helmet with crossed swords", "Medieval gamer and streamer header", "High-resolution PNG, ready to upload"], "banner"),
    "ompwd": ("foot_b", "FOOTBALL BANNER", "SOCCER HEADER DESIGN", ["Dark blue sports look with cyan stripes", "Player silhouette with ball", "High-resolution PNG, ready to upload"], "banner"),
    "skmzia": ("eye_b", "VROID EYE IRIS TEXTURE", "VROID STUDIO ITEM", ["Soft violet iris with highlight", "Import straight into VRoid Studio", "Premade texture, ready to use"], "tall"),
    "emhaxp": ("hair2", "TWIN-TAIL VTUBER HAIR", "VROID STUDIO HAIR", ["Vibrant purple twin-tails", "Import straight into VRoid Studio", "Premade hair, ready to use"], "tall"),
    "kjnoyw": ("plat2", "PLATINUM HAIR & HORNS", "VROID CUSTOM ITEM", ["Platinum white hair with brown horns", "Import straight into VRoid Studio", "Premade item, ready to use"], "tall"),
    "horns": ("horns", "DEMON HORNS", "VROID CUSTOM ITEM", ["Dark curved demon horns accessory", "Import straight into VRoid Studio", "Premade item, ready to use"], "tall"),
    "wbgryj": ("sem4", "SEM VROID MODEL", "PREMADE CHARACTER", ["Premade VRoid character, non-exclusive", "Purple twin-tails with horns", "Ready for your VTuber setup"], "model", "sem2"),
    "odehi": ("emi2", "EMI VROID MODEL", "PREMADE CHARACTER", ["Premade VRoid character, non-exclusive", "Pink hair with golden horns", "Ready for your VTuber setup"], "model", "emi4"),
}


def art(name):
    im = Image.open(SRC / (name + ".bin")).convert("RGBA")
    return im


def bg(main, seed=1):
    dark = tuple(int(c * 0.14) for c in main)
    mid = tuple(int(c * 0.40) for c in main)
    img = radial((W, H), mid, dark, 0.3, 0.3, 1.15).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(-H, W, 60):
        d.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 5), width=2)
    return grain(vignette(img, 0.4, (2, 2, 8)), 4)


def card(im, w, h, radius=18, pad=0, back=(10, 12, 24)):
    fit = ss.fit(im, w - 2 * pad, h - 2 * pad)
    out = Image.new("RGBA", (fit.width + 2 * pad, fit.height + 2 * pad), back + (255,))
    out.alpha_composite(fit, (pad, pad))
    return ss.rounded(out, radius)


def put(canvas, im, xy, blur=24, op=0.6, glow_col=None):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    lay.alpha_composite(im, (int(xy[0]), int(xy[1])))
    if glow_col:
        canvas = glow(canvas, (xy[0] - 40, xy[1] - 40, xy[0] + im.width + 40, xy[1] + im.height + 40), glow_col, blur=80, alpha=90)
    canvas = shadow(canvas, lay.split()[3], (0, 18), blur, (0, 0, 0), op)
    canvas = Image.alpha_composite(canvas, lay)
    ImageDraw.Draw(canvas).rounded_rectangle((xy[0], xy[1], xy[0] + im.width - 1, xy[1] + im.height - 1), radius=18, outline=(255, 255, 255, 50), width=2)
    return canvas


def txt(img, s, xy, size, c1=g.SILVER, c2=(170, 180, 205), anchor="left", track=8):
    return g.txt(img, s, xy, size, c1, c2, anchor, track)


def chip(img, s, xy, col):
    return g.chip(img, s, xy, 15, col)


def accent(main):
    return tuple(min(255, int(c * 0.45 + 150)) for c in main)


def hero(cfg, main, acc):
    name, title, sub, bullets, kind = cfg[:5]
    a = art(name)
    img = bg(main, 1)
    if kind == "wide":
        c = card(a, 1000, 562, 16)
        img = put(img, c, ((W - c.width) // 2, 40 + 0), 26, 0.6, acc)
        img = txt(img, title, (W // 2, 665), 40, g.SILVER, (170, 180, 205), "center", 10)
        img = txt(img, sub, (W // 2, 700), 17, acc, acc, "center", 8)
        return img
    if kind == "banner":
        c = card(a, 1120, 373, 16)
        img = put(img, c, ((W - c.width) // 2, 70), 26, 0.6, acc)
        img = txt(img, title, (W // 2, 560), 46, g.SILVER, (170, 180, 205), "center", 12)
        img = txt(img, sub, (W // 2, 604), 20, acc, acc, "center", 10)
        img = txt(img, "READY TO UPLOAD  ·  PNG", (W // 2, 664), 16, (200, 205, 220), (200, 205, 220), "center", 8)
        return img
    if kind == "square":
        c = card(a, 600, 600, 20)
        img = put(img, c, (90, 60), 26, 0.6, acc)
        img = txt(img, title, (740, 270), 30, g.SILVER, (170, 180, 205), "left", 3)
        img = txt(img, sub, (742, 320), 20, acc, acc, "left", 9)
        ImageDraw.Draw(img).line([(742, 345), (1100, 345)], fill=acc + (255,), width=3)
        img = txt(img, "HIGH-RESOLUTION PNG", (742, 400), 18, (210, 214, 228), (210, 214, 228), "left", 6)
        img = txt(img, "READY TO UPLOAD", (742, 436), 18, (210, 214, 228), (210, 214, 228), "left", 6)
        return img
    # tall and model: art left card, title right
    ar = a.width / a.height
    h = 600 if ar < 1.0 else 500
    w = int(h * ar) if ar < 1.3 else 720
    c = card(a, w, h if ar < 1.3 else int(720 / ar), 20)
    img = put(img, c, (80, (H - c.height) // 2), 26, 0.6, acc)
    x0 = 80 + c.width + 60
    img = txt(img, title, (x0, 290), 38, g.SILVER, (170, 180, 205), "left", 5)
    img = txt(img, sub, (x0 + 2, 340), 19, acc, acc, "left", 8)
    ImageDraw.Draw(img).line([(x0 + 2, 364), (x0 + 330, 364)], fill=acc + (255,), width=3)
    img = txt(img, "PREMADE  ·  DIGITAL DOWNLOAD", (x0 + 2, 410), 16, (210, 214, 228), (210, 214, 228), "left", 6)
    return img


def showcase(cfg, main, acc):
    """For non-screen items: the artwork large on a soft scene, with the second image beside it for model packs."""
    name, title, sub, bullets, kind = cfg[:5]
    a = art(name)
    img = bg(main, 2)
    if len(cfg) > 5:
        b = art(cfg[5])
        c1 = card(b, 620, 440, 18)
        img = put(img, c1, (60, 140), 24, 0.6, acc)
        c2 = card(a, 520, 520, 18)
        img = put(img, c2, (W - 60 - c2.width, 100), 24, 0.6, acc)
    else:
        c = card(a, 640 if kind in ("tall", "square") else 1000, 620 if kind in ("tall", "square") else 400, 20)
        img = put(img, c, ((W - c.width) // 2, 50), 26, 0.6, acc)
    img = txt(img, title, (W // 2, 690), 22, (210, 214, 228), (210, 214, 228), "center", 10)
    return img


def monitor(cfg, main, acc):
    name, title, sub, bullets, kind = cfg[:5]
    if kind != "wide":
        return showcase(cfg, main, acc)
    a = art(name)
    img = bg(main, 2)
    d = ImageDraw.Draw(img)
    mw, mh = 980, 560
    mx, my = (W - mw) // 2, 50
    scr_ar = a.width / a.height
    inner = ss.fit(a, mw - 40, mh - 40) if kind in ("wide", "banner") else None
    body = Image.new("RGBA", (mw, mh), (20, 22, 34, 255))
    body = ss.rounded(body, 22)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lay.alpha_composite(body, (mx, my))
    img = shadow(img, lay.split()[3], (0, 26), 34, (0, 0, 0), 0.65)
    img = Image.alpha_composite(img, lay)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((mx, my, mx + mw - 1, my + mh - 1), radius=22, outline=(70, 74, 96, 255), width=4)
    sx, sy, sw, sh = mx + 20, my + 20, mw - 40, mh - 40
    screen = Image.new("RGBA", (sw, sh), (6, 8, 16, 255))
    if kind in ("wide",):
        f = ss.fit(a, sw, sh)
        screen.alpha_composite(f, ((sw - f.width) // 2, (sh - f.height) // 2))
    else:
        # show the art as it would sit on a stream: dark scene with the art as a banner / avatar
        scene = radial((sw, sh), tuple(int(c * 0.5) for c in main), (8, 10, 20), 0.5, 0.4, 1.0).convert("RGBA")
        f = ss.fit(a, int(sw * 0.8), int(sh * 0.7))
        scene.alpha_composite(f, ((sw - f.width) // 2, (sh - f.height) // 2))
        screen = scene
    img.alpha_composite(screen, (sx, sy))
    # stand
    d = ImageDraw.Draw(img)
    d.polygon([(W // 2 - 60, my + mh), (W // 2 + 60, my + mh), (W // 2 + 90, my + mh + 50), (W // 2 - 90, my + mh + 50)], fill=(36, 38, 54, 255))
    d.rounded_rectangle((W // 2 - 150, my + mh + 46, W // 2 + 150, my + mh + 60), radius=7, fill=(54, 56, 76, 255))
    img = txt(img, title, (W // 2, 706), 18, (210, 214, 228), (210, 214, 228), "center", 10)
    return img


def details(cfg, main, acc):
    name, title, sub, bullets, kind = cfg[:5]
    a = art(name)
    img = bg(main, 3)
    img = txt(img, title, (80, 120), 44, g.SILVER, (170, 180, 205), "left", 6)
    img = txt(img, sub, (82, 168), 19, acc, acc, "left", 9)
    ImageDraw.Draw(img).line([(82, 192), (480, 192)], fill=acc + (255,), width=3)
    y = 260
    for b_ in bullets:
        ImageDraw.Draw(img).ellipse((84, y - 13, 100, y + 3), fill=acc + (255,))
        img = txt(img, b_, (118, y), 24, (232, 236, 246), (232, 236, 246), "left", 2)
        y += 62
    img = chip(img, "INSTANT DOWNLOAD", (82, 520), acc)
    if kind in ("wide", "banner", "square"):
        img = chip(img, "PERSONAL & COMMERCIAL USE", (82, 566), acc)
    c = card(a, 560, 560, 18, 0)
    img = put(img, c, (W - 80 - c.width, (H - c.height) // 2), 24, 0.6, acc)
    return img


def thumb(cfg, main, acc):
    name = cfg[0]
    a = art(name)
    S = 1000
    img = bg(main, 4).resize((S, S), Image.LANCZOS)
    c = card(a, 900, 900 if cfg[4] in ("square", "tall", "model") else 560, 22)
    img = put(img, c, ((S - c.width) // 2, (S - c.height) // 2 - (60 if cfg[4] in ("wide", "banner") else 0)), 28, 0.6, acc)
    if cfg[4] in ("wide", "banner"):
        img = txt(img, cfg[1], (S // 2, 780), 40, g.SILVER, (170, 180, 205), "center", 8)
    return img


def main():
    ids = [a for a in sys.argv[1:] if a in P] or list(P)
    for pid in ids:
        cfg = P[pid]
        a = art(cfg[0])
        main = ss.palette(SRC / (cfg[0] + ".bin"))[0]
        acc = accent(main)
        out = OUT / pid
        out.mkdir(parents=True, exist_ok=True)
        hero(cfg, main, acc).convert("RGB").save(out / "cover_1.png", optimize=True)
        monitor(cfg, main, acc).convert("RGB").save(out / "cover_2.png", optimize=True)
        details(cfg, main, acc).convert("RGB").save(out / "cover_3.png", optimize=True)
        thumb(cfg, main, acc).convert("RGB").save(out / "thumb.png", optimize=True)
        print("done", pid, flush=True)


if __name__ == "__main__":
    main()

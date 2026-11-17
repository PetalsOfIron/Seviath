#!/usr/bin/env python3
"""
Complete brand kits for the two fictional brands Tessel (football boots) and Perfum (perfume), built from your
original product art (images in Downloads/art/assets) with the same palettes as their logos and banners.

    python tools/make_kit.py            # both
    python tools/make_kit.py tessel     # one
"""
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from art import *  # noqa: F401,F403
import make_brands as mb
from make_football import crop_pad, fit, lockup, put, solid, stencil

SITE_TPL, MAIL_TPL, PHONE = "{n}.example", "hello@{n}.example", "+00 000 000 000"


# ------------------------------------------------------------------------------------------- brand themes

def tessel_emblem():
    S = 2000
    cx, cy, D = 1000, 1000, 1500
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    plate = radial((S, S), (22, 96, 62), mb.FOREST, cx=0.5, cy=0.5, spread=0.5).convert("RGBA")
    plate = glow(plate, (cx - 560, cy - 460, cx + 560, cy + 460), mb.PITCH, blur=120, alpha=120)
    boot = mb.load("Footballboot.png", size=(1400, 1400))
    plate = mb.place(plate, boot, (cx - 700 - 20, cy - 700 + 14), shadow_opacity=0.5, shadow_off=(18, 26), blur=24)
    pm = mb.circle_mask((S, S), (cx - D / 2, cy - D / 2, cx + D / 2, cy + D / 2))
    canvas = shadow(canvas, pm, (0, 22), 30, (0, 0, 0), 0.55)
    canvas.paste(plate, (0, 0), pm)
    canvas = mb.ring(canvas, (cx, cy), D + 70, 26, mb.VOLT, (160, 200, 40))
    canvas = mb.ring(canvas, (cx, cy), D + 140, 6, mb.OFFWHITE, (170, 180, 175))
    return canvas


def perfum_emblem():
    S = 2000
    cx, cy, D = 1000, 1000, 1500
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    scene = mb.perfum_scene((S, S), 1130)
    scene = mb.soft_petals(scene, (cx - 650, cy - 650, cx + 650, cy + 100), 14, seed=2, size=(22, 48))
    crop, bx, base_y = mb.bottle_crop(0.42)
    scene = mb.place(scene, mb.feather_x(crop, 120, bottom=150), (cx - bx, 1240 - base_y))
    pm = mb.circle_mask((S, S), (cx - D / 2, cy - D / 2, cx + D / 2, cy + D / 2))
    canvas = shadow(canvas, pm, (0, 22), 30, (90, 40, 40), 0.35)
    canvas.paste(scene, (0, 0), pm)
    canvas = mb.ring(canvas, (cx, cy), D + 70, 24, (226, 190, 120), (172, 128, 62))
    canvas = mb.ring(canvas, (cx, cy), D + 136, 5, (250, 232, 190), (190, 150, 84))
    return canvas



def mono_emblem(key, color):
    """Simple one-colour emblem: rings plus the product as a clean silhouette (photo-like art does not survive one colour)."""
    S = 2000
    cx, cy, D = 1000, 1000, 1500
    c = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = mb.ring(c, (cx, cy), D + 70, 26, color, color)
    c = mb.ring(c, (cx, cy), D + 140, 6, color, color)
    c = mb.ring(c, (cx, cy), D - 60, 10, color, color)
    if key == "tessel":
        boot = mb.load("Footballboot.png", size=(1320, 1320))
        sil = Image.new("RGBA", boot.size, color + (0,))
        sil.putalpha(boot.split()[3].point(lambda v: 255 if v > 30 else 0))
        # the asset is a full square with a flat background: keep only the dark boot and the volt arcs
        a = np.asarray(boot).astype(np.float32)
        keep = ((a[..., :3].max(-1) < 90) | ((a[..., 0] > 180) & (a[..., 1] > 180) & (a[..., 2] < 140))) & (a[..., 3] > 30)
        sil.putalpha(Image.fromarray((keep * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2)))
        c = put(c, sil, center=(cx - 10, cy + 10))
    else:
        def fn(d, S_):
            k = S_
            d.ellipse(((cx - 330) * k, (cy - 110) * k, (cx + 330) * k, (cy + 550) * k), fill=color + (255,))          # body
            d.ellipse(((cx - 270) * k, (cy - 50) * k, (cx + 270) * k, (cy + 490) * k), fill=(0, 0, 0, 0))
            d.rectangle(((cx - 95) * k, (cy - 230) * k, (cx + 95) * k, (cy - 90) * k), fill=color + (255,))             # neck
            d.rectangle(((cx - 150) * k, (cy - 265) * k, (cx + 150) * k, (cy - 215) * k), fill=color + (255,))         # collar
            d.ellipse(((cx - 125) * k, (cy - 480) * k, (cx + 125) * k, (cy - 250) * k), fill=color + (255,))           # stopper
            d.rectangle(((cx - 190) * k, (cy + 540) * k, (cx + 190) * k, (cy + 600) * k), fill=color + (255,))         # base
            d.ellipse(((cx - 180) * k, (cy + 40) * k, (cx - 120) * k, (cy + 100) * k), fill=color + (255,))
            d.rectangle(((cx - 12) * k, (cy + 20) * k, (cx + 12) * k, (cy + 380) * k), fill=color + (255,))            # liquid line
        lay = Image.new("RGBA", (S * 2, S * 2), (0, 0, 0, 0))
        fn(ImageDraw.Draw(lay), 2)
        c = Image.alpha_composite(c, lay.resize((S, S), Image.LANCZOS))
    return c


def grad_bg(size, c1, c2, glow_c=None, cx=0.5):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t
    bg = Image.fromarray(np.repeat(arr, w, axis=1).astype("uint8")).convert("RGBA")
    if glow_c:
        bg = glow(bg, (w * (cx - 0.3), -h * 0.2, w * (cx + 0.3), h * 1.1), glow_c, blur=min(w, h) * 0.3, alpha=70)
    return bg


def speed_lines(bg, color, seed=4, n=18):
    import random
    rnd = random.Random(seed)
    layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = bg.size
    for _ in range(n):
        x, y = rnd.randint(int(w * 0.1), w), rnd.randint(0, h)
        ln = rnd.randint(int(w * 0.06), int(w * 0.25))
        d.line([(x, y), (x - ln, y + ln * 0.5)], fill=color + (rnd.randint(25, 70),), width=max(2, int(h * 0.004)))
    return Image.alpha_composite(bg, layer.filter(ImageFilter.GaussianBlur(0.8)))


def petals(bg, seed=7, n=22):
    return mb.soft_petals(bg, (0, 0, bg.width - 60, bg.height - 60), n, seed=seed, size=(max(10, bg.height // 40), max(24, bg.height // 18)))


THEMES = {
    "tessel": dict(
        name="TESSEL", sub="FOOTBALL BOOTS", tagline="UNSTOPPABLE BY DESIGN", folder="Tessel", emblem=tessel_emblem,
        wm_font="constan.ttf", wm_track=30, wm_light=((250, 252, 250), (206, 214, 208)), wm_dark=((16, 30, 26), (6, 14, 12)),
        accent=mb.VOLT, accent_d=(104, 150, 20), dark=mb.CHARCOAL, mid=mb.FOREST, deep=(8, 24, 20), paper=mb.OFFWHITE, ink=(20, 30, 28),
        sub_on_dark=mb.VOLT, sub_on_light=(40, 110, 50), hero="dark",
        hero_bg=lambda s: speed_lines(grad_bg(s, (16, 56, 44), (10, 20, 18), mb.PITCH), mb.VOLT),
        alt_bg=lambda s: grad_bg(s, (245, 247, 245), (226, 232, 228)),
        swatches=[("Pitch Green", mb.PITCH), ("Deep Forest", mb.FOREST), ("Charcoal", mb.CHARCOAL), ("Volt Yellow", mb.VOLT), ("Off-White", mb.OFFWHITE)],
        head_font="constan.ttf", head_name="Constantia Bold", body="segoeui.ttf"),
    "perfum": dict(
        name="PERFUM", sub="SCENT OF QUIET LUXURY", tagline="Scent of quiet luxury", folder="Perfum", emblem=perfum_emblem,
        wm_font="constan.ttf", wm_track=60, wm_light=((252, 240, 230), (232, 205, 190)), wm_dark=((96, 34, 60), (70, 22, 44)),
        accent=(184, 150, 84), accent_d=(140, 108, 50), dark=(84, 28, 52), mid=(120, 52, 82), deep=(54, 16, 34), paper=(247, 238, 222), ink=(60, 24, 40),
        sub_on_dark=(226, 190, 120), sub_on_light=(150, 112, 56), hero="light",
        hero_bg=lambda s: petals(grad_bg(s, (232, 178, 170), (246, 232, 214))),
        alt_bg=lambda s: grad_bg(s, (92, 32, 58), (54, 16, 34), (190, 120, 120)),
        swatches=[("Plum", (84, 28, 52)), ("Rose Blush", (234, 190, 178)), ("Antique Gold", (184, 150, 84)), ("Cream", (247, 238, 222)), ("Petal Pink", (232, 178, 170))],
        head_font="constan.ttf", head_name="Constantia", body="constani.ttf"),
}


# --------------------------------------------------------------------------------------------- generic parts

def wordmark(T, on_dark, width=2000):
    h = int(width * 0.32)
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    f0 = font(T["wm_font"], 100)
    tw = spaced_width(probe, T["name"], f0, T["wm_track"] * 0.5) / SS
    size = int(100 * width * 0.98 / tw)
    track = T["wm_track"] * 0.5 * size / 100
    f = font(T["wm_font"], size)
    m = text_mask((width, h), T["name"], f, (width / 2, h * 0.64), track=track)
    c = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    col = T["wm_light"] if on_dark else T["wm_dark"]
    if on_dark:
        c = shadow(c, m, (0, 6), 8, (0, 0, 0), 0.4)
    c = fill_mask(c, m, col[0], col[1])
    sub = text_mask((width, h), T["sub"], font("bahnschrift.ttf", int(size * 0.16)), (width / 2, h * 0.95), track=int(size * 0.06))
    return fill_mask(c, sub, T["sub_on_dark"] if on_dark else T["sub_on_light"])


def txt(canvas, s, xy, fnt, fill, track=0, anchor="left"):
    return fill_mask(canvas, text_mask(canvas.size, s, fnt, xy, track=track, anchor=anchor), fill)


def banner(T, W, H, em, wm, bare=False):
    hero_dark = T["hero"] == "dark"
    if W / H < 2.5 and not bare:
        bg = T["hero_bg"]((W, H))
        rw = int(W * 0.6)
        inner = banner(T, rw, int(rw / 3.65), em, wm, bare=True)
        return grain(put(bg, inner, center=(W / 2, H / 2)), 8)
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if bare else T["hero_bg"]((W, H))
    bg = put(bg, fit(em, H * 0.86, H * 0.86), center=(W * 0.2, H * 0.5), shadow_op=0.3)
    bg = put(bg, fit(wm, W * 0.5, H * 0.5), center=(W * 0.62, H * 0.44))
    d = ImageDraw.Draw(bg)
    y = H * 0.44 + H * 0.28
    lc = T["accent"] if hero_dark else T["accent_d"]
    d.line([(W * 0.4, y), (W * 0.84, y)], fill=lc + (255,), width=max(2, int(H * 0.01)))
    bg = txt(bg, T["tagline"].upper() if hero_dark else T["tagline"], (W * 0.62, y + H * 0.13),
             font(T["body"] if not hero_dark else "bahnschrift.ttf", max(10, int(H * (0.085 if hero_dark else 0.11)))),
             (226, 238, 250) if hero_dark else T["ink"], track=int(H * 0.02), anchor="center")
    return bg if bare else grain(bg, 8)


def post(T, em, wm, story):
    W, H = (1080, 1920) if story else (1080, 1080)
    img = T["hero_bg"]((W, H))
    img = put(img, fit(em, W * 0.62, H * 0.45), center=(W / 2, H * (0.38 if story else 0.37)), shadow_op=0.3)
    img = put(img, fit(wm, W * 0.78, 240), center=(W / 2, H * (0.7 if story else 0.76)))
    hero_dark = T["hero"] == "dark"
    img = txt(img, T["tagline"].upper() if hero_dark else T["tagline"], (W / 2, H * (0.83 if story else 0.91)),
              font("bahnschrift.ttf" if hero_dark else T["body"], 46 if hero_dark else 58), (214, 232, 250) if hero_dark else T["ink"], track=12, anchor="center")
    return grain(img, 8)


def avatar(T, em):
    img = T["hero_bg"]((1000, 1000))
    return put(img, fit(em, 880, 880), center=(500, 500), shadow_op=0.3)


def favicon(T, em, size):
    img = Image.new("RGBA", (size, size), T["deep"] + (255,))
    pad = max(1, int(size * 0.06))
    img = put(img, fit(em, size - 2 * pad, size - 2 * pad), center=(size / 2, size / 2))
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), radius=size * 4 // 5, fill=255)
    img.putalpha(m.resize((size, size), Image.LANCZOS))
    return img


def cards(T, em, wm_l, full_d):
    W, H = 1050, 600
    n = T["name"].lower()
    front = T["alt_bg"]((W, H)) if T["hero"] == "light" else T["hero_bg"]((W, H))
    front = put(front, fit(full_d, W * 0.42, H * 0.84), center=(W / 2, H / 2), shadow_op=0.3)
    back = Image.new("RGBA", (W, H), T["paper"] + (255,))
    back = put(back, fit(em, 210, 210), topleft=(70, 66))
    back = put(back, fit(wm_l, 430, 140), topleft=(310, 100))
    ImageDraw.Draw(back).rectangle((70, 320, W - 70, 326), fill=T["accent"] + (255,))
    back = txt(back, "Full Name", (70, 396), font(T["head_font"], 56), T["ink"])
    back = txt(back, "JOB TITLE", (70, 442), font("bahnschrift.ttf", 26), T["sub_on_light"], track=6)
    for i, (l, v) in enumerate((("T", PHONE), ("E", MAIL_TPL.format(n=n)), ("W", SITE_TPL.format(n=n)))):
        back = txt(back, l, (70, 498 + i * 36), font("bahnschrift.ttf", 24), T["sub_on_light"])
        back = txt(back, v, (116, 498 + i * 36), font("segoeui.ttf", 26), (70, 70, 80))
    ImageDraw.Draw(back).polygon([(W, H), (W - 200, H), (W, H - 200)], fill=T["accent"] + (255,))
    return front, back


def letterhead(T, em, wm_l):
    W, H = 2480, 3508
    n = T["name"].lower()
    page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    page.paste(Image.new("RGBA", (W, 36), T["accent"] + (255,)), (0, 0))
    page = put(page, fit(em, 250, 250), topleft=(200, 160))
    page = put(page, fit(wm_l, 720, 230), topleft=(480, 170))
    ghost = solid(fit(em, 1500, 1500), T["accent"])
    ghost.putalpha(ghost.split()[3].point(lambda v: int(v * 0.06)))
    page = put(page, ghost, center=(W - 400, H - 600))
    ImageDraw.Draw(page).rectangle((200, H - 340, W - 200, H - 334), fill=T["accent"] + (255,))
    for i, t in enumerate((f"{T['name'].title()} Ltd.", "Street 1, City, Country", f"{MAIL_TPL.format(n=n)}  -  {SITE_TPL.format(n=n)}")):
        page = txt(page, t, (200, H - 270 + i * 62), font("segoeui.ttf", 40), (70, 70, 80))
    return page


def signature(T, em):
    W, H = 1200, 360
    n = T["name"].lower()
    sig = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    sig = put(sig, fit(em, 270, 270), topleft=(40, 45))
    ImageDraw.Draw(sig).rectangle((340, 40, 344, H - 40), fill=T["accent"] + (255,))
    sig = txt(sig, "Full Name", (390, 104), font(T["head_font"], 60), T["ink"])
    sig = txt(sig, f"JOB TITLE  -  {T['name']}", (390, 150), font("bahnschrift.ttf", 26), T["sub_on_light"], track=5)
    for i, t in enumerate((PHONE, MAIL_TPL.format(n=n), SITE_TPL.format(n=n))):
        sig = txt(sig, t, (390, 214 + i * 46), font("segoeui.ttf", 32), (70, 70, 80))
    return sig


def slides(T, em, wm_l, full_d):
    W, H = 1920, 1080
    t = T["alt_bg"]((W, H)) if T["hero"] == "light" else T["hero_bg"]((W, H))
    t = put(t, fit(full_d, 640, 820), center=(470, H / 2), shadow_op=0.3)
    t = txt(t, "Presentation title", (900, 470), font(T["head_font"], 118), (246, 242, 240))
    t = txt(t, "SUBTITLE  -  DATE", (904, 560), font("bahnschrift.ttf", 42), T["sub_on_dark"], track=8)
    ImageDraw.Draw(t).rectangle((900, 590, 1240, 598), fill=T["accent"] + (255,))
    c = Image.new("RGBA", (W, H), T["paper"] + (255,))
    c.paste(Image.new("RGBA", (W, 20), T["accent"] + (255,)), (0, 0))
    c = put(c, fit(em, 140, 140), topleft=(W - 220, 60))
    c = txt(c, "Slide heading", (120, 220), font(T["head_font"], 92), T["ink"])
    ImageDraw.Draw(c).rectangle((120, 250, 380, 256), fill=T["accent"] + (255,))
    for i in range(3):
        y = 370 + i * 130
        ImageDraw.Draw(c).rectangle((126, y, 150, y + 24), fill=T["accent"] + (255,))
        c = txt(c, f"Key point number {i + 1} goes here", (180, y + 26), font("segoeui.ttf", 54), (70, 70, 80))
    return t, c


def guidelines(T, em, wm_l, full_l, full_d, mono_w, mono_k):
    W, H = 3000, 2000
    img = Image.new("RGBA", (W, H), T["paper"] + (255,))
    img.paste(Image.new("RGBA", (W, 36), T["accent"] + (255,)), (0, 0))
    img = txt(img, f"{T['name'].title()} - brand guidelines", (120, 220), font(T["head_font"], 100), T["ink"])
    img = txt(img, "LOGO, COLOUR AND TYPE AT A GLANCE", (124, 280), font("bahnschrift.ttf", 38), T["sub_on_light"], track=8)
    tiles = [("PRIMARY", Image.new("RGBA", (560, 560), (255, 255, 255, 255)), full_l), ("ON DARK", T["alt_bg"]((560, 560)) if T["hero"] == "light" else T["hero_bg"]((560, 560)), full_d),
             ("WHITE", Image.new("RGBA", (560, 560), T["dark"] + (255,)), mono_w), ("BLACK", Image.new("RGBA", (560, 560), (255, 255, 255, 255)), mono_k)]
    for i, (nme, bg, lg) in enumerate(tiles):
        x = 120 + i * 700
        t = put(bg, fit(lg, 470, 500), center=(280, 280))
        m = Image.new("L", (560, 560), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, 559, 559), radius=28, fill=255)
        img.paste(t, (x, 360), m)
        ImageDraw.Draw(img).rounded_rectangle((x, 360, x + 560, 920), radius=28, outline=T["accent"] + (180,), width=3)
        img = txt(img, nme, (x + 280, 990), font("bahnschrift.ttf", 32), (70, 70, 80), track=6, anchor="center")
    img = txt(img, "COLOUR", (124, 1110), font("bahnschrift.ttf", 38), T["sub_on_light"], track=8)
    for i, (nme, c) in enumerate(T["swatches"]):
        x = 120 + i * 560
        ImageDraw.Draw(img).rounded_rectangle((x, 1160, x + 500, 1360), radius=22, fill=c + (255,), outline=(150, 150, 160, 255), width=2)
        img = txt(img, nme, (x, 1420), font(T["head_font"], 46), T["ink"])
        img = txt(img, "#%02X%02X%02X   RGB %d %d %d" % (c + c), (x, 1470), font("segoeui.ttf", 30), (70, 70, 80))
    img = txt(img, "TYPE", (124, 1580), font("bahnschrift.ttf", 38), T["sub_on_light"], track=8)
    img = txt(img, f"Headings and wordmark: {T['head_name']}", (120, 1670), font(T["head_font"], 66), T["ink"])
    img = txt(img, "Body: Segoe UI.  Labels: Bahnschrift, wide-spaced capitals.", (120, 1750), font("segoeui.ttf", 46), (70, 70, 80))
    img = txt(img, "USE", (1884, 1610), font("bahnschrift.ttf", 38), T["sub_on_light"], track=8)
    for i, t in enumerate(("Keep clear space equal to a quarter of the emblem's width.", "Minimum size: emblem 24 px, full logo 120 px wide.", "Never stretch, rotate or recolour the logo.")):
        img = txt(img, t, (1880, 1670 + i * 70), font("segoeui.ttf", 36), (70, 70, 80))
    return grain(img, 5)


def product_poster(T, key, em):
    W, H = 1800, 2400
    img = T["hero_bg"]((W, H))
    if key == "tessel":
        boot = mb.load("Footballboot.png", size=(1750, 1750))
        img = glow(img, (200, 500, 1600, 1900), mb.PITCH, blur=220, alpha=110)
        img = put(img, boot, center=(W / 2 + 40, 1400), shadow_op=0.55)
        ink, lc = (250, 252, 250), T["accent"]
    else:
        crop, bx, base_y = mb.bottle_crop(0.72)
        img = glow(img, (300, 600, 1500, 1800), (255, 236, 222), blur=200, alpha=130)
        img = put(img, mb.feather_x(crop, 200, bottom=200), topleft=(W // 2 - bx, 2250 - base_y), shadow_op=0.0)
        ink, lc = T["dark"], T["accent_d"]
    img = txt(img, T["name"], (W / 2, 330), font("constan.ttf", 300), ink, track=60 if key == "perfum" else 24, anchor="center")
    ImageDraw.Draw(img).rectangle((W / 2 - 300, 380, W / 2 + 300, 388), fill=lc + (255,))
    img = txt(img, T["tagline"] if key == "perfum" else T["tagline"], (W / 2, 480), font("constani.ttf" if key == "perfum" else "bahnschrift.ttf", 92 if key == "perfum" else 70),
              T["ink"] if key == "perfum" else (226, 238, 250), track=10, anchor="center")
    return grain(img, 8)


def product_tag(T, em):
    W, H = 1000, 1600
    img = Image.new("RGBA", (W, H), T["paper"] + (255,))
    img.paste(Image.new("RGBA", (W, 36), T["accent"] + (255,)), (0, 0))
    ImageDraw.Draw(img).ellipse((W / 2 - 46, 70, W / 2 + 46, 162), fill=(0, 0, 0, 0), outline=T["accent"] + (255,), width=8)
    img = put(img, fit(em, 760, 760), center=(W / 2, 700), shadow_op=0.25)
    img = txt(img, T["name"], (W / 2, 1230), font("constan.ttf", 170), T["ink"], track=26, anchor="center")
    ImageDraw.Draw(img).rectangle((W / 2 - 200, 1290, W / 2 + 200, 1296), fill=T["accent"] + (255,))
    img = txt(img, T["tagline"] if T["hero"] == "light" else T["tagline"].title(), (W / 2, 1400), font("constani.ttf", 56), T["sub_on_light"], track=4, anchor="center")
    return img


# -------------------------------------------------------------------------------------------------- driver

def build(key):
    T = THEMES[key]
    out = ROOT / "images" / "design" / T["folder"]
    out.mkdir(parents=True, exist_ok=True)
    n = key

    def save(img, name, rgba=False):
        p = out / name
        if name.endswith(".ico"):
            img.save(p, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        else:
            (img if rgba else img.convert("RGB")).save(p, optimize=True)
        print("Saved", p.relative_to(ROOT))

    em = crop_pad(T["emblem"]())
    wm_d, wm_l = crop_pad(wordmark(T, True)), crop_pad(wordmark(T, False))
    full_d, full_l = crop_pad(lockup(em, wm_d), 0.04), crop_pad(lockup(em, wm_l), 0.04)
    em_w, em_k = crop_pad(mono_emblem(key, (255, 255, 255))), crop_pad(mono_emblem(key, (20, 20, 22)))
    mono_w = crop_pad(lockup(em_w, crop_pad(stencil(wm_d, (255, 255, 255)))), 0.04)
    mono_k = crop_pad(lockup(em_k, crop_pad(stencil(wm_l, (20, 20, 22)))), 0.04)

    save(fit(full_l, 2000, 2200), f"{n}_logo.png", rgba=True)
    save(fit(em, 1500, 1500), f"{n}_emblem.png", rgba=True)
    save(fit(wm_l, 2400, 800), f"{n}_wordmark.png", rgba=True)
    save(fit(mono_w, 2000, 2200), f"{n}_logo_white.png", rgba=True)
    save(fit(mono_k, 2000, 2200), f"{n}_logo_black.png", rgba=True)
    dk = T["alt_bg"]((2000, 2000)) if T["hero"] == "light" else T["hero_bg"]((2000, 2000))
    save(put(dk, fit(full_d, 1400, 1600), center=(1000, 1000), shadow_op=0.3), f"{n}_logo_dark.png")
    save(avatar(T, em), f"{n}_avatar.png")
    for s in (512, 192, 32):
        save(favicon(T, em, s), f"{n}_favicon_{s}.png", rgba=True)
    save(favicon(T, em, 64), f"{n}_favicon.ico")
    for nm, (W, H) in (("linkedin", (1584, 396)), ("twitter", (1500, 500)), ("facebook", (1640, 624)), ("youtube", (2560, 1440)), ("twitch", (2400, 960))):
        save(banner(T, W, H, em, wm_d if T["hero"] == "dark" else wm_l), f"{n}_banner_{nm}.png")
    save(banner(T, 1200, 630, em, wm_d if T["hero"] == "dark" else wm_l), f"{n}_og_image.png")
    hw = wm_d if T["hero"] == "dark" else wm_l
    save(post(T, em, hw, False), f"{n}_post_square.png")
    save(post(T, em, hw, True), f"{n}_story.png")
    save(product_poster(T, key, em), f"{n}_product_poster.png")
    save(product_tag(T, em), f"{n}_product_tag.png")
    f, b = cards(T, em, wm_l, full_d)
    save(f, f"{n}_business_card_front.png")
    save(b, f"{n}_business_card_back.png")
    f.convert("RGB").save(out / f"{n}_business_card.pdf", save_all=True, append_images=[b.convert("RGB")], resolution=300)
    lh = letterhead(T, em, wm_l)
    save(lh, f"{n}_letterhead.png")
    lh.convert("RGB").save(out / f"{n}_letterhead.pdf", resolution=300)
    save(signature(T, em), f"{n}_email_signature.png")
    t, c = slides(T, em, wm_l, full_d)
    save(t, f"{n}_slide_title.png")
    save(c, f"{n}_slide_content.png")
    g = guidelines(T, em, wm_l, full_l, full_d, mono_w, mono_k)
    save(g, f"{n}_brand_guidelines.png")
    g.convert("RGB").save(out / f"{n}_brand_guidelines.pdf", resolution=200)


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["tessel", "perfum"]):
        build(k)
    print("done")

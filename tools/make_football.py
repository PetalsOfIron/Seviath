#!/usr/bin/env python3
"""
Football company brand kit in the style of images/Football.png (navy gradient, cyan stripes, pale footballer
silhouette and ball). The silhouette is cut from your banner; the ball is redrawn cleanly; the name and tagline are
placeholders you can change in NAME / TAGLINE below.

    python tools/make_football.py
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from art import *  # noqa: F401,F403
import fb_extract

OUT = ROOT / "images" / "design" / "Football"
NAME, SUB, TAGLINE = "STRIKELINE", "FOOTBALL COMPANY", "PLAY THE LINE"
SITE, MAIL, PHONE = "strikeline.example", "hello@strikeline.example", "+00 000 000 000"
CYAN, CYAN_D, NAVY, DEEP, ABYSS = (0, 168, 232), (0, 110, 170), (31, 58, 95), (1, 52, 94), (16, 24, 32)
PALE, INK, WHITE = (232, 232, 232), (10, 2, 6), (255, 255, 255)
SS_ = 4


# ---------------------------------------------------------------------------------------------- emblem

def ball(d_px):
    S = d_px * SS_
    c, r = S / 2, S * 0.47
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((c - r, c - r, c + r, c + r), fill=(244, 244, 244, 255), outline=INK + (255,), width=int(S * 0.035))

    def pent(cx, cy, rr, rot, fill):
        pts = [(cx + math.cos(rot + 2 * math.pi * i / 5) * rr, cy + math.sin(rot + 2 * math.pi * i / 5) * rr) for i in range(5)]
        d.polygon(pts, fill=fill, outline=INK + (255,), width=int(S * 0.012))
    pent(c, c, r * 0.30, -math.pi / 2, INK + (255,))
    for i in range(5):
        a0 = -math.pi / 2 + 2 * math.pi * i / 5
        d.line([(c + math.cos(a0) * r * 0.30, c + math.sin(a0) * r * 0.30), (c + math.cos(a0) * r * 0.62, c + math.sin(a0) * r * 0.62)], fill=INK + (255,), width=int(S * 0.014))
        pent(c + math.cos(a0) * r * 0.83, c + math.sin(a0) * r * 0.83, r * 0.30, a0 + math.pi, CYAN + (255,))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((c - r - S * 0.02, c - r - S * 0.02, c + r + S * 0.02, c + r + S * 0.02), fill=255)
    im.putalpha(ImageChops.multiply(im.split()[3], m))
    return im.resize((d_px, d_px), Image.LANCZOS)


def figure():
    fig = fb_extract.cutout()
    ImageDraw.Draw(fig).rectangle((306, 730, 332, 764), fill=PALE + (255,))
    fig.alpha_composite(ball(230), (327 - 115, 868 - 115))
    box = fig.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
    return fig.crop(box)


def stripes(w, h, color=CYAN, seed=1):
    """Bundle of horizontal stripes of different thickness, like the banner."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pattern = [(0.00, 0.012), (0.045, 0.02), (0.095, 0.012), (0.14, 0.05), (0.24, 0.016), (0.30, 0.09), (0.45, 0.02), (0.52, 0.09), (0.67, 0.02), (0.73, 0.05), (0.82, 0.016), (0.88, 0.02), (0.94, 0.012)]
    for y, t in pattern:
        d.rectangle((0, int(y * h), w, int((y + t) * h) + 1), fill=color + (255,))
    return im


def shield_mask(w, h, ss=3):
    m = Image.new("L", (w * ss, h * ss), 0)
    path = [(0.06 * w, 0.04 * h), (0.94 * w, 0.04 * h)]
    for i in range(0, 61):
        t = i / 60
        path.append((w * (0.5 + 0.44 * (1 - t ** 2.2)), h * (0.60 + 0.38 * t)))
    for i in range(60, -1, -1):
        t = i / 60
        path.append((w * (0.5 - 0.44 * (1 - t ** 2.2)), h * (0.60 + 0.38 * t)))
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in path], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def emblem(size=1600):
    """Crest: navy shield, cyan stripes, footballer and ball, cyan rim."""
    w, h = size, int(size * 1.12)
    sm = shield_mask(w, h)
    base = radial((w, h), NAVY, ABYSS, cx=0.5, cy=0.35, spread=0.9).convert("RGBA")
    st = stripes(w, int(h * 0.3), CYAN)
    base.alpha_composite(st, (0, int(h * 0.27)))
    fig = figure()
    s = h * 0.84 / fig.height
    fig = fig.resize((round(fig.width * s), round(fig.height * s)), Image.LANCZOS)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.alpha_composite(fig, ((w - fig.width) // 2, int(h * 0.08)))
    base = shadow(base, layer.split()[3], (0, 14), 22, (0, 0, 0), 0.5)
    base = Image.alpha_composite(base, layer)
    crest = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    crest.paste(base, (0, 0), sm)
    rim = ImageChops.subtract(sm, sm.filter(ImageFilter.MinFilter(max(3, w // 50) | 1)))
    ring = Image.new("RGBA", (w, h), CYAN + (0,))
    ring.putalpha(rim)
    out = Image.alpha_composite(crest, ring)
    outer = ImageChops.subtract(sm.filter(ImageFilter.MaxFilter(max(3, w // 90) | 1)), sm)
    o = Image.new("RGBA", (w, h), PALE + (0,))
    o.putalpha(outer)
    return Image.alpha_composite(out, o)


def wordmark(width=2000, dark=False):
    h = int(width * 0.34)
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    f = ImageFont.truetype(str(FONTS / "impact.ttf"), 400 * SS) if False else font("impact.ttf", 100)
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    tw = spaced_width(probe, NAME, f, 14) / SS
    size = int(100 * width * 0.98 / tw)
    f = font("impact.ttf", size)
    m = text_mask((width, h), NAME, f, (width / 2, h * 0.62), track=14)
    canvas = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    canvas = shadow(canvas, m, (0, 6), 8, (0, 0, 0), 0.0 if dark else 0.45)
    canvas = fill_mask(canvas, m, (14, 30, 58), (6, 16, 34)) if dark else fill_mask(canvas, m, (250, 252, 255), (196, 206, 216))
    sub = text_mask((width, h), SUB, font("bahnschrift.ttf", int(size * 0.2)), (width / 2, h * 0.93), track=int(size * 0.06))
    canvas = fill_mask(canvas, sub, CYAN_D if dark else CYAN)
    return canvas


def lockup(em, wm, gap=0.04):
    w = max(em.width, wm.width)
    h = em.height + wm.height + int(em.height * gap)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(em, ((w - em.width) // 2, 0))
    out.alpha_composite(wm, ((w - wm.width) // 2, em.height + int(em.height * gap)))
    return out


def crop_pad(img, pad=0.03):
    box = img.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
    c = img.crop(box)
    p = int(max(c.size) * pad)
    out = Image.new("RGBA", (c.width + 2 * p, c.height + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(c, (p, p))
    return out


def fit(img, bw, bh):
    s = min(bw / img.width, bh / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def put(canvas, img, center=None, topleft=None, shadow_op=0.0):
    x, y = topleft if topleft else (round(center[0] - img.width / 2), round(center[1] - img.height / 2))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(img, (x, y))
    if shadow_op:
        canvas = shadow(canvas, layer.split()[3], (0, 10), 18, (0, 0, 0), shadow_op)
    return Image.alpha_composite(canvas, layer)


def stencil(img, color):
    """One-colour crest that keeps its detail: dark areas become gaps."""
    a = np.asarray(img).astype(np.float32)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    keep = np.clip((lum - 66) / 18, 0, 1)
    out = Image.new("RGBA", img.size, color + (0,))
    out.putalpha(Image.fromarray((a[..., 3] * keep).astype("uint8")))
    return out


def solid(img, color):
    out = Image.new("RGBA", img.size, color + (0,))
    out.putalpha(img.split()[3])
    return out


def bg_dark(size, stripe_fade=True):
    w, h = size
    bg = radial(size, NAVY, ABYSS, cx=0.5, cy=0.5, spread=1.0).convert("RGBA")
    if stripe_fade:
        sh = int(h * 0.36)
        s = stripes(int(w * 0.13), sh)
        a = s.split()[3].point(lambda v: int(v * 0.9))
        s.putalpha(a)
        bg.alpha_composite(s, (0, int(h * 0.32)))
        bg.alpha_composite(s.transpose(Image.FLIP_LEFT_RIGHT), (w - s.width, int(h * 0.32)))
    return bg


def bg_light(size):
    return Image.new("RGBA", size, (244, 247, 250, 255))


def text(canvas, s, xy, fnt, fill, track=0, anchor="left"):
    return fill_mask(canvas, text_mask(canvas.size, s, fnt, xy, track=track, anchor=anchor), fill)


def save(img, name, rgba=False):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if name.endswith(".ico"):
        img.save(path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    else:
        (img if rgba else img.convert("RGB")).save(path, optimize=True)
    print("Saved", path.relative_to(ROOT))


# ---------------------------------------------------------------------------------------------- pieces

def banner(W, H, em, wm, bare=False):
    if W / H < 2.5 and not bare:
        bg = bg_dark((W, H))
        rw = int(W * 0.6)
        inner = banner(rw, int(rw / 3.65), em, wm, bare=True)
        return grain(put(bg, inner, center=(W / 2, H / 2)), 8)
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if bare else bg_dark((W, H))
    bg = put(bg, fit(em, H * 0.84, H * 0.84), center=(W * 0.22, H * 0.5), shadow_op=0.5)
    bg = put(bg, fit(wm, W * 0.5, H * 0.5), center=(W * 0.62, H * 0.44), shadow_op=0.3)
    d = ImageDraw.Draw(bg)
    y = H * 0.44 + H * 0.3
    d.line([(W * 0.4, y), (W * 0.84, y)], fill=CYAN + (255,), width=max(2, int(H * 0.012)))
    bg = text(bg, TAGLINE, (W * 0.62, y + H * 0.14), font("bahnschrift.ttf", max(10, int(H * 0.085))), (226, 238, 250), track=int(H * 0.025), anchor="center")
    return bg if bare else grain(bg, 8)


def jersey(em, home=True):
    W, H = 1600, 1800
    body_c = (250, 252, 255) if not home else NAVY
    trim = CYAN
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def fn(d, S):
        pts = [(430, 140), (560, 90), (680, 150), (920, 150), (1040, 90), (1170, 140), (1480, 380), (1330, 560), (1180, 470), (1180, 1620), (420, 1620), (420, 470), (270, 560), (120, 380)]
        d.polygon([(x * S, y * S) for x, y in pts], fill=body_c + (255,), outline=INK + (255,), width=int(10 * S))
        d.polygon([(x * S, y * S) for x, y in [(680, 150), (800, 330), (920, 150)]], fill=(0, 0, 0, 0))
        d.line([(680 * S, 150 * S), (800 * S, 330 * S), (920 * S, 150 * S)], fill=trim + (255,), width=int(34 * S), joint="curve")
        for sx in (1, -1):
            cx = 800
            d.line([((cx + sx * 380) * S, 470 * S), ((cx + sx * 380) * S, 1620 * S)], fill=trim + (255,), width=int(24 * S))
        d.polygon([(x * S, y * S) for x, y in [(120, 380), (270, 560), (230, 610), (80, 430)]], fill=trim + (255,))
        d.polygon([(x * S, y * S) for x, y in [(1480, 380), (1330, 560), (1370, 610), (1520, 430)]], fill=trim + (255,))
        for i in range(7):
            d.rectangle((420 * S, (1180 + i * 62) * S, 1180 * S, (1180 + i * 62 + 22) * S), fill=(trim if home else (0, 168, 232)) + (60,))
    layer = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer), 2)
    canvas = Image.alpha_composite(canvas, layer.resize((W, H), Image.LANCZOS))
    canvas = put(canvas, fit(em, 220, 250), topleft=(360 + 560 - 110 + 40, 330))
    canvas = text(canvas, "10", font("impact.ttf", 330), (255, 255, 255) if home else NAVY, anchor="center") if False else canvas
    return canvas


def card_pair(em, wm, full):
    W, H = 1050, 600
    front = bg_dark((W, H))
    front = put(front, fit(full, W * 0.4, H * 0.82), center=(W / 2, H / 2), shadow_op=0.4)
    back = bg_light((W, H))
    back = put(back, fit(em, 200, 230), topleft=(70, 60))
    back = put(back, fit(wm, 420, 140), topleft=(300, 100))
    d = ImageDraw.Draw(back)
    d.rectangle((70, 320, W - 70, 326), fill=CYAN + (255,))
    back = text(back, "Full Name", (70, 396), font("impact.ttf", 58), ABYSS)
    back = text(back, "JOB TITLE", (70, 442), font("bahnschrift.ttf", 28), CYAN_D, track=6)
    for i, (l, v) in enumerate((("T", PHONE), ("E", MAIL), ("W", SITE))):
        back = text(back, l, (70, 498 + i * 36), font("bahnschrift.ttf", 24), CYAN_D)
        back = text(back, v, (116, 498 + i * 36), font("segoeui.ttf", 26), (60, 66, 74))
    d = ImageDraw.Draw(back)
    d.polygon([(W, H), (W - 200, H), (W, H - 200)], fill=CYAN + (255,))
    return front, back


def letterhead(em, wm):
    W, H = 2480, 3508
    page = Image.new("RGBA", (W, H), WHITE + (255,))
    page.alpha_composite(stripes(W, 70, CYAN), (0, 0))
    page = put(page, fit(em, 230, 260), topleft=(200, 170))
    page = put(page, fit(wm, 700, 240), topleft=(470, 180))
    ghost = solid(fit(em, 1500, 1700), CYAN)
    ghost.putalpha(ghost.split()[3].point(lambda v: int(v * 0.05)))
    page = put(page, ghost, center=(W - 400, H - 600))
    d = ImageDraw.Draw(page)
    d.rectangle((200, H - 340, W - 200, H - 334), fill=CYAN + (255,))
    for i, t in enumerate((f"{NAME.title()} {SUB.title()}", "Street 1, City, Country", f"{MAIL}  -  {SITE}")):
        page = text(page, t, (200, H - 270 + i * 62), font("segoeui.ttf", 40), (60, 66, 74))
    return page


def signature(em):
    W, H = 1200, 360
    sig = Image.new("RGBA", (W, H), WHITE + (255,))
    sig = put(sig, fit(em, 230, 270), topleft=(50, 45))
    ImageDraw.Draw(sig).rectangle((330, 40, 334, H - 40), fill=CYAN + (255,))
    sig = text(sig, "Full Name", (390, 104), font("impact.ttf", 64), ABYSS)
    sig = text(sig, f"JOB TITLE  -  {NAME}", (390, 150), font("bahnschrift.ttf", 26), CYAN_D, track=5)
    for i, t in enumerate((PHONE, MAIL, SITE)):
        sig = text(sig, t, (390, 214 + i * 46), font("segoeui.ttf", 32), (60, 66, 74))
    return sig


def slides(em, wm, full):
    W, H = 1920, 1080
    t = bg_dark((W, H))
    t = put(t, fit(full, 640, 820), center=(470, H / 2), shadow_op=0.4)
    t = text(t, "Presentation title", (900, 470), font("impact.ttf", 128), (240, 246, 255))
    t = text(t, "SUBTITLE  -  DATE", (904, 560), font("bahnschrift.ttf", 42), CYAN, track=8)
    ImageDraw.Draw(t).rectangle((900, 590, 1240, 600), fill=CYAN + (255,))
    c = bg_light((W, H))
    c.alpha_composite(stripes(W, 60, CYAN), (0, 0))
    c = put(c, fit(em, 130, 150), topleft=(W - 210, 70))
    c = text(c, "Slide heading", (120, 220), font("impact.ttf", 96), ABYSS)
    ImageDraw.Draw(c).rectangle((120, 250, 380, 258), fill=CYAN + (255,))
    for i in range(3):
        y = 370 + i * 130
        ImageDraw.Draw(c).rectangle((126, y, 150, y + 24), fill=CYAN + (255,))
        c = text(c, f"Key point number {i + 1} goes here", (180, y + 26), font("segoeui.ttf", 54), (60, 66, 74))
    return t, c


def post(em, wm, kind):
    W, H = (1080, 1080) if kind == "square" else (1080, 1920)
    img = bg_dark((W, H))
    img = put(img, fit(em, W * 0.55, H * 0.4), center=(W / 2, H * (0.36 if kind == "square" else 0.38)), shadow_op=0.5)
    img = put(img, fit(wm, W * 0.78, 220), center=(W / 2, H * (0.76 if kind == "square" else 0.68)), shadow_op=0.3)
    img = text(img, TAGLINE, (W / 2, H * (0.9 if kind == "square" else 0.8)), font("bahnschrift.ttf", 46), (214, 232, 250), track=14, anchor="center")
    return grain(img, 8)


def match_poster(em, wm):
    W, H = 1800, 2400
    img = bg_dark((W, H), stripe_fade=False)
    for i in range(7):
        s = stripes(W, 260)
        img.alpha_composite(s, (0, 180 + i * 300)) if i in (0, 6) else None
    big = fit(figure(), 1200, 1540)
    glw = glow(img, (200, 400, 1600, 1900), CYAN, blur=200, alpha=70)
    img = glw
    img = put(img, big, center=(W / 2, 1080), shadow_op=0.5)
    img = text(img, "MATCH DAY", (W / 2, 330), font("impact.ttf", 250), (250, 252, 255), track=14, anchor="center")
    img = text(img, f"{NAME}  VS  OPPONENT", (W / 2, 1980), font("impact.ttf", 104), CYAN, track=8, anchor="center")
    img = text(img, "SATURDAY  -  15:00  -  HOME STADIUM", (W / 2, 2110), font("bahnschrift.ttf", 52), (226, 238, 250), track=10, anchor="center")
    img = put(img, fit(em, 200, 230), center=(W / 2, 2290))
    return grain(img, 8)


def ticket(em, wm):
    W, H = 2000, 760
    img = bg_dark((W, H))
    img = put(img, fit(em, 300, 340), center=(240, H / 2), shadow_op=0.4)
    img = text(img, NAME, (470, 250), font("impact.ttf", 170), (250, 252, 255), track=10)
    img = text(img, "MATCH TICKET  -  SATURDAY 15:00", (474, 350), font("bahnschrift.ttf", 44), CYAN, track=10)
    img = text(img, "HOME STADIUM  -  BLOCK B  -  ROW 12  -  SEAT 24", (474, 450), font("bahnschrift.ttf", 36), (226, 238, 250), track=6)
    d = ImageDraw.Draw(img)
    d.line([(1560, 40), (1560, H - 40)], fill=(226, 238, 250, 160), width=4)
    for y in range(50, H - 50, 36):
        d.rectangle((1556, y, 1564, y + 18), fill=(16, 24, 32, 255))
    for i in range(34):  # simple barcode
        x = 1625 + i * 10
        d.rectangle((x, 180, x + (3 if i % 3 else 7), 560), fill=(244, 247, 250, 255))
    return grain(img, 6)


def scarf(em):
    W, H = 2400, 600
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(img)
    for i, (x, w, c) in enumerate(((160, 50, CYAN), (260, 20, PALE), (320, 50, CYAN), (W - 530, 50, CYAN), (W - 440, 20, PALE), (W - 370, 50, CYAN))):
        d.rectangle((x, 0, x + w, H), fill=c + (255,))
    img = text(img, NAME, (W / 2 + 120, 395), font("impact.ttf", 230), (250, 252, 255), track=20, anchor="center")
    img = put(img, fit(em, 330, 370), center=(W / 2 - 860, H / 2))
    for x in range(0, W, 24):   # fringe
        d = ImageDraw.Draw(img)
    return grain(img, 10)


def avatar(em):
    S = 1000
    img = radial((S, S), NAVY, ABYSS, cx=0.5, cy=0.5, spread=0.9).convert("RGBA")
    return put(img, fit(em, 800, 880), center=(S / 2, S / 2 + 10), shadow_op=0.45)


def favicon(em, size):
    img = Image.new("RGBA", (size, size), ABYSS + (255,))
    pad = max(1, int(size * 0.1))
    img = put(img, fit(em, size - 2 * pad, size - 2 * pad), center=(size / 2, size / 2))
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), radius=size * 4 // 5, fill=255)
    img.putalpha(m.resize((size, size), Image.LANCZOS))
    return img


LOCK_DARK, LOCK_WHITE, LOCK_BLACK = [None], [None], [None]


def guidelines(em, wm, full):
    W, H = 3000, 2000
    img = bg_light((W, H))
    img.alpha_composite(stripes(W, 70, CYAN), (0, 0))
    img = text(img, f"{NAME.title()} - brand guidelines", (120, 220), font("impact.ttf", 110), ABYSS)
    img = text(img, "LOGO, COLOUR AND TYPE AT A GLANCE", (124, 280), font("bahnschrift.ttf", 38), CYAN_D, track=8)
    tiles = [("PRIMARY", bg_light((560, 560)), full), ("ON DARK", bg_dark((560, 560), False), LOCK_DARK[0]),
             ("WHITE", Image.new("RGBA", (560, 560), NAVY + (255,)), LOCK_WHITE[0]), ("BLACK", bg_light((560, 560)), LOCK_BLACK[0])]
    for i, (n, bg, lg) in enumerate(tiles):
        x = 120 + i * 700
        t = put(bg, fit(lg, 460, 500), center=(280, 280))
        m = Image.new("L", (560, 560), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, 559, 559), radius=28, fill=255)
        img.paste(t, (x, 360), m)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 360, x + 560, 920), radius=28, outline=CYAN + (150,), width=3)
        img = text(img, n, (x + 280, 990), font("bahnschrift.ttf", 32), (60, 66, 74), track=6, anchor="center")
    img = text(img, "COLOUR", (124, 1110), font("bahnschrift.ttf", 38), CYAN_D, track=8)
    for i, (n, c) in enumerate((("Strike Cyan", CYAN), ("Pitch Navy", NAVY), ("Deep Blue", DEEP), ("Night", ABYSS), ("Pale", PALE))):
        x = 120 + i * 560
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 1160, x + 500, 1360), radius=22, fill=c + (255,), outline=(150, 150, 160, 255), width=2)
        img = text(img, n, (x, 1420), font("impact.ttf", 46), ABYSS)
        img = text(img, "#%02X%02X%02X   RGB %d %d %d" % (c + c), (x, 1470), font("segoeui.ttf", 30), (60, 66, 74))
    img = text(img, "TYPE", (124, 1580), font("bahnschrift.ttf", 38), CYAN_D, track=8)
    img = text(img, "Headings: Impact - strong, short, loud.", (120, 1670), font("impact.ttf", 72), ABYSS)
    img = text(img, "Body: Segoe UI.  Labels: Bahnschrift, wide-spaced capitals.", (120, 1750), font("segoeui.ttf", 46), (60, 66, 74))
    for i, t in enumerate(("Keep clear space equal to the ball's diameter around the crest.", "Minimum size: crest 24 px, full logo 120 px wide.", "Never stretch, rotate or recolour the crest.")):
        img = text(img, t, (1880, 1670 + i * 70), font("segoeui.ttf", 36), (60, 66, 74))
    img = text(img, "USE", (1884, 1610), font("bahnschrift.ttf", 38), CYAN_D, track=8)
    return grain(img, 5)


def main():
    em = crop_pad(emblem())
    wm = crop_pad(wordmark())
    wm_l = crop_pad(wordmark(dark=True))
    full_dark = crop_pad(lockup(em, wm), 0.04)       # light lettering, for dark backgrounds
    full = crop_pad(lockup(em, wm_l), 0.04)           # dark lettering, for light backgrounds
    em_mono = crop_pad(stencil(em, WHITE))
    save(fit(full, 2000, 2200), "football_logo.png", rgba=True)
    save(fit(em, 1500, 1700), "football_crest.png", rgba=True)
    save(fit(wm, 2400, 900), "football_wordmark.png", rgba=True)
    save(fit(crop_pad(lockup(stencil(em, WHITE), stencil(wm, WHITE)), 0.04), 2000, 2200), "football_logo_white.png", rgba=True)
    save(fit(crop_pad(lockup(stencil(em, (20, 20, 22)), stencil(wm_l, (20, 20, 22))), 0.04), 2000, 2200), "football_logo_black.png", rgba=True)
    save(put(bg_dark((2000, 2000), False), fit(full_dark, 1400, 1600), center=(1000, 1000), shadow_op=0.4), "football_logo_dark.png")
    save(avatar(em), "football_avatar.png")
    for s in (512, 192, 32):
        save(favicon(em, s), f"football_favicon_{s}.png", rgba=True)
    save(favicon(em, 64), "football_favicon.ico")
    for n, (W, H) in (("linkedin", (1584, 396)), ("twitter", (1500, 500)), ("facebook", (1640, 624)), ("youtube", (2560, 1440)), ("twitch", (2400, 960))):
        save(banner(W, H, em, wm), f"football_banner_{n}.png")
    save(banner(1200, 630, em, wm), "football_og_image.png")
    save(post(em, wm, "square"), "football_post_square.png")
    save(post(em, wm, "story"), "football_story.png")
    save(match_poster(em, wm), "football_match_day_poster.png")
    save(ticket(em, wm), "football_ticket.png")
    save(scarf(em), "football_scarf.png")
    f, b = card_pair(em, wm_l, full_dark)
    save(f, "football_business_card_front.png")
    save(b, "football_business_card_back.png")
    f.convert("RGB").save(OUT / "football_business_card.pdf", save_all=True, append_images=[b.convert("RGB")], resolution=300)
    lh = letterhead(em, wm_l)
    save(lh, "football_letterhead.png")
    lh.convert("RGB").save(OUT / "football_letterhead.pdf", resolution=300)
    save(signature(em), "football_email_signature.png")
    t, c = slides(em, wm_l, full_dark)
    save(t, "football_slide_title.png")
    save(c, "football_slide_content.png")
    LOCK_DARK[0] = full_dark
    LOCK_WHITE[0] = crop_pad(lockup(stencil(em, WHITE), stencil(wm, WHITE)), 0.04)
    LOCK_BLACK[0] = crop_pad(lockup(stencil(em, (20, 20, 22)), stencil(wm_l, (20, 20, 22))), 0.04)
    g = guidelines(em, wm_l, full)
    save(g, "football_brand_guidelines.png")
    g.convert("RGB").save(OUT / "football_brand_guidelines.pdf", resolution=200)
    print("done")


if __name__ == "__main__":
    main()

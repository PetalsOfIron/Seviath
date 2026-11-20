#!/usr/bin/env python3
"""Ornate Twitch design kit around the lavender-haired character (hand-inked portrait on a slate-blue gradient).
Name-free: no brand, generic labels only. Output: Documents/twitch/Lavender/
    Logo/, Banner/, Screens/ (4), Overlay/, Alerts/ (animated), Panels/ (8)
Ornaments (scrollwork corners, lavender sprigs, filigree dividers, sparkles, pearled ring) are drawn procedurally at 3x.
python tools/make_lavender_kit.py <path to the portrait image>"""
import math
import sys
import time as _t
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

_orig_save = Image.Image.save


def _safe_save(self, fp, *a, **k):
    """Windows sometimes refuses to overwrite a file that was just viewed: retry"""
    for i in range(8):
        try:
            return _orig_save(self, fp, *a, **k)
        except OSError:
            try:
                Path(fp).unlink()
            except Exception:
                pass
            _t.sleep(1.2)
    return _orig_save(self, fp, *a, **k)


Image.Image.save = _safe_save

SRC = Path(sys.argv[1])
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Lavender")
FD = "C:/Windows/Fonts/"
HEAD, BODY, UI = FD + "PRISTINA.TTF", FD + "Gabriola.ttf", FD + "candarab.ttf"
DEEP, SLATE, PERI, LAV = (26, 34, 54), (52, 68, 94), (138, 134, 184), (196, 192, 230)
PEACH, CREAM, SAGE = (240, 196, 170), (248, 240, 232), (150, 178, 170)

art = Image.open(SRC).convert("RGB").resize((2000, 2000), Image.LANCZOS)
FACE = (975, 800)


def font(p, s):
    return ImageFont.truetype(p, s)


def spaced(d, xy, text, f, fill, gap=0, anchor="l"):
    w = sum(f.getlength(c) for c in text) + gap * (len(text) - 1)
    x, y = xy
    x = x - w / 2 if anchor == "m" else (x - w if anchor == "r" else x)
    for c in text:
        d.text((x, y), c, font=f, fill=fill, anchor="lm")
        x += f.getlength(c) + gap
    return w


def diamond(d, c, r, fill, line=None):
    x, y = c
    d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=fill, outline=line)


# ------------------------------------------------------------------ ornament toolkit (all coordinates in output pixels)
def layer(w, h, fn, S=3):
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    fn(ImageDraw.Draw(big), S)
    return big.resize((w, h), Image.LANCZOS)


def taper(d, S, pts, w0, w1, fill):
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        r = (w0 + (w1 - w0) * i / max(1, n - 1)) * S / 2
        d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=fill)


def bez(p0, p1, p2, n=70):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def curl(o, ang, length, R, turns, side, wave=0.0):
    """a stroke that runs straight (with a gentle wave) and ends in a tightening spiral"""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy * side, dx * side
    n1 = int(length) + 8
    pts = []
    for i in range(n1 + 1):
        t = i / n1
        w = math.sin(t * math.pi * 2) * wave
        pts.append((o[0] + dx * length * t + nx * w, o[1] + dy * length * t + ny * w))
    ex, ey = pts[-1]
    cx, cy = ex + nx * R, ey + ny * R
    phi0 = math.atan2(-ny, -nx)
    n2 = int(R * turns * 6) + 24
    for i in range(1, n2 + 1):
        t = i / n2
        ph = phi0 + side * t * turns * 2 * math.pi
        r = R * (1 - 0.82 * t)
        pts.append((cx + r * math.cos(ph), cy + r * math.sin(ph)))
    return pts


def leaf(d, S, base, ang, length, width, fill):
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    left, right = [], []
    for i in range(21):
        t = i / 20
        w = math.sin(t * math.pi) * width * (1 - 0.2 * t)
        cx, cy = base[0] + dx * length * t, base[1] + dy * length * t
        left.append(((cx + nx * w) * S, (cy + ny * w) * S))
        right.append(((cx - nx * w) * S, (cy - ny * w) * S))
    d.polygon(left + right[::-1], fill=fill)


def pearl(d, S, c, r, fill, hi=CREAM):
    x, y = c
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=fill)
    d.ellipse([(x - r * 0.45) * S, (y - r * 0.55) * S, (x + r * 0.05) * S, (y - r * 0.05) * S], fill=hi)


def sparkle(d, S, c, r, fill):
    x, y = c
    pts = []
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rr = r if i % 2 == 0 else r * 0.22
        pts.append(((x + math.cos(a) * rr) * S, (y + math.sin(a) * rr) * S))
    d.polygon(pts, fill=fill)


def corner_flourish(d, S, c, sx, sy, size, col=PERI, acc=PEACH):
    """scrollwork corner: two curling arms, leaves, pearls and a diamond; (sx, sy) = direction pointing into the picture"""
    x, y = c
    wd = max(2.6, size * 0.040)
    arms = [(0.0 if sx > 0 else math.pi, sx * sy, size, size * 0.17),
            ((math.pi / 2) if sy > 0 else -math.pi / 2, -sx * sy, size * 0.80, size * 0.14)]
    for ang, side, ln, R in arms:
        pts = curl((x, y), ang, ln, R, 1.3, side, wave=size * 0.025)
        taper(d, S, pts, wd, wd * 0.35, col)
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy * side, dx * side
        for t, lf in ((0.38, 0.10), (0.62, 0.075)):
            bx, by = x + dx * ln * t, y + dy * ln * t
            leaf(d, S, (bx, by), math.atan2(dy + ny * 0.9, dx + nx * 0.9), size * lf * 1.5, size * lf * 0.5, LAV)
        for t in (0.2, 0.5, 0.78):
            pearl(d, S, (x + dx * ln * t - nx * size * 0.03, y + dy * ln * t - ny * size * 0.03), size * 0.024, acc)
    diamond(d, (x * S, y * S), size * 0.075 * S, acc, DEEP)


def sprig(d, S, base, ang, length, sway, bud=LAV, bud2=PERI, stem=SAGE):
    """a sprig of lavender"""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    p0 = base
    p2 = (base[0] + dx * length, base[1] + dy * length)
    p1 = ((p0[0] + p2[0]) / 2 + nx * sway, (p0[1] + p2[1]) / 2 + ny * sway)
    pts = bez(p0, p1, p2, int(length) + 10)
    taper(d, S, pts, max(2.4, length * 0.02), 1.2, stem)
    curve = bez(p0, p1, p2, 200)

    def at(t):
        i = min(198, int(t * 199))
        x, y = curve[i]
        x2, y2 = curve[i + 1]
        return (x, y), math.atan2(y2 - y, x2 - x)

    for t, side in ((0.17, 1), (0.27, -1)):
        pos, a = at(t)
        leaf(d, S, pos, a + side * 0.7, length * 0.20, length * 0.045, stem)
    for k in range(8):
        t = 0.40 + 0.58 * k / 7
        pos, a = at(t)
        sz = length * 0.115 * (1 - 0.40 * k / 7)
        for side in (-1, 1):
            leaf(d, S, pos, a + side * 0.62, sz, sz * 0.33, bud if k % 2 == 0 else bud2)
    pos, a = at(0.99)
    leaf(d, S, pos, a, length * 0.09, length * 0.03, bud)


def divider(d, S, c, half, col=PEACH, acc=LAV):
    """filigree divider: centre diamond, pearls, upward curls and fine lines running out"""
    x, y = c
    diamond(d, (x * S, y * S), 9 * S, col, DEEP)
    for sgn in (-1, 1):
        pearl(d, S, (x + sgn * 24, y), 4.2, col)
        pearl(d, S, (x + sgn * 38, y), 3.0, col)
        pts = curl((x + sgn * 46, y), 0.0 if sgn > 0 else math.pi, half * 0.22, 11, 1.2, -sgn, wave=2.2)
        taper(d, S, pts, 3.0, 1.2, col)
        d.line([((x + sgn * (half * 0.30 + 52)) * S, y * S), ((x + sgn * half) * S, y * S)], fill=col, width=int(2.4 * S))
        diamond(d, ((x + sgn * half) * S, y * S), 5 * S, acc)
        pearl(d, S, (x + sgn * (half * 0.30 + 52), y), 3.2, acc)


def ornate_frame(w, h, inset):
    def fn(d, S):
        d.rectangle([inset * S, inset * S, (w - inset) * S, (h - inset) * S], outline=PERI, width=int(3.4 * S))
        i2 = inset + 11
        d.rectangle([i2 * S, i2 * S, (w - i2) * S, (h - i2) * S], outline=PEACH, width=int(1.6 * S))
        size = h * 0.15
        for (x, y, sx, sy) in [(inset, inset, 1, 1), (w - inset, inset, -1, 1), (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
            corner_flourish(d, S, (x, y), sx, sy, size)
        for yy in (inset, h - inset):
            diamond(d, (w / 2 * S, yy * S), 10 * S, PEACH, DEEP)
            for sgn in (-1, 1):
                pearl(d, S, (w / 2 + sgn * 26, yy), 4.4, PEACH)
                pearl(d, S, (w / 2 + sgn * 42, yy), 3.2, LAV)
                d.line([((w / 2 + sgn * 54) * S, yy * S), ((w / 2 + sgn * h * 0.20) * S, yy * S)], fill=PEACH, width=int(2.2 * S))
        sprig(d, S, (inset + h * 0.030, h - inset - h * 0.03), -math.radians(93), h * 0.23, -h * 0.012)
        sprig(d, S, (inset + h * 0.052, h - inset - h * 0.03), -math.radians(87), h * 0.17, h * 0.010, bud=PERI, bud2=LAV)
    return layer(w, h, fn)


def sparkles_layer(w, h, spots):
    def fn(d, S):
        for fx, fy, r in spots:
            k = h / 1080
            sparkle(d, S, (fx * w, fy * h), r * k + 3, LAV)
            for ox, oy in ((1.8, -1.2), (-1.4, 1.5)):
                x, y = fx * w + ox * r * k, fy * h + oy * r * k
                d.ellipse([(x - 2) * S, (y - 2) * S, (x + 2) * S, (y + 2) * S], fill=PEACH)
    return layer(w, h, fn)


def cover_bg(w, h, ps, y0):
    """background without recognisable shapes: each row takes the colour of the artwork's left edge, plus film grain"""
    strip = art.crop((0, 0, 50, 2000)).resize((1, ps), Image.BOX)
    col = Image.new("RGB", (1, h))
    top, bot = strip.getpixel((0, 0)), strip.getpixel((0, ps - 1))
    for y in range(h):
        sy = y - y0
        col.putpixel((0, y), top if sy < 0 else (bot if sy >= ps else strip.getpixel((0, sy))))
    im = col.resize((w, h), Image.NEAREST).filter(ImageFilter.GaussianBlur(2))
    im = Image.blend(im, Image.effect_noise((w, h), 40).convert("RGB"), 0.05)
    return im.convert("RGBA")


def portrait(size):
    im = art.resize((size, size), Image.LANCZOS).convert("RGBA")
    fe, ft = int(size * 0.30), int(size * 0.10)
    left = Image.new("L", (size, size), 255)
    ld = ImageDraw.Draw(left)
    for x in range(fe):
        ld.line([(x, 0), (x, size)], fill=int(255 * (x / fe) ** 1.6))
    top = Image.new("L", (size, size), 255)
    td = ImageDraw.Draw(top)
    for y in range(ft):
        td.line([(0, y), (size, y)], fill=int(255 * (y / ft) ** 1.4))
    im.putalpha(ImageChops.multiply(left, top))
    return im


def shade_left(img, solid=0.30, fade=0.62, strength=185):
    w, h = img.size
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x in range(w):
        t = x / w
        a = strength if t <= solid else (int(strength * (1 - (t - solid) / (fade - solid))) if t < fade else 0)
        d.line([(x, 0), (x, h)], fill=DEEP + (a,))
    img.alpha_composite(lay)


SPARK_SCENE = [(0.60, 0.16, 12), (0.53, 0.60, 8), (0.64, 0.83, 10), (0.41, 0.11, 8), (0.075, 0.13, 8), (0.57, 0.40, 6), (0.33, 0.90, 7)]


def scene(w, h, lines, sub, label="live stream", size=None, with_portrait=True):
    if with_portrait:
        ps = int(h * 1.20)
        y0 = h - ps + int(ps * 0.20)
        img = cover_bg(w, h, ps, y0)
        img.alpha_composite(portrait(ps), (w - ps + int(ps * 0.06), y0))
    else:
        img = lav_bg(w, h)
        glow, bq = bouquet_scene(w, h)
        img.alpha_composite(glow)
        img.alpha_composite(bq)
    shade_left(img)
    img.alpha_composite(sparkles_layer(w, h, SPARK_SCENE))
    img.alpha_composite(ornate_frame(w, h, int(h * 0.034)))
    d = ImageDraw.Draw(img)
    big = size or int(h * 0.205)
    left = int(w * 0.075)
    cy = h * 0.5
    spaced(d, (left, cy - big * (len(lines) * 0.55) - 40), label, font(BODY, int(h * 0.052)), LAV + (255,), gap=2)
    y = cy - big * (len(lines) - 1) * 0.5 + 6
    for ln in lines:
        d.text((left + 3, y + 4), ln, font=font(HEAD, big), fill=DEEP + (170,), anchor="lm")
        d.text((left, y), ln, font=font(HEAD, big), fill=CREAM + (255,), anchor="lm")
        y += big * 0.98
    ly = y - big * 0.22
    hw = int(w * 0.17)
    img.alpha_composite(layer(w, h, lambda dd, S: divider(dd, S, (left + hw, ly), hw)))
    d = ImageDraw.Draw(img)
    if sub:
        spaced(d, (left, ly + int(h * 0.065)), sub, font(BODY, int(h * 0.056)), LAV + (255,), gap=2)
    return img


def logo_big(with_portrait=True):
    S = 4000
    c = S // 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([c - 1960, c - 1960, c + 1960, c + 1960], fill=LAV + (255,))
    d.ellipse([c - 1880, c - 1880, c + 1880, c + 1880], fill=DEEP + (255,))
    d.ellipse([c - 1860, c - 1860, c + 1860, c + 1860], outline=PEACH + (255,), width=14)
    inner = 1800
    if with_portrait:
        crop = art.crop((FACE[0] - 800, FACE[1] - 800, FACE[0] + 800, FACE[1] + 800)).resize((inner * 2, inner * 2), Image.LANCZOS).convert("RGBA")
    else:
        crop = Image.new("RGBA", (inner * 2, inner * 2))
        cd = ImageDraw.Draw(crop)
        for yy in range(inner * 2):
            t = yy / (inner * 2)
            cd.line([(0, yy), (inner * 2, yy)], fill=(int(70 - 30 * t), int(84 - 34 * t), int(118 - 44 * t), 255))
    m = Image.new("L", crop.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, crop.width - 1, crop.height - 1], fill=255)
    crop.putalpha(m)
    im.alpha_composite(crop, (c - inner, c - inner))
    d = ImageDraw.Draw(im)
    d.ellipse([c - inner, c - inner, c + inner, c + inner], outline=DEEP + (255,), width=10)
    for k in range(72):
        if k % 18 == 0:
            continue
        a = math.radians(k * 5)
        x, y = c + math.cos(a) * 1920, c + math.sin(a) * 1920
        big_p = (k % 6 == 0)
        pr = 34 if big_p else 17
        d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=(PEACH if big_p else PERI) + (255,))
    for ang in (0, 90, 180, 270):
        x, y = c + math.cos(math.radians(ang)) * 1920, c + math.sin(math.radians(ang)) * 1920
        diamond(d, (x, y), 130, PEACH + (255,), DEEP + (255,))
        diamond(d, (x, y), 52, DEEP + (255,))
    for ang in (45, 135, 225, 315):
        x, y = c + math.cos(math.radians(ang)) * 1920, c + math.sin(math.radians(ang)) * 1920
        sparkle(d, 1, (x, y), 120, PEACH + (255,))
    out = im.resize((2000, 2000), Image.LANCZOS)
    if not with_portrait:
        out.alpha_composite(bouquet_layer(2000, 2000, 1000, 1000, 880))
    return out


def x_profile(logo):
    card = Image.new("RGBA", (400, 400), DEEP + (255,))
    card.alpha_composite(logo.resize((372, 372), Image.LANCZOS), (14, 14))
    return card.convert("RGB")


def overlay():
    W, H = 1920, 1080
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    boxes = []

    def box(x, y, w, h, fill_a=0, label=None, r=22):
        if fill_a:
            d.rounded_rectangle([x, y, x + w, y + h], r, fill=DEEP + (fill_a,))
        d.rounded_rectangle([x, y, x + w, y + h], r, outline=PERI + (255,), width=6)
        d.rounded_rectangle([x + 10, y + 10, x + w - 10, y + h - 10], max(4, r - 8), outline=PEACH + (150,), width=2)
        boxes.append((x, y, w, h))
        if label:
            d.rounded_rectangle([x + 120, y - 18, x + 120 + 24 + len(label) * 15, y + 18], 12, fill=PERI + (255,))
            d.text((x + 132, y), label, font=font(UI, 22), fill=DEEP + (255,), anchor="lm")

    box(40, 40, 1440, 810)
    box(1520, 40, 360, 270, label="CAM")
    box(1520, 340, 360, 510, fill_a=170, label="CHAT")
    box(40, 890, 1840, 150, fill_a=175)
    for i, lab in enumerate(["LATEST FOLLOWER", "LATEST SUB", "TOP SUPPORTER"]):
        x = 120 + i * 600
        spaced(d, (x, 935), lab, font(UI, 26), LAV + (255,), gap=5)
        d.line([(x, 960), (x + 480, 960)], fill=PEACH + (200,), width=2)

    def orn(dd, S):
        for (x, y, w, h) in boxes:
            size = 130 if (w > 1000 and h > 400) else (78 if h < 200 else 92)
            for (cx, cy, sx, sy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
                corner_flourish(dd, S, (cx, cy), sx, sy, size)
        for xx in (660, 1260):
            diamond(dd, (xx * S, 965 * S), 10 * S, PEACH, DEEP)
            pearl(dd, S, (xx - 22, 965), 4, PEACH)
            pearl(dd, S, (xx + 22, 965), 4, PEACH)
        for t in (0.25, 0.5, 0.75):
            diamond(dd, ((40 + 1440 * t) * S, 40 * S), 7 * S, PEACH, DEEP)
            diamond(dd, ((40 + 1440 * t) * S, 850 * S), 7 * S, PEACH, DEEP)
        sprig(dd, S, (86, 1010), -math.radians(78), 70, 8, bud=LAV, bud2=PERI)
        sprig(dd, S, (1834, 1010), -math.radians(102), 70, -8, bud=LAV, bud2=PERI)
    im.alpha_composite(layer(W, H, orn))
    return im


def alert_frames(with_portrait=True):
    W, H = 900, 300
    logo = logo_big(with_portrait).resize((220, 220), Image.LANCZOS)
    S = 2
    big = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    bd.rounded_rectangle([20 * S, 40 * S, (W - 20) * S, (H - 20) * S], 36 * S, fill=DEEP + (255,))
    bd.rounded_rectangle([20 * S, 40 * S, (W - 20) * S, (H - 20) * S], 36 * S, outline=PERI + (255,), width=6 * S)
    bd.rounded_rectangle([32 * S, 52 * S, (W - 32) * S, (H - 32) * S], 28 * S, outline=PEACH + (170,), width=2 * S)
    panel = big.resize((W, H), Image.LANCZOS)
    panel.alpha_composite(logo, (50, 40))

    def orn(dd, SS):
        for (cx, cy, sx, sy) in [(300, 66, 1, 1), (W - 36, 58, -1, 1), (300, H - 38, 1, -1), (W - 36, H - 34, -1, -1)]:
            corner_flourish(dd, SS, (cx, cy), sx, sy, 56)
        divider(dd, SS, ((300 + W - 70) / 2, 190), (W - 70 - 300) / 2 - 20)
        for (fx, fy, r) in [(0.50, 0.30, 9), (0.80, 0.78, 7), (0.40, 0.83, 6)]:
            sparkle(dd, SS, (fx * W, fy * H), r, LAV)
    panel.alpha_composite(layer(W, H, orn))
    frames, n_in, n_hold, n_out = [], 12, 26, 10
    for i in range(n_in + n_hold + n_out):
        if i < n_in:
            t = i / (n_in - 1)
            off = int(-(1 - (1 - (1 - t) ** 3)) * 260)
        elif i < n_in + n_hold:
            off = 0
        else:
            t = (i - n_in - n_hold) / (n_out - 1)
            off = int(-(t ** 2) * 260)
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fr.alpha_composite(panel, (0, off))
        if n_in <= i < n_in + n_hold:
            k = (i - n_in) / (n_hold - 1)
            x = int(60 + k * (W - 200))
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sh)
            sd.polygon([(x, 50), (x + 40, 50), (x + 10, H - 30), (x - 30, H - 30)], fill=(255, 255, 255, 46))
            sh.putalpha(Image.composite(sh.split()[3], Image.new("L", (W, H), 0), panel.split()[3]))
            fr.alpha_composite(sh)
        frames.append(fr)
    return frames


def save_gif(frames, path, ms=55):
    out = []
    for f in frames:
        a = f.split()[3]
        p = f.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        p.paste(255, a.point(lambda v: 255 if v < 128 else 0))
        out.append(p)
    out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0, transparency=255, disposal=2)


def bouquet_layer(W, H, cx, cy, r):
    """a bouquet of lavender filling a round medallion of radius r (drawn for r = 120, scaled)"""
    k = r / 120.0

    def fn(d, S):
        base = (cx, cy + 100 * k)
        fan = [(-68, 118, 10, SAGE), (68, 118, -10, SAGE), (-46, 150, 12, None), (46, 150, -12, None),
               (-23, 176, -9, None), (23, 176, 9, None), (0, 192, 6, None)]
        for deg, ln, sw, col in fan:
            if col:
                sprig(d, S, base, math.radians(-90 + deg), ln * k, sw * k, bud=LAV, bud2=PERI)
            else:
                alt = (abs(deg) // 23) % 2 == 0
                sprig(d, S, base, math.radians(-90 + deg), ln * k, sw * k, bud=LAV if alt else PERI, bud2=PERI if alt else LAV)
        for sgn in (-1, 1):
            pts = bez((cx, cy + 96 * k), (cx + sgn * 34 * k, cy + 70 * k), (cx + sgn * 40 * k, cy + 100 * k), 60)
            taper(d, S, pts, 9 * k, 9 * k, PEACH)
            pts2 = bez((cx, cy + 98 * k), (cx + sgn * 14 * k, cy + 130 * k), (cx + sgn * 30 * k, cy + 150 * k), 40)
            taper(d, S, pts2, 6 * k, 3 * k, PEACH)
        pearl(d, S, (cx, cy + 97 * k), 8 * k, PEACH)
        for (fx, fy, rr) in [(-78, -52, 9), (80, -40, 8), (62, 64, 6), (-70, 54, 6)]:
            sparkle(d, S, (cx + fx * k, cy + fy * k), rr * k, CREAM)
    lay = layer(W, H, fn, S=3 if W * H < 4e6 else 2)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], fill=255)
    lay.putalpha(ImageChops.multiply(lay.split()[3], mask))
    return lay


def bouquet_scene(w, h):
    """a large lavender bouquet that takes the place of the portrait on the right of screens and banners"""
    cx = int(w * 0.775)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - h * 0.62, h * 0.50 - h * 0.62, cx + h * 0.62, h * 0.50 + h * 0.62], fill=PERI + (90,))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.10))

    def fn(d, S):
        base = (cx, h * 1.04)
        spec = [(-62, 0.58, 18, SAGE), (62, 0.58, -18, SAGE), (-46, 0.70, 14, None), (46, 0.70, -14, None),
                (-31, 0.80, -12, None), (31, 0.80, 12, None), (-15, 0.88, 10, None), (15, 0.88, -10, None), (0, 0.93, 8, None)]
        for deg, ln, sw, col in spec:
            L = h * ln
            if col:
                sprig(d, S, base, math.radians(-90 + deg), L, sw * h / 500, bud=LAV, bud2=PERI)
            else:
                alt = (abs(deg) // 15) % 2 == 0
                sprig(d, S, base, math.radians(-90 + deg), L, sw * h / 500, bud=LAV if alt else PERI, bud2=PERI if alt else LAV)
    return glow, layer(w, h, fn, S=2)


def lav_bg(w, h):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(SLATE[i] * (1 - t * 0.85) + DEEP[i] * t * 0.85) for i in range(3)))
    im = Image.blend(im, Image.effect_noise((w, h), 40).convert("RGB"), 0.04)
    return im.convert("RGBA")


def panel_img(title, portrait=True):
    W, H, K = 1280, 400, 2
    im = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    g = Image.new("RGBA", (1, H * K))
    for y in range(H * K):
        t = y / (H * K)
        g.putpixel((0, y), tuple(int(SLATE[i] * (1 - t) + DEEP[i] * t) for i in range(3)) + (255,))
    g = g.resize((W * K, H * K))
    m = Image.new("L", (W * K, H * K), 0)
    ImageDraw.Draw(m).rounded_rectangle([14 * K, 14 * K, (W - 14) * K, (H - 14) * K], 150 * K, fill=255)
    im.paste(g, (0, 0), m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14 * K, 14 * K, (W - 14) * K, (H - 14) * K], 150 * K, outline=PERI + (255,), width=8 * K)
    d.rounded_rectangle([30 * K, 30 * K, (W - 30) * K, (H - 30) * K], 136 * K, outline=PEACH + (170,), width=3 * K)
    cx, cy, r = 200 * K, 200 * K, 120 * K
    d.ellipse([cx - r - 20 * K, cy - r - 20 * K, cx + r + 20 * K, cy + r + 20 * K], fill=LAV + (255,))
    if portrait:
        crop = art.crop((FACE[0] - 760, FACE[1] - 760, FACE[0] + 760, FACE[1] + 760)).resize((2 * r, 2 * r), Image.LANCZOS).convert("RGBA")
        mm = Image.new("L", crop.size, 0)
        ImageDraw.Draw(mm).ellipse([0, 0, crop.width - 1, crop.height - 1], fill=255)
        crop.putalpha(mm)
        im.alpha_composite(crop, (cx - r, cy - r))
    else:                                              # plain deep disc, the bouquet is drawn on it below
        g2 = Image.new("RGBA", (2 * r, 2 * r))
        gd = ImageDraw.Draw(g2)
        for yy in range(2 * r):
            t = yy / (2 * r)
            gd.line([(0, yy), (2 * r, yy)], fill=(int(70 - 30 * t), int(84 - 34 * t), int(118 - 44 * t), 255))
        mm = Image.new("L", g2.size, 0)
        ImageDraw.Draw(mm).ellipse([0, 0, g2.width - 1, g2.height - 1], fill=255)
        g2.putalpha(mm)
        im.alpha_composite(g2, (cx - r, cy - r))
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=DEEP + (255,), width=5 * K)
    for k in range(36):
        a = math.radians(k * 10)
        x, y = cx + math.cos(a) * (r + 10 * K), cy + math.sin(a) * (r + 10 * K)
        pr = (5 if k % 3 == 0 else 3) * K
        d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=(PEACH if k % 3 == 0 else PERI) + (255,))
    f = font(HEAD, (170 if len(title) < 9 else 140) * K)
    tx, ty = 800 * K, 170 * K
    d.text((tx + 4 * K, ty + 5 * K), title, font=f, fill=DEEP + (200,), anchor="mm")
    d.text((tx, ty), title, font=f, fill=CREAM + (255,), anchor="mm")
    small = im.resize((W, H), Image.LANCZOS)

    def orn(dd, S):
        divider(dd, S, (800, 292), 270)
        for (cx2, cy2, sx, sy) in [(1130, 62, -1, 1), (1130, 338, -1, -1), (470, 62, 1, 1), (470, 338, 1, -1)]:
            corner_flourish(dd, S, (cx2, cy2), sx, sy, 62)
        sprig(dd, S, (300, 120), -math.radians(52), 118, 14, bud=LAV, bud2=PERI)
        sprig(dd, S, (118, 118), -math.radians(128), 100, -12, bud=LAV, bud2=PERI)
        for (fx, fy, rr) in [(0.43, 0.20, 9), (0.90, 0.30, 11), (0.88, 0.78, 8), (0.36, 0.82, 7)]:
            sparkle(dd, S, (fx * W, fy * H), rr, LAV)
    small.alpha_composite(layer(W, H, orn))
    if not portrait:
        small.alpha_composite(bouquet_layer(W, H, 200, 200, 120))
    return small


def main():
    # remove the earlier, simpler version first (the folder is rebuilt from scratch)
    import shutil
    for sub in ("Logo", "Banner", "Screens", "Overlay", "Alerts", "Panels"):
        shutil.rmtree(OUT / sub, ignore_errors=True)
    for f in ("preview_board.png",):
        try:
            (OUT / f).unlink()
        except Exception:
            pass
    for sub in ("Logo", "Banner", "Screens", "Overlay", "Alerts", "Panels", "Source"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    art.save(OUT / "Source" / "character_2000.png", optimize=True)
    lg = logo_big()
    lg.save(OUT / "Logo" / "lavender_logo.png", optimize=True)
    x_profile(lg).save(OUT / "Logo" / "x_profile_400.png", optimize=True)
    scene(1200, 480, ["Live Stream"], "gaming  ·  art  ·  chat", label="welcome", size=118).convert("RGB").save(OUT / "Banner" / "profile_banner_1200x480.png", optimize=True)
    scene(1500, 500, ["Live Stream"], "gaming  ·  art  ·  chat", label="welcome", size=122).convert("RGB").save(OUT / "Banner" / "x_header_1500x500.png", optimize=True)
    screens = {"starting_soon": (["Starting", "Soon"], "the stream begins shortly"),
               "be_right_back": (["Be Right", "Back"], "back in a moment"),
               "offline": (["Stream", "Offline"], "see you next time"),
               "ending": (["Thanks for", "Watching"], "see you next stream")}
    for k, (lines, sub) in screens.items():
        scene(1920, 1080, lines, sub).convert("RGB").save(OUT / "Screens" / f"{k}.png", optimize=True)
    overlay().save(OUT / "Overlay" / "overlay_1920x1080.png", optimize=True)
    fr = alert_frames()
    save_gif(fr, OUT / "Alerts" / "alert.gif")
    fr[14].save(OUT / "Alerts" / "alert_still.png")
    (OUT / "Panels_lavender_only").mkdir(exist_ok=True)
    for t in ["About Me", "Schedule", "Chat Rules", "FAQ", "Links", "PC Setup", "Socials", "Support"]:
        panel_img(t).save(OUT / "Panels" / (t.lower().replace(" ", "_") + ".png"), optimize=True)
        panel_img(t, portrait=False).save(OUT / "Panels_lavender_only" / (t.lower().replace(" ", "_") + ".png"), optimize=True)
    O2 = OUT / "Lavender_only"
    shutil.rmtree(O2, ignore_errors=True)
    for sub in ("Logo", "Banner", "Screens", "Overlay", "Alerts", "Panels"):
        (O2 / sub).mkdir(parents=True, exist_ok=True)
    lg2 = logo_big(False)
    lg2.save(O2 / "Logo" / "lavender_logo.png", optimize=True)
    x_profile(lg2).save(O2 / "Logo" / "x_profile_400.png", optimize=True)
    scene(1200, 480, ["Live Stream"], "gaming  ·  art  ·  chat", label="welcome", size=118, with_portrait=False).convert("RGB").save(O2 / "Banner" / "profile_banner_1200x480.png", optimize=True)
    scene(1500, 500, ["Live Stream"], "gaming  ·  art  ·  chat", label="welcome", size=122, with_portrait=False).convert("RGB").save(O2 / "Banner" / "x_header_1500x500.png", optimize=True)
    for k, (lines, sub) in screens.items():
        scene(1920, 1080, lines, sub, with_portrait=False).convert("RGB").save(O2 / "Screens" / f"{k}.png", optimize=True)
    overlay().save(O2 / "Overlay" / "overlay_1920x1080.png", optimize=True)
    fr2 = alert_frames(False)
    save_gif(fr2, O2 / "Alerts" / "alert.gif")
    fr2[14].save(O2 / "Alerts" / "alert_still.png")
    for t in ["About Me", "Schedule", "Chat Rules", "FAQ", "Links", "PC Setup", "Socials", "Support"]:
        panel_img(t, portrait=False).save(O2 / "Panels" / (t.lower().replace(" ", "_") + ".png"), optimize=True)
    print("done", OUT)


if __name__ == "__main__":
    main()

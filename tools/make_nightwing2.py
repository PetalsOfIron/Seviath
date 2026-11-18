#!/usr/bin/env python3
"""Nightwing kit, round 2: chibi expression emotes and a new logo built on the character's real wings."""
import math
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import make_nightwing as nw
from make_nightwing import *  # noqa: F401,F403

K = 3
SKIN = (248, 232, 224)
SKIN_D = (226, 186, 182)
HAIR = (152, 40, 68)
HAIR_D = (92, 22, 46)
HAIR_L = (212, 90, 112)
HORN = (104, 150, 222)
HORN_L = (178, 212, 248)
LINE = (30, 16, 42)
RED = (206, 44, 76)
EYE_A = (58, 140, 160)
EYE_B = (150, 226, 230)
RIB = (70, 80, 168)


def sm(pts, n=8):
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * ((2 * p[i][k]) + (-p[i - 1][k] + p[i + 1][k]) * t + (2 * p[i - 1][k] - 5 * p[i][k] + 4 * p[i + 1][k] - p[i + 2][k]) * t * t + (-p[i - 1][k] + 3 * p[i][k] - 3 * p[i + 1][k] + p[i + 2][k]) * t ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def mir(pts):
    return [(448 - x, y) for x, y in pts]


class Pen:
    def __init__(self, S=448):
        self.S = S
        self.im = Image.new("RGBA", (S * K, S * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def poly(self, pts, fill, outline=None, w=0, smooth=False):
        pts = sm(pts) if smooth else pts
        self.d.polygon(self.p(pts), fill=fill + (255,))
        if outline:
            self.d.line(self.p(pts + [pts[0]]), fill=outline + (255,), width=int(w * K), joint="curve")

    def ell(self, cx, cy, rx, ry, fill, outline=None, w=0):
        self.d.ellipse(((cx - rx) * K, (cy - ry) * K, (cx + rx) * K, (cy + ry) * K), fill=fill + (255,) if fill else None, outline=(outline + (255,)) if outline else None, width=int(w * K))

    def line(self, pts, col, w, smooth=False):
        pts = sm(pts) if smooth else pts
        self.d.line(self.p(pts), fill=col + (255,), width=int(w * K), joint="curve")
        r = w * K / 2
        for x, y in (self.p(pts)[0], self.p(pts)[-1]):
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,))

    def arc(self, cx, cy, rx, ry, a0, a1, col, w):
        pts = [(cx + math.cos(math.radians(a)) * rx, cy + math.sin(math.radians(a)) * ry) for a in [a0 + (a1 - a0) * i / 24 for i in range(25)]]
        self.line(pts, col, w)

    def heart(self, cx, cy, r, fill, outline=LINE):
        pts = []
        for i in range(120):
            t = math.pi * 2 * i / 120
            pts.append((cx + 16 * math.sin(t) ** 3 * r / 16, cy - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * r / 16))
        self.poly(pts, fill, outline, 3)

    def text(self, s, x, y, size, col):
        f = ImageFont.truetype(str(FONTS / HEAD), int(size * K))
        self.d.text((x * K, y * K), s, font=f, fill=col + (255,), anchor="mm", stroke_width=int(3 * K), stroke_fill=LINE + (255,))

    def done(self):
        return self.im.resize((self.S, self.S), Image.LANCZOS)


def eye_open(pen, cx, cy, rx=36, ry=42, pupil=1.0, look=0):
    pen.ell(cx, cy, rx, ry, (255, 255, 255), LINE, 3.5)
    pen.ell(cx + look, cy + 4, rx * 0.72, ry * 0.8, EYE_A)
    pen.ell(cx + look, cy + 14, rx * 0.64, ry * 0.5, EYE_B)
    pen.ell(cx + look, cy + 2, rx * 0.34 * pupil, ry * 0.4 * pupil, (20, 24, 44))
    pen.ell(cx + look - rx * 0.28, cy - ry * 0.28, rx * 0.2, rx * 0.2, (255, 255, 255))
    pen.ell(cx + look + rx * 0.26, cy + ry * 0.3, rx * 0.1, rx * 0.1, (255, 255, 255))
    pen.arc(cx, cy + 3, rx + 2, ry + 2, 196, 344, LINE, 7)


def brow(pen, x0, y0, x1, y1, w=6):
    pen.line([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 3), (x1, y1)], HAIR_D, w, smooth=True)


def mouth_open(pen, cx, cy, w, h):
    pen.d.pieslice(((cx - w) * K, (cy - h) * K, (cx + w) * K, (cy + h) * K), 0, 180, fill=(120, 20, 44, 255), outline=LINE + (255,), width=int(3.5 * K))
    pen.ell(cx, cy + h * 0.55, w * 0.52, h * 0.34, (240, 110, 124))
    pen.line([(cx - w, cy), (cx + w, cy)], LINE, 4)


def blush(pen, a=0.0, big=1.0):
    for cx in (110, 338):
        pen.ell(cx, 298, 28 * big, 14 * big, (246, 128, 140))


def chibi(expr):
    pen = Pen()
    # back hair
    pen.poly(sm([(224, 62), (330, 88), (372, 170), (386, 270), (400, 372), (372, 418), (338, 380), (318, 330), (130, 330), (110, 380), (76, 418), (48, 372), (62, 270), (76, 170), (118, 88)]), HAIR, LINE, 4)
    for x in (80, 100, 346, 366):
        pen.line([(x, 250), (x - 6 if x < 224 else x + 6, 330), (x - 2 if x < 224 else x + 2, 392)], HAIR_D, 4, smooth=True)
    # horns
    for sgn in (1, -1):
        def P(x, y):
            return (224 + sgn * (x - 224), y)
        d = pen.d
        for w, col, off in ((46, LINE, 0), (36, HORN, 0), (13, HORN_L, -4)):
            nw.blade(d, tuple(v * K for v in P(150, 112 + off)), tuple(v * K for v in P(96, 4 + off)), tuple(v * K for v in P(18, 56 + off)), w * K, col + (255,))
    # ears
    for pts in ([(112, 238), (34, 184), (18, 168), (104, 276)], [(336, 238), (414, 184), (430, 168), (344, 276)]):
        pen.poly(pts, SKIN, LINE, 4, smooth=True)
    pen.poly([(106, 244), (52, 196), (112, 258)], SKIN_D)
    pen.poly([(342, 244), (396, 196), (336, 258)], SKIN_D)
    # face
    pen.ell(224, 250, 130, 112, SKIN, LINE, 4)
    pen.ell(224, 330, 80, 22, SKIN_D)
    pen.ell(224, 246, 126, 108, SKIN)
    # fringe (parted)
    left = [(224, 98), (156, 110), (108, 160), (96, 240), (132, 206), (170, 192), (206, 154)]
    pen.poly(left, HAIR, LINE, 4, smooth=True)
    pen.poly(mir(left), HAIR, LINE, 4, smooth=True)
    for pts in ([(190, 112), (150, 150), (130, 196)], [(158, 108), (118, 170), (110, 214)]):
        pen.line(pts, HAIR_L, 3.5, smooth=True)
        pen.line(mir(pts), HAIR_L, 3.5, smooth=True)
    # circlet-ish blue ribbon
    for sgn in (1, -1):
        def Q(x, y):
            return (224 + sgn * (x - 224), y)
        pen.line([Q(150, 104), Q(166, 94), Q(184, 96)], RIB, 7, smooth=True)
    # expressions
    L, R = 160, 288
    EY = 262
    if expr == "happy":
        pen.arc(L, EY + 10, 34, 34, 200, 340, LINE, 8)
        pen.arc(R, EY + 10, 34, 34, 200, 340, LINE, 8)
        mouth_open(pen, 224, 316, 38, 36)
        blush(pen)
        brow(pen, 130, 218, 190, 214)
        brow(pen, 258, 214, 318, 218)
    elif expr == "love":
        pen.heart(L, EY + 2, 44, (244, 70, 110))
        pen.heart(R, EY + 2, 44, (244, 70, 110))
        pen.ell(L - 10, EY - 12, 8, 8, (255, 255, 255))
        pen.ell(R - 10, EY - 12, 8, 8, (255, 255, 255))
        pen.arc(224, 308, 30, 22, 20, 160, LINE, 6)
        blush(pen, big=1.2)
        pen.heart(380, 120, 26, (246, 100, 132))
        pen.heart(60, 96, 18, (246, 100, 132))
    elif expr == "cry":
        eye_open(pen, L, EY, 38, 44, 1.2)
        eye_open(pen, R, EY, 38, 44, 1.2)
        brow(pen, 126, 226, 190, 206)
        brow(pen, 258, 206, 322, 226)
        for cx in (L - 8, R + 8):
            pen.poly([(cx - 10, EY + 36), (cx + 10, EY + 36), (cx + 16, 380), (cx - 16, 380)], (140, 210, 255), None, smooth=False)
            pen.ell(cx, 384, 18, 14, (140, 210, 255))
            pen.line([(cx - 5, EY + 40), (cx - 8, 360)], (230, 246, 255), 4)
        pen.line([(194, 328), (210, 316), (238, 316), (254, 328)], LINE, 6, smooth=True)
        pen.ell(224, 330, 0.1, 0.1, LINE)
    elif expr == "angry":
        for cx, sg in ((L, 1), (R, -1)):
            pen.ell(cx, EY + 6, 34, 34, (255, 255, 255), LINE, 3.5)
            pen.ell(cx, EY + 10, 22, 24, EYE_A)
            pen.ell(cx, EY + 10, 11, 13, (20, 24, 44))
            pen.ell(cx - 7, EY, 6, 6, (255, 255, 255))
        pen.poly([(L - 44, EY - 44), (L + 44, EY - 4), (L + 44, EY - 52), (L - 44, EY - 62)], SKIN)
        pen.poly([(R + 44, EY - 44), (R - 44, EY - 4), (R - 44, EY - 52), (R + 44, EY - 62)], SKIN)
        pen.line([(L - 46, EY - 28), (L + 46, EY - 4)], LINE, 8)
        pen.line([(R + 46, EY - 28), (R - 46, EY - 4)], LINE, 8)
        brow(pen, L - 50, EY - 44, L + 40, EY - 16, 8)
        brow(pen, R + 50, EY - 44, R - 40, EY - 16, 8)
        pen.line([(192, 326), (208, 314), (240, 314), (256, 326)], LINE, 6, smooth=True)
        for dx, dy in ((0, 0), (14, 8)):
            pen.line([(340 + dx, 128 + dy), (356 + dx, 112 + dy)], (230, 40, 60), 7)
            pen.line([(340 + dx, 112 + dy), (356 + dx, 128 + dy)], (230, 40, 60), 7)
        pen.ell(110, 298, 24, 12, (234, 90, 110))
        pen.ell(338, 298, 24, 12, (234, 90, 110))
    elif expr == "smug":
        for cx in (L, R):
            eye_open(pen, cx, EY, 36, 42, 1.0, look=6)
            pen.poly([(cx - 42, EY - 48), (cx + 42, EY - 48), (cx + 42, EY - 4), (cx - 42, EY - 4)], SKIN)
            pen.line([(cx - 40, EY - 4), (cx + 40, EY - 4)], LINE, 8)
            pen.arc(cx, EY - 6, 40, 14, 190, 350, LINE, 5)
        brow(pen, 126, 214, 190, 204)
        brow(pen, 258, 200, 322, 212)
        pen.line([(184, 322), (224, 328), (270, 306)], LINE, 7, smooth=True)
        pen.poly([(262, 308), (286, 296), (278, 316)], (246, 246, 246), LINE, 3)
        blush(pen, big=0.8)
    elif expr == "wink":
        eye_open(pen, L, EY, 38, 44)
        pen.line([(R - 32, EY - 16), (R + 24, EY + 4), (R - 32, EY + 24)], LINE, 8, smooth=True)
        mouth_open(pen, 224, 314, 32, 30)
        pen.poly([(238, 332), (262, 332), (258, 360), (242, 360)], (240, 110, 124), LINE, 3)
        blush(pen)
        brow(pen, 130, 212, 190, 204)
        brow(pen, 258, 200, 318, 204)
        pen.text("*", 388, 130, 56, (255, 220, 120))
    elif expr == "sleep":
        pen.arc(L, EY - 4, 32, 24, 20, 160, LINE, 8)
        pen.arc(R, EY - 4, 32, 24, 20, 160, LINE, 8)
        pen.ell(224, 322, 12, 14, (230, 110, 126), LINE, 3.5)
        blush(pen, big=0.9)
        brow(pen, 130, 222, 190, 220, 5)
        brow(pen, 258, 220, 318, 222, 5)
        pen.ell(300, 330, 0, 0, LINE)
        pen.text("Z", 376, 132, 54, (255, 255, 255))
        pen.text("z", 408, 92, 36, (255, 255, 255))
        pen.text("z", 346, 84, 28, (255, 255, 255))
    elif expr == "shock":
        eye_open(pen, L, EY, 40, 48, 0.55)
        eye_open(pen, R, EY, 40, 48, 0.55)
        brow(pen, 126, 202, 190, 192)
        brow(pen, 258, 192, 322, 202)
        pen.ell(224, 332, 26, 34, (120, 20, 44), LINE, 4)
        pen.ell(224, 346, 16, 14, (240, 110, 124))
        pen.poly([(378, 150), (396, 190), (360, 190)], (140, 210, 255), LINE, 3)
        pen.ell(378, 192, 18, 18, (140, 210, 255), LINE, 3)
        pen.line([(100, 120), (84, 90)], (255, 214, 110), 6)
        pen.line([(348, 108), (362, 82)], (255, 214, 110), 6)
    im = nw.outlined(pen.done(), None, 12)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sm_ = im.resize((int(im.width * 0.88), int(im.height * 0.88)), Image.LANCZOS)
    out.alpha_composite(sm_, ((im.width - sm_.width) // 2, int(im.height * 0.09)))
    return out


EXPR = ["happy", "love", "cry", "angry", "smug", "wink", "sleep", "shock"]


def new_logo(art, S=2000):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx, cy, R = S // 2, 880, 600
    d = ImageDraw.Draw(img)
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40), fill=255)
    img = shadow(img, m, (0, 20), 30, (0, 0, 0), 0.6)
    d = ImageDraw.Draw(img)
    for r, col in ((R + 40, DEEP), (R + 30, AMBER), (R + 18, AMBER_D), (R + 10, DEEP)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
    disc = radial((2 * R, 2 * R), (96, 78, 188), (24, 16, 56), 0.5, 0.4, 0.9).convert("RGBA")
    dm = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(dm).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
    disc.putalpha(dm)
    img.alpha_composite(disc, (cx - R, cy - R))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R + 22, cy - R + 22, cx + R - 22, cy + R - 22), outline=SILVER + (255,), width=5)
    for k in range(24):
        a = math.radians(k * 15)
        diamond(d, cx + math.cos(a) * (R - 22), cy + math.sin(a) * (R - 22), 7 if k % 3 else 12, AMBER + (255,))
    # her own wings and bust, breaking out of the plate
    crop = art.crop((20, 60, 980, 830))
    sc = 1.78
    crop = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
    fade = Image.new("L", crop.size, 255)
    fd = ImageDraw.Draw(fade)
    for y in range(crop.height):
        t = y / crop.height
        v = 255 if t < 0.66 else int(255 * max(0, 1 - (t - 0.66) / 0.17) ** 1.3)
        fd.line([(0, y), (crop.width, y)], fill=v)
    crop.putalpha(ImageChops.multiply(crop.split()[3], fade))
    px, py = cx - int((505 - 20) * sc), cy - 560 + int(-70)
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    lay.alpha_composite(crop, (px, py))
    img = shadow(img, lay.split()[3], (0, 16), 22, (0, 0, 0), 0.55)
    img = Image.alpha_composite(img, lay)
    if nw.LOGO_TEXT:
        # name ribbon
        rb = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rb)
        y0, y1 = 1570, 1760
        rd.polygon([(250, y0), (S - 250, y0), (S - 190, (y0 + y1) / 2), (S - 250, y1), (250, y1), (190, (y0 + y1) / 2)], fill=DEEP + (255,))
        img = shadow(img, rb.split()[3], (0, 12), 16, (0, 0, 0), 0.55)
        rd.polygon([(250, y0), (S - 250, y0), (S - 190, (y0 + y1) / 2), (S - 250, y1), (250, y1), (190, (y0 + y1) / 2)], outline=AMBER + (255,), width=7)
        rd.polygon([(268, y0 + 16), (S - 268, y0 + 16), (S - 214, (y0 + y1) / 2), (S - 268, y1 - 16), (268, y1 - 16), (214, (y0 + y1) / 2)], outline=INDIGO + (255,), width=4)
        img = Image.alpha_composite(img, rb)
        img, _ = fit_title(img, NAME, (S // 2, 1706), 1260, size=130, anchor="center", track=14)
    return img


def main():
    art = nw.cutout(nw.ART)
    em = nw.OUT / "Emotes"
    if em.exists():
        shutil.rmtree(em)
    for n in EXPR:
        im = chibi(n)
        for s in (112, 56, 28):
            save(im.resize((s, s), Image.LANCZOS), "Emotes", "nw_%s_%d.png" % (n, s))
        save(im, "Emotes", "nw_%s_448.png" % n)
    heart = nw.emote_heart()
    gg = nw.emote_text("GG", AMBER, AMBER_D)
    for n, im in (("heart", heart), ("gg", gg), ("gem", nw.emote_gem())):
        for s in (112, 56, 28):
            save(im.resize((s, s), Image.LANCZOS), "Emotes", "nw_%s_%d.png" % (n, s))
    logo = new_logo(art)
    save(logo, "Logo", "nightwing_logo.png")
    # round avatar from the face
    save(nw.emblem(art, 1000), "Logo", "nightwing_avatar.png")
    ch = OUT / "ChannelPoints"
    for n, im in (("happy", chibi("happy")), ("love", chibi("love")), ("smug", chibi("smug"))):
        save(im.resize((112, 112), Image.LANCZOS), "ChannelPoints", n + ".png")
    for f in (OUT / "Logo" / "nightwing_emblem.png", ch / "gem.png", ch / "heart.png", ch / "wing.png"):
        if f.exists():
            f.unlink()
    print("done")


if __name__ == "__main__":
    main()

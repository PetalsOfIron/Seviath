#!/usr/bin/env python3
"""Every missing company piece, each company in its OWN style (not one template recoloured):
  Northbeam  night-sky beams, silver gothic title, cyan corner brackets, centred
  Tessel     bold diagonal sport: slanted blocks, huge condensed caps, left aligned, lime accent
  Perfum     elegant luxury: blush, double thin gold frame, italic serif, centred ornaments
  Strikeline scoreboard: navy, horizontal stripe bands, bold sans caps, boxed numbers
Writes Documents/twitch/Missing/<Kit>/ (posters, invoice, envelope, thank-you card, name badge, voucher, sticker, ticket, tag, app icon).
    python tools/make_company_styles.py"""
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DES = ROOT / "images" / "design"
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Missing")
FT = "C:/Windows/Fonts/"
SANS, IMPACT, GEO, TIMESI, TIMES, TIMESBD = FT + "bahnschrift.ttf", FT + "impact.ttf", FT + "georgiab.ttf", FT + "timesi.ttf", FT + "times.ttf", FT + "timesbd.ttf"
GEOR = FT + "georgia.ttf"


def F(p, s):
    f = ImageFont.truetype(p, s)
    if p == SANS:
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f


def lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def logo(brand, kind):
    names = {"white": ("logo_white", "logo"), "black": ("logo_black", "logo"), "color": ("logo",)}[kind]
    for n in names:
        p = DES / brand / f"{brand.lower()}_{n}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")


def fit(img, im, box, anchor="c"):
    x, y, w, h = box
    k = min(w / im.width, h / im.height)
    t = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    px = x if anchor[0] == "l" else x + (w - t.width) // 2
    py = y if anchor[1] == "t" else y + (h - t.height) // 2
    img.alpha_composite(t, (px, py))


def grad(w, h, top, bot):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bot, y / h))
    return im.convert("RGBA")


def lay(w, h, fn, blur=0):
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fn(ImageDraw.Draw(l))
    return l.filter(ImageFilter.GaussianBlur(blur)) if blur else l


# ---------------------------------------------------------------------------- styles
class Style:
    pass


def northbeam():
    s = Style()
    s.name, s.brand, s.align, s.logo_kind = "Northbeam", "Northbeam", "c", "color"
    s.top, s.bot, s.acc, s.ink, s.dark_bg = (46, 66, 150), (14, 20, 62), (120, 226, 240), (246, 248, 255), True
    s.tfont, s.caps = GEO, False
    s.site, s.mail = "NORTHBEAM.EXAMPLE", "hello@northbeam.example"

    def bg(w, h):
        im = grad(w, h, s.top, s.bot)
        im.alpha_composite(lay(w, h, lambda d: [d.polygon([(x - 60, 0), (x + 60, 0), (x + 420, h * .75), (x - 420, h * .75)], fill=(160, 210, 255, 26)) for x in range(int(w * .2), w, int(w * .17))], 40 * w // 2480))
        im.alpha_composite(lay(w, h, lambda d: d.ellipse([w * .2, h * .2, w * .8, h * .65], fill=(110, 160, 255, 60)), 200 * w // 2480))
        return im

    def frame(im):
        w, h = im.size
        m, L = int(w * .06), int(w * .1)
        d = ImageDraw.Draw(im)
        for sx in (m, w - m):
            for sy in (m, h - m):
                dx, dy = (L if sx < w / 2 else -L), (L if sy < h / 2 else -L)
                d.line([(sx, sy), (sx + dx, sy)], fill=s.acc, width=max(3, w // 250))
                d.line([(sx, sy), (sx, sy + dy)], fill=s.acc, width=max(3, w // 250))

    def rule(d, cx, y, wd):
        d.line([(cx - wd // 2, y), (cx - 50, y)], fill=s.acc, width=6)
        d.line([(cx + 50, y), (cx + wd // 2, y)], fill=s.acc, width=6)
        d.polygon([(cx, y - 22), (cx + 22, y), (cx, y + 22), (cx - 22, y)], fill=s.acc)
    s.bg, s.frame, s.rule = bg, frame, rule
    s.paper = (255, 255, 255)
    return s


def tessel():
    s = Style()
    s.name, s.brand, s.align, s.logo_kind = "Tessel", "Tessel", "l", "white"
    s.top, s.bot, s.acc, s.ink, s.dark_bg = (22, 70, 46), (6, 24, 16), (190, 255, 70), (255, 255, 255), True
    s.tfont, s.caps = IMPACT, True
    s.site, s.mail = "TESSEL.EXAMPLE", "hello@tessel.example"

    def bg(w, h):
        im = grad(w, h, s.top, s.bot)

        def stripes(d):
            for i, x in enumerate(range(-h, w + h, int(w * .16))):
                d.polygon([(x, h), (x + int(w * .07), h), (x + int(w * .07) + h * .6, 0), (x + h * .6, 0)], fill=(255, 255, 255, 16 if i % 2 else 8))
        im.alpha_composite(lay(w, h, stripes))
        return im

    def frame(im):
        w, h = im.size
        d = ImageDraw.Draw(im)
        d.polygon([(0, 0), (int(w * .045), 0), (int(w * .02), h), (0, h)], fill=s.acc)
        d.polygon([(w, h), (w - int(w * .3), h), (w - int(w * .27), h - int(w * .02)), (w, h - int(w * .02))], fill=s.acc)

    def rule(d, cx, y, wd):
        d.rectangle([cx - wd // 2, y - 10, cx - wd // 2 + wd // 3, y + 10], fill=s.acc)
    s.bg, s.frame, s.rule = bg, frame, rule
    s.paper = (250, 252, 248)
    return s


def perfum():
    s = Style()
    s.name, s.brand, s.align, s.logo_kind = "Perfum", "Perfum", "c", "black"
    s.top, s.bot, s.acc, s.ink, s.dark_bg = (252, 240, 238), (240, 214, 214), (170, 128, 88), (86, 52, 56), False
    s.tfont, s.caps = TIMESI, False
    s.site, s.mail = "PERFUM.EXAMPLE", "hello@perfum.example"

    def bg(w, h):
        im = grad(w, h, s.top, s.bot)
        im.alpha_composite(lay(w, h, lambda d: d.ellipse([w * .1, h * .1, w * .9, h * .7], fill=(255, 255, 255, 120)), 220 * w // 2480))
        return im

    def frame(im):
        w, h = im.size
        d = ImageDraw.Draw(im)
        m = int(w * .05)
        d.rectangle([m, m, w - m, h - m], outline=s.acc, width=max(3, w // 600))
        m2 = m + int(w * .018)
        d.rectangle([m2, m2, w - m2, h - m2], outline=s.acc, width=max(2, w // 900))
        for cx, cy in [(m, m), (w - m, m), (m, h - m), (w - m, h - m)]:
            r = int(w * .012)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=s.acc)

    def rule(d, cx, y, wd):
        d.line([(cx - wd // 2, y), (cx - 40, y)], fill=s.acc, width=3)
        d.line([(cx + 40, y), (cx + wd // 2, y)], fill=s.acc, width=3)
        d.ellipse([cx - 14, y - 14, cx + 14, y + 14], outline=s.acc, width=4)
    s.bg, s.frame, s.rule = bg, frame, rule
    s.paper = (255, 251, 249)
    return s


def strikeline():
    s = Style()
    s.name, s.brand, s.align, s.logo_kind = "Strikeline", "Football", "c", "black"
    s.navy = (14, 32, 70)
    s.top, s.bot, s.acc, s.ink, s.dark_bg = (246, 249, 253), (214, 226, 244), (30, 110, 200), (14, 32, 70), False
    s.tfont, s.caps = SANS, True
    s.site, s.mail = "STRIKELINE.EXAMPLE", "hello@strikeline.example"

    def bg(w, h):
        im = grad(w, h, s.top, s.bot)

        def bands(d):
            if h < 3000:
                return
            y0 = int(h * .885)
            for i in range(7):
                th = int(h * .004) + i * int(h * .0014)
                y = y0 + i * int(h * .016)
                d.rectangle([0, y, w, y + th], fill=(s.navy if i % 2 == 0 else s.acc) + (255,))
        im.alpha_composite(lay(w, h, bands))
        return im

    def frame(im):
        w, h = im.size
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, int(h * .035)], fill=s.navy)
        d.rectangle([0, int(h * .035), w, int(h * .045)], fill=s.acc)

    def rule(d, cx, y, wd):
        d.rectangle([cx - wd // 2, y - 8, cx + wd // 2, y + 8], fill=s.acc)
    s.bg, s.frame, s.rule = bg, frame, rule
    s.paper = (255, 255, 255)
    return s


# ---------------------------------------------------------------------------- pieces
def T(s, text):
    return text.upper() if s.caps else text


def title_font(s, size):
    return F(s.tfont, size)


def poster(s, name, title, sub, extra):
    W, H = 2480, 3508
    im = s.bg(W, H)
    s.frame(im)
    lg = logo(s.brand, s.logo_kind)
    d = ImageDraw.Draw(im)
    if s.align == "c":
        fit(im, lg, (W // 2 - 650, 330, 1300, 1300), "ct")
        d = ImageDraw.Draw(im)
        cx = W // 2
        if s.name == "Strikeline":                      # scoreboard
            d.rounded_rectangle([cx - 900, 1760, cx + 900, 2300], radius=30, fill=s.navy, outline=s.acc, width=8)
            d.text((cx, 1880), "MATCH DAY" if "Event" in title else "THIS WEEK", font=F(SANS, 78), fill=(120, 190, 255), anchor="mm")
            d.text((cx, 2090), T(s, title), font=title_font(s, 250 if len(title) < 10 else 200), fill=(255, 255, 255), anchor="mm")
            s.rule(d, cx, 2420, 900)
        else:
            d.text((cx, 2000), T(s, title), font=title_font(s, 340 if len(title) < 11 else 270), fill=s.ink, anchor="mm")
            s.rule(d, cx, 2260, 1000)
        subtxt = " ".join(sub.upper()) if s.name == "Northbeam" else (sub if s.name == "Perfum" else sub.upper())
        sf = F(GEOR, 92) if s.name in ("Northbeam", "Perfum") else F(SANS, 100)
        d.text((cx, 2560 if s.name != "Strikeline" else 2580), subtxt, font=sf, fill=s.ink, anchor="mm")
        d.text((cx, 2760 if s.name != "Strikeline" else 2740), extra, font=F(SANS, 70), fill=s.acc if s.dark_bg else s.acc, anchor="mm")
        foot_y = 3290 if s.name != "Strikeline" else 3040
        d.text((300, foot_y), s.site, font=F(SANS, 54), fill=s.ink, anchor="lm")
        d.text((W - 300, foot_y), s.mail, font=F(SANS, 54), fill=s.ink, anchor="rm")
    else:                                               # Tessel: left aligned, huge stacked caps
        fit(im, lg, (300, 260, 900, 700), "lt")
        d = ImageDraw.Draw(im)
        words = T(s, title).split()
        y = 1350
        for wd in words:
            d.text((300, y), wd, font=title_font(s, 640), fill=s.ink, anchor="la")
            y += 620
        d.rectangle([300, y + 40, 300 + 1300, y + 150], fill=s.acc)
        d.text((340, y + 95), sub.upper(), font=F(SANS, 84), fill=(8, 28, 18), anchor="lm")
        d.text((300, y + 280), extra, font=F(SANS, 66), fill=s.acc, anchor="la")
        d.text((300, 3330), s.site + "   -   " + s.mail, font=F(SANS, 52), fill=s.ink, anchor="lm")
    im.convert("RGB").save(OUT / s.name / name, optimize=True)


def doc_header(s, im, d, W, title):
    lg_dark = logo(s.brand, "black" if s.name != "Northbeam" else "black")
    if s.name == "Northbeam":
        d.rectangle([0, 0, W, 90], fill=s.bot)
        fit(im, lg_dark, (180, 220, 700, 280), "lt")
        return F(GEO, 150), s.bot, (W - 180, 300), "rm"
    if s.name == "Tessel":
        d.polygon([(0, 0), (W, 0), (W, 420), (int(W * .55), 420), (int(W * .5), 560), (0, 560)], fill=s.top)
        d.polygon([(0, 560), (int(W * .5), 560), (int(W * .52), 600), (0, 600)], fill=s.acc)
        fit(im, logo(s.brand, "white"), (180, 120, 700, 340), "lt")
        return F(IMPACT, 230), s.top, (180, 800), "lm"
    if s.name == "Perfum":
        fit(im, lg_dark, (W // 2 - 350, 140, 700, 340), "ct")
        s.rule(d, W // 2, 560, 1400)
        return F(TIMESI, 190), s.ink, (W // 2, 720), "mm"
    d.rectangle([0, 0, W, 330], fill=s.navy)
    for i in range(5):
        d.rectangle([0, 330 + i * 28, W, 330 + i * 28 + 6 + i * 3], fill=s.acc)
    fit(im, logo(s.brand, "white"), (180, 60, 600, 220), "lt")
    return F(SANS, 150), s.navy, (W - 180, 540), "rm"


def invoice(s):
    W, H = 2480, 3508
    im = Image.new("RGBA", (W, H), s.paper + (255,))
    d = ImageDraw.Draw(im)
    f, col, xy, anc = doc_header(s, im, d, W, "INVOICE")
    d = ImageDraw.Draw(im)
    d.text(xy, T(s, "Invoice") if s.name in ("Tessel", "Strikeline") else "Invoice", font=f, fill=col, anchor=anc)
    ink = (30, 32, 40)
    d.text((180, 980), "Billed to", font=F(SANS, 52), fill=s.acc if s.dark_bg is False or s.name == "Northbeam" else s.top)
    for i, t in enumerate(["Client Name", "Street 1, City", "client@email.com"]):
        d.text((180, 1060 + i * 80), t, font=F(GEOR, 56), fill=ink)
    for i, t in enumerate(["No. 0000", "Date: 00 / 00 / 0000", "Due: 00 / 00 / 0000"]):
        d.text((W - 180, 1000 + i * 85), t, font=F(GEOR, 56), fill=ink, anchor="rm")
    head = s.navy if s.name == 'Strikeline' else (s.top if s.dark_bg else s.acc)
    d.rectangle([180, 1450, W - 180, 1570], fill=head)
    for x, t, a in [(220, "DESCRIPTION", "lm"), (1650, "QTY", "mm"), (1950, "PRICE", "mm"), (W - 220, "TOTAL", "rm")]:
        d.text((x, 1510), t, font=F(SANS, 48), fill=(255, 255, 255), anchor=a)
    for r in range(6):
        y = 1570 + r * 140
        if s.name == "Strikeline" and r % 2 == 0:
            d.rectangle([180, y, W - 180, y + 140], fill=(238, 244, 252))
        d.line([(180, y + 140), (W - 180, y + 140)], fill=(220, 222, 228), width=3)
        d.text((220, y + 70), "Item or service %d" % (r + 1), font=F(GEOR, 52), fill=ink, anchor="lm")
        for x, t, a in [(1650, "0", "mm"), (1950, "0.00", "mm"), (W - 220, "0.00", "rm")]:
            d.text((x, y + 70), t, font=F(GEOR, 52), fill=ink, anchor=a)
    d.rectangle([W - 900, 2530, W - 180, 2700], fill=head)
    d.text((W - 860, 2615), "TOTAL", font=F(SANS, 56), fill=(255, 255, 255), anchor="lm")
    d.text((W - 220, 2615), "0.00", font=F(GEO, 90), fill=(255, 255, 255), anchor="rm")
    d.text((180, 3330), "Company Name  -  Street 1, Your City  -  " + s.mail, font=F(SANS, 46), fill=head)
    im.convert("RGB").save(OUT / s.name / "invoice_template.png", optimize=True)


def card(s, name, size, heading, lines, shape="rect"):
    W, H = size
    im = s.bg(W, H)
    s.frame(im)
    d = ImageDraw.Draw(im)
    lg = logo(s.brand, s.logo_kind)
    if s.name == "Strikeline":
        d.rectangle([0, 0, W, int(H * .5)], fill=s.navy)
        for i in range(4):
            d.rectangle([0, int(H * .5) + i * int(H * .02), W, int(H * .5) + i * int(H * .02) + 5 + i * 2], fill=s.acc)
        fit(im, logo(s.brand, "white"), (int(W * .06), int(H * .08), int(W * .24), int(H * .34)), "lc")
        d = ImageDraw.Draw(im)
        d.text((int(W * .36), int(H * .25)), heading.upper(), font=F(SANS, int(H * (.15 if len(heading) < 12 else .105))), fill=(255, 255, 255), anchor="lm")
        for i, t in enumerate(lines):
            d.text((int(W * .06), int(H * .68) + i * int(H * .12)), t, font=F(SANS, int(H * .068)), fill=s.navy, anchor="lm")
        im.convert("RGB").save(OUT / s.name / name, optimize=True)
        return
    if s.align == "c":
        fit(im, lg, (W // 2 - int(W * .18), int(H * .08), int(W * .36), int(H * .26)), "ct")
        d = ImageDraw.Draw(im)
        d.text((W // 2, int(H * .55)), T(s, heading), font=title_font(s, int(H * (.14 if len(heading) < 12 else .105))), fill=s.ink, anchor="mm")
        s.rule(d, W // 2, int(H * .68), int(W * .3))
        for i, t in enumerate(lines):
            d.text((W // 2, int(H * .78) + i * int(H * .08)), t, font=F(SANS, int(H * .05)), fill=s.acc, anchor="mm")
    else:
        fit(im, lg, (int(W * .08), int(H * .08), int(W * .3), int(H * .22)), "lt")
        d = ImageDraw.Draw(im)
        d.text((int(W * .08), int(H * .56)), T(s, heading), font=title_font(s, int(H * .2)), fill=s.ink, anchor="lm")
        d.rectangle([int(W * .08), int(H * .7), int(W * .38), int(H * .7) + 14], fill=s.acc)
        for i, t in enumerate(lines):
            d.text((int(W * .08), int(H * .79) + i * int(H * .08)), t, font=F(SANS, int(H * .05)), fill=s.acc, anchor="lm")
    im.convert("RGB").save(OUT / s.name / name, optimize=True)


def envelope(s):
    W, H = 2598, 1299
    im = Image.new("RGBA", (W, H), s.paper + (255,))
    d = ImageDraw.Draw(im)
    ink = (30, 32, 40)
    if s.name == "Tessel":
        d.polygon([(0, 0), (700, 0), (560, H), (0, H)], fill=s.top)
        d.polygon([(700, 0), (740, 0), (600, H), (560, H)], fill=s.acc)
        fit(im, logo(s.brand, "white"), (90, 120, 440, 300), "lt")
        x0 = 900
    elif s.name == "Perfum":
        d.rectangle([60, 60, W - 60, H - 60], outline=s.acc, width=5)
        fit(im, logo(s.brand, "black"), (W // 2 - 300, 120, 600, 260), "ct")
        s.rule(d, W // 2, 440, 900)
        x0 = W // 2 - 380
    elif s.name == "Strikeline":
        d.rectangle([0, 0, W, 150], fill=s.top)
        for i in range(4):
            d.rectangle([0, 150 + i * 22, W, 150 + i * 22 + 6 + i * 2], fill=s.acc)
        fit(im, logo(s.brand, "white"), (140, 20, 360, 110), "lt")
        x0 = 700
    else:
        fit(im, logo(s.brand, "black"), (140, 120, 620, 220), "lt")
        d.line([(140, 380), (W - 140, 380)], fill=s.acc, width=6)
        x0 = W // 2 + 100
    d = ImageDraw.Draw(im)
    for i, t in enumerate(["Recipient Name", "Street 1", "City, 00000"]):
        d.text((x0, 640 + i * 100), t, font=F(GEOR, 64), fill=ink)
    d.rectangle([W - 380, 90 if s.name != "Strikeline" else 240, W - 140, 330 if s.name != "Strikeline" else 480], outline=(190, 192, 200), width=5)
    im.convert("RGB").save(OUT / s.name / "envelope_DL.png", optimize=True)


def sticker(s):
    S = 1500
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill = lerp(s.top, s.bot, .4)
    lg = logo(s.brand, s.logo_kind)
    if s.name == "Northbeam":
        d.ellipse([20, 20, S - 20, S - 20], fill=fill + (255,))
        d.ellipse([90, 90, S - 90, S - 90], outline=s.acc, width=8)
    elif s.name == "Tessel":
        pts = [(S * .3, 30), (S * .7, 30), (S - 30, S * .3), (S - 30, S * .7), (S * .7, S - 30), (S * .3, S - 30), (30, S * .7), (30, S * .3)]
        d.polygon(pts, fill=fill + (255,))
        d.polygon([(S * .3 + 60, 100), (S * .7 - 60, 100), (S - 100, S * .3 + 40), (S - 100, S * .7 - 40), (S * .7 - 60, S - 100), (S * .3 + 60, S - 100), (100, S * .7 - 40), (100, S * .3 + 40)], outline=s.acc, width=10)
    elif s.name == "Perfum":
        d.ellipse([20, 20, S - 20, S - 20], fill=(255, 251, 249, 255), outline=s.acc, width=10)
        d.ellipse([85, 85, S - 85, S - 85], outline=s.acc, width=4)
    else:
        d.rounded_rectangle([20, 20, S - 20, S - 20], radius=220, fill=fill + (255,))
        for i in range(5):
            d.rectangle([60, S - 380 + i * 62, S - 60, S - 380 + i * 62 + 10 + i * 3], fill=s.acc + (160,))
        d.rounded_rectangle([60, 60, S - 60, S - 60], radius=190, outline=s.acc, width=8)
    fit(im, lg, (330, 300, 840, 840), "cc")
    im.save(OUT / s.name / "label_sticker.png", optimize=True)


def tag(s):
    W, H = 900, 1500
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base = s.bg(W, H)
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    if s.name == "Tessel":
        md.polygon([(0, 120), (W, 0), (W, H - 120), (0, H)], fill=255)
    elif s.name == "Perfum":
        md.rounded_rectangle([0, 0, W - 1, H - 1], radius=420, fill=255)
    elif s.name == "Strikeline":
        md.polygon([(0, 0), (W, 0), (W, H - 220), (W // 2, H), (0, H - 220)], fill=255)
    else:
        md.rounded_rectangle([0, 0, W - 1, H - 1], radius=80, fill=255)
    im.paste(base, (0, 0), m)
    d = ImageDraw.Draw(im)
    d.ellipse([W // 2 - 55, 100, W // 2 + 55, 210], fill=(0, 0, 0, 0), outline=s.acc, width=8)
    fit(im, logo(s.brand, s.logo_kind), (150, 300, 600, 400), "ct")
    d = ImageDraw.Draw(im)
    d.text((W // 2, 860), T(s, "Product name"), font=title_font(s, 80 if s.name != "Tessel" else 110), fill=s.ink, anchor="mm")
    s.rule(d, W // 2, 970, 460)
    d.text((W // 2, 1110), "0.00", font=title_font(s, 170) if s.name != "Strikeline" else F(SANS, 170), fill=s.acc, anchor="mm")
    d.text((W // 2, 1290), "www.yourcompany.com", font=F(SANS, 44), fill=s.ink, anchor="mm")
    im.save(OUT / s.name / "product_tag.png", optimize=True)


def app_icon(s):
    S = 1024
    im = s.bg(S, S)
    fav = DES / s.brand / f"{s.brand.lower()}_favicon_512.png"
    if fav.exists():
        fit(im, Image.open(fav).convert("RGBA"), (190, 190, 644, 644), "cc")
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], radius=230, fill=255)
    im.putalpha(m)
    im.save(OUT / s.name / "app_icon_1024.png", optimize=True)


def main():
    for make in (northbeam, tessel, perfum, strikeline):
        s = make()
        out = OUT / s.name
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        poster(s, "event_poster_A3.png", "Big Event", "Join us", "00 / 00 / 0000  -  YOUR VENUE, YOUR CITY")
        poster(s, "sale_poster_A3.png", "Winter Sale", "Up to 00% off", "THIS WEEK ONLY  -  IN STORE AND ONLINE")
        poster(s, "product_poster_A3.png", "New Arrival", "Now available", "DISCOVER THE NEW COLLECTION")
        invoice(s)
        envelope(s)
        card(s, "thank_you_card_A6.png", (1748, 1240), "Thank you", ["We appreciate your order.", "www.yourcompany.com"])
        card(s, "gift_voucher.png", (2100, 900), "Gift voucher", ["For: ________   From: ________", "Value  0"])
        card(s, "ticket.png", (2400, 900), "Admit one", ["00 / 00 / 0000   00:00", "Your venue  -  No. 0000"])
        card(s, "name_badge.png", (1200, 800), "Full Name", ["JOB TITLE"])
        sticker(s)
        tag(s)
        app_icon(s)
        print(s.name, len(list(out.iterdir())))


if __name__ == "__main__":
    main()

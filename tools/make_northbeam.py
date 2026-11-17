#!/usr/bin/env python3
"""
Northbeam company kit, built from the logo in images/Northbeamlogo.png:
logo versions (full, icon, wordmark, white, black, dark background), favicon and avatar, social banners and posts,
business cards, letterhead, email signature, presentation slides and a brand guidelines sheet.
The emblem and the lettering are your original drawing; everything around them is laid out here.

    python tools/make_northbeam.py
"""
import math
from collections import deque

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403
import nb_extract

OUT = ROOT / "images" / "design" / "Northbeam"
INDIGO, CYAN, NIGHT, DEEP = (88, 100, 214), (125, 235, 240), (14, 24, 52), (24, 40, 96)
CHAR, FROST, CREAM, MINT = (52, 52, 52), (240, 248, 252), (254, 248, 224), (224, 255, 251)
TAGLINE = "Guided by light."
SITE, MAIL, PHONE = "northbeam.example", "hello@northbeam.example", "+00 000 000 000"


# --------------------------------------------------------------------------------------- logo parts

def load_logo():
    im = nb_extract.cutout()
    a = np.asarray(im).copy()
    a[:12] = 0; a[-12:] = 0; a[:, :12] = 0; a[:, -12:] = 0          # white frame line of the source image
    a[2000:2110, 1790:2030] = 0 if False else a[2000:2110, 1790:2030]  # (signature handled below)
    return Image.fromarray(a, "RGBA")


def components(alpha, scale=4):
    """Connected shapes of the logo (labelled on a reduced copy to stay fast)."""
    small = np.asarray(Image.fromarray(alpha).resize((alpha.shape[1] // scale, alpha.shape[0] // scale), Image.BOX)) > 20
    lab = np.zeros(small.shape, np.int32)
    n = 0
    for y, x in zip(*np.nonzero(small)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        q = deque([(y, x)])
        while q:
            cy, cx = q.popleft()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = cy + dy, cx + dx
                    if 0 <= yy < small.shape[0] and 0 <= xx < small.shape[1] and small[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        q.append((yy, xx))
    return lab, n


def split_logo(logo):
    a = np.asarray(logo)
    lab, n = components(a[..., 3])
    full = np.kron(lab, np.ones((4, 4), np.int32))
    full = np.pad(full, ((0, a.shape[0] - full.shape[0]), (0, a.shape[1] - full.shape[1])))
    emblem_ids, word_ids = set(), set()
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 6:
            continue
        top = ys.min() * 4
        (emblem_ids if top < 2000 else word_ids).add(i)
    # the little hand-written signature near the emblem belongs to neither
    def mask_for(ids):
        m = np.isin(full, list(ids)).astype(np.uint8) * 255
        m = np.asarray(Image.fromarray(m).filter(ImageFilter.MaxFilter(9)))
        return m
    parts = []
    for ids in (emblem_ids, word_ids):
        m = mask_for(ids)
        arr = a.copy()
        arr[..., 3] = np.minimum(arr[..., 3], m)
        parts.append(Image.fromarray(arr, "RGBA"))
    return parts


def crop_pad(img, pad=0.04):
    box = img.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
    c = img.crop(box)
    p = int(max(c.size) * pad)
    out = Image.new("RGBA", (c.width + 2 * p, c.height + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(c, (p, p))
    return out


def tint(img, color):
    out = Image.new("RGBA", img.size, color + (0,))
    out.putalpha(img.split()[3])
    return out


def lockup(emblem, word, gap=0.06):
    """Emblem above the wordmark, centred."""
    w = max(emblem.width, word.width)
    h = emblem.height + word.height + int(word.height * gap)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(emblem, ((w - emblem.width) // 2, 0))
    out.alpha_composite(word, ((w - word.width) // 2, emblem.height + int(word.height * gap)))
    return out


def fit(img, box_w, box_h):
    s = min(box_w / img.width, box_h / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def put(canvas, img, center=None, topleft=None, shadow_op=0.0):
    x, y = topleft if topleft else (round(center[0] - img.width / 2), round(center[1] - img.height / 2))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(img, (x, y))
    if shadow_op:
        canvas = shadow(canvas, layer.split()[3], (0, 10), 18, (0, 0, 0), shadow_op)
    return Image.alpha_composite(canvas, layer)


# ----------------------------------------------------------------------------------------- backgrounds

def dark_bg(size, mark=None):
    w, h = size
    bg = radial(size, DEEP, NIGHT, cx=0.3, cy=0.45, spread=0.9).convert("RGBA")
    bg = glow(bg, (-w * 0.1, -h * 0.4, w * 0.7, h * 0.9), INDIGO, blur=min(w, h) * 0.25, alpha=60)
    if mark is not None:   # big, very faint emblem as a watermark
        big = fit(tint(mark, (255, 255, 255)), h * 1.3, h * 1.3)
        a = big.split()[3].point(lambda v: int(v * 0.045))
        big.putalpha(a)
        bg = put(bg, big, center=(w * 0.82, h * 0.55))
    return bg


def light_bg(size):
    w, h = size
    t = np.linspace(0, 1, w)[None, :, None]
    arr = np.array(CREAM)[None, None, :] * (1 - t) + np.array(MINT)[None, None, :] * t
    arr = np.repeat(arr, h, axis=0)
    return Image.fromarray(arr.astype("uint8")).convert("RGBA")


def gradient_fill(size, c1=INDIGO, c2=CYAN):
    w, h = size
    t = np.linspace(0, 1, w)[None, :, None]
    arr = np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t
    return Image.fromarray(np.repeat(arr, h, axis=0).astype("uint8")).convert("RGBA")


# ---------------------------------------------------------------------------------------------- pieces

def save(img, name, rgba=False):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if name.endswith(".ico"):
        img.save(path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    else:
        (img if rgba else img.convert("RGB")).save(path, optimize=True)
    print("Saved", path.relative_to(ROOT))


def tagline_mask(size, text, y, x, px, anchor="left", track=6):
    return text_mask(size, text, font("georgia.ttf", px), (x, y), track=track, anchor=anchor)


def banner(W, H, emblem, word, dark=True):
    bg = dark_bg((W, H), emblem) if dark else light_bg((W, H))
    safe_h = H * 0.8
    em = fit(emblem, H * 0.78, safe_h)
    bg = put(bg, em, center=(W * 0.19, H * 0.5), shadow_op=0.4 if dark else 0.15)
    wd = fit(word, W * 0.44, H * 0.34)
    cx = W * 0.62
    bg = put(bg, wd, center=(cx, H * 0.46), shadow_op=0.35 if dark else 0.0)
    d = ImageDraw.Draw(bg)
    y = H * 0.46 + wd.height / 2 + H * 0.08
    d.line([(cx - wd.width * 0.46, y), (cx - 24, y)], fill=CYAN + (255,) if dark else INDIGO + (255,), width=max(2, int(H * 0.008)))
    d.line([(cx + 24, y), (cx + wd.width * 0.46, y)], fill=CYAN + (255,) if dark else INDIGO + (255,), width=max(2, int(H * 0.008)))
    diamond(d, cx, y, max(6, H * 0.02), CYAN + (255,) if dark else INDIGO + (255,))
    bg = fill_mask(bg, tagline_mask(bg.size, TAGLINE.upper(), y + H * 0.16, cx, int(H * 0.085), "center", track=int(H * 0.02)), (226, 238, 250) if dark else (40, 50, 110))
    return grain(bg, 8)


def business_cards(emblem, word, full):
    W, H = 1050, 600
    front = dark_bg((W, H), emblem)
    front = put(front, fit(full, W * 0.46, H * 0.74), center=(W / 2, H / 2), shadow_op=0.4)
    d = ImageDraw.Draw(front)
    d.rectangle((0, H - 14, W, H), fill=CYAN + (255,))
    back = light_bg((W, H))
    back = put(back, fit(emblem, 190, 190), topleft=(70, 64))
    back = put(back, fit(word, 380, 110), topleft=(290, 104))
    d = ImageDraw.Draw(back)
    d.line([(70, 300), (W - 70, 300)], fill=INDIGO + (255,), width=3)
    f1, f2 = font("georgiab.ttf", 52), font("segoeui.ttf", 30)
    back = fill_mask(back, text_mask(back.size, "Full Name", f1, (70, 372), anchor="left"), NIGHT)
    back = fill_mask(back, text_mask(back.size, "JOB TITLE", font("segoeui.ttf", 26), (70, 418), track=6, anchor="left"), INDIGO)
    for i, (label, val) in enumerate((("T", PHONE), ("E", MAIL), ("W", SITE))):
        y = 480 + i * 42
        back = fill_mask(back, text_mask(back.size, label, font("segoeuib.ttf" if (FONTS / "segoeuib.ttf").exists() else "segoeui.ttf", 26), (70, y), anchor="left"), INDIGO)
        back = fill_mask(back, text_mask(back.size, val, f2, (120, y), anchor="left"), CHAR)
    d = ImageDraw.Draw(back)
    d.polygon([(W, H), (W - 220, H), (W, H - 220)], fill=INDIGO + (255,))
    return front, back


def letterhead(emblem, word):
    W, H = 2480, 3508
    page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    top = gradient_fill((W, 26))
    page.paste(top, (0, 0))
    page = put(page, fit(emblem, 190, 190), topleft=(200, 170))
    page = put(page, fit(word, 560, 170), topleft=(430, 190))
    ghost = fit(tint(emblem, INDIGO), 1500, 1500)
    ghost.putalpha(ghost.split()[3].point(lambda v: int(v * 0.05)))
    page = put(page, ghost, center=(W - 380, H - 520))
    d = ImageDraw.Draw(page)
    d.line([(200, H - 330), (W - 200, H - 330)], fill=INDIGO + (255,), width=4)
    f = font("segoeui.ttf", 40)
    for i, t in enumerate(("Northbeam Ltd.", "Street 1, City, Country", f"{MAIL}   -   {SITE}")):
        page = fill_mask(page, text_mask(page.size, t, f, (200, H - 270 + i * 62), anchor="left"), CHAR)
    page = fill_mask(page, text_mask(page.size, "Date", font("segoeui.ttf", 40), (W - 200, 230), anchor="right"), (150, 150, 160))
    return page


def email_signature(emblem, word):
    W, H = 1200, 360
    sig = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    sig = put(sig, fit(emblem, 260, 260), topleft=(40, 50))
    d = ImageDraw.Draw(sig)
    d.line([(350, 40), (350, H - 40)], fill=INDIGO + (255,), width=4)
    sig = fill_mask(sig, text_mask(sig.size, "Full Name", font("georgiab.ttf", 56), (400, 100), anchor="left"), NIGHT)
    sig = fill_mask(sig, text_mask(sig.size, "JOB TITLE  -  NORTHBEAM", font("segoeui.ttf", 26), (400, 148), track=5, anchor="left"), INDIGO)
    for i, t in enumerate((PHONE, MAIL, SITE)):
        sig = fill_mask(sig, text_mask(sig.size, t, font("segoeui.ttf", 32), (400, 214 + i * 46), anchor="left"), CHAR)
    return sig


def slides(emblem, word, full):
    W, H = 1920, 1080
    title = dark_bg((W, H), emblem)
    title = put(title, fit(full, 640, 760), center=(480, H / 2), shadow_op=0.4)
    title = fill_mask(title, text_mask(title.size, "Presentation title", font("georgiab.ttf", 108), (900, 470), anchor="left"), (240, 246, 255))
    title = fill_mask(title, text_mask(title.size, "SUBTITLE  -  DATE", font("segoeui.ttf", 40), (904, 560), track=8, anchor="left"), CYAN)
    d = ImageDraw.Draw(title)
    d.rectangle((900, 590, 1220, 598), fill=CYAN + (255,))
    content = light_bg((W, H))
    content.paste(gradient_fill((W, 18)), (0, 0))
    content = put(content, fit(emblem, 120, 120), topleft=(W - 200, 50))
    content = fill_mask(content, text_mask(content.size, "Slide heading", font("georgiab.ttf", 84), (120, 200), anchor="left"), NIGHT)
    d = ImageDraw.Draw(content)
    d.rectangle((120, 236, 360, 242), fill=INDIGO + (255,))
    for i in range(3):
        y = 350 + i * 130
        diamond(d, 140, y, 14, INDIGO + (255,))
        content = fill_mask(content, text_mask(content.size, f"Key point number {i + 1} goes here", font("segoeui.ttf", 54), (180, y + 18), anchor="left"), CHAR)
        d = ImageDraw.Draw(content)
    return title, content


def post_square(emblem, word):
    W = 1080
    img = dark_bg((W, W), emblem)
    img = put(img, fit(emblem, 440, 440), center=(W / 2, 380), shadow_op=0.4)
    img = put(img, fit(word, 760, 190), center=(W / 2, 760), shadow_op=0.3)
    img = fill_mask(img, text_mask(img.size, TAGLINE.upper(), font("georgia.ttf", 42), (W / 2, 930), track=12), (214, 232, 250))
    return grain(img, 8)


def story(emblem, word):
    W, H = 1080, 1920
    img = dark_bg((W, H), emblem)
    img = put(img, fit(emblem, 560, 560), center=(W / 2, 760), shadow_op=0.4)
    img = put(img, fit(word, 820, 210), center=(W / 2, 1180), shadow_op=0.3)
    img = fill_mask(img, text_mask(img.size, TAGLINE.upper(), font("georgia.ttf", 48), (W / 2, 1400), track=14), (214, 232, 250))
    return grain(img, 8)


def avatar(emblem):
    S = 1000
    img = Image.new("RGBA", (S, S), NIGHT + (255,))
    img = glow(img, (100, 100, 900, 900), INDIGO, blur=140, alpha=120)
    img = put(img, fit(emblem, 620, 620), center=(S / 2, S / 2 + 10), shadow_op=0.4)
    return img


def favicon(emblem, size):
    img = Image.new("RGBA", (size, size), NIGHT + (255,))
    pad = max(1, int(size * 0.14))
    em = fit(emblem, size - 2 * pad, size - 2 * pad)
    img = put(img, em, center=(size / 2, size / 2))
    # rounded corners
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), radius=size * 4 // 5, fill=255)
    img.putalpha(m.resize((size, size), Image.LANCZOS))
    return img


def brand_sheet(emblem, word, full):
    W, H = 3000, 2000
    img = light_bg((W, H))
    img.paste(gradient_fill((W, 30)), (0, 0))
    d = ImageDraw.Draw(img)
    img = fill_mask(img, text_mask(img.size, "Northbeam - brand guidelines", font("georgiab.ttf", 84), (120, 190), anchor="left"), NIGHT)
    img = fill_mask(img, text_mask(img.size, "LOGO, COLOUR AND TYPE AT A GLANCE", font("segoeui.ttf", 34), (124, 250), track=8, anchor="left"), INDIGO)
    # logo versions
    panels = [("Primary", light_bg((560, 560)), full), ("On dark", dark_bg((560, 560)), full),
              ("White", gradient_fill((560, 560), INDIGO, DEEP), tint(full, (255, 255, 255))), ("Black", light_bg((560, 560)), tint(full, (20, 20, 20)))]
    for i, (name, bg, lg) in enumerate(panels):
        x = 120 + i * 700
        tile = put(bg, fit(lg, 440, 440), center=(280, 280))
        m = Image.new("L", (560, 560), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, 559, 559), radius=28, fill=255)
        img.paste(tile, (x, 340), m)
        img = fill_mask(img, text_mask(img.size, name.upper(), font("segoeui.ttf", 30), (x + 280, 950), track=6), CHAR)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 340, x + 560, 900), radius=28, outline=INDIGO + (120,), width=2)
    # colours
    img = fill_mask(img, text_mask(img.size, "COLOUR", font("segoeui.ttf", 34), (124, 1090), track=8, anchor="left"), INDIGO)
    swatches = [("Northbeam Indigo", INDIGO), ("Aurora Cyan", CYAN), ("Deep Night", NIGHT), ("Charcoal", CHAR), ("Frost", FROST)]
    d = ImageDraw.Draw(img)
    for i, (n, c) in enumerate(swatches):
        x = 120 + i * 560
        d.rounded_rectangle((x, 1140, x + 500, 1340), radius=22, fill=c + (255,), outline=(150, 150, 160, 255), width=2)
        img = fill_mask(img, text_mask(img.size, n, font("georgiab.ttf", 36), (x, 1400), anchor="left"), NIGHT)
        img = fill_mask(img, text_mask(img.size, "#%02X%02X%02X   RGB %d %d %d" % (c + c), font("segoeui.ttf", 30), (x, 1448), anchor="left"), CHAR)
        d = ImageDraw.Draw(img)
    # typography
    img = fill_mask(img, text_mask(img.size, "TYPE", font("segoeui.ttf", 34), (124, 1560), track=8, anchor="left"), INDIGO)
    img = fill_mask(img, text_mask(img.size, "Headings: Georgia Bold", font("georgiab.ttf", 70), (120, 1650), anchor="left"), NIGHT)
    img = fill_mask(img, text_mask(img.size, "Body and interface: Segoe UI Regular - clear, calm, readable.", font("segoeui.ttf", 46), (120, 1730), anchor="left"), CHAR)
    img = fill_mask(img, text_mask(img.size, "The wordmark is the gothic lettering of the logo - never retype it.", font("segoeui.ttf", 46), (120, 1800), anchor="left"), CHAR)
    # rules
    rules = ["Keep clear space equal to the height of the small triangle around the logo.",
             "Minimum size: emblem 24 px, full logo 120 px wide.",
             "Do not stretch, recolour, rotate or add effects to the logo."]
    for i, t in enumerate(rules):
        img = fill_mask(img, text_mask(img.size, t, font("segoeui.ttf", 36), (1880, 1620 + i * 70), anchor="left"), CHAR)
    img = fill_mask(img, text_mask(img.size, "USE", font("segoeui.ttf", 34), (1884, 1560), track=8, anchor="left"), INDIGO)
    return grain(img, 5)


def main():
    logo = load_logo()
    emblem, word = (crop_pad(p) for p in split_logo(logo))
    full = crop_pad(lockup(emblem, word), 0.05)

    save(fit(full, 2000, 2000), "northbeam_logo.png", rgba=True)
    save(fit(emblem, 1500, 1500), "northbeam_icon.png", rgba=True)
    save(fit(word, 2400, 1000), "northbeam_wordmark.png", rgba=True)
    save(fit(tint(full, (255, 255, 255)), 2000, 2000), "northbeam_logo_white.png", rgba=True)
    save(fit(tint(full, (20, 20, 22)), 2000, 2000), "northbeam_logo_black.png", rgba=True)
    dk = put(dark_bg((2000, 2000), emblem), fit(full, 1400, 1400), center=(1000, 1000), shadow_op=0.4)
    save(dk, "northbeam_logo_dark.png")
    save(avatar(emblem), "northbeam_avatar.png")
    for s in (512, 192, 32):
        save(favicon(emblem, s), f"northbeam_favicon_{s}.png", rgba=True)
    save(favicon(emblem, 64), "northbeam_favicon.ico")

    for name, (W, H) in (("linkedin", (1584, 396)), ("twitter", (1500, 500)), ("facebook", (1640, 624)),
                         ("youtube", (2560, 1440)), ("twitch", (2400, 960))):
        save(banner(W, H, emblem, word), f"northbeam_banner_{name}.png")
    save(banner(1500, 500, emblem, word, dark=False), "northbeam_banner_light.png")
    save(post_square(emblem, word), "northbeam_post_square.png")
    save(story(emblem, word), "northbeam_story.png")
    og = banner(1200, 630, emblem, word)
    save(og, "northbeam_og_image.png")

    front, back = business_cards(emblem, word, full)
    save(front, "northbeam_business_card_front.png")
    save(back, "northbeam_business_card_back.png")
    front.convert("RGB").save(OUT / "northbeam_business_card.pdf", save_all=True, append_images=[back.convert("RGB")], resolution=300)
    lh = letterhead(emblem, word)
    save(lh, "northbeam_letterhead.png")
    lh.convert("RGB").save(OUT / "northbeam_letterhead.pdf", resolution=300)
    save(email_signature(emblem, word), "northbeam_email_signature.png")
    t, c = slides(emblem, word, full)
    save(t, "northbeam_slide_title.png")
    save(c, "northbeam_slide_content.png")
    sheet = brand_sheet(emblem, word, full)
    save(sheet, "northbeam_brand_guidelines.png")
    sheet.convert("RGB").save(OUT / "northbeam_brand_guidelines.pdf", resolution=200)
    print("done")


if __name__ == "__main__":
    main()

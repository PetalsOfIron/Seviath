"""Patch make_sets.py: mascots are close-ups cut from the artwork that defines each set (the user's own assets)."""
from pathlib import Path

P = Path(__file__).resolve().parent / "make_sets.py"
s = P.read_text(encoding="utf-8")

code = '''
# ------------------------------------------------------------------------- portraits cut from the user's own art
ART = ROOT / "images"
DL = Path("C:/Users/SaphiresSilver/Downloads/art")
_PORTRAIT_CACHE = {}


def _crop_circle(img, cx, cy, r, px=480):
    box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    im = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    src = img.crop(box)
    im.paste(src, (0, 0))
    return im.resize((px, px), Image.LANCZOS)


def portrait(kind, C):
    """Returns an RGBA square (the face zone is centred, as make_rose draws faces around its centre)."""
    if kind in _PORTRAIT_CACHE:
        return _PORTRAIT_CACHE[kind]
    px = 480
    if kind == "hood":
        im = _crop_circle(Image.open(ART / "LogoGaming.png").convert("RGBA"), 1507, 1023, 380, px)
        patch = None
    elif kind == "helmet":
        im = _crop_circle(Image.open(ART / "Gamerstreamer.png").convert("RGBA"), 1524, 435, 362, px)
        patch = None
    elif kind == "snake":
        im = _crop_circle(Image.open(ART / "Banner snake.png").convert("RGBA"), 1160, 480, 300, px)
        patch = ((250, 232, 150), 0.88, 0.0, 0.05, 0.8, 0.62)
    elif kind == "flower":
        src = Image.open(DL / "priekstwitterfiver" / "2x" / "1x" / "I will be right back.png").convert("RGBA")
        im = _crop_circle(src, 160, 300, 210, px)
        patch = ((252, 244, 255), 0.82, 0.0, 0.05, 0.74, 0.58)
    elif kind == "triangle":
        import nb_extract
        cut = nb_extract.cutout().crop((300, 240, 2700, 2150))
        base = Image.new("RGBA", (px, px), C["dark"] + (255,))
        e = cut.resize((int(px * 1.5), int(px * 1.5 * cut.height / cut.width)), Image.LANCZOS)
        base.alpha_composite(e, ((px - e.width) // 2, int(px * 0.5 - e.height * 0.58)))
        im = base
        patch = ((228, 244, 250), 0.9, 0.0, 0.22, 0.7, 0.55)
    elif kind == "shield":
        import fb_extract
        cut = fb_extract.cutout()
        base = Image.new("RGBA", (px, px), C["dark"] + (255,))
        part = cut.crop((320 - 120, 110 - 120, 320 + 120, 110 + 120)).resize((px, px), Image.LANCZOS)
        for k in range(4):
            ImageDraw.Draw(base).rectangle((0, int(px * (0.1 + k * 0.08)), int(px * 0.16), int(px * (0.15 + k * 0.08))), fill=C["main"] + (255,))
            ImageDraw.Draw(base).rectangle((int(px * 0.84), int(px * (0.1 + k * 0.08)), px, int(px * (0.15 + k * 0.08))), fill=C["main"] + (255,))
        base.alpha_composite(part)
        im = base
        patch = None
    elif kind == "bottle":
        src = Image.open(DL / "assets" / "Bottle.png").convert("RGBA")
        im = _crop_circle(src, 2290, 3226, 700, px)
        patch = ((255, 236, 236), 0.55, 0.0, 0.0, 0.8, 0.66)
    elif kind == "football":
        src = Image.open(DL / "assets" / "Footballboot.png").convert("RGBA")
        im = _crop_circle(src, 2250, 1100, 700, px)
        base = Image.new("RGBA", (px, px), (20, 80, 50, 255))
        base.alpha_composite(im)
        im = base
        patch = ((240, 246, 240), 0.9, 0.0, 0.0, 0.72, 0.56)
    else:
        im = None
        patch = None
    _PORTRAIT_CACHE[kind] = (im, patch)
    return im, patch

'''
s = s.replace("def make_body(kind, C):", code + "\ndef make_body(kind, C):", 1)

# dispatch: portrait bodies for the art-based kinds
s = s.replace('''    def body(d, S, cx, cy, r, tint):
        dark = tint in ((150, 22, 38), (170, 40, 58))
        if kind == "hood":''', '''    def body(d, S, cx, cy, r, tint):
        dark = tint in ((150, 22, 38), (170, 40, 58))
        if kind in ("hood", "helmet", "snake", "flower", "triangle", "shield", "bottle", "football"):
            im, patch = portrait(kind, C)
            n = int(2 * r * S)
            pic = im.resize((n, n), Image.LANCZOS)
            m = Image.new("L", (n, n), 0)
            ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
            if dark:
                pic = Image.blend(pic.convert("RGB"), Image.new("RGB", pic.size, (60, 0, 0)), 0.35).convert("RGBA")
            pic.putalpha(ImageChops.multiply(pic.split()[3], m))
            d._image.alpha_composite(pic, (int((cx - r) * S), int((cy - r) * S)))
            if patch:
                col, al, ox, oy, rx, ry = patch
                lay = Image.new("RGBA", pic.size, (0, 0, 0, 0))
                ImageDraw.Draw(lay).ellipse((n * (0.5 + ox - rx / 2), n * (0.5 + oy - ry / 2), n * (0.5 + ox + rx / 2), n * (0.5 + oy + ry / 2)), fill=col + (int(255 * al),))
                lay.putalpha(ImageChops.multiply(lay.split()[3], m))
                d._image.alpha_composite(lay, (int((cx - r) * S), int((cy - r) * S)))
            d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), outline=ink, width=int(r * 0.07 * S))
            return
        if kind == "hood":''', 1)
P.write_text(s, encoding="utf-8")
print("portrait patch applied")

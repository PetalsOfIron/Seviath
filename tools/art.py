"""Small drawing helpers shared by the tools/make_*.py scripts (text at 2x, gradient fills, glow)."""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("C:/Windows/Fonts")
SS = 2  # supersampling factor for text


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size * SS)


def radial(size, center_rgb, edge_rgb, cx=0.5, cy=0.5, spread=0.75):
    """Soft radial gradient: center colour in the middle, edge colour in the corners."""
    w, h = size
    base = Image.new("RGB", size, edge_rgb)
    m = Image.radial_gradient("L").resize((int(w * 2 * spread), int(h * 2 * spread)), Image.BICUBIC)
    m = ImageChops.invert(m)
    mask = Image.new("L", size, 0)
    mask.paste(m, (int(w * cx - m.width / 2), int(h * cy - m.height / 2)))
    return Image.composite(Image.new("RGB", size, center_rgb), base, mask)


def spaced_width(d, text, fnt, track):
    return sum(d.textlength(c, font=fnt) for c in text) + track * SS * (len(text) - 1)


def text_mask(size, text, fnt, xy, track=0, anchor="center"):
    """Mask (full size) of text drawn at SS x and scaled down. xy is the centre (or left) of the text."""
    w, h = size
    layer = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(layer)
    x, y = xy[0] * SS, xy[1] * SS
    total = spaced_width(d, text, fnt, track)
    if anchor == "center":
        x -= total / 2
    elif anchor == "right":
        x -= total
    for c in text:
        d.text((x, y), c, font=fnt, fill=255, anchor="ls")
        x += d.textlength(c, font=fnt) + track * SS
    return layer.resize(size, Image.LANCZOS)


def fill_mask(canvas, mask, c1, c2=None):
    """Paint the mask with a flat colour or a top-to-bottom gradient."""
    if c2 is None:
        solid = Image.new("RGBA", canvas.size, tuple(c1) + (255,))
    else:
        box = mask.getbbox() or (0, 0, canvas.width, canvas.height)
        grad = Image.new("RGBA", canvas.size, tuple(c1) + (255,))
        gd = ImageDraw.Draw(grad)
        for y in range(box[1], box[3] + 1):
            t = (y - box[1]) / max(1, box[3] - box[1])
            col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)
            gd.line([(0, y), (canvas.width, y)], fill=col)
        solid = grad
    solid.putalpha(mask)
    return Image.alpha_composite(canvas, solid)


def shadow(canvas, mask, offset=(0, 8), blur=10, color=(0, 0, 0), opacity=0.55):
    sh = Image.new("RGBA", canvas.size, color + (0,))
    moved = ImageChops.offset(mask, offset[0], offset[1])
    sh.putalpha(moved.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity)))
    return Image.alpha_composite(canvas, sh)


def glow(canvas, bbox, color, blur=90, alpha=90, mode="screen"):
    layer = Image.new("RGB", canvas.size, (0, 0, 0))
    ImageDraw.Draw(layer).ellipse(bbox, fill=tuple(int(c * alpha / 255) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    out = ImageChops.screen(canvas.convert("RGB"), layer).convert("RGBA")
    if canvas.mode == "RGBA":
        out.putalpha(canvas.split()[3])   # keep transparency of the canvas
    return out


def vignette(canvas, strength=0.55, color=(0, 0, 0)):
    w, h = canvas.size
    vig = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(vig).ellipse((-w * 0.2, -h * 0.35, w * 1.2, h * 1.35), fill=255)
    vig = ImageChops.invert(vig.filter(ImageFilter.GaussianBlur(min(w, h) * 0.2)))
    dark = Image.new("RGBA", canvas.size, color + (0,))
    dark.putalpha(vig.point(lambda v: int(v * strength)))
    return Image.alpha_composite(canvas, dark)


def grain(canvas, amount=14):
    noise = Image.effect_noise(canvas.size, 14).convert("L")
    g = Image.merge("RGBA", (noise, noise, noise, Image.new("L", canvas.size, amount)))
    return Image.alpha_composite(canvas, g)


def diamond(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def sparkles(canvas, box, n, color, seed=3, max_r=4):
    """Little golden specks, some soft and some sharp, for a bit of life in the background."""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x = rnd.randint(box[0], box[2])
        y = rnd.randint(box[1], box[3])
        r = rnd.uniform(1, max_r)
        a = rnd.randint(70, 200)
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    soft = layer.filter(ImageFilter.GaussianBlur(2.2))
    return Image.alpha_composite(Image.alpha_composite(canvas, soft), layer)


def corner_brackets(canvas, inset, length, color, width=3, gap=10):
    d = ImageDraw.Draw(canvas)
    w, h = canvas.size
    for (x, y, sx, sy) in [(inset, inset, 1, 1), (w - inset, inset, -1, 1), (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
        d.line([(x, y), (x + sx * length, y)], fill=color, width=width)
        d.line([(x, y), (x, y + sy * length)], fill=color, width=width)
        d.line([(x + sx * gap, y + sy * gap), (x + sx * (gap + length * 0.45), y + sy * gap)], fill=color, width=max(1, width - 1))
        d.line([(x + sx * gap, y + sy * gap), (x + sx * gap, y + sy * (gap + length * 0.45))], fill=color, width=max(1, width - 1))
    return canvas

#!/usr/bin/env python3
"""
Hood set redone in the style of the red hooded-gamer logo (images/LogoGaming.png): hand-drawn wobbly frames in dark
maroon, white and red, white paper panels, maroon gothic lettering. The logo itself is your original drawing and is used
as the picture on the screens and banner. Replaces the Hood screens, logo, banner, overlay, alert, corner and panels
(emotes, badges, icons and flair stay as they were).

    python tools/make_hood.py
"""
import math
import random
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import *  # noqa: F401,F403

OUT = ROOT / "images" / "twitch" / "Hood"
SRC = ROOT / "images" / "LogoGaming.png"
DARK, MAROON, RED, WHITE, CREAM = (58, 2, 4), (112, 6, 8), (150, 14, 20), (255, 255, 255), (250, 238, 228)
PAPER = (252, 250, 248)


def rough_loop(box, seed, jit=3.0, step=16):
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    pts = []
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        n = max(2, int(math.hypot(bx - ax, by - ay) / step))
        for i in range(n):
            t = i / n
            pts.append((ax + (bx - ax) * t + rnd.uniform(-jit, jit), ay + (by - ay) * t + rnd.uniform(-jit, jit)))
    return pts


def rough_frame(size, inset=0, seed=1, scale=1.0, hole=None):
    """The logo's frame: dark band, white band, thin red line - all wobbly. Returns (frame layer, inner paper mask)."""
    w, h = size
    S = 3
    layer = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bands = [(0, 26, DARK), (24, 30, WHITE), (50, 6, RED)]
    for off, wd, col in bands:
        o = (inset + off * scale)
        box = (o, o, w - o, h - o)
        pts = [(x * S, y * S) for x, y in rough_loop(box, seed + off, jit=2.6 * scale)]
        d.line(pts + [pts[0], pts[1]], fill=col + (255,), width=max(1, int(wd * scale * S)), joint="curve")
    layer = layer.resize((w, h), Image.LANCZOS)
    o = inset + 64 * scale
    paper = Image.new("L", (w, h), 0)
    ImageDraw.Draw(paper).rectangle((o, o, w - o, h - o), fill=255)
    return layer, paper


def paper_panel(size, scale=1.0, seed=1, fill=PAPER):
    w, h = size
    base = Image.new("RGBA", (w, h), DARK + (255,))
    frame, paper = rough_frame(size, 0, seed, scale)
    inner = Image.new("RGBA", (w, h), fill + (255,))
    base.paste(inner, (0, 0), paper)
    return Image.alpha_composite(base, frame)


def lettered(img, text, center, size, color=(120, 4, 6), grad=(80, 0, 2), track=0):
    f = font("OLDENGL.TTF", size)
    m = text_mask(img.size, text, f, center, track=track)
    return fill_mask(img, m, color, grad)


def fit_size(text, fontname, target_w, start, track=0):
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    size = start
    while size > 16 and spaced_width(probe, text, font(fontname, size), track) / SS > target_w:
        size -= 2
    return size


def bg_maroon(size):
    return radial(size, (108, 8, 12), (36, 0, 2), cx=0.35, cy=0.5, spread=1.0).convert("RGBA")


def logo_card(px, tilt=-2.5):
    logo = Image.open(SRC).convert("RGBA").resize((px, px), Image.LANCZOS)
    pad = int(px * 0.08)
    canvas = Image.new("RGBA", (px + 2 * pad, px + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", logo.size, (0, 0, 0, 255)), (pad, pad + 12))
    sh = sh.filter(ImageFilter.GaussianBlur(px * 0.03))
    sh.putalpha(sh.split()[3].point(lambda v: int(v * 0.6)))
    canvas = Image.alpha_composite(canvas, sh)
    canvas.alpha_composite(logo, (pad, pad))
    return canvas.rotate(tilt, resample=Image.BICUBIC, expand=True)


def screen(title, sub):
    W, H = 1920, 1080
    img = bg_maroon((W, H))
    card = logo_card(860)
    img.alpha_composite(card, (110, (H - card.height) // 2))
    cx = 1400
    img = lettered(img, title, (cx, 520), fit_size(title, "OLDENGL.TTF", 760, 200), color=CREAM, grad=(226, 196, 186))
    d = ImageDraw.Draw(img)
    for x0, x1 in ((cx - 340, cx - 40), (cx + 40, cx + 340)):
        d.line([(x0, 600), (x1, 600)], fill=WHITE + (235,), width=4)
    diamond(d, cx, 600, 12, WHITE + (255,))
    words = sub.split(" ")
    lines = [sub] if len(sub) <= 26 else [" ".join(words[:len(words) // 2 + len(words) % 2]), " ".join(words[len(words) // 2 + len(words) % 2:])]
    for k, ln in enumerate(lines):
        sz = fit_size(ln, "georgiai.ttf", 700, 52)
        img = fill_mask(img, text_mask(img.size, ln, font("georgiai.ttf", sz), (cx, 676 + k * 66)), CREAM)
    return grain(img, 8)


def banner():
    W, H = 3000, 1000
    img = bg_maroon((W, H))
    card = logo_card(880)
    img.alpha_composite(card, (120, (H - card.height) // 2))
    cx = 1950
    size = fit_size("Petals Of Iron", "OLDENGL.TTF", 1700, 300)
    img = lettered(img, "Petals Of Iron", (cx, 520), size, color=CREAM, grad=(226, 196, 186))
    d = ImageDraw.Draw(img)
    d.line([(cx - 700, 610), (cx - 40, 610)], fill=WHITE + (235,), width=5)
    d.line([(cx + 40, 610), (cx + 700, 610)], fill=WHITE + (235,), width=5)
    diamond(d, cx, 610, 16, WHITE + (255,))
    img = fill_mask(img, text_mask(img.size, "Gamer  -  Streamer  -  Artist", font("georgiai.ttf", 84), (cx, 740), track=4), CREAM)
    return grain(img, 8)


def logo_round():
    S = 2000
    src = Image.open(SRC).convert("RGBA").crop((250, 250, 2750, 2750)).resize((1500, 1500), Image.LANCZOS)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    m = Image.new("L", (S * 3, S * 3), 0)
    ImageDraw.Draw(m).ellipse((S * 3 * 0.12, S * 3 * 0.12, S * 3 * 0.88, S * 3 * 0.88), fill=255)
    m = m.resize((S, S), Image.LANCZOS)
    plate = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    plate.alpha_composite(src, ((S - 1500) // 2, (S - 1500) // 2))
    img = shadow(img, m, (0, 20), 28, (0, 0, 0), 0.5)
    img.paste(plate, (0, 0), m)
    ring = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(71)))
    r = Image.new("RGBA", (S, S), DARK + (0,))
    r.putalpha(ring)
    img = Image.alpha_composite(img, r)
    ring2 = ImageChops.subtract(m.filter(ImageFilter.MinFilter(71)), m.filter(ImageFilter.MinFilter(111)))
    r2 = Image.new("RGBA", (S, S), RED + (0,))
    r2.putalpha(ring2)
    return Image.alpha_composite(img, r2)


def panel(title):
    W, H = 1280, 400
    img = paper_panel((W, H), scale=1.2, seed=11)
    img = lettered(img, title, (W / 2, H / 2 + 52), fit_size(title, "OLDENGL.TTF", 900, 150))
    return img


def overlay_frame():
    W, H = 1920, 1080
    frame, paper = rough_frame((W, H), 0, 7, 1.4)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img = Image.alpha_composite(img, frame)
    # webcam window (bottom left) with its own wobbly frame
    cx0, cy0, cx1, cy1 = 70, H - 70 - 300, 70 + 533, H - 70
    cam, _ = rough_frame((cx1 - cx0 + 160, cy1 - cy0 + 160), 0, 5, 0.6)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(cam, (cx0 - 80, cy0 - 80))
    img = Image.alpha_composite(img, layer)
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rectangle((cx0 + 4, cy0 + 4, cx1 - 4, cy1 - 4), fill=0)
    # clear the paper interior of the full frame so the game shows through (frame bands only remain)
    inner = Image.new("L", (W, H), 255)
    ImageDraw.Draw(inner).rectangle((int(64 * 1.4), int(64 * 1.4), W - int(64 * 1.4), H - int(64 * 1.4)), fill=0)
    a = img.split()[3]
    img.putalpha(ImageChops.multiply(a, ImageChops.lighter(inner, Image.new("L", (W, H), 0))))
    # keep the webcam frame (it lies inside the cleared area), re-add it
    img = Image.alpha_composite(img, layer)
    ca = img.split()[3]
    img.putalpha(ImageChops.multiply(ca, cut))
    return img


def banner_panel(size, text, tsize):
    img = paper_panel(size, scale=0.9, seed=3)
    return lettered(img, text, (size[0] / 2, size[1] / 2 + tsize * 0.34), fit_size(text, "OLDENGL.TTF", size[0] - 190, tsize))


def shine_frames(base, text_box_mask, n=26):
    W, H = base.size
    frames = []
    for i in range(n):
        x = -80 + (W + 160) * i / (n - 1)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).polygon([(x, 0), (x + 46, 0), (x - 28, H), (x - 74, H)], fill=(255, 255, 255, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        a = ImageChops.multiply(sh.split()[3], text_box_mask)
        w = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        w.putalpha(a)
        frames.append(Image.alpha_composite(base, w))
    return frames


def alert_frames():
    base = banner_panel((800, 360), "Thanks for the follow!", 96)
    m = Image.new("L", base.size, 0)
    ImageDraw.Draw(m).rectangle((60, 60, 740, 300), fill=255)
    return shine_frames(base, m)


def corner_frames():
    base = banner_panel((440, 200), "Petals Of Iron", 62)
    m = Image.new("L", base.size, 0)
    ImageDraw.Draw(m).rectangle((40, 40, 400, 160), fill=255)
    return shine_frames(base, m, 30)


def gif(frames, path, dur=50):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=dur, disposal=2, loop=0, optimize=False)
    print("Saved", path.relative_to(ROOT))


def save(img, path, rgba=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    (img if rgba else img.convert("RGB")).save(path, optimize=True)
    print("Saved", path.relative_to(ROOT))


def main():
    for n, t, s in (("starting_soon", "Starting soon", "The stream begins shortly"), ("be_right_back", "Be right back", "I will be back in a moment"),
                    ("offline", "Offline", "Thank you for watching, see you next time")):
        save(screen(t, s), OUT / "Screens" / (n + ".png"))
    save(banner(), OUT / "Banner" / "banner.png")
    save(logo_round(), OUT / "Logo" / "logo.png", rgba=True)
    save(overlay_frame(), OUT / "Overlay" / "overlay_frame.png", rgba=True)
    gif(alert_frames(), OUT / "Alert" / "alert.gif")
    gif(corner_frames(), OUT / "Corner" / "corner.gif")
    for t in ("About me", "Schedule", "Chat rules", "Donation", "FAQ", "PC setup", "Links", "Socials"):
        save(panel(t), OUT / "Panels" / (t.lower().replace(" ", "_") + ".png"))
    print("done")


if __name__ == "__main__":
    main()

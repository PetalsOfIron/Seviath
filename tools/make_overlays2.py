#!/usr/bin/env python3
"""Refined overlays for Perfum (gold filigree and rose-petal corners) and Tessel (broadcast-style angled frame with pitch markings and the boot)."""
import math
import sys

from PIL import Image, ImageChops, ImageDraw

from art import *  # noqa: F401,F403
import make_brands as mb

TW = ROOT / "images" / "twitch"
W, H = 1920, 1080
S = 2
CAM = (80, H - 80 - 300, 80 + 533, H - 80)   # webcam window


def cut_cam(img, margin=6):
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rectangle((CAM[0] + margin, CAM[1] + margin, CAM[2] - margin, CAM[3] - margin), fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], cut))
    return img


def petal(d, cx, cy, ln, wd, ang, fill, outline):
    pts = []
    for i in range(40):
        t = 2 * math.pi * i / 40
        pts.append((math.sin(t) * wd * 0.5 * (1 - 0.35 * math.cos(t)), -math.cos(t) * ln * 0.5))
    ca, sa = math.cos(ang), math.sin(ang)
    d.polygon([((cx + x * ca - y * sa) * S, (cy + x * sa + y * ca) * S) for x, y in pts], fill=fill, outline=outline, width=int(1.5 * S))


def layer():
    L = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    return L, ImageDraw.Draw(L)


def down(L):
    return L.resize((W, H), Image.LANCZOS)


def perfum():
    GOLD, GOLD_D, PLUM = (200, 162, 92, 255), (150, 112, 52, 255), (96, 34, 60, 255)
    ROSE, BLUSH = (226, 150, 160, 255), (246, 206, 200, 255)
    L, d = layer()
    d.rounded_rectangle((26 * S, 26 * S, (W - 26) * S, (H - 26) * S), radius=34 * S, outline=GOLD, width=int(4 * S))
    d.rounded_rectangle((40 * S, 40 * S, (W - 40) * S, (H - 40) * S), radius=24 * S, outline=PLUM, width=int(2 * S))
    d.rounded_rectangle((48 * S, 48 * S, (W - 48) * S, (H - 48) * S), radius=18 * S, outline=GOLD_D[:3] + (140,), width=int(1.5 * S))
    start = {(1, 1): 180, (-1, 1): 270, (-1, -1): 0, (1, -1): 90}
    for ox, oy, sx, sy in ((26, 26, 1, 1), (W - 26, 26, -1, 1), (26, H - 26, 1, -1), (W - 26, H - 26, -1, -1)):
        x0, y0 = ox + sx * 28, oy + sy * 28
        for rr, wd in ((120, 3), (150, 2), (180, 1.5)):
            box = (min(x0, x0 + sx * rr * 2) * S, min(y0, y0 + sy * rr * 2) * S, max(x0, x0 + sx * rr * 2) * S, max(y0, y0 + sy * rr * 2) * S)
            d.arc(box, start[(sx, sy)], start[(sx, sy)] + 90, fill=GOLD, width=int(wd * S))
        base = math.atan2(sy, sx)
        for da, ln, col in ((-0.55, 112, BLUSH), (0.55, 112, BLUSH), (0.0, 136, ROSE)):
            petal(d, ox + sx * 70, oy + sy * 70, ln, 44, base + math.pi / 2 + da, col, GOLD_D)
        d.ellipse(((x0 - 7) * S, (y0 - 7) * S, (x0 + 7) * S, (y0 + 7) * S), fill=GOLD, outline=GOLD_D, width=S)
    for cy in (26, H - 26):
        cx = W / 2
        d.line([((cx - 220) * S, cy * S), ((cx - 28) * S, cy * S)], fill=GOLD, width=int(2 * S))
        d.line([((cx + 28) * S, cy * S), ((cx + 220) * S, cy * S)], fill=GOLD, width=int(2 * S))
        d.polygon([((cx - 17) * S, cy * S), (cx * S, (cy - 17) * S), ((cx + 17) * S, cy * S), (cx * S, (cy + 17) * S)], fill=GOLD, outline=GOLD_D)
        for k in (-1, 1):
            d.ellipse(((cx + k * 44 - 4) * S, (cy - 4) * S, (cx + k * 44 + 4) * S, (cy + 4) * S), fill=ROSE)
    img = down(L)
    b = mb.load("Bottle.png").crop((1750, 2000, 2850, 3900))
    b.thumbnail((190, 300))
    cam = Image.new("RGBA", (232, 346), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cam)
    cd.ellipse((0, 0, 231, 345), fill=(250, 238, 226, 255), outline=GOLD, width=5)
    cd.ellipse((10, 10, 221, 335), outline=PLUM, width=2)
    cam.alpha_composite(b, ((232 - b.width) // 2, (346 - b.height) // 2))
    img.alpha_composite(cam, (W - 340, 90))
    x0, y0, x1, y1 = CAM
    L, d = layer()
    d.rounded_rectangle(((x0 - 10) * S, (y0 - 10) * S, (x1 + 10) * S, (y1 + 10) * S), radius=22 * S, outline=GOLD, width=int(4 * S))
    d.rounded_rectangle(((x0 - 1) * S, (y0 - 1) * S, (x1 + 1) * S, (y1 + 1) * S), radius=14 * S, outline=PLUM, width=int(2 * S))
    for (px, py, a) in ((x0 - 10, y0 - 10, 2.4), (x1 + 10, y0 - 10, 3.9), (x1 + 10, y1 + 10, 5.5), (x0 - 10, y1 + 10, 0.8)):
        for da in (-0.5, 0.5):
            petal(d, px, py, 54, 20, a + da, BLUSH, GOLD_D)
    img = Image.alpha_composite(img, down(L))
    return cut_cam(img)


def tessel():
    LIME, GREEN, WHITE = (223, 255, 61, 255), (31, 163, 74, 255), (245, 247, 245, 255)
    L, d = layer()
    c = 70
    pts = [(c, 16), (W - c, 16), (W - 16, c), (W - 16, H - c), (W - c, H - 16), (c, H - 16), (16, H - c), (16, c)]
    d.line([(x * S, y * S) for x, y in pts + [pts[0], pts[1]]], fill=LIME, width=int(5 * S), joint="curve")
    p2 = [(c + 18, 34), (W - c - 18, 34), (W - 34, c + 18), (W - 34, H - c - 18), (W - c - 18, H - 34), (c + 18, H - 34), (34, H - c - 18), (34, c + 18)]
    d.line([(x * S, y * S) for x, y in p2 + [p2[0], p2[1]]], fill=GREEN[:3] + (150,), width=int(2 * S), joint="curve")

    def bundle(ox, oy, sx, sy):
        for k, (wd, col) in enumerate(((46, LIME), (22, GREEN), (14, WHITE))):
            o = 120 + k * 56
            poly = [(ox + sx * o, oy), (ox + sx * (o + wd), oy), (ox + sx * (o + wd - 90), oy + sy * 20), (ox + sx * (o - 90), oy + sy * 20)]
            d.polygon([(x * S, y * S) for x, y in poly], fill=col)
    bundle(0, 0, 1, 1)
    bundle(W, H - 20, -1, -1)
    d.arc(((W / 2 - 150) * S, (-134) * S, (W / 2 + 150) * S, 166 * S), 0, 180, fill=LIME[:3] + (150,), width=int(3 * S))
    d.arc(((W / 2 - 150) * S, (H - 166) * S, (W / 2 + 150) * S, (H + 134) * S), 180, 360, fill=LIME[:3] + (150,), width=int(3 * S))
    for (cx, cy, a) in ((c, c, 0), (W - c, c, 90), (W - c, H - c, 180), (c, H - c, 270)):
        d.arc(((cx - 46) * S, (cy - 46) * S, (cx + 46) * S, (cy + 46) * S), a, a + 90, fill=WHITE[:3] + (170,), width=int(3 * S))
    img = down(L)
    boot = mb.load("Footballboot.png")
    box = boot.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox()
    boot = boot.crop(box)
    boot.thumbnail((470, 470))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(boot, (W - boot.width - 70, H - boot.height - 70))
    img = Image.alpha_composite(img, shadow(Image.new("RGBA", (W, H), (0, 0, 0, 0)), lay.split()[3], (0, 10), 12, (0, 0, 0), 0.5))
    img = Image.alpha_composite(img, lay)
    x0, y0, x1, y1 = CAM
    L, d = layer()
    ch = 36
    poly = [(x0 - 12 + ch, y0 - 12), (x1 + 12, y0 - 12), (x1 + 12, y1 + 12 - ch), (x1 + 12 - ch, y1 + 12), (x0 - 12, y1 + 12), (x0 - 12, y0 - 12 + ch)]
    d.line([(x * S, y * S) for x, y in poly + [poly[0], poly[1]]], fill=LIME, width=int(6 * S), joint="curve")
    d.line([((x0 - 12) * S, (y0 - 30) * S), ((x0 + 160) * S, (y0 - 30) * S)], fill=GREEN, width=int(8 * S))
    for k in range(6):
        d.line([((x1 - k * 22 - 20) * S, (y1 + 28) * S), ((x1 - k * 22) * S, (y1 + 28) * S)], fill=WHITE, width=int(4 * S))
    img = Image.alpha_composite(img, down(L))
    return cut_cam(img)


if __name__ == "__main__":
    for name, fn in (("Perfum", perfum), ("Tessel", tessel)):
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        p = TW / name / "Overlay" / "overlay_frame.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        fn().save(p, optimize=True)
        print("Saved", name, flush=True)

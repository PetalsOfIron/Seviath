#!/usr/bin/env python3
"""The Petals corner redrawn completely fresh as vector-style drawing at 880x400 (6x supersampled), same design as the
user's 440x200 GIF. The falling petals follow the exact positions measured in the original frames, so the animation
is the same. Output: images/twitch-large/Corner/petals_corner.png (animated PNG). The original GIF is never changed."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageSequence

from art import ROOT, FONTS
import make_rose as mr

SRC = ROOT / "images" / "twitch" / "Corner" / "petals_corner.gif"
OUT = ROOT / "images" / "twitch-large" / "Corner" / "petals_corner.png"
W, H = 900, 450          # a little roomier than 2x the original so nothing touches the edge
OX, OY = 12, 34          # shifts the whole design: centred, and the top leaf is no longer cut off
SS = 5

DARK = (58, 12, 22)
PLATE = (23, 10, 15)
CREAM = (243, 230, 220)
RED = (178, 38, 58)
GOLD = (240, 188, 66)
SLATE = (126, 134, 146)
PINK = (250, 108, 126)


def P(x, y):
    return ((x + OX) * SS, (y + OY) * SS)


def box(x0, y0, x1, y1):
    return ((x0 + OX) * SS, (y0 + OY) * SS, (x1 + OX) * SS, (y1 + OY) * SS)


def label(mask):
    """Connected components of a boolean mask -> list of (cx, cy, area, angle, major, minor)."""
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    comps = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                stack = [(y, x)]
                seen[y, x] = True
                pts = []
                while stack:
                    cy, cx = stack.pop()
                    pts.append((cx, cy))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                if len(pts) >= 14:
                    p = np.array(pts, float)
                    c = p.mean(0)
                    cov = np.cov((p - c).T)
                    ev, evec = np.linalg.eigh(cov)
                    ang = math.atan2(evec[1, 1], evec[0, 1])
                    comps.append((c[0], c[1], len(pts), ang, math.sqrt(max(ev[1], 0.1)) * 2.6, math.sqrt(max(ev[0], 0.1)) * 2.6))
    return comps


def measure_petals():
    """Pink petals of every original frame (below the plate), in original 440x200 pixel coordinates."""
    out = []
    with Image.open(SRC) as im:
        for f in ImageSequence.Iterator(im):
            a = np.asarray(f.convert("RGBA")).astype(int)
            m = (a[..., 3] > 128) & (a[..., 0] > 215) & (a[..., 1] > 70) & (a[..., 1] < 150) & (a[..., 2] > 80) & (a[..., 2] < 165)
            m[:128, :] = False                       # only below the plate
            out.append(label(m))
        durs = [f.info.get("duration", 60) for f in ImageSequence.Iterator(im)]
    return out, durs


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), int(size * SS))


def catmull(pts, n=14):
    out = []
    p = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(p) - 2):
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * ((2 * p[i][k]) + (-p[i - 1][k] + p[i + 1][k]) * t + (2 * p[i - 1][k] - 5 * p[i][k] + 4 * p[i + 1][k] - p[i + 2][k]) * t * t + (-p[i - 1][k] + 3 * p[i][k] - 3 * p[i + 1][k] + p[i + 2][k]) * t ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def vine(d):
    """Thorny vine with berries and leaves, top right (same layout as the original)."""
    ctrl = [(560, 76), (600, 30), (690, 26), (770, 52), (832, 70)]
    curve = catmull(ctrl)
    d.line([P(x, y) for x, y in curve], fill=RED + (255,), width=int(8 * SS), joint="curve")
    for i in (10, 24, 38, 50):                       # small thorns
        x, y = curve[min(i, len(curve) - 1)]
        d.polygon([P(x - 5, y + 4), P(x + 5, y + 4), P(x + 1, y + 16)], fill=(150, 30, 48, 255))
    for (x, y) in ((600, 30), (690, 26), (770, 52), (832, 70)):
        d.ellipse(box(x - 11, y - 11, x + 11, y + 11), fill=RED + (255,), outline=DARK + (255,), width=int(3.5 * SS))
    for (x, y, ang, L) in ((610, 28, -96, 54), (700, 24, -78, 58), (772, 50, -52, 52)):
        mr.leaf(d, SS, x + OX, y + OY, L, 19, math.radians(ang), fill=SLATE, outline=DARK, lw=7)


def star(d, x, y, r, col=CREAM):
    if r < 1:
        return
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.26
        a = -math.pi / 2 + math.pi * i / 4
        pts.append(P(x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=col + (255,), outline=DARK + (255,), width=int(2.4 * SS))


def swirl_rose(d, cx, cy, r):
    """The stylised spiral rose: layered rounded petals and a spiral line."""
    for k in range(4):
        rr = r * (1 - k * 0.17)
        col = [(150, 24, 40), (176, 34, 52), (196, 44, 62), (206, 60, 78)][k]
        ox, oy = math.cos(k * 1.9) * r * 0.05, math.sin(k * 1.9) * r * 0.04
        d.ellipse(box(cx + ox - rr, cy + oy - rr * 0.78, cx + ox + rr, cy + oy + rr * 0.78), fill=col + (255,), outline=DARK + (255,), width=int(4 * SS))
    pts = []
    for i in range(90):
        t = i / 89
        a = t * 4.6 * math.pi
        rr = r * 0.62 * t
        pts.append(P(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.84))
    d.line(pts, fill=DARK + (255,), width=int(4 * SS), joint="curve")
    d.arc(box(cx - r * 0.7, cy - r * 0.62, cx + r * 0.1, cy + r * 0.1), 200, 262, fill=(236, 120, 134, 255), width=int(4 * SS))


def base_layer(twinkle):
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 222, 84, 838, 250
    d.rounded_rectangle(box(x0, y0, x1, y1), radius=34 * SS, fill=DARK + (255,))
    d.rounded_rectangle(box(x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28 * SS, fill=CREAM + (255,))
    d.rounded_rectangle(box(x0 + 14, y0 + 14, x1 - 14, y1 - 14), radius=24 * SS, fill=RED + (255,))
    d.rounded_rectangle(box(x0 + 18, y0 + 18, x1 - 18, y1 - 18), radius=20 * SS, fill=PLATE + (255,))
    d.text(P(527, 150), "PetalsOfIron", font=font("georgiab.ttf", 72), fill=CREAM + (255,), anchor="mm")
    d.text(P(525, 212), "WoW  ·  Addons  ·  Art", font=font("georgiai.ttf", 27), fill=(158, 146, 148, 255), anchor="mm")
    vine(d)
    cx, cy = 124, 170
    for r, col in ((116, DARK), (108, GOLD), (90, DARK), (85, CREAM)):
        d.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
    swirl_rose(d, cx, cy + 4, 72)
    for (sx, sy, r0, ph) in ((38, 57, 17, 0.0), (122, 27, 19, 0.33), (208, 56, 19, 0.66), (48, 282, 15, 0.15), (207, 300, 19, 0.5)):
        star(d, sx, sy, r0 * (0.55 + 0.45 * abs(math.sin(math.pi * (twinkle + ph)))))
    return L


def main():
    petals, durs = measure_petals()
    frames = []
    n = len(petals)
    for i, comps in enumerate(petals):
        L = base_layer(i / n)
        d = ImageDraw.Draw(L)
        for (px, py, area, ang, major, minor) in comps:
            x, y = px * 2, py * 2
            a, b = max(major * 2, 12), max(minor * 2, 8)
            pts = []
            for j in range(36):
                t = 2 * math.pi * j / 36
                ex, ey = math.cos(t) * a * (1 + 0.18 * math.cos(t)), math.sin(t) * b
                pts.append(P(x + ex * math.cos(ang) - ey * math.sin(ang), y + ex * math.sin(ang) + ey * math.cos(ang)))
            d.polygon(pts, fill=PINK + (255,), outline=DARK + (255,), width=int(3.2 * SS))
        frames.append(L.resize((W, H), Image.LANCZOS))
    # centre the whole design (union of all frames) on the canvas, with an even margin
    bb = None
    for f in frames:
        b = f.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    dx = (W - (bb[2] - bb[0])) // 2 - bb[0]
    dy = (H - (bb[3] - bb[1])) // 2 - bb[1]
    shifted = []
    for f in frames:
        g = Image.new("RGBA", f.size, (0, 0, 0, 0))
        g.alpha_composite(f, (max(dx, 0), max(dy, 0)), (max(-dx, 0), max(-dy, 0)))
        shifted.append(g)
    frames = shifted
    print("content box", bb, "shift", dx, dy)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, format="PNG", save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=1)
    print("Saved", OUT, len(frames), "frames; petals per frame", [len(c) for c in petals][:8])


if __name__ == "__main__":
    main()

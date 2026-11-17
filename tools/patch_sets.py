"""One-off patch: distinct medallion / panel / corner shapes per set in make_sets.py."""
import re
from pathlib import Path

P = Path(__file__).resolve().parent / "make_sets.py"
s = P.read_text(encoding="utf-8")

shapes = {"Hood": ("circle", None), "Helmet": ("shield", "chamfer"), "Slash": ("octagon", "slant"), "Snake": ("scallop", "pill"),
          "Floral": ("flower", "pill"), "Tessel": ("hex", "notch"), "Perfum": ("oval", "cartouche"), "Northbeam": ("triangle", "arrow"),
          "Strikeline": ("rsquare", "slantL")}
for k, (a, b) in shapes.items():
    s = s.replace('"%s": dict(main=' % k, '"%s": dict(shape="%s", pshape=%r, main=' % (k, a, b), 1)

helpers = '''
def shape_pts(kind, cx, cy, r, n=96):
    if kind == "oval":
        return [(cx + math.cos(2 * math.pi * i / n) * r * 0.86, cy + math.sin(2 * math.pi * i / n) * r) for i in range(n)]
    if kind in ("scallop", "flower"):
        lobes, amp = (7, 0.06) if kind == "scallop" else (4, 0.14)
        pts = []
        for i in range(n * 2):
            a = 2 * math.pi * i / (n * 2)
            rr = r * ((1 - amp) + amp * abs(math.cos(a * lobes)))
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        return pts
    if kind == "hex":
        return [(cx + math.cos(math.radians(-90 + 60 * i)) * r, cy + math.sin(math.radians(-90 + 60 * i)) * r) for i in range(6)]
    if kind == "octagon":
        return [(cx + math.cos(math.radians(22.5 + 45 * i)) * r * 1.04, cy + math.sin(math.radians(22.5 + 45 * i)) * r * 1.04) for i in range(8)]
    if kind == "triangle":
        return [(cx, cy - r * 1.02), (cx + r * 1.0, cy + r * 0.8), (cx - r * 1.0, cy + r * 0.8)]
    if kind == "rsquare":
        k = r * 0.7
        pts = []
        for (px, py, a0) in ((cx + k, cy - k, -90), (cx + k, cy + k, 0), (cx - k, cy + k, 90), (cx - k, cy - k, 180)):
            for t in range(0, 91, 10):
                pts.append((px + math.cos(math.radians(a0 + t)) * r * 0.3, py + math.sin(math.radians(a0 + t)) * r * 0.3))
        return pts
    if kind == "shield":
        pts = [(cx - r * 0.86, cy - r * 0.9), (cx + r * 0.86, cy - r * 0.9), (cx + r * 0.86, cy + r * 0.1)]
        for t in range(1, 21):
            a = math.pi / 2 * t / 20
            pts.append((cx + r * 0.86 * math.cos(a), cy + r * 0.1 + r * 0.9 * math.sin(a)))
        for t in range(20, 0, -1):
            a = math.pi / 2 * t / 20
            pts.append((cx - r * 0.86 * math.cos(a), cy + r * 0.1 + r * 0.9 * math.sin(a)))
        return pts
    return [(cx + math.cos(2 * math.pi * i / n) * r, cy + math.sin(2 * math.pi * i / n) * r) for i in range(n)]


def panel_poly(kind, w, h, m):
    if kind == "chamfer":
        c = 70
        return [(m + c, m), (w - m - c, m), (w - m, m + c), (w - m, h - m - c), (w - m - c, h - m), (m + c, h - m), (m, h - m - c), (m, m + c)]
    if kind == "slant":
        return [(m + 70, m), (w - m, m), (w - m - 70, h - m), (m, h - m)]
    if kind == "slantL":
        return [(m, m), (w - m - 70, m), (w - m, h - m), (m + 70, h - m)]
    if kind == "arrow":
        return [(m + 70, m), (w - m - 70, m), (w - m, h / 2), (w - m - 70, h - m), (m + 70, h - m), (m, h / 2)]
    if kind == "pill":
        r = (h - 2 * m) / 2
        pts = [(w - m - r + math.sin(math.radians(t)) * r, h / 2 - math.cos(math.radians(t)) * r) for t in range(0, 181, 6)]
        pts += [(m + r - math.sin(math.radians(t)) * r, h / 2 + math.cos(math.radians(t)) * r) for t in range(0, 181, 6)]
        return pts
    if kind == "notch":
        r = min(56, h // 6)
        pts = [(m, m), (w - m, m), (w - m, h / 2 - r)]
        pts += [(w - m - math.sin(math.radians(t)) * r, h / 2 - r * math.cos(math.radians(t))) for t in range(0, 181, 10)]
        pts += [(w - m, h - m), (m, h - m), (m, h / 2 + r)]
        pts += [(m + math.sin(math.radians(t)) * r, h / 2 + r * math.cos(math.radians(t))) for t in range(0, 181, 10)]
        return pts
    if kind == "cartouche":
        r = 60
        pts = []
        for (cx_, cy_, a0) in ((m, m, 0), (w - m, m, 90), (w - m, h - m, 180), (m, h - m, 270)):
            for t in range(0, 91, 10):
                a = math.radians(a0 + t)
                pts.append((cx_ + math.cos(a) * r, cy_ + math.sin(a) * r))
        return pts
    return [(m, m), (w - m, m), (w - m, h - m), (m, h - m)]


def shaped_panel(C, size):
    w, h = size
    S = 2

    def mask(poly):
        im = Image.new("L", (w * S, h * S), 0)
        ImageDraw.Draw(im).polygon([(x * S, y * S) for x, y in poly], fill=255)
        return im.resize((w, h), Image.LANCZOS)
    outer = mask(panel_poly(C["pshape"], w, h, 10))
    p = C["pshape"]
    bands = ((outer, C["dark"]), (outer.filter(ImageFilter.MinFilter(15)), C["accent"]),
             (outer.filter(ImageFilter.MinFilter(21)), C["main"] if p in ("slant", "slantL") else C["accent2"]), (outer.filter(ImageFilter.MinFilter(29)), C["fill"]))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for m_, col in bands:
        lay = Image.new("RGBA", (w, h), col + (255,))
        lay.putalpha(m_)
        img = Image.alpha_composite(img, lay)
    orn = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(orn)
    sc = h / 400.0
    if p in ("slant", "slantL"):
        for k in range(3):
            x = (60 + k * 26) * sc if p == "slant" else w - (130 + k * 26) * sc
            if p == "slant":
                poly = [(x, 38 * sc), (x + 12 * sc, 38 * sc), (x - 22 * sc, h - 38 * sc), (x - 34 * sc, h - 38 * sc)]
            else:
                poly = [(x, 38 * sc), (x + 12 * sc, 38 * sc), (x + 46 * sc, h - 38 * sc), (x + 34 * sc, h - 38 * sc)]
            od.polygon(poly, fill=(C["main"] if k != 1 else C["accent"]) + (255,))
    elif p == "chamfer":
        for sx in (80 * sc, w - 80 * sc):
            for sy in (50 * sc, h - 50 * sc):
                od.polygon([(sx - 12 * sc, sy), (sx, sy - 12 * sc), (sx + 12 * sc, sy), (sx, sy + 12 * sc)], fill=C["accent"] + (255,))
    elif p == "pill":
        step = int(40 * sc)
        for x in range(int(150 * sc), int(w - 150 * sc), step):
            od.arc((x, 32 * sc, x + step, 72 * sc), 0, 180, fill=C["accent"] + (255,), width=max(2, int(4 * sc)))
            od.arc((x, h - 72 * sc, x + step, h - 32 * sc), 180, 360, fill=C["accent"] + (255,), width=max(2, int(4 * sc)))
    elif p == "notch":
        od.line([(w / 2, 36 * sc), (w / 2, h - 36 * sc)], fill=C["accent"] + (110,), width=max(2, int(3 * sc)))
        od.arc((w / 2 - 60 * sc, h / 2 - 60 * sc, w / 2 + 60 * sc, h / 2 + 60 * sc), 0, 360, fill=C["accent"] + (110,), width=max(2, int(3 * sc)))
    elif p == "cartouche":
        for sy in (30 * sc, h - 30 * sc):
            od.polygon([(w / 2 - 14 * sc, sy), (w / 2, sy - 14 * sc), (w / 2 + 14 * sc, sy), (w / 2, sy + 14 * sc)], fill=C["accent"] + (255,))
    elif p == "arrow":
        for k in range(5):
            od.polygon([((150 + k * 26) * sc, h - 44 * sc), ((163 + k * 26) * sc, h - 70 * sc), ((176 + k * 26) * sc, h - 44 * sc)], fill=C["accent"] + (255,))
            od.polygon([(w - (150 + k * 26) * sc, 44 * sc), (w - (163 + k * 26) * sc, 70 * sc), (w - (176 + k * 26) * sc, 44 * sc)], fill=C["accent"] + (255,))
    orn.putalpha(ImageChops.multiply(orn.split()[3], outer.filter(ImageFilter.MinFilter(25))))
    return Image.alpha_composite(img, orn)

'''
s = s.replace("def panel(C, title):", helpers + "\ndef panel(C, title):", 1)
s = s.replace('    img = panel_base((W, H), C, 1.2)\n    ic = mascot_icon(C, "smile", 210)',
              '    img = shaped_panel(C, (W, H)) if C.get("pshape") else panel_base((W, H), C, 1.2)\n    ic = mascot_icon(C, "smile", 210)', 1)
s = s.replace('    img.alpha_composite(ic, (96, (H - 210) // 2 + 6))\n    sz = fit_size(title, C["font"], 760, 150)',
              '    img.alpha_composite(ic, (130 if C.get("pshape") in ("slant", "arrow", "cartouche") else 100, (H - 210) // 2 + 6))\n    sz = fit_size(title, C["font"], 700, 150)', 1)

# medallion shapes
a = s.index("def medallion(")
b = s.index("def badge_img(")
s = s[:a] + '''def medallion(C, size, inner_fn, ring_col, dots=0, crown=False, stars=0):
    k = size / 432
    kind = C["shape"]
    plate = C["fill"] if sum(C["fill"]) > 500 else tuple(min(255, c + 34) for c in C["accent2"])

    def fn(d, S):
        c = size / 2
        for r, col in ((c - 4, C["dark"]), (c - 12, ring_col), (c - 50, C["dark"]), (c - 59, plate)):
            cy = c + (8 * k if kind == "triangle" else 0)
            d.polygon([(x * S, y * S) for x, y in shape_pts(kind, c, cy, r * (0.93 if kind == "triangle" else 1))], fill=col + (255,))
        if kind in ("circle", "oval", "scallop", "flower"):
            for i in range(dots):
                a = 2 * math.pi * i / max(dots, 1)
                px, py = c + math.cos(a) * (c - 31 * k) * (0.86 if kind == "oval" else 1), c + math.sin(a) * (c - 31 * k)
                d.ellipse(((px - 8 * k) * S, (py - 8 * k) * S, (px + 8 * k) * S, (py + 8 * k) * S), fill=C["accent"] + (255,))
    return mr.layer((size, size), fn)


''' + s[b:]
s = s.replace('int(size * 0.62))\n    img.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2 + int(size * 0.02)))',
              'int(size * (0.5 if C["shape"] == "triangle" else 0.62)))\n    img.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2 + int(size * 0.02)))', 1)
s = s.replace('"crown" if tier == 3 else "", int(size * 0.64))', '"crown" if tier == 3 else "", int(size * (0.5 if C["shape"] == "triangle" else 0.64)))', 1)
s = s.replace("    ic = mr.emote(mood, extra, int(size * 0.64))", '    ic = mr.emote(mood, extra, int(size * (0.5 if C["shape"] == "triangle" else 0.64)))', 1)

# animated(): shaped base when the set has a panel shape (corners and alerts follow the panel shape)
s = s.replace("    base = panel_base(size, C, sc)\n    sz = fit_size(text, C[\"font\"], w - 200 * sc, tsize)",
              "    base = shaped_panel(C, size) if C.get(\"pshape\") else panel_base(size, C, sc)\n    sz = fit_size(text, C[\"font\"], w - 200 * sc, tsize)", 1)
s = s.replace('            bd = border(size, C["frame"], C, sc)\n            wh = Image.new("RGBA", size, (255, 255, 255, 0))\n            wh.putalpha(bd.split()[3].point(lambda v: int(v * 0.45 * k)))',
              '            bd = base\n            wh = Image.new("RGBA", size, (255, 255, 255, 0))\n            wh.putalpha(bd.split()[3].point(lambda v: int(v * 0.35 * k)))', 1)

# icons-only rebuild
s = s.replace("def build(name):\n    C = dict(SETS[name])", "def build(name, only=None):\n    C = dict(SETS[name])", 1)
s = s.replace('    if em_dir.exists():\n        shutil.rmtree(em_dir)\n    for folder, nm, mood, extra in mr.EMOTE_SETS:',
              '    if em_dir.exists() and not only:\n        shutil.rmtree(em_dir)\n    for folder, nm, mood, extra in ([] if only else mr.EMOTE_SETS):', 1)
s = s.replace('    if C["frame"]:\n        overlay(C)', '    if C["frame"] and not only:\n        overlay(C)', 1)
s = s.replace('        gif(animated(C, (800, 360)', '        gif(animated(C, (800, 360)', 1)
s = s.replace('        for fn_, t in PANELS:\n            p = out / "Panels" / f"{fn_}.png"',
              '    if C["frame"] or C.get("pshape"):\n        for fn_, t in PANELS:\n            p = out / "Panels" / f"{fn_}.png"', 1)
s = s.replace('    if C["screens"]:\n        for fn_, t, s, mood, extra in', '    if C["screens"] and not only:\n        for fn_, t, s, mood, extra in', 1)
s = s.replace('    for n in (sys.argv[1:] or list(SETS)):\n        build(n)',
              '    args = [a for a in sys.argv[1:] if not a.startswith("--")]\n    for n in (args or list(SETS)):\n        build(n, only="--icons" in sys.argv)', 1)
P.write_text(s, encoding="utf-8")
print("patched")

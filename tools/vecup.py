"""Crisp enlargement for flat cartoon art: re-draws the image from its own colour palette with smooth outlines
(posterise the 8x enlarged picture to the original palette, clean the edge pixels, shrink with anti-aliasing)."""
import numpy as np
from PIL import Image, ImageFilter


def palette(rgba_list, k=12, seed=1):
    pts = []
    for im in rgba_list:
        a = np.asarray(im.convert("RGBA"))
        pts.append(a[a[..., 3] > 200][:, :3])
    pts = np.concatenate(pts).astype(np.float32)
    if len(pts) > 20000:
        pts = pts[np.random.default_rng(seed).choice(len(pts), 20000, replace=False)]
    cent = pts[np.random.default_rng(seed).choice(len(pts), min(k, len(pts)), replace=False)]
    for _ in range(14):
        d = ((pts[:, None, :] - cent[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        for j in range(len(cent)):
            m = lab == j
            if m.any():
                cent[j] = pts[m].mean(0)
    # merge near-duplicate colours
    keep = []
    for c in cent:
        if all(np.abs(c - q).max() > 14 for q in keep):
            keep.append(c)
    return np.array(keep, np.float32)


def enlarge(im, pal, out=448, work=8):
    """im: RGBA original; returns RGBA at out x out (non-square sizes keep their ratio)."""
    im = im.convert("RGBA")
    ow = round(im.width * out / max(im.size)); oh = round(im.height * out / max(im.size))
    ww, wh = ow * 2, oh * 2                                  # working size, then shrink for anti-aliasing
    prem = im.convert("RGBa").resize((ww, wh), Image.BICUBIC).convert("RGBA")
    a = np.asarray(prem).astype(np.float32)
    rgb = a[..., :3]
    d = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    lab = d.argmin(-1).astype(np.uint8)
    L = Image.fromarray(lab, "L").filter(ImageFilter.ModeFilter(5))
    lab = np.asarray(L)
    colored = pal[lab].astype(np.uint8)
    alpha = im.split()[3].resize((ww, wh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.4))
    alpha = alpha.point(lambda v: 0 if v < 110 else 255 if v > 150 else int((v - 110) * 255 / 40))
    out_im = Image.fromarray(np.dstack([colored, np.asarray(alpha)]), "RGBA")
    return out_im.resize((ow, oh), Image.LANCZOS)


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    im = Image.open(p).convert("RGBA")
    pal = palette([im])
    r = enlarge(im, pal)
    bg = Image.new("RGBA", r.size, (200, 196, 196, 255)); bg.alpha_composite(r)
    b2 = Image.new("RGBA", r.size, (200, 196, 196, 255)); b2.alpha_composite(im.resize(r.size, Image.LANCZOS))
    s = Image.new("RGB", (r.width * 2 + 10, r.height)); s.paste(b2.convert("RGB"), (0, 0)); s.paste(bg.convert("RGB"), (r.width + 10, 0))
    s.save("C:/Users/SAPHIR~1/AppData/Local/Temp/claude/1c11d2ce0030b2d4/5c4410c7-1755-4db2-9956-c88b7487f3ac/scratchpad/vec.png")

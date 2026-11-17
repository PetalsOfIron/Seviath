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


def enlarge_mode(im, pal, out=448, work=8, ablur=1.4, acut=130):
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
    alpha = im.split()[3].resize((ww, wh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(ablur))
    alpha = alpha.point(lambda v: 0 if v < acut - 20 else 255 if v > acut + 20 else int((v - acut + 20) * 255 / 40))
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


def gif_save(frames, pal, out, path, durations):
    """Animated GIF with a fixed palette and hard (1-bit) transparency - no dithering, no halo dots around the edges."""
    n = len(pal)
    flat = [int(c) for p in pal for c in p] + [0, 0, 0] * (256 - n)
    ims = []
    for f in frames:
        big = enlarge(f, pal, out=out, ablur=2.0, acut=118)
        a = np.asarray(big)
        rgb = a[..., :3].astype(np.float32)
        d = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
        lab = d.argmin(-1).astype(np.uint8)
        lab[a[..., 3] < 128] = n                      # transparent index
        im = Image.fromarray(lab, "P")
        im.putpalette(flat)
        ims.append(im)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=durations, loop=0, disposal=2, transparency=n, optimize=False)


def enlarge(im, pal, out=448, work=8, ablur=1.4, acut=130):   # noqa: F811  (smooth label-field version)
    """Smooth enlargement: every palette colour (and 'transparent') becomes a soft field that is enlarged with
    bicubic interpolation; the winning colour at each pixel gives clean, curved outlines instead of stair steps."""
    im = im.convert("RGBA")
    ow = round(im.width * out / max(im.size))
    oh = round(im.height * out / max(im.size))
    ww, wh = ow * 2, oh * 2
    a = np.asarray(im)
    K = len(pal)
    d = ((a[..., :3].astype(np.float32)[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    soft = np.exp(-(d - d.min(-1, keepdims=True)) / 900.0)               # soft colour membership (keeps edge blends)
    soft = soft / soft.sum(-1, keepdims=True)
    al = (a[..., 3].astype(np.float32) / 255.0)[..., None]
    memb = np.concatenate([soft * al, 1 - al], axis=-1)                    # last channel: transparent
    sc = ww / im.width
    fields = np.zeros((wh, ww, K + 1), np.float32)
    for k in range(K + 1):
        ch = Image.fromarray((memb[..., k] * 255).astype(np.uint8))
        up = ch.resize((ww, wh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(max(1.0, 0.55 * sc)))
        fields[..., k] = np.asarray(up)
    win = fields.argmax(-1)
    colors = np.vstack([pal, np.zeros((1, 3), np.float32)])[win].astype(np.uint8)
    alpha = np.where(win == K, 0, 255).astype(np.uint8)
    big = Image.fromarray(np.dstack([colors, alpha]), "RGBA")
    return big.resize((ow, oh), Image.LANCZOS)

"""Small 'PETALS OF IRON' watermark for portfolio images.

  python tools/watermark.py sample            # writes one sample next to the repo (nothing is changed)
  python tools/watermark.py apply             # marks every image in images/ (originals are kept in ../portfolio_originals)

The marking always starts from the untouched originals in ../portfolio_originals, so running it twice never marks an image twice.
"""
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageSequence

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
ORIG = ROOT.parent / "portfolio_originals"
FONT = "C:/Windows/Fonts/georgiab.ttf"
TEXT = "PETALS OF IRON"
SKIP_NAMES = {"seviath-logo.png", "background.jpg", "petals-background.png"}
# images that already carry the Petals of Iron name (logo lettering or a signature) are left alone
ALREADY_NAMED = {"Rose.png", "Snake.png", "Scalewoman.png", "characterdesign.jpg", "Beija.png", "Beija1.png", "beija444.png", "beija666.png",
                 "rose_logo.png", "petals_rowan_trees_banner.png"}
MIN_WIDTH = 300


def mark(im):
    """Return a copy of the RGBA image with a small, soft watermark in the bottom right corner."""
    im = im.convert("RGBA")
    w, h = im.size
    size = max(13, min(44, int(min(w, h * 1.6) / 38)))
    f = ImageFont.truetype(FONT, size)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    margin = max(8, size // 2)
    kw = dict(font=f, fill=(255, 255, 255, 140), stroke_width=max(1, size // 14), stroke_fill=(0, 0, 0, 105))
    # all four corners, so cropping one side never removes the mark
    d.text((margin, margin), TEXT, anchor="lt", **kw)
    d.text((w - margin, margin), TEXT, anchor="rt", **kw)
    d.text((margin, h - margin), TEXT, anchor="lb", **kw)
    d.text((w - margin, h - margin), TEXT, anchor="rb", **kw)
    return Image.alpha_composite(im, layer)


def mark_file(src, dest):
    im = Image.open(src)
    if getattr(im, "is_animated", False):
        frames, durs = [], []
        for fr in ImageSequence.Iterator(im):
            durs.append(fr.info.get("duration", 60))
            frames.append(mark(fr.copy()))
        frames[0].save(dest, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    else:
        out = mark(im)
        if dest.suffix.lower() in (".jpg", ".jpeg"):
            out = out.convert("RGB")
            out.save(dest, quality=93)
        else:
            out.save(dest, optimize=True)


def candidates():
    for p in sorted(IMAGES.rglob("*")):
        if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif") and p.name not in SKIP_NAMES and p.name not in ALREADY_NAMED:
            if p.name.startswith(("favicon", "apple-touch")):
                continue
            yield p


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"
    if mode == "sample":
        first = next(candidates())
        out = ROOT.parent / "seviathstudio" / "src" / "_g_tmp" / "watermark_sample.png"
        mark_file(first, out)
        print(first, "->", out)
    elif mode == "apply":
        if not ORIG.exists():
            shutil.copytree(IMAGES, ORIG)
        n = 0
        for p in candidates():
            rel = p.relative_to(IMAGES)
            src = ORIG / rel
            try:
                if Image.open(src).width < MIN_WIDTH:
                    continue
                mark_file(src, p)
                n += 1
            except Exception as e:
                print("skipped", rel, e)
        print("marked", n)

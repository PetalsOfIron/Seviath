"""Cut the footballer silhouette and ball out of images/Football.png (transparent PNG)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = "C:/Users/SaphiresSilver/Projects/portfolio/images/Football.png"


def cutout():
    im = Image.open(SRC).convert("RGB").crop((1180, 0, 1820, 1000))
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    mx = a.max(-1)
    fg = ((lum > 95) | ((a[..., 2] > 150) & (a[..., 0] < 90))).astype(np.uint8) * 255   # grey figure, white ball, cyan patches
    m = Image.fromarray(fg).filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.MinFilter(21))   # close small gaps
    # fill holes: flood the outside, everything not reached is inside
    pad = Image.new("L", (m.width + 2, m.height + 2), 0)
    pad.paste(m, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    arr = np.asarray(pad)[1:-1, 1:-1]
    inside = (arr != 128).astype(np.uint8) * 255
    mask = Image.fromarray(inside).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(1.5))   # include black outline
    rgba = im.convert("RGBA")
    rgba.putalpha(mask)
    return rgba


if __name__ == "__main__":
    im = cutout()
    sp = "C:/Users/SAPHIR~1/AppData/Local/Temp/claude/1c11d2ce0030b2d4/5c4410c7-1755-4db2-9956-c88b7487f3ac/scratchpad/"
    bg = Image.new("RGBA", im.size, (200, 60, 120, 255)); bg.alpha_composite(im)
    bg.convert("RGB").resize((480, 750)).save(sp + "fb_cut.png"); print(im.split()[3].getbbox())

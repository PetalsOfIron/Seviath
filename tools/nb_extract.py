"""Cut the Northbeam logo out of its pale gradient background (transparent PNG, no halos)."""
import numpy as np
from PIL import Image

SRC = "C:/Users/SaphiresSilver/Projects/portfolio/images/Northbeamlogo.png"


def cutout():
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
    bg = a[40, :, :]                                   # background only changes left to right
    d = np.abs(a - bg[None, :, :]).max(-1)
    alpha = np.clip((d - 7) / 20, 0, 1)
    safe = np.maximum(alpha, 1e-3)[..., None]
    fg = ((a - (1 - alpha[..., None]) * bg[None]) / safe).clip(0, 255)
    out = np.dstack([fg, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


if __name__ == "__main__":
    im = cutout()
    sp = "C:/Users/SAPHIR~1/AppData/Local/Temp/claude/1c11d2ce0030b2d4/5c4410c7-1755-4db2-9956-c88b7487f3ac/scratchpad/"
    bg = Image.new("RGBA", im.size, (14, 24, 52, 255)); bg.alpha_composite(im)
    bg.convert("RGB").resize((1000, 1000), Image.LANCZOS).save(sp + "nb_cut.png")
    print(im.getbbox(), im.split()[3].getbbox())

"""Remove the play-button overlay from the Starcaller artwork and repaint the hair strand that ran under it."""
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = "C:/Users/SaphiresSilver/Documents/twitch/character2_original.jpg"
DST = "C:/Users/SaphiresSilver/Documents/twitch/character2.png"
im = cv2.imread(SRC)
m = np.zeros(im.shape[:2], np.uint8)
cv2.circle(m, (602, 341), 30, 255, -1)
bg = cv2.inpaint(im, m, 9, cv2.INPAINT_NS)
bg = cv2.GaussianBlur(bg, (0, 0), 0.01)
# soften the inpainted disc so it matches the grain of the night sky
blur = cv2.GaussianBlur(bg, (0, 0), 3)
soft = cv2.GaussianBlur(m, (0, 0), 4) / 255.0
bg = (bg * (1 - soft[..., None] * 0.55) + blur * (soft[..., None] * 0.55)).astype(np.uint8)
pil = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert("RGBA")
# repaint the strand (white -> cyan, tapering) through the gap
K = 6
lay = Image.new("RGBA", (pil.width * K, pil.height * K), (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
pts = [(548, 311.5), (566, 321), (585, 329.5), (603, 337.5), (628, 346.5), (642, 351)]
cols = [(246, 250, 255), (244, 250, 255), (222, 246, 255), (176, 234, 255), (140, 224, 252), (128, 216, 250)]
wid = [15, 14.5, 13.5, 12.5, 11.5, 10.5]
def lerp(a, b, t): return a + (b - a) * t
N = 60
samples = []
for i in range(N + 1):
    f = i / N * (len(pts) - 1)
    j = min(int(f), len(pts) - 2); t = f - j
    x = lerp(pts[j][0], pts[j + 1][0], t); y = lerp(pts[j][1], pts[j + 1][1], t)
    w = lerp(wid[j], wid[j + 1], t)
    c = tuple(int(lerp(cols[j][k], cols[j + 1][k], t)) for k in range(3))
    samples.append((x, y, w, c))
for i in range(N):
    x0, y0, w0, c0 = samples[i]
    x1, y1, w1, c1 = samples[i + 1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    poly = [((x0 + nx * w0 / 2) * K, (y0 + ny * w0 / 2) * K), ((x1 + nx * w1 / 2) * K, (y1 + ny * w1 / 2) * K),
            ((x1 - nx * w1 / 2) * K, (y1 - ny * w1 / 2) * K), ((x0 - nx * w0 / 2) * K, (y0 - ny * w0 / 2) * K)]
    d.polygon(poly, fill=c0 + (255,))
# fade the strand in at both ends so it joins the existing painting
a = lay.split()[3]
fade = Image.new("L", lay.size, 255)
fd = ImageDraw.Draw(fade)
for x in range(int(548 * K), int(562 * K)):
    fd.line([(x, 0), (x, lay.height)], fill=int(255 * (x - 548 * K) / (14 * K)))
for x in range(int(632 * K), int(644 * K)):
    fd.line([(x, 0), (x, lay.height)], fill=int(255 * (1 - (x - 632 * K) / (12 * K))))
from PIL import ImageChops
lay.putalpha(ImageChops.multiply(a, fade))
lay = lay.filter(ImageFilter.GaussianBlur(0.9 * K / 2)).resize(pil.size, Image.LANCZOS)
pil = Image.alpha_composite(pil, lay)
pil.save(DST)
pil.crop((480, 270, 780, 430)).resize((1200, 640), Image.LANCZOS).save("C:/Users/SAPHIR~1/AppData/Local/Temp/claude/9e8a5a803a320e6c/5c4410c7-1755-4db2-9956-c88b7487f3ac/scratchpad/pb2.png")

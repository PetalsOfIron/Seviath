#!/usr/bin/env python3
"""Traced SVG vector files for the neutral brand kits (OpenCV contour tracing, no extra libraries).
Writes vector_*.svg next to the other kit files in Documents/twitch/Neutral/Kits/<kit>/"""
import sys
from pathlib import Path
import cv2
import numpy as np

ROOT = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral/Kits")
KITS = ["Business_Consulting_Brand_Kit", "Sports_Footwear_Brand_Kit", "Luxury_Perfume_Brand_Kit", "Football_Club_Brand_Kit"]
SIZE = 1000


def contours_path(mask, eps=1.2, min_area=18):
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cs:
        if cv2.contourArea(c) < min_area:
            continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        if len(a) < 3:
            continue
        parts.append("M" + " L".join("%d %d" % (x, y) for x, y in a) + "Z")
    return " ".join(parts)


def load(path):
    im = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA)
    h, w = im.shape[:2]
    s = SIZE / max(h, w)
    return cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)


def svg_mono(path, color):
    im = load(path)
    mask = (im[..., 3] > 128).astype(np.uint8) * 255
    d = contours_path(mask)
    h, w = mask.shape
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><path fill="{color}" fill-rule="evenodd" d="{d}"/></svg>'


def svg_color(path, k=10):
    im = load(path)
    alpha = im[..., 3] > 128
    rgb = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2RGB)
    rgb = cv2.bilateralFilter(rgb, 7, 40, 7)
    pix = rgb[alpha].astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1.0)
    _, lab, cen = cv2.kmeans(pix, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    idx = np.full(alpha.shape, -1, np.int32)
    idx[alpha] = lab[:, 0]
    h, w = alpha.shape
    order = sorted(range(k), key=lambda i: -(idx == i).sum())
    layers = []
    base = np.zeros((h, w), np.uint8)
    for n, i in enumerate(order):
        m = (idx == i).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        if n == 0:
            m = cv2.dilate(alpha.astype(np.uint8) * 255, np.ones((3, 3), np.uint8))      # biggest colour sits underneath as the base layer
        d = contours_path(m)
        if d:
            c = cen[i].astype(int)
            layers.append('<path fill="#%02X%02X%02X" fill-rule="evenodd" d="%s"/>' % (c[0], c[1], c[2], d))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">' + "".join(layers) + "</svg>"


for kit in KITS:
    d = ROOT / kit
    if not (d / "logo_color.png").exists():
        continue
    (d / "vector_logo_color.svg").write_text(svg_color(d / "logo_color.png"), encoding="utf-8")
    (d / "vector_logo_black.svg").write_text(svg_mono(d / "logo_black.png", "#141416"), encoding="utf-8")
    (d / "vector_logo_white.svg").write_text(svg_mono(d / "logo_white.png", "#FFFFFF"), encoding="utf-8")
    for f in sorted(d.glob("vector_*.svg")):
        print(kit, f.name, round(f.stat().st_size / 1e3), "KB")

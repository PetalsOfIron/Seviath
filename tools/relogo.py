#!/usr/bin/env python3
"""Regenerate only the Floral and Purple logos (+ X profile pictures) with the emblem centred on the canvas."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_neutral_old as mo

def floral():
    lg = mo.patched("make_floral.py", [('text_mask(canvas.size, "P", fP, (cx, cy + 290))', 'text_mask(canvas.size, " ", fP, (cx, cy + 290))'),
        ('text_mask(canvas.size, "Petals Of Iron", fW, (cx, 1790))', 'text_mask(canvas.size, " ", fW, (cx, 1790))'),
        ("cx, cy, D = 1000, 740, 1380", "cx, cy, D = 1000, 1000, 1380")], mo.LOGO_LINES)
    mo.finish(mo.NEUTRAL / "Floral", "Floral", lg.floral_logo())

def purple():
    lg = mo.patched("make_purple.py", [('"P", (cx, cy + 270), 720', '" ", (cx, cy + 270), 720'), ('"Petals Of Iron", (cx, 1790), 215', '" ", (cx, 1790), 215'),
        ("cx, cy, D = 1000, 800, 1400", "cx, cy, D = 1000, 1000, 1400")], mo.LOGO_LINES)
    mo.finish(mo.NEUTRAL / "Purple", "Purple", lg.logo())

if __name__ == "__main__":
    floral(); purple()

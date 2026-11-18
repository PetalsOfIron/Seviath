#!/usr/bin/env python3
"""Text-free wide banners (the Twitch-style banner art without lettering) for the neutral brand kits."""
from pathlib import Path
import make_brands as mb

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral/Kits")
mb.wordmark = lambda canvas, *a, **k: canvas      # no lettering: the buyer adds their own name
for fn, folder in ((mb.tessel_banner, "Sports_Footwear_Brand_Kit"), (mb.perfum_banner, "Luxury_Perfume_Brand_Kit")):
    img = fn().convert("RGB")
    img.save(OUT / folder / "banner_wide_3000x1000.png", optimize=True)
    img.resize((1500, 500)).save(OUT / folder / "banner_wide_1500x500.png", optimize=True)
    print("banner", folder)

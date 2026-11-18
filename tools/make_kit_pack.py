#!/usr/bin/env python3
"""Zips + covers + thumbnail for the text-free brand kits. Output: Documents/twitch/Neutral/Kits/<folder>_pack/"""
import sys, zipfile
from pathlib import Path
from PIL import Image
import make_pack_full as pf
import make_gumroad as mg

KITS = {"Northbeam": ("Business_Consulting_Brand_Kit", "BUSINESS"), "Strikeline": ("Football_Club_Brand_Kit", "FOOTBALL CLUB"), "Tessel": ("Sports_Footwear_Brand_Kit", "SPORTS FOOTWEAR"), "Perfum": ("Luxury_Perfume_Brand_Kit", "LUXURY PERFUME")}
ROOT = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral/Kits")
W, H = 1280, 720
for key in (sys.argv[1:] or KITS):
    folder, title = KITS[key]
    src = ROOT / folder
    out = ROOT / (folder + "_pack")
    out.mkdir(exist_ok=True)
    for f in out.glob("*"):
        f.unlink()
    # opaque artwork goes into the zips as high-quality JPG (much smaller); logos with transparency stay PNG
    stage = ROOT / (folder + "_stage")
    stage.mkdir(exist_ok=True)
    for f in stage.glob("*"):
        f.unlink()
    for f in sorted(src.glob("*")):
        if f.suffix == ".png" and f.name.startswith(("banner", "post", "story", "size_", "slide", "business_card", "letterhead", "colour")):
            Image.open(f).convert("RGB").save(stage / (f.stem + ".jpg"), quality=93, subsampling=0, optimize=True)
        else:
            (stage / f.name).write_bytes(f.read_bytes())
    (stage / "VECTOR_README.txt").write_text(chr(10).join(["VECTOR FILES", "",
        "vector_logo_color.svg, vector_logo_black.svg and vector_logo_white.svg are scalable SVG versions of the logo emblem. Open them in Illustrator, Inkscape, Affinity Designer, Figma or Canva and scale them to any size without losing sharpness.",
        "The colour version is a traced vector with a limited number of flat colours; the black and white versions are clean one-colour silhouettes. No lettering is included.", ""]), encoding="utf-8")
    for v in src.glob("vector_*.svg"):
        (stage / v.name).write_bytes(v.read_bytes())
    files = sorted(stage.glob("*"))
    parts = {"brand_kit_logos_and_stationery.zip": [f for f in files if f.name.startswith(("logo", "profile", "favicon", "colour", "README", "business", "letterhead", "slide"))],
             "brand_kit_banners_and_social.zip": [f for f in files if f.name.startswith(("banner", "post", "story", "README"))],
             "brand_kit_more_sizes.zip": [f for f in files if f.name.startswith(("size_", "README"))],
             "brand_kit_vector_files.zip": [f for f in files if f.name.startswith(("vector_", "VECTOR_"))]}
    for zn, fl in parts.items():
        with zipfile.ZipFile(out / zn, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for f in fl:
                z.write(f, f"{folder}/{f.name}")
        print(zn, round((out / zn).stat().st_size / 1e6, 1), "MB")
    P = lambda n: src / n
    _, acc = pf.pal(key)
    line = "LOGO · BANNERS · SOCIAL POSTS · BUSINESS CARD · LETTERHEAD · SLIDES · NO TEXT"
    # cover 1
    img = pf.base(key, W, H)
    img = pf.tt(img, title + " BRAND KIT", (60, 100), 42)
    img = pf.tt(img, "FULL BRAND IDENTITY · ADD YOUR OWN NAME · READY FOR ANY COMPANY", (62, 144), 16, acc, acc, track=4)
    img = pf.card(img, P("logo_color.png"), (60, 190, 360, 360))
    img = pf.card(img, P("banner_twitch.png"), (450, 190, 520, 208))
    img = pf.card(img, P("business_card_front.png"), (450, 420, 250, 143))
    img = pf.card(img, P("business_card_back_blank.png"), (720, 420, 250, 143))
    img = pf.card(img, P("post_square.png"), (1000, 190, 240, 240))
    img = pf.card(img, P("slide_title_background.png"), (1000, 450, 240, 135))
    img.convert("RGB").save(out / "cover_1.png", optimize=True)
    # cover 2: logo versions
    img = pf.base(key, W, H)
    img = pf.tt(img, "LOGO VERSIONS · NO LETTERING", (60, 100), 42)
    img = pf.tt(img, "COLOUR · WHITE · BLACK · ON DARK · PROFILE PICTURE · FAVICONS", (62, 144), 16, acc, acc, track=4)
    for i, nm in enumerate(("logo_color", "logo_white", "logo_black", "logo_on_dark_background")):
        img = pf.card(img, P(nm + ".png"), (60 + i * 305, 200, 285, 285), back=(120, 120, 130) if nm == "logo_white" else (235, 235, 240) if nm == "logo_black" else (8, 10, 22))
    img = pf.card(img, P("profile_picture.png"), (60, 510, 160, 160))
    img = pf.card(img, P("favicon_512.png"), (240, 560, 100, 100))
    img = pf.card(img, P("colour_palette.png"), (380, 540, 600, 134))
    img.convert("RGB").save(out / "cover_2.png", optimize=True)
    # cover 3: banners
    img = pf.base(key, W, H)
    img = pf.tt(img, "BANNERS · SOCIAL · BLANK LAYOUTS", (60, 100), 42)
    img = pf.tt(img, "LINKEDIN · X (TWITTER) · FACEBOOK · YOUTUBE · TWITCH · STORY · LETTERHEAD", (62, 144), 16, acc, acc, track=4)
    img = pf.card(img, P("banner_wide_3000x1000.png"), (60, 190, 560, 187))
    img = pf.card(img, P("banner_facebook.png"), (640, 190, 580, 220))
    img = pf.card(img, P("banner_x_twitter_header.png"), (640, 430, 580, 193))
    img = pf.card(img, P("story.png"), (60, 530, 90, 160)) if False else img
    img = pf.card(img, P("letterhead_blank.png"), (60, 530, 120, 170))
    img = pf.card(img, P("story.png"), (200, 530, 96, 170))
    img = pf.card(img, P("banner_linkedin.png"), (330, 560, 290, 72))
    img.convert("RGB").save(out / "cover_3.png", optimize=True)
    # thumbnail
    S = 1000
    img = pf.base(key, S, S)
    img = pf.tt(img, title, (S // 2, 120), 56, anchor="center")
    img = pf.tt(img, "COMPLETE BRAND KIT · NO TEXT", (S // 2, 176), 24, acc, acc, anchor="center", track=12)
    img = pf.card(img, P("logo_color.png"), (80, 230, 380, 380))
    img = pf.card(img, P("banner_twitch.png"), (480, 230, 440, 176))
    img = pf.card(img, P("post_square.png"), (480, 420, 215, 215))
    img = pf.card(img, P("business_card_front.png"), (710, 420, 210, 120))
    img = pf.card(img, P("business_card_back_blank.png"), (710, 555, 210, 120))
    img = pf.card(img, P("colour_palette.png"), (80, 650, 380, 85))
    img = pf.tt(img, "LOGO + VECTOR SVG · BANNERS · 20+ SIZES · STATIONERY", (S // 2, 900), 20, (210, 214, 228), (210, 214, 228), anchor="center", track=5)
    img.convert("RGB").save(out / "thumb.png", optimize=True)
    print("built", key)

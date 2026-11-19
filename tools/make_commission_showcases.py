#!/usr/bin/env python3
"""Showcase boards (1600x900) for the Ko-fi commission listings: four real examples of each kind of work on the shop's cream look.
    python tools/make_commission_showcases.py"""
from pathlib import Path
from PIL import Image, ImageDraw
import make_shop_designs as m

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
DOC = Path("C:/Users/SaphiresSilver/Documents/twitch")
OUT = DOC / "Shops" / "commissions"
D = IMG / "design"
SC = DOC / "Showcases"
BOARDS = {
    "show_poster": ("Poster design", [D / "Tessel/tessel_poster.png", D / "Perfum/perfum_poster.png", D / "Football/football_poster.png", D / "Northbeam/northbeam_poster.png"]),
    "show_event": ("Social posts, tickets & posters", [D / "Football/football_match_day_poster.png", D / "Football/football_ticket.png", D / "Football/football_story.png", D / "Football/football_post_square.png"]),
    "show_stationery": ("Business cards & stationery", [D / "Tessel/tessel_business_card_front.png", D / "Perfum/perfum_letterhead.png", D / "Northbeam/northbeam_business_card_front.png", D / "Football/football_email_signature.png"]),
    "show_brandkit": ("Brand kits", [DOC / "CompanyKits/Tessel/board_1_identity.png", DOC / "CompanyKits/Perfum/board_1_identity.png", DOC / "CompanyKits/Northbeam/board_1_identity.png", DOC / "CompanyKits/Strikeline/board_1_identity.png"]),
    "show_logo": ("Logo design", [DOC / "Neutral/Crimson/Logo/crimson_logo.png", DOC / "Neutral/Hood/Logo/logo.png", DOC / "Neutral/Helmet/Logo/logo.png", DOC / "Neutral/Purple/Logo/logo.png"]),
    "show_banner": ("Banners & headers", [IMG / "twitch/Banner/petals_rowan_trees_banner.png", IMG / "twitch/Hood/Banner/petals_gamer_banner.png", D / "Football/football_banner_twitch.png", D / "Perfum/perfum_banner_twitch.png"]),
    "show_panels": ("Twitch panels", [IMG / "twitch/addons.png", IMG / "twitch/Crimson/Panels/crimson_about.png", IMG / "twitch/Purple/Panels/about_me.png", IMG / "twitch/Floral/Panels/about_me.png"]),
    "show_screens": ("Stream screens", [IMG / "twitch/Crimson/Screens/crimson_starting_soon.png", IMG / "twitch/Purple/Screens/starting_soon.png", IMG / "twitch/Floral/Screens/starting_soon.png", IMG / "twitch/Hood/Screens/starting_soon.png"]),
}


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def board(title, paths):
    W, H = 1600, 900
    img = m.cover_crop(m.LEAVES, W, H)
    img.alpha_composite(Image.new("RGBA", (W, H), m.CREAM + (232,)))
    d = ImageDraw.Draw(img)
    d.text((70, 70), title.upper(), font=m.sans(46), fill=m.WINE, anchor="lm")
    d.text((W - 70, 70), "EXAMPLES OF MY WORK", font=m.sans(30), fill=m.SUB, anchor="rm")
    gx, gy, cw, ch, gap = 70, 130, (W - 140 - 40) // 2, (H - 130 - 70 - 40) // 2, 40
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGBA")
        t = fit(im, cw, ch)
        x, y = gx + (i % 2) * (cw + gap) + (cw - t.width) // 2, gy + (i // 2) * (ch + gap) + (ch - t.height) // 2
        m.shadowed(img, t, (x, y), blur=10, alpha=100)
    return img.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for k, (t, ps) in BOARDS.items():
        missing = [p for p in ps if not p.exists()]
        if missing:
            print(k, "MISSING", missing)
            continue
        board(t, ps).save(OUT / f"{k}.png", optimize=True)
        print(k)

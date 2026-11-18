#!/usr/bin/env python3
"""Text-free brand kits for sale (no brand name, no tagline, nothing a buyer cannot replace): emblem logo versions, avatar, favicons,
banners and social posts without lettering, blank business card / letterhead / slides with the emblem and colour accents, and a colour palette.
Output: Documents/twitch/Neutral/Kits/<folder>/        py make_kit_neutral.py tessel|perfum"""
import sys
from pathlib import Path

key = sys.argv[1]
sys.argv = sys.argv[:1]
import make_kit as mk
from make_kit import ImageDraw, Image, crop_pad, fit, put, grain, solid, font
import zipfile

FOLDERS = {"tessel": "Sports_Footwear_Brand_Kit", "perfum": "Luxury_Perfume_Brand_Kit"}
OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral/Kits") / FOLDERS[key]
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*"):
    old.unlink()
T = mk.THEMES[key]
n = "brand"


def save(img, name, rgba=False):
    p = OUT / name
    if name.endswith(".ico"):
        img.save(p, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    else:
        (img if rgba else img.convert("RGB")).save(p, optimize=True)
    print("saved", name)


em = crop_pad(T["emblem"]())
em_w, em_k = crop_pad(mk.mono_emblem(key, (255, 255, 255))), crop_pad(mk.mono_emblem(key, (20, 20, 22)))
dark_bg = lambda s: T["alt_bg"](s) if T["hero"] == "light" else T["hero_bg"](s)

save(fit(em, 2000, 2000), "logo_color.png", rgba=True)
save(fit(em_w, 2000, 2000), "logo_white.png", rgba=True)
save(fit(em_k, 2000, 2000), "logo_black.png", rgba=True)
save(put(dark_bg((2000, 2000)), fit(em, 1500, 1500), center=(1000, 1000), shadow_op=0.3), "logo_on_dark_background.png")
save(mk.avatar(T, em), "profile_picture.png")
for s in (512, 192, 32):
    save(mk.favicon(T, em, s), f"favicon_{s}.png", rgba=True)
save(mk.favicon(T, em, 64), "favicon.ico")


def text_free_banner(W, H):
    bg = T["hero_bg"]((W, H))
    bg = put(bg, fit(em, H * 0.78, H * 0.78), center=(W * 0.5, H * 0.5), shadow_op=0.3)
    ImageDraw.Draw(bg).line([(W * 0.08, H * 0.5), (W * 0.36, H * 0.5)], fill=T["accent"] + (255,), width=max(2, int(H * 0.01)))
    ImageDraw.Draw(bg).line([(W * 0.64, H * 0.5), (W * 0.92, H * 0.5)], fill=T["accent"] + (255,), width=max(2, int(H * 0.01)))
    return grain(bg, 8)


for nm, (W, H) in (("linkedin", (1584, 396)), ("x_twitter_header", (1500, 500)), ("facebook", (1640, 624)), ("youtube", (2560, 1440)), ("twitch", (2400, 960)), ("link_preview", (1200, 630))):
    save(text_free_banner(W, H), f"banner_{nm}.png")
for nm, (W, H) in (("post_square", (1080, 1080)), ("story", (1080, 1920))):
    img = T["hero_bg"]((W, H))
    img = put(img, fit(em, W * 0.66, H * 0.5), center=(W / 2, H * 0.5), shadow_op=0.3)
    save(grain(img, 8), f"{nm}.png")

# more sizes companies use
def emblem_layout(W, H, scale=0.55, ghost_line=True):
    bg = T["hero_bg"]((W, H))
    side = min(W, H) * scale
    bg = put(bg, fit(em, side, side), center=(W / 2, H / 2), shadow_op=0.3)
    return grain(bg, 8)


for nm, (W, H) in (("instagram_post_portrait_1080x1350", (1080, 1350)), ("linkedin_post_1200x627", (1200, 627)), ("x_post_1600x900", (1600, 900)),
                   ("youtube_thumbnail_1280x720", (1280, 720)), ("pinterest_pin_1000x1500", (1000, 1500)), ("email_header_1200x400", (1200, 400)),
                   ("zoom_background_1920x1080", (1920, 1080)), ("facebook_post_1200x630", (1200, 630)), ("poster_A4_2480x3508", (2480, 3508)),
                   ("flyer_A5_1748x2480", (1748, 2480)), ("roll_up_banner_2000x4800", (2000, 4800))):
    sc = 0.3 if H > W * 1.8 else (0.55 if "email" not in nm else 0.8)
    save(emblem_layout(W, H, sc), f"size_{nm}.png")
save(put(Image.new("RGBA", (1024, 1024), T["deep"] + (255,)), fit(em, 860, 860), center=(512, 512)), "size_app_icon_1024x1024.png")
save(put(Image.new("RGBA", (400, 400), T["deep"] + (255,)), fit(em, 340, 340), center=(200, 200)), "size_linkedin_logo_400x400.png")

# business card: front with the emblem, back blank with accent shapes (add your own text)
W, H = 1050, 600
front = put(dark_bg((W, H)), fit(em, 380, 380), center=(W / 2, H / 2), shadow_op=0.3)
back = Image.new("RGBA", (W, H), T["paper"] + (255,))
back = put(back, fit(em, 210, 210), topleft=(70, 66))
ImageDraw.Draw(back).rectangle((70, 320, W - 70, 326), fill=T["accent"] + (255,))
ImageDraw.Draw(back).polygon([(W, H), (W - 200, H), (W, H - 200)], fill=T["accent"] + (255,))
save(front, "business_card_front.png")
save(back, "business_card_back_blank.png")
# letterhead without text
W, H = 2480, 3508
page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
page.paste(Image.new("RGBA", (W, 36), T["accent"] + (255,)), (0, 0))
page = put(page, fit(em, 300, 300), topleft=(200, 150))
ghost = solid(fit(em, 1500, 1500), T["accent"])
ghost.putalpha(ghost.split()[3].point(lambda v: int(v * 0.06)))
page = put(page, ghost, center=(W - 400, H - 600))
ImageDraw.Draw(page).rectangle((200, H - 340, W - 200, H - 334), fill=T["accent"] + (255,))
save(page, "letterhead_blank.png")
page.convert("RGB").save(OUT / "letterhead_blank.pdf", resolution=300)
# slides without text
W, H = 1920, 1080
t = put(dark_bg((W, H)), fit(em, 640, 820), center=(W / 2, H / 2), shadow_op=0.3)
c = Image.new("RGBA", (W, H), T["paper"] + (255,))
c.paste(Image.new("RGBA", (W, 20), T["accent"] + (255,)), (0, 0))
c = put(c, fit(em, 140, 140), topleft=(W - 220, 60))
ImageDraw.Draw(c).rectangle((120, 250, 380, 256), fill=T["accent"] + (255,))
save(t, "slide_title_background.png")
save(c, "slide_content_background.png")
# colour palette
img = Image.new("RGB", (2500, 560), (245, 245, 247))
d = ImageDraw.Draw(img)
lines = []
for i, (nme, col) in enumerate(T["swatches"]):
    x = 60 + i * 480
    d.rounded_rectangle((x, 60, x + 420, 380), radius=24, fill=col, outline=(150, 150, 160), width=2)
    hexv = "#%02X%02X%02X" % tuple(col)
    d.text((x, 410), hexv, fill=(60, 60, 70), font=font("segoeui.ttf", 54))
    lines.append(hexv)
img.save(OUT / "colour_palette.png", optimize=True)
(OUT / "colours.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
(OUT / "README.txt").write_text("\n".join([
    "BRAND KIT - how to use", "",
    "This kit has no brand name and no text on any of the files, so you can add your own name and wording.",
    "logo_*.png: emblem on transparent background (colour, white, black) and on a dark background. No lettering.",
    "profile_picture.png, favicon_*.png, favicon.ico: avatar and site icons.",
    "banner_*.png, post_square.png, story.png: social media graphics sized for LinkedIn, X (Twitter), Facebook, YouTube, Twitch and link previews.",
    "size_*.png: more sizes in the file names - Instagram portrait post, LinkedIn and Facebook posts, X post, YouTube thumbnail, Pinterest pin, email header, Zoom background, A4 poster, A5 flyer, roll-up banner, app icon, LinkedIn logo.",
    "business_card_front.png / business_card_back_blank.png, letterhead_blank.png / .pdf, slide_*_background.png: blank layouts - add your own text in Canva, Photoshop, Word or PowerPoint.",
    "colour_palette.png and colours.txt: the colour codes of the kit.", ""]), encoding="utf-8")
print("done", key)

#!/usr/bin/env python3
"""Text-free football club brand kit (the blue one) for sale, same file set as make_kit_neutral.py. Output: Documents/twitch/Neutral/Kits/Football_Club_Brand_Kit"""
from pathlib import Path
import make_football as mf
from make_football import ImageDraw, Image, crop_pad, fit, put, solid, stencil, NAVY, ABYSS, CYAN, CYAN_D, WHITE, PALE
from art import grain

OUT = Path("C:/Users/SaphiresSilver/Documents/twitch/Neutral/Kits/Football_Club_Brand_Kit")
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*"):
    old.unlink()


def save(img, name, rgba=False):
    p = OUT / name
    if name.endswith(".ico"):
        img.save(p, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    else:
        (img if rgba else img.convert("RGB")).save(p, optimize=True)
    print("saved", name)


em = crop_pad(mf.emblem())
em_w, em_k = crop_pad(stencil(em, WHITE)), crop_pad(stencil(em, (20, 20, 22)))
dark = lambda s: mf.bg_dark(s)
save(fit(em, 2000, 2000), "logo_color.png", rgba=True)
save(fit(em_w, 2000, 2000), "logo_white.png", rgba=True)
save(fit(em_k, 2000, 2000), "logo_black.png", rgba=True)
save(put(dark((2000, 2000)), fit(em, 1500, 1500), center=(1000, 1000), shadow_op=0.4), "logo_on_dark_background.png")
save(mf.avatar(em), "profile_picture.png")
for s in (512, 192, 32):
    save(mf.favicon(em, s), f"favicon_{s}.png", rgba=True)
save(mf.favicon(em, 64), "favicon.ico")


def layout(W, H, scale=0.62, lines=False):
    bg = dark((W, H))
    side = min(W, H) * scale
    bg = put(bg, fit(em, side, side), center=(W / 2, H / 2), shadow_op=0.4)
    if lines:
        d = ImageDraw.Draw(bg)
        d.line([(W * 0.06, H * 0.5), (W * 0.34, H * 0.5)], fill=CYAN + (255,), width=max(2, int(H * 0.01)))
        d.line([(W * 0.66, H * 0.5), (W * 0.94, H * 0.5)], fill=CYAN + (255,), width=max(2, int(H * 0.01)))
    return grain(bg, 8)


for nm, (W, H) in (("linkedin", (1584, 396)), ("x_twitter_header", (1500, 500)), ("facebook", (1640, 624)), ("youtube", (2560, 1440)), ("twitch", (2400, 960)), ("link_preview", (1200, 630)), ("wide_3000x1000", (3000, 1000))):
    save(layout(W, H, 0.78, lines=W / H > 2), f"banner_{nm}.png")
save(layout(1080, 1080, 0.66), "post_square.png")
save(layout(1080, 1920, 0.66), "story.png")
for nm, (W, H) in (("instagram_post_portrait_1080x1350", (1080, 1350)), ("linkedin_post_1200x627", (1200, 627)), ("x_post_1600x900", (1600, 900)),
                   ("youtube_thumbnail_1280x720", (1280, 720)), ("pinterest_pin_1000x1500", (1000, 1500)), ("email_header_1200x400", (1200, 400)),
                   ("zoom_background_1920x1080", (1920, 1080)), ("facebook_post_1200x630", (1200, 630)), ("poster_A4_2480x3508", (2480, 3508)),
                   ("flyer_A5_1748x2480", (1748, 2480)), ("roll_up_banner_2000x4800", (2000, 4800))):
    sc = 0.3 if H > W * 1.8 else (0.8 if "email" in nm else 0.55)
    save(layout(W, H, sc), f"size_{nm}.png")
save(put(Image.new("RGBA", (1024, 1024), ABYSS + (255,)), fit(em, 860, 860), center=(512, 512)), "size_app_icon_1024x1024.png")
save(put(Image.new("RGBA", (400, 400), ABYSS + (255,)), fit(em, 340, 340), center=(200, 200)), "size_linkedin_logo_400x400.png")
# match-day / club extras without lettering
save(layout(2480, 3508, 0.6), "poster_match_day_blank_A4.png")
# stationery (blank)
W, H = 1050, 600
front = put(dark((W, H)), fit(em, 400, 400), center=(W / 2, H / 2), shadow_op=0.4)
back = Image.new("RGBA", (W, H), (244, 247, 250, 255))
back = put(back, fit(em, 210, 210), topleft=(70, 66))
ImageDraw.Draw(back).rectangle((70, 320, W - 70, 326), fill=CYAN + (255,))
ImageDraw.Draw(back).polygon([(W, H), (W - 200, H), (W, H - 200)], fill=CYAN + (255,))
save(front, "business_card_front.png")
save(back, "business_card_back_blank.png")
W, H = 2480, 3508
page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
page.paste(Image.new("RGBA", (W, 36), CYAN + (255,)), (0, 0))
page = put(page, fit(em, 300, 300), topleft=(200, 150))
ghost = solid(fit(em, 1500, 1500), CYAN)
ghost.putalpha(ghost.split()[3].point(lambda v: int(v * 0.06)))
page = put(page, ghost, center=(W - 400, H - 600))
ImageDraw.Draw(page).rectangle((200, H - 340, W - 200, H - 334), fill=CYAN + (255,))
save(page, "letterhead_blank.png")
page.convert("RGB").save(OUT / "letterhead_blank.pdf", resolution=300)
t = put(dark((1920, 1080)), fit(em, 640, 820), center=(960, 540), shadow_op=0.4)
c = Image.new("RGBA", (1920, 1080), (244, 247, 250, 255))
c.paste(Image.new("RGBA", (1920, 20), CYAN + (255,)), (0, 0))
c = put(c, fit(em, 140, 140), topleft=(1700, 60))
ImageDraw.Draw(c).rectangle((120, 250, 380, 256), fill=CYAN + (255,))
save(t, "slide_title_background.png")
save(c, "slide_content_background.png")
sw = [("Cyan", CYAN), ("Deep blue", mf.DEEP), ("Navy", NAVY), ("Abyss", ABYSS), ("Pale grey", PALE)]
img = Image.new("RGB", (2500, 560), (245, 245, 247))
d = ImageDraw.Draw(img)
lines = []
for i, (nme, col) in enumerate(sw):
    x = 60 + i * 480
    d.rounded_rectangle((x, 60, x + 420, 380), radius=24, fill=col, outline=(150, 150, 160), width=2)
    hexv = "#%02X%02X%02X" % tuple(col)
    d.text((x, 410), hexv, fill=(60, 60, 70), font=mf.font("segoeui.ttf", 54))
    lines.append(hexv)
img.save(OUT / "colour_palette.png", optimize=True)
(OUT / "colours.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
(OUT / "README.txt").write_text("\n".join([
    "BRAND KIT - how to use", "",
    "This kit has no club or brand name and no text on any file, so you can add your own name and wording.",
    "logo_*.png: crest on transparent background (colour, white, black) and on a dark background. No lettering.",
    "profile_picture.png, favicon_*.png, favicon.ico: avatar and site icons.",
    "banner_*.png, post_square.png, story.png: social media graphics sized for LinkedIn, X (Twitter), Facebook, YouTube, Twitch and link previews.",
    "size_*.png: more sizes in the file names - Instagram portrait post, LinkedIn and Facebook posts, X post, YouTube thumbnail, Pinterest pin, email header, Zoom background, A4 poster, A5 flyer, roll-up banner, app icon, LinkedIn logo.",
    "business_card_*, letterhead_blank, slide_*_background, poster_match_day_blank_A4: blank layouts - add your own text in Canva, Photoshop, Word or PowerPoint.",
    "colour_palette.png and colours.txt: the colour codes of the kit.", ""]), encoding="utf-8")
print("done")

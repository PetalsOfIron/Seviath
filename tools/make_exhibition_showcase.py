#!/usr/bin/env python3
"""4 showcase boards (1600x900) for the Urban Dictionary exhibition kit."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import make_exhibition as ex
import make_set_showcases as ss
import make_banner_gig as g

R = ex.OUT
O = R / "Showcase"
W, H = 1600, 900
def ld(p): return Image.open(R / p).convert("RGBA")
def C(p, w, h, back=(30, 28, 40)): return ss.card(ld(p), w, h, back, 8, pad=0)
def row(img, items, y, hh, x0=90, x1=1510, gap=20):
    ars = [ld(p).width / ld(p).height for p in items]
    h = min(hh, int((x1 - x0 - gap * (len(items) - 1)) / sum(ars)))
    x = x0 + ((x1 - x0) - (sum(ars) * h + gap * (len(items) - 1))) // 2
    for p, a in zip(items, ars):
        w = int(a * h)
        img = ss.drop(img, C(p, w, h), (x, y + (hh - h) // 2), 12, 0.5)
        x += w + gap
    return img
def board(t, sub):
    img = ss.bg((236, 20, 140), 1)
    return ss.head(img, t, sub, (255, 120, 190))

def b1():
    img = board("URBAN DICTIONARY", "STUDENT EXHIBITION  ·  VISUAL IDENTITY")
    img = row(img, ["Print/poster_A3.png", "Print/flyer_A5_back.png", "Print/invitation_front.png", "Print/invitation_back.png", "Print/program_cover_A5.png"], 215, 400)
    img = row(img, ["Brand/brand_guidelines.png"], 640, 220, 500, 1100)
    return img
def b2():
    img = board("PRINT & WALL", "PROGRAM  ·  WALL LABEL  ·  STATEMENT  ·  CERTIFICATE")
    img = row(img, ["Print/program_schedule_A4.png", "Print/artist_statement_panel_A4.png", "Print/wall_label_template.png"], 210, 420)
    img = row(img, ["Print/certificate_A4.png", "Tickets/ticket_opening_night.png"], 660, 200)
    return img
def b3():
    img = board("SIGNAGE & WEARABLES", "ENTRANCE  ·  ARROWS  ·  ROLL-UP  ·  BADGES  ·  TICKETS  ·  PIN  ·  STICKER")
    img = row(img, ["Signage/entrance_sign_A3.png", "Signage/arrow_right_A3.png", "Signage/opening_night_sign_A3.png", "Signage/roll_up_banner.png"], 205, 250)
    img = row(img, ["Wearables/badge_visitor.png", "Wearables/badge_student.png", "Wearables/badge_organizer.png", "Wearables/pin_button.png", "Wearables/sticker.png", "Tickets/ticket_exhibition_day.png"], 480, 380)
    return img
def b4():
    img = board("SOCIAL & DIGITAL", "STORY  ·  POSTS  ·  COVERS  ·  SLIDES  ·  EMAIL  ·  WEB")
    img = row(img, ["Social/instagram_story.png", "Social/post_save_the_date.png", "Social/post_opening_night.png", "Social/post_exhibition_days.png", "Social/instagram_post_square.png"], 205, 330)
    img = row(img, ["Social/facebook_event_cover.png", "Social/x_header.png", "Digital/slide_title.png", "Digital/web_banner.png"], 560, 300)
    return img

O.mkdir(parents=True, exist_ok=True)
for i, f in enumerate((b1, b2, b3, b4), 1):
    f().convert("RGB").save(O / ("board_%d.png" % i), optimize=True); print("saved", i)

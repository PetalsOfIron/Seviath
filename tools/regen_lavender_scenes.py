import sys
sys.argv = ["x", "C:/Users/SaphiresSilver/Documents/twitch/Lavender/Source/character_2000.png"]
sys.path.insert(0, "C:/Users/SaphiresSilver/Projects/portfolio/tools")
import make_lavender_kit as m

O2 = m.OUT / "Lavender_only"
m.scene(1200, 480, ["Live Stream"], "gaming  ·  art  ·  chat", label="welcome", size=118, with_portrait=False).convert("RGB").save(O2 / "Banner" / "profile_banner_1200x480.png", optimize=True)
m.scene(1500, 500, ["Live Stream"], "gaming  ·  art  ·  chat", label="welcome", size=122, with_portrait=False).convert("RGB").save(O2 / "Banner" / "x_header_1500x500.png", optimize=True)
screens = {"starting_soon": (["Starting", "Soon"], "the stream begins shortly"),
           "be_right_back": (["Be Right", "Back"], "back in a moment"),
           "offline": (["Stream", "Offline"], "see you next time"),
           "ending": (["Thanks for", "Watching"], "see you next stream")}
for k, (lines, sub) in screens.items():
    m.scene(1920, 1080, lines, sub, with_portrait=False).convert("RGB").save(O2 / "Screens" / f"{k}.png", optimize=True)
print("ok")

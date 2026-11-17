#!/usr/bin/env python3
"""
Portfolio generator - builds the whole static site from data/*.json.

Pages:  index.html (Portfolio), contacts.html, seviathstudio.html,
        portfolio.html (redirect to index), sitemap.xml, robots.txt, style.css

Edit data/projects.json for works and data/site.json for contact info and the
Seviathstudio download link, then run:

    python3 generate.py
"""
import hashlib
import json
import html
import re
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).parent
PROJECTS_FILE = ROOT / "data" / "projects.json"
SITE_FILE = ROOT / "data" / "site.json"


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------- portfolio

def render_button(project):
    title = esc(project.get("title", "Untitled"))
    href = esc(project.get("href", "#"))
    if project.get("type", "image") == "video":
        return f'<a class="proj-btn" href="{href}" target="_blank" rel="noopener">🎬 {title} (YouTube)</a>'
    return f'<a class="proj-btn" href="{href}" target="_blank" rel="noopener">{title}</a>'


def render_section(projects, section_id):
    if projects:
        buttons = "\n      ".join(render_button(p) for p in projects)
    else:
        buttons = '<p class="empty-note">No works added yet.</p>'
    return f'<div class="btn-grid" id="{section_id}">\n      {buttons}\n    </div>'


SECTIONS = [
    ("programming", "Programming", "programming-grid"),
    ("design", "Design", "design-grid"),
    ("twitch", "Twitch Design", "twitch-grid"),
    ("art-3D", "Illustration", "illustration-grid", "image"),
    ("art-3D", "3D", "video-grid", "video"),
]


SECTION_INFO = {
    "programming-grid": ("Programming & DevOps projects",
        "Software and DevOps projects by Santa Madara Neilande: World of Warcraft addons, a digital painting app, "
        "provisioning scripts and CI demos on GitHub."),
    "design-grid": ("Graphic design",
        "Graphic design work: brochures, posters, logos, banners and layouts."),
    "twitch-grid": ("Twitch design",
        "Twitch design for streamers: channel logos, stream banners and panels."),
    "illustration-grid": ("Illustration & character design",
        "Digital illustration and character design: elves, pirates, warriors and fantasy portraits."),
    "video-grid": ("3D art and Unity games",
        "3D environments and Unity game scenes shown as videos on YouTube."),
}


def abs_url(site, href):
    if href.startswith("http"):
        return href
    return site["url"].rstrip("/") + "/" + quote(href)


def section_ld(site, topic, sid, items):
    """schema.org ItemList so Google understands what each section contains."""
    elems = []
    for i, p in enumerate(items, 1):
        url = abs_url(site, p.get("href", ""))
        if sid == "programming-grid":
            thing = {"@type": "SoftwareSourceCode", "name": p["title"], "codeRepository": url}
        elif p.get("type", "image") == "video":
            thing = {"@type": "VideoObject", "name": p["title"], "url": url, "contentUrl": url}
        else:
            thing = {"@type": "ImageObject", "name": p["title"], "contentUrl": url,
                     "creator": {"@id": site["url"].rstrip("/") + "/#person"}}
        elems.append({"@type": "ListItem", "position": i, "item": thing})
    return {"@type": "ItemList", "name": f'{topic} - {site["name"]}', "itemListElement": elems}


# ------------------------------------------------------------ twitch assets
# Everything dropped into images/twitch/ shows up in the Twitch Design section automatically.
# Rules: one entry per design (the biggest size is used), and a GIF always wins over a PNG of the same design.
# GIFs repeat forever (the loop flag is added to the file when it is missing).

TWITCH_DIR = ROOT / "images" / "twitch"
TWITCH_GROUPS = [  # (folder, title, description used for alt text)
    ("", "Panels", "Twitch channel panel"),
    ("__points", "Channel point icons", "Twitch channel point icon"),
    ("Alert", "Alert", "Twitch stream alert animation"),
    ("Corner", "Corner", "Twitch stream corner animation"),
    ("Overlay", "Overlays", "Twitch stream overlay"),
    ("Badges", "Sub badges", "Twitch subscriber badge"),
    ("Flair", "Flair", "Twitch chat flair"),
    ("Starting", "Starting soon screen", "Twitch starting soon screen"),
    ("Brb", "Be right back screen", "Twitch be right back screen"),
    ("Offline", "Offline screen", "Twitch offline screen"),
    ("Logo", "Logos", "Twitch channel logo"),
    ("Banner", "Banners", "Twitch channel banner"),
    ("Emotes", "Emotes", "Twitch emote"),
    ("Emotes/Hype", "Hype emotes", "Twitch hype emote"),
    ("Emotes/Tier1", "Tier 1 emotes", "Twitch tier 1 sub emote"),
    ("Emotes/Tier2_3_Bits", "Tier 2, Tier 3 & Bits emotes", "Twitch tier 2, tier 3 and bits emote"),
]


THEME_SETS = ("Purple", "Floral")
THEME_FOLDERS = {"Panels": "", "Emotes": "Emotes", "Badges": "Badges", "Points": "__points", "Flair": "Flair",
                 "Overlay": "Overlay", "Alert": "Alert", "Logo": "Logo", "Banner": "Banner", "Screens": "Offline"}
THEME_FILES = {"offline": "Offline", "logo": "Logo", "banner": "Banner"}  # loose files in Floral/


def ensure_gif_loop(path):
    """Make sure the GIF repeats forever (adds the NETSCAPE looping extension when it is missing)."""
    data = path.read_bytes()
    if b"NETSCAPE2.0" in data or data[:6] not in (b"GIF87a", b"GIF89a"):
        return
    pos = 13 + (3 * 2 ** ((data[10] & 7) + 1) if data[10] & 0x80 else 0)   # right after the global colour table
    ext = bytes([0x21, 0xFF, 0x0B]) + b"NETSCAPE2.0" + bytes([3, 1, 0, 0, 0])
    path.write_bytes(data[:pos] + ext + data[pos:])


def image_size(path):
    head = path.read_bytes()[:26]
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return int.from_bytes(head[6:8], "little"), int.from_bytes(head[8:10], "little")
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def pretty_label(stem):
    stem = re.sub(r"^(\d+)_(\d)year", r"\1.\2 year", stem)
    stem = re.sub(r"(\d)([a-z])", r"\1 \2", stem).replace("_", " ")
    return stem[:1].upper() + stem[1:]


LARGE_DIR = ROOT / "images" / "twitch-large"


def upscale_factor(w):
    return 6 if w <= 80 else 4 if w < 400 else 1


def large_version(src, rel, is_gif, w, h):
    """Bigger, smooth copy of a small asset (badges, icons, emotes, panels). Returns the site path of the file to link.
    Uses Lanczos in premultiplied alpha (no dark halos) plus a light sharpen. Needs Pillow; without it the existing
    copy is used (the copies are committed, so the deploy does not need Pillow)."""
    k = upscale_factor(w)
    if k == 1:
        return "images/twitch/" + rel.as_posix()
    dest = LARGE_DIR / rel
    href = "images/twitch-large/" + rel.as_posix()
    if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return href
    try:
        from PIL import Image, ImageFilter, ImageSequence

        import numpy as np

        def shock(img, iters=2, r=2):
            """Edge sharpening for flat illustrations: each pixel takes the colour of the lightest or darkest
            neighbour, whichever is closer in brightness. Edges become crisp without colour fringes."""
            arr = np.asarray(img).astype(np.float32)
            rgb, alpha = arr[..., :3], Image.fromarray(arr[..., 3].astype("uint8"))
            hh, ww, _ = rgb.shape
            for _ in range(iters):
                lum = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1)
                pl = np.pad(lum, r, mode="edge")
                pr = np.pad(rgb, ((r, r), (r, r), (0, 0)), mode="edge")
                bmax = np.full((hh, ww), -1, np.float32)
                bmin = np.full((hh, ww), 1e9, np.float32)
                cmax, cmin = np.zeros_like(rgb), np.zeros_like(rgb)
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy > r * r + 1:
                            continue
                        l = pl[r + dy:r + dy + hh, r + dx:r + dx + ww]
                        c = pr[r + dy:r + dy + hh, r + dx:r + dx + ww]
                        m = l > bmax
                        bmax, cmax = np.where(m, l, bmax), np.where(m[..., None], c, cmax)
                        m = l < bmin
                        bmin, cmin = np.where(m, l, bmin), np.where(m[..., None], c, cmin)
                tmax, tmin = (bmax - lum) < (lum - bmin), (bmax - lum) > (lum - bmin)
                rgb = np.where(tmax[..., None], cmax, np.where(tmin[..., None], cmin, rgb))
            for _ in range(iters):
                mx = np.asarray(alpha.filter(ImageFilter.MaxFilter(2 * r + 1))).astype(int)
                mn = np.asarray(alpha.filter(ImageFilter.MinFilter(2 * r + 1))).astype(int)
                v = np.asarray(alpha).astype(int)
                alpha = Image.fromarray(np.where(mx - v < v - mn, mx, np.where(mx - v > v - mn, mn, v)).astype("uint8"))
            return Image.fromarray(np.dstack([rgb.clip(0, 255), np.asarray(alpha)]).astype("uint8"), "RGBA")

        def big(frame):
            frame = frame.convert("RGBA")
            pm = frame.convert("RGBa").resize((w * k, h * k), Image.LANCZOS).convert("RGBA")
            r, g, b, a = shock(pm, 2, 2 if k <= 4 else 3).split()
            rgb = Image.merge("RGB", (r, g, b)).filter(ImageFilter.GaussianBlur(k * 0.3)).filter(
                ImageFilter.UnsharpMask(radius=1.6, percent=80, threshold=1))
            r, g, b = rgb.split()
            return Image.merge("RGBA", (r, g, b, a.filter(ImageFilter.GaussianBlur(k * 0.2))))

        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            if is_gif:
                frames, durations = [], []
                for fr in ImageSequence.Iterator(im):
                    durations.append(fr.info.get("duration", 60))
                    frames.append(big(fr))
                frames[0].save(dest, save_all=True, append_images=frames[1:], duration=durations, disposal=2, loop=0, optimize=False)
            else:
                big(im).save(dest, optimize=True)
        return href
    except Exception:
        return href if dest.exists() else "images/twitch/" + rel.as_posix()


def twitch_assets():
    if not TWITCH_DIR.is_dir():
        return []
    best = {}
    for f in sorted(TWITCH_DIR.rglob("*")):
        if f.suffix.lower() not in (".png", ".gif", ".jpg", ".jpeg", ".webp"):
            continue
        rel = f.relative_to(TWITCH_DIR)
        folder = rel.parent.as_posix().replace(".", "")
        stem = f.stem
        if folder == "" and stem.startswith("channel_points"):
            folder = "__points"
        theme = rel.parts[0] if rel.parts[0] in THEME_SETS else None
        if theme:  # generated sets (Purple, Floral) go into the normal groups instead of getting their own
            sub = rel.parts[1] if len(rel.parts) > 2 else ""
            if sub:
                folder = THEME_FOLDERS.get(sub, folder)
            else:
                folder = next((g for key, g in THEME_FILES.items() if key in stem), folder)
            if "be_right_back" in stem:
                folder = "Brb"
        # same design in other sizes / previews: strip "_112", "_small", "_preview"
        base = re.sub(r"_(\d+|small|preview)$", "", stem)
        if base.endswith("_preview") or base.endswith("_small"):
            base = re.sub(r"_(small|preview)$", "", base)
        if theme and not base.startswith(theme.lower() + "_"):
            base = theme.lower() + "_" + base  # keeps the two sets apart: "Purple about me" next to "About me"
        is_gif = f.suffix.lower() == ".gif"
        w, h = image_size(f)
        score = (is_gif, w * h)
        key = (folder, base)
        if key not in best or score > best[key][0]:
            best[key] = (score, f, folder, base, w, h, is_gif)
    order = {g[0]: i for i, g in enumerate(TWITCH_GROUPS)}
    out = []
    for _, f, folder, base, w, h, is_gif in best.values():
        if is_gif:
            ensure_gif_loop(f)
        rel = f.relative_to(TWITCH_DIR)
        out.append({"folder": folder, "label": pretty_label(base), "href": large_version(f, rel, is_gif, w, h),
                    "w": w, "h": h, "gif": is_gif})
    def sort_key(a):
        label = a["label"]
        if label == "Base":
            name = ""
        elif label[:1].isdigit():  # badges: months before years
            num = float(re.match(r"[0-9.]+", label).group())
            name = "%08.3f" % (num / 12 if "month" in label else num)
        else:
            name = label.lower()
        return (order.get(a["folder"], 99), name)

    out.sort(key=sort_key)
    return out


def render_twitch_gallery(assets):
    """One button per design, grouped under small headings - the same look as the other works."""
    parts = []
    for folder, title, what in TWITCH_GROUPS:
        items = [a for a in assets if a["folder"] == folder]
        if not items:
            continue
        btns = "\n      ".join(
            f'<a class="proj-btn" href="{esc(quote(a["href"]))}" target="_blank" rel="noopener" '
            f'title="{esc(what)}: {esc(a["label"])}">{esc(a["label"])}{" (animated)" if a["gif"] else ""}</a>'
            for a in items)
        parts.append(f'        <h3 class="gallery-title">{esc(title)}</h3>\n'
                     f'        <div class="btn-grid">\n      {btns}\n    </div>')
    return "\n".join(parts)


# ------------------------------------------------------------- design assets
# Brand projects: everything in images/design/<Brand>/ becomes buttons under the Design section.
DESIGN_DIR = ROOT / "images" / "design"
DESIGN_BRANDS = {"Tessel": "Tessel brand", "Perfum": "Perfum brand"}


def design_assets():
    out = []
    if not DESIGN_DIR.is_dir():
        return out
    for brand_dir in sorted(p for p in DESIGN_DIR.iterdir() if p.is_dir()):
        for f in sorted(brand_dir.iterdir()):
            if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                continue
            label = pretty_label(f.stem.replace(brand_dir.name.lower() + "_", ""))
            out.append({"brand": brand_dir.name, "label": f"{brand_dir.name} {label.lower()}",
                        "href": "images/design/" + brand_dir.name + "/" + f.name})
    return out


def render_design_gallery(assets):
    parts = []
    for brand in sorted({a["brand"] for a in assets}):
        items = [a for a in assets if a["brand"] == brand]
        btns = "\n      ".join(
            f'<a class="proj-btn" href="{esc(quote(a["href"]))}" target="_blank" rel="noopener" '
            f'title="{esc(a["label"])}">{esc(a["label"])}</a>' for a in items)
        parts.append(f'        <h3 class="gallery-title">{esc(DESIGN_BRANDS.get(brand, brand))}</h3>\n'
                     f'        <div class="btn-grid">\n      {btns}\n    </div>')
    return "\n".join(parts)


def portfolio_body(site, projects):
    parts = ['<header class="hero">\n        <h1 class="hero-name">Portfolio</h1>\n'
             '        <p class="hero-tagline">Santa Madara Neilande &mdash; designer, illustrator, 3D artist &amp; developer</p>\n'
             '    </header>']
    lds = []
    assets = twitch_assets()
    for key, title, sid, *kind in SECTIONS:
        items = [p for p in projects if p.get("section") == key
                 and (not kind or (p.get("type", "image") == "video") == (kind[0] == "video"))]
        topic, intro = SECTION_INFO[sid]
        anchor = sid.replace("-grid", "")
        extra = ""
        ld_items = items
        if sid == "design-grid" and design_assets():
            extra = chr(10) + render_design_gallery(design_assets())
            ld_items = items + [{"title": a["label"], "href": a["href"], "type": "image"} for a in design_assets()]
        if sid == "twitch-grid" and assets:
            extra = "\n" + render_twitch_gallery(assets)
            ld_items = items + [{"title": f'{a["label"]} ({a["folder"] or "panel"})', "href": a["href"], "type": "image"}
                                for a in assets]
        lds.append(section_ld(site, topic, sid, ld_items))
        parts.append(
            f'    <section class="section" id="{anchor}" aria-labelledby="{anchor}-title">\n'
            f'        <h2 class="section-title" id="{anchor}-title">{esc(title)}</h2>\n'
            f'        <p class="section-intro">{esc(intro)}</p>\n'
            f'        {render_section(items, sid)}{extra}\n'
            f'    </section>')
    return "\n\n".join(parts), lds


# ----------------------------------------------------------------- contacts

def contacts_body(site):
    roles = "".join(f"<li>{esc(r)}</li>" for r in site["roles"])
    return f"""<header class="hero">
        <h1 class="hero-name">Contacts</h1>
        <p class="hero-tagline">Let's work together</p>
    </header>

    <section class="section">
        <div class="card">
            <h2 class="section-title">{esc(site["name"])}</h2>
            <p>Graphic designer, Twitch designer, illustrator, 3D artist and DevOps / software developer.
            I make logos, banners and stream overlays, character illustrations, 3D scenes, and I build tools and apps.</p>
            <h3 class="card-sub">What I am</h3>
            <ul class="tag-list">{roles}</ul>
            <h3 class="card-sub">Get in touch</h3>
            <div class="btn-grid">
                <a class="proj-btn" href="mailto:{esc(site["email"])}">&#9993; {esc(site["email"])}</a>
                <a class="proj-btn" href="{esc(site["linkedin"])}" target="_blank" rel="me noopener">LinkedIn</a>
                <a class="proj-btn" href="{esc(site["github"])}" target="_blank" rel="me noopener">GitHub</a>
            </div>
        </div>
    </section>"""


# ------------------------------------------------------------ seviathstudio

def studio_body(site):
    s = site["seviathstudio"]
    features = [
        "Brush designer: edges, wet rim, variations, tip pad, brush cards, remix and surprise brushes",
        "Gradient and textured brushes with directional hair / fur strokes",
        "Layers with blend modes, selections and vector node editing",
        "Color wheel, color profiles and filters",
        "Sub view with references and navigator",
        "Session recorder that exports your painting process to MP4",
        "Tablet support (pressure pen)",
        "Free and open source",
    ]
    li = "\n                ".join(f"<li>{esc(f)}</li>" for f in features)
    return f"""<header class="hero">
        <h1 class="hero-name">Seviathstudio</h1>
        <p class="hero-tagline">A digital painting &amp; illustration app, made by Santa Madara Neilande</p>
    </header>

    <section class="section">
        <div class="card">
            <h2 class="section-title">About</h2>
            <p>Seviathstudio is a painting and illustration studio I build myself, made for artists who want deep control
            over their brushes. Design your own brushes, paint with layers, gradients and textures, and record your
            whole session as a video.</p>
            <h3 class="card-sub">Features</h3>
            <ul class="feature-list">
                {li}
            </ul>
            <h3 class="card-sub">Download</h3>
            <p>Current version: <strong>{esc(s["version"])}</strong></p>
            <div class="btn-grid">
                <a class="proj-btn download-btn" href="{esc(s["download_url"])}" rel="noopener">&#11015; {esc(s["download_label"])}</a>
                <a class="proj-btn" href="{esc(s["source_url"])}" target="_blank" rel="noopener">Source code on GitHub</a>
            </div>
        </div>
    </section>"""


# ------------------------------------------------------------ useful tools

def tools_body(site):
    t = site["usefultools"]

    def card(key, text):
        e = t[key]
        return (f'''<div class="tool-card">
                <h3 class="card-sub">{esc(e["name"])}</h3>
                <p>{text}</p>
                <p>Current version: <strong>{esc(e["version"])}</strong>{(" &middot; updated " + esc(e["updated"])) if e.get("updated") else ""}</p>
                <div class="btn-grid">
                    <a class="proj-btn download-btn" href="{esc(e["download_url"])}" rel="noopener">&#11015; Download for {esc(e["name"])}</a>
                    <a class="proj-btn" href="{esc(e.get("releases_url", e["download_url"]))}" target="_blank" rel="noopener">What is new</a>
                    <a class="proj-btn" href="{esc(e["source_url"])}" target="_blank" rel="noopener">Source code on GitHub</a>
                </div>
            </div>''')

    retail = card("retail", "The retail edition for the current World of Warcraft (Midnight). One merged addon that "
                  "brings all the Useful Tools modules together in a single install.")
    forever = card("forever", "The edition for the WoW Forever client. Same tools, adapted to Forever, with quest "
                   "markers built from the Questie quest database.")
    return f"""<header class="hero">
        <h1 class="hero-name">SeviathsUsefultools</h1>
        <p class="hero-tagline">World of Warcraft addons made by Santa Madara Neilande</p>
    </header>

    <section class="section">
        <div class="card">
            <h2 class="section-title">About</h2>
            <p>SeviathsUsefultools is a collection of <strong>World of Warcraft addons</strong> that adds handy tools
            to the game: a farming pack, a codex, dungeon &amp; raid helpers and guild tools. They are free,
            open source and available for two versions of the game. Pick the one that matches your client.</p>
            <p>To install, download the addon, unzip it and put <strong>all the folders</strong> of the zip (<code>SeviathsUsefulTools</code>
            and the <code>SeviathsUsefulTools_...</code> data folders) into your <code>Interface/AddOns</code> folder of the matching
            game version.</p>
            {retail}
            {forever}
        </div>
    </section>"""


# --------------------------------------------------------------------- page

NAV = [("index.html", "Portfolio"), ("usefultools.html", "SeviathsUsefultools"), ("seviathstudio.html", "Seviathstudio"), ("contacts.html", "Contacts")]


def layout(site, *, filename, title, description, body, keywords, extra_ld=None, og_type="website"):
    base = site["url"].rstrip("/")
    url = f"{base}/" if filename == "index.html" else f"{base}/{filename}"
    image = f"{base}/images/petals-background.png"
    nav = "".join(
        f'<a href="{f}?v={BUILD}"' + (' aria-current="page"' if f == filename else "") + f'>{esc(n)}</a>'
        for f, n in NAV)
    person = {
        "@type": "Person",
        "@id": f"{base}/#person",
        "name": site["name"],
        "url": f"{base}/",
        "email": f'mailto:{site["email"]}',
        "jobTitle": "Graphic Designer, Illustrator, 3D Artist & Developer",
        "image": image,
        "sameAs": [site["linkedin"], site["github"]],
        "knowsAbout": ["Graphic design", "Twitch design", "Illustration", "3D art", "DevOps", "Software development"],
    }
    graph = [person, {
        "@type": "WebSite", "@id": f"{base}/#website", "url": f"{base}/",
        "name": f'{site["name"]} - Portfolio', "inLanguage": "en",
        "publisher": {"@id": f"{base}/#person"}}]
    if extra_ld:
        graph.extend(extra_ld if isinstance(extra_ld, list) else [extra_ld])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="keywords" content="{esc(keywords)}">
<meta name="author" content="{esc(site["name"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#dcc9c3">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(site["name"])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(image)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,600;0,900;1,500&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={CSS_VERSION}">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>

    <nav class="nav" aria-label="Main">{nav}</nav>

    <main>
    {body}
    </main>

    <footer class="footer">&copy; {esc(site["name"])} &middot; <a href="contacts.html?v={BUILD}">Contacts</a></footer>

</body>
</html>
"""


CSS = """
:root {
    --ink: #2a2427;
    --burgundy: #7a1a2b;
    --burgundy-dark: #5a1120;
    --gold: #a88b52;
    --cream: #f3ebe4;
    --blush: #dcc9c3;
    --btn-bg: #7a1a2b;
    --btn-text: #f6eee8;
    --panel: rgba(243, 235, 228, 0.86);
}

* { box-sizing: border-box; }

body {
    margin: 0;
    color: var(--ink);
    font-family: 'Space Grotesk', sans-serif;
    min-height: 100vh;
    background-color: var(--blush);
    position: relative;
}

/* The banner covers the whole page and stays put while content scrolls over it. */
body::before {
    content: "";
    position: fixed;
    inset: 52px 0 0 0; /* starts right under the slim bar so the logo is not cut */
    background-image: url('images/petals-background.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    z-index: -1;
}

a { color: var(--burgundy); }

/* slim top bar with the navigation inside */
.nav {
    position: sticky;
    top: 0;
    z-index: 10;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 6vw;
    background: var(--panel);
    border-bottom: 2px solid var(--burgundy);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
}
.nav a {
    color: var(--burgundy-dark);
    text-decoration: none;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 999px;
    border: 1px solid var(--burgundy);
    transition: background 0.15s ease, color 0.15s ease;
}
.nav a:hover { background: var(--burgundy); color: var(--btn-text); }
.nav a[aria-current="page"] { background: var(--burgundy); color: var(--btn-text); }

/* content blocks float over the banner as cream panels */
.hero, .section {
    max-width: 1100px;
    margin: 28px auto 0;
    padding: 32px;
    border-radius: 16px;
    background: var(--panel);
    border: 1px solid rgba(122, 26, 43, 0.35);
    box-shadow: 0 8px 24px rgba(42, 36, 39, 0.15);
}

.hero { text-align: center; }
/* leave the banner's logo visible above the first panel on big screens */
main > .hero:first-child { margin-top: 20vh; }

.hero-name {
    font-family: 'Fraunces', serif;
    font-weight: 900;
    font-size: clamp(40px, 7vw, 88px);
    margin: 0;
    letter-spacing: -0.01em;
    color: var(--burgundy);
}

.hero-tagline {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 500;
    font-size: clamp(18px, 2.4vw, 26px);
    margin: 14px auto 0;
    max-width: 40ch;
    color: var(--ink);
}

.section-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(24px, 3vw, 34px);
    margin: 0 0 24px;
    color: var(--burgundy-dark);
}

.btn-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
}

.proj-btn {
    background: var(--btn-bg);
    color: var(--btn-text);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 15px;
    text-align: center;
    text-decoration: none;
    padding: 22px 18px;
    border-radius: 10px;
    border: 1px solid var(--burgundy-dark);
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    box-shadow: 0 2px 0 rgba(42, 36, 39, 0.3);
    overflow-wrap: anywhere;
}

.proj-btn:hover {
    background: var(--burgundy-dark);
    transform: translateY(-3px);
    box-shadow: 0 6px 14px rgba(42, 36, 39, 0.3);
}

.download-btn { font-size: 18px; }

/* a card lives inside a section panel, so it adds no second box */
.card {
    max-width: 760px;
    margin: 0 auto;
    line-height: 1.6;
}
.card .section-title { margin-bottom: 12px; }
.card-sub {
    font-family: 'Fraunces', serif;
    font-size: 20px;
    margin: 28px 0 12px;
    color: var(--burgundy-dark);
}
.tag-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.tag-list li {
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(122, 26, 43, 0.12);
    border: 1px solid rgba(122, 26, 43, 0.35);
    color: var(--burgundy-dark);
}
code { background: rgba(122, 26, 43, 0.12); padding: 1px 6px; border-radius: 4px; }
.tool-card { margin-top: 8px; }
.gallery-title { font-family: 'Fraunces', serif; font-size: 22px; margin: 32px 0 14px; color: var(--burgundy-dark); }
.section-intro { margin: -12px 0 20px; line-height: 1.5; }
.feature-list { padding-left: 20px; margin: 0; }
.feature-list li { margin-bottom: 6px; }

.footer {
    max-width: 1100px;
    margin: 28px auto 28px;
    padding: 14px;
    border-radius: 12px;
    background: var(--panel);
    text-align: center;
    color: var(--ink);
    font-size: 14px;
}

.empty-note {
    opacity: 0.7;
    font-size: 14px;
    font-style: italic;
}

@media (max-width: 760px) {
    body::before { inset: 0; }
    main > .hero:first-child { margin-top: 16px; }
    .hero, .section { margin: 16px 12px 0; padding: 22px; }
    .footer { margin: 16px 12px 16px; }
}
"""

CSS_VERSION = hashlib.md5(CSS.encode("utf-8")).hexdigest()[:8]
# Changes whenever the generator or data change. Page links carry it so a browser that cached an
# older copy of a page (GitHub Pages allows 10 minutes) fetches the fresh one after a deploy.
BUILD = hashlib.md5(b"".join(p.read_bytes() for p in (Path(__file__), PROJECTS_FILE, SITE_FILE))).hexdigest()[:8]


def main():
    site = load(SITE_FILE)
    projects = load(PROJECTS_FILE).get("projects", [])
    name = site["name"]
    base = site["url"].rstrip("/")
    s = site["seviathstudio"]

    port_body, port_lds = portfolio_body(site, projects)
    pages = {
        "index.html": layout(
            site, filename="index.html",
            title=f"{name} - Portfolio | Graphic Designer, Twitch Designer, Illustrator & 3D Artist",
            description=(f"Portfolio of {name}: graphic design, Twitch design (logos, banners, overlays), "
                         "character illustration, 3D art and DevOps / software projects."),
            keywords=(f"{name}, Santa Neilande, Madara Neilande, portfolio, graphic designer, twitch design, "
                      "twitch logo, twitch banner, twitch overlay, stream design, illustrator, character design, "
                      "fantasy illustration, 3D artist, Unity, brochure design, poster design, logo design, "
                      "DevOps, Latvia"),
            body=port_body,
            extra_ld=[{"@type": "CollectionPage", "name": f"{name} - Portfolio", "url": f"{base}/",
                       "about": {"@id": f"{base}/#person"}}] + port_lds),
        "contacts.html": layout(
            site, filename="contacts.html",
            title=f"Contacts - {name} | Designer, Illustrator & Developer",
            description=(f"Contact {name} - graphic designer, Twitch designer, illustrator, 3D artist and DevOps "
                         f"developer. Email {site['email']} or find me on LinkedIn."),
            keywords=f"{name}, contact, hire designer, twitch designer, illustrator, LinkedIn, email",
            body=contacts_body(site),
            extra_ld={"@type": "ContactPage", "name": f"Contacts - {name}", "url": f"{base}/contacts.html",
                      "about": {"@id": f"{base}/#person"}}),
        "usefultools.html": layout(
            site, filename="usefultools.html",
            title=f"SeviathsUsefultools - World of Warcraft addons by {name} | Download",
            description=("SeviathsUsefultools is a free World of Warcraft addon with farming, codex, dungeon & raid "
                         "and guild tools. Download the Retail (Midnight) or WoW Forever edition."),
            keywords=(f"SeviathsUsefultools, Seviaths Useful Tools, WoW addon, World of Warcraft addon, WoW Forever, "
                      f"retail addon, Midnight, {name}, download"),
            body=tools_body(site),
            extra_ld={"@type": "SoftwareApplication", "name": "SeviathsUsefultools",
                      "applicationCategory": "GameApplication", "operatingSystem": "Windows, macOS",
                      "url": f"{base}/usefultools.html",
                      "downloadUrl": [site["usefultools"]["retail"]["download_url"],
                                      site["usefultools"]["forever"]["download_url"]],
                      "author": {"@id": f"{base}/#person"},
                      "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}),
        "seviathstudio.html": layout(
            site, filename="seviathstudio.html",
            title=f"Seviathstudio - Digital painting app by {name} | Download",
            description=("Seviathstudio is a free, open source digital painting and illustration app with a brush "
                         "designer, layers, gradient brushes, filters and a session recorder. Download it here."),
            keywords=(f"Seviathstudio, {name}, digital painting app, illustration software, brush designer, "
                      "free painting software, open source, download"),
            body=studio_body(site),
            extra_ld={"@type": "SoftwareApplication", "name": "Seviathstudio",
                      "applicationCategory": "MultimediaApplication", "operatingSystem": "Windows",
                      "url": f"{base}/seviathstudio.html", "downloadUrl": s["download_url"],
                      "author": {"@id": f"{base}/#person"},
                      "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}),
        # old URL kept alive, points search engines to the new home
        "portfolio.html": f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Portfolio - {esc(name)}</title>
<link rel="canonical" href="{esc(base)}/"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=index.html"></head>
<body><a href="index.html">Portfolio</a></body></html>
""",
    }
    for fname, content in pages.items():
        (ROOT / fname).write_text(content, encoding="utf-8")
        print(f"Generated: {fname}")

    urls = [f"{base}/", f"{base}/usefultools.html", f"{base}/seviathstudio.html", f"{base}/contacts.html"]
    # image entries help Google Images find the illustrations and designs
    img_xml = "".join(
        f"    <image:image><image:loc>{esc(abs_url(site, p['href']))}</image:loc>"
        f"<image:title>{esc(p['title'])}</image:title></image:image>\n"
        for p in [q for q in projects if not q.get("href", "").startswith("http")]
        + [{"title": a["label"] + " - Twitch design", "href": a["href"]} for a in twitch_assets()]
        + [{"title": a["label"], "href": a["href"]} for a in design_assets()])
    entries = "".join(
        f"  <url>\n    <loc>{esc(u)}</loc>\n{img_xml if u == f'{base}/' else ''}  </url>\n" for u in urls)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + entries + "</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "style.css").write_text(CSS, encoding="utf-8")
    print("Generated: sitemap.xml, robots.txt, style.css")


if __name__ == "__main__":
    main()

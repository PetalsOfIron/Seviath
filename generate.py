#!/usr/bin/env python3
"""
Portfolio generator - builds the whole static site from data/*.json.

Pages:  index.html (Portfolio), contacts.html, seviathstudio.html,
        portfolio.html (redirect to index), sitemap.xml, robots.txt, style.css

Edit data/projects.json for works and data/site.json for contact info and the
Seviathstudio download link, then run:

    python3 generate.py
"""
import json
import html
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
    ("art-3D", "Art & 3D", "art-grid"),
]


def portfolio_body(projects):
    parts = ['<header class="hero">\n        <h1 class="hero-name">Portfolio</h1>\n'
             '        <p class="hero-tagline">Santa Madara Neilande &mdash; designer, illustrator, 3D artist &amp; developer</p>\n'
             '    </header>']
    for key, title, sid in SECTIONS:
        items = [p for p in projects if p.get("section") == key]
        parts.append(
            f'    <section class="section" id="{sid.replace("-grid", "")}">\n'
            f'        <h2 class="section-title">{esc(title)}</h2>\n'
            f'        {render_section(items, sid)}\n'
            f'    </section>')
    return "\n\n".join(parts)


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


# --------------------------------------------------------------------- page

NAV = [("index.html", "Portfolio"), ("seviathstudio.html", "Seviathstudio"), ("contacts.html", "Contacts")]


def layout(site, *, filename, title, description, body, keywords, extra_ld=None, og_type="website"):
    base = site["url"].rstrip("/")
    url = f"{base}/" if filename == "index.html" else f"{base}/{filename}"
    image = f"{base}/images/petals-background.png"
    nav = "".join(
        f'<a href="{f}"' + (' aria-current="page"' if f == filename else "") + f'>{esc(n)}</a>'
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
        graph.append(extra_ld)
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
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>

    <nav class="nav" aria-label="Main">{nav}</nav>

    <main>
    {body}
    </main>

    <footer class="footer">&copy; {esc(site["name"])} &middot; <a href="contacts.html">Contacts</a></footer>

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
    --panel: rgba(243, 235, 228, 0.82);
}

* { box-sizing: border-box; }

/* The banner sits at the top of every page and fades into the same blush colour the page continues with. */
body {
    margin: 0;
    color: var(--ink);
    font-family: 'Space Grotesk', sans-serif;
    min-height: 100vh;
    background-color: var(--blush);
    background-image: url('images/petals-background.png');
    background-repeat: no-repeat;
    background-position: top center;
    background-size: 100% auto;
}

a { color: var(--burgundy); }

.nav {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    /* the banner is 3:1, so 33vw keeps nav and content below it */
    padding: 33vw 6vw 0;
    justify-content: center;
}
.nav a {
    color: var(--burgundy-dark);
    text-decoration: none;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 999px;
    border: 1px solid var(--burgundy);
    background: var(--panel);
    transition: background 0.15s ease, color 0.15s ease;
}
.nav a:hover { background: var(--burgundy); color: var(--btn-text); }
.nav a[aria-current="page"] { background: var(--burgundy); color: var(--btn-text); }

.hero {
    padding: 36px 6vw 40px;
    text-align: center;
}

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

.section {
    padding: 40px 6vw 60px;
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

.card {
    max-width: 860px;
    margin: 0 auto;
    padding: 32px;
    border-radius: 16px;
    background: var(--panel);
    border: 1px solid rgba(122, 26, 43, 0.35);
    box-shadow: 0 8px 24px rgba(42, 36, 39, 0.12);
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
.feature-list { padding-left: 20px; margin: 0; }
.feature-list li { margin-bottom: 6px; }

.footer {
    text-align: center;
    padding: 30px 6vw 40px;
    color: var(--ink);
    opacity: 0.8;
    font-size: 14px;
}

.empty-note {
    opacity: 0.7;
    font-size: 14px;
    font-style: italic;
}

@media (max-width: 560px) {
    .section { padding: 30px 6vw 40px;}
    .card { padding: 22px; }
}
"""


def main():
    site = load(SITE_FILE)
    projects = load(PROJECTS_FILE).get("projects", [])
    name = site["name"]
    base = site["url"].rstrip("/")
    s = site["seviathstudio"]

    pages = {
        "index.html": layout(
            site, filename="index.html",
            title=f"{name} - Portfolio | Graphic Designer, Twitch Designer, Illustrator & 3D Artist",
            description=(f"Portfolio of {name}: graphic design, Twitch design (logos, banners, overlays), "
                         "character illustration, 3D art and DevOps / software projects."),
            keywords=(f"{name}, Santa Neilande, Madara Neilande, portfolio, graphic designer, twitch design, "
                      "twitch logo, stream banner, illustrator, character design, 3D artist, DevOps, Latvia"),
            body=portfolio_body(projects),
            extra_ld={"@type": "CollectionPage", "name": f"{name} - Portfolio", "url": f"{base}/",
                      "about": {"@id": f"{base}/#person"}}),
        "contacts.html": layout(
            site, filename="contacts.html",
            title=f"Contacts - {name} | Designer, Illustrator & Developer",
            description=(f"Contact {name} - graphic designer, Twitch designer, illustrator, 3D artist and DevOps "
                         f"developer. Email {site['email']} or find me on LinkedIn."),
            keywords=f"{name}, contact, hire designer, twitch designer, illustrator, LinkedIn, email",
            body=contacts_body(site),
            extra_ld={"@type": "ContactPage", "name": f"Contacts - {name}", "url": f"{base}/contacts.html",
                      "about": {"@id": f"{base}/#person"}}),
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

    urls = [f"{base}/", f"{base}/seviathstudio.html", f"{base}/contacts.html"]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url><loc>{esc(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "style.css").write_text(CSS, encoding="utf-8")
    print("Generated: sitemap.xml, robots.txt, style.css")


if __name__ == "__main__":
    main()

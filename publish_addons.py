"""Publishes the SeviathsUsefultools addons: builds a zip of each edition (retail and WoW Forever), puts it on a GitHub release of its repository, and updates
the download links and the version of the SeviathsUsefultools page (data/site.json) of this site.

    python publish_addons.py            build the zips, make or update the releases, update the site data, regenerate the site, commit and push it
    python publish_addons.py --no-push  everything except the commit and the push of the site

Run it after every change of an addon. A release is kept for each version of the .toc (v2.3, v1.0 ...): a new run of the same version replaces its zip.
The download buttons of the page point to .../releases/latest/download/<fixed name>.zip, so they never change; the page shows the version and the date.
The zip holds the addon folder and its load-on-demand folders (SeviathsUsefulTools_*) of that game version, without .git, tools and backup files.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
WOW = r"D:\wow\World of Warcraft"
EDITIONS = {
    "retail": {"client": "_retail_", "repo": "PetalsOfIron/WOWSeviathsUsefultools-Retail", "asset": "SeviathsUsefulTools-Retail.zip"},
    "forever": {"client": "_forever_", "repo": "PetalsOfIron/SeviathsUsefultools-forever", "asset": "SeviathsUsefulTools-Forever.zip"},
}
SKIP_DIRS = {".git", ".github", "tools", "__pycache__"}
SKIP_FILES = {".gitignore", ".gitattributes"}
DIST = os.path.join(HERE, "_dist")


def run(*args, cwd=None, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise SystemExit("failed: %s\n%s" % (" ".join(args), (r.stdout + r.stderr).strip()))
    return (r.stdout + r.stderr).strip()


def toc_version(addons):
    for line in open(os.path.join(addons, "SeviathsUsefulTools", "SeviathsUsefulTools.toc"), encoding="utf-8-sig"):
        m = re.match(r"##\s*Version:\s*(\S+)", line)
        if m:
            return m.group(1)
    return "0"


def newest_changelog(addon_dir):
    p = os.path.join(addon_dir, "CHANGELOG.md")
    if not os.path.exists(p):
        return ""
    text = open(p, encoding="utf-8").read().replace("\r\n", "\n")
    try:
        start = text.index("## ")
    except ValueError:
        return ""
    end = text.find("\n## ", start + 3)
    return text[start:end if end > 0 else len(text)].strip()


def build_zip(key, e):
    addons = os.path.join(WOW, e["client"], "Interface", "AddOns")
    folders = ["SeviathsUsefulTools"] + sorted(d for d in os.listdir(addons) if d.startswith("SeviathsUsefulTools_") and os.path.isdir(os.path.join(addons, d)))
    os.makedirs(DIST, exist_ok=True)
    zpath = os.path.join(DIST, e["asset"])
    if os.path.exists(zpath):
        os.remove(zpath)
    n = 0
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for folder in folders:
            base = os.path.join(addons, folder)
            for root, dirs, files in os.walk(base):
                dirs[:] = [d for d in dirs if not (root == base and d in SKIP_DIRS) and d != "__pycache__"]
                for f in files:
                    if f in SKIP_FILES or f.endswith(".bak"):
                        continue
                    full = os.path.join(root, f)
                    z.write(full, os.path.relpath(full, addons).replace(os.sep, "/"))
                    n += 1
    print("%s: %d files in %d folders, %.1f MB -> %s" % (key, n, len(folders), os.path.getsize(zpath) / 1e6, zpath))
    return zpath, toc_version(addons), os.path.join(addons, "SeviathsUsefulTools")


def publish(key, e, zpath, version, addon_dir, today):
    repo, tag = e["repo"], "v" + version
    notes = "SeviathsUsefultools %s - %s edition, built %s.\n\nUnzip it and put ALL the folders of the zip into your Interface/AddOns folder.\n\n%s\n" % (
        version, key, today, newest_changelog(addon_dir))
    nf = os.path.join(DIST, "notes-%s.md" % key)
    open(nf, "w", encoding="utf-8").write(notes)
    exists = subprocess.run(["gh", "release", "view", tag, "--repo", repo], capture_output=True).returncode == 0
    if exists:
        print(run("gh", "release", "upload", tag, zpath, "--repo", repo, "--clobber"))
        run("gh", "release", "edit", tag, "--repo", repo, "--notes-file", nf, "--latest")
        print("%s: release %s updated" % (key, tag))
    else:
        out = run("gh", "release", "create", tag, zpath, "--repo", repo, "--target", "main", "--title", "SeviathsUsefultools %s (%s)" % (version, key),
                  "--notes-file", nf, "--latest")
        print("%s: release %s created %s" % (key, tag, out))


def main():
    today = datetime.date.today().strftime("%d %b %Y").lstrip("0")
    site_path = os.path.join(HERE, "data", "site.json")
    site = json.load(open(site_path, encoding="utf-8"))
    for key, e in EDITIONS.items():
        zpath, version, addon_dir = build_zip(key, e)
        publish(key, e, zpath, version, addon_dir, today)
        t = site["usefultools"][key]
        t["version"] = version
        t["updated"] = today
        t["download_url"] = "https://github.com/%s/releases/latest/download/%s" % (e["repo"], e["asset"])
        t["releases_url"] = "https://github.com/%s/releases/latest" % e["repo"]
    json.dump(site, open(site_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(run(sys.executable, "generate.py", cwd=HERE))
    if "--no-push" in sys.argv:
        return
    status = run("git", "status", "--short", cwd=HERE)
    if not status:
        print("site: nothing changed")
        return
    run("git", "add", "-A", cwd=HERE)
    msg = "Update the SeviathsUsefultools downloads (retail %s, forever %s)" % (
        site["usefultools"]["retail"]["version"], site["usefultools"]["forever"]["version"])
    run("git", "-c", "user.name=santamadaraneilande-ctrl", "-c", "user.email=santamadaraneilande@gmail.com", "commit", "-q", "-m", msg, cwd=HERE)
    print(run("git", "push", "origin", "main", cwd=HERE) or "site: pushed")


if __name__ == "__main__":
    main()

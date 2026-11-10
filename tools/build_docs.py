#!/usr/bin/env python3
"""Builds the Huncho World docs site (/docs) from the GitBook docs repo.

Usage: python3 tools/build_docs.py <path to huncho-phone-docs checkout> <output dir, e.g. docs>

Reads each script's SUMMARY.md and markdown pages (GitBook flavour: hints, steppers,
tabs, <details>), and writes static pages with one A-Z sidebar, a JG-style home page
and a search index. Nothing in the docs repo changes, so GitBook keeps working.
"""
import html, json, os, re, shutil, sys
import markdown
import yaml

SRC, OUT = sys.argv[1], sys.argv[2]
BASE = "/docs"
STORE = "https://hunchoworldstore.github.io/"
DISCORD = "https://discord.gg/hP8VTtwgs5"
GITBOOK = "https://huncho-world-store.gitbook.io/huncho-world-store-docs"

# Getting Started first, then scripts A-Z.
SECTIONS = [
    {"slug": "getting-started", "title": "Getting Started", "dir": "home", "icon": "rocket", "skip": ["README.md"]},
    {"slug": "huncho-designer-bookbags", "title": "Designer Bookbags", "dir": "huncho-designer-bookbags", "icon": "backpack"},
    {"slug": "huncho-job-center", "title": "Job Center", "dir": "huncho-job-center", "icon": "briefcase"},
    {"slug": "huncho-npc-police", "title": "NPC Police", "dir": "huncho-npc-police", "icon": "siren"},
    {"slug": "huncho-phone", "title": "Huncho Phone", "dir": ".", "icon": "phone"},
    {"slug": "huncho-world-game-pack", "title": "World Game Pack", "dir": "huncho-world-game-pack", "icon": "dice"},
]
# GitBook URL prefixes → section slug (phone pages live under /huncho-phone on GitBook too)
GB_PREFIX = {s["slug"]: s["slug"] for s in SECTIONS if s["slug"] != "getting-started"}

ICONS = {  # lucide-style outline icons
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "backpack": '<path d="M4 10a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/><path d="M8 10h8"/><path d="M8 18h8"/><path d="M8 22v-6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v6"/><path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>',
    "briefcase": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
    "siren": '<path d="M7 18v-6a5 5 0 1 1 10 0v6"/><path d="M5 21a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2z"/><path d="M21 12h1"/><path d="M18.5 4.5 18 5"/><path d="M2 12h1"/><path d="M12 2v1"/><path d="m4.93 4.93.71.71"/><path d="M12 12v6"/>',
    "phone": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "dice": '<rect width="12" height="12" x="2" y="10" rx="2" ry="2"/><path d="m17.92 14 3.5-3.5a2.24 2.24 0 0 0 0-3l-5-4.92a2.24 2.24 0 0 0-3 0L10 6"/><path d="M6 18h.01"/><path d="M10 14h.01"/><path d="M15 6h.01"/><path d="M18 9h.01"/>',
    "package": '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7"/><path d="m7.5 4.27 9 5.15"/>',
    "key": '<path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
    "scroll": '<path d="M15 12h-5"/><path d="M15 8h-5"/><path d="M19 17V5a2 2 0 0 0-2-2H4"/><path d="M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3"/>',
    "book": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "bag": '<path d="M16 10a4 4 0 0 1-8 0"/><path d="M3.103 6.034h17.794"/><path d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "menu": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
    "chev": '<path d="m9 18 6-6-6-6"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "back": '<path d="m15 18-6-6 6-6"/>',
}
def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

# ---------------------------------------------------------------- SUMMARY parsing
def parse_summary(sec):
    path = os.path.join(SRC, sec["dir"], "SUMMARY.md")
    groups, cur = [], {"title": None, "items": []}
    stack = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^##\s+(.+)", line)
        if m:
            if cur["items"] or cur["title"]: groups.append(cur)
            cur = {"title": m.group(1).strip(), "items": []}; stack = []
            continue
        m = re.match(r"^(\s*)[*-]\s+\[(.+?)\]\((.+?)\)", line)
        if not m: continue
        depth = len(m.group(1).replace("\t", "  ")) // 2
        f = m.group(3).split("#")[0]
        if f in sec.get("skip", []): continue
        item = {"title": m.group(2).replace("\\", ""), "file": os.path.normpath(f), "children": []}
        stack = stack[:depth]
        (stack[-1]["children"] if stack else cur["items"]).append(item)
        stack.append(item)
    groups.append(cur)
    return [g for g in groups if g["items"]]

def flat(items):
    for it in items:
        yield it; yield from flat(it["children"])

def route(sec, file):
    stem = re.sub(r"\.md$", "", file)
    stem = re.sub(r"(^|/)README$", "", stem)
    if sec["slug"] == "getting-started": stem = re.sub(r"^getting-started/", "", stem)
    return f"{BASE}/{sec['slug']}/" + (stem + "/" if stem else "")

# ---------------------------------------------------------------- markdown
MD_EXT = ["tables", "fenced_code", "md_in_html", "toc", "attr_list", "sane_lists"]

def frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            try: meta = yaml.safe_load(text[4:end]) or {}
            except Exception: meta = {}
            return meta, text[end + 4:].lstrip("\n")
    return {}, text

def gitbook_blocks(t):
    t = re.sub(r'\{%\s*hint\s+style="(\w+)"\s*%\}', r'\n<div class="hint hint-\1" markdown="1">\n', t)
    t = re.sub(r"\{%\s*endhint\s*%\}", "\n</div>\n", t)
    t = re.sub(r"\{%\s*stepper\s*%\}", '\n<div class="stepper" markdown="1">\n', t)
    t = re.sub(r"\{%\s*endstepper\s*%\}", "\n</div>\n", t)
    t = re.sub(r"\{%\s*step\s*%\}", '\n<div class="step" markdown="1">\n', t)
    t = re.sub(r"\{%\s*endstep\s*%\}", "\n</div>\n", t)
    t = re.sub(r"\{%\s*tabs\s*%\}", '\n<div class="tabs" markdown="1">\n', t)
    t = re.sub(r"\{%\s*endtabs\s*%\}", "\n</div>\n", t)
    t = re.sub(r'\{%\s*tab\s+title="([^"]*)"\s*%\}', lambda m: f'\n<div class="tab" data-title="{html.escape(m.group(1))}" markdown="1">\n', t)
    t = re.sub(r"\{%\s*endtab\s*%\}", "\n</div>\n", t)
    t = re.sub(r'\{%\s*(?:embed|content-ref)\s+url="([^"]+)"\s*%\}', r"\n[\1](\1)\n", t)
    t = re.sub(r"\{%\s*end(?:embed|content-ref)\s*%\}", "", t)
    t = re.sub(r"<details>", '<details markdown="1">', t)
    t = re.sub(r"<summary>(.*?)</summary>", lambda m: "<summary>" + m.group(1) + "</summary>\n", t)
    return t

ASSETS = set()  # (src abs path, out rel path)

def fix_links(body, sec, file, files_in_sec):
    page_dir = os.path.dirname(os.path.join(sec["dir"], file))
    def resolve(url, is_img):
        if re.match(r"^(https?:|mailto:|#|data:)", url):
            if url.startswith(GITBOOK):
                rest = url[len(GITBOOK):].strip("/")
                return f"{BASE}/{rest}/" if rest else f"{BASE}/"
            if url.rstrip("/") == STORE.rstrip("/"): return "/"
            return url
        path, _, frag = url.partition("#")
        full = os.path.normpath(os.path.join(page_dir, path))
        if is_img or not path.endswith(".md"):
            if os.path.isfile(os.path.join(SRC, full)):
                rel = "assets/" + full.replace("/", "__").lstrip(".")
                rel = re.sub(r"\.(png|jpe?g)$", ".webp", rel, flags=re.I)  # compressed copy
                ASSETS.add((os.path.join(SRC, full), rel))
                return f"{BASE}/{rel}"
            return url
        # markdown link → find its section
        for s in SECTIONS:
            d = os.path.normpath(s["dir"])
            relp = os.path.relpath(full, d)
            if not relp.startswith("..") and (s["slug"] != "huncho-phone" or "/" not in relp):
                return route(s, relp) + (("#" + frag) if frag else "")
        return route(sec, os.path.relpath(full, os.path.normpath(sec["dir"])))
    body = re.sub(r'(<img[^>]*\ssrc=")([^"]+)(")', lambda m: m.group(1) + resolve(m.group(2), True) + m.group(3), body)
    body = re.sub(r'(<a[^>]*\shref=")([^"]+)(")', lambda m: m.group(1) + resolve(html.unescape(m.group(2)), False) + m.group(3), body)
    body = re.sub(r'<a href="(https?://(?!hunchoworldstore\.github\.io)[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)
    return body

def plain(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()

# ---------------------------------------------------------------- templates
CSS_V = "4"
def shell(title, desc, main, active_sec=None, active_url=None, home=False, toc_html=""):
    side = sidebar(active_sec, active_url)
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc or 'Guides for every Huncho World FiveM script.')}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:image" content="https://hunchoworldstore.github.io/assets/og.jpg">
<meta name="theme-color" content="#070b16">
<link rel="icon" type="image/png" href="/assets/favicon.png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="{BASE}/docs.css?v={CSS_V}">
</head><body class="{'home' if home else 'page'}">
<header class="top">
  <button class="iconbtn only-m" id="menuBtn" aria-label="Menu">{icon('menu')}</button>
  <a class="brand" href="{BASE}/"><img src="/assets/logo-sm.webp" alt="" width="40" height="40"><span>Huncho World <b>Docs</b></span></a>
  <button class="searchbar only-d" data-search>{icon('search')}<span>Search docs…</span><kbd>⌘K</kbd></button>
  <nav class="toplinks only-d"><a href="/">Store</a><a href="{DISCORD}" target="_blank" rel="noopener">Discord</a></nav>
  <button class="iconbtn only-m" data-search aria-label="Search">{icon('search')}</button>
</header>
<div class="layout">
  <aside class="side" id="side"><div class="sidein">{side}</div>
    <div class="sidefoot"><a href="/">{icon('bag')}<span>Store</span></a><a href="{DISCORD}" target="_blank" rel="noopener">{icon('help')}<span>Need more help?</span></a></div>
  </aside>
  <div class="scrim" id="scrim"></div>
  <main class="main">{main}</main>
  {f'<aside class="toc only-xl"><div class="tocin"><b>On this page</b>{toc_html}</div></aside>' if toc_html else ''}
</div>
<div class="search" id="search" hidden>
  <div class="sbox"><div class="sin">{icon('search')}<input id="q" placeholder="Search guides, fixes & config options…" autocomplete="off"><button class="esc" data-close>Esc</button></div>
  <div class="sres" id="sres"></div></div>
</div>
<script src="{BASE}/docs.js?v={CSS_V}" defer></script>
</body></html>"""

NAV = {}  # slug -> groups
def nav_items(sec, items, active_url, depth=0):
    out = []
    for it in items:
        u = route(sec, it["file"]); on = " on" if u == active_url else ""
        out.append(f'<a class="nl d{depth}{on}" href="{u}">{html.escape(it["title"])}</a>')
        if it["children"]: out.append(nav_items(sec, it["children"], active_url, depth + 1))
    return "".join(out)

def sidebar(active_sec, active_url):
    out = []
    for s in SECTIONS:
        open_ = " open" if s is active_sec else ""
        inner = []
        for g in NAV[s["slug"]]:
            if g["title"]: inner.append(f'<div class="ng">{html.escape(g["title"])}</div>')
            inner.append(nav_items(s, g["items"], active_url))
        out.append(f'<details class="ns"{open_}><summary>{icon(s["icon"])}<span>{html.escape(s["title"])}</span>{icon("chev","chev")}</summary><div class="nsin">{"".join(inner)}</div></details>')
    return "".join(out)

def card(href, ic, title, text, ext=False):
    t = ' target="_blank" rel="noopener"' if ext else ""
    return f'<a class="card" href="{href}"{t}>{icon(ic)}<b>{html.escape(title)}</b><span>{html.escape(text)}</span></a>'

# ---------------------------------------------------------------- build
def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    for s in SECTIONS: NAV[s["slug"]] = parse_summary(s)
    index, pages = [], []
    for s in SECTIONS:
        order = [it for g in NAV[s["slug"]] for it in flat(g["items"])]
        for i, it in enumerate(order):
            pages.append((s, it, order[i - 1] if i else None, order[i + 1] if i + 1 < len(order) else None))
    descs = {}
    for s, it, prev, nxt in pages:
        src = os.path.join(SRC, s["dir"], it["file"])
        meta, text = frontmatter(open(src, encoding="utf-8").read())
        md = markdown.Markdown(extensions=MD_EXT, extension_configs={"toc": {"permalink": False}})
        body = md.convert(gitbook_blocks(text))
        body = fix_links(body, s, it["file"], None)
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title = plain(m.group(1)) if m else it["title"]
        if m: body = body.replace(m.group(0), "", 1)
        desc = meta.get("description") or ""
        descs[(s["slug"], it["file"])] = desc
        url = route(s, it["file"])
        cover = ""
        if meta.get("cover"):
            c = fix_links(f'<img src="{meta["cover"]}">', s, it["file"], None)
            cover = f'<div class="cover">{c.replace("<img", "<img alt=\"\"")}</div>'
        heads = re.findall(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body, re.S)
        toc = "".join(f'<a class="t{l}" href="#{i}">{html.escape(plain(h))}</a>' for l, i, h in heads)
        pn = '<nav class="pn">' + (f'<a class="prev" href="{route(s, prev["file"])}"><small>Previous</small>{html.escape(prev["title"])}</a>' if prev else "<span></span>") + \
             (f'<a class="next" href="{route(s, nxt["file"])}"><small>Next</small>{html.escape(nxt["title"])}</a>' if nxt else "<span></span>") + "</nav>"
        main_html = f"""{cover}<article class="doc">
<div class="crumb">{icon(s['icon'])}<a href="{route(s, order_first(s))}">{html.escape(s['title'])}</a></div>
<h1>{html.escape(title)}</h1>{f'<p class="lead">{html.escape(desc)}</p>' if desc else ''}
{body}
{pn}
<p class="edit">Can't find what you need? <a href="{DISCORD}" target="_blank" rel="noopener">Open a ticket on Discord</a>.</p>
</article>"""
        out_dir = os.path.join(OUT, url[len(BASE) + 1:])
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(
            shell(f"{title} · {s['title']} · Huncho World Docs", desc, main_html, s, url, toc_html=toc if len(heads) > 1 else ""))
        index.append({"t": title, "s": s["title"], "u": url, "h": [plain(h) for _, _, h in heads][:30], "x": plain(body)[:6000]})

    # changelogs overview
    rows = []
    for s in SECTIONS[1:]:
        f = next((it["file"] for g in NAV[s["slug"]] for it in flat(g["items"]) if it["file"].endswith("changelog.md")), None)
        if not f: continue
        txt = open(os.path.join(SRC, s["dir"], f), encoding="utf-8").read()
        v = re.search(r"^##\s+(.+)$", txt, re.M)
        rows.append(f'<a class="card row" href="{route(s, f)}">{icon(s["icon"])}<b>{html.escape(s["title"])}</b><span>Latest: {html.escape(v.group(1).strip()) if v else "—"}</span></a>')
    cl = f'<article class="doc"><div class="crumb">{icon("scroll")}<span>Changelogs</span></div><h1>Changelogs</h1><p class="lead">What changed in every Huncho World script. Updates also post in our Discord.</p><div class="cards one">{"".join(rows)}</div></article>'
    os.makedirs(os.path.join(OUT, "changelogs"), exist_ok=True)
    open(os.path.join(OUT, "changelogs", "index.html"), "w").write(shell("Changelogs · Huncho World Docs", "", cl))
    index.append({"t": "Changelogs", "s": "Docs", "u": f"{BASE}/changelogs/", "h": [], "x": "changelog updates versions what changed"})

    # home
    gs = SECTIONS[0]
    common = "".join([
        card(route(gs, "getting-started/download.md"), "package", "Download Purchase", "Download & install your script"),
        card(route(gs, "getting-started/escrow-errors.md"), "key", "Escrow Errors", "Fix Keymaster & escrow issues"),
        card(route(gs, "getting-started/permissions.md"), "shield", "Permissions", "Sort out ace permission problems"),
        card(f"{BASE}/changelogs/", "scroll", "Changelogs", "See what's new in every script"),
    ])
    guides = "".join(card(route(s, order_first(s)), s["icon"], s["title"], descs.get((s["slug"], "README.md"), "")) for s in SECTIONS[1:])
    hand = "".join([
        card(route(gs, "getting-started/escrow-errors.md"), "book", "Read the guides", "Every script ends with Troubleshooting and its Changelog."),
        card(DISCORD, "chat", "Open a ticket on Discord", "Send your console output and script version.", True),
        card("/", "bag", "Visit the store", "Every script, with prices and checkout.", False),
    ])
    home = f"""<section class="hero">
<img class="hlogo" src="/assets/logo.webp" alt="Huncho World Store" width="640" height="632">
<h1>Complete Guides for Everything <span>Huncho World</span></h1>
<p>Installation guides, setup, integrations &amp; fixes for every Huncho World FiveM script.</p>
<button class="bigsearch" data-search>{icon('search')}<span>Search guides, fixes &amp; config options…</span></button>
</section>
<section class="blk"><h2>Common solutions</h2><div class="cards">{common}</div></section>
<section class="blk"><h2>Script guides</h2><div class="cards">{guides}</div></section>
<section class="blk"><h2>Need a hand?</h2><div class="cards three">{hand}</div></section>"""
    open(os.path.join(OUT, "index.html"), "w").write(shell("Huncho World Docs", "Guides for every Huncho World FiveM script.", home, home=True))

    from PIL import Image
    for src, rel in ASSETS:
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel.endswith(".webp") and not src.lower().endswith(".webp"):
            im = Image.open(src)
            im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
            if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
            im.save(dst, "WEBP", quality=82, method=6)
        else:
            shutil.copy2(src, dst)
    json.dump(index, open(os.path.join(OUT, "search.json"), "w"), separators=(",", ":"))
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copy2(os.path.join(here, "docs.css"), os.path.join(OUT, "docs.css"))
    shutil.copy2(os.path.join(here, "docs.js"), os.path.join(OUT, "docs.js"))
    print(f"built {len(pages)} pages, {len(ASSETS)} assets → {OUT}")

def order_first(s):
    return NAV[s["slug"]][0]["items"][0]["file"]

main()

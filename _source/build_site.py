#!/usr/bin/env python3
"""Generate adam-costa.com static site from Obsidian/WordPress markdown export."""
import os, re, shutil, sys
import markdown
from markdown.extensions.toc import slugify

SRC = "/sessions/relaxed-brave-dirac/mnt/Website"
OUT = os.environ.get("SITE_OUT", "/tmp/site")

SITE_NAME = "Adam Costa"

# ---------------- content structure ----------------
FF_PARTS = [
    ("Part 1: Overview and strategy", [
        ("ff1-the-exact-roadmap", "Financial freedom in 10 minutes"),
        ("how-much-money-do-i-need-to-retire-at-40", "How much money do you need?"),
        ("levels-of-financial-freedom", "Levels of financial freedom"),
        ("difference-between-assets-liabilities", "Assets vs. liabilities"),
    ]),
    ("Part 2: Reduce your expenses", [
        ("housing", "Reduce your housing expenses"),
        ("taxes", "Pay less tax"),
        ("transportation", "Transportation"),
    ]),
    ("Part 3: Increase your income", [
        ("ask-for-a-raise", "Ask for a raise"),
        ("work-remotely", "Work remotely"),
        ("creating-assets", "Create assets"),
        ("consulting", "Consulting (or coaching)"),
        ("buying-businesses", "Buy businesses"),
    ]),
    ("Part 4: Invest your savings", [
        ("investment-order", "Investment order"),
        ("asset-allocation", "Asset allocation"),
        ("build-wealth-automatically", "Automate your investments"),
        ("withdraw-your-money", "Withdraw your money"),
    ]),
]
FF_CHAPTERS = [c for _, cs in FF_PARTS for c in cs]

PROD_CHAPTERS = [
    ("introduction-what-youll-get-in-this-course", "Introduction"),
    ("chapter-1-find-your-purpose", "Find your purpose"),
    ("chapter-2-pinpoint-and-prioritize-your-goals", "Pinpoint and prioritize your goals"),
    ("chapter-3-optimize-your-workflow", "Optimize your workflow"),
    ("chapter-4-maximize-your-willpower", "Maximize your willpower"),
    ("chapter-5-build-rock-solid-routines", "Build rock-solid routines"),
    ("chapter-6-block-distractions", "Block distractions"),
    ("chapter-7-follow-through", "Follow through"),
    ("conclusion-what-to-do-next", "Conclusion: what to do next"),
    ("additional-resources", "More resources"),
]

LIFE_PAGES = [
    ("sleepless", "Sleep(less)", "My quest to end insomnia, once and for all."),
    ("journey-through-the-gi-tract", "Journey through the GI tract", "What happens to your food after you swallow it."),
    ("knots", "Knots", "The knots I've learned so far—and what each one is for."),
    ("save-money-by-traveling", "Quit yer job and travel", "How the recession sent us around the world—and saved us money."),
    ("media-appearances", "Media appearances", "Interviews and articles elsewhere on the internet."),
]

# ---------------- old URL -> new site-root-relative path ----------------
URL_MAP = {}
for slug, _ in FF_CHAPTERS:
    URL_MAP[slug] = f"financial-freedom/{slug}/"
ALIASES = {
    "freedom-aint-free-so-how-much-does-it-cost-4-rule-explained": "financial-freedom/how-much-money-do-i-need-to-retire-at-40/",
    "the-different-levels-of-financial-freedom": "financial-freedom/levels-of-financial-freedom/",
    "assets-vs-liabilities": "financial-freedom/difference-between-assets-liabilities/",
    "automation": "financial-freedom/build-wealth-automatically/",
}

def map_old_url(url):
    """Map an adam-costa.com URL to a site-root-relative path (may include #anchor)."""
    m = re.match(r"https?://adam-costa\.com/?(.*)$", url)
    if not m:
        return None
    path = m.group(1)
    path, _, anchor = path.partition("#")
    anchor = ("#" + anchor) if anchor else ""
    path = path.strip("/")
    if path.startswith("wp-admin"):
        return anchor or ""
    if "attachment/four-percent-rule-success-rate" in path:
        return "images/Four-Percent-Rule-Success-Rate-700x556.jpg"
    if "attachment/four-percent-rule-median-balance" in path:
        return "images/Four-Percent-Rule-Median-Balance-700x557.jpg"
    path = path.replace("financial-freedom-page", "financial-freedom")
    if path == "":
        return ""
    segs = path.split("/")
    last = segs[-1]
    if last in ALIASES:
        return ALIASES[last] + anchor
    if last in URL_MAP:
        return URL_MAP[last] + anchor
    if path == "financial-freedom":
        return "financial-freedom/" + anchor
    part_anchors = {
        "strategy": "part-1-overview-and-strategy",
        "reduce-expenses": "part-2-reduce-your-expenses",
        "how-to-increase-your-income": "part-3-increase-your-income",
        "automate-scale-your-investments": "part-4-invest-your-savings",
        "part-2-automate-your-investments-and-then-scale-them": "part-4-invest-your-savings",
        "protect-your-wealth-and-pass-it-on": "part-5-protect-your-wealth-and-pass-it-on",
    }
    if last in part_anchors:
        return "financial-freedom/#" + part_anchors[last]
    if segs[0] == "productivity-course":
        if len(segs) == 1:
            return "productivity/" + anchor
        return f"productivity/{last}/" + anchor
    if path == "nutrition":
        return "life/"
    if last == "journey-through-the-gi-tract":
        return "life/journey-through-the-gi-tract/"
    if last in ("privacy", "disclaimer"):
        return f"{last}/"
    life_slugs = [s for s, _, _ in LIFE_PAGES]
    if last in life_slugs:
        return f"life/{last}/"
    print(f"  [warn] unmapped internal URL -> home: {url}")
    return ""

# ---------------- markdown handling ----------------
def read_page(slug):
    with open(os.path.join(SRC, slug + ".md"), encoding="utf-8") as f:
        text = f.read()
    title = None
    if text.startswith("---"):
        end = text.index("---", 3)
        fm = text[3:end]
        body = text[end + 3:]
        m = re.search(r'^title:\s*"(.*)"\s*$', fm, re.M)
        if m:
            title = m.group(1)
    else:
        body = text
    if title:
        title = title.replace("\\", "").strip('"').strip()
    return title, body.strip()

def quote_table(m):
    """WordPress pull-quote 'tables' (| ***quote* ** ... —author |) -> blockquote."""
    inner = m.group(1)
    if "*" not in inner and "—" not in inner:
        return m.group(0)  # not a pull quote; leave alone
    text = inner.replace("*", "")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    quote, author = [], []
    for l in lines:
        (author if (author or l.startswith("—")) else quote).append(l)
    out = "\n> *" + " ".join(quote) + "*\n"
    if author:
        out += ">\n> " + " ".join(author) + "\n"
    return out

def preprocess(md_text):
    t = md_text
    # single-cell pull-quote tables -> blockquotes (no inner pipes = not a real table)
    t = re.sub(r"^\|([^|]+?)\|[ \t]*$", quote_table, t, flags=re.M | re.S)
    # empty bold pairs (** ** / **\xa0**)
    t = re.sub(r"\*\*[\s ]+\*\*", " ", t)
    # bullets with broken emphasis: "- * text**" or "- * text*" -> "- *text*"
    t = re.sub(r"^(-\s+)\*\s+(\S.*?)\*{1,2}\s*$", r"\1*\2*", t, flags=re.M)
    # nbsp glued to bold markers blocks emphasis parsing
    t = t.replace(" **", " **").replace("** ", "** ")
    # ***text *** with stray spaces
    t = re.sub(r"^(\s*-\s+)?\*{3}\s+(.+?)\s*\*{3}\s*$", r"\1***\2***", t, flags=re.M)
    # whole line wrapped in bold with stray trailing space: **text ** -> **text**
    t = re.sub(r"^\*\*(.+?)[ \t]+\*\*[ \t]*$", r"**\1**", t, flags=re.M)
    # bold with stray inner spaces (opener must follow whitespace to avoid cross-pairing)
    t = re.sub(r"(?<![^\s])\*\*(\S[^*\n]*?)[ \t]+\*\*", r"**\1** ", t)
    t = re.sub(r"(?<![^\s])\*\*[ \t]+([^*\n]*?\S)\*\*", r" **\1**", t)
    # tables: merge wrapped rows, insert missing separator rows
    lines = t.split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and "|" in lines[i].lstrip()[1:]:
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                row = lines[i]
                i += 1
                while (not row.rstrip().endswith("|")) and i < len(lines) \
                        and not lines[i].lstrip().startswith(("|", "#")):
                    if lines[i].strip():
                        row = row.rstrip() + " " + lines[i].strip()
                    i += 1
                rows.append(row)
            if rows and rows[0].count("|") >= 3:
                if not (len(rows) > 1 and re.match(r"^\s*\|[\s:|-]+$", rows[1])):
                    cols = rows[0].count("|") - 1
                    rows = [rows[0], "|" + " --- |" * cols] + rows[1:]
            out.extend(rows)
        else:
            out.append(lines[i])
            i += 1
    t = "\n".join(out)
    # drop empty list items and whitespace-only lines
    t = re.sub(r"^\s*-\s*$", "", t, flags=re.M)
    t = re.sub(r"^[ \t]+$", "", t, flags=re.M)
    # repair split headings: an empty "##" line whose text landed on the next line
    t = re.sub(r"^(#{1,6})[ \t]*\n+[ \t]*([^#\-!\s>][^\n]{0,90})\n(?=\s*\n)",
               lambda m: f"{m.group(1)} {m.group(2).strip()}\n", t, flags=re.M)
    # drop remaining empty headings
    t = re.sub(r"^#{1,6}\s*$", "", t, flags=re.M)
    # standalone bare URLs -> watch links
    t = re.sub(
        r"^(https?://(?:www\.)?(?:youtube\.com|youtu\.be|vimeo\.com)\S*)$",
        r'<p class="watch"><a href="\1">Watch the video&nbsp;&#8599;</a></p>',
        t, flags=re.M)
    t = re.sub(r"^(https?://\S+)$", r"[\1](\1)", t, flags=re.M)
    return t

def rewrite_links(md_text, depth):
    rel = "../" * depth
    def repl(m):
        target = map_old_url(m.group(1))
        if target is None:
            return m.group(0)
        if target.startswith("#") or target == "":
            return "](" + (target if target else rel if depth else "./") + ")"
        return "](" + rel + target + ")"
    return re.sub(r"\]\((https?://adam-costa\.com[^)\s]*)\)", repl, md_text)

USED_IMAGES = set()

def postprocess_html(html, depth):
    rel = "../" * depth
    # collect + rewrite image srcs
    def img_src(m):
        src = m.group(1)
        USED_IMAGES.add(src.split("/", 1)[1])
        return f'src="{rel}{src}"'
    html = re.sub(r'src="(images/[^"]+)"', img_src, html)
    # links pointing at images: fix path depth; fall back to an existing size variant
    def img_href(m):
        fname = m.group(1)
        if not os.path.exists(os.path.join(SRC, "images", fname)):
            import glob
            stem = os.path.splitext(fname)[0]
            cands = sorted(glob.glob(os.path.join(SRC, "images", stem + "-*")))
            if not cands:
                print(f"  [warn] missing image target {fname}")
                return m.group(0)
            fname = os.path.basename(cands[0])
        USED_IMAGES.add(fname)
        return f'href="{rel}images/{fname}"'
    html = re.sub(r'href="images/([^"]+)"', img_href, html)
    # figure/caption: <p><img ...>caption</p>
    def figure(m):
        img, caption = m.group(1), m.group(2).strip()
        if caption:
            return f"<figure>{img}<figcaption>{caption}</figcaption></figure>"
        return f"<figure>{img}</figure>"
    html = re.sub(r"<p>((?:<a [^>]*>)?<img[^>]+>(?:</a>)?)\s*(.*?)</p>", figure, html, flags=re.S)
    # responsive tables
    html = html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    # fix in-page anchors that don't match generated heading ids
    ids = set(re.findall(r'id="([^"]+)"', html))
    def fix_anchor(m):
        a = m.group(1)
        if a in ids:
            return m.group(0)
        tokens = [w for w in re.split(r"[^a-z0-9]+", a.lower()) if w]
        best = None
        for hid in ids:
            hw = set(re.split(r"[^a-z0-9]+", hid.lower()))
            if all(tok in hw for tok in tokens):
                best = hid
                break
        if best is None:
            for hid in ids:
                if tokens and tokens[0] in hid:
                    best = hid
                    break
        if best:
            return f'href="#{best}"'
        print(f"  [warn] unresolved anchor #{a}")
        return m.group(0)
    html = re.sub(r'href="#([^"]+)"', fix_anchor, html)
    return html

def md_to_html(md_text, depth):
    t = preprocess(md_text)
    t = rewrite_links(t, depth)
    html = markdown.markdown(t, extensions=["tables", "sane_lists", "toc"])
    return postprocess_html(html, depth)

# ---------------- template ----------------
def page(depth, title, content, description="", active=""):
    from navdata import render_nav
    rel = "../" * depth
    desc = f'\n  <meta name="description" content="{description}">' if description else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>{desc}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{rel}style.css">
</head>
<body>
<div class="container">
  <header>
    <a class="site-name" href="{rel if depth else './'}">{SITE_NAME}</a>
    {render_nav(rel, active)}
  </header>
  <main>
{content}
  </main>
  <footer>
    <p>&copy; Adam Costa &middot; <a href="{rel}privacy/">Privacy</a> &middot; <a href="{rel}disclaimer/">Disclaimer</a></p>
  </footer>
</div>
</body>
</html>
"""

def write_page(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)

def prevnext(items, i, base_rel):
    """items: list of (slug, short_title); pages live at ../<slug>/ relative to each other."""
    parts = []
    if i > 0:
        s, t = items[i - 1]
        parts.append(f'<a class="pn prev" href="../{s}/"><span class="pn-label">&larr; Previous</span><span class="pn-title">{t}</span></a>')
    else:
        parts.append('<span class="pn"></span>')
    if i < len(items) - 1:
        s, t = items[i + 1]
        parts.append(f'<a class="pn next" href="../{s}/"><span class="pn-label">Next &rarr;</span><span class="pn-title">{t}</span></a>')
    else:
        parts.append('<span class="pn"></span>')
    return '<nav class="prevnext">' + "".join(parts) + "</nav>"

def chapter_page(slug, kicker_html, body_html, pn_html, title, active):
    content = f"""<article>
  <p class="kicker">{kicker_html}</p>
  <h1>{title}</h1>
{body_html}
</article>
{pn_html}"""
    return page(2, f"{title} — {SITE_NAME}", content, active=active)

# ---------------- build ----------------
def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # --- financial freedom chapters ---
    for pi, (part_title, chapters) in enumerate(FF_PARTS):
        for slug, short in chapters:
            i = FF_CHAPTERS.index((slug, short))
            title, body = read_page(slug)
            print(f"FF ch{i+1}: {slug}")
            html = md_to_html(body, 2)
            kicker = f'<a href="../">Financial freedom</a> &middot; {part_title.split(":")[0]}'
            pn = prevnext(FF_CHAPTERS, i, "../")
            write_page(f"financial-freedom/{slug}/index.html",
                       chapter_page(slug, kicker, html, pn, title, "ff"))

    # --- productivity chapters ---
    for i, (slug, short) in enumerate(PROD_CHAPTERS):
        title, body = read_page(slug)
        print(f"PROD: {slug}")
        html = md_to_html(body, 2)
        kicker = '<a href="../">How to live your best life</a>'
        pn = prevnext(PROD_CHAPTERS, i, "../")
        write_page(f"productivity/{slug}/index.html",
                   chapter_page(slug, kicker, html, pn, title, "prod"))

    # --- life essays ---
    for slug, nice_title, desc in LIFE_PAGES:
        title, body = read_page(slug)
        print(f"LIFE: {slug}")
        # trim trailing empty headings (unfinished drafts)
        body = re.sub(r"(\n#{1,6}[^\n]*\s*)+$", "\n", body)
        html = md_to_html(body, 2)
        kicker = '<a href="../">Life</a>'
        content = f"""<article>
  <p class="kicker">{kicker}</p>
  <h1>{nice_title}</h1>
{html}
</article>"""
        write_page(f"life/{slug}/index.html",
                   page(2, f"{nice_title} — {SITE_NAME}", content, desc, active="life"))

    # --- financial freedom landing ---
    title, body = read_page("financial-freedom")
    body += ("\n\n## Part 5: Protect your wealth and pass it on\n\n"
             "Create a will, and plan your estate. (Chapters coming&hellip; eventually.)\n")
    html = md_to_html(body, 1)
    content = f"""<article>
  <p class="kicker">A free book</p>
  <h1>Financial freedom: the ultimate guide</h1>
{html}
</article>"""
    write_page("financial-freedom/index.html",
               page(1, f"Financial freedom — {SITE_NAME}",
                    content, "A free 16-chapter book on reaching financial independence.", active="ff"))

    # --- productivity landing ---
    title, body = read_page("productivity-course")
    html = md_to_html(body, 1)
    content = f"""<article>
  <p class="kicker">A free book</p>
  <h1>How to live your best life</h1>
{html}
</article>"""
    write_page("productivity/index.html",
               page(1, f"Productivity — {SITE_NAME}",
                    content, "A free book on purpose, focus, and follow-through.", active="prod"))

    # --- life index ---
    items = "\n".join(
        f'<li><a href="{slug}/">{t}</a><span class="item-desc">{d}</span></li>'
        for slug, t, d in LIFE_PAGES)
    content = f"""<article>
  <h1>Life</h1>
  <p>Essays and notes on everything else: sleep, food, travel, and rope.</p>
  <ul class="index-list">
{items}
  </ul>
</article>"""
    write_page("life/index.html",
               page(1, f"Life — {SITE_NAME}", content,
                    "Essays and notes on sleep, food, travel, and rope.", active="life"))

    # --- privacy & disclaimer ---
    for slug in ("privacy", "disclaimer"):
        title, body = read_page(slug)
        html = md_to_html(body, 1)
        content = f"<article>\n  <h1>{title}</h1>\n{html}\n</article>"
        write_page(f"{slug}/index.html", page(1, f"{title} — {SITE_NAME}", content))

    # --- homepage ---
    life_items = "\n".join(
        f'<li><a href="life/{slug}/">{t}</a><span class="item-desc">{d}</span></li>'
        for slug, t, d in LIFE_PAGES)
    content = f"""<div class="home">
  <h1>Hi, I'm Adam.</h1>
  <p class="lede">I write about money, productivity, and living well. I've published two books on those subjects&mdash;both are free to read here, in full.</p>

  <section>
    <h2><a href="financial-freedom/">Financial freedom: the ultimate guide</a></h2>
    <p>How to achieve financial independence, travel the world, and live off your investments forever. Sixteen chapters covering strategy, cutting your biggest expenses, increasing your income, and investing&mdash;on autopilot.</p>
    <p><a class="cta" href="financial-freedom/">Start reading &rarr;</a></p>
  </section>

  <section>
    <h2><a href="productivity/">How to live your best life</a></h2>
    <p>A simple blueprint to help you find your purpose, sharpen your focus, and do what <em>really</em> matters&mdash;from defining your goals to building rock-solid routines, blocking distractions, and following through on everything.</p>
    <p><a class="cta" href="productivity/">Start reading &rarr;</a></p>
  </section>

  <section>
    <h2><a href="life/">Life</a></h2>
    <p>Essays and notes on everything else.</p>
    <ul class="index-list">
{life_items}
    </ul>
  </section>
</div>"""
    write_page("index.html",
               page(0, f"{SITE_NAME} — money, productivity, and living well",
                    content, "Two free books—on financial freedom and productivity—plus essays on living well."))

    # --- 404 ---
    content = """<article>
  <h1>Page not found</h1>
  <p>That page doesn't exist (or moved). Try the <a href="/">homepage</a>.</p>
</article>"""
    write_page("404.html", page(0, f"Page not found — {SITE_NAME}", content))

    # --- copy used images ---
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    missing = []
    for img in sorted(USED_IMAGES):
        src = os.path.join(SRC, "images", img)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, "images", img))
        else:
            missing.append(img)
    # images linked (not embedded) via attachment mapping
    for img in ("Four-Percent-Rule-Success-Rate-700x556.jpg", "Four-Percent-Rule-Median-Balance-700x557.jpg"):
        src = os.path.join(SRC, "images", img)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, "images", img))
    print(f"\nImages copied: {len(os.listdir(os.path.join(OUT, 'images')))}, missing: {missing}")

if __name__ == "__main__":
    build()
    print("done")

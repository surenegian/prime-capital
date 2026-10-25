import re, json, os, shutil, filecmp, pathlib

# Which app appearance the screenshots show. Both sets live in appearances/<name>/ under the same
# file names; change this one word and run `python3 generator.py` to switch the whole site.
# (PC_APPEARANCE=burgundy python3 generator.py builds the other one without editing this file.)
APPEARANCE = os.environ.get("PC_APPEARANCE", "espresso")   # "espresso" or "burgundy"
ACCENTS = {"espresso": "#1f4d3a", "burgundy": "#6b1d2e"}   # small page accent that sits best with each

SRC = pathlib.Path(__file__).parent / "raw-source"
OUT = pathlib.Path(__file__).parent / "site"

CSS_NAMES = ["3cgp9wgn1jz2r.css", "2yivp3fx_0wqo.css", "42i-eaj0l7rw6.css"]

SITE_URL = "https://prime-capital-app.pages.dev"
LOGO_IMG = "assets/img/v1-86ff3b4995f993732fca-9cfdf38b9eba223c.webp"
OG_IMAGE = "assets/img/og-image.png"

# privacy/support/terms shipped with AppLaunchFlow's own unedited SEO/OG
# metadata (their tagline, their site name, their opengraph.png) -- this is
# the real Prime Capital copy for each page, keyed by page slug ("" = home)
PAGE_SEO = {
    "": (
        "Prime Capital — Privacy-First Personal Finance for iPhone",
        "Prime Capital is a local-first personal finance tracker for iPhone with no server, "
        "no sign-up, and no ads. Your accounts and transactions stay on your device or your "
        "own private iCloud — never on ours. Available in English, German, Spanish, French, "
        "Italian, Dutch, Portuguese, Russian, and Armenian.",
    ),
    "privacy": (
        "Privacy Policy – Prime Capital",
        "How Prime Capital handles your data: no server, no account, no analytics, and no ad "
        "tracking. Everything stays on your device or your own private iCloud.",
    ),
    "terms": (
        "Terms of Service – Prime Capital",
        "The terms governing use of Prime Capital, a local-first personal finance tracker for iPhone.",
    ),
    "support": (
        "Support – Prime Capital",
        "Get help with Prime Capital, or contact us directly with a question or issue.",
    ),
}


def fix_seo_meta(html: str, page: str) -> str:
    title, desc = PAGE_SEO[page]
    canonical = f"{SITE_URL}/{page + '/' if page else ''}"
    image = f"{SITE_URL}/{OG_IMAGE}"
    html = re.sub(r'<meta name="description" content="[^"]*"/>',
                  f'<meta name="description" content="{desc}"/>', html)
    html = re.sub(r'<link rel="canonical" href="[^"]*"/>',
                  f'<link rel="canonical" href="{canonical}"/>', html)
    html = re.sub(r'<meta property="og:title" content="[^"]*"/>',
                  f'<meta property="og:title" content="{title}"/>', html)
    html = re.sub(r'<meta property="og:description" content="[^"]*"/>',
                  f'<meta property="og:description" content="{desc}"/>', html)
    html = re.sub(r'<meta property="og:site_name" content="[^"]*"/>',
                  '<meta property="og:site_name" content="Prime Capital"/>', html)
    html = re.sub(r'<meta property="og:image" content="[^"]*"/>',
                  f'<meta property="og:image" content="{image}"/>', html)
    html = re.sub(r'<meta property="og:image:width" content="[^"]*"/>',
                  '<meta property="og:image:width" content="1200"/>', html)
    html = re.sub(r'<meta property="og:image:height" content="[^"]*"/>',
                  '<meta property="og:image:height" content="630"/>', html)
    html = re.sub(r'<meta property="og:image:alt" content="[^"]*"/>',
                  '<meta property="og:image:alt" content="Prime Capital"/>', html)
    html = re.sub(r'<meta name="twitter:title" content="[^"]*"/>',
                  f'<meta name="twitter:title" content="{title}"/>', html)
    html = re.sub(r'<meta name="twitter:description" content="[^"]*"/>',
                  f'<meta name="twitter:description" content="{desc}"/>', html)
    html = re.sub(r'<meta name="twitter:image" content="[^"]*"/>',
                  f'<meta name="twitter:image" content="{image}"/>', html)
    return html

# real on-device screenshots the user supplied directly (not App Store
# composites with a baked-in wordmark/caption, not AppLaunchFlow's generic
# stock mockups) -- actual Prime Capital screens, full-bleed inside the frame
PHONE_SHOTS = [
    ("shot-dashboard.webp", "Dashboard: net worth, accounts, and recent activity"),
    ("shot-accounts.webp", "Accounts screen with income, expenses, and transaction counts"),
    ("shot-transfer.webp", "Transfer screen moving funds between accounts"),
    ("shot-add-expense.webp", "Add a new expense with account and category picker"),
    ("shot-settings.webp", "Settings: currency, categories, appearance, and security"),
    ("feature-currency.webp", "Multi-currency account with a live exchange rate"),
    ("feature-design.webp", "Appearance settings with the color theme picker"),
    ("feature-lockscreen.webp", "Face ID / PIN lock screen"),
    ("feature-reports.webp", "Generated PDF financial report"),
    ("feature-import.webp", "Importing a bank statement"),
    ("feature-budgets.webp", "Budgets: monthly spending limits per category"),
    ("feature-profiles.webp", "Profiles: Personal and Business"),
    ("shot-statistics.webp", "Statistics: spending by category and balance growth"),
]

# Screenshots are 1320px wide but shown at ~150-260px. Lossless 780px copies
# (3x the widest display size) cut each file roughly in half with no quality
# loss; the originals stay as the srcset fallback. Built here, not by hand.
SHOT_W = 780
IMG_DIR = OUT / "assets" / "img"

def _variant(shot: str) -> str:
    return shot.replace(".webp", f"-{SHOT_W}.webp")

def _build_variants():
    from PIL import Image
    for shot, _ in PHONE_SHOTS:
        src, dst = IMG_DIR / shot, IMG_DIR / _variant(shot)
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        im = Image.open(src)
        im.resize((SHOT_W, round(im.height * SHOT_W / im.width)), Image.LANCZOS).save(
            dst, "WEBP", lossless=True, quality=100, method=6)

# iPhone Duo: the app screens composited into the real device frames (appearances/frames/,
# screen offsets from the frames' frames.json), then scaled to 1640px for the open device.
# (state, frame, screenshot, screen offset, screen corner radius, which corners are round: tl tr br bl)
DUO = [("closed", "duo-outer.webp", "outer.webp", (126, 78), 245, (False, True, True, False)),
       ("open", "duo-inner.webp", "inner.webp", (114, 114), 126, (True, True, True, True))]
DUO_SCALE = 1640 / 3082   # open frame width -> output width; closed uses the same scale

def _duo_cover(im):
    """Fit the closed phone onto the right half of the open one, edge to edge, so it can be the
    cover that swings open: outer body x 66..1584, y 20..2170 -> open body's right half x 0..1499, y 40..2195
    (measured from the two frames). x 19..65 is the hinge spine drawn beside the phone; it is cut off,
    since it reads as a separate object once the cover lifts. x 66 starts the same 24px rim as the right edge."""
    from PIL import Image, ImageChops, ImageDraw
    sx, sy = 1499 / (1584 - 66), (2195 - 40) / (2170 - 20)
    body = im.resize((round(im.width * sx), round(im.height * sy)), Image.LANCZOS)
    half = Image.new("RGBA", (3082 // 2, 2236))
    body = body.crop((round(66 * sx), 0, round(66 * sx) + half.width, body.height))  # drop the spine
    half.alpha_composite(body, (0, round(40 - 20 * sy)))
    # round the hinge-side corners like the others (screen radius 47 + 60 of bezel and rim), which also
    # clears the cut-off ends of the spine poking past the top and bottom
    r, top, bot = 107, 40, 2195
    keep = Image.new("L", half.size, 255)
    d = ImageDraw.Draw(keep)
    d.rectangle((0, 0, r, top + r), 0); d.ellipse((0, top, 2 * r, top + 2 * r), 255)
    d.rectangle((0, bot - r, r, half.height), 0); d.ellipse((0, bot - 2 * r, 2 * r, bot), 255)
    half.putalpha(ImageChops.multiply(half.getchannel("A"), keep))
    return half

def _build_duo():
    from PIL import Image, ImageChops, ImageDraw
    base = pathlib.Path(__file__).parent / "appearances"
    for state, frame, shot, xy, radius, corners in DUO:
        # ponytail: an appearance without its own Duo captures borrows espresso's; capture them to fix
        shot_src = next(p for p in (base / APPEARANCE / "duo" / shot, base / "espresso" / "duo" / shot) if p.exists())
        srcs = [base / "frames" / frame, shot_src]
        dst = IMG_DIR / f"duo-{state}.webp"
        if dst.exists() and dst.stat().st_mtime >= max(s.stat().st_mtime for s in srcs):
            continue
        f = Image.open(srcs[0]).convert("RGBA")
        im = Image.new("RGBA", f.size)
        screen = Image.open(srcs[1]).convert("RGBA")
        mask = Image.new("L", screen.size)   # the outer screen's big corners reach past the device outline
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *screen.size), radius, fill=255, corners=corners)
        im.paste(screen, xy, mask)
        im.alpha_composite(f)
        if state == "closed":
            im = _duo_cover(im)
        else:   # bare body only (x 40..3040, y 40..2195), with the cover's rounder corners (320, not the
                # frame's 200): otherwise its buttons and squarer corners poke out past the cover as it swings
            keep = Image.new("L", im.size)
            ImageDraw.Draw(keep).rounded_rectangle((40, 40, 3040, 2195), 320, fill=255)
            im.putalpha(ImageChops.multiply(im.getchannel("A"), keep))
        im.resize((round(im.width * DUO_SCALE), round(im.height * DUO_SCALE)), Image.LANCZOS).save(
            dst, "WEBP", lossless=True, quality=100, method=6)

def apply_appearance():
    src = pathlib.Path(__file__).parent / "appearances" / APPEARANCE
    assert src.is_dir(), f"no screenshots for appearance {APPEARANCE!r} in {src}"
    for f in sorted(src.glob("*.webp")):
        dst = IMG_DIR / f.name
        if dst.exists() and filecmp.cmp(f, dst, shallow=False):
            continue
        shutil.copyfile(f, dst)                      # new mtime, so the 780px copy is rebuilt below
        (IMG_DIR / _variant(f.name)).unlink(missing_ok=True)
    print("appearance:", APPEARANCE)

def transform(html: str, prefix: str, page: str = "") -> str:
    html = fix_seo_meta(html, page)
    # drop every script tag (external + inline hydration payloads)
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<script\b[^>]*/>", "", html)
    # drop now-pointless preload/modulepreload links (real stylesheet links stay)
    html = re.sub(r'<link[^>]*rel="modulepreload"[^>]*/?>', "", html)
    html = re.sub(r'<link[^>]*as="script"[^>]*/?>', "", html)
    html = re.sub(r'<link[^>]*as="style"[^>]*/?>', "", html)
    html = re.sub(r'<link[^>]*as="fetch"[^>]*model/gltf-binary[^>]*/?>', "", html)
    html = re.sub(r'<link[^>]*\.hdr"[^>]*/?>', "", html)
    # css chunks -> local, relative to this page's depth
    for name in CSS_NAMES:
        html = re.sub(r'/_next/static/chunks/' + re.escape(name) + r'\?[^"]*', f'{prefix}assets/css/{name}', html)
    # supabase-hosted screenshots -> local
    html = re.sub(
        r'https://ubvbpgodmmitzutgshzu\.supabase\.co/storage/v1/object/public/website-assets/[^"]*/([^"/]+\.webp)',
        prefix + r'assets/img/\1',
        html,
    )
    # local app store badge svg + favicon, standardized everywhere
    html = html.replace(
        "/promovideo/Download_on_the_App_Store_Badge_US-UK_RGB_blk_092917.svg",
        f"{prefix}assets/img/app-store-badge.svg",
    )
    # AppLaunchFlow's own favicon.png (their lightning-bolt mark) was still
    # wired up on privacy/support/terms -- point every favicon/apple-touch-icon
    # reference at the real Prime Capital logo instead, same as the homepage
    html = html.replace(
        'href="/favicon.png"',
        f'href="{prefix}assets/img/v1-86ff3b4995f993732fca-9cfdf38b9eba223c.webp"',
    )
    # nav "Download" button was a dead client-side-only control -> real App Store link
    html = html.replace(
        '<button type="button" class="alf-btn alf-btn-primary " aria-hidden="false" tabindex="0">',
        '<a href="https://apps.apple.com/app/id6792149434" target="_blank" rel="noopener noreferrer" class="alf-btn alf-btn-primary">',
    ).replace(
        '<path d="M204,64V168a12,12,0,0,1-24,0V93L72.49,200.49a12,12,0,0,1-17-17L163,76H88a12,12,0,0,1,0-24H192A12,12,0,0,1,204,64Z"></path></svg></button>',
        '<path d="M204,64V168a12,12,0,0,1-24,0V93L72.49,200.49a12,12,0,0,1-17-17L163,76H88a12,12,0,0,1,0-24H192A12,12,0,0,1,204,64Z"></path></svg></a>',
    )
    # doc pages (privacy/terms/support) get the same 4-item footer link row
    # as the homepage, except the link to the page you're already ON is
    # replaced with a link back to Home instead (no point linking to itself)
    if '<a class="alf-btn alf-btn-ghost" href="/">' in html:
        doc_links = [("privacy", "Privacy"), ("terms", "Terms"), ("support", "Support")]
        items = "".join(
            f'<li><a href="/">Home</a></li>' if slug == page
            else f'<li><a href="/{slug}">{label}</a></li>'
            for slug, label in doc_links
        )
        html = html.replace(
            '<div>© <!-- -->2026<!-- --> <!-- -->Prime Capital</div></div></footer>',
            '<div>© <!-- -->2026<!-- --> <!-- -->Prime Capital</div>'
            f'<ul class="alf-footer-links">{items}'
            '<li><a href="mailto:surenegian00@gmail.com"><span class="alf-sr-only">Email</span>'
            '<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" '
            'viewBox="0 0 256 256" aria-hidden="true"><path d="M224,44H32A12,12,0,0,0,20,56V192a20,20,0,0,0,20,20H216a20,'
            '20,0,0,0,20-20V56A12,12,0,0,0,224,44ZM193.15,68,128,127.72,62.85,68ZM44,188V83.28l75.89,69.57a12,12,0,0,0,'
            '16.22,0L212,83.28V188Z"></path></svg></a></li></ul></div></footer>',
        )
    # internal nav -> relative
    html = re.sub(r'href="/privacy"', f'href="{prefix}privacy/"', html)
    html = re.sub(r'href="/support"', f'href="{prefix}support/"', html)
    html = re.sub(r'href="/terms"', f'href="{prefix}terms/"', html)
    html = re.sub(r'href="/"(?!\w)', f'href="{prefix}"' if prefix else 'href="./"', html)
    # stop the browser from restoring the previous scroll position on a
    # redeploy/reload -- felt like lag, since the page would flash to top
    # then jump back to wherever the visitor was before the update landed
    html = html.replace("<head>", "<head><script>if('scrollRestoration' in history){history.scrollRestoration='manual';}window.scrollTo(0,0);</script>", 1)
    return html

# The home page is our own template (templates/home.html). The other three pages
# are still the AppLaunchFlow templates, transformed and re-skinned to match it.
# privacy/terms/support: the legal copy still comes from the AppLaunchFlow files in
# raw-source/ (it is the source of truth for the wording), but it is poured into our
# own templates/doc.html so these pages share the home page's header, type and footer.
DOC_PAGES = {
    "pc-privacy.html": (OUT / "privacy" / "index.html", "privacy"),
    "pc-support.html": (OUT / "support" / "index.html", "support"),
    "pc-terms.html": (OUT / "terms" / "index.html", "terms"),
}

APP_STORE_ID = "6792149434"
PAPER = "#f7f5f0"   # warm stone; the same value the home template uses

FACT_FIXES = {
    "(24 supported)": "(25 supported)",   # CurrencyCode now has 25 cases (Armenian dram added)
}

def extract_doc(raw: str):
    """Pull (title, updated, body_html) out of a vendor doc page."""
    title = re.search(r'<h1[^>]*>(.*?)</h1>', raw, re.S).group(1).strip()
    meta = re.sub(r"<!--.*?-->", "", re.search(r'<p class="alf-doc-meta">(.*?)</p>', raw, re.S).group(1))
    updated = re.sub(r"\s+", " ", meta.split("Last updated")[1]).strip()
    body = re.search(r'<div class="alf-prose">(.*?)</div>', raw, re.S).group(1)
    body = re.sub(r"<!--.*?-->", "", body)
    # facts that changed in the app after the vendor copy was written (checked against the app source)
    for old, new in FACT_FIXES.items():
        body = body.replace(old, new)
    # the vendor body repeats the page title as its first heading
    body = re.sub(r"^\s*<h2>" + re.escape(title) + r"</h2>", "", body)
    # internal and mailto links should not open new tabs; external ones keep it
    def link(m):
        href = m.group(1)
        if href.startswith("http"):
            return f'<a href="{href}" target="_blank" rel="noopener noreferrer">'
        if href.startswith("/"):
            href = ".." + href + ("/" if not href.endswith("/") else "")
        return f'<a href="{href}">'
    body = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>', link, body)
    return title, updated, body

def doc_seo(page: str) -> str:
    title, desc = PAGE_SEO[page]
    image = f"{SITE_URL}/{OG_IMAGE}"
    url = f"{SITE_URL}/{page}/"
    return "\n".join([
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}">',
        f'<link rel="canonical" href="{url}">',
        f'<meta name="theme-color" content="{PAPER}">',
        f'<link rel="icon" href="../{LOGO_IMG}">',
        f'<link rel="apple-touch-icon" href="../{LOGO_IMG}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Prime Capital">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<meta name="twitter:image" content="{image}">',
    ])

def home_seo() -> str:
    """Everything that goes in the home page <head> besides the template's own CSS."""
    title, desc = PAGE_SEO[""]
    image = f"{SITE_URL}/{OG_IMAGE}"
    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Prime Capital",
        "operatingSystem": "iOS",
        "applicationCategory": "FinanceApplication",
        "url": SITE_URL + "/",
        "downloadUrl": f"https://apps.apple.com/app/id{APP_STORE_ID}",
        "description": desc,
        "inLanguage": ["en", "de", "es", "fr", "it", "nl", "pt", "ru", "hy"],
        "sameAs": ["https://www.linkedin.com/company/prime-capital-finance", "https://www.instagram.com/primecapitalapp"],
    }, ensure_ascii=False)
    return "\n".join([
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}">',
        f'<link rel="canonical" href="{SITE_URL}/">',
        f'<meta name="theme-color" content="{PAPER}">',
        f'<meta name="apple-itunes-app" content="app-id={APP_STORE_ID}">',
        f'<link rel="icon" href="{LOGO_IMG}">',
        f'<link rel="apple-touch-icon" href="{LOGO_IMG}">',
        '<link rel="preload" as="image" href="assets/img/shot-dashboard-780.webp">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Prime Capital">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="{SITE_URL}/">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="Prime Capital">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<meta name="twitter:image" content="{image}">',
        f'<script type="application/ld+json">{ld}</script>',
    ])

apply_appearance()
_build_variants()
_build_duo()

home = (pathlib.Path(__file__).parent / "templates" / "home.html").read_text()
assert home.count("<!--SEO-->") == 1
(OUT / "index.html").write_text(home.replace("<!--SEO-->", home_seo(), 1).replace("__ACCENT__", ACCENTS[APPEARANCE]))
print(OUT / "index.html", len(home), "bytes (template)")

doc_tpl = (pathlib.Path(__file__).parent / "templates" / "doc.html").read_text()
for src_name, (dest, page) in DOC_PAGES.items():
    title, updated, body = extract_doc((SRC / src_name).read_text())
    html = doc_tpl.replace("<!--SEO-->", doc_seo(page), 1).replace("{{ROOT}}", "../").replace("__ACCENT__", ACCENTS[APPEARANCE])
    html = html.replace("{{TITLE}}", title).replace("{{UPDATED}}", updated).replace("{{BODY}}", body)
    for slug in ("privacy", "terms", "support"):
        html = html.replace("{{NAV_" + slug + "}}", ' aria-current="page"' if slug == page else "")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    print(dest, len(html), "bytes")

(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE_URL}/{slug + '/' if slug else ''}</loc></url>\n" for slug in PAGE_SEO)
    + "</urlset>\n"
)

import re, json, pathlib

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
DOC_PAGES = {
    "pc-privacy.html": (OUT / "privacy" / "index.html", "../", "privacy"),
    "pc-support.html": (OUT / "support" / "index.html", "../", "support"),
    "pc-terms.html": (OUT / "terms" / "index.html", "../", "terms"),
}

APP_STORE_ID = "6792149434"
PAPER = "#f7f5f0"   # warm stone; the same value the home template uses

# Re-skin of the vendor pages so privacy/terms/support read as the same product
# as the home page: same paper color, same SF display type, same ink. Every
# --w-* token is overridden (not just accent) because the vendor CSS bakes its
# dark values into the raw template.
BRAND_VARS = {
    '--w-font-display:&quot;Inter Variable&quot;, &quot;Inter&quot;, ui-sans-serif, system-ui, -apple-system, &quot;Segoe UI&quot;, sans-serif':
        '--w-font-display:-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif',
    '--w-font-body:&quot;Inter Variable&quot;, &quot;Inter&quot;, ui-sans-serif, system-ui, -apple-system, &quot;Segoe UI&quot;, sans-serif':
        '--w-font-body:-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
    '--w-display-tracking:-0.03em': '--w-display-tracking:-0.035em',
    '--w-display-weight:750': '--w-display-weight:600',
    '--w-radius:20px': '--w-radius:14px',
    '--w-bg:#0a0a0a': f'--w-bg:{PAPER}',
    '--w-fg:#ffffff': '--w-fg:#131313',
    '--w-muted:#b7b7b7': '--w-muted:#67655f',
    '--w-card:#FF6B72': '--w-card:#ffffff',
    '--w-border:rgba(255, 255, 255, 0.14)': '--w-border:rgba(19, 19, 19, 0.11)',
    '--w-band:#1b1b1b': '--w-band:#ece9e1',
    '--w-accent:#ff6b72': '--w-accent:#131313',
    '--w-primary:#0a0a0a': '--w-primary:#ece9e1',
    '--w-primary-fg:#ffffff': '--w-primary-fg:#131313',
    '--w-secondary:#1b1b1b': '--w-secondary:#e3dfd5',
    '--w-secondary-fg:#ffffff': '--w-secondary-fg:#131313',
    '--w-accent-fg:#ffffff': '--w-accent-fg:#ffffff',
    '--w-accent-soft:rgba(255, 107, 114, 0.22)': '--w-accent-soft:rgba(19, 19, 19, 0.06)',
    '--w-accent-glow:rgba(255, 107, 114, 0.45)': '--w-accent-glow:rgba(19, 19, 19, 0.12)',
    '--w-accent-line:rgba(255, 107, 114, 0.55)': '--w-accent-line:rgba(19, 19, 19, 0.35)',
    'color-scheme:dark': 'color-scheme:light',
}

# .alf-btn's pill radius is hardcoded in the vendor CSS (not driven by --w-radius),
# and body{background:var(--background)} is Next.js boilerplate unrelated to the
# themed wrapper -- on mobile a scroll bounce past the wrapper shows raw body, so
# html/body is pinned to the same paper color.
BRAND_STYLE_OVERRIDE = (
    f'<style>.alf-btn{{border-radius:999px;min-height:44px}}html,body{{background:{PAPER}}}'
    '.alf-footer-links a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;min-width:44px}'
    '.alf-cta-panel{background:var(--w-bg)}.alf-cta-panel:before{display:none}</style>'
)

def apply_brand_identity(html: str) -> str:
    for old, new in BRAND_VARS.items():
        html = html.replace(old, new)
    return html.replace("</head>", BRAND_STYLE_OVERRIDE + "</head>")

def drop_dead_preloads(html: str, page_dir: pathlib.Path) -> str:
    # the vendor template preloads its own hero image, which isn't shipped
    def keep(m):
        href = m.group(1)
        return m.group(0) if href.startswith(("http", "/", "data:")) or (page_dir / href).exists() else ""
    return re.sub(r'<link rel="preload"[^>]*?href="([^"]+)"[^>]*/?>', keep, html)

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

_build_variants()

home = (pathlib.Path(__file__).parent / "templates" / "home.html").read_text()
assert home.count("<!--SEO-->") == 1
(OUT / "index.html").write_text(home.replace("<!--SEO-->", home_seo(), 1))
print(OUT / "index.html", len(home), "bytes (template)")

for src_name, (dest, prefix, page) in DOC_PAGES.items():
    html = (SRC / src_name).read_text()
    html = transform(html, prefix, page)
    html = apply_brand_identity(html)
    html = html.replace("</head>", f'<meta name="theme-color" content="{PAPER}"/></head>', 1)
    html = drop_dead_preloads(html, dest.parent)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    print(dest, len(html), "bytes")

(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE_URL}/{slug + '/' if slug else ''}</loc></url>\n" for slug in PAGE_SEO)
    + "</urlset>\n"
)

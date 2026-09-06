import re, pathlib

SRC = pathlib.Path(__file__).parent / "raw-source"
OUT = pathlib.Path(__file__).parent

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

def _phone_hero_html():
    imgs = "".join(
        f'<img src="{{prefix}}assets/img/{shot}" alt="{label}"'
        f' class="pc-phone-shot{" is-active" if i == 0 else ""}" loading="{"eager" if i == 0 else "lazy"}"/>'
        for i, (shot, label) in enumerate(PHONE_SHOTS)
    )
    dots = "".join(
        f'<button type="button" class="pc-phone-dot{" is-active" if i == 0 else ""}"'
        f' aria-label="Show screenshot {i+1}" data-idx="{i}"></button>'
        for i in range(len(PHONE_SHOTS))
    )
    return (
        '<div class="pc-phone">'
        '<div class="pc-phone-frame"><div class="pc-phone-notch"></div>'
        f'<div class="pc-phone-screen">{imgs}</div></div>'
        '<div class="pc-phone-controls">'
        '<button type="button" class="pc-phone-arrow" data-dir="-1" aria-label="Previous screenshot">&#8249;</button>'
        f'<div class="pc-phone-dots">{dots}</div>'
        '<button type="button" class="pc-phone-arrow" data-dir="1" aria-label="Next screenshot">&#8250;</button>'
        '</div></div>'
    )

PHONE_HERO_HTML = _phone_hero_html()

PHONE_STYLE = """<style>
.pc-phone{display:flex;flex-direction:column;align-items:center;gap:18px;height:100%;justify-content:center}
.pc-phone-frame{position:relative;width:min(260px,20vw);aspect-ratio:1320/2868;background:#050505;border-radius:44px;padding:4px;box-shadow:0 0 0 1.5px rgba(255,255,255,.14)}
.pc-phone-notch{position:absolute;top:12px;left:50%;transform:translateX(-50%);width:28%;height:16px;background:#050505;border-radius:10px;z-index:2}
.pc-phone-screen{position:relative;width:100%;height:100%;border-radius:41px;overflow:hidden;background:#000}
.pc-phone-shot{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .45s ease}
.pc-phone-shot.is-active{opacity:1}
.pc-phone-controls{display:flex;align-items:center;gap:16px}
.pc-phone-dots{display:flex;gap:7px}
.pc-phone-dot{width:7px;height:7px;padding:0;border:0;border-radius:999px;background:var(--w-border);cursor:pointer;transition:width .3s cubic-bezier(.2,.7,.2,1),background .3s}
.pc-phone-dot.is-active{width:22px;background:var(--w-accent)}
.pc-phone-arrow{width:32px;height:32px;border-radius:999px;border:1px solid var(--w-border);background:transparent;color:var(--w-fg);font-size:18px;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:border-color .2s,background .2s}
.pc-phone-arrow:hover{border-color:var(--w-accent-line);background:var(--w-accent-soft)}
@media (prefers-reduced-motion:reduce){.pc-phone-shot,.pc-phone-dot{transition:none}}
@media (max-width:760px){
  /* explicit width+height (not aspect-ratio) -- aspect-ratio combined with a
     min()-based width was letterboxing the screenshot on real mobile WebKit,
     meaning the box's rendered height wasn't actually landing on the
     1320:2868 ratio the aspect-ratio property was supposed to derive.
     Computing height directly (same ratio, same min() shape) sidesteps that
     derivation entirely -- both branches are locked to the same ratio by
     construction, so there's nothing left for a browser to get wrong. */
  .pc-phone-frame{box-sizing:content-box;width:min(190px,50vw);height:min(413px,108.64vw);aspect-ratio:auto;border-radius:32px;padding:3px;box-shadow:0 0 0 1.1px rgba(255,255,255,.14)}
  .pc-phone-notch{top:9px;height:12px;border-radius:7px}
  .pc-phone-screen{border-radius:30px}
  .pc-phone-shot{object-fit:contain}
  .alf-story-device .pc-phone{justify-content:flex-end;padding-bottom:8%}
  /* the vendor's own mobile .alf-hero-visual min-height (270px) is shorter
     than the phone+dots/arrows really need (~460-500px) -- the centered
     phone was overflowing upward past .alf-hero's overflow:hidden edge,
     clipping its top. Force enough room so nothing has to overflow. */
  .alf-hero-visual{min-height:500px}
}
</style>"""

# v2 experiment: every mobile dimension below is the desktop value multiplied
# by the exact same ratio as the width (190/260 = 0.7308) -- literally the
# same phone model, just uniformly scaled down, including the bezel padding
# (never scaled in any prior attempt). Desktop/base rules are untouched --
# only this mobile block differs from PHONE_STYLE.
PHONE_STYLE_V2 = """<style>
.pc-phone{display:flex;flex-direction:column;align-items:center;gap:18px;height:100%;justify-content:center}
.pc-phone-frame{position:relative;box-sizing:content-box;width:min(260px,20vw);height:min(565px,43.45vw);background:#050505;border-radius:44px;padding:4px;box-shadow:0 0 0 1.5px rgba(255,255,255,.14)}
.pc-phone-notch{position:absolute;top:12px;left:50%;transform:translateX(-50%);width:28%;height:16px;background:#050505;border-radius:10px;z-index:2}
.pc-phone-screen{position:relative;width:100%;height:100%;border-radius:41px;overflow:hidden;background:#000}
.pc-phone-shot{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity .45s ease}
.pc-phone-shot.is-active{opacity:1}
.pc-phone-controls{display:flex;align-items:center;gap:16px}
.pc-phone-dots{display:flex;gap:7px}
.pc-phone-dot{width:7px;height:7px;padding:0;border:0;border-radius:999px;background:var(--w-border);cursor:pointer;transition:width .3s cubic-bezier(.2,.7,.2,1),background .3s}
.pc-phone-dot.is-active{width:22px;background:var(--w-accent)}
.pc-phone-arrow{width:32px;height:32px;border-radius:999px;border:1px solid var(--w-border);background:transparent;color:var(--w-fg);font-size:18px;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:border-color .2s,background .2s}
.pc-phone-arrow:hover{border-color:var(--w-accent-line);background:var(--w-accent-soft)}
@media (prefers-reduced-motion:reduce){.pc-phone-shot,.pc-phone-dot{transition:none}}
@media (max-width:760px){
  /* explicit width+height (not aspect-ratio) -- aspect-ratio combined with a
     min()-based width was letterboxing the screenshot to ~80% height on real
     mobile WebKit, meaning the box's rendered height wasn't actually landing
     on the 1320:2868 ratio the aspect-ratio property was supposed to derive.
     Computing height directly (same 1320:2868 ratio, same min() shape) sidesteps
     that derivation entirely -- both branches are locked to the same ratio by
     construction, so there's nothing left for a browser to get wrong. */
  .pc-phone-frame{box-sizing:content-box;width:min(190px,50vw);height:min(413px,108.64vw);aspect-ratio:auto;border-radius:32px;padding:3px;box-shadow:0 0 0 1.1px rgba(255,255,255,.14)}
  .pc-phone-notch{top:9px;height:12px;border-radius:7px}
  .pc-phone-screen{border-radius:30px}
  .pc-phone-shot{object-fit:contain}
  .alf-story-device .pc-phone{justify-content:flex-end;padding-bottom:8%}
  /* remove the hero's own phone on mobile entirely -- only the feature
     section's synced phone stays, per explicit request */
  .alf-hero-visual{display:none}
  /* the vendor's own mobile grid still reserves a 2nd row (minmax(0,1fr))
     for the now-hidden phone -- collapse to a single row so the copy
     column doesn't leave dead space where the phone used to be */
  .alf-hero-grid{grid-template-rows:auto}
  /* .alf-hero's own min-height (a clamp sized for phone+copy together) was
     still forcing a tall section even with the phone gone, leaving a big
     empty gap below the copy. Let it size to its actual content instead. */
  .alf-hero{min-height:auto}
}
</style>"""

PHONE_SCRIPT = """<script>
(function(){
  var phone = document.querySelector('.pc-phone');
  if (!phone) return;
  var shots = phone.querySelectorAll('.pc-phone-shot');
  var dots = phone.querySelectorAll('.pc-phone-dot');
  var i = 0;
  var timer = null;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(n) {
    i = (n + shots.length) % shots.length;
    shots.forEach(function(s, idx){ s.classList.toggle('is-active', idx === i); });
    dots.forEach(function(d, idx){ d.classList.toggle('is-active', idx === i); });
  }
  function restartTimer(){
    if (reduceMotion || shots.length < 2) return;
    if (timer) clearInterval(timer);
    timer = setInterval(function(){ show(i + 1); }, 4000);
  }
  dots.forEach(function(d){ d.addEventListener('click', function(){ show(parseInt(d.dataset.idx, 10)); restartTimer(); }); });
  phone.querySelectorAll('.pc-phone-arrow').forEach(function(btn){
    btn.addEventListener('click', function(){ show(i + parseInt(btn.dataset.dir, 10)); restartTimer(); });
  });
  restartTimer();
})();
</script>"""

# --- Feature story: 7 real features, each with its own real screenshot in
# the shared .pc-phone frame (same component/CSS as the hero), crossfading
# in sync with the scroll-driven text panels instead of a big icon ---

ICON_CHART = '<path d="M224,64V208H32V48H208A16,16,0,0,1,224,64Z" opacity="0.2"></path><path d="M232,208a8,8,0,0,1-8,8H32a8,8,0,0,1-8-8V48a8,8,0,0,1,16,0V156.69l50.34-50.35a8,8,0,0,1,11.32,0L128,132.69,180.69,80H160a8,8,0,0,1,0-16h40a8,8,0,0,1,8,8v40a8,8,0,0,1-16,0V91.31l-58.34,58.35a8,8,0,0,1-11.32,0L96,123.31l-56,56V200H224A8,8,0,0,1,232,208Z"></path>'
ICON_LIGHTNING = '<path d="M96,240l16-80L48,136,160,16,144,96l64,24Z" opacity="0.2"></path><path d="M215.79,118.17a8,8,0,0,0-5-5.66L153.18,90.9l14.66-73.33a8,8,0,0,0-13.69-7l-112,120a8,8,0,0,0,3,13l57.63,21.61L88.16,238.43a8,8,0,0,0,13.69,7l112-120A8,8,0,0,0,215.79,118.17ZM109.37,214l10.47-52.38a8,8,0,0,0-5-9.06L62,132.71l84.62-90.66L136.16,94.43a8,8,0,0,0,5,9.06l52.8,19.8Z"></path>'
ICON_WALLET = '<path d="M224,80V192a8,8,0,0,1-8,8H56a16,16,0,0,1-16-16V56A16,16,0,0,0,56,72H216A8,8,0,0,1,224,80Z" opacity="0.2"></path><path d="M216,64H56a8,8,0,0,1,0-16H192a8,8,0,0,0,0-16H56A24,24,0,0,0,32,56V184a24,24,0,0,0,24,24H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64Zm0,128H56a8,8,0,0,1-8-8V78.63A23.84,23.84,0,0,0,56,80H216Zm-48-60a12,12,0,1,1,12,12A12,12,0,0,1,168,132Z"></path>'
ICON_LOCK = '<path d="M216,96V208a8,8,0,0,1-8,8H48a8,8,0,0,1-8-8V96a8,8,0,0,1,8-8H208A8,8,0,0,1,216,96Z" opacity="0.2"></path><path d="M208,80H176V56a48,48,0,0,0-96,0V80H48A16,16,0,0,0,32,96V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V96A16,16,0,0,0,208,80ZM96,56a32,32,0,0,1,64,0V80H96ZM208,208H48V96H208V208Zm-68-56a12,12,0,1,1-12-12A12,12,0,0,1,140,152Z"></path>'
ICON_PALETTE = '<path d="M128,24a104,104,0,1,0,104,104A104.12,104.12,0,0,0,128,24Z" opacity="0.2"></path><path d="M128,16A112,112,0,1,0,240,128,112.13,112.13,0,0,0,128,16Zm0,208a96,96,0,1,1,96-96A96.11,96.11,0,0,1,128,224Z"></path><circle cx="92" cy="108" r="16"></circle><circle cx="164" cy="108" r="16"></circle><circle cx="128" cy="168" r="16"></circle>'
ICON_REPORT = '<path d="M200,88H152V40Z" opacity="0.2"></path><path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48Z"></path><rect x="80" y="128" width="96" height="12" rx="6"></rect><rect x="80" y="152" width="96" height="12" rx="6"></rect><rect x="80" y="176" width="64" height="12" rx="6"></rect>'
ICON_IMPORT = '<rect x="40" y="152" width="176" height="64" rx="12" opacity="0.2"></rect><path d="M224,152v56a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V152a8,8,0,0,1,16,0v56H208V152a8,8,0,0,1,16,0Z"></path><path d="M170.34,133.66l-40,40a8,8,0,0,1-11.32,0l-40-40a8,8,0,0,1,11.32-11.32L120,152V32a8,8,0,0,1,16,0V152l29.66-29.66a8,8,0,0,1,11.32,11.32Z"></path>'

FEATURE_PANELS = [
    ("See Your Full Picture", "View net worth, monthly income, spending, and top categories as soon as you open the app.", ICON_CHART, "shot-dashboard.webp", "Dashboard"),
    ("Add Entries Quickly", "Record an expense or income in a few taps, with custom categories and suggested emojis.", ICON_LIGHTNING, "shot-add-expense.webp", "Add a transaction"),
    ("Multi-Currency, Real Rates", "Add accounts in any of 24 currencies and fetch that day's exchange rate with one tap — never type one in by hand.", ICON_WALLET, "feature-currency.webp", "Currency and live rate"),
    ("Make It Yours", "Switch between eight complete color designs, from OLED black to warm cream, any time in Settings.", ICON_PALETTE, "feature-design.webp", "Appearance and themes"),
    ("Locked Down", "Face ID or a PIN keeps the app closed until you open it — on by default, always under your control.", ICON_LOCK, "feature-lockscreen.webp", "Lock screen"),
    ("A Report, Designed", "Balances, spending, and a 3-month trend — generated as a real PDF you can save or share.", ICON_REPORT, "feature-reports.webp", "PDF report"),
    ("Bring Your Bank Statement", "Import an OFX, QFX, or CSV export from your bank and match its columns in a few taps.", ICON_IMPORT, "feature-import.webp", "Import a statement"),
]

def _feature_rail(prefix: str) -> str:
    items = "".join(
        f'<li{" class=\"is-active\"" if i == 0 else ""}></li>' for i in range(len(FEATURE_PANELS))
    )
    return f'<ol class="alf-story-rail" aria-hidden="true">{items}</ol>'

def _feature_panels_html() -> str:
    out = []
    for i, (title, body, icon, _shot, _alt) in enumerate(FEATURE_PANELS):
        active = " is-active" if i == 0 else ""
        hidden = "false" if i == 0 else "true"
        out.append(
            f'<article class="alf-story-panel{active}" aria-hidden="{hidden}">'
            f'<span class="alf-feature-icon" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 256 256">{icon}</svg></span>'
            f'<div class="alf-editable-shell" data-inline-kind="block"><h3 class="alf-display">{title}</h3></div>'
            f'<div class="alf-editable-shell" data-inline-kind="block"><p>{body}</p></div>'
            f'</article>'
        )
    return "".join(out)

def _feature_device_html(prefix: str) -> str:
    imgs = "".join(
        f'<img src="{prefix}assets/img/{shot}" alt="{alt}"'
        f' class="pc-phone-shot{" is-active" if i == 0 else ""}" loading="lazy"/>'
        for i, (_t, _b, _i, shot, alt) in enumerate(FEATURE_PANELS)
    )
    return (
        '<div class="alf-story-device "><div class="pc-phone" style="height:100%">'
        '<div class="pc-phone-frame"><div class="pc-phone-notch"></div>'
        f'<div class="pc-phone-screen">{imgs}</div></div>'
        '</div></div>'
    )

FEATURE_STORY_SCRIPT = """<script>
(function(){
  var story = document.querySelector('.alf-story');
  var rail = document.querySelectorAll('.alf-story-rail li');
  var panels = document.querySelectorAll('.alf-story-panel');
  var shots = document.querySelectorAll('.alf-story-device .pc-phone-shot');
  if (!story || !panels.length) return;
  var count = panels.length;
  var i = -1;
  function show(n) {
    n = Math.max(0, Math.min(count - 1, n));
    if (n === i) return;
    i = n;
    rail.forEach(function(li, idx){ li.classList.toggle('is-active', idx === i); });
    panels.forEach(function(p, idx){
      p.classList.toggle('is-active', idx === i);
      p.setAttribute('aria-hidden', idx === i ? 'false' : 'true');
    });
    shots.forEach(function(s, idx){ s.classList.toggle('is-active', idx === i); });
  }
  // mirrors .alf-story's own height formula: stage(100vh) + (beats-1)*beat(90vh) + tail(80vh)
  function beatPx(){ return window.innerHeight * 0.9; }
  function onScroll(){
    var rect = story.getBoundingClientRect();
    var into = -rect.top; // px scrolled into the sticky story block
    show(Math.floor(into / beatPx()));
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', onScroll);
  rail.forEach(function(li, idx){
    li.style.cursor = 'pointer';
    li.setAttribute('aria-hidden', 'false');
    li.addEventListener('click', function(){
      var rect = story.getBoundingClientRect();
      var target = window.scrollY + rect.top + idx * beatPx() + 1;
      window.scrollTo({top: target, behavior: 'smooth'});
    });
  });
  show(0);
  onScroll();
})();
</script>"""

def rebuild_feature_story(html: str, prefix: str) -> str:
    if '<div class="alf-story"' not in html:
        return html
    html = html.replace('style="--alf-story-beats:5"', f'style="--alf-story-beats:{len(FEATURE_PANELS)}"')
    html = re.sub(r'<ol class="alf-story-rail"[^>]*>.*?</ol>', _feature_rail(prefix), html, flags=re.DOTALL)
    html = re.sub(r'(<article class="alf-story-panel[^"]*"[^>]*>.*?</article>\s*)+', _feature_panels_html(), html, flags=re.DOTALL)
    html = html.replace('<div class="alf-story-device "></div>', _feature_device_html(prefix))
    html = html.replace("</body>", FEATURE_STORY_SCRIPT + "</body>")
    return html

# v2 experiment: replace the scroll-driven phone-story section with a plain
# static 3-column icon+text grid -- no phone mockup, no screenshot swapping
# on desktop. On mobile only, a phone mockup sits above the (now one-at-a-
# time) cards, its screenshot synced to whichever card is active -- every
# one of the 9 features now has a real screenshot to show there.
ICON_TRANSFER = '<path d="M224,84a8,8,0,0,1-8,8H59.31l26.35,26.34a8,8,0,0,1-11.32,11.32l-40-40a8,8,0,0,1,0-11.32l40-40a8,8,0,0,1,11.32,11.32L59.31,76H216A8,8,0,0,1,224,84Z" opacity="0.2"></path><path d="M228.69,172l-40,40a8,8,0,0,1-11.32-11.32L203.31,180H40a8,8,0,0,1,0-16H203.31l-25.94-25.94a8,8,0,0,1,11.32-11.32l40,40A8,8,0,0,1,228.69,172Z"></path>'
ICON_BARS = '<rect x="32" y="128" width="48" height="96" rx="8" opacity="0.2"></rect><rect x="104" y="80" width="48" height="144" rx="8" opacity="0.2"></rect><rect x="176" y="32" width="48" height="192" rx="8" opacity="0.2"></rect><path d="M224,216a8,8,0,0,1-8,8H40a8,8,0,0,1-8-8V40a8,8,0,0,1,16,0V208H216A8,8,0,0,1,224,216Z"></path><path d="M56,208a8,8,0,0,1-8-8V128a8,8,0,0,1,16,0v72A8,8,0,0,1,56,208Z"></path><path d="M128,208a8,8,0,0,1-8-8V80a8,8,0,0,1,16,0v120A8,8,0,0,1,128,208Z"></path><path d="M200,208a8,8,0,0,1-8-8V32a8,8,0,0,1,16,0v168A8,8,0,0,1,200,208Z"></path>'

FEATURE_GRID_ITEMS = [(title, body, icon, shot, alt) for title, body, icon, shot, alt in FEATURE_PANELS] + [
    ("Move Money Between Accounts", "Transfer between your accounts in a couple of taps, with balances updating instantly.", ICON_TRANSFER, "shot-transfer.webp", "Transfer"),
    ("Spending, Broken Down", "See where your money goes by category, track balance growth over time, and get simple insights on trends.", ICON_BARS, "shot-statistics.webp", "Statistics"),
]

def _feature_grid_html(prefix: str) -> str:
    cards = "".join(
        f'<div class="alf-fgrid-card{" is-active" if i == 0 else ""}"><div class="alf-fgrid-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor">{icon}</svg></div>'
        f'<h3 class="alf-display">{title}</h3><p>{body}</p></div>'
        for i, (title, body, icon, _shot, _alt) in enumerate(FEATURE_GRID_ITEMS)
    )
    shots = "".join(
        f'<img src="{prefix}assets/img/{shot}" alt="{alt}" class="pc-phone-shot{" is-active" if i == 0 else ""}" loading="lazy"/>'
        for i, (_t, _b, _i, shot, alt) in enumerate(FEATURE_GRID_ITEMS)
    )
    phone = (
        '<div class="alf-fgrid-phone"><div class="pc-phone"><div class="pc-phone-frame">'
        f'<div class="pc-phone-notch"></div><div class="pc-phone-screen">{shots}</div>'
        '</div></div></div>'
    )
    return f'{phone}<div class="alf-fgrid">{cards}</div>'

# desktop keeps the full static 3-column grid, untouched, and no phone at
# all; below 760px only the .is-active card is shown at all -- FEATURE_GRID_SCRIPT
# auto-advances which one (same "keep it alive" idea as the hero phone's
# auto-rotation, and solves mobile's very long single-column scroll), and
# the phone above it stays in sync, one screenshot per card
FEATURE_GRID_STYLE = """<style>
.alf-fgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.alf-fgrid-card{background:var(--w-card);border:1px solid var(--w-border);border-radius:16px;padding:28px 24px;display:flex;flex-direction:column;gap:14px}
.alf-fgrid-icon{width:44px;height:44px;border-radius:12px;background:var(--w-accent-soft);display:flex;align-items:center;justify-content:center;color:var(--w-accent)}
.alf-fgrid-icon svg{width:22px;height:22px}
.alf-fgrid-card h3{font-size:1.08rem;font-weight:600;margin:0}
.alf-fgrid-card p{color:var(--w-muted);font-size:.92rem;margin:0;line-height:1.5}
.alf-fgrid-phone{display:none}
@media (max-width:820px){.alf-fgrid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:760px){
  .alf-fgrid{display:block;position:relative;overflow:hidden;min-height:230px}
  .alf-fgrid-card{
    position:absolute;top:0;left:0;right:0;
    transform:translateX(100%);opacity:0;pointer-events:none;
    transition:transform .5s cubic-bezier(.2,.7,.2,1),opacity .5s ease;
  }
  .alf-fgrid-card.is-active{transform:translateX(0);opacity:1;pointer-events:auto}
  .alf-fgrid-card.is-prev{transform:translateX(-100%);opacity:0}
  .alf-fgrid-card.no-anim{transition:none}
  .alf-fgrid-phone{display:flex;justify-content:center;margin-bottom:24px}
  .alf-fgrid-phone .pc-phone-frame{width:min(150px,42vw);height:min(326px,91.6vw);aspect-ratio:auto;box-sizing:content-box;border-radius:25px;padding:2px;box-shadow:0 0 0 1.1px rgba(255,255,255,.14)}
  .alf-fgrid-phone .pc-phone-notch{top:7px;height:9px;border-radius:5px}
  .alf-fgrid-phone .pc-phone-screen{border-radius:24px}
}
@media (prefers-reduced-motion:reduce){.alf-fgrid-card{transition:none}}
</style>"""

FEATURE_GRID_SCRIPT = """<script>
(function(){
  var cards = document.querySelectorAll('.alf-fgrid-card');
  if (!cards.length) return;
  var shots = document.querySelectorAll('.alf-fgrid-phone .pc-phone-shot');
  var mq = window.matchMedia('(max-width:760px)');
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var i = 0;
  var timer = null;
  function show(n){
    var next = (n + cards.length) % cards.length;
    if (next === i) return;
    var prevCard = cards[i];
    var nextCard = cards[next];
    prevCard.classList.remove('is-active');
    prevCard.classList.add('is-prev');
    nextCard.classList.add('is-active');
    shots.forEach(function(s, idx){ s.classList.toggle('is-active', idx === next); });
    i = next;
    setTimeout(function(){
      prevCard.classList.add('no-anim');
      prevCard.classList.remove('is-prev');
      void prevCard.offsetWidth;
      prevCard.classList.remove('no-anim');
    }, 520);
  }
  function start(){
    if (timer || !mq.matches || reduceMotion) return;
    timer = setInterval(function(){ show(i + 1); }, 4500);
  }
  function stop(){
    if (timer) { clearInterval(timer); timer = null; }
  }
  function sync(){ if (mq.matches) { start(); } else { stop(); } }
  if (mq.addEventListener) mq.addEventListener('change', sync); else mq.addListener(sync);
  sync();
})();
</script>"""

def rebuild_feature_grid(html: str, prefix: str) -> str:
    if '<div class="alf-story"' not in html:
        return html
    html = re.sub(r'<div class="alf-story"[^>]*>.*?</div></div></div>', _feature_grid_html(prefix), html, count=1, flags=re.DOTALL)
    html = html.replace("</head>", FEATURE_GRID_STYLE + "</head>")
    html = html.replace("</body>", FEATURE_GRID_SCRIPT + "</body>")
    return html

def transform(html: str, prefix: str, page: str = "", phone_style: str = None) -> str:
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
    # hero's WebGL 3D phone had no static fallback at all -> real CSS phone frame
    # with actual (unbranded) in-app screenshots, switchable via dots + arrows.
    # Keep the original .alf-hero-visual wrapper (its own CSS already handles
    # sizing/mobile collapse) -- only swap what's inside it.
    if '<div class="alf-hero-stage" aria-hidden="true"></div>' in html:
        html = html.replace(
            '<div class="alf-hero-stage" aria-hidden="true"></div><!--$!--><template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING"></template><!--/$-->',
            PHONE_HERO_HTML.format(prefix=prefix),
        )
        html = html.replace("</head>", (phone_style or PHONE_STYLE) + "</head>")
        html = html.replace("</body>", PHONE_SCRIPT + "</body>")
    # story device column: was a WebGL bailout with no static fallback -> emptied
    # here; rebuild_feature_story() (index page only) fills it back in with a
    # real phone frame + real screenshots, one per feature panel
    if 'alf-story-device' in html:
        html = re.sub(
            r'(<div class="alf-story-device ">)<!--\$!--><template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING"></template><!--/\$-->(</div>)',
            r'\1\2',
            html,
        )
    # stop the browser from restoring the previous scroll position on a
    # redeploy/reload -- felt like lag, since the page would flash to top
    # then jump back to wherever the visitor was before the update landed
    html = html.replace("<head>", "<head><script>if('scrollRestoration' in history){history.scrollRestoration='manual';}window.scrollTo(0,0);</script>", 1)
    return html

TRUST_FACTS = """<div class="alf-enter" style="--alf-delay:200ms"><ul style="list-style:none;margin:0 0 26px;padding:0;display:flex;flex-direction:column;gap:10px;max-width:34rem">
<li style="display:flex;gap:10px;align-items:flex-start;font-size:.95rem;color:var(--w-muted)"><span aria-hidden="true" style="color:var(--w-accent);flex:none">&#10003;</span><span><b style="color:var(--w-fg);font-weight:600">No account, ever.</b> Nothing to sign up for, nothing to lose the password to.</span></li>
<li style="display:flex;gap:10px;align-items:flex-start;font-size:.95rem;color:var(--w-muted)"><span aria-hidden="true" style="color:var(--w-accent);flex:none">&#10003;</span><span><b style="color:var(--w-fg);font-weight:600">Nothing leaves your device.</b> No server, no analytics, no third-party SDKs of any kind.</span></li>
<li style="display:flex;gap:10px;align-items:flex-start;font-size:.95rem;color:var(--w-muted)"><span aria-hidden="true" style="color:var(--w-accent);flex:none">&#10003;</span><span><b style="color:var(--w-fg);font-weight:600">You control sync.</b> Optional, and only through your own private iCloud &mdash; we never see it.</span></li>
</ul></div>"""

def trust_first_rework(html: str, prefix: str, use_grid: bool = False) -> str:
    # eyebrow -> lead with the concrete privacy facts, not a generic descriptor
    html = html.replace(
        '<span class="alf-eyebrow alf-enter" style="--alf-delay:0ms">Private finance tracking</span>',
        '<span class="alf-eyebrow alf-enter" style="--alf-delay:0ms">No account &middot; No server &middot; No ads</span>',
    )
    # headline -> plain, literal "what is the app" statement; the privacy
    # claim lives in the smaller lede below it, per explicit request to
    # lead with function, not the trust claim
    html = html.replace(
        '<h1 class="alf-display alf-h1 alf-enter" style="--alf-delay:80ms">Know Where Your Money Goes</h1>',
        '<h1 class="alf-display alf-h1 alf-enter" style="--alf-delay:80ms">A Personal Finance Tracker for iPhone</h1>',
    )
    # lede -> opens on the privacy claim, capability claim follows
    html = html.replace(
        '<p class="alf-lede alf-enter" style="--alf-delay:160ms">Track balances, spending, and income privately on your iPhone, with optional sync through your own iCloud.</p>',
        TRUST_FACTS,
    )
    # feature-section headline -> "Money, Clearly Seen" read as surveillance-y
    html = html.replace(
        '<h2 class="alf-display alf-h2">Money, Clearly Seen</h2>',
        '<h2 class="alf-display alf-h2">Your Complete Financial Picture</h2>',
    )
    # language support -> a real, checkable fact (9 languages, confirmed in
    # the iOS project's own Localizable.xcstrings), mentioned right where a
    # visitor is deciding whether to download
    html = html.replace(
        '<img src="assets/img/app-store-badge.svg" alt="Download on the App Store" draggable="false"/></a></div></div></div><div class="alf-hero-visual',
        '<img src="assets/img/app-store-badge.svg" alt="Download on the App Store" draggable="false"/></a></div>'
        '<p style="margin:14px 0 0;font-size:.85rem;color:var(--w-muted)">Available in English, German, Spanish, French, Italian, Dutch, Portuguese, Russian, and Armenian.</p>'
        '</div></div><div class="alf-hero-visual',
    )
    # feature story rebuilt to the 7 real, concrete features requested, each
    # with its own real screenshot in the shared phone frame -- v2 swaps this
    # for a static icon+text grid (no phone mockup) when use_grid is set
    html = rebuild_feature_grid(html, prefix) if use_grid else rebuild_feature_story(html, prefix)
    # showcase marquee removed along with every other screenshot on the site
    html = re.sub(r'<section id="showcase".*?</section>', '', html, flags=re.DOTALL)
    # CTA closes on the same claim it opened on
    html = html.replace(
        '<h2 class="alf-display alf-h2">Take Control of Your Finances</h2>',
        '<h2 class="alf-display alf-h2">No Account. No Catch.</h2>',
    )
    html = html.replace(
        '<p class="alf-lede">Track your money privately with Prime Capital on iPhone.</p>',
        '<p class="alf-lede">Nothing to sign up for, nothing to hand over &mdash; just download and go.</p>',
    )
    return html

pages = {
    "pc-index.html": (OUT / "index.html", "", ""),
    "pc-privacy.html": (OUT / "privacy" / "index.html", "../", "privacy"),
    "pc-support.html": (OUT / "support" / "index.html", "../", "support"),
    "pc-terms.html": (OUT / "terms" / "index.html", "../", "terms"),
}

# AppLaunchFlow's defaults were the textbook AI-generic cluster: Inter as the
# "safe" font, a lone coral accent (#ff6b72) on near-black, pill (999px)
# buttons everywhere. Fixed by adopting the identity this project already
# established on the privacy/support/terms pages -- real brand consistency,
# not a new arbitrary choice -- and by dropping the Google Fonts request
# entirely in favor of the exact same native font stacks those pages use.
# Switched from dark to a light theme per explicit request ("black looks
# wrong, fishy") -- every --w-* token below is flipped, not just accent,
# since the original dark values (bg/fg/muted/border/band/primary/secondary)
# were baked into the raw AppLaunchFlow source untouched until now. The
# accent moved from platinum (unreadable on white) to near-black -- a
# monochrome black-button-on-white contrast pair, WCAG-verified (17-18:1),
# rather than introducing a new hue.
BRAND_VARS = {
    '--w-font-display:&quot;Inter Variable&quot;, &quot;Inter&quot;, ui-sans-serif, system-ui, -apple-system, &quot;Segoe UI&quot;, sans-serif':
        '--w-font-display:ui-serif, "New York", Georgia, "Times New Roman", serif',
    '--w-font-body:&quot;Inter Variable&quot;, &quot;Inter&quot;, ui-sans-serif, system-ui, -apple-system, &quot;Segoe UI&quot;, sans-serif':
        '--w-font-body:-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif',
    '--w-display-tracking:-0.03em': '--w-display-tracking:-0.01em',
    '--w-display-weight:750': '--w-display-weight:600',
    '--w-radius:20px': '--w-radius:14px',
    '--w-bg:#0a0a0a': '--w-bg:#fbfbfa',
    '--w-fg:#ffffff': '--w-fg:#141414',
    '--w-muted:#b7b7b7': '--w-muted:#6b6b6b',
    '--w-card:#FF6B72': '--w-card:#ffffff',
    '--w-border:rgba(255, 255, 255, 0.14)': '--w-border:rgba(20, 20, 20, 0.12)',
    '--w-band:#1b1b1b': '--w-band:#f0efec',
    '--w-accent:#ff6b72': '--w-accent:#141414',
    '--w-primary:#0a0a0a': '--w-primary:#f3f3f1',
    '--w-primary-fg:#ffffff': '--w-primary-fg:#141414',
    '--w-secondary:#1b1b1b': '--w-secondary:#e8e7e3',
    '--w-secondary-fg:#ffffff': '--w-secondary-fg:#141414',
    '--w-accent-fg:#ffffff': '--w-accent-fg:#ffffff',
    '--w-accent-soft:rgba(255, 107, 114, 0.22)': '--w-accent-soft:rgba(20, 20, 20, 0.06)',
    '--w-accent-glow:rgba(255, 107, 114, 0.45)': '--w-accent-glow:rgba(20, 20, 20, 0.12)',
    '--w-accent-line:rgba(255, 107, 114, 0.55)': '--w-accent-line:rgba(20, 20, 20, 0.35)',
    'color-scheme:dark': 'color-scheme:light',
}

# .alf-btn's 999px pill radius is hardcoded in the vendor CSS, not driven by
# --w-radius -- overridden separately, after the real stylesheets, so it wins.
# Also: body{background:var(--background)} is leftover Next.js boilerplate,
# totally unrelated to .alf-site's own --w-bg theming, which only lives on
# that inner wrapper div -- on mobile, any scroll/bounce past .alf-site's own
# box reveals raw body underneath, so html/body is hardcoded to match --w-bg.
BRAND_STYLE_OVERRIDE = (
    '<style>.alf-btn{border-radius:14px}html,body{background:#fbfbfa}'
    '.alf-cta-panel{background:var(--w-bg)}.alf-cta-panel:before{display:none}'
    '@media (max-width:760px){.alf-hero-glow{display:none}.alf-hero-copy .alf-badges{margin-bottom:28px}}</style>'
)

def apply_brand_identity(html: str) -> str:
    for old, new in BRAND_VARS.items():
        html = html.replace(old, new)
    html = html.replace("</head>", BRAND_STYLE_OVERRIDE + "</head>")
    return html

# v2's phone-sizing fixes (explicit width+height, no aspect-ratio,
# object-fit:contain) and the 9-item feature grid are now confirmed good --
# promoted here to be the real site itself, not a separate experiment.
for src_name, (dest, prefix, page) in pages.items():
    html = (SRC / src_name).read_text()
    is_index = src_name == "pc-index.html"
    html = transform(html, prefix, page, phone_style=PHONE_STYLE_V2 if is_index else None)
    if is_index:
        html = trust_first_rework(html, prefix, use_grid=True)
    html = apply_brand_identity(html)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    print(dest, len(html), "bytes")

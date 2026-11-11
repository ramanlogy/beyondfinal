"""Shared building blocks for the static site generator (no third-party deps)."""
import html, json, math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src")
SITE = "https://www.beyondsummitexped.com"
BRAND = "Beyond Summit Expeditions"
PHONE = "+977 981 115 7421"
PHONE_RAW = "+9779811157421"
WA = "9779811157421"
EMAIL = "info@beyondsummitexped.com"
ADDRESS = "Thamel, Kathmandu 44600, Nepal"
INSTAGRAM = "https://www.instagram.com/beyondsummitexpeditions"
FACEBOOK = "https://www.facebook.com/beyondsummitexped"
YOUTUBE = "https://www.youtube.com/@beyondsummitexpeditions"
CTA = "Plan your trip"

e = lambda s: html.escape(str(s), quote=True)
fmt = lambda n: f"{n:,}"


# ── icons: our own line set (tools/make_icons.py) + brand logos from Phosphor (MIT) ──
_ICONS = {}
def icon(name, cls="i"):
    """Inline an icon from _src/icons. Our own line icons (24 grid, 1.5 stroke, see tools/make_icons.py) keep their
    stroke attributes; the four social/brand logos are filled shapes and keep theirs."""
    if name not in _ICONS:
        svg = open(os.path.join(SRC, "icons", f"{name}.svg")).read()
        m = re.search(r"<svg([^>]*)>(.*)</svg>", svg, re.S)
        attrs = re.sub(r'\s*xmlns="[^"]*"', "", m.group(1))
        _ICONS[name] = (attrs, m.group(2))
    attrs, inner = _ICONS[name]
    extra = " i-arrow" if name == "arrow-right" else ""
    return f'<svg class="{cls}{extra}"{attrs} aria-hidden="true">{inner}</svg>'


# ── photos ────────────────────────────────────────────────────────────────────
CREDITS = json.load(open(os.path.join(SRC, "data/photos_credits.json")))
OWN = json.load(open(os.path.join(SRC, "data/own_photos.json")))
OWN_ALT = {
    "hero": "Our group walking towards snow peaks on the Manaslu Circuit",
    "autumn-valley": "Autumn colours in a high Himalayan valley",
    "dusk-range": "Snow peaks at dusk",
    "forest-trail": "Trekkers on a forest trail beside a tea house",
    "glacier-walk": "Climbers walking up a snow slope under a deep blue sky",
    "high-peaks": "High snow peaks above a valley",
    "larke-pass-group": "Our group at the Larkya La sign, 5,106 m, on the Manaslu Circuit",
    "prayer-flags": "Two trekkers smiling under prayer flags",
    "rope-team": "A roped team resting on a snow summit",
    "snow-group": "A trekking group in the snow at high altitude",
    "summit-climber": "A climber on a snow ridge above the clouds",
    "team-sign": "A trekking group with their guides below snow peaks",
    "valley-walk": "Trekkers on a valley trail towards snow mountains",
    "waterfall-trail": "Two trekkers beside a waterfall on the Manaslu Circuit",
    "yak-meadow": "A yak grazing in an autumn meadow below the Manaslu range",
    "teahouse-group": "Five trekkers with backpacks outside a tea house",
    "golden-peaks": "Morning light on snow peaks above a stone village",
    "gate-group": "Our group under a painted kani gate with prayer flags",
    "snow-village": "Fresh snow on a stone village below the peaks",
    "moraine-walk": "Two trekkers crossing a snow-covered moraine",
    "trail-joy": "A happy trekker on a sunny forest trail",
    "snow-gate": "A snow-covered kani gate on the trail",
    "road-cheer": "Trekkers cheering on a valley trail below forested hills",
    "waterfall-spray": "Trekkers walking through the spray of a tall waterfall",
    "snow-bridge": "A trekker crossing a suspension bridge in the snow",
    "cholatse-lodge": "A trekking lodge below the north face of Cholatse",
    "elwin-mountains": "Elwin Tamang standing above a glacier valley below snow peaks",
    "elwin-guitar": "Elwin Tamang playing guitar outside a tea house",
    "traveller-child": "A smiling traveller with a young child in a mountain village",
    "traveller-local": "A traveller and a local woman in traditional dress",
}

def photo(slug):
    """Return dict(src_base, w, h, alt, credit) for a commons or own photo."""
    if slug in CREDITS:
        c = CREDITS[slug]
        return {"base": c["src"], "w": c["w"], "h": c["h"], "alt": c["alt"], "credit": c}
    o = OWN[slug]
    return {"base": f"/images/web/{slug}", "w": o["w"], "h": o["h"], "alt": OWN_ALT[slug], "credit": None}

def img(slug, sizes="100vw", eager=False, alt=None, cls="", pos=None):
    p = photo(slug)
    seen, parts = set(), []
    for w in (640, 1024, 1600):
        real = min(w, p["w"])
        if real in seen: continue
        seen.add(real); parts.append(f'{p["base"]}-{w}.webp {real}w')
    srcset = ", ".join(parts)
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    style = f' style="object-position:{pos}"' if pos else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{p["base"]}-1024.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{p["w"]}" height="{p["h"]}" alt="{e(alt if alt is not None else p["alt"])}" {load}{style}>')

def credit_line(slug, short=False):
    c = photo(slug)["credit"]
    if not c:
        return "Photo: Beyond Summit group"
    return f'Photo: {e(c["artist"])}, <a href="{e(c["source"])}" rel="noopener" target="_blank">{e(c["license"])}</a>'


# ── page shell ───────────────────────────────────────────────────────────────
NAV = [("Treks", "/trekking.html"), ("Climbing", "/expeditions.html"), ("Activities", "/outdoor.html"),
       ("Gallery", "/gallery.html"), ("Journal", "/blog.html"), ("About", "/about.html")]

# Ama Dablam (6,812 m) from Tengboche: summit, shaded west face, west shoulder and the two 'mother's arms' ridges.
# Strokes are non-scaling so the line weight stays crisp at any size.
LOGO = '<svg class="logo-mark" viewBox="-1.5 -1.5 88 59" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M45.4 0 47.3 2.3 49.6 4.8 51.6 8.5 52.9 13.6 54.2 17.2 56.1 19.6 58.6 24.7 55.9 23.9 53.9 17.8 51.8 16.5 49.7 14.1 44.7 11.9 44.5 6.8 45 1.7Z" fill="currentColor" stroke="none" opacity=".9"/><path d="M0 50.8 2.9 46.6 5.1 43.2 7.2 41.3 8.8 38.1 11.2 34.5 12.6 31.5 13.7 30.8 15.2 25.6 17.8 20.7 19.6 17.9 20.5 19.2 21.8 18 23.4 19.9 25 22.3 26.3 21.9 27.7 24 29.5 24.8 30.9 23.9 32.8 19.9 35 17.9 37.2 13.8 39.6 8.9 41.6 5.1 43.4 2.8 45.4 0 47.3 2.3 49.6 4.8 51.6 8.5 52.9 13.6 54.2 17.2 56.1 19.6 58.6 24.7 60.4 26.7 63.3 28.4 67.4 29.1 71.7 27.7 75 29.7 81.3 31.8 85 29.1" stroke-width="1.6" vector-effect="non-scaling-stroke"/><path d="M3.7 55.7 10.2 49.3 12.8 47.9 20.3 39.3 24 38.3 28.3 47.1 36.7 55.7 M52.7 53.4 58.8 48.8 63.6 44.4 66.8 40.5 76.2 38.1 85 29.1" stroke-width="1.15" vector-effect="non-scaling-stroke"/><path d="M45 1.7 44.5 6.8 44.7 11.9 M19 20.9 19.5 27.4 19.6 34.6 20.7 38.9" stroke-width=".9" vector-effect="non-scaling-stroke" opacity=".6"/></svg>'

def head(title, desc, path, image="/images/web/hero-1600.webp", ld=None, preload=None, noindex=False, og_type="website"):
    url = SITE + path
    lds = "".join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>' for x in (ld or []))
    pre = f'\n<link rel="preload" as="image" href="{preload[0]}" imagesrcset="{preload[1]}" imagesizes="100vw" fetchpriority="high">' if preload else ""
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-image-preview:large'}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f1f3ee">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/geist-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/bricolage-grotesque-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>{pre}
<link rel="stylesheet" href="/css/site.css?v=2">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<script src="https://analytics.ahrefs.com/analytics.js" data-key="di3Rvm0gqVdeUF9iTgLxQQ" async></script>{lds}
</head>"""

def header(active="", photo_hero=False, body_cls=""):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if active == h else ""}>{n}</a>' for n, h in NAV)
    mlinks = "".join(f'<a href="{h}">{n}{icon("arrow-right")}</a>' for n, h in NAV + [("Our team", "/guides.html"), ("Contact", "/contact.html")])
    cls = " ".join(x for x in [("has-photo-hero" if photo_hero else ""), body_cls] if x)
    return f"""<body{f' class="{cls}"' if cls else ''}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header" id="header">
  <div class="wrap header-inner">
    <a href="/" class="brand" aria-label="{BRAND}, home">{LOGO}<span>Beyond Summit<small>Expeditions, Kathmandu</small></span></a>
    <nav class="nav" aria-label="Main">{links}<a href="/contact.html" class="btn btn-primary">{CTA}</a></nav>
    <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu"><span></span></button>
  </div>
</header>
<nav class="mobile-menu" id="mobileMenu" aria-label="Mobile">
  {mlinks}
  <a href="/contact.html" class="btn btn-primary btn-block">{CTA}</a>
  <div class="contact-mini"><a href="tel:{PHONE_RAW}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><span>{ADDRESS}</span></div>
</nav>
"""

FOOT_TREKS = [("Everest Base Camp", "/articles/everest-blog-new.html"), ("Annapurna Base Camp", "/articles/annapurna-blog.html"),
              ("Annapurna Circuit", "/articles/annapurna-circuit.html"), ("Manaslu Circuit", "/articles/manaslu-blog.html"),
              ("Upper Mustang", "/articles/upper-mustang-blog.html"), ("Langtang Valley", "/articles/langtang-valley.html")]
FOOT_CLIMBS = [("Island Peak", "/articles/islandpeak.html"), ("Mera Peak", "/articles/merapeak.html"), ("Lobuche East", "/articles/lobuche.html"),
               ("Ama Dablam", "/articles/amadablam-blog.html"), ("Himlung Himal", "/articles/himlung.html"), ("8,000 m expeditions", "/expeditions.html#eight-thousanders")]
FOOT_PLAN = [("Trekking permits 2026", "/articles/nepal-trekking-permits.html"), ("Best time to trek", "/articles/best-time-to-trek-nepal.html"),
             ("Activities", "/outdoor.html"), ("Journal", "/blog.html")]
FOOT_CO = [("About us", "/about.html"), ("Our team", "/guides.html"), ("Photo gallery", "/gallery.html"), ("Contact", "/contact.html"), ("Photo credits", "/photo-credits.html")]

def footer(extra=""):
    col = lambda t, items: f'<div><h4>{t}</h4><ul>' + "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in items) + '</ul></div>'
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a href="/" class="brand" aria-label="{BRAND}, home">{LOGO}<span>Beyond Summit<small>Expeditions, Kathmandu</small></span></a>
        <p class="footer-about">A trekking and mountaineering company in Thamel, Kathmandu, licensed by the Department of Tourism, Government of Nepal.</p>
        <p class="footer-about"><a href="tel:{PHONE_RAW}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
      {col("Treks", FOOT_TREKS)}{col("Climbing", FOOT_CLIMBS)}{col("Plan", FOOT_PLAN)}{col("Company", FOOT_CO)}
    </div>
    <div class="footer-accred"><p>Licensed and registered in Nepal</p>{accred_row("mini")}</div>
    <div class="footer-bottom">
      <p>&copy; 2026 {BRAND}</p>
      <button class="theme-toggle" type="button" data-theme-toggle>{icon("sun")}<span>Dark mode</span></button>
      <div class="socials">
        <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram">{icon("instagram-logo")}</a>
        <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook">{icon("facebook-logo")}</a>
        <a href="{YOUTUBE}" target="_blank" rel="noopener" aria-label="YouTube">{icon("youtube-logo")}</a>
      </div>
    </div>
  </div>
</footer>
<a href="https://wa.me/{WA}" class="wa-float" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{icon("whatsapp-logo")}</a>
{extra}<script src="/js/site.js?v=2" defer></script>
</body>
</html>
"""

def crumbs(items):
    lis = "".join((f'<li><a href="{h}">{e(n)}</a></li>' if h else f'<li aria-current="page">{e(n)}</li>') for n, h in items)
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{lis}</ol></nav>'

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": SITE + h} if h else {})} for i, (n, h) in enumerate(items)]}

# Licences and memberships confirmed by the owner (2026-11-11).
# Add licence / membership numbers in "no" when available; they are shown under each badge.
ACCRED = [
    {"key": "dot", "logo": None, "short": "Department of Tourism", "name": "Department of Tourism, Government of Nepal",
     "role": "Licensed trekking and mountaineering agency", "url": "https://tourismdepartment.gov.np/", "no": ""},
    {"key": "ntb", "logo": "/images/logos/ntb", "short": "Nepal Tourism Board", "name": "Nepal Tourism Board",
     "role": "Registered with Nepal's national tourism body", "url": "https://ntb.gov.np/", "no": ""},
    {"key": "taan", "logo": "/images/logos/taan", "short": "TAAN", "name": "Trekking Agencies' Association of Nepal",
     "role": "Member of the national trekking association", "url": "https://www.taan.org.np/", "no": ""},
    {"key": "nma", "logo": "/images/logos/nma", "short": "NMA", "name": "Nepal Mountaineering Association",
     "role": "Member agency for peak climbing", "url": "https://www.nepalmountaineering.org/", "no": ""},
]
LOGO_SIZE = {"ntb": (189, 192), "taan": (140, 192), "nma": (220, 192)}

def accred_mark(a, h=48):
    if a["logo"]:
        w, hh = LOGO_SIZE[a["key"]]
        return (f'<picture><source srcset="{a["logo"]}.webp" type="image/webp">'
                f'<img src="{a["logo"]}.png" alt="{e(a["name"])} logo" width="{round(w * h / hh)}" height="{h}" loading="lazy" decoding="async"></picture>')
    return f'<span class="accred-text" aria-hidden="true">{icon("certificate")}<b>Govt. of<br>Nepal</b></span>'

def accred_row(variant="full"):
    """variant: full (home/about cards), mini (footer, trip aside)."""
    if variant == "mini":
        items = "".join(f'<a class="accred-mini" href="{a["url"]}" target="_blank" rel="noopener" title="{e(a["name"])}: {e(a["role"])}">{accred_mark(a, 34)}<span class="sr-only">{e(a["name"])}</span></a>' for a in ACCRED)
        return f'<div class="accred-minis">{items}</div>'
    cards = []
    for a in ACCRED:
        no = f'<small class="num">No. {e(a["no"])}</small>' if a["no"] else ""
        cards.append(f'<a class="accred-card reveal" href="{a["url"]}" target="_blank" rel="noopener"><span class="accred-logo">{accred_mark(a)}</span>'
                     f'<span class="accred-body"><strong>{e(a["name"])}</strong><span>{e(a["role"])}</span>{no}</span></a>')
    return f'<div class="accred">{"".join(cards)}</div>'

ORG_LD = {
    "@context": "https://schema.org", "@type": "TravelAgency", "@id": SITE + "/#organization",
    "name": BRAND, "url": SITE + "/", "logo": SITE + "/favicon.svg", "image": SITE + "/images/web/hero-1600.webp",
    "description": "Small-group trekking and mountaineering company in Thamel, Kathmandu, licensed by the Department of Tourism, Government of Nepal.",
    "telephone": PHONE_RAW, "email": EMAIL, "priceRange": "$$",
    "address": {"@type": "PostalAddress", "streetAddress": "Thamel", "addressLocality": "Kathmandu", "postalCode": "44600", "addressCountry": "NP"},
    "areaServed": {"@type": "Country", "name": "Nepal"},
    "sameAs": [INSTAGRAM, FACEBOOK, YOUTUBE],
    "founder": {"@type": "Person", "name": "Elwin Tamang"},
    "memberOf": [
        {"@type": "Organization", "name": "Trekking Agencies' Association of Nepal", "alternateName": "TAAN", "url": "https://www.taan.org.np/"},
        {"@type": "Organization", "name": "Nepal Mountaineering Association", "alternateName": "NMA", "url": "https://www.nepalmountaineering.org/"},
    ],
}

def grade(n, label, total=5):
    bars = "".join(f'<b class="{"on" if i < n else ""}"></b>' for i in range(total))
    return f'<span class="grade" title="Grade {n} of {total}"><i>{bars}</i>{e(label)}</span>'

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def months_strip(season):
    cells = "".join(f'<div class="month {"best" if i+1 in season["best"] else "good" if i+1 in season.get("good", []) else ""}" title="{MONTHS_FULL[i]}">{m}</div>' for i, m in enumerate(MONTHS))
    key = ('<div class="months-key"><span><i style="background:var(--accent)"></i>Best</span>'
           '<span><i style="background:var(--accent-soft)"></i>Good</span><span><i style="background:var(--surface-2)"></i>Possible, but not ideal</span></div>')
    return f'<div class="months" role="img" aria-label="Best months: {", ".join(MONTHS_FULL[m-1] for m in season["best"])}">{cells}</div>{key}'

def best_months_text(season):
    b = sorted(season["best"])
    groups, cur = [], [b[0]]
    for m in b[1:]:
        if m == cur[-1] + 1: cur.append(m)
        else: groups.append(cur); cur = [m]
    groups.append(cur)
    return ", ".join(MONTHS[g[0]-1] if len(g) == 1 else f"{MONTHS[g[0]-1]} to {MONTHS[g[-1]-1]}" for g in groups)


# ── geography: places, projection, line maps, profile ────────────────────────
def load_places():
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("places", os.path.join(SRC, "data/places.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    osm = json.load(open(os.path.join(SRC, "data/coords_osm.json")))
    km = lambda a, b, c, d: math.hypot((a - c) * 111, (b - d) * 111 * math.cos(math.radians(a)))
    out, src = {}, {}
    for k, (name, alt, la, lo, variants, reg) in m.PLACES.items():
        best = None
        for o in osm:
            if variants and (o[1] in variants or o[2] in variants):
                d = km(la, lo, o[3], o[4])
                if d <= 11 and (best is None or d < best[0]): best = (d, o)
        if best: la, lo = best[1][3], best[1][4]; src[k] = "osm"
        else: src[k] = "approx"
        out[k] = {"name": name, "alt": alt, "lat": la, "lon": lon_fix(lo), "key": k}
    return out, src

def lon_fix(x): return x

REF_PEAKS = [
    ("Everest", 8849, 27.9881, 86.9250), ("Lhotse", 8516, 27.9617, 86.9333), ("Nuptse", 7861, 27.9672, 86.8864),
    ("Ama Dablam", 6812, 27.8611, 86.8611), ("Makalu", 8485, 27.8897, 87.0889), ("Cho Oyu", 8188, 28.0942, 86.6608),
    ("Thamserku", 6623, 27.7856, 86.7883), ("Kangtega", 6782, 27.7978, 86.8133), ("Pumori", 7161, 28.0150, 86.8281),
    ("Annapurna I", 8091, 28.5961, 83.8203), ("Annapurna South", 7219, 28.5180, 83.8070), ("Machapuchare", 6993, 28.4950, 83.9492),
    ("Hiunchuli", 6441, 28.5150, 83.8500), ("Dhaulagiri", 8167, 28.6967, 83.4875), ("Annapurna II", 7937, 28.5397, 84.1217),
    ("Gangapurna", 7455, 28.6067, 83.9650), ("Tilicho Peak", 7134, 28.6820, 83.8080), ("Nilgiri", 7061, 28.6900, 83.7130),
    ("Manaslu", 8163, 28.5497, 84.5597), ("Himlung", 7126, 28.7723, 84.4218), ("Ganesh Himal", 7422, 28.3910, 85.1270),
    ("Langtang Lirung", 7227, 28.2561, 85.5194), ("Dorje Lakpa", 6966, 28.1740, 85.7850), ("Chamlang", 7319, 27.7750, 86.9800),
    ("Mera Peak", 6476, 27.7098, 86.8687), ("Kangchenjunga", 8586, 27.7025, 88.1475),
]

class Proj:
    def __init__(self, pts, W, H, pad, min_km=0):
        lat0 = sum(p["lat"] for p in pts) / len(pts)
        self.k = math.cos(math.radians(lat0))
        xs = [p["lon"] * self.k for p in pts]; ys = [p["lat"] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        m = min_km / 111.0
        if x1 - x0 < m: c = (x0 + x1) / 2; x0, x1 = c - m / 2, c + m / 2
        if y1 - y0 < m: c = (y0 + y1) / 2; y0, y1 = c - m / 2, c + m / 2
        self.s = min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0))
        self.ox = (W - (x1 - x0) * self.s) / 2 - x0 * self.s
        self.oy = (H - (y1 - y0) * self.s) / 2 + y1 * self.s
        self.W, self.H = W, H
    def __call__(self, p):
        return (round(p["lon"] * self.k * self.s + self.ox, 1), round(self.oy - p["lat"] * self.s, 1))
    def km_px(self): return self.s / 111.0

def dedupe(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x: out.append(x)
    return out

def path_d(points):
    return "M" + " L".join(f"{x},{y}" for x, y in points)

def _seg_hits_box(x1, y1, x2, y2, bx, by, bw, bh):
    """Liang-Barsky: does the segment cross the rectangle?"""
    t0, t1, dx, dy = 0.0, 1.0, x2 - x1, y2 - y1
    for p, q in ((-dx, x1 - bx), (dx, bx + bw - x1), (-dy, y1 - by), (dy, by + bh - y1)):
        if p == 0:
            if q < 0: return False
        else:
            t = q / p
            if p < 0: t0 = max(t0, t)
            else: t1 = min(t1, t)
            if t0 > t1: return False
    return True

def place_labels(cands, W, H, fs=11, pad=3, lines=()):
    """Label placement. cands: list of (priority, x, y, text, cls); lines: [(points, weight)] route lines to keep clear of.
    Labels never overlap each other or a stop dot. Among the clear spots the one crossing the least route line wins
    (the day's own route weighs more than the faint context line). Highest priority is placed first; the start/finish
    and high point may shrink a little to fit, other labels that cannot be placed cleanly are dropped."""
    r = 6  # keep-out radius around every stop dot
    boxes = [(x - r, y - r, 2 * r, 2 * r) for _, x, y, _, _ in cands]
    segs = [(p[i][0], p[i][1], p[i + 1][0], p[i + 1][1], wt) for p, wt in lines for i in range(len(p) - 1)]
    out = []
    for pr, x, y, t, cls in sorted(cands, key=lambda c: c[0]):
        bold = "strong" in cls
        own = (x - r, y - r, 2 * r, 2 * r)
        for k in ((1, .86, .74) if pr <= 1 else (1,)):
            f = fs * k
            w, h = len(t) * f * (.6 if bold else .56) + 4, f * 1.2
            g = f * .35
            spots = ((r + g, f * .35, "start"), (-r - g, f * .35, "end"),
                     (0, -r - g, "middle"), (0, r + g + f * .85, "middle"),
                     (r * .7, -r - g * .4, "start"), (-r * .7, -r - g * .4, "end"),
                     (r * .7, r + g + f * .8, "start"), (-r * .7, r + g + f * .8, "end"))
            best = None
            for n, (dx, dy, anchor) in enumerate(spots):
                bx = x + dx if anchor == "start" else x + dx - w if anchor == "end" else x - w / 2
                by = y + dy - h * .8
                if bx < pad or bx + w > W - pad or by < pad or by + h > H - pad: continue
                if any(bb != own and not (bx + w < a or bx > a + aw or by + h < b or by > b + bh)
                       for bb in boxes for a, b, aw, bh in (bb,)): continue
                cost = n * .1 + sum(wt for x1, y1, x2, y2, wt in segs
                                    if _seg_hits_box(x1, y1, x2, y2, bx + 1, by + 1, w - 2, h - 2))
                if best is None or cost < best[0]: best = (cost, dx, dy, anchor, bx, by)
                if cost < 1: break
            # crossing the faint context line is fine; only shrink to keep clear of the day's own route
            if best and (best[0] < 10 or k == (.74 if pr <= 1 else 1)):
                _, dx, dy, anchor, bx, by = best
                boxes.append((bx, by, w, h))
                size = "" if k == 1 else f' style="font-size:{f:.1f}px"'
                out.append(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" class="{cls}"{size}>{e(t)}</text>')
                break
    return out

def scale_bar(proj, W, H):
    kmpx = proj.km_px()
    for km in (1, 2, 5, 10, 20, 50):
        if km * kmpx >= 40: break
    L = km * kmpx
    x0, y0 = 10, H - 10
    return (f'<g class="map-scale"><path d="M{x0},{y0-4} V{y0} H{x0+L:.1f} V{y0-4}" fill="none" stroke="currentColor" stroke-width="1" style="stroke:var(--ink-3)"/>'
            f'<text x="{x0 + L + 5:.1f}" y="{y0}" class="map-scale" style="paint-order:normal;stroke:none">{km} km</text></g>')

def route_points(trip, P):
    """Ordered list of segments per day: [(day_index, [place keys])]."""
    segs = []
    for i, d in enumerate(trip["days"]):
        r = dedupe(d["r"])
        segs.append((i, r))
    return segs

def overview_map(trip, P, W=640, H=420, live=False):
    segs = route_points(trip, P)
    keys = list(dict.fromkeys(k for _, r in segs for k in r))
    pts = [P[k] for k in keys]
    if len(pts) < 2: return ""
    la0, la1 = min(p["lat"] for p in pts), max(p["lat"] for p in pts)
    lo0, lo1 = min(p["lon"] for p in pts), max(p["lon"] for p in pts)
    m = .07
    named = {P[k]["name"].replace(" summit", "") for k in keys}
    refs = [r for r in REF_PEAKS if la0 - m <= r[2] <= la1 + m and lo0 - m <= r[3] <= lo1 + m and r[0] not in named]
    proj = Proj(pts + [{"lat": r[2], "lon": r[3]} for r in refs], W, H, 34, min_km=6)
    full = []
    for _, r in segs:
        for k in r: full.append(k)
    full_xy = [proj(P[k]) for k in dedupe(full)]
    parts = []
    for name, alt, la, lo in refs:
        x, y = proj({"lat": la, "lon": lo})
        parts.append(f'<path class="peak-ref" d="M{x},{y-6} l5.5,9 h-11z"><title>{e(name)}, {fmt(alt)} m</title></path>')
    parts.append(f'<path class="track" d="{path_d(full_xy)}"/>')
    for i, r in segs:
        if len(r) >= 2:
            parts.append(f'<path class="seg" data-i="{i}" d="{path_d([proj(P[k]) for k in r])}"/>')
    sleeps = {}
    for i, d in enumerate(trip["days"]):
        if d.get("sleep") and d["sleep"] in keys: sleeps.setdefault(d["sleep"], i)
    hi_keys = {d.get("hi") for d in trip["days"] if d.get("hi")}
    top = max(keys, key=lambda k: P[k]["alt"])
    cands = []
    for k in keys:
        x, y = proj(P[k])
        is_peak = k in hi_keys or k == top
        cls = "stop peak" if is_peak else "stop"
        di = f' data-i="{sleeps[k]}"' if k in sleeps else ""
        parts.append(f'<circle class="{cls}"{di} cx="{x}" cy="{y}" r="{5 if is_peak else 4}"><title>{e(P[k]["name"])}, {fmt(P[k]["alt"])} m</title></circle>')
        pr = 0 if k == top else 1 if k in (keys[0],) else 2 if is_peak else 3 if k in sleeps else 4
        txt = P[k]["name"] + (f' {fmt(P[k]["alt"])} m' if k == top else "")
        cands.append((pr, x, y, txt, "strong" if pr <= 1 else ""))
    for name, alt, la, lo in refs:
        x, y = proj({"lat": la, "lon": lo})
        cands.append((5, x, y + 2, name, "peak-name"))
    parts += place_labels(cands, W, H, lines=[(full_xy, 10)])
    parts.append(scale_bar(proj, W, H))
    parts.append(f'<text x="{W-14}" y="22" class="north" text-anchor="middle" style="paint-order:normal;stroke:none">N</text><path d="M{W-14},26 l-4,10 h8z" style="fill:var(--ink-3)"/>')
    cls = "map map-big" if live else "map"
    return f'<div class="{cls}"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Route map of the {e(trip["name"])}">{"".join(parts)}</svg></div>'

def day_map(trip, P, i, W=240, H=170):
    d = trip["days"][i]
    r = dedupe(d["r"])
    if not r: return ""
    all_keys = dedupe([k for dd in trip["days"] for k in dd["r"]])
    focus = [P[k] for k in r]
    proj = Proj(focus, W, H, 30, min_km=4 if len(r) > 1 else 6)
    ctx = [proj(P[k]) for k in all_keys]
    parts = [f'<path class="track" d="{path_d(ctx)}" style="opacity:.3"/>'] if len(ctx) > 1 else []
    xy = [proj(P[k]) for k in r]
    if len(xy) > 1: parts.append(f'<path class="track-day" d="{path_d(xy)}"/>')
    hi = d.get("hi")
    cands = []
    seen = set()
    for j, k in enumerate(r):
        if k in seen: continue
        seen.add(k)
        x, y = proj(P[k])
        last = k == r[-1] or k == d.get("sleep")
        first = j == 0
        cls = "stop peak" if k == hi else ("stop on" if last else "stop")
        parts.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{5 if (k == hi or last) else 4}"/>')
        pr = 0 if last else 1 if k == hi else 2 if first else 3
        cands.append((pr, x, y, P[k]["name"].replace(" summit", ""), "strong" if pr <= 1 else ""))
    lines = [(ctx, 1)] + ([(xy, 10)] if len(xy) > 1 else [])
    parts += place_labels(cands, W, H, fs=14, lines=lines)  # matches .day-map text { font-size: 14px }
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Map of day {e(d["n"])}: {e(" to ".join(P[k]["name"] for k in dedupe(r)))}">{"".join(parts)}</svg>'

def day_high(d, P):
    """Highest point of the day, only if it is above both the start and the overnight stop."""
    if not d["r"]: return None
    hp = P[d["hi"]] if d.get("hi") else max((P[k] for k in d["r"]), key=lambda p: p["alt"])
    ref = [P[d["r"][0]]["alt"]] + ([P[d["sleep"]]["alt"]] if d.get("sleep") in P else [])
    return hp if hp["alt"] > max(ref) + 80 else None

def profile(trip, P, W=640, H=220):
    rows = []
    for i, d in enumerate(trip["days"]):
        s = d.get("sleep")
        if not s: continue
        sp = P[s] if s in P else None
        if not sp: continue
        hp = day_high(d, P)
        rows.append((i, d, sp, hp if hp and hp["alt"] > sp["alt"] + 80 else None))
    if len(rows) < 2: return ""
    pl, pr, pt, pb = 44, 12, 24, 26
    amax = max(max(r[2]["alt"], r[3]["alt"] if r[3] else 0) for r in rows)
    top = math.ceil((amax + 200) / 1000) * 1000
    bot = 0
    X = lambda j: pl + j * (W - pl - pr) / (len(rows) - 1)
    Y = lambda a: pt + (top - a) * (H - pt - pb) / (top - bot)
    g = []
    for a in range(bot, top + 1, 1000 if top <= 7000 else 2000):
        g.append(f'<line class="grid" x1="{pl}" x2="{W-pr}" y1="{Y(a):.1f}" y2="{Y(a):.1f}"/><text class="axis" x="{pl-6}" y="{Y(a)+3.5:.1f}" text-anchor="end">{fmt(a)}</text>')
    line = [(X(j), Y(r[2]["alt"])) for j, r in enumerate(rows)]
    area = f'M{pl},{Y(bot):.1f} ' + " ".join(f"L{x:.1f},{y:.1f}" for x, y in line) + f' L{X(len(rows)-1):.1f},{Y(bot):.1f} Z'
    g.append(f'<path class="area" d="{area}"/><path class="line" d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in line) + '"/>')
    step = 1 if len(rows) <= 14 else 2
    hits, best = [], max(rows, key=lambda r: (r[3] or r[2])["alt"])
    colw = (W - pl - pr) / max(1, len(rows) - 1)
    g.append(f'<line class="cursor" x1="0" x2="0" y1="{pt}" y2="{H-pb}"/>')
    for j, (i, d, sp, hp) in enumerate(rows):
        x, y = X(j), Y(sp["alt"])
        if hp:
            yh = Y(hp["alt"])
            g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{yh:.1f}" y2="{y:.1f}" style="stroke:var(--ink-3);stroke-width:1;stroke-dasharray:2 2"/><circle class="hi" cx="{x:.1f}" cy="{yh:.1f}" r="4"/>')
        g.append(f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="4"/>')
        if j % step == 0 or j == len(rows) - 1:
            g.append(f'<text class="axis" x="{x:.1f}" y="{H-8}" text-anchor="middle">{e(d["n"].split("-")[0])}</text>')
        tip = f'<b>Day {e(d["n"])}</b><br>Sleep: {e(sp["name"])}, {fmt(sp["alt"])} m' + (f'<br>High point: {e(hp["name"])}, {fmt(hp["alt"])} m' if hp else "")
        ty = Y(hp["alt"]) if hp else y
        hits.append(f'<rect class="hit" x="{x-colw/2:.1f}" y="{pt}" width="{colw:.1f}" height="{H-pt-pb}" data-x="{x:.1f}" data-y="{ty:.1f}" data-day="{e(d["n"])}" data-tip="{e(tip)}" tabindex="0" role="button" aria-label="Day {e(d["n"])}: sleep at {e(sp["name"])}, {fmt(sp["alt"])} m"/>')
    bp = best[3] or best[2]
    bj = rows.index(best)
    lx, ly = X(bj), Y(bp["alt"]) - 9
    anchor = "end" if bj > len(rows) * .6 else "start" if bj < len(rows) * .25 else "middle"
    g.append(f'<text class="lbl" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">{e(bp["name"].replace(" summit", ""))} {fmt(bp["alt"])} m</text>')
    g.append(f'<text class="axis" x="{pl}" y="{pt-10}">metres</text><text class="axis" x="{W-pr}" y="{H-8}" text-anchor="end" style="display:none">day</text>')
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Altitude profile: overnight altitude each day, highest {fmt(bp["alt"])} m at {e(bp["name"])}">{"".join(g)}{"".join(hits)}</svg>'
    table = "".join(f'<tr><td>Day {e(d["n"])}</td><td>{e(sp["name"])}</td><td>{fmt(sp["alt"])} m</td><td>{(e(hp["name"]) + ", " + fmt(hp["alt"]) + " m") if hp else ""}</td></tr>' for i, d, sp, hp in rows)
    return (f'<div class="profile profile-wrap">{svg}<div class="tip" role="status"></div></div>'
            '<div class="legend-inline"><span><i style="background:var(--accent)"></i>Where you sleep</span>'
            '<span><i style="border:1.5px solid var(--ink);background:var(--surface)"></i>Highest point that day</span><span>Days along the bottom. Hover or tap for details.</span></div>'
            f'<details class="note"><summary>Show as a table</summary><div class="table-wrap"><table><thead><tr><th>Day</th><th>Overnight</th><th>Altitude</th><th>High point</th></tr></thead><tbody>{table}</tbody></table></div></details>')

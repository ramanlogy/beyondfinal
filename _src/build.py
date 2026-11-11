"""Build every page of the site from _src/data. Run: python3 _src/build.py"""
import importlib.util, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

spec = importlib.util.spec_from_file_location("trips", os.path.join(SRC, "data/trips.py"))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
TRIPS, EIGHT = T.TRIPS, T.EIGHT_THOUSANDERS
P, PSRC = load_places()
BYSLUG = {t["slug"]: t for t in TRIPS}
url = lambda t: "/" + t["file"]
WRITTEN = []

def write(path, html_):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html_)
    WRITTEN.append(path)

def preload_for(slug):
    p = photo(slug)
    return (f'{p["base"]}-1024.webp', f'{p["base"]}-640.webp 640w, {p["base"]}-1024.webp 1024w, {p["base"]}-1600.webp {p["w"]}w')

def trip_card(t, cls="card reveal", sizes="(max-width: 640px) 100vw, (max-width: 1099px) 50vw, 400px"):
    tags = t["tags"] + (" trek" if t["kind"] == "trek" else " climb") + (" short" if t["days_n"] <= 12 else "")
    return f"""<a href="{url(t)}" class="{cls}" data-tags="{e(tags)}">
  <div class="ph">{img(t["card"], sizes)}</div>
  <div class="card-body">
    <p class="card-region">{e(t["region"])}</p>
    <h3>{e(t["short"])}</h3>
    <p class="card-text">{e(t["blurb"])}</p>
    <div class="card-facts">
      <span class="chip">{icon("calendar-blank")}{t["days_n"]} days</span>
      <span class="chip">{icon("mountains")}{fmt(t["max_alt"])} m</span>
      <span class="chip">{grade(t["grade"], t["grade_txt"])}</span>
    </div>
    <div class="card-foot"><p class="price"><small>From</small><strong>US${fmt(t["price"])}</strong></p><span class="link">View itinerary {icon("arrow-right")}</span></div>
  </div>
</a>"""

def cta_band(title="Let's plan your trip", text="Tell us when you'd like to travel, who's coming and what you have in mind. Elwin will write back within a working day with a suggested plan and a clear price.", photo_slug="valley-walk", trip=None):
    q = f"?trip={trip}" if trip else ""
    return f"""<section class="section-sm"><div class="wrap"><div class="cta reveal">
  {img(photo_slug, "100vw", alt="")}
  <div><h2>{e(title)}</h2><p>{e(text)}</p></div>
  <div class="cta-actions">
    <a href="/contact.html{q}" class="btn btn-light">{CTA} {icon("arrow-right")}</a>
    <a href="https://wa.me/{WA}" class="btn btn-onphoto" target="_blank" rel="noopener">{icon("whatsapp-logo")} WhatsApp us</a>
    <div class="cta-lines"><a href="tel:{PHONE_RAW}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </div>
</div></div></section>"""

# ═════════════════════════════════════════════════════════════════ TRIP PAGE
def trip_page(t):
    path = url(t)
    is_trek = t["kind"] == "trek"
    section_name, section_url = ("Treks", "/trekking.html") if is_trek else ("Climbing", "/expeditions.html")
    bc = [("Home", "/"), (section_name, section_url), (t["short"], None)]
    incl = T.TREK_INCLUDED if is_trek else T.CLIMB_INCLUDED
    excl = T.TREK_EXCLUDED if is_trek else T.CLIMB_EXCLUDED
    hero = photo(t["hero"])
    wa_text = f"Hello, I'm interested in the {t['name']} ({t['days_n']} days)."

    # Day cards
    days_html = []
    for i, d in enumerate(t["days"]):
        stats = []
        if d.get("km"): stats.append(f'<span class="chip">{icon("path")}about {d["km"]} km</span>')
        if d.get("h"): stats.append(f'<span class="chip">{icon("clock")}{e(d["h"])}</span>')
        hp = day_high(d, P)
        if hp:
            stats.append(f'<span class="chip">{icon("trend-up")}High point {fmt(hp["alt"])} m</span>')
        if d.get("sleep") and d["sleep"] in P:
            stats.append(f'<span class="chip">{icon("bed")}Sleep {fmt(P[d["sleep"]]["alt"])} m</span>')
        stay = []
        if d.get("stay"): stay.append(f'<span>{icon("bed")}{e(d["stay"])}</span>')
        if d.get("meals"): stay.append(f'<span>{icon("bowl-food")}Meals: {e(d["meals"])}</span>')
        badge = f'<span class="badge">{e(d["tag"])}</span>' if d.get("tag") else ""
        dm = day_map(t, P, i)
        label = f'Day {d["n"]}: {d["t"]}'
        days_html.append(f"""<li class="day" id="day-{e(d['n'])}" data-day="{i}" data-label="{e(label)}">
  <div class="day-no" aria-hidden="true"><small>Day</small><b>{e(d["n"])}</b></div>
  <article class="day-card"{' style="grid-template-columns:1fr"' if not dm else ''}>
    <div class="day-body">
      <h3><span class="sr-only">Day {e(d["n"])}: </span>{e(d["t"])}{badge}</h3>
      <div class="day-stats">{"".join(stats)}</div>
      <p>{e(d["x"])}</p>
      {f'<div class="day-stay">{"".join(stay)}</div>' if stay else ''}
    </div>
    {f'<div class="day-map map">{dm}</div>' if dm else ''}
  </article>
</li>""")

    gallery = "".join(f'<figure>{img(g, "(max-width: 860px) 50vw, 33vw")}<figcaption>{e(photo(g)["alt"])}</figcaption></figure>' for g in t["gallery"][:5])
    gallery_credits = "; ".join(f'{e(photo(g)["alt"].split(",")[0])}: {credit_line(g)}' for g in t["gallery"][:5] if photo(g)["credit"])
    faq = "".join(f'<details><summary>{e(q)}{icon("plus")}</summary><div><p>{e(a)}</p></div></details>' for q, a in t["faq"])
    permits = "".join(f'<li><strong>{e(n)}</strong><br>{e(v)}</li>' for n, v in t["permits"])
    related = [x for x in TRIPS if x["slug"] != t["slug"] and (set(x["tags"].split()) & set(t["tags"].split()))][:3]
    if len(related) < 3: related += [x for x in TRIPS if x not in related and x["slug"] != t["slug"]][:3 - len(related)]
    route_note = "Route lines join overnight stops and viewpoints in walking order. They are a guide to the shape of the route, not a navigation track."

    ld_trip = {
        "@context": "https://schema.org", "@type": "TouristTrip", "name": t["name"], "description": t["seo_desc"],
        "url": SITE + path, "image": SITE + hero["base"] + "-1600.webp",
        "touristType": "Trekkers" if is_trek else "Mountaineers",
        "provider": {"@id": SITE + "/#organization"},
        "itinerary": {"@type": "ItemList", "numberOfItems": len(t["days"]), "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": {"@type": "TouristAttraction", "name": f'Day {d["n"]}: {d["t"]}', "description": d["x"]}}
            for i, d in enumerate(t["days"])]},
        "offers": {"@type": "Offer", "price": t["price"], "priceCurrency": "USD", "availability": "https://schema.org/InStock",
                   "url": SITE + path, "seller": {"@id": SITE + "/#organization"}},
    }
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}

    summary_dl = [
        ("calendar-blank", "Duration", f'{t["days_n"]} days'),
        ("mountains", "Max altitude", f'{fmt(t["max_alt"])} m'),
        ("trend-up", "Grade", t["grade_txt"]),
        ("users-three", "Group size", t["group"]),
        ("map-pin", "Starts", t["start"]),
        ("sun", "Best months", best_months_text(t["season"])),
    ]
    dl = "".join(f'<div><dt>{icon(i)}{e(k)}</dt><dd>{e(v)}</dd></div>' for i, k, v in summary_dl)

    html_ = head(t["seo_title"], t["seo_desc"], path, image=hero["base"] + "-1600.webp",
                 ld=[ORG_LD, crumbs_ld(bc), ld_trip, ld_faq], preload=preload_for(t["hero"]))
    html_ += header(section_url, photo_hero=True, body_cls="is-trip")
    html_ += f"""<main id="main">
<section class="photo-hero trip-hero on-photo" aria-labelledby="trip-title">
  <picture>{img(t["hero"], "100vw", eager=True)}</picture>
  <div class="wrap hero-in">
    {crumbs(bc)}
    <h1 id="trip-title">{e(t["name"])}</h1>
    <p class="lede">{e(t["tagline"])}</p>
    <div class="facts-bar">
      <div><span>Duration</span><strong>{t["days_n"]} days</strong></div>
      <div><span>Max altitude</span><strong>{fmt(t["max_alt"])} m</strong></div>
      <div><span>Grade</span><strong>{e(t["grade_txt"])}</strong></div>
      <div><span>Group</span><strong>{e(t["group"])}</strong></div>
      <div><span>From</span><strong>US${fmt(t["price"])}</strong></div>
    </div>
  </div>
  <p class="photo-credit">{credit_line(t["hero"])}</p>
</section>

<nav class="trip-nav" aria-label="On this page"><div class="wrap"><ul>
  <li><a href="#overview">Overview</a></li><li><a href="#route">Route map</a></li><li><a href="#itinerary">Day by day</a></li>
  <li><a href="#included">What's included</a></li><li><a href="#permits">Permits</a></li><li><a href="#when">When to go</a></li><li><a href="#faq">Questions</a></li>
</ul></div></nav>

<div class="wrap trip-layout">
  <div class="trip-main">
    <section id="overview" aria-labelledby="ov-title">
      <h2 id="ov-title">About this {"trek" if is_trek else "climb"}</h2>
      <p class="lede">{e(t["intro"])}</p>
      <ul class="highlights">{"".join(f'<li>{icon("check")}<span>{e(h)}</span></li>' for h in t["highlights"])}</ul>
    </section>

    <section id="route" aria-labelledby="route-title">
      <h2 id="route-title">Route and altitude</h2>
      <div class="route">
        <div class="route-panel"><h3><span>Route map</span><span>{e(t["distance"])}</span></h3>{overview_map(t, P)}</div>
        <div class="route-panel"><h3><span>Altitude, day by day</span><span>Max {fmt(t["max_alt"])} m</span></h3>{profile(t, P)}</div>
      </div>
      <p class="note">{route_note}</p>
    </section>

    <section id="itinerary" aria-labelledby="it-title">
      <h2 id="it-title">Day by day</h2>
      <ol class="itin-layout">{"".join(days_html)}</ol>
      <p class="note">Walking times are for a steady pace with stops. Your guide may change overnight stops to suit the weather, trail conditions and how the group is feeling.</p>
    </section>

    <section id="included" aria-labelledby="inc-title">
      <h2 id="inc-title">What's included</h2>
      <div class="incl">
        <div class="yes"><h3>Included in the price</h3><ul>{"".join(f'<li>{icon("check")}<span>{e(x)}</span></li>' for x in incl)}</ul></div>
        <div class="no"><h3>Not included</h3><ul>{"".join(f'<li>{icon("minus")}<span>{e(x)}</span></li>' for x in excl)}</ul></div>
      </div>
    </section>

    <section id="permits" aria-labelledby="perm-title">
      <h2 id="perm-title">Permits and practical details</h2>
      <div class="info">
        <div class="info-item"><h3>{icon("identification-card")}Permits you need</h3><ul>{permits}</ul><p class="note">{e(t["permit_note"])}</p></div>
        <div class="info-item"><h3>{icon("first-aid-kit")}Altitude and safety</h3><p>Above 3,000 m we check everyone's oxygen level and pulse each evening, and talk through how you're sleeping and eating. If altitude symptoms don't ease with rest, we go down. No summit or pass is worth pushing on for. Your insurance needs to cover helicopter rescue up to {fmt(t["max_alt"])} m.</p></div>
        <div class="info-item"><h3>{icon("bed")}Where you stay</h3><p>{"Simple, family-run tea houses: twin rooms, shared bathrooms higher up, and a warm dining room around the stove where everyone gathers in the evening. Hot showers and phone charging cost a few dollars extra." if is_trek else "Tea houses on the walk in, then two-person tents at base camp and high camp. At base camp a cook team looks after you, with a dining tent and a toilet tent."}</p></div>
        <div class="info-item"><h3>{icon("backpack")}Fitness and preparation</h3><p>{"If you can walk for six hours on hilly ground several days in a row, you'll be fine. Two or three months of regular hill walks with a loaded daypack is the best preparation." if is_trek else "You need good hill fitness, some experience walking in crampons and a head for heights. When you book, we send a training plan and a full kit list, and we check your gear together in Kathmandu."}</p></div>
      </div>
    </section>

    <section id="when" aria-labelledby="when-title">
      <h2 id="when-title">When to go</h2>
      {months_strip(t["season"])}
      <p class="note">Best months: {best_months_text(t["season"])}. Private departures run on any date that suits you within the season.</p>
    </section>

    <section aria-labelledby="gal-title">
      <h2 id="gal-title">Along the way</h2>
      <div class="gallery">{gallery}</div>
      <p class="credit">{gallery_credits}</p>
    </section>

    <section id="faq" aria-labelledby="faq-title">
      <h2 id="faq-title">Common questions</h2>
      <div class="faq">{faq}</div>
    </section>
  </div>

  <aside class="trip-aside" aria-label="Trip summary">
    <div class="summary">
      <div class="summary-top"><small>From, per person</small><p class="amount">US${fmt(t["price"])} <span>{t["days_n"]} days</span></p></div>
      <dl>{dl}</dl>
      <div class="summary-actions">
        <a href="/contact.html?trip={t["slug"]}" class="btn btn-primary btn-block">{CTA} {icon("arrow-right")}</a>
        <a href="https://wa.me/{WA}?text={e(wa_text.replace(' ', '%20'))}" class="btn btn-ghost btn-block" target="_blank" rel="noopener">{icon("whatsapp-logo")} Ask on WhatsApp</a>
        <p class="summary-note">No payment needed to enquire. We reply within one working day.</p>
      </div>
      <div class="summary-accred"><span>Licensed in Nepal</span>{accred_row("mini")}</div>
    </div>
    <div class="aside-live">
      <div class="route-panel"><h3><span id="mapDay">Route overview</span></h3>{overview_map(t, P, W=340, H=300, live=True)}</div>
    </div>
  </aside>
</div>

<section class="section" aria-labelledby="rel-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="rel-title">Other trips you might like</h2></div><a class="link" href="{section_url}">All {section_name.lower()} {icon("arrow-right")}</a></div>
  <div class="cards">{"".join(trip_card(x) for x in related)}</div>
</div></section>
{cta_band(title=f"Thinking about the {t['short']}?", text="Tell us your dates and who's coming. We'll send a day-by-day plan, a clear price and an honest view on whether it's the right trip for you.", photo_slug=t["gallery"][0], trip=t["slug"])}
</main>
<div class="mobile-book"><p class="price"><small>From, per person</small><strong>US${fmt(t["price"])}</strong></p><a href="/contact.html?trip={t["slug"]}" class="btn btn-primary">{CTA}</a></div>
"""
    html_ += footer()
    write(t["file"], html_)

# ═════════════════════════════════════════════════════════════════ HOME
def home():
    treks = [t for t in TRIPS if t["kind"] == "trek"]
    tile = lambda cls, slug, title, text, href, sizes: f'<a href="{href}" class="tile {cls} reveal">{img(slug, sizes, alt="")}<h3>{e(title)}</h3><p>{e(text)}</p></a>'
    ladder = [
        ("Mera Peak", 6476, "A long glacier walk with no steep ice", "/articles/merapeak.html", "mera"),
        ("Island Peak", 6189, "Fixed ropes up a short, steep headwall", "/articles/islandpeak.html", "island-peak"),
        ("Lobuche East", 6119, "An airy summit ridge facing Everest", "/articles/lobuche.html", "lobuche"),
        ("Himlung Himal", 7126, "The natural first 7,000 m peak", "/articles/himlung.html", "phu"),
        ("Ama Dablam", 6812, "Real rock and ice climbing", "/articles/amadablam-blog.html", "ama-dablam"),
    ]
    ld_web = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": BRAND, "publisher": {"@id": SITE + "/#organization"}}
    h = head("Beyond Summit Expeditions | Small-Group Treks & Climbs in Nepal",
             "Small-group treks and guided climbs in Nepal with a local Kathmandu team. Everest Base Camp, Annapurna, Manaslu, Upper Mustang, Island Peak and Mera Peak, with day-by-day route maps.",
             "/", ld=[ORG_LD, ld_web], preload=preload_for("hero"))
    h += header("/", photo_hero=True)
    opt = lambda pairs: "".join(f'<option value="{v}">{e(n)}</option>' for v, n in pairs)
    h += f"""<main id="main">
<section class="photo-hero home-hero" aria-labelledby="hero-title">
  <picture>{img("hero", "100vw", eager=True, pos="50% 45%")}</picture>
  <div class="wrap hero-in">
    <h1 id="hero-title">Walk the Himalaya with a <em>local</em> guide.</h1>
    <p class="lede">Small-group treks and climbs across Nepal, planned and led by Elwin Tamang from Kathmandu.</p>
    <div class="hero-actions"><a href="#trips" class="btn btn-light">Find your trek {icon("arrow-right")}</a><a href="/contact.html" class="btn btn-onphoto">{CTA}</a></div>
  </div>
  <p class="photo-credit">Our autumn group on the Manaslu Circuit</p>
</section>

<div class="wrap finder">
  <form class="finder-card" id="finder" aria-label="Find a trip">
    <label><span>Trip type</span><select name="type">{opt([("trek", "Trekking"), ("climb", "Peak climbing")])}</select></label>
    <label><span>Region</span><select name="region">{opt([("all", "Anywhere in Nepal"), ("everest", "Everest"), ("annapurna", "Annapurna"), ("manaslu", "Manaslu"), ("mustang", "Mustang"), ("langtang", "Langtang")])}</select></label>
    <label><span>Length</span><select name="length">{opt([("all", "Any length"), ("short", "Up to 12 days"), ("two-weeks", "About two weeks"), ("long", "Three weeks or more")])}</select></label>
    <label><span>Level</span><select name="level">{opt([("all", "Any level"), ("moderate", "Moderate"), ("strenuous", "Challenging")])}</select></label>
    <button class="btn btn-primary" type="submit">Show trips</button>
  </form>
</div>

<section class="section-sm" aria-label="Why travel with us"><div class="wrap">
  <div class="trust reveal">
    <div>{icon("chat-circle-text")}<strong>A real person replies</strong><span>Every message is answered by Elwin, usually within a working day</span></div>
    <div>{icon("users-three")}<strong>Groups of 2 to 8</strong><span>Private departures on the dates you choose</span></div>
    <div>{icon("mountains")}<strong>Led by a local</strong><span>Every trip planned and led by our founder, Elwin Tamang</span></div>
    <div>{icon("shield-check")}<strong>One clear price</strong><span>Permits, guide, porters and meals on the trek are all included</span></div>
  </div>
  <h2 class="accred-title">Licensed and registered in Nepal</h2>
  {accred_row()}
</div></section>

<section class="section" id="trips" aria-labelledby="treks-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="treks-title">Our most-loved treks</h2><p class="lede">Tea-house treks with rest days built in, permits and flights taken care of, and a map for every day of the route.</p></div>
  <a class="link" href="/trekking.html">All treks {icon("arrow-right")}</a></div>
  <div class="cards">{"".join(trip_card(t) for t in treks)}</div>
</div></section>

<section class="section section-alt" aria-labelledby="reg-title"><div class="wrap">
  <div class="head"><h2 id="reg-title">Where would you like to go?</h2></div>
  <div class="bento">
    {tile("tile-a", "everest-sunset", "Everest", "Sherpa villages, old monasteries and the highest mountains on Earth", "/trekking.html?f=everest#trips", "(max-width: 860px) 100vw, 50vw")}
    {tile("tile-b", "machapuchare", "Annapurna", "Forest trails, Gurung villages and the Annapurna Sanctuary", "/trekking.html?f=annapurna#trips", "(max-width: 860px) 100vw, 50vw")}
    {tile("tile-c", "lo-manthang", "Upper Mustang", "A walled Tibetan kingdom where the monsoon barely reaches", "/articles/upper-mustang-blog.html", "(max-width: 860px) 50vw, 33vw")}
    {tile("tile-d", "manaslu", "Manaslu", "Quiet trails, big mountains", "/articles/manaslu-blog.html", "(max-width: 860px) 50vw, 17vw")}
  </div>
</div></section>

<section class="section" aria-labelledby="how-title"><div class="wrap split">
  <div class="split-media reveal">
    <div class="ph">{img("larke-pass-group", "(max-width: 860px) 60vw, 30vw")}</div>
    <div class="ph">{img("prayer-flags", "(max-width: 860px) 40vw, 20vw")}</div>
    <div class="ph">{img("team-sign", "(max-width: 860px) 40vw, 20vw", pos="30% 50%")}</div>
  </div>
  <div class="reveal">
    <p class="eyebrow">How we travel</p>
    <h2 id="how-title">Small groups, at the pace of the mountains</h2>
    <p class="lede" style="margin-top:1rem">Never more than eight people, rest days in every itinerary, and plans that change with the weather and with how you're feeling.</p>
    <ul class="ticks">
      <li><span class="i-wrap">{icon("calendar-blank")}</span><strong>Private departures</strong><span>Your dates, your group, no strangers unless you want them.</span></li>
      <li><span class="i-wrap">{icon("identification-card")}</span><strong>Permits and flights sorted</strong><span>Everything is arranged before you land in Kathmandu.</span></li>
      <li><span class="i-wrap">{icon("handshake")}</span><strong>Porters treated fairly</strong><span>Fair pay, insurance, proper boots and jackets, and loads under 20 kg.</span></li>
      <li><span class="i-wrap">{icon("first-aid-kit")}</span><strong>Daily health checks</strong><span>Above 3,000 m we check everyone's oxygen level each evening.</span></li>
    </ul>
  </div>
</div></section>

<section class="section section-alt" aria-labelledby="climb-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="climb-title">From your first summit to 7,000 m</h2><p class="lede">Most people build up step by step: a glacier walk first, then fixed ropes, then higher and more technical peaks.</p></div>
  <a class="link" href="/expeditions.html">All climbs {icon("arrow-right")}</a></div>
  <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
    {"".join(f'<a class="card reveal" href="{hr}"><div class="ph" style="aspect-ratio:3/2">{img(ph, "(max-width: 640px) 100vw, 20vw", alt="")}</div><div class="card-body"><p class="card-region num">{fmt(a)} m</p><h3>{e(n)}</h3><p class="card-text">{e(s)}</p></div></a>' for n, a, s, hr, ph in ladder)}
  </div>
</div></section>

<section class="section" aria-labelledby="when-title"><div class="wrap">
  <div class="head"><h2 id="when-title">When to go</h2><p class="lede">Spring and autumn are the main seasons, but there's somewhere good to walk in every month of the year.</p></div>
  <div class="seasons">
    <div class="season reveal"><h3>{icon("flower-tulip")}Spring</h3><small>March to May</small><p>Rhododendrons in flower and warm days on the trail. The views get hazier towards late May.</p></div>
    <div class="season reveal"><h3>{icon("cloud-rain")}Monsoon</h3><small>June to August</small><p>Wet and cloudy on most trails, with one great exception: Upper Mustang, which stays dry.</p></div>
    <div class="season reveal"><h3>{icon("sun")}Autumn</h3><small>September to November</small><p>Crisp, clear skies after the rains. October is the classic month, and the busiest.</p></div>
    <div class="season reveal"><h3>{icon("snowflake")}Winter</h3><small>December to February</small><p>Cold nights, and snow often closes the high passes. Lower treks like Poon Hill are quiet and beautiful.</p></div>
  </div>
  <p style="margin-top:1.5rem"><a class="link" href="/articles/best-time-to-trek-nepal.html">Month-by-month guide {icon("arrow-right")}</a></p>
</div></section>

<section class="section section-alt" aria-labelledby="ph-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="ph-title">Photos from our recent groups</h2></div><a class="link" href="/gallery.html">See all {len(GALLERY)} photos {icon("arrow-right")}</a></div>
  <div class="gallery reveal">
    <figure>{img("traveller-local", "(max-width: 860px) 100vw, 50vw", pos="50% 30%")}<figcaption>Making friends in the villages</figcaption></figure>
    <figure>{img("waterfall-spray", "(max-width: 860px) 50vw, 25vw")}<figcaption>Manaslu Circuit</figcaption></figure>
    <figure>{img("snow-bridge", "(max-width: 860px) 50vw, 25vw")}</figure>
    <figure>{img("gate-group", "(max-width: 860px) 50vw, 25vw")}<figcaption>Kani gate on the trail</figcaption></figure>
    <figure>{img("cholatse-lodge", "(max-width: 860px) 50vw, 25vw")}<figcaption>Cholatse</figcaption></figure>
  </div>
  <p style="margin-top:1.25rem"><a class="link" href="{INSTAGRAM}" target="_blank" rel="noopener">Follow us on Instagram {icon("arrow-up-right")}</a></p>
</div></section>

<section class="section" aria-labelledby="j-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="j-title">Before you go</h2></div><a class="link" href="/blog.html">All guides {icon("arrow-right")}</a></div>
  <div class="posts">{"".join(post_card(p) for p in POSTS[:3])}</div>
</div></section>
{cta_band()}
</main>
"""
    h += footer()
    write("index.html", h)

# ═════════════════════════════════════════════════════════════════ LISTINGS
INCLUDED_SHORT = [
    ("Your own licensed guide", "English-speaking and first-aid trained, with you from the first day to the last."),
    ("Porters, treated fairly", "One porter for every two trekkers, insured, with loads kept under 20 kg."),
    ("Every permit", "National park, conservation and restricted-area fees, all arranged before you arrive."),
    ("Rooms and meals on the trek", "Tea-house twin rooms, with breakfast, lunch and dinner every day."),
    ("Flights and transfers", "Domestic flights, road transport and airport pick-ups, as listed in the itinerary."),
]
def page_hero(bc, title, lede, slug=None, extra=""):
    fig = f'<figure>{img(slug, "(max-width: 860px) 100vw, 50vw", eager=True)}</figure>' if slug else ""
    return f"""<section class="page-hero{'' if slug else ' text-only'}"><div class="wrap">
  {crumbs(bc)}
  <div class="page-hero-grid">
    <div class="hero-in"><h1>{e(title)}</h1><p class="lede">{e(lede)}</p>{extra}</div>
    {fig}
  </div>
  {f'<p class="credit" style="text-align:right">{credit_line(slug)}</p>' if slug and photo(slug)["credit"] else ''}
</div></section>"""

def compare_table(trips):
    rows = "".join(f'<tr><td><a class="link" href="{url(t)}">{e(t["short"])}</a></td><td>{t["days_n"]}</td><td>{fmt(t["max_alt"])} m</td><td>{e(t["grade_txt"])}</td><td>{e(best_months_text(t["season"]))}</td><td>US${fmt(t["price"])}</td></tr>' for t in trips)
    return f'<div class="table-wrap"><table><thead><tr><th>Trip</th><th>Days</th><th>Highest point</th><th>Grade</th><th>Best months</th><th>From</th></tr></thead><tbody>{rows}</tbody></table></div>'

def trekking():
    treks = [t for t in TRIPS if t["kind"] == "trek"]
    bc = [("Home", "/"), ("Treks", None)]
    filt = [("all", "All treks"), ("everest", "Everest"), ("annapurna", "Annapurna"), ("manaslu", "Manaslu"), ("mustang", "Mustang"), ("langtang", "Langtang"),
            ("short", "Up to 12 days"), ("moderate", "Moderate"), ("strenuous", "Challenging"), ("restricted", "Restricted areas")]
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + url(t), "name": t["name"]} for i, t in enumerate(treks)]}
    h = head("Trekking in Nepal 2026: Itineraries, Maps & Prices | Beyond Summit",
             "Compare Nepal's best treks: Everest Base Camp, Annapurna Base Camp, Annapurna Circuit, Manaslu, Upper Mustang and Langtang. Day-by-day route maps, altitude profiles and clear prices.",
             "/trekking.html", ld=[ORG_LD, crumbs_ld(bc), ld], preload=preload_for("pokhara"))
    h += header("/trekking.html")
    h += f"""<main id="main">
{page_hero(bc, "Trekking in Nepal", "Tea-house treks from ten days to three weeks. Each one has a day-by-day map, an altitude profile and a price that already includes permits, guide and porters.", "pokhara")}
<section class="section-sm" id="trips" aria-labelledby="list-title"><div class="wrap">
  <h2 id="list-title" class="sr-only">All treks</h2>
  <div class="filters" data-filters="tripGrid" role="group" aria-label="Filter treks">{"".join(f'<button type="button" data-f="{v}" aria-pressed="{str(v == "all").lower()}">{e(n)}</button>' for v, n in filt)}</div>
  <div class="cards" id="tripGrid">{"".join(trip_card(t) for t in treks)}</div>
  <p class="empty" hidden>No treks match that filter yet. <a class="link" href="/contact.html">Ask us about a custom route</a></p>
</div></section>
<section class="section" aria-labelledby="cmp-title"><div class="wrap">
  <div class="head"><h2 id="cmp-title">Compare at a glance</h2></div>
  {compare_table(treks)}
</div></section>
<section class="section section-alt" aria-labelledby="inc-title"><div class="wrap split">
  <div><h2 id="inc-title">What every trek includes</h2><p class="lede" style="margin-top:1rem">One price covers the trek. The only extras are your flights to Nepal, travel insurance, drinks and tips.</p>
  <p style="margin-top:1.5rem"><a class="link" href="/articles/nepal-trekking-permits.html">Nepal trekking permits explained {icon("arrow-right")}</a></p></div>
  <ul class="ticks">{"".join(f'<li><span class="i-wrap">{icon("check")}</span><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in INCLUDED_SHORT)}</ul>
</div></section>
{cta_band(title="Not sure which trek suits you?", text="Tell us how many days you have, when you'd like to go and how much hiking you've done. We'll suggest two or three treks that genuinely suit you.", photo_slug="forest-trail")}
</main>
"""
    h += footer()
    write("trekking.html", h)

def expeditions():
    climbs = [t for t in TRIPS if t["kind"] == "climb"]
    bc = [("Home", "/"), ("Climbing", None)]
    eight = "".join(f"""<article class="card reveal" id="{x['slug']}">
  <div class="ph">{img(x["photo"], "(max-width: 640px) 100vw, (max-width: 1099px) 50vw, 400px")}</div>
  <div class="card-body"><p class="card-region num">{fmt(x["alt"])} m, {e(x["route"])}</p><h3>{e(x["name"])}</h3>
  <p class="card-text">{e(x["note"])}</p>
  <div class="card-facts"><span class="chip">{icon("calendar-blank")}{x["days"]} days</span><span class="chip">{icon("sun")}{e(x["season"])}</span></div>
  <p class="card-text" style="margin-top:.6rem"><strong>Experience:</strong> {e(x["req"])}</p>
  <div class="card-foot"><p class="price"><small>From</small><strong>US${fmt(x["price"])}</strong></p><a class="link" href="/contact.html?trip={x['slug']}">Request the plan {icon("arrow-right")}</a></div></div>
</article>""" for x in EIGHT)
    h = head("Peak Climbing & Expeditions in Nepal 2026 | Beyond Summit",
             "Guided climbs in Nepal from your first 6,000 m summit to 8,000 m: Island Peak, Mera Peak, Lobuche East, Himlung Himal, Ama Dablam, Manaslu and Everest. Itineraries, maps and prices.",
             "/expeditions.html", ld=[ORG_LD, crumbs_ld(bc)], preload=preload_for("ama-dablam"))
    h += header("/expeditions.html")
    h += f"""<main id="main">
{page_hero(bc, "Peak climbing and expeditions", "From your first glacier summit to the highest mountains on Earth, with experienced Sherpa climbing guides.", "ama-dablam")}
<section class="section-sm" id="trips" aria-labelledby="p-title"><div class="wrap">
  <div class="head"><h2 id="p-title">6,000 and 7,000 m peaks</h2><p class="lede">Every climb includes a skills day at base camp and a spare summit day in case the weather turns.</p></div>
  <div class="cards">{"".join(trip_card(t) for t in climbs)}</div>
</div></section>
<section class="section" aria-labelledby="cmp-title"><div class="wrap">
  <div class="head"><h2 id="cmp-title">Compare the peaks</h2></div>
  {compare_table(climbs)}
</div></section>
<section class="section section-alt" id="eight-thousanders" aria-labelledby="e-title"><div class="wrap">
  <div class="head"><h2 id="e-title">8,000 m expeditions</h2><p class="lede">For experienced climbers. Ask us for the full expedition plan, kit list and oxygen strategy.</p></div>
  <div class="cards">{eight}</div>
</div></section>
{cta_band(title="Which peak should you climb first?", text="Tell us what you've climbed so far and we'll suggest a sensible next step, with an honest view of your chances.", photo_slug="rope-team")}
</main>
"""
    h += footer()
    write("expeditions.html", h)

# ═════════════════════════════════════════════════════════════════ ACTIVITIES
ACTIVITIES = [
 {"slug": "paragliding", "blurb": "Launch from Sarangkot and ride the thermals over Phewa Lake, with Machapuchare filling the skyline.", "file": "activities/paragliding.html", "name": "Paragliding in Pokhara", "short": "Paragliding", "photo": "paragliding", "hero": "pokhara",
  "place": "Sarangkot, Pokhara", "tags": "air", "from": 75,
  "seo_title": "Paragliding in Pokhara: Tandem Flights from Sarangkot | Beyond Summit",
  "seo_desc": "Tandem paragliding from Sarangkot over Phewa Lake with views of Machapuchare and the Annapurnas. 30 to 90 minute flights with licensed pilots, from US$75.",
  "intro": "Pokhara is one of the best places in the world to fly. You launch from Sarangkot (about 1,600 m), ride the thermals above Phewa Lake with the Annapurna range and Machapuchare in front of you, and land on the lakeshore. Tandem flights need no experience.",
  "facts": [("Launch", "Sarangkot, about 1,600 m"), ("Landing", "Phewa Lake shore"), ("Season", "Best October to May"), ("Age and weight", "From 5 years, up to 110 kg")],
  "options": [("Classic tandem", "30 minutes", 75, "A first flight over the lake and the town."), ("Long thermal flight", "45 minutes", 110, "Higher and longer, with photos and video included."), ("Cross-country and acro", "60 to 90 minutes", 175, "Thermal soaring and wingovers for confident flyers.")],
  "steps": ["Pick-up from your Pokhara hotel", "A 30-minute drive up to Sarangkot", "Safety briefing and harness fitting with your pilot", "A few running steps and you're flying", "Landing by the lake and drive back"],
  "faq": [("Is paragliding in Pokhara safe?", "Pokhara has some of the most reliable flying conditions in Nepal. We only book licensed tandem pilots from established companies, and flights don't go up in poor weather."), ("When is the best time to fly?", "October to May. Flights still run in the monsoon on clear days, but cancellations are more common.")]},
 {"slug": "rafting", "blurb": "From a fun day on the Trishuli to a week of beach camps on the Sun Koshi.", "file": "activities/rafting.html", "name": "Whitewater Rafting in Nepal", "short": "Rafting", "photo": "rafting", "hero": "rafting",
  "place": "Trishuli, Bhote Koshi, Kali Gandaki, Sun Koshi", "tags": "water", "from": 35,
  "seo_title": "Whitewater Rafting in Nepal: Trishuli, Bhote Koshi & Sun Koshi | Beyond Summit",
  "seo_desc": "Rafting trips in Nepal from a one-day Trishuli run (grade III) to the 10-day Sun Koshi expedition. Licensed river guides, safety kayakers and riverside camps. From US$35.",
  "intro": "Nepal's rivers drain the highest mountains in the world, which makes for big, clean whitewater close to Kathmandu and Pokhara. Start with a day on the Trishuli on the way to Chitwan, or spend a week camping on white-sand beaches on the Sun Koshi.",
  "facts": [("Grades", "II to V"), ("Length", "Half a day to 10 days"), ("Season", "September to June, by river"), ("Minimum age", "12 for grade III")],
  "options": [("Trishuli day trip", "1 day, grade III", 35, "Fun rapids on the road between Kathmandu, Pokhara and Chitwan."), ("Bhote Koshi", "2 days, grade IV to V", 120, "Steep, continuous rapids near the Tibetan border. Experienced paddlers."), ("Kali Gandaki", "3 days, grade III to IV", 180, "A deep gorge between Dhaulagiri and Annapurna, with riverside camps."), ("Sun Koshi expedition", "9 to 10 days, grade IV", 680, "A classic multi-day river journey across the country.")],
  "steps": ["Pick-up and drive to the put-in", "Safety talk, paddle training and kit fitting", "On the river with a licensed raft guide", "Lunch on a beach", "Take-out and onward transport"],
  "faq": [("Do I need to be able to swim?", "It helps, but it isn't required on grade III trips. You wear a life jacket and helmet, and our guides teach you what to do if you fall in."), ("When is the river too high?", "During the monsoon (July to August) most rivers are too high for commercial trips. The best months are October to December and March to May.")]},
 {"slug": "jungle-safari", "blurb": "Look for one-horned rhinos from a jeep, from a dugout canoe and on foot with a naturalist.", "file": "activities/junglesafar.html", "name": "Jungle Safari in Chitwan National Park", "short": "Jungle safari", "photo": "rhino", "hero": "rhino",
  "place": "Chitwan National Park", "tags": "wildlife", "from": None,
  "seo_title": "Chitwan National Park Jungle Safari: Rhinos, Birds & Canoeing | Beyond Summit",
  "seo_desc": "Two to four days in Chitwan National Park, a UNESCO World Heritage Site: jeep safaris, canoeing on the Rapti, guided jungle walks and Tharu villages. One-horned rhinos and over 500 bird species.",
  "intro": "Chitwan, in Nepal's subtropical lowlands, became the country's first national park in 1973 and a UNESCO World Heritage Site in 1984. It is one of the best places in Asia to see the greater one-horned rhinoceros, along with gharial crocodiles, sloth bears, deer and more than 500 species of birds. Tigers live here too, though sightings are rare.",
  "facts": [("Location", "Sauraha, 5 to 6 h from Kathmandu"), ("Length", "2 to 4 days"), ("Best season", "October to March"), ("Wildlife", "Rhino, gharial, deer, 500+ bird species")],
  "options": [("Two nights in Sauraha", "3 days", None, "Jeep safari, canoe trip and a walk with a naturalist."), ("Three nights", "4 days", None, "Adds a full-day jeep safari deeper into the park.")],
  "steps": ["Drive or fly to Chitwan (Bharatpur airport)", "Canoe down the Rapti River looking for gharial and kingfishers", "Guided walk in the grasslands with two naturalists", "Jeep safari into the core of the park", "Evening visit to a Tharu village"],
  "faq": [("Do you offer elephant rides?", "No. We don't include elephant-back safaris, for animal welfare reasons. Jeep safaris and walks with experienced naturalists give you a better chance of seeing wildlife anyway."), ("When is the best time to see rhinos?", "February to April, when the tall grass is cut and burned and animals are easier to see. October to March is cooler and more comfortable overall.")]},
 {"slug": "mountain-biking", "blurb": "Dirt roads and singletrack linking temples and villages on the rim of the Kathmandu Valley.", "file": "activities/mountainbiking.html", "name": "Mountain Biking in Nepal", "short": "Mountain biking", "photo": "autumn-valley", "hero": "autumn-valley",
  "place": "Kathmandu Valley and beyond", "tags": "land", "from": 55,
  "seo_title": "Mountain Biking in Nepal: Kathmandu Valley Rides & Tours | Beyond Summit",
  "seo_desc": "Guided mountain-bike rides around the Kathmandu Valley rim and longer tours into the hills. Good bikes, helmets and a local guide. Day rides from US$55.",
  "intro": "The hills around Kathmandu are criss-crossed with dirt roads and singletrack linking temples, Newar towns and terraced farmland. A day on a bike is a great way to see village life on rest days before or after a trek.",
  "facts": [("Where", "Kathmandu Valley rim, Nagarkot, Shivapuri"), ("Length", "Half day to several days"), ("Level", "Beginners to experienced riders"), ("Season", "October to May")],
  "options": [("Valley day ride", "Full day", 55, "Temples, villages and viewpoints on the valley rim."), ("Multi-day tour", "3 to 7 days", None, "Routes in the middle hills, planned to your level.")],
  "steps": ["Pick-up and bike fitting in Kathmandu", "Short drive out of the city traffic", "Ride with your guide and a support vehicle where possible", "Lunch in a village", "Drive back to your hotel"],
  "faq": [("What bikes do you use?", "Hard-tail and full-suspension mountain bikes with hydraulic disc brakes, rented from a specialist shop in Kathmandu. Helmets and gloves are included."), ("Do I need to be very fit?", "No. We choose a route to match your experience, and a vehicle can pick you up on most day rides.")]},
 {"slug": "yoga", "blurb": "A few slow mornings by Phewa Lake to rest your legs after the trek.", "file": "activities/yogaandmeditation.html", "name": "Yoga and Meditation in Pokhara", "short": "Yoga retreats", "photo": "phewa-dawn", "hero": "phewa-dawn",
  "place": "Pokhara lakeside", "tags": "wellness", "from": 280,
  "seo_title": "Yoga & Meditation Retreats in Pokhara, Nepal | Beyond Summit",
  "seo_desc": "Three to seven day yoga and meditation retreats by Phewa Lake in Pokhara, with Annapurna views. A good way to recover after a trek. From US$280.",
  "intro": "After a long trek, a few quiet days by Phewa Lake are hard to beat. We work with small retreat centres around Pokhara for gentle hatha and yin yoga, guided meditation and healthy vegetarian food, with the Annapurnas reflected in the lake at dawn.",
  "facts": [("Where", "Pokhara lakeside"), ("Length", "3 to 7 days"), ("Style", "Hatha, yin and meditation"), ("Level", "All levels")],
  "options": [("Three-day retreat", "3 days", 280, "Daily yoga, meditation and meals."), ("Seven-day retreat", "7 days", None, "A longer stay with optional walks to the World Peace Pagoda and Sarangkot.")],
  "steps": ["Arrive in Pokhara", "Morning yoga at sunrise", "Breakfast and free time by the lake", "Afternoon meditation or a short walk", "Evening yin session"],
  "faq": [("Do I need yoga experience?", "No. Teachers adapt classes for beginners, and sessions are gentle after a trek."), ("Can I add this to a trek?", "Yes. Most people add a retreat after an Annapurna trek, as Pokhara is the end point anyway.")]},
]

def activity_page(a):
    bc = [("Home", "/"), ("Activities", "/outdoor.html"), (a["short"], None)]
    opts = "".join(f'<div class="info-item"><h3>{e(n)}</h3><p class="muted">{e(dur)}</p><p style="margin-top:.4rem">{e(txt)}</p><p class="price" style="margin-top:.8rem"><small>From</small><strong>{("US$" + fmt(pr)) if pr else "Price on request"}</strong></p></div>' for n, dur, pr, txt in a["options"])
    facts = "".join(f'<div class="stat"><span>{e(k)}</span><b style="font-size:1.15rem;margin-top:.2rem">{e(v)}</b></div>' for k, v in a["facts"])
    steps = "".join(f'<li><span class="i-wrap"><b class="num">{i+1}</b></span><strong>{e(s)}</strong><span></span></li>' for i, s in enumerate(a["steps"]))
    faq = "".join(f'<details><summary>{e(q)}{icon("plus")}</summary><div><p>{e(x)}</p></div></details>' for q, x in a["faq"])
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in a["faq"]]}
    h = head(a["seo_title"], a["seo_desc"], "/" + a["file"], image=photo(a["photo"])["base"] + "-1600.webp", ld=[ORG_LD, crumbs_ld(bc), ld_faq], preload=preload_for(a["photo"]))
    h += header("/outdoor.html")
    h += f"""<main id="main">
{page_hero(bc, a["name"], a["intro"], a["photo"], extra=f'<div class="hero-actions"><a class="btn btn-primary" href="/contact.html?trip={a["slug"]}">{CTA} {icon("arrow-right")}</a><a class="btn btn-ghost" href="https://wa.me/{WA}" target="_blank" rel="noopener">{icon("whatsapp-logo")} WhatsApp us</a></div>')}
<section class="section-sm"><div class="wrap"><div class="stats">{facts}</div></div></section>
<section class="section" aria-labelledby="o-title"><div class="wrap">
  <div class="head"><h2 id="o-title">Options and prices</h2></div>
  <div class="info">{opts}</div>
  <p class="note">Prices are per person. We confirm the exact price with your dates, as it depends on group size and season.</p>
</div></section>
<section class="section section-alt" aria-labelledby="s-title"><div class="wrap split">
  <div><h2 id="s-title">How the day works</h2><p class="lede" style="margin-top:1rem">{e(a["blurb"])}</p></div>
  <ol class="ticks">{steps}</ol>
</div></section>
<section class="section" aria-labelledby="f-title"><div class="wrap" style="max-width:860px">
  <h2 id="f-title" style="margin-bottom:1.25rem">Common questions</h2><div class="faq">{faq}</div>
</div></section>
{cta_band(title=f"Add {a['short'].lower()} to your trip", text="Most people add it before or after a trek. Tell us your dates and we'll fit it in.", photo_slug=a["hero"], trip=a["slug"])}
</main>
"""
    h += footer()
    write(a["file"], h)

def outdoor():
    bc = [("Home", "/"), ("Activities", None)]
    cards = []
    for a in ACTIVITIES:
        pr = f'<p class="price"><small>From</small><strong>US${fmt(a["from"])}</strong></p>' if a["from"] else '<p class="price"><small>Price</small><strong>On request</strong></p>'
        cards.append(f"""<a href="/{a['file']}" class="card reveal"><div class="ph">{img(a["photo"], "(max-width: 640px) 100vw, (max-width: 1099px) 50vw, 400px")}</div>
<div class="card-body"><p class="card-region">{e(a["place"])}</p><h3>{e(a["short"])}</h3><p class="card-text">{e(a["blurb"])}</p>
<div class="card-foot">{pr}<span class="link">Details {icon("arrow-right")}</span></div></div></a>""")
    cards.append(f"""<a href="/contact.html?trip=everest-heli" class="card reveal"><div class="ph">{img("everest-lhotse", "(max-width: 640px) 100vw, (max-width: 1099px) 50vw, 400px")}</div>
<div class="card-body"><p class="card-region">Kathmandu to the Khumbu</p><h3>Everest helicopter flight</h3><p class="card-text">A morning flight up the Khumbu valley past Everest Base Camp, with a breakfast stop at the Hotel Everest View.</p>
<div class="card-foot"><p class="price"><small>From</small><strong>US$1,200</strong></p><span class="link">Ask us {icon("arrow-right")}</span></div></div></a>""")
    h = head("Things to Do in Nepal Besides Trekking | Beyond Summit Expeditions",
             "Paragliding in Pokhara, whitewater rafting, jungle safari in Chitwan, mountain biking, yoga retreats and Everest helicopter flights. Add a few days to your trek.",
             "/outdoor.html", ld=[ORG_LD, crumbs_ld(bc)], preload=preload_for("phewa-dawn"))
    h += header("/outdoor.html")
    h += f"""<main id="main">
{page_hero(bc, "More to do in Nepal", "Before or after your trek: fly over Phewa Lake, raft a Himalayan river or go looking for rhinos in Chitwan.", "phewa-dawn")}
<section class="section-sm"><div class="wrap"><div class="cards">{"".join(cards)}</div></div></section>
{cta_band(title="Build a trip around your trek", text="Many people add three or four days for Pokhara, Chitwan or a river trip. We'll sort out the transport in between.", photo_slug="pokhara")}
</main>
"""
    h += footer()
    write("outdoor.html", h)

# ═════════════════════════════════════════════════════════════════ ARTICLES / JOURNAL
POSTS = []  # filled in main()

def post_card(p):
    return f"""<a class="post reveal" href="{p['url']}"><div class="ph">{img(p['photo'], "(max-width: 640px) 100vw, (max-width: 1099px) 50vw, 400px")}</div>
<h3>{e(p['title'])}</h3><p>{e(p['desc'])}</p><p class="meta">{e(p['meta'])}</p></a>"""

def article(path, title, seo_title, desc, photo_slug, bc_name, sections, updated="11 November 2026", related_slugs=()):
    bc = [("Home", "/"), ("Journal", "/blog.html"), (bc_name, None)]
    toc = "".join(f'<li><a href="#{sid}">{e(h_)}</a></li>' for sid, h_, _ in sections)
    body = "".join(f'<h2 id="{sid}">{e(h_)}</h2>{content}' for sid, h_, content in sections)
    ld_art = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "image": SITE + photo(photo_slug)["base"] + "-1600.webp",
              "datePublished": "2026-11-11", "dateModified": "2026-11-11", "author": {"@type": "Organization", "name": BRAND, "url": SITE + "/"}, "publisher": {"@id": SITE + "/#organization"},
              "mainEntityOfPage": SITE + path}
    rel = "".join(trip_card(BYSLUG[s]) for s in related_slugs)
    h = head(seo_title, desc, path, image=photo(photo_slug)["base"] + "-1600.webp", ld=[ORG_LD, crumbs_ld(bc), ld_art], og_type="article", preload=preload_for(photo_slug))
    h += header("/blog.html")
    h += f"""<main id="main">
{page_hero(bc, title, desc, photo_slug, extra=f'<p class="muted" style="margin-top:1rem;font-size:.9rem">Updated {updated}. Written by our Kathmandu team.</p>')}
<div class="wrap article-layout section-sm">
  <article class="prose">{body}</article>
  <nav class="toc" aria-label="Contents"><strong>On this page</strong><ul>{toc}</ul></nav>
</div>
{f'<section class="section" aria-labelledby="rel"><div class="wrap"><div class="head"><h2 id="rel">Treks mentioned in this guide</h2></div><div class="cards">{rel}</div></div></section>' if rel else ''}
{cta_band()}
</main>
"""
    h += footer()
    write(path.lstrip("/"), h)

def permits_article():
    tr = lambda rows: '<div class="table-wrap"><table><thead><tr><th>Permit</th><th>Where it applies</th><th>Fee (foreign nationals)</th></tr></thead><tbody>' + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows) + "</tbody></table></div>"
    sections = [
        ("short-answer", "The short answer", "<p>Most treks in Nepal need two things: an entry permit for the national park or conservation area you walk through, and, in some regions, a local fee or TIMS card. Restricted areas near the Tibetan border, such as Manaslu and Upper Mustang, also need a Restricted Area Permit, which is only issued through a registered agency to trekkers with a licensed guide.</p><p>On every trip we run, all permits are arranged before you arrive and included in the price. This guide explains what they are, so you know what you're paying for.</p>"),
        ("guide-rule", "Do you need a guide?", "<p>Since 2023, the Nepal Tourism Board has required foreign trekkers in national parks and conservation areas to walk with a licensed guide hired through a registered agency. Enforcement varies from trail to trail, but checkpoints in the main regions do check. In restricted areas a guide has always been compulsory.</p><p>From March 2026, restricted-area permits can be issued to a single trekker. Before that you needed at least two people in the group. You still need a licensed guide.</p>"),
        ("regions", "Permits by region", tr([
            ("Sagarmatha National Park", "Everest region (Khumbu)", "NPR 3,000"),
            ("Khumbu Pasang Lhamu Rural Municipality", "Everest region, collected at Lukla or Monjo", "Local fee"),
            ("Annapurna Conservation Area Permit (ACAP)", "Annapurna, Mustang, Nar Phu, Manaslu exit", "NPR 3,000"),
            ("Manaslu Conservation Area Permit (MCAP)", "Manaslu Circuit", "NPR 3,000"),
            ("Langtang National Park", "Langtang Valley", "NPR 3,000"),
            ("Makalu Barun National Park", "Mera Peak approach", "NPR 3,000"),
            ("TIMS card", "Annapurna and Langtang; not used in the Khumbu", "NPR 2,000"),
        ]) + "<p>National park and conservation area fees are lower for SAARC nationals. Fees are paid in Nepali rupees.</p>"),
        ("restricted", "Restricted areas", tr([
            ("Manaslu", "Jagat to Dharamsala", "US$100 for the first 7 days (Sep to Nov), US$75 (Dec to Aug), then a daily fee"),
            ("Upper Mustang", "North of Kagbeni", "US$500 for 10 days until late 2025; change to US$50 per day approved in November 2025"),
            ("Nar Phu", "Koto to Phu", "Weekly fee, higher in autumn"),
            ("Tsum Valley", "Above Lokpa", "Weekly fee, higher in autumn"),
        ]) + "<p>On 18 November 2025 Nepal's cabinet approved replacing the flat Upper Mustang fee with a daily charge of US$50 per person. Some agencies still quote the old system, so check which one applies on your dates. We quote the fee in force when you book.</p>"),
        ("peaks", "Climbing permits", "<p>Trekking peaks such as Island Peak, Mera Peak and Lobuche East need a climbing permit from the Nepal Mountaineering Association. Higher mountains such as Ama Dablam, Himlung and Everest need a royalty permit from the Department of Tourism. Both systems were revised in September 2025: fees are highest in spring, about half in autumn and lowest in winter and the monsoon.</p><p>The spring royalty for Everest rose from US$11,000 to US$15,000 per climber from September 2025.</p>"),
        ("visa", "Nepal tourist visa", "<p>Most nationalities can get a tourist visa on arrival at Kathmandu airport or apply online beforehand. Fees are US$30 for 15 days, US$50 for 30 days and US$125 for 90 days. Your passport must be valid for at least six months.</p>"),
        ("checks", "Before you go", "<ul><li>Bring your passport and four passport photos; we need a copy for permits.</li><li>Restricted-area permits need your original passport in Kathmandu for a few hours on a working day.</li><li>Carry your permits on the trail: they are checked at several posts.</li><li>Fees change. This page reflects the rules we know of in November 2026, and we always confirm before you pay.</li></ul>"),
    ]
    article("/articles/nepal-trekking-permits.html", "Nepal trekking permits in 2026", "Nepal Trekking Permits 2026: Costs, Rules & Restricted Areas Explained",
            "Which permits you need for Everest, Annapurna, Manaslu, Mustang and Langtang, what they cost, the guide rule and the 2025 to 2026 changes.",
            "kagbeni", "Trekking permits", sections, related_slugs=("everest-base-camp", "manaslu-circuit", "upper-mustang"))

def season_article():
    months = [
        ("January", "Cold and clear. Lower treks such as Poon Hill are quiet and beautiful; high passes are often snowed in."),
        ("February", "Still cold, with more snow up high. Days lengthen and the first trekkers arrive by the end of the month."),
        ("March", "Spring begins. Rhododendrons flower in the foothills, and high routes open as snow melts."),
        ("April", "One of the best months: warm days, flowering forests and the Everest climbing season under way."),
        ("May", "Warm and busy until the middle of the month, then haze and the first pre-monsoon storms. Good for Mustang."),
        ("June", "Monsoon arrives. Most trails are wet and cloudy with leeches lower down. Upper Mustang is the exception."),
        ("July", "Peak monsoon. Flights are often delayed and landslides block roads. Choose rain-shadow routes."),
        ("August", "Still wet, but the countryside is green. Late August starts to clear in the high valleys."),
        ("September", "The rains ease through the month. Quieter trails, waterfalls at their best and occasional showers."),
        ("October", "The classic month: clear, stable skies and comfortable temperatures. The busiest month on the trails."),
        ("November", "Cold, very clear and calmer than October. Excellent for Everest, Annapurna and Manaslu."),
        ("December", "Cold nights and short days, but often clear and very quiet. Good for lower and mid-altitude treks."),
    ]
    rows = "".join(f'<tr><td>{m}</td><td>{t}</td></tr>' for m, t in months)
    sections = [
        ("overview", "The short answer", "<p>The best months for trekking in Nepal are <strong>October and November</strong>, followed by <strong>March and April</strong>. Skies are clearest in autumn after the monsoon has washed the air clean; spring is warmer and brings flowering rhododendron forests. Upper Mustang is best from May to October because it lies in the Himalayan rain shadow.</p>"),
        ("months", "Month by month", f'<div class="table-wrap"><table><thead><tr><th>Month</th><th>What to expect</th></tr></thead><tbody>{rows}</tbody></table></div>'),
        ("by-trek", "Best time for each trek", "<ul>" + "".join(f'<li><a href="{url(t)}">{e(t["short"])}</a>: best {e(best_months_text(t["season"]))}</li>' for t in TRIPS) + "</ul>"),
        ("temperatures", "How cold does it get?", "<p>Temperature drops by roughly 6 to 7 &deg;C for every 1,000 m you climb. In October, a pleasant 20 &deg;C afternoon in Namche Bazaar (3,440 m) can be well below freezing at night in Gorak Shep (5,164 m). A four-season sleeping bag is worth it for any trek above 4,500 m, whatever the month.</p>"),
        ("crowds", "Avoiding the crowds", "<p>If you want quieter trails in the main seasons, start in late September or late November, or choose Manaslu, Langtang or the upper Annapurna routes instead of Everest Base Camp. In spring, early March and late May are calmer than April.</p>"),
    ]
    article("/articles/best-time-to-trek-nepal.html", "The best time to trek in Nepal", "Best Time to Trek in Nepal: Month-by-Month Guide 2026",
            "Spring or autumn? A month-by-month guide to weather, crowds and the best season for each of Nepal's main treks.",
            "poon-hill", "Best time to trek", sections, related_slugs=("annapurna-base-camp", "upper-mustang", "langtang-valley"))

def blog():
    bc = [("Home", "/"), ("Journal", None)]
    h = head("Nepal Trekking Guides & Advice | Beyond Summit Journal",
             "Practical guides from our Kathmandu team: permits, the best time to trek, and detailed itineraries with route maps for Everest, Annapurna, Manaslu, Mustang and Nepal's climbing peaks.",
             "/blog.html", ld=[ORG_LD, crumbs_ld(bc)])
    h += header("/blog.html")
    h += f"""<main id="main">
{page_hero(bc, "Journal and trip guides", "Practical, up-to-date advice from the people who run the trips: permits, seasons, and every itinerary in detail.")}
<section class="section-sm"><div class="wrap"><div class="head"><h2>Planning guides</h2></div><div class="posts">{"".join(post_card(p) for p in POSTS if p["type"] == "guide")}</div></div></section>
<section class="section"><div class="wrap"><div class="head"><h2>Trek and climb guides</h2></div><div class="posts">{"".join(post_card(p) for p in POSTS if p["type"] == "trip")}</div></div></section>
{cta_band()}
</main>
"""
    h += footer()
    write("blog.html", h)

# ═════════════════════════════════════════════════════════════════ COMPANY PAGES
# The team is one person. Edit the bio here; keep it to facts Elwin is happy to publish.
FOUNDER = {
    "name": "Elwin Tamang", "role": "Founder and lead guide",
    "photo": "elwin-mountains", "photo2": "elwin-guitar",
    "bio": ["Elwin Tamang founded Beyond Summit Expeditions and runs it from Thamel, Kathmandu.",
            "Elwin plans every trip personally, from the first message about dates to the drive back to your hotel, "
            "and leads groups on the trail. The photos on this site are from those trips.",
            "When you write to us, Elwin is the one who answers."],
}

def founder_card(link=False):
    f = FOUNDER
    more = f'<p><a class="link" href="/guides.html">More about Elwin {icon("arrow-right")}</a></p>' if link else ""
    return f"""<div class="founder reveal">
  <div class="founder-photos"><div class="ph">{img(f["photo"], "(max-width: 860px) 60vw, 28vw")}</div><div class="ph">{img(f["photo2"], "(max-width: 860px) 40vw, 18vw", pos="50% 60%")}</div></div>
  <div class="founder-text"><p class="eyebrow">{e(f["role"])}</p><h3>{e(f["name"])}</h3>{"".join(f"<p>{e(p)}</p>" for p in f["bio"])}{more}</div>
</div>"""

def about():
    bc = [("Home", "/"), ("About", None)]
    vals = [("shield-check", "Safety before summits", "Turnaround times are fixed before summit day, and the guide's call is final. We have turned back many times and will again."),
            ("users-three", "Small groups", "Never more than eight people, so the pace suits you and nobody gets lost in the crowd."),
            ("handshake", "Fair to our team", "Porters are paid fairly and insured, loads are kept under 20 kg, and every porter has proper boots and a jacket."),
            ("certificate", "Licensed and accountable", "We're registered with Nepal's Department of Tourism, and every guide we work with holds a government trekking or climbing licence."),
            ("leaf", "Leave no trace", "We carry rubbish out, use boiled and filtered water instead of plastic bottles, and buy food from the villages we stay in."),
            ("chat-circle-text", "Honest advice", "If a trip isn't right for your experience or the season, we'll tell you, and suggest one that is.")]
    h = head("About Beyond Summit Expeditions | Local Trekking Company in Kathmandu",
             "Beyond Summit Expeditions is a small trekking and mountaineering company in Thamel, Kathmandu, run by Elwin Tamang. Small groups, fair treatment of porters and honest advice.",
             "/about.html", ld=[ORG_LD, crumbs_ld(bc)], preload=preload_for("larke-pass-group"))
    h += header("/about.html")
    h += f"""<main id="main">
{page_hero(bc, "A small, local company in Kathmandu", "Beyond Summit Expeditions is run by Elwin Tamang from Thamel. We keep trips small and unhurried, and plan each one around the people on it.", "larke-pass-group")}
<section class="section"><div class="wrap split">
  <div class="prose reveal">
    <h2 style="margin-top:0">Our story</h2>
    <p>Beyond Summit Expeditions was founded by <strong>Elwin Tamang</strong> to run treks and climbs where every trip is built around the people on it, and where safety comes before any summit.</p>
    <p>Today we run treks and climbs across Nepal, from a first week in the Annapurna foothills to the high passes of the Manaslu Circuit, all planned from Kathmandu.</p>
    <p>We are small on purpose. When you write to us, you hear back from Elwin, the person who will plan your trip.</p>
  </div>
  <div class="split-media reveal">
    <div class="ph">{img("traveller-local", "(max-width: 860px) 60vw, 30vw")}</div>
    <div class="ph">{img("gate-group", "(max-width: 860px) 40vw, 20vw")}</div>
    <div class="ph">{img("snow-bridge", "(max-width: 860px) 40vw, 20vw")}</div>
  </div>
</div></section>
<section class="section section-alt" aria-labelledby="v-title"><div class="wrap">
  <div class="head"><h2 id="v-title">What we stand for</h2></div>
  <div class="values">{"".join(f'<div class="reveal"><span class="i-wrap">{icon(i)}</span><h3>{e(t)}</h3><p>{e(x)}</p></div>' for i, t, x in vals)}</div>
</div></section>
<section class="section" id="licences" aria-labelledby="l-title"><div class="wrap">
  <div class="head"><h2 id="l-title">Licences and memberships</h2><p class="lede">We are a licensed trekking and mountaineering agency in Nepal. Restricted-area and climbing permits can only be issued through agencies like ours, which is one reason it matters who you book with.</p></div>
  {accred_row()}
  <p class="note">You can check any Nepali trekking agency in the member directory on the <a class="link" href="https://www.taan.org.np/" target="_blank" rel="noopener">TAAN website</a>. Ask us for copies of our licence and registration certificates at any time.</p>
</div></section>
<section class="section section-alt" aria-labelledby="t-title"><div class="wrap">
  <div class="head"><h2 id="t-title">Who you'll travel with</h2></div>
  {founder_card(link=True)}
</div></section>
<section class="section" aria-labelledby="g-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="g-title">On the trail with our groups</h2></div><a class="link" href="/gallery.html">See all photos {icon("arrow-right")}</a></div>
  {gallery_strip(["road-cheer", "traveller-child", "golden-peaks", "teahouse-group"])}
</div></section>
{cta_band()}
</main>
"""
    h += footer(extra=LIGHTBOX)
    write("about.html", h)

def guides():
    bc = [("Home", "/"), ("About", "/about.html"), ("Our team", None)]
    person_ld = {"@context": "https://schema.org", "@type": "Person", "name": FOUNDER["name"], "jobTitle": FOUNDER["role"],
                 "image": SITE + "/images/web/elwin-mountains-1024.webp", "worksFor": {"@id": SITE + "/#organization"}}
    h = head("Our Team: Elwin Tamang | Beyond Summit Expeditions, Nepal",
             "Meet Elwin Tamang, founder and lead guide of Beyond Summit Expeditions in Kathmandu, who plans and leads our small-group treks and climbs in Nepal.",
             "/guides.html", image="/images/web/elwin-mountains-1024.webp", ld=[ORG_LD, crumbs_ld(bc), person_ld], preload=preload_for("elwin-mountains"))
    h += header("/about.html")
    h += f"""<main id="main">
{page_hero(bc, "Our team", "Beyond Summit Expeditions is a one-person company: Elwin Tamang plans your trip, answers your messages and leads on the trail.", "elwin-mountains")}
<section class="section-sm"><div class="wrap">{founder_card()}</div></section>
<section class="section"><div class="wrap split">
  <div class="reveal"><h2>What that means for you</h2><p class="lede" style="margin-top:1rem">You deal with one person from start to finish, so nothing gets lost between an office and the trail. If you'd like to talk before you book, we'll set up a video call.</p></div>
  <ul class="ticks reveal">
    <li><span class="i-wrap">{icon("chat-circle-text")}</span><strong>One point of contact</strong><span>The person you message is the person who plans your trip.</span></li>
    <li><span class="i-wrap">{icon("users-three")}</span><strong>Small groups only</strong><span>Never more than eight trekkers, so everyone gets attention.</span></li>
    <li><span class="i-wrap">{icon("handshake")}</span><strong>Porters treated fairly</strong><span>Paid fairly, insured, and loads kept under 20 kg.</span></li>
  </ul>
</div></section>
<section class="section section-alt" aria-labelledby="g-title"><div class="wrap">
  <div class="head-row"><div class="head"><h2 id="g-title">Photos from our trips</h2></div><a class="link" href="/gallery.html">See all photos {icon("arrow-right")}</a></div>
  {gallery_strip(["larke-pass-group", "waterfall-spray", "trail-joy", "cholatse-lodge"])}
</div></section>
{cta_band(title="Talk to Elwin before you book", text="Ask about routes, fitness and gear. No obligation, and you'll get a reply from a real person, not a booking system.")}
</main>
"""
    h += footer(extra=LIGHTBOX)
    write("guides.html", h)

# ═════════════════════════════════════════════════════════════════ GALLERY
# Every own photo once (duplicates from "new images/" were left out). (slug, caption, category)
GALLERY_CATS = [("all", "All"), ("people", "People"), ("trail", "On the trail"), ("peaks", "Mountains"), ("villages", "Villages"), ("climbing", "Climbing")]
GALLERY = [
    ("hero", "Walking towards the Manaslu range", "trail"),
    ("larke-pass-group", "Larkya La, 5,106 m, Manaslu Circuit", "people"),
    ("golden-peaks", "First light on the peaks above a stone village", "villages"),
    ("traveller-local", "Making friends in the villages", "people"),
    ("waterfall-spray", "Through the spray of a waterfall", "trail"),
    ("snow-bridge", "Crossing a suspension bridge after fresh snow", "trail"),
    ("cholatse-lodge", "Cholatse above a lodge in the Khumbu", "peaks"),
    ("gate-group", "Under a kani gate at the entrance to a village", "people"),
    ("yak-meadow", "Nubri valley, Manaslu", "peaks"),
    ("elwin-guitar", "Elwin Tamang, our founder, at a tea-house stop", "people"),
    ("moraine-walk", "Crossing a snowy moraine", "trail"),
    ("autumn-valley", "Larch forest in autumn colour", "peaks"),
    ("traveller-child", "A new friend in the village", "people"),
    ("snow-gate", "A kani gate after a snowfall", "villages"),
    ("road-cheer", "Halfway through a long valley day", "trail"),
    ("rope-team", "Roped together on a snow summit", "climbing"),
    ("teahouse-group", "Packed and ready outside the tea house", "people"),
    ("snow-village", "A stone village under fresh snow", "villages"),
    ("summit-climber", "On a snow ridge above the clouds", "climbing"),
    ("forest-trail", "Forest trail past a tea house", "trail"),
    ("elwin-mountains", "Elwin Tamang above a glacier valley", "people"),
    ("trail-joy", "Good mood on the forest trail", "people"),
    ("glacier-walk", "Glacier walk under a deep blue sky", "climbing"),
    ("high-peaks", "A sea of snow peaks", "peaks"),
    ("prayer-flags", "Under the prayer flags", "people"),
    ("team-sign", "Group photo in the Annapurna region", "people"),
    ("dusk-range", "Snow peaks at dusk", "peaks"),
    ("valley-walk", "Walking up the valley towards the snows", "trail"),
    ("waterfall-trail", "Beside a waterfall on the Manaslu Circuit", "trail"),
    ("snow-group", "Larkya La, 5,106 m", "people"),
]
GCAP = {s: c for s, c, _ in GALLERY}
assert len(GCAP) == len(GALLERY), "duplicate photo in GALLERY"

def gallery_item(slug, cat, sizes, lightbox=True):
    p = photo(slug)
    full = f'{p["base"]}-1600.webp'
    return (f'<figure class="g-item" data-cat="{cat}"><a href="{full}" data-lightbox data-caption="{e(GCAP.get(slug, p["alt"]))}" '
            f'aria-label="Open photo: {e(GCAP.get(slug, p["alt"]))}">{img(slug, sizes)}</a>'
            f'<figcaption>{e(GCAP.get(slug, ""))}</figcaption></figure>')

def gallery_strip(slugs):
    return '<div class="g-strip reveal">' + "".join(gallery_item(s, "", "(max-width: 640px) 50vw, 25vw") for s in slugs) + '</div>'

def gallery():
    bc = [("Home", "/"), ("Gallery", None)]
    ld = {"@context": "https://schema.org", "@type": "ImageGallery", "name": "Photo gallery", "url": SITE + "/gallery.html",
          "author": {"@id": SITE + "/#organization"},
          "image": [{"@type": "ImageObject", "contentUrl": SITE + photo(s)["base"] + "-1600.webp", "caption": c} for s, c, _ in GALLERY]}
    filters = "".join(f'<button type="button" data-g="{k}"{" aria-pressed=\"true\"" if k == "all" else " aria-pressed=\"false\""}>{e(n)}</button>' for k, n in GALLERY_CATS)
    items = "".join(gallery_item(s, c, "(max-width: 640px) 50vw, (max-width: 1099px) 33vw, 25vw") for s, _, c in GALLERY)
    h = head("Photo Gallery: Treks and Climbs in Nepal | Beyond Summit Expeditions",
             "Photos from our small-group treks and climbs in Nepal: the Manaslu Circuit, Larkya La, mountain villages, tea houses and the people we meet along the way.",
             "/gallery.html", image="/images/web/larke-pass-group-1600.webp", ld=[ORG_LD, crumbs_ld(bc), ld])
    h += header("/gallery.html")
    h += f"""<main id="main">
{page_hero(bc, "Photo gallery", f"{len(GALLERY)} photos from our own trips: the trails, the mountains, the villages and the people we walk with. Tap any photo to see it full size.")}
<section class="section-sm"><div class="wrap">
  <div class="g-filters" role="group" aria-label="Filter photos">{filters}</div>
  <div class="g-grid" id="gGrid">{items}</div>
  <p class="note">All photos on this page were taken on our trips. <a class="link" href="{INSTAGRAM}" target="_blank" rel="noopener">More on Instagram {icon("arrow-up-right")}</a></p>
</div></section>
{cta_band(title="Want to be in the next photo?", text="Tell us your dates and which of these places caught your eye. We'll reply within one working day with a plan and a clear price.", photo_slug="road-cheer")}
</main>
"""
    h += footer(extra=LIGHTBOX)
    write("gallery.html", h)

LIGHTBOX = f"""<dialog class="lightbox" id="lightbox" aria-label="Photo viewer">
  <figure><img alt=""><figcaption></figcaption></figure>
  <button type="button" class="lb-btn lb-close" data-lb="close" aria-label="Close">{icon("x")}</button>
  <button type="button" class="lb-btn lb-prev" data-lb="prev" aria-label="Previous photo">{icon("arrow-right")}</button>
  <button type="button" class="lb-btn lb-next" data-lb="next" aria-label="Next photo">{icon("arrow-right")}</button>
  <p class="lb-count" aria-live="polite"></p>
</dialog>
"""

def contact():
    bc = [("Home", "/"), ("Contact", None)]
    opts = "".join(f'<option value="{t["slug"]}">{e(t["name"])}</option>' for t in TRIPS)
    opts += "".join(f'<option value="{x["slug"]}">{e(x["name"])} expedition</option>' for x in EIGHT)
    opts += "".join(f'<option value="{a["slug"]}">{e(a["short"])}</option>' for a in ACTIVITIES) + '<option value="everest-heli">Everest helicopter flight</option>'
    month_opts = "".join(f'<option>{m} {y}</option>' for y in (2027,) for m in MONTHS_FULL)
    month_opts = '<option value="">Not sure yet</option>' + "".join(f'<option>{m} 2026</option>' for m in MONTHS_FULL[10:]) + month_opts
    ld_contact = {"@context": "https://schema.org", "@type": "ContactPage", "url": SITE + "/contact.html", "about": {"@id": SITE + "/#organization"}}
    h = head("Contact Beyond Summit Expeditions | Plan Your Nepal Trek",
             "Plan your Nepal trek or climb with our Kathmandu team. Send a message by WhatsApp or e-mail, or call +977 981 115 7421. We reply within one working day.",
             "/contact.html", ld=[ORG_LD, crumbs_ld(bc), ld_contact])
    h += header("/contact.html")
    h += f"""<main id="main">
{page_hero(bc, CTA, "Tell us roughly what you have in mind. A guide from our Kathmandu office replies within one working day with a suggested itinerary and a clear price.")}
<section class="section-sm"><div class="wrap contact-grid">
  <form class="form" id="enquiry" novalidate data-wa="{WA}" data-email="{EMAIL}" aria-describedby="formHelp">
    <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required><span class="err">Please tell us your name.</span></div>
    <div class="field"><label for="f-email">E-mail</label><input id="f-email" name="email" type="email" autocomplete="email" required><span class="err">Please enter a valid e-mail address.</span></div>
    <div class="field"><label for="f-trip">Trip</label><select id="f-trip" name="trip"><option value="">Not sure yet, I'd like some advice</option>{opts}</select></div>
    <div class="field"><label for="f-month">When</label><select id="f-month" name="month">{month_opts}</select></div>
    <div class="field"><label for="f-people">Number of travellers</label><input id="f-people" name="people" type="number" min="1" max="20" inputmode="numeric"></div>
    <div class="field"><label for="f-country">Country</label><input id="f-country" name="country" autocomplete="country-name"></div>
    <div class="field full"><label for="f-msg">Tell us a bit more</label><textarea id="f-msg" name="message"></textarea><span class="help" id="formHelp">Your fitness, treks you've done before, dietary needs or any questions. Nothing is booked until you say so.</span></div>
    <div class="form-actions">
      <button class="btn btn-wa" type="submit" name="via" value="whatsapp">{icon("whatsapp-logo")} Send on WhatsApp</button>
      <button class="btn btn-ghost" type="submit" name="via" value="email">{icon("envelope-simple")} Send by e-mail</button>
    </div>
    <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
  </form>
  <div>
    <div class="contact-list">
      <a href="https://wa.me/{WA}" target="_blank" rel="noopener"><span class="i-wrap">{icon("whatsapp-logo")}</span><small>WhatsApp</small><strong>{PHONE}</strong></a>
      <a href="tel:{PHONE_RAW}"><span class="i-wrap">{icon("phone")}</span><small>Call, 9 am to 7 pm Nepal time</small><strong>{PHONE}</strong></a>
      <a href="mailto:{EMAIL}"><span class="i-wrap">{icon("envelope-simple")}</span><small>E-mail</small><strong>{EMAIL}</strong></a>
      <a href="https://maps.google.com/?q=Thamel,Kathmandu,Nepal" target="_blank" rel="noopener"><span class="i-wrap">{icon("map-pin")}</span><small>Office</small><strong>{ADDRESS}</strong></a>
    </div>
    <div class="info-item" style="margin-top:1rem"><h3>{icon("clock")}What happens next</h3><p>We reply within one working day with a day-by-day plan and a price. You can change anything. A deposit is only asked for once you're happy with the plan.</p></div>
  </div>
</div></section>
</main>
"""
    h += footer()
    write("contact.html", h)

def credits():
    bc = [("Home", "/"), ("Photo credits", None)]
    rows = "".join(f'<tr><td><a href="{e(c["source"])}" target="_blank" rel="noopener">{e(c["title"])}</a></td><td>{e(c["artist"])}</td><td>{e(c["license"])}</td></tr>' for c in CREDITS.values())
    h = head("Photo Credits | Beyond Summit Expeditions", "Credits and licences for the photographs used on this website.", "/photo-credits.html", ld=[crumbs_ld(bc)])
    h += header("")
    h += f"""<main id="main">
{page_hero(bc, "Photo credits", "Photos of our groups are our own. Photos of places and mountains come from Wikimedia Commons under Creative Commons licences, credited below. They have been resized and compressed.")}
<section class="section-sm"><div class="wrap"><div class="table-wrap"><table><thead><tr><th>Photo</th><th>Photographer</th><th>Licence</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
</main>
"""
    h += footer()
    write("photo-credits.html", h)

def not_found():
    h = head("Page not found | Beyond Summit Expeditions", "This page doesn't exist.", "/404.html", noindex=True)
    h += header("")
    h += f"""<main id="main">
{page_hero([("Home", "/"), ("Not found", None)], "This trail doesn't go anywhere", "The page you were looking for has moved or no longer exists. Try one of these instead.")}
<section class="section-sm"><div class="wrap"><div class="cards">{"".join(trip_card(t) for t in TRIPS[:3])}</div></div></section>
</main>
"""
    h += footer()
    write("404.html", h)

def redirect(path, target, title):
    h = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{e(title)}</title>
<link rel="canonical" href="{SITE}{target}"><meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={target}"></head>
<body><p>This page has moved to <a href="{target}">{e(title)}</a>.</p></body></html>"""
    write(path, h)

def sitemap():
    pages = [p for p in WRITTEN if p not in REDIRECTS and p != "404.html"]
    pri = lambda p: "1.0" if p == "index.html" else "0.9" if p.startswith("articles/") or p in ("trekking.html", "expeditions.html") else "0.7"
    urls = "".join(f'<url><loc>{SITE}/{"" if p == "index.html" else p}</loc><lastmod>2026-11-11</lastmod><priority>{pri(p)}</priority></url>\n' for p in sorted(pages))
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /_src/\nDisallow: /auto.html\n\nSitemap: {SITE}/sitemap.xml\n")

REDIRECTS = {"everest-blog-new.html", "everest-base-camp-guide.html", "articles/everest-base-camp-guide.html", "final.html"}

def main():
    POSTS.extend([
        {"type": "guide", "url": "/articles/nepal-trekking-permits.html", "photo": "kagbeni", "title": "Nepal trekking permits in 2026", "desc": "Which permits you need for each region, what they cost, and the 2025 to 2026 rule changes.", "meta": "Planning guide"},
        {"type": "guide", "url": "/articles/best-time-to-trek-nepal.html", "photo": "poon-hill", "title": "The best time to trek in Nepal", "desc": "A month-by-month guide to weather, crowds and the best season for each trek.", "meta": "Planning guide"},
    ])
    POSTS.extend({"type": "trip", "url": url(t), "photo": t["card"], "title": t["name"], "desc": t["blurb"], "meta": f'{t["days_n"]} days, up to {fmt(t["max_alt"])} m'} for t in TRIPS)
    POSTS.insert(2, {"type": "trip", "url": url(BYSLUG["everest-base-camp"]), "photo": "everest-sunset", "title": "Everest Base Camp, day by day", "desc": "The full 14-day route with maps, altitudes and what each day is really like.", "meta": "Trek guide"})
    for t in TRIPS: trip_page(t)
    for a in ACTIVITIES: activity_page(a)
    home(); trekking(); expeditions(); outdoor(); blog(); about(); guides(); gallery(); contact(); credits(); not_found()
    permits_article(); season_article()
    ebc = url(BYSLUG["everest-base-camp"])
    redirect("everest-blog-new.html", ebc, "Everest Base Camp Trek")
    redirect("everest-base-camp-guide.html", ebc, "Everest Base Camp Trek")
    redirect("articles/everest-base-camp-guide.html", ebc, "Everest Base Camp Trek")
    redirect("final.html", "/", "Beyond Summit Expeditions")
    sitemap()
    approx = sorted(k for k, v in PSRC.items() if v == "approx" and P[k]["key"] not in ("kathmandu", "pokhara"))
    print(f"Built {len(WRITTEN)} pages. Places using approximate coordinates: {len(approx)}")

if __name__ == "__main__":
    main()

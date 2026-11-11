"""Download chosen Commons photos at 2000px, write responsive WebP variants and credits.json."""
import json, os, sys, urllib.request, urllib.error, urllib.parse, io, time
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UA = {"User-Agent": "StaticSiteImageResearch/1.0 (photo attribution lookup)"}
cand = json.load(open(sys.argv[1]))           # candidate meta from commons_search
choice = json.load(open(os.path.join(ROOT, "_src/data/photos_commons.json")))
out = os.path.join(ROOT, "images/places"); os.makedirs(out, exist_ok=True)
credits = {}
for slug, (key, alt) in choice.items():
    m = cand[key]
    target = os.path.join(out, f"{slug}-1600.webp")
    if not os.path.exists(target):
        q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": m["title"], "prop": "imageinfo",
                                    "iiprop": "url", "iiurlwidth": 1920})
        d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers=UA)))
        url = next(iter(d["query"]["pages"].values()))["imageinfo"][0]["thumburl"]
        for attempt in range(6):
            try:
                raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read(); break
            except urllib.error.HTTPError as e:
                if e.code != 429: raise
                time.sleep(15 * (attempt + 1))
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        for w in (640, 1024, 1600):
            v = im.copy(); v.thumbnail((w, w * 2)); v.save(os.path.join(out, f"{slug}-{w}.webp"), "WEBP", quality=74, method=6)
        time.sleep(2.5)
    w, h = Image.open(target).size
    credits[slug] = {"alt": alt, "artist": m["artist"], "license": m["license"], "source": m["page"],
                     "title": m["title"][5:], "w": w, "h": h, "src": f"/images/places/{slug}"}
    print(slug, w, h, flush=True)
json.dump(credits, open(os.path.join(ROOT, "_src/data/photos_credits.json"), "w"), indent=1, ensure_ascii=False)

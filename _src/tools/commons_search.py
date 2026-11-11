"""Search Wikimedia Commons for CC-licensed photos and save candidate thumbnails + metadata.
Usage: python3 commons_search.py OUTDIR "key|query" ...
"""
import json, sys, os, re, urllib.request, urllib.parse, time
UA = {"User-Agent": "StaticSiteImageResearch/1.0 (photo attribution lookup)"}
API = "https://commons.wikimedia.org/w/api.php"
def get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
meta = {}
for arg in sys.argv[2:]:
    key, q = arg.split("|", 1)
    d = get({"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap",
             "gsrnamespace": 6, "gsrlimit": 12, "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
             "iiurlwidth": 360})
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    n = 0
    for p in pages:
        ii = p["imageinfo"][0]; em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "")
        if ii["mime"] != "image/jpeg" or ii["width"] < 1600 or ii["width"] < ii["height"]: continue
        if not re.search(r"CC BY|CC0|Public domain", lic, re.I) or "NC" in lic or "ND" in lic: continue
        artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "")).strip()
        cand = f"{key}-{n}"
        with urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=30) as r:
            open(f"{out}/{cand}.jpg", "wb").write(r.read())
        meta[cand] = {"title": p["title"], "license": lic, "artist": artist[:80], "page": ii["descriptionurl"],
                      "url": ii["url"], "w": ii["width"], "h": ii["height"]}
        n += 1
        if n >= 6: break
    print(key, n, flush=True); time.sleep(0.5)
json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)

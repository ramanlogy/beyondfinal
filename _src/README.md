# How this site is built

Every page is generated, so the header, footer, cards and itinerary blocks are identical everywhere.
Edit the data or templates here, then rebuild. Don't hand-edit the generated .html files: the next build overwrites them.

```
python3 _src/build.py
```

| To change | Edit |
|---|---|
| Trip text, prices, days, FAQs | `data/trips.py` |
| Stop names, altitudes, coordinates | `data/places.py` (OSM positions in `data/coords_osm.json` override within 11 km) |
| Page layouts, home page, contact, about, activities | `build.py` |
| Header, footer, maps, altitude chart, photos | `lib.py` |
| Look and feel | `/css/site.css` (one stylesheet for all pages) |
| Behaviour (menu, filters, live map, enquiry form) | `/js/site.js` |

Photos: place photos come from Wikimedia Commons (`tools/commons_search.py`, `tools/fetch_photos.py`) and are credited on
`/photo-credits.html`. Your own photos live in `/images/web/`; add a new one as a large JPEG, then create its
640/1024/1600 WebP versions the same way the build expects (`name-640.webp` and so on) and add it to `data/own_photos.json`.

The build also regenerates `sitemap.xml` and `robots.txt`.

Icons: our own line set in `icons/` (24 px grid, 1.5 stroke, round caps — the same hand as the Ama Dablam logo).
Edit or add one in `tools/make_icons.py` and run `python3 _src/tools/make_icons.py` to rewrite the SVGs. The four
social logos (WhatsApp, Instagram, Facebook, YouTube) are the brands' own marks and stay as they are.

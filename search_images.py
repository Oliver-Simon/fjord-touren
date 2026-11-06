import json, os, sys, time, urllib.parse, urllib.request, urllib.error, re
UA = {"User-Agent": "FjordTourenNesttun/1.0 (private trip planner; simon.oliver27012004 at gmail)"}
def get(url):
    for a in range(6):
        try:
            time.sleep(2.5)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and a < 5: time.sleep(15*(a+1)); continue
            raise
Q = {"milde": ["Arboretet Milde", "Milde arboretum Bergen"], "alvoen": ["Alvøen hovedgård", "Alvøen Bergen"],
     "sotra": ["Fjell festning", "Fjell fortress Sotra"], "korsfjord_ring": ["Sotrabrua", "Korsfjorden"],
     "dale_vaksdal": ["Vaksdal mølle", "Dale Vaksdal", "Sørfjorden Vaksdal"], "fjord_dreieck": ["Halhjem ferjekai", "Sandvikvåg ferje", "Bjørnafjorden ferje"]}
out = {}
for tid, qs in Q.items():
    n = 0
    for q in qs:
        u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap",
            "gsrnamespace": 6, "gsrlimit": 6, "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 330, "format": "json"})
        pages = json.loads(get(u)).get("query", {}).get("pages", {})
        for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            ii = p["imageinfo"][0]; em = ii.get("extmetadata", {})
            lic = re.sub(r"<[^>]+>", "", em.get("LicenseShortName", {}).get("value", ""))
            if not re.search(r"CC|Public domain|PD", lic, re.I) or ii.get("width", 0) < 800 or ii["width"] < ii["height"]: continue
            n += 1; key = f"{tid}_{n}"
            open(f"img_cand/{key}.jpg", "wb").write(get(ii["thumburl"]))
            out[key] = {"file": p["title"][5:], "license": lic}
            print(key, p["title"][5:][:60], lic, flush=True)
            if n >= 4: break
        if n >= 4: break
json.dump(out, open("img_cand/cands.json", "w"), ensure_ascii=False, indent=1)

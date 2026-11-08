"""Find a fitting, freely licensed lead image per tour (Wikipedia/Commons) and store thumbnail + credit."""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img_src")
UA = {"User-Agent": "FjordTourenNesttun/1.0 (private trip planner; simon.oliver27012004 at gmail)"}
CANDIDATES = {  # tour id -> list of (wiki, article) tried in order
    "troldhaugen": [("no", "Troldhaugen"), ("en", "Troldhaugen")],
    "hjellestad": [("no", "Bjelkarøyna"), ("no", "Hjellestad"), ("no", "Korsfjorden")],
    "fana_krokeide": [("no", "Fana kirke"), ("nn", "Fana kyrkje")],
    "milde": [("no", "Arboretet på Milde"), ("nn", "Milde"), ("no", "Milde"), ("no", "Arboretet og Botanisk hage, Milde"), ("en", "Milde")],
    "alvoen": [("no", "Alvøen hovedgård"), ("no", "Alvøen")],
    "askoy": [("no", "Strusshamn"), ("no", "Askøybroen")],
    "herdla": [("no", "Herdla"), ("en", "Herdla")],
    "nordhordland": [("no", "Nordhordlandsbrua"), ("en", "Nordhordland Bridge")],
    "sotra": [("no", "Fjell festning"), ("en", "Fjell Fortress")],
    "glesvaer": [("no", "Glesvær"), ("nn", "Glesvær")],
    "korsfjord_ring": [("no", "Klokkarvik"), ("no", "Sotrabrua")],
    "knarvik_salhus": [("no", "Salhus"), ("no", "Norsk Trikotasjemuseum")],
    "osteroy": [("no", "Osterøybrua"), ("en", "Osterøy Bridge")],
    "radoy": [("no", "Manger kyrkje"), ("no", "Radøy"), ("nn", "Manger")],
    "samnanger": [("no", "Samnangerfjorden"), ("nn", "Samnanger"), ("no", "Samnanger")],
    "dale_vaksdal": [("no", "Vaksdal Mølle"), ("no", "Vaksdal"), ("no", "Dale (Vaksdal)")],
    "sonnen": [("no", "Bryggen"), ("en", "Bryggen")],
    "lysekloster": [("no", "Lyse kloster"), ("en", "Lyse Abbey")],
    "hardanger": [("no", "Steinsdalsfossen"), ("en", "Steinsdalsfossen")],
    "tysnes": [("no", "Tysnes"), ("nn", "Tysnes")],
    "fjord_dreieck": [("no", "Halhjem–Sandvikvåg"), ("no", "Bekkjarvik"), ("no", "Austevoll")],
    "rosendal": [("no", "Baroniet Rosendal"), ("en", "Barony Rosendal")],
    "fusa_express": [("no", "Fusa"), ("no", "Eikelandsfjorden")],
    "holdhus": [("no", "Holdhus kirke"), ("nn", "Holdhus kyrkje")],
    "hardanger_kreuzung": [("no", "Kvinnherad"), ("no", "Baroniet Rosendal")],
    "varaldsoy": [("no", "Varaldsøy"), ("nn", "Varaldsøy")],
    "fusa_samnanger": [("no", "Samnangerfjorden"), ("no", "Samnanger")],
    "norheimsund_740": [("no", "Norheimsund"), ("no", "Mundheim")],
    "tysnes_lukksund": [("no", "Lukksund bru"), ("nn", "Lukksund bru")],
    "odda_express": [("no", "Odda"), ("en", "Odda")],
    "hardanger_voss": [("no", "Hardangerbrua"), ("en", "Hardanger Bridge")],
    "utne_ring": [("no", "Utne"), ("no", "Utne Hotel"), ("nn", "Utne"), ("no", "Hardanger Folkemuseum")],
    "fyllingsdalen_bones": [("no", "Nordåsvannet"), ("no", "Straume bru (Bergen)"), ("no", "Fyllingsdalen")],
    "fyllingsdalen_loddefjord": [("no", "Damsgård hovedgård"), ("no", "Laksevåg"), ("no", "Loddefjord")],
    "lovstakken_ring": [("no", "Løvstakken"), ("en", "Løvstakken"), ("no", "Fyllingsdalen terminal")],
    "olsvik_godvik_ring": [("no", "Puddefjorden"), ("no", "Askøybroen"), ("no", "Olsvik")],
    "kokstad_soreide_ring": [("no", "Siljustøl"), ("no", "Birkeland kirke"), ("no", "Rådal")],
    "helldalsasen_fyllingsdalen": [("no", "Stadsporten"), ("no", "Nattland"), ("no", "Sandviken (Bergen)")],
    "arna_asane_fyllingsdalen": [("no", "Ytre Arna"), ("no", "Gamle Bergen Museum"), ("no", "Åsane")],
    "sotra_straume_express": [("no", "Sotrabrua"), ("no", "Straume (Øygarden)"), ("en", "Sotra Bridge")],
    "bjoroy_fyllingsdalen": [("no", "Bjorøyna"), ("no", "Bjorøytunnelen"), ("no", "Haakonsvern")],
}
def get(url):
    for attempt in range(6):
        try:
            time.sleep(2.5)
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:
                time.sleep(15 * (attempt + 1)); continue
            raise
def lead_file(wiki, title):
    u = f"https://{wiki}.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "prop": "pageimages", "piprop": "name", "titles": title, "format": "json", "redirects": 1})
    pages = json.loads(get(u))["query"].get("pages", {})
    for p in pages.values():
        if p.get("pageimage"):
            return p["pageimage"]
def info(fname):
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": "File:" + fname, "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 960, "format": "json"})
    pages = json.loads(get(u))["query"]["pages"]
    for p in pages.values():
        if "imageinfo" in p:
            return p["imageinfo"][0]
strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()
only = sys.argv[1:]
meta = json.load(open(os.path.join(OUT, "credits.json"))) if os.path.exists(os.path.join(OUT, "credits.json")) else {}
for tid, cands in CANDIDATES.items():
    if only and tid not in only:
        continue
    for wiki, title in cands:
        try:
            f = lead_file(wiki, title)
            if not f or f.lower().endswith((".svg", ".gif")):
                continue
            ii = info(f)
            if not ii:
                continue
            em = ii.get("extmetadata", {})
            lic = strip(em.get("LicenseShortName", {}).get("value"))
            if not re.search(r"CC|Public domain|PD|GFDL", lic, re.I):
                continue
            data = get(ii["thumburl"])
            open(os.path.join(OUT, tid + ".jpg"), "wb").write(data)
            meta[tid] = {"file": f, "article": f"{wiki}:{title}", "artist": strip(em.get("Artist", {}).get("value"))[:80],
                         "license": lic, "licenseUrl": strip(em.get("LicenseUrl", {}).get("value")),
                         "page": ii.get("descriptionurl"), "w": ii.get("thumbwidth"), "h": ii.get("thumbheight")}
            print(f"{tid:15} {wiki}:{title:28} -> {f[:50]:50} {lic}")
            break
        except Exception as e:
            print(f"{tid:15} {wiki}:{title} Fehler {e}")
        time.sleep(0.3)
    else:
        print(f"{tid:15} KEIN BILD")
json.dump(meta, open(os.path.join(OUT, "credits.json"), "w"), ensure_ascii=False, indent=1)

import os, sys, json, time, re, urllib.request, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "img")
IMG_SRC = os.path.join(HERE, "img_src")
CREDITS_PATH = os.path.join(IMG_SRC, "credits.json")

UA = {"User-Agent": "FjordTourenNesttun/1.0 (private trip planner; simon.oliver27012004 at gmail)"}

FILES = {
    "fedje": "Fedje_Hordaland_Norway_tunliweb_03.jpg",
    "bekkjarvik_stolmen": "Stolmabrua01-edit.JPG",
    "hellesoy": "Hellesøy_-_Øygarden_-_Norway.jpg",
    "modalen_eksingedalen": "Mo_2.jpg",
    "ulvik_siderstien": "Ulvik_med_tilliggande_herligheiter_II.jpg",
    "eidfjord": "P1000532Eidfjord.JPG",
    "sunnhordland_leirvik": "Leirvik_Sentrum_(Stord,_Norway_2013,_cropped).jpg",
    "lygra": "Lyngheisenteret_på_Lygra.jpg",
    "gudvangen": "Gudvangen-2005-06-30.jpg",
    "flamsbana": "Flåmsbana_train_at_Flåm_Station.jpg",
    "hausdalen_gullfjellet": "Redningshytten.jpg",
    "gullbotn": "Langavatnet_Gullbotn.JPG",
    "strono_ervikane": "Ervikane.jpg",
    "masfjorden_matre": "Matrefjorden,_2025.jpg",
}

def get(url):
    for attempt in range(6):
        try:
            time.sleep(1.5)
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:
                print(f"Rate limited, sleeping {15 * (attempt + 1)}s...")
                time.sleep(15 * (attempt + 1))
                continue
            raise

def info(fname):
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "titles": "File:" + fname, "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1200, "format": "json"
    })
    pages = json.loads(get(u))["query"]["pages"]
    for p in pages.values():
        if "imageinfo" in p:
            return p["imageinfo"][0]

def crop_and_save(src_path, dst_path):
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    target_ratio = 16.0 / 9.0
    current_ratio = w / float(h)
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))
    im = im.resize((800, 450), Image.Resampling.LANCZOS)
    im.save(dst_path, "JPEG", quality=85)

strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()

credits = json.load(open(CREDITS_PATH, encoding="utf-8")) if os.path.exists(CREDITS_PATH) else {}

for tid, fname in FILES.items():
    print(f"Processing {tid} -> {fname}...")
    ii = info(fname)
    if not ii:
        print(f"ERROR: No imageinfo for {fname}")
        continue
    em = ii.get("extmetadata", {})
    lic = strip(em.get("LicenseShortName", {}).get("value"))
    artist = strip(em.get("Artist", {}).get("value"))[:80]
    lic_url = strip(em.get("LicenseUrl", {}).get("value"))
    page_url = ii.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(fname)}"
    
    thumb_url = ii.get("thumburl") or ii.get("url")
    src_img_data = get(thumb_url)
    src_file = os.path.join(IMG_SRC, tid + ".jpg")
    with open(src_file, "wb") as f:
        f.write(src_img_data)
        
    dst_file = os.path.join(IMG_DIR, tid + ".jpg")
    crop_and_save(src_file, dst_file)
    
    credits[tid] = {
        "file": fname,
        "article": f"commons:{fname}",
        "artist": artist,
        "license": lic,
        "licenseUrl": lic_url,
        "page": page_url,
        "w": 800,
        "h": 450
    }
    print(f"  Saved {dst_file} (800x450), artist='{artist}', license='{lic}'")

with open(CREDITS_PATH, "w", encoding="utf-8") as f:
    json.dump(credits, f, ensure_ascii=False, indent=2)

print("Done! Total credits:", len(credits))

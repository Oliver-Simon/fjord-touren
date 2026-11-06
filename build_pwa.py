"""Build the installable web app (index.html + sw.js) from the app template and data.json.

usage: python3 build_pwa.py <template.html> <data.json> [<standalone_out.html>]
"""
import os, re, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
tpl_path, data_path = sys.argv[1], sys.argv[2]
standalone = sys.argv[3] if len(sys.argv) > 3 else None
vendor = os.path.join(HERE, "vendor")

tpl = open(tpl_path, encoding="utf-8").read()
css = re.sub(r"url\(images/[^)]*\)", "none", open(os.path.join(vendor, "leaflet.css"), encoding="utf-8").read())
js = open(os.path.join(vendor, "leaflet.js"), encoding="utf-8").read()
D = json.load(open(data_path, encoding="utf-8"))
# tour photos (img/<id>.jpg, 800x450) + credits from Wikimedia Commons
import base64
credits_path = os.path.join(HERE, "img_src", "credits.json")
credits = json.load(open(credits_path, encoding="utf-8")) if os.path.exists(credits_path) else {}
for t in D["tours"]:
    f = os.path.join(HERE, "img", t["id"] + ".jpg")
    if os.path.exists(f):
        t["img"] = "data:image/jpeg;base64," + base64.b64encode(open(f, "rb").read()).decode()
        c = credits.get(t["id"], {})
        t["imgCredit"] = {k: c.get(k, "") for k in ("artist", "license", "licenseUrl", "page")}
data = json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = tpl.replace("/*LEAFLET_CSS*/", css).replace("/*LEAFLET_JS*/", js).replace("/*DATA*/", data)

if standalone:
    open(standalone, "w", encoding="utf-8").write(page)
    print(standalone, os.path.getsize(standalone), "bytes")

head = ('<link rel="manifest" href="manifest.json">\n'
        '<link rel="apple-touch-icon" href="icon-192.png">\n</head>')
reg = ('<script>if("serviceWorker" in navigator && /^https?:$/.test(location.protocol))'
       'navigator.serviceWorker.register("sw.js").catch(function(){});</script>\n</body>')
pwa = page.replace("</head>", head, 1)
pwa = pwa[::-1].replace("</body>"[::-1], reg[::-1], 1)[::-1]
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(pwa)

version = "fjord-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
sw = open(os.path.join(HERE, "sw.template.js"), encoding="utf-8").read().replace("__VERSION__", version)
open(os.path.join(HERE, "sw.js"), "w", encoding="utf-8").write(sw)
print("index.html", os.path.getsize(os.path.join(HERE, "index.html")), "bytes,", version)

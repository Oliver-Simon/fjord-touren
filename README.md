# Fjord-Touren Web-App

- `index.html` + `sw.js` + `manifest.json` + Icons = installierbare Web-App (offline per Service Worker).
- Standalone-Datei ohne Server: `~/fjord_touren_neu.html` (Handy: /sdcard/Download/fjord_touren_wetter_v2.html).

## Aufs Handy installieren / aktualisieren
1. `cd ~/fjord_touren_webapp && python3 -m http.server 8765 --bind 127.0.0.1`
2. Handy per ADB verbinden, dann `adb reverse tcp:8765 tcp:8765`
3. In Chrome auf dem Handy `http://localhost:8765/` öffnen → Menü ⋮ → „App installieren“.
   Später reicht Schritt 1+2 und die App einmal öffnen: der Service Worker holt die neue Version.

## Fahrpläne neu berechnen (Entur)
```
cd planer
# in chain.py: DAYS = Stichtage (Mi/Sa/So) anpassen
python3 planner2.py            # -> data.json (Entur-Abfragen, ca. 3/s, Cache in ./cache)
python3 slim.py data.json ../data.json
python3 validate.py ../data.json   # Haustür, Umstiege >= 4 Min., Abfahrten am Steig
python3 enturvia.py ../data.json   # Via-Punkt je Tour für „Ganze Tour in Entur“ (nur PC-Browser)
cd .. && python3 build_pwa.py template.html data.json ~/fjord_touren_neu.html
```
Tourdefinitionen: `planer/tours.py`.

## Entur-Links (Stand 27.10.2026, Entur-App 21.6.0)
- Die App `no.entur` öffnet nur `https://entur.no/reiseresultater?…` (nicht `/reiselenke`). Start braucht `startId`, das Ziel darf Koordinaten sein.
- Die App ignoriert Via-Punkte und liest Links nur beim Kaltstart (läuft sie schon, bleibt die alte Suche stehen).
- Android gibt jeden entur.no-Link an die App (verifizierter App-Link) – Via-Links gibt es deshalb nur im PC-Browser.

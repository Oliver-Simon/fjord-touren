// Fjord-Touren service worker: app shell offline, visited map tiles cached.
const VERSION = "fjord-20261106-194008";
const SHELL = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png"];
const TILE_CACHE = "fjord-tiles-v1";
const TILE_HOSTS = ["cache.kartverket.no", "tile.openstreetmap.org", "tiles.openseamap.org"];
const MAX_TILES = 3000;

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== TILE_CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function trimTiles(cache) {
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - MAX_TILES; i++) await cache.delete(keys[i]);
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (TILE_HOSTS.includes(url.hostname)) {
    // map tiles: cache first, so already seen areas work offline
    e.respondWith(caches.open(TILE_CACHE).then(async cache => {
      const hit = await cache.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === "opaque") { cache.put(req, res.clone()); trimTiles(cache); }
      return res;
    }));
    return;
  }
  if (url.origin === self.location.origin) {
    // app shell: network first (picks up updates), cache when offline
    e.respondWith(fetch(req).then(res => {
      if (res.ok) caches.open(VERSION).then(c => c.put(req, res.clone()));
      return res;
    }).catch(async () => {
      const match = await caches.match(req, {ignoreSearch: true});
      if (match) return match;
      return (await caches.match(new URL("index.html", self.location).href)) ||
             (await caches.match(new URL("./", self.location).href)) ||
             (await caches.match("./index.html"));
    }));
  }
});

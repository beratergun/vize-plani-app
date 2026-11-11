/* Vize Planı service worker — sürüm 7738f29956
   Kural: HTML ağ-öncelikli (eski sürümde takılma yok), kabuk dosyaları önbellekte; PDF/özel dosya/yerel sunucu asla önbelleğe alınmaz.
   Kullanıcı verisi (localStorage/IndexedDB) service worker tarafından hiç silinmez. */
const V = "vizeplan-7738f29956";
const CORE = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/apple-touch-icon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => Promise.all(CORE.map(u => fetch(new Request(u, {cache: "reload"})).then(r => { if (!r.ok) throw new Error(u + " " + r.status); return c.put(u, r); }))))); });
self.addEventListener("message", e => { if (e.data === "skip") self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith("vizeplan-") && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const NOCACHE = /\.(pdf|pptx|docx|zip)(\?|$)|\/f\/|\/api\//i;
self.addEventListener("fetch", e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== "GET" || u.origin !== location.origin || NOCACHE.test(u.pathname + u.search) || req.headers.has("range")) return;
  const isDoc = req.mode === "navigate" || u.pathname.endsWith("/") || u.pathname.endsWith("index.html");
  if (isDoc) {
    e.respondWith(Promise.race([fetch(req).then(r => { if (r.ok) { const cp = r.clone(); caches.open(V).then(c => c.put("index.html", cp)); } return r; }), new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 4000))]).catch(() => caches.match("index.html").then(r => r || caches.match("./"))));
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req).then(n => { if (n.ok) { const cp = n.clone(); caches.open(V).then(c => c.put(req, cp)); } return n; })));
});

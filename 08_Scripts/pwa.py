# -*- coding: utf-8 -*-
"""Bağımsız site (GitHub Pages) için PWA dosyaları: manifest, ikonlar, service worker; index.html'e <head> eklemeleri.
Kullanım: build_repo.py içinden make_pwa(dest). Yalnızca HERKESE AÇIK sürüm için (özel materyal içermez)."""
import os
import hashlib
import json

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="{rx}" fill="#111915"/>
<g transform="translate({o} {o}) scale({sc})"><rect x="96" y="132" width="320" height="200" rx="18" fill="#f4f7f5"/>
<rect x="96" y="132" width="16" height="200" rx="8" fill="#6db6f5"/><rect x="140" y="170" width="150" height="16" rx="8" fill="#111915" opacity=".85"/>
<rect x="140" y="204" width="220" height="10" rx="5" fill="#111915" opacity=".35"/><rect x="140" y="228" width="190" height="10" rx="5" fill="#111915" opacity=".35"/>
<path d="M150 290 l30 -34 l26 22 l46 -54 l38 40" fill="none" stroke="#5fd08e" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="196" y="352" width="120" height="14" rx="7" fill="#f4f7f5" opacity=".9"/><rect x="236" y="332" width="40" height="22" fill="#f4f7f5" opacity=".9"/></g></svg>"""

SW = r'''/* Vize Planı service worker — sürüm __VER__
   Kural: HTML ağ-öncelikli (eski sürümde takılma yok), kabuk dosyaları önbellekte; PDF/özel dosya/yerel sunucu asla önbelleğe alınmaz.
   Kullanıcı verisi (localStorage/IndexedDB) service worker tarafından hiç silinmez. */
const V = "vizeplan-__VER__";
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
'''

MANIFEST = {
    "name": "Vize Planı", "short_name": "Vize Planı", "description": "Vize haftası çalışma planı, sınav takvimi ve slayt çalışma stüdyosu",
    "id": "./", "start_url": "./", "scope": "./", "display": "standalone", "orientation": "any", "lang": "tr",
    "background_color": "#0d1311", "theme_color": "#0d1311", "categories": ["education", "productivity"],
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

HEAD = ('<link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#0d1311"><link rel="icon" type="image/png" href="icons/icon-192.png">'
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-title" content="Vize Planı"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">')


def render_icons(out):
    from playwright.sync_api import sync_playwright
    os.makedirs(out, exist_ok=True)
    spec = [("icon-192.png", 192, 96, 1.0), ("icon-512.png", 512, 112, 1.0), ("maskable-512.png", 512, 0, 0.72), ("apple-touch-icon.png", 180, 0, 0.86)]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, size, rx, sc in spec:
            o = 256 - 256 * sc
            svg = ICON_SVG.format(rx=rx, o=round(o, 1), sc=sc)
            pg = b.new_page(viewport={"width": size, "height": size})
            pg.set_content(f'<body style="margin:0;background:transparent"><img style="width:{size}px;height:{size}px;display:block" src="data:image/svg+xml;utf8,{svg.replace("#", "%23").replace(chr(10), "")}"></body>')
            pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(out, name), omit_background=True, clip={"x": 0, "y": 0, "width": size, "height": size})
            pg.close()
        b.close()
    open(os.path.join(out, "icon.svg"), "w", encoding="utf-8").write(ICON_SVG.format(rx=112, o=0, sc=1.0))


def make_pwa(dest, index_html):
    """dest köküne manifest/sw/ikonlar yazar; <head> eklemeli index.html metnini döndürür."""
    ver = hashlib.sha256(index_html.encode("utf-8")).hexdigest()[:10]
    render_icons(os.path.join(dest, "icons"))
    open(os.path.join(dest, "manifest.webmanifest"), "w", encoding="utf-8").write(json.dumps(MANIFEST, ensure_ascii=False, indent=1))
    open(os.path.join(dest, "sw.js"), "w", encoding="utf-8").write(SW.replace("__VER__", ver))
    out = index_html.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + HEAD, 1)
    assert HEAD in out
    return out, ver

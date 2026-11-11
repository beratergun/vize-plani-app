# -*- coding: utf-8 -*-
"""Bağımsız site + PWA: manifest, kurulabilirlik, service worker, çevrimdışı, güncelleme/geri alma (veri kaybı yok), gizlilik sızıntısı, Claude hesabı gerektirmeme.
Önkoşul: py build_repo.py <PWA_DIR> ile üretilmiş genel (public) site. Kullanım: py e2e_pwa.py <PWA_DIR> [chromium|webkit]"""
import sys, os, json, time, shutil, threading, http.server, socketserver, functools, re, tempfile
PWA_SRC = sys.argv[1]; BR = sys.argv[2] if len(sys.argv) > 2 else "chromium"
from playwright.sync_api import sync_playwright
RES = []


def rec(name, ok, detail=""):
    RES.append({"test": name, "result": "PASS" if ok else "FAIL", "detail": str(detail)[:300]})
    print(("PASS" if ok else "FAIL"), name, "::", str(detail)[:200])


def skip(name, why):
    RES.append({"test": name, "result": "NOT TESTED", "detail": why}); print("NOT TESTED", name, "::", why)


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache"); super().end_headers()

    def log_message(self, *a): pass


def serve(d, port):
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), functools.partial(H, directory=d)); srv.allow_reuse_address = True
    threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv


def until(pg, js, t=30):
    s = time.time()
    while time.time() - s < t:
        try:
            v = pg.evaluate(js)
            if v: return v
        except Exception: pass
        time.sleep(0.3)


def main(p):
    work = tempfile.mkdtemp(); site = os.path.join(work, "site"); shutil.copytree(PWA_SRC, site, ignore=shutil.ignore_patterns(".git", "0*", "1*", "__pycache__"))
    # --- gizlilik taraması (yayın paketi)
    idx = open(os.path.join(PWA_SRC, "index.html"), encoding="utf-8").read()
    pdfs = [os.path.join(r, f) for r, _, fs in os.walk(PWA_SRC) for f in fs if f.lower().endswith((".pdf", ".pptx", ".docx")) and ".git" not in r]
    pdfs_priv = [x for x in pdfs if "05_Printable_PDF" not in x]
    rec("[pwa][gizlilik] yayın paketinde ders PDF/PPTX/DOCX dosyası yok (yalnızca üretilmiş yazdırılabilir plan PDF'leri)", not pdfs_priv, pdfs_priv[:3])
    rec("[pwa][gizlilik] genel index.html'de OCR verisi, tam metin dizini ve slayt metni yok (kod içindeki işaret ve müfredat konu başlıkları hariç)", '"⟦OCR⟧' not in idx and '"ft":{"' not in idx, "")
    srv = serve(site, 8780); URL = "http://127.0.0.1:8780/"
    b = getattr(p, BR).launch(); ctx = b.new_context(viewport={"width": 1366, "height": 768}, service_workers="allow"); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append("console:" + m.text[:120]) if m.type == "error" else None)
    pg.goto(URL); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    # --- Claude hesabı gerekmeden çalışıyor
    nclaude = pg.evaluate("typeof window.claude")
    pub = pg.evaluate("[Object.keys(DATA.ft||{}).length, (DATA.qb||[]).length, (DATA.lib||[]).length]")
    rec("[pwa] Claude olmadan açıldı (window.claude yok), ana ekran + takvim sekmeleri hatasız", nclaude == "undefined" and pg.locator("nav.tabs a").count() >= 10, {"claude": nclaude})
    tabs_ok = []
    for t in ("bugun", "takvim", "sinavlar", "odevler", "planlayici", "ilerleme", "slayt", "hazirlik"):
        try:
            pg.evaluate(f"location.hash='#{t}'; 0"); time.sleep(0.5); tabs_ok.append(bool(pg.locator("#view").inner_text().strip()))
        except Exception as e:
            tabs_ok.append(False)
    rec("[pwa] çekirdek sekmeler (Bugün, Takvim, Sınavlar, Ödevler, Planlayıcı, İlerleme, Slayt, CMPE453) Claude hesabı olmadan içerik gösteriyor", all(tabs_ok), tabs_ok)
    rec("[pwa][gizlilik] çalışan genel sitede tam metin dizini ve soru bankası boş (özel materyal sızmıyor)", pub[0] == 0 and pub[1] == 0, pub)
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.8)
    t = pg.locator("#view").inner_text()
    rec("[pwa] Slayt ana ekranı: dosya bağlı değilken dürüst durum ('Yerel kütüphane bağlı değil'), sahte slayt yok", "bağlı değil" in t and pg.locator(".card169").count() == 0, "")
    # --- manifest
    m = pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json())")
    rec("[pwa] manifest: ad 'Vize Planı', display=standalone, start_url/scope, tema rengi, 192/512/maskable ikon", m["name"] == "Vize Planı" and m["display"] == "standalone" and m["start_url"] == "./" and m["theme_color"] and {i["sizes"] for i in m["icons"]} >= {"192x192", "512x512"} and any(i["purpose"] == "maskable" for i in m["icons"]), {k: m[k] for k in ("name", "display", "start_url")})
    sizes = pg.evaluate("Promise.all(['icons/icon-192.png','icons/icon-512.png','icons/maskable-512.png','icons/apple-touch-icon.png'].map(u=>new Promise(r=>{const i=new Image();i.onload=()=>r([u,i.naturalWidth,i.naturalHeight]);i.onerror=()=>r([u,0,0]);i.src=u})))")
    rec("[pwa] ikon dosyaları gerçekten yükleniyor (192, 512, maskable 512, apple 180)", [x[1] for x in sizes] == [192, 512, 512, 180], sizes)
    # --- kurulabilirlik (yalnızca Chromium CDP)
    if BR == "chromium":
        try:
            cdp = ctx.new_cdp_session(pg); cdp.send("Page.enable"); r = cdp.send("Page.getInstallabilityErrors")
            rec("[pwa] Chromium kurulabilirlik denetimi (Page.getInstallabilityErrors) hata döndürmedi", r.get("installabilityErrors") == [], r.get("installabilityErrors"))
        except Exception as e:
            skip("[pwa] kurulabilirlik denetimi", "CDP kullanılamadı: " + str(e)[:80])
    else:
        skip(f"[pwa][{BR}] kurulabilirlik denetimi", "WebKit'te kurulabilirlik API'si yok; gerçek yükleme cihazda denenmeli")
    # --- service worker
    ok = until(pg, "navigator.serviceWorker.ready.then(r=>!!r.active)", 30)
    pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    ctl = pg.evaluate("!!navigator.serviceWorker.controller")
    cached = pg.evaluate("caches.keys().then(async ks=>{const o={}; for(const k of ks){o[k]=(await (await caches.open(k)).keys()).map(r=>new URL(r.url).pathname)} return o})")
    v1 = list(cached.keys())
    rec("[pwa] service worker kaydoldu, etkinleşti ve sayfayı kontrol ediyor; kabuk önbellekte", bool(ok) and ctl and len(v1) == 1 and any(x.endswith("index.html") or x == "/" for x in list(cached.values())[0]), {"önbellek": v1})
    rec("[pwa] önbellekte PDF/özel dosya yok (büyük dosyalar otomatik indirilmiyor)", not any(re.search(r"\.(pdf|pptx|docx)$", x, re.I) for v in cached.values() for x in v), "")
    # --- kullanıcı verisi yaz (tema + IDB kaydı + not)
    pg.click("#theme"); time.sleep(0.4)
    theme = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    pg.evaluate("""new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onupgradeneeded=()=>{}; q.onsuccess=()=>{const db=q.result; const tx=db.transaction('files','readwrite'); tx.objectStore('files').put(new TextEncoder().encode('%PDF-test').buffer,'korunacak-test.pdf'); tx.oncomplete=()=>r(1)}})""")
    ls0 = pg.evaluate("localStorage.getItem('vizeplan.v2')")
    # --- çevrimdışı
    ctx.set_offline(True); pg.reload(); time.sleep(2)
    off = pg.locator("nav.tabs a").count()
    pg.evaluate("location.hash='#takvim'; 0"); time.sleep(0.5)
    rec("[pwa] ÇEVRİMDIŞI: sayfa yenilenince açılıyor, sekmeler ve takvim çalışıyor", off >= 10 and bool(pg.locator("#view").inner_text().strip()), off)
    pg.screenshot(path=os.path.join(r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V102\sonraki", f"{BR}_pwa_offline.png"))
    ctx.set_offline(False)
    # --- güncelleme (v2): sunucudaki dosyaları değiştir
    def swver(): return re.search(r'const V = "(vizeplan-[0-9a-z]+)"', open(os.path.join(site, "sw.js"), encoding="utf-8").read()).group(1)
    ver0 = swver(); orig_sw = open(os.path.join(site, "sw.js"), encoding="utf-8").read(); orig_idx = open(os.path.join(site, "index.html"), encoding="utf-8").read()
    open(os.path.join(site, "sw.js"), "w", encoding="utf-8").write(orig_sw.replace(ver0, "vizeplan-v2test"))
    open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(orig_idx.replace("</body>", "<!-- v2 --></body>"))
    pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); pg.evaluate("navigator.serviceWorker.ready.then(r=>r.update()); 0")
    got = until(pg, "!!document.getElementById('pwa-upd')", 30)
    rec("[pwa] yeni sürüm bulununca 'Yeni sürüm hazır' bildirimi gösteriliyor (otomatik zorla yenileme yok)", bool(got), "")
    if got:
        pg.screenshot(path=os.path.join(r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V102\sonraki", f"{BR}_pwa_update_banner.png"))
        pg.click("#pwa-go"); time.sleep(3); pg.wait_for_selector("nav.tabs a", state="attached")
        keys = pg.evaluate("caches.keys()")
        has_v2 = "<!-- v2 -->" in pg.evaluate("fetch('index.html').then(r=>r.text())")
        theme2 = pg.evaluate("document.documentElement.getAttribute('data-theme')"); ls2 = pg.evaluate("localStorage.getItem('vizeplan.v2')")
        idb = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result)}})")
        rec("[pwa] güncelleme uygulandı: yeni önbellek etkin, eski sürüm önbelleği silindi", keys == ["vizeplan-v2test"] and has_v2, keys)
        rec("[pwa] güncelleme veri kaybettirmedi: tema, yerel kayıt (vizeplan.v2) ve IndexedDB dosyası korundu", theme2 == theme and ls2 == ls0 and "korunacak-test.pdf" in idb, {"tema": theme2, "idb": idb})
        # --- geri alma (rollback): eski sürüm sunucuya geri
        open(os.path.join(site, "sw.js"), "w", encoding="utf-8").write(orig_sw); open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(orig_idx)
        pg.evaluate("navigator.serviceWorker.ready.then(r=>r.update()); 0"); got2 = until(pg, "!!document.getElementById('pwa-upd')", 30)
        if got2:
            pg.click("#pwa-go"); time.sleep(3); pg.wait_for_selector("nav.tabs a", state="attached")
            keys = pg.evaluate("caches.keys()"); has_v2 = "<!-- v2 -->" in pg.evaluate("fetch('index.html').then(r=>r.text())")
            idb = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result)}})")
            rec("[pwa] geri alma (eski sürüme dönüş): önbellek eski sürüme döndü, kullanıcı verisi korundu", keys == [v1[0]] and not has_v2 and "korunacak-test.pdf" in idb and pg.evaluate("localStorage.getItem('vizeplan.v2')") == ls0, keys)
        else:
            rec("[pwa] geri alma bildirimi geldi", False, "bildirim yok")
    rec("[pwa] konsol/istisna hatası yok", not [e for e in errs if "favicon" not in e], errs[:3])
    b.close()
    # --- mobil görünüm (genel site)
    b = getattr(p, BR).launch(); ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    ov = []
    for t in ("bugun", "takvim", "sinavlar", "slayt"):
        pg.evaluate(f"location.hash='#{t}'; 0"); time.sleep(0.5); ov.append(pg.evaluate("document.documentElement.scrollWidth - window.innerWidth"))
    rec("[pwa] mobil 390px: Bugün/Takvim/Sınavlar/Slayt yatay taşma yok", all(x <= 1 for x in ov), ov)
    pg.screenshot(path=os.path.join(r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V102\sonraki", f"{BR}_pwa_mobile_slayt.png")); b.close()
    srv.shutdown(); shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(RES, open(os.path.join(r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V7", f"results_pwa_{BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in RES), "PASS /", sum(r["result"] == "FAIL" for r in RES), "FAIL /", sum(r["result"] == "NOT TESTED" for r in RES), "NOT TESTED")

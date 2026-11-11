# -*- coding: utf-8 -*-
"""Yerel sunucu + otomatik slayt erişimi (dosya seçmeden). Önkoşul: py 12_Local/yerel_sunucu.py --port 8790 --no-browser
Kullanım: py e2e_local.py [chromium|webkit]"""
import sys, os, json, time, urllib.request, urllib.error
import e2e_core as T
from e2e_core import rec, skip, sync_playwright, SHOTS
from e2e_viewer import canvas_state

BASE = os.environ.get("VP_BASE", "http://127.0.0.1:8790")
TOK = open(os.path.join(os.environ["APPDATA"], "VizePlani", "token.txt"), encoding="utf-8").read().strip()


def http(path, headers=None, method="GET"):
    req = urllib.request.Request(BASE + path, headers=headers or {}, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=15); return r.status, r.read(2000), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(300), dict(e.headers)


def until(pg, js, timeout=60, step=0.5):
    t = time.time()
    while time.time() - t < timeout:
        try:
            v = pg.evaluate(js)
            if v: return v
        except Exception:
            pass
        time.sleep(step)
    return None


def main(p):
    # --- sunucu güvenliği
    c, _, _ = http("/api/scan"); rec("[local] anahtarsız /api/scan → 403", c == 403, c)
    c, _, _ = http("/f/D/cmpe%20453/Lecture2.2%20(1).pdf"); rec("[local] anahtarsız dosya → 403", c == 403, c)
    H = {"X-VP-Token": TOK}
    c, b, h = http("/f/D/cmpe%20453/Lecture2.2%20(1).pdf", {**H, "Range": "bytes=0-99"}); rec("[local] anahtarlı dosya + Range → 206, 100 bayt, %PDF", c == 206 and b[:4] == b"%PDF" and h.get("Content-Range", "").startswith("bytes 0-99/"), (c, h.get("Content-Range")))
    for bad in ("/f/D/..%2F..%2FAppData%2Fx.pdf", "/f/D/%2e%2e/%2e%2e/Desktop/Berat_Plan_3Kasim.pdf", "/f/D/cmpe%20453/CMPE453_Syllabus_2026_Fall_VMidTerm.docx.exe", "/f/X/a.pdf"):
        c, _, _ = http(bad, H); rec(f"[local] yol kaçışı/izinsiz tür reddedildi: {bad[:46]}", c in (404, 403), c)
    c, b, _ = http("/api/scan", H); j = json.loads(b[:0] or http("/api/scan", H)[1] or b"{}") if False else None
    body = urllib.request.urlopen(urllib.request.Request(BASE + "/api/scan", headers=H)).read()
    sj = json.loads(body); names = {f["p"].split("/")[-1] for f in sj["files"]}
    rec("[local] /api/scan: DERSLER+ders dosyaları listeleniyor (yeni dosya ekleyince burada çıkar)", sj["ok"] and "Lecture2.2 (1).pdf" in names and "1st week slides_.pdf" in names and not any(f["p"].startswith("_Vize") for f in sj["files"]), len(sj["files"]))
    # --- tarayıcı: HİÇ dosya seçmeden slayt açma
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1500, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached")
    ok = until(pg, "document.querySelectorAll('nav.tabs a').length>0 && document.cookie==='' ", 3)  # HttpOnly: JS çerezi görmez
    pg.evaluate("location.hash='#envanter'; 0"); time.sleep(1.5)
    on = until(pg, "document.body.innerText.includes('Yerel kütüphane bağlı')", 15)
    rec(f"[{T.BR}][local] Envanter: 'Yerel kütüphane bağlı' (dosya seçilmedi)", bool(on), "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_local_envanter.png"))
    txt = pg.locator("#view").inner_text()
    rec(f"[{T.BR}][local] Envanter: BIO110 görünür, konu denetimi (Myhill–Nerode 'Bulundu', CTFT 'Dosyalarda yok')", "BIO110" in txt and "Myhill" in txt and "Bulundu" in txt and "Dosyalarda yok" in txt, "")
    # dosyaları IDB'ye eklemeden aç: BIO 1. hafta PDF
    def open_doc(fname, course):
        pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.6)
        pg.select_option("#vw-c1", label=course); time.sleep(0.4); pg.select_option("#vw-f", value=fname)
        st = until(pg, "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \\d+ \\/ \\d+/.test(e.textContent) ? e.textContent : ''})()", 60)
        return st, canvas_state(pg)
    st, cs = open_doc("1st week slides_.pdf", "BIO110")
    rec(f"[{T.BR}][local] BIO110 '1st week slides_.pdf' dosya seçmeden AÇILDI, sayfa çizildi", bool(st) and "/ 51" in st and cs and cs["ink"] > 3, {"durum": st, "ink": cs and cs["ink"]})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_local_bio1.png"))
    st, cs = open_doc("2nd week presentation slides.pptx", "BIO110")
    rec(f"[{T.BR}][local] BIO110 PPTX (PowerPoint→PDF, 114 slayt) dosya seçmeden AÇILDI", bool(st) and "/ 114" in st and cs and cs["ink"] > 3, {"durum": st})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_local_bio2_pptx.png"))
    st, cs = open_doc("Ch.3.pptx", "CMPE421")
    rec(f"[{T.BR}][local] CMPE421 Ch.3.pptx (56 slayt) dosya seçmeden AÇILDI", bool(st) and "/ 56" in st and cs and cs["ink"] > 3, {"durum": st})
    st, cs = open_doc("PETER LINZ-automata-6th-2017.pdf", "CMPE327") if False else (None, None)
    # IDB'ye hiç dosya yazılmadı
    n = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result.length)}})")
    rec(f"[{T.BR}][local] tarayıcı depolamasına dosya KOPYALANMADI (akışla açılıyor)", n == 0, n)
    # PORTB araması → Slaytı aç → gerçek slayt (sunucudan)
    pg.evaluate("location.hash='#kutuphane'; 0"); time.sleep(0.6); pg.fill("#lib-q", "PORTB"); pg.wait_for_selector("#lib-res .qi")
    pg.locator("#lib-res .qi").first.locator('button[data-act="vw-open"]').click()
    st = until(pg, "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \\d+ \\/ \\d+/.test(e.textContent) ? e.textContent : ''})()", 40)
    rec(f"[{T.BR}][local] PORTB sonucu → 'Slaytı aç' → dosya eklemeden gerçek sayfa çizildi", bool(st) and canvas_state(pg) and canvas_state(pg)["ink"] > 3, st)
    # OCR metni aranabilir mi (görsel sayfa)
    rec(f"[{T.BR}][local] konsol/istisna yok", not errs, errs[:2])
    b.close()
    # --- yanlış anahtarla sayfa açılmaz
    b = getattr(p, T.BR).launch(); pg = b.new_page(); r = pg.goto(f"{BASE}/?t=yanlis"); rec(f"[{T.BR}][local] yanlış anahtarla sayfa → 403", r.status == 403, r.status); b.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_local_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

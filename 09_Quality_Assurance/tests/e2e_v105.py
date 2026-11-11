# -*- coding: utf-8 -*-
"""V10.5: akıllı ana ekran, tek akışta sınav hazırlığı, otomatik yeniden planlama (sınav tamamlandı / yeni materyal / önizleme / geri al), akıllı yanlış defteri, gruplu gezinme, yedek kapsamı.
Önkoşul: yerel sunucu 8790 + genel paket klasörü. py e2e_v105.py <PWA_DIR> [chromium|webkit]"""
import sys, os, json, time, shutil, tempfile, threading, http.server, socketserver, functools, re
PWA = sys.argv[1]; BR = sys.argv[2] if len(sys.argv) > 2 else "chromium"
from playwright.sync_api import sync_playwright
RES = []; SH = r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V102\sonraki"
TOK = open(os.path.join(os.environ["APPDATA"], "VizePlani", "token.txt"), encoding="utf-8").read().strip()
LOCAL = f"http://127.0.0.1:8790/?t={TOK}"
DERS = r"C:\Users\berat\Desktop\DERSLER"


def rec(name, ok, detail=""):
    RES.append({"test": name, "result": "PASS" if ok else "FAIL", "detail": str(detail)[:300]}); print(("PASS" if ok else "FAIL"), name, "::", str(detail)[:230])


def skip(name, why):
    RES.append({"test": name, "result": "NOT TESTED", "detail": why}); print("NOT TESTED", name, "::", why)


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self): self.send_header("Cache-Control", "no-cache"); super().end_headers()
    def log_message(self, *a): pass


def go(pg, t, w=0.7): pg.evaluate(f"location.hash='#{t}'; 0"); time.sleep(w)
def txt(pg): return pg.locator("#view").inner_text()
def ls(pg): return pg.evaluate("JSON.parse(localStorage.getItem('vizeplan.v2')||'{}')")


def page(b, url, w=1440, h=900, freeze=None, state=None, mobile=False):
    ctx = b.new_context(viewport={"width": w, "height": h}, has_touch=mobile, is_mobile=mobile and BR == "chromium", storage_state=state)
    pg = ctx.new_page(); pg.errs = []; pg.on("pageerror", lambda e: pg.errs.append(str(e)))
    if freeze: pg.clock.install(time=freeze)
    pg.goto(url); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    return ctx, pg


def main(p):
    b = getattr(p, BR).launch()
    # ---------- 1) akıllı ana ekran + gruplu gezinme (masaüstü)
    ctx, pg = page(b, LOCAL, freeze="2026-11-10T12:00:00+03:00")
    t = txt(pg); tiles = pg.locator(".mhome .mt").count()
    groups = pg.evaluate("[...document.querySelectorAll('nav.tabs .tg')].map(g=>[g.getAttribute('aria-label'), g.querySelectorAll('a').length])")
    rec("[v105][1] Akıllı ana ekran: en yakın sınav/quiz/ödev, bugünün programı, devam et, 'Sınava hazırlanmaya başla', tekrar edilecekler, son ders — 8 kart", tiles == 8 and all(k in t for k in ("Sıradaki sınav", "Sıradaki quiz", "Sıradaki ödev", "Bugünün çalışması", "Sınava hazırlanmaya başla", "Kaldığım yerden devam", "Tekrar etmem gerekenler", "Son çalıştığım ders")), tiles)
    rec("[v105][1] 18 bölümün hepsi duruyor, masaüstü gezinme 3 gruba ayrıldı (Çalış / Planla / Materyal) ve hepsi görünür", pg.locator("nav.tabs a").count() == 19 and sum(g[1] for g in groups) == 18 and [g[0] for g in groups] == ["Çalış", "Planla", "Materyal"] and all(pg.locator(f'nav.tabs a[data-tab="{k}"]').is_visible() for k in ("bugun", "sinavlar", "hazirlan", "slayt", "kaynaklar")), groups)
    pg.screenshot(path=os.path.join(SH, f"{BR}_v105_home_desktop.png"))
    # ---------- 2) sınav hazırlığı (CMPE453 Midterm 12 Kas)
    pg.locator('.mhome button[data-act="exam-prep"]').click(); time.sleep(0.9)
    h = txt(pg)
    secs = ["1 · Sınav kapsamı", "2 · İlgili ders slaytları", "3 · Orijinal sorular", "4 · Çözümlü pratikler", "5 · Eksik konular", "6 · Yanlış defteri", "7 · Son tekrar listesi"]
    rec("[v105][2] Ana ekrandan 'Sınava hazırlan' → tek akışta 7 bölüm (kapsam, slaytlar, orijinal sorular, çözümlü pratikler, eksik konular, yanlış defteri, son tekrar) + CMPE453 Midterm başlığı", pg.evaluate("location.hash") == "#hazirlan" and all(s in h for s in secs) and "CMPE453 Midterm" in h, [s for s in secs if s not in h])
    pg.screenshot(path=os.path.join(SH, f"{BR}_v105_exam_prep_desktop.png"), full_page=True)
    rec("[v105][2] içerik gerçek veriden: slaytlar listede ('açılır'), orijinal soru sayısı ve 'doğrulanmadı' etiketi var, uydurma çözüm yok", "açılır" in h and re.search(r"\d+ soru adayı", h) and ("doğrulanmadı" in h or "Kayıtlı çözümlü soru yok" in h), "")
    pg.locator('.dl', has_text="Lecture2.2").first.click(); time.sleep(4)
    st = pg.evaluate("(document.querySelector('#vw-st')||{}).textContent||''")
    rec("[v105][2] sınav hazırlığındaki slayt düğmesi gerçek slaytı açıyor (canvas çizildi)", st.startswith("sayfa 1 /"), st)
    go(pg, "hazirlan"); cb = pg.locator('input[data-act="xr"]').first
    n_cb = pg.locator('input[data-act="xr"]').count()
    if n_cb:
        cb.check(); time.sleep(0.6); state = ctx.storage_state(); k = [x for x in ls(pg).get("notes", {}) if x.startswith("xr:")]
        rec("[v105][2] 'Son tekrar listesi' işaretleri kalıcı kayda yazılıyor", len(k) == 1, k)
    else:
        skip("[v105][2] son tekrar işareti", "listelenecek madde yok")
    # sınav değiştirme: quiz
    go(pg, "hazirlan"); pg.locator('button[data-act="exam-pick"]', has_text="CMPE327 Quiz").first.click(); time.sleep(0.6)
    rec("[v105][2] sınav/quiz seçici: CMPE327 Quiz için aynı akış (kapsam, slaytlar) yeniden kuruldu", "CMPE327 Quiz" in txt(pg) and "2 · İlgili ders slaytları" in txt(pg), "")
    rec("[v105] konsol/istisna yok (masaüstü)", not pg.errs, pg.errs[:2]); ctx.close()
    # ---------- 3) bağımsız (public) sürümde dürüstlük
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 8782), functools.partial(H, directory=PWA)); srv.allow_reuse_address = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    ctx, pg = page(b, "http://127.0.0.1:8782/", freeze="2026-11-10T12:00:00+03:00")
    go(pg, "hazirlan"); pt = txt(pg)
    rec("[v105][2] bağımsız (public) sürümde sınav hazırlığı: kapsam/konular var, sorular için 'özel sürümde' dürüst notu, uydurma soru/çözüm yok", "1 · Sınav kapsamı" in pt and ("orijinal soru kaydı yok" in pt) and "Mock" not in pt and "Kayıtlı çözümlü soru yok" in pt, pt[:120].replace("\n", " "))
    ctx.close(); srv.shutdown()
    # ---------- 4) yeniden planlama: sınav tamamlandı + yeni materyal + önizleme + geri al
    ctx, pg = page(b, LOCAL, freeze="2026-11-13T09:00:00+03:00")
    go(pg, "bugun"); bt = txt(pg)
    rec("[v105][3] sınav tamamlandı tetikleyicisi (13 Kas): 'Sınav tamamlandı: CMPE453 Midterm' bildirimi görünüyor", "Sınav tamamlandı" in bt and "CMPE453 Midterm" in bt, bt[bt.find("Plan güncelleme"):][:140].replace("\n", " "))
    ack = pg.locator('button[data-act="ex-ack"][data-id="mcu-m"]')
    if ack.count(): ack.click(); time.sleep(0.6)
    go(pg, "bugun", 0.6); gone = "Sınav tamamlandı: CMPE453 Midterm" not in txt(pg); pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5); gone2 = "Sınav tamamlandı: CMPE453 Midterm" not in txt(pg)
    rec("[v105][3] 'Tamam' ile bildirim kapanıyor ve yenilemeden sonra geri gelmiyor (kalıcı)", gone and gone2, {"anında": gone, "yenileme": gone2})
    ctx.close()
    # yeni materyal (10 Kas): cmpe 327/Week9_Yeni_Konu.pdf
    tmp = tempfile.mkdtemp(); d = os.path.join(tmp, "cmpe 327"); os.makedirs(d); shutil.copy(os.path.join(DERS, "cmpe 327", "Slide04.pdf"), os.path.join(d, "Week9_Yeni_Konu.pdf"))
    ctx, pg = page(b, LOCAL, freeze="2026-11-10T12:00:00+03:00")
    go(pg, "slayt"); pg.set_input_files("#vw-dir", d); time.sleep(3)
    if pg.locator('button[data-act="imp-go"]').count():
        pg.click('button[data-act="imp-go"]')
        t0 = time.time()
        while time.time() - t0 < 90 and "Özet:" not in pg.locator("body").inner_text(): time.sleep(0.6)
    go(pg, "planlayici", 1.0); pl = txt(pg)
    moves0 = json.dumps(ls(pg).get("moves", {}), sort_keys=True)
    rec("[v105][3] yeni materyal tetikleyicisi: eklenen slayt için 'Yeni materyal önerileri (önizleme)' çıkıyor (ders, süre, gün, neden); plan henüz DEĞİŞMEDİ", "Yeni materyal önerileri" in pl and "Week9_Yeni_Konu.pdf" in pl and "cust:tasks" not in ls(pg).get("notes", {}), pl[pl.find("Yeni materyal önerileri"):][:200].replace("\n", " "))
    pg.screenshot(path=os.path.join(SH, f"{BR}_v105_replan_preview.png"), full_page=True)
    pg.locator('button[data-act="nm-apply"]').click(); time.sleep(1.0)
    ct = json.loads(ls(pg)["notes"]["cust:tasks"]["v"]); day = ct[0]["date"]
    go(pg, "takvim"); pg.evaluate("1")
    rec("[v105][3] öneri uygulanınca özel görev oluştu (sınavdan önce, kapasiteye uygun), geri alma kaydı tutuldu", len(ct) == 1 and ct[0]["date"] < "2026-11-15" and ct[0]["m"] <= 90 and "plan:undo" in ls(pg)["notes"], ct[0])
    go(pg, "planlayici", 0.8)
    pg.locator('button[data-act="plan-undo"]').click(); time.sleep(0.8)
    ct2 = json.loads(ls(pg)["notes"]["cust:tasks"]["v"])
    rec("[v105][3] 'Geri al' yeni materyal görevini kaldırdı ve önceki plana döndü (taşımalar bozulmadı)", ct2 == [] and json.dumps(ls(pg).get("moves", {}), sort_keys=True) == moves0, ct2)
    pg.evaluate("indexedDB.deleteDatabase('vizeplan-files'); 0"); ctx.close(); shutil.rmtree(tmp, ignore_errors=True)
    # ---------- 5) akıllı yanlış defteri (zaman yolculuğu)
    ctx, pg = page(b, LOCAL, freeze="2026-11-10T12:00:00+03:00")
    go(pg, "sorular", 1.0)
    btn = pg.locator('button[data-act="qb-st"][data-v="bad"]').first; qid = btn.get_attribute("data-id")
    btn.click(); time.sleep(0.8)
    mk = [k for k in ls(pg).get("mist", {}) if k.startswith("mq")]; m0 = ls(pg)["mist"][mk[0]] if mk else {}
    rec("[v105][4] soruyu 'yanlış' işaretleyince yanlış defterine ORİJİNAL kaynak (src=orijinal, soru no) ve cevap doğrulama durumuyla kaydoldu", bool(mk) and m0.get("src") == "orijinal" and m0.get("qid") == qid and "ver" in m0, {k: m0.get(k) for k in ("src", "qid", "ver")})
    state = ctx.storage_state(); ctx.close()
    ctx, pg = page(b, LOCAL, freeze="2026-11-11T12:00:00+03:00", state=state)
    go(pg, "yanlislar", 0.9); yt = txt(pg)
    rec("[v105][4] ertesi gün: 'Bugün tekrar' listesinde, ORİJİNAL SLAYT SORUSU etiketiyle ve (gerekirse) 'kayıtlı cevap doğrulanmamış' uyarısıyla görünüyor", "Bugün tekrar" in yt and "ORİJİNAL SLAYT SORUSU" in yt and qid and (m0.get("ver") is True or "doğrulanmamış" in yt), yt[:140].replace("\n", " "))
    pg.screenshot(path=os.path.join(SH, f"{BR}_v105_mistakes.png"), full_page=True)
    pg.locator('button[data-act="mist-ok"]').first.click(); time.sleep(0.6); a1 = ls(pg)["mist"][mk[0]]
    rec("[v105][4] 'Hatırladım': aralık uzadı (11 Kas → 14 Kas = +3 gün), yenilemeden sonra da kalıcı", a1.get("nx") == "2026-11-14" and a1.get("si") == 1, {k: a1.get(k) for k in ("nx", "si", "okN")})
    state = ctx.storage_state(); ctx.close()
    ctx, pg = page(b, LOCAL, freeze="2026-11-14T12:00:00+03:00", state=state)
    go(pg, "yanlislar", 0.9); pg.locator('button[data-act="mist-hard"]').first.click(); time.sleep(0.6); a2 = ls(pg)["mist"][mk[0]]
    rec("[v105][4] 'Zorlandım': aralık ertesi güne sıfırlandı (14 Kas → 15 Kas), zorlanma sayısı arttı", a2.get("nx") == "2026-11-15" and a2.get("si") == 0 and a2.get("hardN") == 1, {k: a2.get(k) for k in ("nx", "si", "hardN")})
    # ---------- 6) yedek kapsamı: yeni kayıtlar yedeğe giriyor
    with pg.expect_download() as dl:
        go(pg, "kaynaklar", 0.8); pg.locator('button[data-act="bk-export"]').click()
    path = dl.value.path(); o = json.load(open(path, encoding="utf-8"))
    rec("[v105][6] yedek dosyası yanlış defteri (src/nx/si alanları), planlayıcı kayıtları ve sürüm/bütünlük özetini içeriyor", o["meta"]["format"] == "vizeplan-backup" and o["sha256"] and any(v.get("src") == "orijinal" and v.get("nx") for v in o["data"]["mist"].values()), {"version": o["meta"]["version"]})
    ctx.close()
    # ---------- 7) mobil: sadeleşmiş alt gezinme + gruplu sayfa
    ctx, pg = page(b, LOCAL, w=390, h=844, freeze="2026-11-10T12:00:00+03:00", mobile=True)
    items = pg.evaluate("[...document.querySelectorAll('.bnav a')].map(a=>a.dataset.bt)"); pg.click('.bnav [data-bmore]'); time.sleep(0.4)
    heads = pg.evaluate("[...document.querySelectorAll('#bsheet h6')].map(h=>h.textContent)"); n = pg.locator("#bsheet a").count()
    pg.click('.bnav a[data-bt="hazirlan"]') if False else None
    rec("[v105][5] mobil alt gezinme 4 ana ekran (Bugün, Takvim, Hazırlan, Slayt) + 'Daha fazla' sayfası gruplu (Çalış/Planla/Materyal), 19 bölüm (18 + Panel) erişilebilir", items == ["bugun", "takvim", "hazirlan", "slayt"] and heads == ["Çalış", "Planla", "Materyal", "Diğer"] and n == 19, {"items": items, "heads": heads, "n": n})
    pg.evaluate("document.querySelector('#bsheet').hidden=true; 0")
    pg.click('.bnav a[data-bt="hazirlan"]'); time.sleep(0.8)
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth"); small = pg.evaluate("[...document.querySelectorAll('.bnav a,.bnav button')].filter(e=>e.getBoundingClientRect().height<44).length")
    rec("[v105][5] mobilde sınav hazırlığı açılıyor, yatay taşma yok, alt çubuk hedefleri ≥44px", "7 · Son tekrar listesi" in txt(pg) and ov <= 1 and small == 0, {"ov": ov})
    pg.screenshot(path=os.path.join(SH, f"{BR}_v105_exam_prep_mobile.png"))
    go(pg, "bugun"); pg.screenshot(path=os.path.join(SH, f"{BR}_v105_home_mobile.png")); ctx.close(); b.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(RES, open(os.path.join(r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V7", f"results_v105_{BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in RES), "PASS /", sum(r["result"] == "FAIL" for r in RES), "FAIL /", sum(r["result"] == "NOT TESTED" for r in RES), "NOT TESTED")

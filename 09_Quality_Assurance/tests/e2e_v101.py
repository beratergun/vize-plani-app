# -*- coding: utf-8 -*-
"""V10.1: dosya ekle → otomatik aç, yerel kütüphane otomatik açılış, başlangıç ekranı, yenileme, eksik dosya, çoklu dosya/klasör, kalıcı klasör (OPFS ile).
Her adımda GERÇEK canvas çizimi doğrulanır (yalnızca 'dosya seçildi' mesajı PASS sayılmaz).
Önkoşul: 8765 statik + 8790 yerel sunucu. Kullanım: py e2e_v101.py [chromium|webkit]"""
import sys, os, json, time, base64, shutil, tempfile
import e2e_core as T
from e2e_core import rec, skip, sync_playwright, SHOTS
from e2e_viewer import canvas_state
from e2e_slide import until, STATIC, LOCAL, TOK, stage_text
from e2e_studio import wait_page

D = T.DERS
S04 = os.path.join(D, "cmpe 327", "Slide04.pdf")
L22 = os.path.join(D, "cmpe 453", "Lecture2.2 (1).pdf")
SEG = os.path.join(D, "cmpe 453", "7 segment.pdf")
BIO1 = r"C:\Users\berat\Desktop\ders\1st week slides_.pdf"


def drawn(pg, n=None, t=60, doc=None):
    cond = (" && document.querySelector('#vw-f') && document.querySelector('#vw-f').value === " + json.dumps(doc)) if doc else ""
    ok = until(pg, "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \\d+ \\/ \\d+/.test(e.textContent)" + cond + " ? e.textContent : ''})()", t)
    cs = canvas_state(pg)
    return bool(ok) and bool(cs) and cs["ink"] > 3 and (n is None or ok.startswith(f"sayfa {n} /")), ok


def sel(pg):
    return pg.evaluate("[document.querySelector('#vw-c1')&&document.querySelector('#vw-c1').value, document.querySelector('#vw-f')&&document.querySelector('#vw-f').value]")


def fresh(p, url, w=1500, init=None):
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": w, "height": 900})
    if init: ctx.add_init_script(init)
    pg = ctx.new_page(); pg.errs = []; pg.on("pageerror", lambda e: pg.errs.append(str(e))); pg.goto(url); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    return b, ctx, pg


def main(p):
    # ---- A) Tek dosya: Slayt sekmesindeyken PDF ekle → otomatik açılır
    b, ctx, pg = fresh(p, STATIC)
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.8)
    home = pg.locator('[data-home]').count()
    txt0 = pg.locator("#view").inner_text()
    rec(f"[{T.BR}][v101] başlangıç ekranı (dosya yokken): Derslerim / bağlantı durumu / belgeler, 'Bir ders ve dosya seç' boş ekranı YOK", home == 1 and "Derslerim" in txt0 and "Kütüphane bağlantı durumu" in txt0 and "Bir ders ve dosya seç" not in txt0 and "Yerel kütüphane bağlı değil" in txt0, txt0[:100].replace("\n", " "))
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v101_home_static.png"))
    pg.set_input_files("#vw-files", L22)
    ok, st = drawn(pg, 1)
    body = pg.locator("body").inner_text()
    rec(f"[{T.BR}][v101][A] tek PDF eklendi → otomatik açıldı, 1. sayfa canvas'ta çizildi (ek ders/belge seçimi yok)", ok and sel(pg) == ["CMPE453", "Lecture2.2 (1).pdf"] and pg.evaluate("location.hash") == "#slayt", {"durum": st, "seçim": sel(pg)})
    rec(f"[{T.BR}][v101][A] eski 'depoya eklendi / ayrıca doğrulanır' mesajı YOK; başarı mesajı render sonrası", "ayrıca doğrulan" not in body and "depoya eklendi" not in body, "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v101_A_single.png"))
    # ---- E) yenile: aynı belge+sayfa, dosya yeniden eklemeden (tarayıcı deposu)
    pg.fill("#vw-p", "3"); pg.press("#vw-p", "Enter"); wait_page(pg, 3, 30); time.sleep(0.5)
    pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    ok, st = drawn(pg, 3)
    rec(f"[{T.BR}][v101][E] yenileme: Lecture2.2 sayfa 3 kaldığı yerden otomatik açıldı (dosya eklenmeden)", ok, {"durum": st, "seçim": sel(pg)})
    # ---- B) indeksli dosya: Slide04 → CMPE327 + doğru belge otomatik
    pg.set_input_files("#vw-files", S04)
    ok, st = drawn(pg, 1, 90, "Slide04.pdf")
    rec(f"[{T.BR}][v101][B] CMPE327 Slide04.pdf eklendi → ders ve belge otomatik seçildi, sayfa çizildi / 33", ok and sel(pg) == ["CMPE327", "Slide04.pdf"] and "/ 33" in st, {"durum": st, "seçim": sel(pg)})
    rec(f"[{T.BR}][v101] konsol/istisna yok (A,B,E)", not pg.errs, pg.errs[:2]); b.close()

    # ---- F) eksik kaynak: ana ekran → belge seç → açık hata, OCR/sahte slayt yok
    b, ctx, pg = fresh(p, STATIC)
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.6)
    pg.locator('[data-home] button[data-act="vw-hcourse"]', has_text="CMPE327").first.click(); time.sleep(0.5)
    pg.locator('[data-home] .dl', has_text="Slide04.pdf").first.click(); time.sleep(1.5)
    rec(f"[{T.BR}][v101][F] dosya yokken belge seçimi: 'Orijinal slayt dosyası bağlı değil', sahte/OCR slayt yok, canvas yok", pg.locator("[data-noslide]").count() == 1 and "Orijinal slayt dosyası bağlı değil" in stage_text(pg) and canvas_state(pg) is None and pg.locator(".card169").count() == 0, stage_text(pg)[:80].replace("\n", " "))
    b.close()

    # ---- G) klasör: farklı derslerden birden çok dosya + indekste olmayan dosya
    tmp = tempfile.mkdtemp(); root = os.path.join(tmp, "DERSLER")
    for rel, src in [("cmpe 327/Slide04.pdf", S04), ("cmpe 453/Lecture2.2 (1).pdf", L22), ("bio/1st week slides_.pdf", BIO1), ("diger/zzz_indekste_yok.pdf", SEG)]:
        dst = os.path.join(root, *rel.split("/")); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(src, dst)
    b, ctx, pg = fresh(p, STATIC)
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.6)
    pg.set_input_files("#vw-dir", root)
    ok, st = drawn(pg, 1, 90)
    first = sel(pg)
    rec(f"[{T.BR}][v101][G] 4 dosyalı klasör: ilk dosya otomatik açıldı (tüm belgeler aynı anda render EDİLMEDİ)", ok and first[1] in ("Slide04.pdf", "Lecture2.2 (1).pdf", "1st week slides_.pdf") and pg.locator("#vw-c").count() == 1 and {"Slide04.pdf": "CMPE327", "Lecture2.2 (1).pdf": "CMPE453", "1st week slides_.pdf": "BIO110"}[first[1]] == first[0], {"durum": st, "seçim": first})
    # başka derse geç, dosya eklemeden
    pg.select_option("#vw-c1", label="CMPE453"); time.sleep(0.5)
    txt = pg.locator("#view").inner_text()
    pg.locator('[data-home] .dl', has_text="Lecture2.2 (1).pdf").first.click(); ok2, st2 = drawn(pg, 1)
    rec(f"[{T.BR}][v101][G] CMPE453'e geç → belge listesinde 'açılır'; seçince tekrar dosya eklemeden çizildi", "açılır" in txt and ok2 and sel(pg)[0] == "CMPE453", {"durum": st2})
    pg.select_option("#vw-c1", label="BIO110"); time.sleep(0.5)
    pg.locator('[data-home] .dl', has_text="1st week slides_.pdf").first.click(); ok3, st3 = drawn(pg, 1)
    rec(f"[{T.BR}][v101][G] BIO110 belgesi doğru derse eşleşti ve çizildi (/ 51)", ok3 and "/ 51" in st3 and sel(pg)[0] == "BIO110", {"durum": st3})
    pg.select_option("#vw-c1", label="CMPE327"); time.sleep(0.4)
    rec(f"[{T.BR}][v101][G] indekste olmayan dosya sessizce atlanmadı: ana ekranda adıyla bildiriliyor", "zzz_indekste_yok.pdf" in pg.locator("#view").inner_text(), "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v101_G_home_after_dir.png"))
    keys = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result.sort())}})")
    rec(f"[{T.BR}][v101][G] depoya yalnızca indeksli 3 dosya yazıldı (yanlış derse bağlama yok)", keys == ["1st week slides_.pdf", "Lecture2.2 (1).pdf", "Slide04.pdf"], keys)
    b.close(); shutil.rmtree(tmp, ignore_errors=True)

    # ---- yanlış dosya (aynı ad, farklı sayfa sayısı): bağlanmaz, canvas yok
    tmp = tempfile.mkdtemp(); wrong = os.path.join(tmp, "Slide04.pdf"); shutil.copy(L22, wrong)
    b, ctx, pg = fresh(p, STATIC); pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.5)
    pg.set_input_files("#vw-files", wrong); time.sleep(4)
    keys = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result)}})")
    rec(f"[{T.BR}][v101] yanlış içerikli 'Slide04.pdf' (sayfa sayısı uyuşmuyor): depoya alınmadı, yanlış sayfa çizilmedi", keys == [] and canvas_state(pg) is None and "uyuşmuyor" in pg.locator("body").inner_text(), keys)
    b.close(); shutil.rmtree(tmp, ignore_errors=True)

    # ---- D) yerel kütüphane: dosya seçmeden
    b, ctx, pg = fresh(p, f"{LOCAL}/?t={TOK}")
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(1.5)
    t = pg.locator("#view").inner_text()
    rec(f"[{T.BR}][v101][D] yerel başlatıcı: ana ekranda 'Yerel kütüphane bağlı', dosya yükleme butonları kapalı bölümde", pg.locator('[data-home]').count() == 1 and "Yerel kütüphane bağlı" in t and pg.evaluate("!document.querySelector('[data-home] details').open"), t[:120].replace("\n", " "))
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v101_D_home_local.png"))
    pg.locator('[data-home] button[data-act="vw-hcourse"]', has_text="CMPE327").first.click(); time.sleep(0.4)
    pg.locator('[data-home] .dl', has_text="Slide04.pdf").first.click(); ok, st = drawn(pg, 1)
    pg.fill("#vw-p", "26"); pg.press("#vw-p", "Enter"); ok26, st26 = drawn(pg, 26)
    rec(f"[{T.BR}][v101][D] hiçbir dosya eklemeden CMPE327 → Slide04 → sayfa 26 gerçek canvas (26 / 33)", ok and ok26 and "/ 33" in st26, {"1": st, "26": st26})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v101_D_local_p26.png"))
    n = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result.length)}})")
    rec(f"[{T.BR}][v101][D] tarayıcı depolamasına dosya yazılmadı (akışla açıldı)", n == 0, n)
    # ---- C) kütüphane derin bağlantı: Slide04 s.26 (arama → Slaytı aç)
    pg.evaluate("location.hash='#kutuphane'; 0"); time.sleep(0.6); pg.fill("#lib-q", "of DFA and NFA: i 1,31"); time.sleep(1.2)
    hit = pg.locator("#lib-res .qi").filter(has_text="Slide04.pdf").filter(has_text="s.26"); nh = hit.count()
    if nh: hit.first.locator('button[data-act="vw-open"]').click(); ok, st = drawn(pg, 26)
    else: ok, st = False, "sonuç yok"
    rec(f"[{T.BR}][v101][C] Kütüphane araması → CMPE327 Slide04 s.26 → GERÇEK sayfa canvas'ta (26 / 33)", ok and "/ 33" in st, {"sonuç": nh, "durum": st})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v101_C_slide04_p26.png"))
    # ---- E) yerel: sayfa değiştir + yenile → aynı belge/sayfa otomatik
    pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
    ok, st = drawn(pg, 26, 60)
    rec(f"[{T.BR}][v101][E] yerel kütüphane + yenileme: CMPE327 Slide04 sayfa 26'dan otomatik devam (ana ekranda beklemeden)", ok and sel(pg) == ["CMPE327", "Slide04.pdf"], {"durum": st, "seçim": sel(pg)})
    # ---- H) sunum: F, ok, zoom, küçük resim
    pg.evaluate("document.activeElement&&document.activeElement.blur(); 0"); pg.keyboard.press("f"); time.sleep(0.8)
    full = pg.evaluate("!!document.querySelector('.vw.full')"); pg.keyboard.press("ArrowRight"); r1 = wait_page(pg, 27, 30)
    w0 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width"); pg.keyboard.press("+"); time.sleep(1.5); w1 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    cs = canvas_state(pg); pg.keyboard.press("Escape"); time.sleep(0.8)
    pg.click('#vw-th .th[data-p="5"]'); r2 = wait_page(pg, 5, 30)
    rec(f"[{T.BR}][v101][H] sunum modu (F), → sonraki sayfa, + zoom, Esc, küçük resimle gezinme — hepsi gerçek canvas üzerinde", full and bool(r1) and w1 > w0 and cs and cs["ink"] > 3 and bool(r2), {"w0": w0, "w1": w1})
    rec(f"[{T.BR}][v101] konsol/istisna yok (D,E,H)", not pg.errs, pg.errs[:2]); b.close()

    # ---- I) kalıcı klasör bağlantısı (OPFS, gerçek showDirectoryPicker yerine): bağla → aç → yenile → izin onay/otomatik
    data = base64.b64encode(open(S04, "rb").read()).decode()
    INIT = """(()=>{ if (!navigator.storage || !navigator.storage.getDirectory) return; window.showDirectoryPicker = async () => { const root = await navigator.storage.getDirectory(); const dir = await root.getDirectoryHandle('vp-test-' + (window.__fsaN||'a'), {create:true}); return dir; }; })()"""
    try:
        b, ctx, pg = fresh(p, STATIC, init=INIT)
        has = pg.evaluate("!!(navigator.storage && navigator.storage.getDirectory)")
        if not has or T.BR == "webkit":
            skip(f"[{T.BR}][v101][I] kalıcı klasör bağlantısı", "WebKit/Safari ana iş parçacığında OPFS createWritable desteklemiyor: kalıcı klasör testi bu ortamda kurulamadı (BLOCKED), gerçek showDirectoryPicker WebKit'te zaten yok"); b.close()
        else:
            pg.evaluate("""async (b64) => { const root = await navigator.storage.getDirectory(); try { await root.removeEntry('vp-test-a', {recursive:true}); } catch(e){} const d = await root.getDirectoryHandle('vp-test-a', {create:true}); const sub = await d.getDirectoryHandle('cmpe 327', {create:true}); const f = await sub.getFileHandle('Slide04.pdf', {create:true}); const w = await f.createWritable(); const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); await w.write(bin); await w.close(); return 1; }""", data)
            pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.8)
            if not pg.evaluate("document.querySelector('[data-home] details').open"): pg.locator('[data-home] details summary').click()
            pg.locator('[data-home] button[data-act="fsa-pick"]').click(); time.sleep(2)
            pg.locator('[data-home] button[data-act="vw-hcourse"]', has_text="CMPE327").first.click(); time.sleep(0.4)
            pg.locator('[data-home] .dl', has_text="Slide04.pdf").first.click(); ok, st = drawn(pg, 1)
            rec(f"[{T.BR}][v101][I] klasör bağlama (kalıcı handle, OPFS ile simüle) → dosya ekleme olmadan Slide04 çizildi", ok and "/ 33" in st, st)
            n = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result.length)}})")
            rec(f"[{T.BR}][v101][I] bağlı klasörden açılınca dosya tarayıcı deposuna kopyalanmadı", n == 0, n)
            pg.fill("#vw-p", "9"); pg.press("#vw-p", "Enter"); wait_page(pg, 9, 30); time.sleep(0.5)
            pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2.5)
            ok, st = drawn(pg, 9, 60)
            rec(f"[{T.BR}][v101][I] yenileme sonrası kayıtlı klasör handle'ı geri yüklendi: izin varsa otomatik açılış (sayfa 9)", ok, st)
            # belirsizlik: aynı adlı iki PDF (farklı klasör) → bağlanmaz
            pg.evaluate("""async (b64) => { const root = await navigator.storage.getDirectory(); const d = await root.getDirectoryHandle('vp-test-a'); try { await d.removeEntry('cmpe 327', {recursive:true}); } catch(e){} for (const n of ['x1','x2']) { const sub = await d.getDirectoryHandle(n, {create:true}); const f = await sub.getFileHandle('Slide04.pdf', {create:true}); const w = await f.createWritable(); await w.write(Uint8Array.from(atob(b64), c => c.charCodeAt(0))); await w.close(); } return 1; }""", data)
            pg.evaluate("localStorage.clear(); 0")
            b2 = getattr(p, T.BR).launch()  # temiz profil değil: aynı bağlamda yeniden bağla
            b2.close()
            pg.goto(STATIC + "?amb=1"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
            pg.evaluate("location.hash='#slayt'; 0"); time.sleep(1)
            time.sleep(3)   # son belge otomatik açılır; klasörde aynı adlı 2 PDF var
            rec(f"[{T.BR}][v101][I] aynı adlı iki PDF (belirsiz): yanlış dosyaya bağlanmadı, açık hata", "belirsiz" in pg.locator("#view").inner_text() and canvas_state(pg) is None, stage_text(pg)[:80].replace("\n", " "))
            rec(f"[{T.BR}][v101][I] konsol/istisna yok", not pg.errs, pg.errs[:2]); b.close()
    except Exception as e:
        rec(f"[{T.BR}][v101][I] kalıcı klasör testi çalıştı", False, repr(e)[:300])


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_v101_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in T.RES: print(r["result"], r["test"], "::", str(r.get("detail"))[:200])
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

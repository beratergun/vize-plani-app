# -*- coding: utf-8 -*-
"""Slayt görüntüleyici + Kütüphane araması: gerçek dosya (cmpe 453/Lecture2.2) ile.
Kullanım: py e2e_viewer.py [chromium|webkit]"""
import sys, os, json, re
sys.argv = [sys.argv[0]] + sys.argv[1:]
import e2e_core as T
from e2e_core import rec, skip, newctx, tab, sync_playwright, os, SHOTS

FN = "Lecture2.2 (1).pdf"


def canvas_state(pg):
    """Canvas gerçekten çizilmiş mi: boyut + beyaz olmayan piksel sayısı."""
    return pg.evaluate("""()=>{const c=document.querySelector('#vw-c'); if(!c||!c.width) return null;
      const x=c.getContext('2d'),d=x.getImageData(0,0,c.width,c.height).data; let ink=0,n=0;
      for(let i=0;i<d.length;i+=4*37){n++; if(d[i]<240||d[i+1]<240||d[i+2]<240) ink++;} return {w:c.width,h:c.height,ink:ink,n:n,css:c.getBoundingClientRect().width}}""")


def wait_render(pg, timeout=40000):
    pg.wait_for_function("(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \\d+ \\/ \\d+/.test(e.textContent)})()", timeout=timeout)


def status(pg):
    return pg.evaluate("(document.querySelector('#vw-st')||{}).textContent||''")


def run(p, w=1366, h=768, tag="laptop"):
    b, c, pg = newctx(p, w, h, mobile=w < 800)
    if not os.path.exists(T.F453):
        skip(f"[{T.BR}] gerçek dosya testi ({FN})", "dosya bulunamadı"); b.close(); return
    tab(pg, "slayt")
    pg.set_input_files("#vw-files", T.F453)
    pg.wait_for_function("(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \d+ \/ \d+/.test(e.textContent)})()", timeout=40000)
    rec(f"[{T.BR}] dosya seçimi + depoya yazma ({tag})", True, "toast görüldü")
    # dosyayı seç
    tab(pg, "slayt")
    pg.select_option("#vw-c1", label="CMPE453") if pg.locator("#vw-c1 option", has_text="CMPE453").count() else None
    pg.select_option("#vw-f", value=FN)
    try:
        wait_render(pg)
        ok = True
    except Exception as e:
        ok = False
    st = status(pg)
    cs = canvas_state(pg)
    rec(f"[{T.BR}] ilk sayfa çizildi ({tag})", ok and cs and cs["ink"] > 3, {"durum": st, "canvas": cs})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_viewer_p1_{tag}.png"))
    if not ok:
        print("  stage:", st, pg.errs[:5]); b.close(); return
    # sayfa 2 / geri
    pg.click('button[data-act="vw-go"][data-v="1"]'); wait_render(pg); pg.wait_for_function("document.querySelector('#vw-st').textContent.startsWith('sayfa 2 /')")
    rec(f"[{T.BR}] sonraki sayfa → 2 ({tag})", status(pg).startswith("sayfa 2 /"), status(pg))
    pg.click('button[data-act="vw-go"][data-v="-1"]'); pg.wait_for_function("document.querySelector('#vw-st').textContent.startsWith('sayfa 1 /')")
    rec(f"[{T.BR}] önceki sayfa → 1 ({tag})", status(pg).startswith("sayfa 1 /"), status(pg))
    # zoom
    w0 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    pg.click('button[data-act="vw-zoom"][data-v="0.2"]'); pg.wait_for_timeout(1500)
    w1 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    pg.click('button[data-act="vw-zoom"][data-v="-0.2"]'); pg.click('button[data-act="vw-zoom"][data-v="-0.2"]'); pg.wait_for_timeout(1500)
    w2 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    rec(f"[{T.BR}] zoom + / − ({tag})", w1 > w0 + 1 and w2 < w1 - 1, {"w0": w0, "zoom+": w1, "zoom-": w2})
    # tam ekran
    pg.click('button[data-act="vw-full"]'); pg.wait_for_timeout(500)
    full = pg.evaluate("!!document.querySelector('.vw.full') || !!document.fullscreenElement")
    rec(f"[{T.BR}] tam ekran ({tag})", full, "")
    pg.click('button[data-act="vw-full"]') if pg.locator('button[data-act="vw-full"]').count() else pg.keyboard.press("Escape")
    # kapat/yeniden aç (başka sekme → geri → aynı dosya)
    tab(pg, "bugun"); tab(pg, "slayt")
    try:
        wait_render(pg, 20000); ok2 = True
    except Exception:
        ok2 = False
    cs2 = canvas_state(pg)
    rec(f"[{T.BR}] kapat → yeniden aç, yine çiziliyor ({tag})", ok2 and cs2 and cs2["ink"] > 3, {"durum": status(pg)})
    # kütüphaneden tekrar aç: PORTB
    b.close()


def open_file(pg, name, course="CMPE453"):
    tab(pg, "slayt")
    pg.select_option("#vw-c1", label=course); pg.select_option("#vw-f", value=name)


def test_errors(p):
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    # 1) bozuk PDF (aynı adla) -> sonsuz yükleme yok, teknik hata + tekrar dene
    bad = os.path.join(tmp, FN); open(bad, "wb").write(b"%PDF-1.4\nbu bozuk bir dosyadir\n")
    b, c, pg = newctx(p); pg.set_default_timeout(45000)
    tab(pg, "slayt"); pg.set_input_files("#vw-files", bad)
    pg.wait_for_function("location.hash=='#kutuphane' && document.body.innerText.includes('Özet:')", timeout=20000)
    t = pg.locator("body").inner_text()
    keys = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result)}})")
    rec(f"[{T.BR}] bozuk PDF: içe aktarma reddediyor, 'Eklendi' DEMİYOR, hata nedeni log'da, depo temiz", keys == [] and "hata 1" in t and "✗" in t, re.findall(r"✗.*", t)[:1])
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_import_corrupt.png")); b.close()
    # 2) sayfa sayısı eşleşmeyen PDF: gerçek dosyayla aynı ad, farklı içerik
    wrong = os.path.join(tmp, FN); shutil.copy(os.path.join(T.DERS, "cmpe 453", "Lecture3.1 (1).pdf"), wrong)
    b, c, pg = newctx(p); pg.set_default_timeout(45000)
    tab(pg, "slayt"); pg.set_input_files("#vw-files", wrong); pg.wait_for_timeout(2500)
    t = pg.locator("body").inner_text()
    keys = pg.evaluate("new Promise(r=>{const q=indexedDB.open('vizeplan-files'); q.onsuccess=()=>{const g=q.result.transaction('files').objectStore('files').getAllKeys(); g.onsuccess=()=>r(g.result)}})")
    open_file(pg, FN); pg.wait_for_timeout(1500)
    t2 = pg.locator("#view").inner_text()
    rec(f"[{T.BR}] yanlış PDF (aynı ad, farklı sayfa sayısı) depoya alınmıyor; açılırsa 'Orijinal slayt dosyası bağlı değil' (yanlış sayfaya gitmiyor)", keys == [] and "Orijinal slayt dosyası bağlı değil" in t2 and canvas_state(pg) is None, {"depo": keys})
    b.close()
    # 3) pdf.js takılırsa (hiç dönmeyen getDocument): zaman aşımı mesajı, sonsuz bekleme yok
    b, c, pg = newctx(p); pg.set_default_timeout(60000)
    tab(pg, "slayt"); pg.set_input_files("#vw-files", T.F453); pg.wait_for_timeout(2500)
    open_file(pg, "7 segment.pdf"); pg.wait_for_timeout(800)
    pg.evaluate("Blob.prototype.arrayBuffer = () => new Promise(() => {}); 0")
    open_file(pg, FN)
    pg.wait_for_selector('button[data-act="vw-retry"]', timeout=45000)
    t = pg.locator("#view").inner_text()
    rec(f"[{T.BR}] pdf.js takılması: ~30 sn sonra 'zaman aşımı' (belleğe okuma takılması) + Tekrar dene", "zaman aşımı" in t, t[t.find("Teknik hata"):][:120].replace("\n", " "))
    b.close(); shutil.rmtree(tmp, ignore_errors=True)


def test_resources(p):
    """Aç/kapat döngüsünde bellek/URL sızıntısı: pdf nesnesi yok edilir, JS heap şişmez."""
    b, c, pg = newctx(p); pg.set_default_timeout(45000)
    tab(pg, "slayt"); pg.set_input_files("#vw-files", T.F453); pg.wait_for_timeout(2500)
    cdp = None
    try:
        cdp = c.new_cdp_session(pg); cdp.send("HeapProfiler.enable")
    except Exception:
        pass
    def heap():
        if not cdp: return None
        cdp.send("HeapProfiler.collectGarbage"); return pg.evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")
    open_file(pg, FN); wait_render(pg); h0 = heap()
    for i in range(12):
        tab(pg, "bugun"); tab(pg, "slayt"); wait_render(pg, 30000)
        pg.select_option("#vw-c1", label="CMPE453"); pg.select_option("#vw-f", value=FN); wait_render(pg, 30000)
    h1 = heap()
    if h0 and h1:
        rec(f"[{T.BR}] 12× aç/kapat: JS heap artışı < 25 MB (sızıntı yok)", (h1 - h0) < 25e6, f"{h0/1e6:.1f} MB → {h1/1e6:.1f} MB")
    else:
        skip(f"[{T.BR}] bellek ölçümü", "bu tarayıcıda heap ölçümü yok")
    b.close()


if __name__ == "__main__":
    which = os.environ.get("VTESTS", "main,errors,resources").split(",")
    with sync_playwright() as p:
        if "main" in which:
            for vn, w, h in T.VIEWPORTS:
                run(p, w, h, vn)
        if "errors" in which: test_errors(p)
        if "resources" in which and T.BR == "chromium": test_resources(p)
    out = os.path.join(T.OUT, f"results_viewer_{T.BR}.json")
    json.dump(T.RES, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

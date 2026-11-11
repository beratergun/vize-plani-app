# -*- coding: utf-8 -*-
"""Slayt alanında YALNIZCA orijinal sayfa; dosya yoksa sahte slayt yok. Önkoşul: yerel sunucu (--port 8790) ve 8765 statik sunucu (10_Website).
Kullanım: py e2e_slide.py [chromium|webkit] [all]   (all: 82 belgenin hepsini aç)"""
import sys, os, json, time
import e2e_core as T
from e2e_core import rec, skip, sync_playwright, SHOTS
from e2e_viewer import canvas_state

LOCAL = os.environ.get("VP_BASE", "http://127.0.0.1:8790")
STATIC = "http://127.0.0.1:8765/index.html"
TOK = open(os.path.join(os.environ["APPDATA"], "VizePlani", "token.txt"), encoding="utf-8").read().strip()
ALL = "all" in sys.argv[2:]


def until(pg, js, timeout=60, step=0.4):
    t = time.time()
    while time.time() - t < timeout:
        try:
            v = pg.evaluate(js)
            if v: return v
        except Exception:
            pass
        time.sleep(step)
    return None


ST = "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \\d+ \\/ \\d+/.test(e.textContent) ? e.textContent : ''})()"


def open_doc(pg, course, fname, page=1):
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.5)
    pg.select_option("#vw-c1", label=course); time.sleep(0.4); pg.select_option("#vw-f", value=fname); time.sleep(0.6)
    if page != 1:
        pg.fill("#vw-p", str(page)); pg.press("#vw-p", "Enter"); time.sleep(0.8)


def stage_text(pg):
    return pg.evaluate("(document.querySelector('#vw-cv')||{}).innerText||''")


def main(p):
    # --- A) dosya YOK (Artifact benzeri: statik sayfa, IDB boş): sahte slayt yok, açık hata var
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(STATIC); pg.wait_for_selector("nav.tabs a", state="attached")
    open_doc(pg, "CMPE327", "Slide04.pdf", 26)
    time.sleep(1.2)
    ns = pg.locator("[data-noslide]").count()
    st = stage_text(pg)
    pg.click('button[data-act="vw-tab"][data-v="metin"]'); time.sleep(0.4)
    ext = pg.evaluate("(document.querySelector('.sbody .pgtxt')||{}).textContent||''")
    words = [w for w in ext.replace("⟦OCR⟧", " ").split() if len(w) > 5][:6]
    rec(f"[{T.BR}][slide] dosya yokken (CMPE327 Slide04 s.26): açık hata gösteriliyor", ns == 1 and "Orijinal slayt dosyası bağlı değil" in st, st[:90].replace("\n", " "))
    rec(f"[{T.BR}][slide] dosya yokken: slayt alanında OCR/çıkarılmış metin YOK, sahte slayt kartı YOK", pg.locator(".card169").count() == 0 and not any(w in st for w in words) and bool(words), {"kontrol edilen kelimeler": words})
    rec(f"[{T.BR}][slide] metin katmanı ayrı panelde ('Metin' sekmesi, 'slayt DEĞİL' etiketli); slayt alanında değil", "slayt DEĞİL" in pg.locator(".study").inner_text() and "slayt DEĞİL" not in stage_text(pg), "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_slide04_p26_dosya_yok.png"))
    # PPTX dosyası da yok -> aynı açık hata
    open_doc(pg, "CMPE421", "Ch.3.pptx", 1); time.sleep(0.8)
    rec(f"[{T.BR}][slide] PPTX bağlı değil: açık hata, sahte slayt yok", pg.locator("[data-noslide]").count() == 1 and pg.locator(".card169").count() == 0 and "Orijinal slayt dosyası bağlı değil" in stage_text(pg), "")
    b.close()
    # --- B) dosya VAR (yerel kütüphane): gerçek sayfa
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1500, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
    open_doc(pg, "CMPE327", "Slide04.pdf", 26)
    st = until(pg, ST, 60); cs = canvas_state(pg)
    rec(f"[{T.BR}][slide] CMPE327 Slide04.pdf s.26: GERÇEK sayfa çizildi (pdf.js canvas), 26 / 33", bool(st) and st.startswith("sayfa 26 / 33") and cs and cs["ink"] > 3 and pg.locator("[data-noslide]").count() == 0, {"durum": st, "ink": cs and cs["ink"]})
    sx = stage_text(pg).replace("‹", "").replace("›", "").strip()   # ‹ › = gezinme okları
    rec(f"[{T.BR}][slide] gerçek slayt alanında yalnızca canvas + sayfa sayacı (başka metin yok)", sx == st.strip() or sx.replace("\n", "") == st.replace("\n", ""), sx[:80])
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_slide04_p26_gercek.png"))
    # sayfa atla / önceki-sonraki / zoom / fit / fullscreen / klavye
    pg.click('button[data-act="vw-go"][data-v="-1"]'); until(pg, "(document.querySelector('#vw-st')||{}).textContent==='sayfa 25 / 33'", 30)
    rec(f"[{T.BR}][slide] önceki → 25", "sayfa 25 / 33" in pg.evaluate("document.querySelector('#vw-st').textContent"), "")
    pg.keyboard.press("ArrowRight"); until(pg, "(document.querySelector('#vw-st')||{}).textContent==='sayfa 26 / 33'", 30)
    rec(f"[{T.BR}][slide] klavye → ile 26'ya dönüş", "sayfa 26 / 33" in pg.evaluate("document.querySelector('#vw-st').textContent"), "")
    w0 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    pg.click('button[data-act="vw-zoom"][data-v="0.2"]'); time.sleep(1.5); w1 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    pg.click('button[data-act="vw-fit"]'); time.sleep(1.5); w2 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    rec(f"[{T.BR}][slide] zoom + ve 'Sığdır' (gerçek canvas üzerinde)", w1 > w0 + 1 and abs(w2 - w0) < 3, {"fit": w0, "zoom": w1, "fit2": w2})
    pg.click('button[data-act="vw-full"]'); time.sleep(0.8)
    rec(f"[{T.BR}][slide] tam ekran/sunum modu", pg.evaluate("!!document.querySelector('.vw.full')"), "")
    pg.click('button[data-act="vw-full"]'); time.sleep(0.5)
    rec(f"[{T.BR}][slide] konsol/istisna yok", not errs, errs[:2])
    # DOCX (çizilemez): açık hata
    open_doc(pg, "CMPE453", "CMPE453_Syllabus_2026_Fall_VMidTerm.docx", 1); time.sleep(1.2)
    rec(f"[{T.BR}][slide] DOCX: 'slayt olarak çizilemez' açık hata, sahte slayt yok", "slayt olarak çizilemez" in stage_text(pg) and pg.locator(".card169").count() == 0, stage_text(pg)[:80].replace("\n", " "))
    # --- C) tüm belgeler (gerçek render)
    if ALL:
        info = pg.evaluate("[...document.querySelectorAll('#vw-c1 option')].map(o=>o.textContent)")
        bad, n_ok, n_doc = [], 0, 0
        for course in info:
            pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.3); pg.select_option("#vw-c1", label=course); time.sleep(0.5)
            files = pg.evaluate("[...document.querySelectorAll('#vw-f option')].filter(o=>o.value).map(o=>[o.value,o.textContent])")
            for f, label in files:
                if f.lower().endswith(".docx"): continue
                n_doc += 1
                pg.select_option("#vw-f", value=f)
                st = until(pg, ST, 90)
                exp = int(label.rsplit("(", 1)[1].split(")")[0]) if "(" in label else 0
                good = bool(st) and f"/ {exp}" in st and pg.locator("[data-noslide]").count() == 0 and canvas_state(pg) is not None
                if good: n_ok += 1
                else: bad.append((course, f, st, pg.locator("[data-noslide] h3").all_inner_texts()[:1]))
        rec(f"[{T.BR}][slide] TÜM PDF/PPTX belgeler gerçek sayfa olarak render edildi ({n_ok}/{n_doc}); sahte slayt yok", not bad, bad[:5])
    b.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_slide_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

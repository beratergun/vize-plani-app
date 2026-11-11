# -*- coding: utf-8 -*-
"""Katı CSP altında (eval YOK, harici script YOK, yalnızca blob/data görsel, worker-src blob:) uçtan uca.
Not: Playwright'ın wait_for_function'ı eval kullandığı için bu dosyada yalnızca click/evaluate/locator beklemesi kullanılır; CSP gevşetilmez.
Kullanım: py csp_server.py 8777  (ayrı süreç) ; py e2e_csp.py chromium|webkit"""
import sys, os, json, re, zipfile, tempfile, time
import e2e_core as T
from e2e_core import rec, sync_playwright, SHOTS
URL = "http://127.0.0.1:8777/index.html"
FN = "Lecture2.2 (1).pdf"


def until(pg, js, timeout=40, step=0.4):
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
    b = getattr(p, T.BR).launch()
    c = b.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    pg = c.new_page(); viol = []
    pg.on("console", lambda m: viol.append(m.text[:200]) if ("Content Security Policy" in m.text or "violates" in m.text) else None)
    pg.on("pageerror", lambda e: viol.append("PE " + str(e)[:200]))
    pg.goto(URL); pg.wait_for_selector("nav.tabs a", state="attached")
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.5)
    pg.set_input_files("#vw-files", T.F453)
    until(pg, "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \d+ \/ \d+/.test(e.textContent)})()", 40)
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.5)
    pg.select_option("#vw-c1", label="CMPE453"); pg.select_option("#vw-f", value=FN)
    st = until(pg, "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \\d+ \\/ \\d+/.test(e.textContent) ? e.textContent : ''})()", 40)
    ink = pg.evaluate("""()=>{const c=document.querySelector('#vw-c'); if(!c||!c.width) return -1; const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data; let k=0; for(let i=0;i<d.length;i+=148){ if(d[i]<240||d[i+1]<240) k++ } return k}""")
    rec(f"[{T.BR}][CSP] PDF.js + gömülü worker + canvas: ilk sayfa çiziliyor", bool(st) and ink > 3, {"durum": st, "ink": ink})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_csp_viewer.png"))
    pg.click('button[data-act="vw-go"][data-v="1"]'); st2 = until(pg, "(document.querySelector('#vw-st')||{}).textContent.startsWith('sayfa 2 /')")
    rec(f"[{T.BR}][CSP] sayfa 2'ye geçiş", bool(st2), "")
    w0 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    pg.click('button[data-act="vw-zoom"][data-v="0.2"]'); time.sleep(1.5)
    w1 = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width")
    rec(f"[{T.BR}][CSP] zoom", w1 > w0 + 1, {"w0": w0, "w1": w1})
    # yedek indirme (blob URL / download)
    pg.evaluate("location.hash='#kaynaklar'; 0"); time.sleep(0.5)
    try:
        with pg.expect_download(timeout=15000) as dl:
            pg.click('button[data-act="bk-export"]')
        path = os.path.join(tempfile.gettempdir(), "csp_bk.json"); dl.value.save_as(path)
        o = json.load(open(path, encoding="utf-8"))
        rec(f"[{T.BR}][CSP] yedek indirme (blob URL) çalışıyor, geçerli JSON", o["meta"]["format"] == "vizeplan-backup", os.path.getsize(path))
    except Exception as e:
        rec(f"[{T.BR}][CSP] yedek indirme", False, str(e)[:200])
    # küçük ZIP içe aktarma (DecompressionStream)
    tmp = tempfile.mkdtemp(); zp = os.path.join(tmp, "mini.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(T.F421, "cmpe 421/Ch.3.pdf")
    pg.evaluate("location.hash='#kutuphane'; 0"); time.sleep(0.5)
    pg.set_input_files('input[data-act="imp-files"] >> nth=0', zp); time.sleep(1.5)
    pg.click('button[data-act="imp-go"]')
    summ = until(pg, "(document.body.innerText.match(/Özet:[^\\n]*/)||[''])[0]", 40)
    rec(f"[{T.BR}][CSP] ZIP içe aktarma (Ch.3.pdf, 56 sayfa doğrulama)", bool(summ) and "eklenen 1" in summ and "hata 0" in summ, summ)
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_csp_zip.png"))
    rec(f"[{T.BR}][CSP] CSP ihlali / yakalanmamış istisna yok", not viol, viol[:3])
    b.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_csp_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

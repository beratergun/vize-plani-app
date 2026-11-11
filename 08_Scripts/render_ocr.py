# -*- coding: utf-8 -*-
"""Boş/az metinli sayfaları pdf.js ile GERÇEK olarak render eder, Windows.Media.Ocr ile okur.
OCR çıktısı 'ocr_text.json' (yerel, herkese açık depoya girmez). OCR güvenilirliği düşüktür: formül/diyagram/kod
görsellerini yalnızca OCR metnine dayanarak yorumlamayın (uygulamada 'OCR (düşük güvenilirlik)' etiketli)."""
import os, sys, json, base64, subprocess, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LIB = os.path.join(ROOT, "11_Library")
VEND = os.path.join(ROOT, "08_Scripts", "vendor")
TMP = r"C:\Users\berat\AppData\Local\Temp\ocr_png"; os.makedirs(TMP, exist_ok=True)
DESK = r"C:\Users\berat\Desktop"
inv = json.load(open(os.path.join(LIB, "inventory_scan.json"), encoding="utf-8"))["files"]
OUT = os.path.join(LIB, "ocr_text.json")
ocr = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}


def pdf_for(f):
    if f["src"] not in ("DERSLER", "ders"):
        return None
    base = DESK + "\\" + ("DERSLER" if f["src"] == "DERSLER" else "ders") + "\\" + f["rel"].replace("/", "\\")
    if f["ext"] == ".pdf":
        return None if f["rel"].startswith("_pdf_donusum") or f["rel"].startswith("_Vize") else base
    if f["ext"] == ".pptx":
        stem = os.path.splitext(f["rel"])[0]
        c = DESK + "\\DERSLER\\_pdf_donusum\\" + stem.replace("/", "\\") + ".pdf" if f["src"] == "DERSLER" else DESK + "\\DERSLER\\_pdf_donusum\\ders\\" + os.path.basename(stem) + ".pdf"
        if f["src"] == "DERSLER":   # cmpe 421/Ch.3.pptx -> _pdf_donusum/cmpe 421/Ch.3.pdf
            c = DESK + "\\DERSLER\\_pdf_donusum\\" + stem.replace("/", "\\") + ".pdf"
        return c if os.path.exists(c) else None
    return None


jobs = []
for f in inv:
    pth = pdf_for(f)
    tc = os.path.join(LIB, "text_cache", f["sha"][:16] + ".json")
    if not pth or not os.path.exists(tc):
        continue
    if "linz" in f["name"].lower():   # 700+ sayfalık ders kitabı: boş sayfaları kitap yapısı, OCR gerekmez
        continue
    pages = json.load(open(tc, encoding="utf-8"))
    need = [i + 1 for i, t in enumerate(pages) if len(t.strip()) < 60 and f["sha"][:16] + ":" + str(i + 1) not in ocr]
    if need:
        jobs.append((f, pth, need))
print("OCR iş:", len(jobs), "dosya,", sum(len(j[2]) for j in jobs), "sayfa", flush=True)
if "--count" in sys.argv:
    sys.exit()

HTML = "<!doctype html><meta charset=utf8><canvas id=c></canvas>"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    cur = {"path": None}
    def handler(r):
        u = r.request.url
        if "/doc.pdf" in u:
            r.fulfill(path=cur["path"], content_type="application/pdf")
        else:
            r.fulfill(body=HTML, content_type="text/html")
    pg.route("http://x.local/**", handler)
    pg.goto("http://x.local/")
    pg.add_script_tag(path=os.path.join(VEND, "pdf.min.js")); pg.add_script_tag(path=os.path.join(VEND, "pdf.worker.min.js"))
    lst = []
    for f, pth, need in jobs:
        cur["path"] = pth
        n = pg.evaluate("""async()=>{ if (window.__d) { try { await window.__d.destroy() } catch(e) {} } const r = await fetch('/doc.pdf?'+Date.now()); const buf = await r.arrayBuffer(); window.__d = await pdfjsLib.getDocument({data:buf, isEvalSupported:false}).promise; return window.__d.numPages }""")
        for pno in need:
            if pno > n:
                continue
            data = pg.evaluate("""async(p)=>{ const pgx = await window.__d.getPage(p); const v0 = pgx.getViewport({scale:1}); const sc = Math.min(3, 1800 / v0.width); const v = pgx.getViewport({scale:sc});
                const c = document.getElementById('c'); c.width = v.width; c.height = v.height; const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0,0,c.width,c.height);
                await pgx.render({canvasContext:x, viewport:v}).promise; return c.toDataURL('image/png').split(',')[1] }""", pno)
            png = os.path.join(TMP, f["sha"][:16] + "_" + str(pno) + ".png")
            open(png, "wb").write(base64.b64decode(data)); lst.append((png, f["sha"][:16] + ":" + str(pno)))
        print("render", f["name"], len(need), flush=True)
    b.close()
# OCR (Windows)
B = 40
for k in range(0, len(lst), B):
    part = lst[k:k + B]; lp = os.path.join(TMP, "list.txt"); op = os.path.join(TMP, "out.json")
    open(lp, "w", encoding="utf-8").write("\n".join(x[0] for x in part))
    if os.path.exists(op): os.remove(op)
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(ROOT, "08_Scripts", "ocr_batch.ps1"), lp, op], timeout=900)
    res = json.load(open(op, encoding="utf-8-sig"))
    for png, key in part:
        t = res.get(png, "")
        ocr[key] = {"t": t.strip(), "err": t.startswith("__OCR_ERR__")}
    json.dump(ocr, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print("ocr", k + len(part), "/", len(lst), flush=True)
print("bitti")

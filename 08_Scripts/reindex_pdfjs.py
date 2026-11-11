# -*- coding: utf-8 -*-
"""Sayfa sayısı pdftotext ile pdf.js arasında UYUŞMAYAN PDF'leri, görüntüleyicinin gördüğü sayfa yapısıyla (pdf.js) yeniden indeksler.
Kullanım: py reindex_pdfjs.py "QuantifyingUncertainty.pdf" ...   library.json + text_cache güncellenir; OCR anahtarları bu dosya için silinir."""
import sys, os, json
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LIB = os.path.join(ROOT, "11_Library"); VEND = os.path.join(ROOT, "08_Scripts", "vendor")
DESK = r"C:\Users\berat\Desktop\DERSLER"
names = sys.argv[1:]
L = json.load(open(os.path.join(LIB, "library.json"), encoding="utf-8"))
ocr_p = os.path.join(LIB, "ocr_text.json"); ocr = json.load(open(ocr_p, encoding="utf-8")) if os.path.exists(ocr_p) else {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); cur = {"f": None}
    pg.route("http://x.local/**", lambda r: r.fulfill(path=cur["f"], content_type="application/pdf") if "doc.pdf" in r.request.url else r.fulfill(body="<canvas id=c>", content_type="text/html"))
    pg.goto("http://x.local/"); pg.add_script_tag(path=os.path.join(VEND, "pdf.min.js")); pg.add_script_tag(path=os.path.join(VEND, "pdf.worker.min.js"))
    for d in L["docs"]:
        if d["file"] not in names:
            continue
        cur["f"] = os.path.join(DESK, d["path"].replace("/", os.sep))
        txt = pg.evaluate("""async()=>{const r=await fetch('/doc.pdf?'+Date.now());const b=await r.arrayBuffer();const doc=await pdfjsLib.getDocument({data:b,isEvalSupported:false}).promise;const o=[];for(let i=1;i<=doc.numPages;i++){const g=await doc.getPage(i);const t=await g.getTextContent();let s='',y=null;for(const it of t.items){ if(y!==null && Math.abs(it.transform[5]-y)>3) s+='\\n'; else if(s&&!s.endsWith('\\n')) s+=' '; s+=it.str; y=it.transform[5]; }o.push(s)}return o}""")
        print(d["file"], "indeks", d["pages"], "->", len(txt))
        for k in [k for k in ocr if k.startswith(d["sha"][:16] + ":")]:
            del ocr[k]
        d["pages"] = len(txt); d["text"] = txt; d["empty"] = [i + 1 for i, t in enumerate(txt) if len(t.strip()) < 5]
        json.dump(txt, open(os.path.join(LIB, "text_cache", d["sha"][:16] + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    b.close()
json.dump(L, open(os.path.join(LIB, "library.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(ocr, open(ocr_p, "w", encoding="utf-8"), ensure_ascii=False)
print("bitti")

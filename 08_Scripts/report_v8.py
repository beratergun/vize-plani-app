# -*- coding: utf-8 -*-
"""Gömülü DATA'dan (artifact_page.html) envanter raporu üretir -> 09_Quality_Assurance/INVENTORY_REPORT_V8.md"""
import json, re, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = open(os.path.join(ROOT, "10_Website", "artifact_page.html"), encoding="utf-8").read()
i = h.index("const DATA = ") + len("const DATA = "); dec = json.JSONDecoder(); D, _ = dec.raw_decode(h[i:])
inv = D["inv"]; sc = inv["scan"]
L = ["# V8 envanter raporu (gerçek dosyalardan)", "", f"Taranan gerçek dosya (DERSLER + ders; çevrilmiş PDF kopyaları ve proje klasörü hariç): **{sc['disk']}** PDF/PPTX/DOCX, {sc['bytes']/1048576:.0f} MB.",
     f"DERSLER.zip: {sc['zip']['DERSLER.zip']['files']} dosya; SHA-256'ya göre diskte olmayan: **{sc['zip']['DERSLER.zip']['miss']}**. Mükerrer (aynı SHA): 0. PPTX→PDF: {sc['converted']}/{sc['pptx']}.",
     f"Dizinde olmayan gerçek dosyalar: {sc['not_indexed'] or 'yok'}", "", "| Ders | Dosya | Slayt/sayfa | Metni okunan | OCR (≥30 kr) | OCR zayıf | Okunamayan görsel | Soru adayı | Doğrulanan | İnceleme gerek | PPTX→PDF |", "|---|---|---|---|---|---|---|---|---|---|---|"]
T = collections.Counter()
for c, x in sorted(inv["courses"].items()):
    L.append(f"| {c} | {x['files']} | {x['slides']} | {x['proc']} | {x['ocr']} | {x['ocrw']} | {x['ocre']} | {x['q']} | {x['qv']} | {x['qn']} | {x['conv']} |")
    for k in ("files", "slides", "proc", "ocr", "ocrw", "ocre", "q", "qv", "qn", "conv"):
        T[k] += x[k]
L.append(f"| **Toplam** | {T['files']} | {T['slides']} | {T['proc']} | {T['ocr']} | {T['ocrw']} | {T['ocre']} | {T['q']} | {T['qv']} | {T['qn']} | {T['conv']} |")
L += ["", "## Konu denetimi (tam metin + OCR)", ""] + [f"- **{t['c']} · {t['t']}** — {t['s']}: {t['n']}" for t in inv["topics"]]
L += ["", "## Notlar", "- OCR: Windows.Media.Ocr (Türkçe motor), düşük güvenilirlik; formül/diyagram/kod görsellerini OCR metnine dayanarak yorumlama.",
      "- Okunamayan görsel = OCR boş döndü; içeriği slayttan okuman gerekir.", "- Soru adayı sayısı 'Soru değil' (False Positive) hariç."]
open(os.path.join(ROOT, "09_Quality_Assurance", "INVENTORY_REPORT_V8.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))

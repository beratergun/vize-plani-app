# -*- coding: utf-8 -*-
"""Eksik denen konuları TÜM kaynakların sayfa metninde ara (dosya adına değil). Çıktı: 11_Library/topic_audit.json"""
import json, os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LIB = os.path.join(ROOT, "11_Library")
inv = json.load(open(os.path.join(LIB, "inventory_scan.json"), encoding="utf-8"))["files"]
docs = []
for f in inv:
    p = os.path.join(LIB, "text_cache", f["sha"][:16] + ".json")
    if os.path.exists(p):
        docs.append((f["src"] + "/" + f["rel"], f["course"], json.load(open(p, encoding="utf-8"))))
OCR = os.path.join(LIB, "ocr_text.json")
ocr = json.load(open(OCR, encoding="utf-8")) if os.path.exists(OCR) else {}
TOPICS = {
 "CMPE327 Myhill–Nerode": r"myhill|nerode|distinguishable|indistinguishab",
 "CMPE327 Derivatives (Brzozowski/regex)": r"derivative of|brzozowski|derivatives? of (a )?(regular|language)|\bD_a\b",
 "CMPE327 CFG (context-free grammar)": r"context[- ]free grammar|\bCFG\b|context-free languages?",
 "CMPE327 Ambiguity": r"ambigu",
 "CMPE371 CTFT (continuous-time Fourier)": r"CTFT|continuous[- ]time fourier|fourier transform",
 "CMPE453 ADC": r"\bADC\b|analog[- ]to[- ]digital|ADMUX|ADCSRA|ADCH",
 "CMPE453 Interrupt": r"interrupt|\bISR\b|INT0|EIMSK|sei\(\)|TIMER\d?_COMP|vect",
 "BIO110 genel": r"campbell|macromolecule|membrane|chemical context|polarity|electronegativ",
}
res = {}
for t, rx in TOPICS.items():
    r = re.compile(rx, re.I); hits = {}
    for name, course, pages in docs:
        for i, tx in enumerate(pages):
            if r.search(tx):
                hits.setdefault(name, []).append(i + 1)
    for k, tx in ocr.items():   # OCR metni (düşük güvenilirlik) ayrı sayılır
        pass
    res[t] = {"files": {k: {"pages": v[:30], "n": len(v)} for k, v in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:12]}, "total_pages": sum(len(v) for v in hits.values())}
json.dump(res, open(os.path.join(LIB, "topic_audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for t, v in res.items():
    print("==", t, "| sayfa:", v["total_pages"])
    for k, h in list(v["files"].items())[:5]:
        print("   ", k, h["n"], h["pages"][:8])

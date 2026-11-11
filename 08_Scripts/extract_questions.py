# -*- coding: utf-8 -*-
"""library.json -> 11_Library/questions.json + AUDIT.md.
Sayfa metninden soru adayları çıkarır (kural tabanlı; model yok). Her kayıt kaynak dosya + sayfa taşır.
Güven: 'yüksek' = sayfada Quiz/Exercise/Question/Problem/Practice vb. başlık/etiket var; 'orta' = emir/soru kalıbı var.
Doğrulama durumu hep 'otomatik – gözden geçirilmedi'; resmi cevap yalnızca kaynakta varsa yazılır (burada çıkarılmadı).
Görsel/boş sayfalar 'Needs Visual Review' sayılır. Hiçbir soru uydurulmaz."""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LIB = os.path.join(ROOT, "11_Library", "library.json")
TAG = re.compile(r"\b(worked example|quiz|exercises?|questions?|homework|your turn|pop quiz|try it|assignment)\b", re.I)
TAG_BAD = re.compile(r"^questions?\?$|decision problem|membership question|question:\s*is|why study|course catalog", re.I)
IMPER = re.compile(r"^\s*(?:example\s*\d*\s*[:.\-]\s*)?(?:\(?[0-9a-z]{1,2}[.)]\s+)?(construct|design|find|draw|convert|minimi[sz]e|determine|compute|calculate|trace|write|show that|prove|give|simplify|develop|build|implement|create|modify|program|derive|solve|list|compare|given|suppose)\b\b", re.I)
QLINE = re.compile(r"^\s*(?:\(?[0-9a-z]{1,2}[.)]\s+)?(what|which|how many|how big|how much|how|why|is|are|can|does|do)\b.*\?\s*$", re.I)
CHOICE = re.compile(r"^\s*\(?[A-Ea-e][.)]\s+\S")
CODE = re.compile(r"(#include|int main|PORT[A-D]|DDR[A-D]|PIN[A-D]|UBRR|ADMUX|OCR|TCCR|_delay_ms)")
NOISE = re.compile(r"^(what|how|why) (is|are) (the|a|an) (point|goal|idea|difference)", re.I)


def qtype(t):
    if re.search(r"true or false|true/false|\bT/F\b", t, re.I):
        return "true_false"
    if sum(1 for ln in t.split("\n") if CHOICE.match(ln)) >= 2:
        return "multiple_choice"
    if CODE.search(t):
        return "code"
    if re.search(r"\b(trace|simulate|run .* on)\b", t, re.I):
        return "algorithm_trace"
    if re.search(r"\b(calculate|compute|find the|how many|evaluate|solve)\b", t, re.I):
        return "calculation"
    if re.search(r"\b(explain|describe|why|define|compare|what is)\b", t, re.I):
        return "concept"
    if re.search(r"\b(construct|design|draw|convert|minimi[sz]e|prove|show that|derive)\b", t, re.I):
        return "design_or_proof"
    return "exercise"


def lines_of(page):
    out = []
    for ln in page.split("\n"):
        ln = re.sub(r"\s+", " ", ln).strip()
        if ln:
            out.append(ln)
    return out


def main():
    L = json.load(open(LIB, encoding="utf-8"))
    qs, perfile = [], {}
    seen = {}
    for d in L["docs"]:
        kind = "kitap" if "LINZ" in d["file"].upper() else "syllabus" if "syllabus" in d["file"].lower() else "mock" if "mock" in d["file"].lower() else "materyal"
        st = dict(file=d["file"], course=d["course"], kind=kind, pages=d["pages"], scanned=0, text=0, little=0, empty=0, q=0, visual=0, errors=0)
        if kind in ("kitap", "syllabus", "mock"):
            st["scanned"] = d["pages"] if kind != "kitap" else 0
            st["note"] = {"kitap": "ders kitabı: soru çıkarımı yapılmadı (bölüm sonu soruları ayrı iş)", "syllabus": "idari belge", "mock": "hocanın örnek sınavı: sorular elle aktarıldı"}[kind]
            for t in d["text"]:
                n = len("".join(t.split()))
                st["text" if n >= 40 else "little" if n >= 8 else "empty"] += 1
            perfile[d["path"]] = st
            continue
        for i, page in enumerate(d["text"], start=1):
            st["scanned"] += 1
            n = len("".join(page.split()))
            if n < 8:
                st["empty"] += 1; st["visual"] += 1; continue
            if n < 40:
                st["little"] += 1
            else:
                st["text"] += 1
            ls = lines_of(page)
            title = ls[0] if ls else ""
            tagged = bool(TAG.search(title)) and not TAG_BAD.search(title)
            cands = [k for k, ln in enumerate(ls) if 20 <= len(ln) <= 260 and (IMPER.match(ln) or QLINE.match(ln)) and not NOISE.match(ln) and (QLINE.match(ln) or ln.endswith((".", ":", "?")) or d["course"] == "CMPE453") and (k > 0 or IMPER.match(ln))]
            if not tagged and not cands:
                continue
            if "quiz" in title.lower() or re.search(r"\b(exercises?|questions?|problems?|practice)\b", title, re.I):
                conf = "yüksek"
            elif tagged and cands:
                conf = "yüksek"
            elif cands:
                conf = "orta"
            else:
                conf = "düşük"
            if conf == "düşük":
                continue
            txt = "\n".join(ls[:14])[:700]
            h = hashlib.sha1(re.sub(r"\W+", "", txt.lower()).encode()).hexdigest()[:12]
            rec = dict(id=f"Q{len(qs) + 1:04d}", course=d["course"], file=d["file"], page=i, title=title[:90], text=txt, type=qtype(page), conf=conf, kind=("çözümlü örnek" if re.search(r"worked example", title, re.I) else "soru"),
                       status="otomatik – gözden geçirilmedi", answer=None, dup_of=seen.get(h))
            seen.setdefault(h, rec["id"])
            if n < 120:
                rec["note"] = "az metin: görsel içerik olabilir (Needs Visual Review)"
            qs.append(rec); st["q"] += 1
        perfile[d["path"]] = st
    out = os.path.join(ROOT, "11_Library")
    json.dump(dict(questions=qs, files=perfile), open(os.path.join(out, "questions.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    tot = Counter()
    for st in perfile.values():
        for k in ("pages", "scanned", "text", "little", "empty", "q", "visual"):
            tot[k] += st[k]
    L2 = ["# Materyal denetimi (yerel; herkese açık depoya konmaz)", "",
          f"Dosya: {len(perfile)} · sayfa: {tot['pages']} · taranan: {tot['scanned']} (kitap hariç) · metin≥40 kar.: {tot['text']} · az metin (8–39): {tot['little']} · boş/görsel (<8): {tot['empty']} · soru adayı: {tot['q']} · gözden geçirilen: 0", "",
          "| Ders | Dosya | Tür | Sayfa | Taranan | Metinli | Az metin | Boş/görsel | Soru adayı |", "|---|---|---|---|---|---|---|---|---|"]
    for p, st in sorted(perfile.items()):
        L2.append(f"| {st['course']} | {st['file']} | {st['kind']} | {st['pages']} | {st['scanned']} | {st['text']} | {st['little']} | {st['empty']} | {st['q']} |")
    open(os.path.join(out, "AUDIT.md"), "w", encoding="utf-8").write("\n".join(L2) + "\n")
    byc = Counter((q["course"], q["conf"]) for q in qs)
    print("soru adayı:", len(qs), dict(byc), "| tekrar:", sum(1 for q in qs if q["dup_of"]))
    print("özet:", dict(tot))


if __name__ == "__main__":
    main()

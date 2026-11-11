# -*- coding: utf-8 -*-
"""DERSLER klasörü (açılmış ZIP) -> 11_Library/library.json: dosya başına sayfa/slayt metni, içerik hash'i, hata kaydı.
Kullanım: py import_slides.py <açılmış_klasör>.  Metin çıkarımı: pdftotext (PDF), python-pptx (PPTX), zipfile+XML (DOCX).
Okunamayan/boş sayfalar 'empty' olarak sayılır; metin uydurulmaz."""
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
COURSE = {"cmpe 327": "CMPE327", "cmpe 371": "CMPE371", "cmpe 421": "CMPE421", "cmpe 453": "CMPE453", "engr 490": "ENGR490", "bio": "BIO110", "bio110": "BIO110", "cmpe 499": "CMPE499"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pdf_pages(p):
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", p, "-"], capture_output=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "ignore")[:200])
    pages = r.stdout.decode("utf-8", "ignore").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pptx_pages(p):
    from pptx import Presentation
    out = []
    for s in Presentation(p).slides:
        txt = []
        for sh in s.shapes:
            try:
                if sh.has_text_frame:
                    txt.append(sh.text_frame.text)
                elif getattr(sh, "has_table", False) and sh.has_table:
                    for r in sh.table.rows:
                        txt.append(" | ".join(c.text for c in r.cells))
            except Exception:
                pass
        out.append("\n".join(x for x in txt if x.strip()))
    return out


def docx_pages(p):
    z = zipfile.ZipFile(p)
    x = ET.fromstring(z.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paras = []
    for para in x.iter("{%s}p" % ns["w"]):
        paras.append("".join(t.text or "" for t in para.iter("{%s}t" % ns["w"])))
    return ["\n".join(paras)]


def main(src):
    docs, errors = [], []
    for dp, _d, fs in os.walk(src):
        for f in sorted(fs):
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, src).replace("\\", "/")
            parts = rel.split("/")
            course = ""
            for part in parts:
                if part.lower() in COURSE:
                    course = COURSE[part.lower()]
            ext = os.path.splitext(f)[1].lower()
            try:
                pages = {".pdf": pdf_pages, ".pptx": pptx_pages, ".docx": docx_pages}[ext](full)
            except KeyError:
                errors.append([rel, "desteklenmeyen tür"]); continue
            except Exception as e:
                errors.append([rel, type(e).__name__ + ": " + str(e)[:120]]); continue
            empty = [i + 1 for i, t in enumerate(pages) if len(re.sub(r"\s+", "", t)) < 8]
            docs.append(dict(course=course, file=f, path=rel, kind=ext[1:], sha=sha(full), bytes=os.path.getsize(full), pages=len(pages), empty=empty,
                             text=[re.sub(r"[ \t]+", " ", t).strip() for t in pages]))
    out = os.path.join(ROOT, "11_Library")
    os.makedirs(out, exist_ok=True)
    json.dump(dict(docs=docs, errors=errors), open(os.path.join(out, "library.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(docs)} dosya, {sum(d['pages'] for d in docs)} sayfa/slayt, boş sayfa {sum(len(d['empty']) for d in docs)}, hata {len(errors)}")
    for e in errors:
        print("HATA", e)


if __name__ == "__main__":
    main(sys.argv[1])

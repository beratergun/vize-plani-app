# -*- coding: utf-8 -*-
"""Gerçek kaynak taraması (V8). Salt-okunur: hiçbir kaynak dosya değiştirilmez/silinmez.
Çıktı: 11_Library/inventory_scan.json (dosya envanteri + SHA-256 + ZIP karşılaştırması) ve
       11_Library/text_cache/<sha16>.json (sayfa/slayt metni; YEREL, herkese açık depoya girmez)."""
import os, sys, json, hashlib, zipfile, subprocess, re, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "11_Library")
TC = os.path.join(LIB, "text_cache")
os.makedirs(TC, exist_ok=True)
DESK = r"C:\Users\berat\Desktop"
SOURCES = [("DERSLER", os.path.join(DESK, "DERSLER"), True), ("ders", os.path.join(DESK, "ders"), False)]
SKIP_DIRS = {"_Vize_Plani_Proje"}
ZIPS = [os.path.join(DESK, "DERSLER.zip"), os.path.join(DESK, "CourseHero_10_Study_Notes.zip"), os.path.join(DESK, "CourseHero_10_Additional_Study_Notes.zip")]


def sha_stream(f):
    h = hashlib.sha256()
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)
    return h.hexdigest()


def course_of(rel):
    r = rel.lower().replace("\\", "/")
    for k, c in (("cmpe 327", "CMPE327"), ("cmpe 371", "CMPE371"), ("cmpe 421", "CMPE421"), ("cmpe 453", "CMPE453"), ("engr 490", "ENGR490"), ("cmpe453", "CMPE453"), ("cmpe 499", "CMPE499")):
        if k in r:
            return c
    return ""


def pdf_pages(path):
    try:
        out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, timeout=300).stdout.decode("utf-8", "replace")
    except Exception:
        return None
    pg = out.split("\f")
    if pg and not pg[-1].strip():
        pg = pg[:-1]
    return pg


def pptx_slides(data_path):
    """Gizli slaytlar DAHİL, sunum sırasıyla slayt metni."""
    z = zipfile.ZipFile(data_path)
    pres = z.read("ppt/presentation.xml").decode("utf8", "replace")
    rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf8", "replace")
    rid2t = dict(re.findall(r'<Relationship [^>]*?Id="([^"]+)"[^>]*?Target="([^"]+)"', rels))
    rid2t.update({a: b for b, a in re.findall(r'<Relationship [^>]*?Target="([^"]+)"[^>]*?Id="([^"]+)"', rels)})
    order = re.findall(r'<p:sldId [^>]*?r:id="([^"]+)"', pres)
    out = []
    for rid in order:
        t = rid2t.get(rid, "")
        name = "ppt/" + t.lstrip("/").replace("ppt/", "") if not t.startswith("/") else t.lstrip("/")
        try:
            x = z.read(name).decode("utf8", "replace")
        except KeyError:
            out.append(""); continue
        out.append(" ".join(re.findall(r"<a:t>([^<]*)</a:t>", x)))
    return out


def docx_text(path):
    z = zipfile.ZipFile(path)
    x = z.read("word/document.xml").decode("utf8", "replace")
    paras = re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S)
    return ["\n".join("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)) for p in paras)]


def main():
    t0 = time.time(); inv = []
    for label, base, _ in SOURCES:
        for dp, dn, fs in os.walk(base):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            for f in fs:
                if f.startswith("~$") or f == "desktop.ini":
                    continue
                p = os.path.join(dp, f); rel = os.path.relpath(p, base).replace("\\", "/")
                inv.append({"src": label, "rel": rel, "abs": p, "name": f, "ext": os.path.splitext(f)[1].lower(), "size": os.path.getsize(p), "course": course_of(rel)})
    print("diskte", len(inv), "dosya", flush=True)
    for it in inv:
        with open(it["abs"], "rb") as f:
            it["sha"] = sha_stream(f)
    # ZIP içeriği (bir kez, akışla): SHA-256
    zinfo = {}
    for zp in ZIPS:
        if not os.path.exists(zp):
            continue
        z = zipfile.ZipFile(zp); ents = []
        for i in z.infolist():
            if i.is_dir():
                continue
            with z.open(i) as f:
                ents.append({"name": i.filename, "size": i.file_size, "sha": sha_stream(f)})
        zinfo[os.path.basename(zp)] = ents
        print("zip", os.path.basename(zp), len(ents), "dosya", flush=True)
    disk_by_sha = {}
    for it in inv:
        disk_by_sha.setdefault(it["sha"], []).append(it["src"] + "/" + it["rel"])
    for it in inv:
        it["dups"] = [x for x in disk_by_sha[it["sha"]] if x != it["src"] + "/" + it["rel"]]
    # ZIP ↔ disk
    zrep = {}
    for zn, ents in zinfo.items():
        miss = [e["name"] for e in ents if e["sha"] not in disk_by_sha]
        zrep[zn] = {"files": len(ents), "bytes": sum(e["size"] for e in ents), "not_on_disk_by_sha": miss}
    # metin çıkarma
    for it in inv:
        pages = None
        try:
            if it["ext"] == ".pdf":
                pages = pdf_pages(it["abs"])
            elif it["ext"] == ".pptx":
                pages = pptx_slides(it["abs"])
            elif it["ext"] == ".docx":
                pages = docx_text(it["abs"])
        except Exception as e:
            it["err"] = str(e)[:120]
        if pages is not None:
            it["pages"] = len(pages)
            it["empty"] = sum(1 for x in pages if len(x.strip()) < 5)
            it["low"] = sum(1 for x in pages if 5 <= len(x.strip()) < 60)
            json.dump(pages, open(os.path.join(TC, it["sha"][:16] + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    # zip-only (diskte olmayan) dosyalar: CourseHero zip'leri açılmamışsa dahil et
    for zn, ents in zinfo.items():
        if zn == "DERSLER.zip":
            continue
        z = zipfile.ZipFile([p for p in ZIPS if os.path.basename(p) == zn][0])
        for e in ents:
            if e["sha"] in disk_by_sha:
                continue
            it = {"src": "zip:" + zn, "rel": e["name"], "abs": "", "name": os.path.basename(e["name"]), "ext": os.path.splitext(e["name"])[1].lower(), "size": e["size"], "course": "", "sha": e["sha"], "dups": []}
            if it["ext"] == ".pdf":
                tmp = os.path.join(LIB, "_tmp_zip.pdf"); open(tmp, "wb").write(z.read(e["name"]))
                pages = pdf_pages(tmp); os.remove(tmp)
                if pages is not None:
                    it["pages"] = len(pages); it["empty"] = sum(1 for x in pages if len(x.strip()) < 5); it["low"] = sum(1 for x in pages if 5 <= len(x.strip()) < 60)
                    json.dump(pages, open(os.path.join(TC, e["sha"][:16] + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
            inv.append(it)
    for it in inv:
        it.pop("abs", None) if it["src"].startswith("zip:") else None
    out = {"created": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": inv, "zips": zrep, "secs": round(time.time() - t0)}
    json.dump(out, open(os.path.join(LIB, "inventory_scan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("bitti", out["secs"], "sn;", len(inv), "kayıt")


if __name__ == "__main__":
    main()

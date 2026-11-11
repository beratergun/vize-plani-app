# -*- coding: utf-8 -*-
"""plan.json + progress.json + resources.py -> 10_Website/index.html (tek dosya, çevrimdışı da açılır).
Aynı dosya claude.ai'da Artifact olarak da yayımlanır (db yeteneği ile telefon-bilgisayar senkronu)."""
import json
import os
import re
from common import *
import resources as R
import questions as Q
try:
    import questions_review as QRV
except ImportError:
    QRV = None
try:
    import questions_orig as QO
    ORIG = QO.ORIG
except ImportError:
    ORIG = {}
PUBLIC = os.environ.get("PUBLIC") == "1"


def _load_expl():   # hazır (sabit) açıklamalar: özel ders materyalinden türetildiği için herkese açık sürüme KONMAZ
    if PUBLIC:
        return {}
    f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "11_Library", "explanations.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
   # herkese açık sürüm: hoca materyali (orijinal sorular, slayt başlıkları) çıkarılır
import syllabus as SY
import slides as SL
import inventory_v8 as INV8
import prep453 as P453

VIDEOS = {}
_vp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos.json")
if os.path.exists(_vp):
    VIDEOS = json.load(open(_vp, encoding="utf-8"))
GBAN = ["hindi", "in tamil", "urdu"]   # Türkçe/İngilizce dışı anlatımlar
BANV = {"M3": ["pcf8574"], "A9": ["table filling"]}   # elle ayıklanan alakasız/tekrar videolar
GRADE0 = {"BIO110": [["Midterm 1", 25], ["Midterm 2", 25], ["Proje sunumu", 20], ["Final", 30]], "CMPE371": [["Midterm", 30], ["Final", 40], ["Quiz", 15], ["Homework", 15]],
         "CMPE421": [["Homework", 30], ["Midterm", 30], ["Final", 40]], "CMPE499": [["Rapor", 70], ["Sunum", 30]], "CMPE327": [["Quiz (toplam)", 20], ["Midterm", 30], ["Final", 50]], "CMPE453": [["Midterm", 32], ["Lab (6×3)", 18], ["Final", 50]]}
GRADE = GRADE0
ASSIGN = dict(c="CMPE421", t="Assignment-1", due="2026-11-26", tm="23:59", lms="https://lms.tedu.edu.tr/mod/resource/view.php?id=16460",
              comps=[["pdf", "Assignment-1 PDF (yönerge)", "LMS kaynağı; içeriği bu ortamda okuyamadım. Gereksinimleri PDF'den buraya yapıştır."], ["code", "Code Submission", "Kod ayrı teslim; gereksinimler PDF'e göre."], ["report", "Report Submission", "Rapor ayrı teslim; gereksinimler PDF'e göre."], ["qa", "Q&A", "Zorunlu teslim mi, soru-cevap alanı mı? LMS sayfasından doğrula."]])
GAPS = {"CMPE327": "Yüklü: Slide01–07 + Linz ders kitabı. Tam metin taramasıyla DOĞRULANDI: Myhill–Nerode VAR (Slide07 + Linz s.124–132). CFG ve Ambiguity için ders slaytı yok, yalnızca Linz kitabı; Derivatives hiçbir dosyada yok (yalnızca syllabus başlığı).",
        "CMPE371": "Yüklü: 1–7 (CTFS'e kadar). CTFT (W8) dersi dosyalarda YOK (yalnızca syllabus/Introduction'da anılıyor); LMS'ten gelince ekle.",
        "CMPE421": "Yüklü: Chapter 1–11 (PPTX'ler gizli slaytlar dahil PDF'e çevrildi ve görüntülenebilir) ve ek PDF'ler. Midterm (20 Kas) kapsamı resmî duyurulmadı; Assignment-1 PDF'i LMS'te.",
        "CMPE453": "Yüklü: Lecture 0–6.2, Lab 1–3, Mock Exam. Ayrı ADC dersi YOK; Interrupt için yalnızca Lecture6.1'de SPI kesme bitleri var. Midterm (12 Kas) kapsamı W1–W7 varsayımı: ADC için Elliot Ch.7 + LMS.",
        "ENGR490": "Slaytlar yüklü (Legal Consequence, Risk Management, Sustainable Development) + 'İLK 2 HAFTA' quiz soru/cevap dosyası. Haftalık quiz tarihleri LMS'ten doğrulanmalı.",
        "BIO110": "BULUNDU (masaüstü 'ders' klasörü): 1. hafta slaytı (51 sayfa) + 2. hafta sunumu (114 slayt: makromolekül, hücre turu, zar/taşıma). Karbon/fonksiyonel grup ve metabolizma slaytı bu iki dosyada yok."}
EXTRA = [dict(c="ENGR490", n="Contemporary Issues in Engineering", info="Çarşamba 15:00–17:00. 11 quiz: hepsine katılırsan final yok (final %32 / quiz %20 / proje %13 / sunum %20); 2'den fazla quiz kaçırırsan FX. Geç teslim ve quiz telafisi yok. Quiz tarihleri bu dosyalarda yok, LMS'ten doğrula. Slaytlar: Legal Consequence, Risk Management, Sustainable Development.")]
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_template.html")
GROUP = {"L": "L", "P": "P", "R": "R", "W": "W", "V": "V", "T": "T"}


def how_for(task, blk):
    k = task["kind"]
    if k == "L":
        key = "L_BIO" if task["course"] == "BIO110" else "L_TECH"
    else:
        key = k
    prac = (blk or {}).get("practice", "")
    return [s.format(practice=prac) for s in R.HOW[key]], R.DONE.get(k, "")


def main():
    plan = load_plan()
    prog = load_progress(plan)
    links_used = {}
    LIBDOCS = SL.build()
    BF, _miss = SL.block_files(LIBDOCS)
    FT, QB, AUD = {}, [], []
    _lj = SL.load_lib()
    _qj = json.load(open(os.path.join(ROOT, "11_Library", "questions.json"), encoding="utf-8"))
    for _d in _lj["docs"]:
        if "LINZ" not in _d["file"].upper():
            FT[_d["file"]] = [" ".join(x.split())[:900] for x in _d["text"]]
    def _wk(f):
        for b, fs in SL.BLOCK_FILES.items():
            if f in fs:
                for c, rows in SY.SYL.items():
                    for w, _t, _n, bl in rows:
                        if b in bl:
                            return w
        return 0
    QB = []
    for q in _qj["questions"]:
        rv = (QRV.R.get(q["id"]) if QRV else None) or {}
        QB.append(dict(id=q["id"], c=q["course"], f=q["file"], p=q["page"], ti=q["title"], tx=q["text"][:420], ty=q["type"], cf=q["conf"], kd=q["kind"], du=q["dup_of"],
                       st=rv.get("st", "Candidate"), tp=rv.get("tp", ""), wk=_wk(q["file"]), nt=rv.get("nt", ""), an=rv.get("ans", ""), gen=rv.get("gen", "")))
    QB += INV8.engr_questions([d for d in _lj["docs"] if d.get("ex")])
    PATHS = json.load(open(os.path.join(ROOT, "11_Library", "paths.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "11_Library", "paths.json")) else {}
    _op = os.path.join(ROOT, "11_Library", "ocr_text.json")
    OCRJ = json.load(open(_op, encoding="utf-8")) if os.path.exists(_op) else {}
    _hid = json.load(open(os.path.join(ROOT, "11_Library", "hidden_slides.json"), encoding="utf-8"))
    for _l in LIBDOCS:
        _src = next((d for d in _lj["docs"] if d["file"] == _l["f"]), None)
        _l["vis"] = [i + 1 for i, t in enumerate(_src["text"]) if len("".join(t.split())) < 40] if _src and _l["k"] in ("slayt", "lab") else []
        _l["hid"] = _hid.get(_l["f"], [])
        _l["h"] = _src["sha"][:16] if _src else ""
        _l["w"] = _wk(_l["f"])
        _p = PATHS.get(_l["f"])
        if _p:
            _l["r"], _l["rp"], _l["vr"], _l["vp"] = _p["r"], _p["p"], _p["vr"], _p["vp"]
        if _src and OCRJ:
            oc, ow, oe = [], [], []
            for i in range(_l["n"]):
                o = OCRJ.get(_src["sha"][:16] + ":" + str(i + 1))
                if not o or o["err"]:
                    continue
                t = o["t"]
                if len(t) >= 30:
                    oc.append(i + 1)
                elif t:
                    ow.append(i + 1)
                else:
                    oe.append(i + 1)
                if len(t) >= 8 and _l["f"] in FT and i < len(FT[_l["f"]]):
                    FT[_l["f"]][i] = (FT[_l["f"]][i] + " ⟦OCR⟧ " + " ".join(t.split()))[:900].strip()
            _l["oc"], _l["ow"], _l["oe"] = oc, ow, oe
    AUD = [dict(c=s["course"], f=s["file"], k=s["kind"], n=s["pages"], sc=s["scanned"], tx=s["text"], lt=s["little"], em=s["empty"], q=s["q"], nt=s.get("note", "")) for s in _qj["files"].values()]
    _isc = json.load(open(os.path.join(ROOT, "11_Library", "inventory_scan.json"), encoding="utf-8"))
    INV = INV8.build(LIBDOCS, QB, _isc["files"], OCRJ, _isc["zips"])
    if PUBLIC:
        FT, QB, AUD = {}, [], []
        for _d in LIBDOCS:
            for _k in ("r", "rp", "vr", "vp", "oc", "ow", "oe"):
                _d.pop(_k, None)
            _d["t"] = []
            _d["q"] = []
            _d["vis"] = []
            _d["hid"] = []
    days = []
    for d in plan["days"]:
        tasks = []
        for t in d["tasks"]:
            blk = plan["blocks"].get(t["block"])
            item = dict(id=t["id"], c=t["course"], x=0 if t["tier"] == "core" else 1, m=t["minutes"], p=t["priority"], k=t["kind"],
                        ti=t["title"], cr=1 if t.get("critical") else 0)
            if t["kind"] == "T":
                ids = t["block"].replace("REV:", "").split(",")
                rev = []
                for b in ids:
                    bl = plan["blocks"].get(b)
                    if not bl:
                        continue
                    main_l = R.M.get(b, ([], [], [], ""))[0]
                    for lid in main_l[:1]:
                        links_used[lid] = 1
                    rev.append([bl["title"], main_l[0] if main_l else ""])
                item["rev"] = rev
                item["h"], item["dn"] = R.HOW["T"], R.DONE["T"]
            else:
                item["w"], item["pr"], item["b"] = blk["what"], blk["practice"], t["block"]
                main_l, sup, prac, yt = R.M.get(t["block"], ([], [], [], ""))
                ls = [["Ana kaynak", i] for i in main_l] + [["Destek", i] for i in sup] + [["Uygulama", i] for i in prac]
                seen, out = set(), []
                for r, i in ls:
                    if i not in seen:
                        seen.add(i)
                        out.append([r, i])
                        links_used[i] = 1
                item["l"] = out
                if yt:
                    item["yt"] = yt
                item["h"], item["dn"] = how_for(t, blk)
                if BF.get(t["block"]):
                    item["sl"] = BF[t["block"]]
                qs = [[a, b, 0] for a, b in Q.QS.get(t["block"], [])] + [[a, b, 1] for a, b in ([] if PUBLIC else ORIG.get(t["block"], []))]
                if qs:
                    item["qs"] = qs
                vids = [v for v in VIDEOS.get(t["block"], []) if not any(x in v["t"].lower() for x in BANV.get(t["block"], []) + GBAN)]
                if vids:
                    item["vd"] = [[v["id"], v["t"], v["ch"], v["d"]] for v in vids]
                if t["block"] == "V1":
                    item["v"] = [s.strip() for s in blk["what"].split(";")]
            tasks.append(item)
        days.append(dict(d=d["date"], wd=d["weekday"], g=d["goal"], ph=d["phase"], rk=d["ranking"][:3], cm=d["core_min"], em=d["ext_min"], t=tasks))
    for ids in R.COURSE_HOME.values():
        for i in ids:
            links_used[i] = 1
    evals = [dict(id=e["id"], c=e["course"], t=e["title"], d=e["date"], e=e["end"], tm=e.get("time"), s=e["status"], n=e["note"]) for e in plan["evals"] if e["date"]]
    courses = {c: dict(n=m["name"], s=m["short"], diff=m["diff"], meth=m["method"]) for c, m in plan["courses"].items() if c != "GENEL"}
    data = dict(start=plan["start"], end=plan["end"], courses=courses, evals=evals, weeks=plan["weeks"], phases=plan["phases"], days=days,
                links={k: [R.LINKS[k][0], R.LINKS[k][1], R.LINKS[k][2]] for k in links_used}, home=R.COURSE_HOME, grade=GRADE, lms=R.LMS, syl=SY.as_json(), w0=SY.W0.isoformat(), alias={d["f"]: d["f"].rsplit(".", 1)[0] + ".pdf" for d in LIBDOCS if d["f"].endswith(".pptx")}, caps=plan["caps"], lib=LIBDOCS, ft=FT, qb=QB, aud=AUD, asg=ASSIGN, extra=EXTRA, gaps=GAPS, inv=INV, prep=P453.build(PUBLIC), expl=_load_expl(),
                topics=[dict(id=b["id"], c=b["course"], t=b["title"], u=(R.M.get(b["id"], ([], [], [], ""))[0] or [""])[0]) for b in plan["blocks"].values() if b["kind"] == "L"])
    data["skip"] = [] if PUBLIC else json.load(open(os.path.join(ROOT, "11_Library", "private_skip.json"), encoding="utf-8"))   # yerel taramada atlanacak kişisel dosya adı parçaları (yalnızca özel sürümde)
    if PUBLIC:   # herkese açık paket: ders materyalinden/Mock Exam'den türetilen içerik YOK, üst veri minimum
        ex = data["prep"]["exam"]
        data["prep"] = dict(exam={k: ex[k] for k in ("date", "time", "weight") if k in ex}, topics=[], qs=[], weight=[])
        data["inv"] = dict(courses=data["inv"]["courses"], topics=[], scan={})
        data["gaps"] = {}
        data["lib"] = [d for d in data["lib"] if d.get("k") != "mock"]
        for _dd in data["days"]:
            for _t in _dd["t"]:
                if "sl" in _t:
                    _t["sl"] = [f for f in _t["sl"] if "mockexam" not in f.lower()]
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("�", "")  # bozuk karakterleri at (yayın aracı U+FFFD kabul etmez)
    if PUBLIC:
        js = re.sub(r"\s*Mock Exam PDF'i yüklendi\.", "", js)
    tpl = open(TEMPLATE, encoding="utf-8").read()
    assert "/*__DATA__*/null" in tpl
    out_dir = os.path.join(ROOT, "10_Website")
    os.makedirs(out_dir, exist_ok=True)
    vend = ""
    for _n in ("pdf.min.js", "pdf.worker.min.js"):
        _c = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", _n), encoding="utf-8").read()
        assert "</script" not in _c
        vend += "<script>/* " + _n + " (pdf.js 3.11.174, Apache-2.0, Mozilla) */\n" + _c + "\n</script>\n"
    frag = tpl.replace("/*__DATA__*/null", js).replace("<script>\nconst DATA", vend + "<script>\nconst DATA", 1)
    # Artifact için parça (doctype/html/head/body yok); yerel kullanım için tam belge
    open(os.path.join(out_dir, "artifact_page.html"), "w", encoding="utf-8").write(frag)
    path = os.path.join(out_dir, "index.html")
    open(path, "w", encoding="utf-8").write('<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + frag + "</body></html>")
    print(f"Site yazıldı: {os.path.getsize(path) // 1024} KB, {len(days)} gün, {sum(len(x['t']) for x in days)} görev, {len(links_used)} bağlantı")


if __name__ == "__main__":
    main()

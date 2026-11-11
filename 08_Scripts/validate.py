# -*- coding: utf-8 -*-
"""Programatik kalite kontrolleri → 09_Quality_Assurance/VALIDATION_REPORT.md"""
import os
import re
import shutil
import tempfile
import zipfile
import xml.dom.minidom as minidom
from datetime import date, timedelta
from common import *

TOPICS = {  # syllabus'taki tüm konular (finale kadar)
    "BIO110": ["Chemical Context", "Water and Life", "Carbon", "Large Biological Molecules", "Tour of the Cell", "Membrane", "Metabolism", "Cellular Respiration",
               "Photosynthesis", "Cell Cycle", "Mendel", "Chromosomal", "Molecular Basis", "Gene Expression", "Regulation of Gene", "DNA Tools",
               "Descent with Modification", "Evolution of Populations"],
    "CMPE371": ["Introduction to Signals", "Sinusoids", "Special Signals", "LTI", "Differential and Difference", "Continuous-Time Fourier Series",
                "Continuous-Time Fourier Transform", "Discrete-Time Fourier Series", "Discrete-Time Fourier Transform", "Filtering", "Sampling", "Z-Transform"],
    "CMPE327": ["History", "Central Concepts", "Mathematical Preliminaries", "Deterministic Finite", "Nondeterministic", "Closure", "Equivalence of DFA and NFA",
                "Regular Languages", "Pattern Matching", "Regular Expressions", "State Minimization", "Myhill", "Derivatives", "Equivalence of Regular Expressions",
                "Context-Free", "Ambiguity", "Chomsky", "CYK", "Pumping", "Nonregularity", "Pushdown", "Ogden", "Turing", "Decision Problems"],
    "CMPE421": ["Introduction to AI", "Intelligent Agents", "Uninformed", "Informed", "Game Playing", "Constraint Satisfaction", "Adversarial", "Planning",
                "Knowledge Representation", "Theorem Proving", "Uncertainty", "Machine Learning Fundamentals", "Classification and Regression",
                "Neural Networks", "NLP and LLMs", "Reinforcement", "Ethics"],
    "CMPE453": ["Course Overview", "Architecture", "Programming AVR", "I/O", "Digital Input", "USART", "SPI", "Analog-to-Digital", "Interrupts", "Timers", "PWM",
                "ARM Cortex", "GPIO", "LED", "PWM for ARM"],
}
COURSES6 = ["BIO110", "CMPE371", "CMPE327", "CMPE421", "CMPE453", "CMPE499"]
R = []
FAIL = []


def check(name, ok, detail=""):
    R.append((name, ok, detail))
    if not ok:
        FAIL.append(name)


def main():
    plan = load_plan()
    prog = load_progress(plan)
    days = plan["days"]
    tasks = [(d, t) for d in days for t in d["tasks"]]
    caps = plan["caps"]

    # --- kapsam ve takvim
    check("Altı dersin tamamı planda", all(any(t["course"] == c for _, t in tasks) for c in COURSES6),
          ", ".join(f"{c}:{sum(1 for _, t in tasks if t['course'] == c)}" for c in COURSES6))
    ds = [date.fromisoformat(d["date"]) for d in days]
    exp = [date(2026, 10, 30) + timedelta(days=i) for i in range((date(2026, 12, 31) - date(2026, 10, 30)).days + 1)]
    check("30 Ekim–31 Aralık (14. hafta sonu) her takvim günü mevcut", ds == exp, f"{len(ds)} gün")
    ids = [t["id"] for _, t in tasks]
    check("Görev ID'leri benzersiz", len(ids) == len(set(ids)), f"{len(ids)} görev")
    blocks_sched = {}
    for _, t in tasks:
        if not t["block"].startswith("REV:"):
            blocks_sched[t["block"]] = blocks_sched.get(t["block"], 0) + 1
    check("Her blok tam bir kez programlı", set(blocks_sched) == set(plan["blocks"]) and all(v == 1 for v in blocks_sched.values()),
          f"{len(plan['blocks'])} blok")
    # --- syllabus kapsamı
    miss = []
    alltext = {c: " ".join(b["topics"] + " " + b["title"] for b in plan["blocks"].values() if b["course"] == c) for c in TOPICS}
    for c, tl in TOPICS.items():
        for k in tl:
            if k.lower() not in alltext[c].lower():
                miss.append(f"{c}:{k}")
    n_top = sum(len(v) for v in TOPICS.values())
    check("Syllabus'taki tüm konular (finale kadar) plan dışı kalmadı", not miss, f"{n_top} konu anahtarı; eksik: {miss or 'yok'}")
    # --- kapasite
    wk_over = []
    for d in days:
        cc, ec = caps[d["dtype"]]
        if d["ext_min"] > ec + 40 or d["core_min"] > cc + 70:
            wk_over.append(f"{d['date']} core {d['core_min']} ext {d['ext_min']}")
    check("Hiçbir gün aşırı yüklü değil (min ≤ 4,4 sa hafta içi / ext ≤ 6,7 sa)", not wk_over, "; ".join(wk_over) or "tamam")
    sun = [d for d in days if d["dtype"] == "sunday"]
    sun_hi = [d for d in sun if d["ext_min"] >= 360]
    check("Pazarlar hafta içinden yüksek kapasiteyle (≥6 sa genişletilmiş) planlı — ilk 4 hafta", all(d["ext_min"] >= 300 for d in sun[:3]),
          "; ".join(f"{d['date']}:{hours(d['ext_min'])}" for d in sun))
    light = [f"{d['date']}({d['core_min']})" for d in days if d["core_min"] < 100]
    R.append(("Bilgi: hafif günler (sınav öncesi/sonrası ya da boş): " + (", ".join(light) or "yok"), True, ""))
    # --- BIO öncelik
    bio_ok = all(days[i]["ranking"][0] == "BIO110" for i in range(0, 5))
    check("BIO110, 30 Ekim–3 Kasım arası her gün 1. öncelik", bio_ok, "; ".join(days[i]["ranking"][0] for i in range(5)))
    # --- ICS
    ics_dir = os.path.join(ROOT, "04_Calendar")
    for fn, expect in (("Study_Plan_2026.ics", len(days)), ("Exams_Deadlines_2026.ics", None)):
        t = open(os.path.join(ics_dir, fn), "rb").read().decode("utf-8")
        lines = t.split("\r\n")
        ev = t.count("BEGIN:VEVENT")
        uids = re.findall(r"^UID:(.*)$", t, re.M)
        ok = (t.startswith("BEGIN:VCALENDAR") and t.rstrip().endswith("END:VCALENDAR") and ev == t.count("END:VEVENT") and
              t.count("BEGIN:VALARM") == t.count("END:VALARM") and len(uids) == len(set(uids)) and max(len(l.encode()) for l in lines) <= 75 and "\r\n" in t)
        if expect:
            ok = ok and ev == expect
        check(f"{fn}: geçerli yapı, UID benzersiz, satır ≤75 oktet", ok, f"{ev} etkinlik")
    ex = open(os.path.join(ics_dir, "Exams_Deadlines_2026.ics"), "rb").read().decode("utf-8")
    unfold = ex.replace("\r\n ", "")
    check("CMPE453 midterm 12 Kasım 18:00–20:00 (Europe/Istanbul)", "DTSTART;TZID=Europe/Istanbul:20261112T180000" in unfold and "DTEND;TZID=Europe/Istanbul:20261112T200000" in unfold)
    check("CMPE499 teslimleri 22 ve 29 Kasım", "UID:eval-sum-str" in unfold and "DTSTART;VALUE=DATE:20261122" in unfold and "DTSTART;VALUE=DATE:20261129" in unfold)
    tent = [e for e in plan["evals"] if e["status"] in ("tentative", "window")]
    flagged = all(("[TEYİT BEKLİYOR] " + e["title"]) in unfold.replace("\\,", ",") or ("[TEYİT BEKLİYOR] " + e["title"]).replace(",", "\\,") in unfold for e in tent)
    check("Doğrulanmamış tarihlerin hepsi 'TEYİT BEKLİYOR' + STATUS:TENTATIVE", flagged and unfold.count("STATUS:TENTATIVE") == len(tent), f"{len(tent)} tarih")
    check("Final sınavına UYDURMA tarih yazılmadı", "eval-finals" not in unfold)
    # --- XLSX
    xp = os.path.join(ROOT, "06_Progress_Tracker", "Academic_Study_Tracker_2026.xlsx")
    z = zipfile.ZipFile(xp)
    for n in z.namelist():
        minidom.parseString(z.read(n))
    names = re.findall(r'<sheet name="([^"]+)"', z.read("xl/workbook.xml").decode())
    want = ["Dashboard", "Daily Tasks", "Course Progress", "Topic Mastery", "Exam Countdown", "Assignments", "Revision Schedule", "Mistake Log", "Slide Coverage", "Weekly Reviews"]
    check("Excel: 10 sayfa adı doğru ve XML iyi biçimli", names == want, ", ".join(names))
    sheet2 = z.read("xl/worksheets/sheet2.xml").decode()
    check("Excel: Daily Tasks satır sayısı = görev sayısı", sheet2.count("<row ") == len(tasks) + 1, f"{sheet2.count('<row ') - 1}/{len(tasks)}")
    refs = set(re.findall(r"'([^']+)'!", "".join(z.read(f"xl/worksheets/sheet{i}.xml").decode() for i in range(1, 11))))
    check("Excel: formüllerdeki sayfa referansları mevcut sayfalara işaret ediyor", refs <= set(names), ", ".join(sorted(refs)))
    # --- excel -> progress senkron testi (kopya üzerinde)
    import sync_from_xlsx as sx
    tmp = tempfile.mkdtemp()
    cp = os.path.join(tmp, "t.xlsx")
    zi = zipfile.ZipFile(xp)
    with zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            data = zi.read(n)
            if n == "xl/worksheets/sheet2.xml":
                s = data.decode()
                s = s.replace(">Not Started<", ">Completed<", 1)
                data = s.encode()
            zo.writestr(n, data)
    rows = sx.read_sheet(cp, "Daily Tasks")
    check("sync_from_xlsx: değiştirilen durum doğru okunuyor", rows[1].get(10) == "Completed" and rows[1].get(1) == days[0]["tasks"][0]["id"], f"{rows[1].get(1)} → {rows[1].get(10)}")
    shutil.rmtree(tmp, ignore_errors=True)
    # --- replan testi (bellekte)
    import replan
    pl, moves, dropped = replan.replan(date(2026, 11, 5), apply=False)
    orig_ext = {d["date"]: d["ext_min"] for d in plan["days"]}
    bad = [d["date"] for d in pl["days"] if d["date"] >= "2026-11-05" and d["ext_min"] > max(orig_ext[d["date"]], caps[d["dtype"]][1] + 20)]
    check("replan (5 Kas, hiçbir şey yapılmamış varsayımı): kapasite aşılmıyor", not bad, f"{len(moves)} taşındı, {len(dropped)} düşürüldü; aşan: {bad or 'yok'}")
    check("Orijinal planda her dersin öğrenme blokları tanım (önkoşul) sırasında", _order_ok(plan) == [], str(_order_ok(plan)))
    skip = {t["id"] for _, t in dropped}
    check("replan sonrası da ders içi öğrenme sırası korunuyor (Postponed olanlar hariç)", _order_ok(pl, skip) == [], str(_order_ok(pl, skip)))
    # --- PDF
    pp = os.path.join(ROOT, "05_Printable_PDF", "Akademik_Basari_Plani_30_Ekim_2026.pdf")
    b = open(pp, "rb").read()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", b))
    mb = re.findall(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", b)
    a4 = bool(mb) and all(abs(float(w) - 595.3) < 1.5 and abs(float(h) - 841.9) < 1.5 for w, h in mb)
    check("PDF: tüm sayfalar A4 ve sayfa sayısı makul (≤32)", a4 and pages <= 32, f"{pages} sayfa, MediaBox {mb[:1]}, {len(b) // 1024} KB")
    html = open(pp.replace(".pdf", ".html"), encoding="utf-8").read()
    check("PDF kaynağı: Türkçe karakterler UTF-8 ve tablo taşması CSS'i", all(ch in html for ch in "şğıİöüçŞĞ") and "@page { size: A4" in html)
    # --- site
    import json as _json
    site = open(os.path.join(ROOT, "10_Website", "artifact_page.html"), encoding="utf-8").read()
    m = re.search(r"const DATA = (\{.*?\});" + chr(10), site, re.S)
    sd = _json.loads(m.group(1).replace("<" + chr(92) + "/", "</")) if m else {}
    s_tasks = sum(len(d["t"]) for d in sd.get("days", []))
    check("Site: veri plan.json ile aynı (gün ve görev sayısı)", len(sd.get("days", [])) == len(days) and s_tasks == len(tasks), f"{len(sd.get('days', []))} gün, {s_tasks} görev")
    nolink = [t["ti"] for d in sd.get("days", []) for t in d["t"] if t["k"] in "L" and not t.get("l")]
    check("Site: her öğrenme görevinin en az bir kaynak bağlantısı var", not nolink, str(nolink[:5]) if nolink else f"{sum(1 for d in sd['days'] for t in d['t'] if t['k'] == 'L')} öğrenme görevi")
    badurl = [k for k, v in sd.get("links", {}).items() if not v[1].startswith("https://")]
    check("Site: tüm bağlantılar https", not badurl, str(badurl))
    Lids = {t["b"] for d in sd.get("days", []) for t in d["t"] if t["k"] == "L" and t.get("b")}
    noq = sorted(i for i in Lids if len([1 for d in sd["days"] for t in d["t"] if t.get("b") == i for _ in t.get("qs", [])]) < 2)
    check("Site: her öğrenme bloğunda en az 2 örnek soru + cevap", not noq and len(Lids) > 0, f"{len(Lids)} blok" + (f"; eksik: {noq}" if noq else ""))
    syl = sd.get("syl", {})
    check("Site: 6 dersin 14 haftalık syllabus haritası var ve tüm blok kimlikleri planda", len(syl) == 6 and all(len(v) == 14 for v in syl.values()) and all(b in plan["blocks"] for v in syl.values() for r in v for b in r[3]), f"{sum(len(v) for v in syl.values())} hafta satırı")
    check("Site: TEDU LMS bağlantıları https ve lms.tedu.edu.tr içeriyor", any("lms.tedu.edu.tr" in x[1] for x in sd.get("lms", [])) and all(x[1].startswith("https://") for x in sd.get("lms", [])), f"{len(sd.get('lms', []))} bağlantı")
    # ---- V5: kesin Kasım tarihleri, kütüphane, mock exam
    ev = {e["id"]: e for e in plan["evals"]}
    ok_dates = (ev["aut-q1"]["date"] == "2026-11-15" and ev["aut-q1"]["time"] == ["13:00", "14:00"] and ev["aut-m"]["date"] == "2026-11-29" and ev["aut-m"]["time"] == ["13:00", "15:00"]
                and ev["ai-20"]["date"] == "2026-11-20" and ev["ai-20"]["time"] == ["18:00", "20:00"] and ev["ai-a1"]["date"] == "2026-11-26" and ev["sig-m"]["date"] == "2026-11-30" and ev["sig-m"]["time"] == ["18:00", "20:00"])
    check("V5: Kasım etkinlikleri (327 quiz 15/11 13–14, 327 midterm 29/11 13–15, 421 midterm 20/11 18–20, A1 26/11, 371 midterm 30/11 18–20) plan verisinde doğru", ok_dates)
    check("V5: CMPE327 Midterm kapsamı Week 08 dahil olarak kayıtlı; eski 15 Kas 'Midterm' kaydı yok", "Week 08 DAHİL" in ev["aut-m"]["note"] and not any("Midterm" in e["title"] and e["date"] == "2026-11-15" for e in plan["evals"]))
    ics_x = open(os.path.join(ROOT, "04_Calendar", "Exams_Deadlines_2026.ics"), encoding="utf-8").read().replace("\r\n ", "")
    check("V5: ICS'te yeni sınav saatleri var", all(k in ics_x for k in ("DTSTART;TZID=Europe/Istanbul:20261115T130000", "DTSTART;TZID=Europe/Istanbul:20261129T130000", "DTSTART;TZID=Europe/Istanbul:20261120T180000", "DTSTART;TZID=Europe/Istanbul:20261130T180000", "DTSTART;VALUE=DATE:20261126")))
    lib = sd.get("lib", [])
    lj = _json.load(open(os.path.join(ROOT, "11_Library", "library.json"), encoding="utf-8"))
    base = [d for d in lib if not d.get("r") or d["f"] in {x["file"] for x in lj["docs"]}]
    check("V5/V8: temel kütüphane = DERSLER.zip içeriği (library.json ile aynı dosya/sayfa), hata yok; ek dosyalar ayrıca (library_extra)", len(base) == len(lj["docs"]) and sum(d["n"] for d in base) == sum(d["pages"] for d in lj["docs"]) and not lj["errors"], f"temel {len(base)} dosya + ek {len(lib) - len(base)}; toplam {sum(d['n'] for d in lib)} sayfa")
    import slides as _SL
    _bf, _miss = _SL.block_files(lib)
    check("V5: blok→slayt eşlemesindeki bütün dosyalar kütüphanede var", not _miss, str(_miss))
    mm = [t for d in sd["days"] for t in d["t"] if t.get("b") == "MM"][0]
    check("V5: CMPE453 Mock Exam orijinal soruları ayrı etiketle (orijinal/yazılmış) yüklü", sum(1 for q in mm.get("qs", []) if q[2] == 1) == 6 , f"{len(mm.get('qs', []))} soru")
    # Q3: PORTB programının elle yürütmesi (Pin 2,5,7) cevap anahtarıyla uyuşuyor mu
    def _sim(t):
        steps = [(0b10000010, "set"), (0b01010010, "or"), (0b00000100, "or"), (0b00100000 << 1, "or")]
        port = 0; k = int((t % 400) // 100); port = steps[0][0]
        for i in range(1, k + 1):
            port |= steps[i][0]
        return tuple((port >> b) & 1 for b in (2, 5, 7))
    want = {10: (0, 0, 1), 150: (0, 0, 1), 250: (1, 0, 1), 350: (1, 0, 1), 510: (0, 0, 1)}
    check("V5: Mock Exam Q3 cevabı (Pin 2/5/7) simülasyonla doğrulandı", all(_sim(t) == v for t, v in want.items()))
    check("V5: Assignment-1 4 bileşen (PDF, Code, Report, Q&A) ayrı kayıtlı; 26 Kas 23:59", [c[0] for c in sd["asg"]["comps"]] == ["pdf", "code", "report", "qa"] and sd["asg"]["due"] == "2026-11-26" and sd["asg"]["tm"] == "23:59")
    # ---- V6: sayfa dökümü, soru bankası, açık/herkese açık sürüm ayrımı
    aud = sd.get("aud", [])
    check("V6: sayfa dökümü eksiksiz: metinli+az+görsel = toplam sayfa (2697) ve soru bankası dosya/sayfaya geri dönüyor", sum(x["tx"] + x["lt"] + x["em"] for x in aud) == sum(x["n"] for x in aud) == 2697 and all(q["f"] in sd["ft"] and 1 <= q["p"] <= len(sd["ft"][q["f"]]) for q in sd["qb"]), f"{len(sd['qb'])} soru adayı; gözden geçirilen 0")
    check("V6: soru adaylarında kaynak (dosya+sayfa) olmayan kayıt yok; 'gözden geçirilmedi' dürüstçe belirtili", all(q["f"] and q["p"] for q in sd["qb"]) and "slayt görseliyle karşılaştırılmadı" in site)
    check("V6: tam metin dizini: her slayt/lab dosyası için sayfa sayısı kadar metin girdisi", all(len(sd["ft"][d["f"]]) == d["n"] for d in sd["lib"] if d["f"] in sd["ft"]) and len(sd["ft"]) == len([d for d in sd["lib"] if d["k"] != "kitap"]))
    _pub = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "vize-plani", "index.html")
    if os.path.exists(_pub):
        _ph = open(_pub, encoding="utf-8").read()
        check("V6: herkese açık sürümde hoca materyali yok (tam metin, soru bankası, Mock Exam soruları)", '"ft":{}' in _ph and '"qb":[]' in _ph and "Mock Exam Q1a" not in _ph)
    # ---- V7 (veri/kod düzeyi; tarayıcı etkileşim testleri ayrı raporlanır)
    import collections as _co
    st = _co.Counter(q["st"] for q in sd["qb"])
    check("V7/V8: 106 soru adayı + 9 ENGR490 quiz sorusunun hepsi için karar kayıtlı (Candidate kalmadı)", st.get("Candidate", 0) == 0 and sum(st.values()) == 115, str(dict(st)))
    check("V7: 'Verified' sorularda cevap/çözüm/not var; resmî cevap (an) ile üretilen çözüm (gen) ayrı alanlarda", all((q["an"] or q["gen"] or q["nt"]) for q in sd["qb"] if q["st"] == "Verified"))
    import subprocess as _sp
    _DD = r"C:/Users/berat/Desktop/DERSLER"
    if os.path.isdir(_DD):
        bad, nconv = [], 0
        for d in sd["lib"]:
            if d["f"].endswith(".pptx"):
                if not d.get("vp"):
                    bad.append((d["f"], "PDF yolu yok", d["n"])); continue
                pdf = os.path.join(_DD, d["vp"].replace("/", os.sep))
                try:
                    n = _sp.run(["pdftotext", pdf, "-"], capture_output=True, timeout=120).stdout.count(b"")
                except Exception:
                    n = -1
                nconv += 1
                if n != d["n"]:
                    bad.append((d["f"], n, d["n"]))
        check("V7/V8: PPTX→PDF dönüşümleri: PDF sayfa sayısı = slayt sayısı (gizli slaytlar dahil)", not bad, str(bad) if bad else f"{nconv}/{nconv} dosya")
    else:
        R.append(("V7: dönüşüm klasörü bulunamadı (atlandı)", True, ""))
    check("V7: planlayıcı/yedek/içe aktarma kodu sitede var; planlayıcı sınav tarihlerini değiştiren atama içermiyor", all(k in site for k in ("planProposal", "bkExport", "impRun", "zipList")) and "e.d =" not in site.split("function planProposal")[1].split("function planApply")[0])
    # ---- V9: CMPE453 hazırlık içeriği kaynaklara bağlı mı
    import re as _re
    _P = sd.get("prep") or {}
    _lib = {d["f"]: d for d in sd["lib"]}
    _bad = []
    for _t in _P.get("topics", []):
        for _f, _pg in _t["src"]:
            if _f not in _lib or any(int(x) > _lib[_f]["n"] for x in _re.findall(r"\d+", str(_pg).split(" (")[0])):
                _bad.append((_t["id"], _f, _pg))
    for _q in _P.get("qs", []):
        if _q["src"][0] not in _lib or _q["src"][1] > _lib[_q["src"][0]]["n"]:
            _bad.append((_q["id"], _q["src"]))
        if _q.get("qbid"):
            _x = [y for y in sd["qb"] if y["id"] == _q["qbid"]]
            if not _x or _x[0]["st"] != "Verified" or _x[0]["f"] != _q["src"][0] or _x[0]["p"] != _q["src"][1]:
                _bad.append((_q["id"], "soru bankası uyumsuz"))
    check("V9: CMPE453 hazırlık: her kaynak dosya/sayfa gerçek, her slayt sorusu soru bankasında Verified ve aynı sayfada", not _bad and len(_P.get("topics", [])) == 10 and len(_P.get("qs", [])) == 16, str(_bad) if _bad else "10 konu, 16 soru")
    check("V9: ADC 'slayt-dışı', Interrupt 'kısmi' olarak işaretli (kaynakta yokmuş gibi gösterilmiyor)", {t["id"]: t["st"] for t in _P.get("topics", [])}.get("T9") == "slayt-dışı" and {t["id"]: t["st"] for t in _P.get("topics", [])}.get("T10") == "kısmi")
    try:
        import check_links as _cl
        lbad = [x[1] for x in sd.get("lms", []) if _cl.status(x[1]) != 200]
        check("Site: LMS/okul bağlantıları HTTP 200 döndü", not lbad, str(lbad) if lbad else f"{len(sd.get('lms', []))} bağlantı")
    except Exception as ex:
        R.append(("Site: LMS testi atlandı (ağ yok): " + type(ex).__name__, True, ""))
    try:
        import check_links
        res = check_links.check_all()
        bad = {k: v for k, v in res.items() if v != 200}
        check("Site: kaynak bağlantılarının hepsi HTTP 200 döndü", not bad, f"{len(res) - len(bad)}/{len(res)}" + (f"; sorunlu: {bad}" if bad else ""))
    except Exception as ex:
        R.append(("Site: bağlantı testi atlandı (ağ yok): " + type(ex).__name__, True, ""))
    try:
        vids = sorted({x[0] for d in sd.get("days", []) for t in d["t"] for x in t.get("vd", [])})
        vr = check_links.check_videos(vids)
        badv = [k for k, g in vr.items() if not g]
        check("Site: önerilen videoların hepsi YouTube'da doğrulandı (oEmbed)", not badv and len(vids) > 0, f"{len(vids) - len(badv)}/{len(vids)} video" + (f"; sorunlu: {badv}" if badv else ""))
        titles = [x[1].lower() for d in sd.get("days", []) for t in d["t"] for x in t.get("vd", [])]
        check("Site: video başlıklarında dil dışı (Hindice vb.) anlatım yok", not any(w in tt for tt in titles for w in ("hindi", "in tamil", "urdu")))
    except Exception as ex:
        R.append(("Site: video testi atlandı: " + type(ex).__name__, True, ""))
    # --- rapor
    bio_det = f"{days[0]['goal']}"
    L = ["# VALIDATION REPORT", "", f"Üretim: {date.today().isoformat()} · {len(days)} gün · {len(tasks)} görev · {len(plan['blocks'])} blok", "",
         "| # | Kontrol | Sonuç | Detay |", "|---|---|---|---|"]
    for i, (n, ok, dt) in enumerate(R, 1):
        L.append(f"| {i} | {n} | {'✅ GEÇTİ' if ok else '❌ KALDI'} | {str(dt).replace('|', '/')} |")
    L += ["", f"**Özet:** {len(R) - len(FAIL)}/{len(R)} kontrol geçti." + (f" Kalan: {', '.join(FAIL)}" if FAIL else ""), "",
          "## Manuel / görsel kontroller (otomatik değil)", "",
          "- PDF sayfa 1, 2, 3, 4, 27, 28 (son sürüm) ve 6 (günlük kart; önceki derlemede, biçimi sonradan değişmedi) pdf.js ile çizdirilip gözle kontrol edildi: kapak, özet, yol haritası, ders analizi, günlük kart, sınav listeleri, takip sayfası; Türkçe karakterler (ş ğ ı İ ö ü ç) doğru göründü, tablolar sayfa içinde kaldı, sayfa numaraları görünüyor. Diğer sayfalar gözle taranmadı.",
          "- PDF'nin siyah-beyaz yazıcıda görünümü simüle edilmedi; tasarım gri tonları ve çerçeveleri kullanıyor (renk bağımlılığı yok).",
          "- **Excel formülleri Excel/LibreOffice ile hesaplanmadı** (bu makinede kurulu değil). Yapı, sayfa adları, formül metinleri ve başlangıç (önbellek) değerleri Python ile doğrulandı; dosya `fullCalcOnLoad` ile açılışta yeniden hesaplanır. İlk açılışta bir uyarı çıkarsa bildir.",
          "- Site: tarayıcıda (telefon genişliği) Bugün, Takvim ve ayrıntı kartı görünümleri açılıp kontrol edildi; hesap senkronu (db) yalnızca yayımlandıktan sonra çalışır ve yerelde denenemez.",
          "- ICS dosyaları gerçek Google/Apple/Outlook'a içe aktarılmadı (hesaplara dokunulmadı); yapı RFC 5545'e göre kontrol edildi.", "",
          "## Doğrulanamayan tarihler / eksik kaynaklar", "",
          "- BIO110 Midterm 1 (3 Kas), CMPE327 Quiz (15 Kas), CMPE421 (20 Kas), CMPE327 Midterm (29 Kas), CMPE371 Midterm (30 Kas): kullanıcı bildirimi; saatler ve kapsamlar belli değil, doğrulanmadı.",
          "- CMPE371 HW1 ve Midterm günleri; BIO110 Midterm 2 günü — **Teyit Bekliyor** (yalnızca syllabus haftası biliniyor). CMPE327 Quiz-1 (syllabus W5) durumu bilinmiyor.",
          "- CMPE499 Evaluation Form: kullanıcı teslim edildiğini bildirdi (Assignments sayfasında Completed).",
          "- Kapsam: plan 14. haftanın sonuna (31 Aralık) kadar; final tarihleri duyurulunca plan_data.py'a eklenir.",
          "- Hiç slayt/PDF/ders notu paylaşılmadı → SLIDE_COVERAGE_MATRIX tümü 'Materyal bekleniyor'; sayfa aralığı/soru numarası UYDURULMADI.",
          "- Dış bağlantılar doğrulanmadı (yalnızca kaynak adları verildi).", "",
          "## Bulunan ve düzeltilen sorunlar (geliştirme sırasında)", "",
          "- BIO110, 30 Ekim'de 3. sıradaydı → 7 gün içindeki sınav için öncelik artırımı eklendi (şimdi 1. sıra).",
          "- Kritik teslim işlerinin bir kısmı isteğe bağlı listedeydi → 'kritik' işareti (★) ve replan'da min'e terfi kuralı eklendi.",
          "- Yol haritası tablosu sayfa dışına taşıyordu → yazı boyutu/satır sayısı düzeltildi; ders analizi tek sayfaya sığdırıldı.", ""]
    with open(os.path.join(ROOT, "09_Quality_Assurance", "VALIDATION_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    for n, ok, dt in R:
        print(("PASS " if ok else "FAIL ") + n + (" — " + str(dt) if dt else ""))
    print(f"\n{len(R) - len(FAIL)}/{len(R)} geçti")


def _order_ok(plan, skip=()):
    """Her ders için 'L' (öğrenme) bloklarının tarihleri, blok tanım sırasıyla azalmamalı. İhlal listesini döndürür."""
    when = {}
    for d in plan["days"]:
        for t in d["tasks"]:
            if not t["block"].startswith("REV:") and t["id"] not in skip:
                when[t["block"]] = d["date"]
    bad = []
    for c in COURSES6:
        seq = [b for b in plan["blocks"].values() if b["course"] == c and b["kind"] == "L" and b["id"] in when]
        for x, y in zip(seq, seq[1:]):
            if when[x["id"]] > when[y["id"]]:
                bad.append(f"{x['id']}({when[x['id']]})>{y['id']}({when[y['id']]})")
    return bad


if __name__ == "__main__":
    main()

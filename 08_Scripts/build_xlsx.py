# -*- coding: utf-8 -*-
"""plan.json + progress.json -> Academic_Study_Tracker_2026.xlsx, SLIDE_COVERAGE_MATRIX.xlsx/.csv"""
import csv
import os
from datetime import date, timedelta
from xlsxw import Workbook, serial, col_letter
from common import *

COURSE_ORDER = ["BIO110", "CMPE371", "CMPE327", "CMPE421", "CMPE453", "CMPE499"]
STATUS_LIST = '"' + ",".join(STATUSES) + '"'
TODAY_NOTE = "Excel açıldığında TODAY() ile otomatik hesaplanır."


def build():
    plan = load_plan()
    prog = load_progress(plan)
    sts = {k: v["status"] for k, v in prog["tasks"].items()}
    notes = {k: v.get("note", "") for k, v in prog["tasks"].items()}
    tasks = [(d, t) for d in plan["days"] for t in d["tasks"]]
    N = len(tasks) + 1
    wb = Workbook()
    S = wb.styles
    hdr = S.get(font=2, fill=2, border=1, wrap=1, h="center", v="center")
    cell = S.get(border=1, wrap=1, v="top")
    cellc = S.get(border=1, h="center", v="top")
    dcell = S.get(border=1, fmt="date", h="center", v="top")
    pcell = S.get(border=1, fmt="pct", h="center", v="center")
    icell = S.get(border=1, fmt="int", h="center", v="center")
    inp = S.get(border=1, fill=8, wrap=1, v="top")
    inpd = S.get(border=1, fill=8, fmt="date", h="center", v="top")
    inpp = S.get(border=1, fill=8, fmt="pct", h="center", v="top")
    title = S.get(font=3)
    sub = S.get(font=4)
    bold = S.get(font=1)
    kpi_l = S.get(font=1, fill=3, border=1, wrap=1, h="center", v="center")
    kpi_v = S.get(font=5, border=1, h="center", v="center")
    kpi_p = S.get(font=5, border=1, fmt="pct", h="center", v="center")
    dcol = S.get(border=1, fmt="date", h="center", v="center")

    # ---------------- Daily Tasks (önce; diğer sayfalar buna bağlı)
    dt = wb.add("Daily Tasks", "1F2937")
    dh = ["ID", "Tarih", "Gün", "Ders", "Seviye", "Öncelik", "Süre (dk)", "Görev", "Materyal / Slayt", "Durum", "Not", "Kritik"]
    dt.row(1, dh, hdr)
    for i, (d, t) in enumerate(tasks, start=2):
        dt.set(i, 1, t["id"], cell)
        dt.set(i, 2, serial(d["date"]), dcell)
        dt.set(i, 3, d["weekday"], cellc)
        dt.set(i, 4, t["course"], cellc)
        dt.set(i, 5, "Min" if t["tier"] == "core" else "Ext", cellc)
        dt.set(i, 6, t["priority"], cellc)
        dt.set(i, 7, t["minutes"], icell)
        dt.set(i, 8, t["text"], cell)
        dt.set(i, 9, (t["ref"] + (" — " + PENDING_TXT if t["kind"] in "LP" else "")) if t["ref"] else "", cell)
        dt.set(i, 10, sts.get(t["id"], "Not Started"), inp)
        dt.set(i, 11, notes.get(t["id"], ""), inp)
        dt.set(i, 12, "★" if t.get("critical") else "", cellc)
    for c, w in zip(range(1, 13), [14, 11, 11, 10, 8, 8, 8, 70, 32, 13, 24, 7]):
        dt.widths[c] = w
    dt.freeze = (1, 0)
    dt.filter = f"A1:L{N}"
    dt.dv.append((f"J2:J{N}", STATUS_LIST))
    rng = lambda col: f"'Daily Tasks'!${col}$2:${col}${N}"
    dt.cf.append((f"A2:L{N}", "expr", '$J2="Completed"', 0))
    dt.cf.append((f"A2:L{N}", "expr", '$J2="In Progress"', 1))
    dt.cf.append((f"A2:L{N}", "expr", '$J2="Blocked"', 4))
    dt.cf.append((f"A2:L{N}", "expr", '$J2="Postponed"', 3))
    dt.cf.append((f"A2:L{N}", "expr", 'AND($J2<>"Completed",$B2<TODAY())', 2))

    # ---------------- Course Progress
    cp = wb.add("Course Progress", "2E7D32")
    cp.set(1, 1, "Ders bazlı ilerleme (görev tamamlanma — öğrenme seviyesi DEĞİL)", title)
    cp.set(2, 1, "Öğrenme seviyesi için Topic Mastery sayfasına bak. " + TODAY_NOTE, sub)
    heads = ["Ders", "Toplam görev", "Tamamlanan", "% Tamamlanma", "Min görev", "Min tamamlanan", "% Min plan", "Planlanan dk",
             "Tamamlanan dk", "Geciken", "In Progress", "Postponed", "Blocked"]
    cp.row(4, heads, hdr)
    cached = {c: dict(tot=0, done=0, mt=0, md=0, pm=0, dm=0) for c in COURSE_ORDER}
    for d, t in tasks:
        c = t["course"]
        if c in cached:
            x = cached[c]
            x["tot"] += 1
            x["pm"] += t["minutes"]
            if t["tier"] == "core":
                x["mt"] += 1
            if sts.get(t["id"]) == "Completed":
                x["done"] += 1
                x["dm"] += t["minutes"]
                if t["tier"] == "core":
                    x["md"] += 1
    for i, c in enumerate(COURSE_ORDER, start=5):
        x = cached[c]
        cp.set(i, 1, c, cell)
        base = f"{rng('D')},$A{i}"
        cp.set(i, 2, None, icell, f=f"COUNTIFS({base})", cached=x["tot"])
        cp.set(i, 3, None, icell, f=f'COUNTIFS({base},{rng("J")},"Completed")', cached=x["done"])
        cp.set(i, 4, None, pcell, f=f"IF(B{i}=0,0,C{i}/B{i})", cached=(x["done"] / x["tot"] if x["tot"] else 0))
        cp.set(i, 5, None, icell, f=f'COUNTIFS({base},{rng("E")},"Min")', cached=x["mt"])
        cp.set(i, 6, None, icell, f=f'COUNTIFS({base},{rng("E")},"Min",{rng("J")},"Completed")', cached=x["md"])
        cp.set(i, 7, None, pcell, f=f"IF(E{i}=0,0,F{i}/E{i})", cached=(x["md"] / x["mt"] if x["mt"] else 0))
        cp.set(i, 8, None, icell, f=f"SUMIFS({rng('G')},{base})", cached=x["pm"])
        cp.set(i, 9, None, icell, f=f'SUMIFS({rng("G")},{base},{rng("J")},"Completed")', cached=x["dm"])
        cp.set(i, 10, None, icell, f=f'COUNTIFS({base},{rng("J")},"<>Completed",{rng("B")},"<"&TODAY())')
        for j, st in zip((11, 12, 13), ("In Progress", "Postponed", "Blocked")):
            cp.set(i, j, None, icell, f=f'COUNTIFS({base},{rng("J")},"{st}")')
    r = 11
    cp.set(r, 1, "TOPLAM", kpi_l)
    for j in (2, 3, 5, 6, 8, 9, 10, 11, 12, 13):
        L = col_letter(j)
        cp.set(r, j, None, S.get(font=1, border=1, fmt="int", h="center"), f=f"SUM({L}5:{L}10)")
    cp.set(r, 4, None, S.get(font=1, border=1, fmt="pct", h="center"), f="IF(B11=0,0,C11/B11)")
    cp.set(r, 7, None, S.get(font=1, border=1, fmt="pct", h="center"), f="IF(E11=0,0,F11/E11)")
    cp.cf.append(("D5:D10", "bar", None, 0))
    cp.cf.append(("G5:G10", "bar", None, 0))
    cp.cf.append(("J5:J10", "expr", "$J5>0", 2))
    for c, w in zip(range(1, 14), [12, 13, 12, 14, 11, 14, 12, 14, 14, 10, 12, 12, 10]):
        cp.widths[c] = w
    cp.heights[4] = 32

    # ---------------- Topic Mastery
    tm = wb.add("Topic Mastery", "6A1B9A")
    tm.set(1, 1, "Konu öğrenme seviyesi (kendi test sonucunla doldur — sarı alanlar)", title)
    tm.set(2, 1, "%85–100 Güçlü · %70–84 İyi ama tekrar gerekli · %50–69 Eksik · %0–49 Önkoşul + konu yeniden. Başlangıç çalışma politikasıdır, başarı garantisi değildir.", sub)
    tm.row(4, ["Ders", "Konu / Blok", "İlk öğrenme", "Son tekrar", "Öğrenme skoru %", "Seviye", "Notlar"], hdr)
    placed = {}
    for d, t in tasks:
        if t["block"] in plan["blocks"] and t["block"] not in placed:
            placed[t["block"]] = d["date"]
    lblocks = [b for b in plan["blocks"].values() if b["kind"] == "L" and b["id"] in placed]
    lblocks.sort(key=lambda b: (COURSE_ORDER.index(b["course"]), placed[b["id"]]))
    r0 = 5
    for i, b in enumerate(lblocks):
        r = r0 + i
        tm.set(r, 1, b["course"], cellc)
        tm.set(r, 2, f"{b['id']} · {b['title']}", cell)
        tm.set(r, 3, serial(placed[b["id"]]), dcell)
        tm.set(r, 4, None, inpd)
        tm.set(r, 5, None, inpp)
        tm.set(r, 6, None, cellc, f=f'IF(E{r}="","",IF(E{r}>=0.85,"Güçlü",IF(E{r}>=0.7,"İyi — tekrar gerekli",IF(E{r}>=0.5,"Eksik","Yeniden çalış"))))', cached="")
        tm.set(r, 7, None, inp)
    tmN = r0 + len(lblocks) - 1
    tm.cf += [(f"F{r0}:F{tmN}", "expr", f'$E{r0}>=0.85', 0), (f"F{r0}:F{tmN}", "expr", f'AND($E{r0}<>"",$E{r0}>=0.7,$E{r0}<0.85)', 1),
              (f"F{r0}:F{tmN}", "expr", f'AND($E{r0}<>"",$E{r0}<0.7)', 2)]
    for c, w in zip(range(1, 8), [11, 52, 12, 12, 14, 22, 36]):
        tm.widths[c] = w
    tm.freeze = (4, 0)
    tm.filter = f"A4:G{tmN}"

    # ---------------- Exam Countdown
    ex = wb.add("Exam Countdown", "C62828")
    ex.set(1, 1, "Sınav ve teslim geri sayımı", title)
    ex.set(2, 1, "Teyit Bekliyor = doğrulanmamış tarih. Kesin tarih öğrenince sarı hücreleri düzenle. " + TODAY_NOTE, sub)
    ex.row(4, ["Ders", "Başlık", "Tarih", "Bitiş", "Saat", "Durum", "Gün kaldı", "Not"], hdr)
    label = {"confirmed": "Kesin (syllabus)", "user": "Kullanıcı teyitli", "tentative": "Teyit Bekliyor",
             "window": "Teyit Bekliyor (aralık)", "unknown": "Duyurulacak"}
    evs = sorted([e for e in plan["evals"]], key=lambda e: (e["date"] or "9999"))
    for i, e in enumerate(evs, start=5):
        ex.set(i, 1, e["course"], cellc)
        ex.set(i, 2, e["title"], cell)
        ex.set(i, 3, serial(e["date"]) if e["date"] else None, inpd)
        ex.set(i, 4, serial(e["end"]) if e["end"] else None, inpd)
        ex.set(i, 5, "–".join(e["time"]) if e.get("time") else "belli değil", cellc)
        ex.set(i, 6, label[e["status"]], cell)
        ex.set(i, 7, None, icell, f=f'IF(C{i}="","",C{i}-TODAY())')
        ex.set(i, 8, e["note"], cell)
    exN = 4 + len(evs)
    ex.cf += [(f"A5:H{exN}", "expr", "AND(ISNUMBER($G5),$G5>=0,$G5<=7)", 2), (f"A5:H{exN}", "expr", "AND(ISNUMBER($G5),$G5>7,$G5<=14)", 1),
              (f"A5:H{exN}", "expr", "AND(ISNUMBER($G5),$G5<0)", 3)]
    for c, w in zip(range(1, 9), [11, 38, 12, 12, 13, 26, 10, 80]):
        ex.widths[c] = w

    # ---------------- Assignments
    asg = wb.add("Assignments", "EF6C00")
    asg.set(1, 1, "Ödev / teslim / quiz takibi", title)
    asg.row(3, ["Ders", "Teslim / Ödev", "Resmi son tarih", "İç hedef", "Durum", "Gün kaldı", "Not"], hdr)
    inner = {}
    for d, t in tasks:
        inner.setdefault(t["block"], d["date"])
    items = [
        ("CMPE499", "Evaluation Form", "2026-10-07", None, "Kullanıcı: teslim edildi."),
        ("CMPE499", "Summer Training Report (STR)", "2026-11-22", inner.get("U9"), "Resmi son: Pazar. Plan: 2 gün erken yükle."),
        ("CMPE499", "Summer Training Video", "2026-11-29", inner.get("VD6"), "Resmi son: Pazar. Plan: 3 gün erken yükle."),
        ("CMPE371", "HW 1 (Teyit Bekliyor)", "2026-11-06", inner.get("SH1b"), "Syllabus W6 (2–6 Kas). Kesin gün yok; Cuma varsayıldı."),
        ("CMPE371", "Quiz 1 (Teyit Bekliyor)", "2026-12-07", inner.get("SQ1"), "Syllabus W11 (7–11 Ara)."),
        ("CMPE327", "Quiz-2 (Teyit Bekliyor)", "2026-12-14", inner.get("AQ2"), "Syllabus W12 (14–18 Ara). Gün doğrulanacak."),
        ("CMPE327", "Quiz (kullanıcı bildirimi) 13:00–14:00", "2026-11-15", inner.get("AQ1"), "Ertelenen quiz; kapsamı Midterm'den ayrı doğrula."),
        ("CMPE421", "Assignment-1 (Code + Report + Q&A) 23:59", "2026-11-26", inner.get("AS6"), "LMS: 26 Kasım 23:59. PDF gereksinimleri doğrulanacak; bileşen durumlarını ayrı izle."),
        ("BIO110", "Proje sunumu (15–20 slayt)", "2026-12-10", inner.get("BP5"), "Sunum penceresi 10–31 Ara; sıra belli değil."),
        ("CMPE327", "Midterm (29 Kasım 13:00–15:00, W1–W8)", "2026-11-29", inner.get("AF"), "Kullanıcı bildirimi; kapsam Week 08 dahil. Eski kayıt 15 Kasım artık Quiz."),
        ("CMPE421", "Midterm (20 Kasım 18:00–20:00)", "2026-11-20", inner.get("IF"), "Hoca duyurusu (kullanıcı bildirimi)."),
        ("CMPE371", "Midterm (30 Kasım 18:00–20:00)", "2026-11-30", inner.get("SR4"), "Kullanıcı bildirimi; syllabus W9 (23–27 Kas) ile farklı, duyuru esas."),
        ("CMPE421", "Homework(lar) %30", None, inner.get("IH"), "Teslim tarihi/sayısı syllabus'ta yok — doğrula."),
    ]
    for i, (c, n, due, it, note) in enumerate(items, start=4):
        asg.set(i, 1, c, cellc)
        asg.set(i, 2, n, cell)
        asg.set(i, 3, serial(due) if due else None, inpd)
        asg.set(i, 4, serial(it) if it else None, inpd)
        asg.set(i, 5, "Completed" if n == "Evaluation Form" else "Not Started", inp)
        asg.set(i, 6, None, icell, f=f'IF(C{i}="","",C{i}-TODAY())')
        asg.set(i, 7, note, cell)
    aN = 3 + len(items)
    asg.dv.append((f"E4:E{aN}", STATUS_LIST))
    asg.cf += [(f"A4:G{aN}", "expr", '$E4="Completed"', 0), (f"A4:G{aN}", "expr", 'AND($E4<>"Completed",ISNUMBER($F4),$F4<0)', 2),
               (f"A4:G{aN}", "expr", 'AND($E4<>"Completed",ISNUMBER($F4),$F4>=0,$F4<=7)', 1)]
    for c, w in zip(range(1, 8), [11, 34, 14, 12, 13, 10, 70]):
        asg.widths[c] = w

    # ---------------- Revision Schedule
    rv = wb.add("Revision Schedule", "00838F")
    rv.set(1, 1, "Aralıklı tekrar takvimi (D+1, D+3, D+7, D+14)", title)
    rv.set(2, 1, "Sınav yaklaşınca sıkıştır; iyi öğrenilen konuda azalt (Topic Mastery). Günlük görevlerdeki 'Tekrar' satırları aynı kaynaktan üretilir.", sub)
    rv.row(4, ["Ders", "Konu / Blok", "Öğrenme", "D+1", "D+3", "D+7", "D+14", "D+1 ✓", "D+3 ✓", "D+7 ✓", "D+14 ✓"], hdr)
    for i, b in enumerate(lblocks, start=5):
        sd = date.fromisoformat(placed[b["id"]])
        rv.set(i, 1, b["course"], cellc)
        rv.set(i, 2, f"{b['id']} · {b['title']}", cell)
        rv.set(i, 3, serial(sd), dcell)
        for j, n in zip((4, 5, 6, 7), (1, 3, 7, 14)):
            rv.set(i, j, serial(sd + timedelta(days=n)), dcell)
        for j in (8, 9, 10, 11):
            rv.set(i, j, "Pending", inp)
    rvN = 4 + len(lblocks)
    rv.dv.append((f"H5:K{rvN}", '"Pending,Done,Skipped"'))
    rv.cf += [(f"H5:K{rvN}", "expr", 'H5="Done"', 0), (f"D5:G{rvN}", "expr", 'AND(D5<TODAY(),H5<>"Done")', 2)]
    for c, w in zip(range(1, 12), [11, 52, 12, 12, 12, 12, 12, 10, 10, 10, 10]):
        rv.widths[c] = w
    rv.freeze = (4, 0)

    # ---------------- Mistake Log
    ml = wb.add("Mistake Log", "AD1457")
    ml.set(1, 1, "Yanlış defteri — her yanlışın SEBEBİNİ yaz; aynı hata tekrarlanıyorsa o konuya düzeltici çalışma ekle", title)
    ml.row(3, ["Tarih", "Ders", "Konu", "Kaynak / soru", "Hata türü", "Ne yanlış gitti", "Doğru çözüm / kural", "Tekrar (D+3)", "Tekrar (D+7)", "Düzeltildi?"], hdr)
    for i in range(4, 304):
        for j in range(1, 8):
            ml.set(i, j, None, inpd if j == 1 else inp)
        ml.set(i, 8, None, dcol, f=f'IF($A{i}="","",$A{i}+3)', cached="")
        ml.set(i, 9, None, dcol, f=f'IF($A{i}="","",$A{i}+7)', cached="")
        ml.set(i, 10, None, inp)
    ml.dv += [("E4:E303", '"Konu bilinmiyor,Formül hatası,İşlem hatası,Kavram karışıklığı,Algoritma mantığı hatası,Soruyu yanlış yorumlama,Dikkat hatası"'),
              ("B4:B303", '"' + ",".join(COURSE_ORDER) + '"'), ("J4:J303", '"Yes,No"')]
    for c, w in zip(range(1, 11), [12, 11, 26, 24, 24, 40, 40, 12, 12, 11]):
        ml.widths[c] = w
    ml.freeze = (3, 0)

    # ---------------- Slide Coverage
    sc = wb.add("Slide Coverage", "37474F")
    write_slide_sheet(sc, S, plan, lblocks, placed, hdr, cell, cellc, dcell, icell, inp, title, sub)

    # ---------------- Weekly Reviews
    wr = wb.add("Weekly Reviews", "F9A825")
    wr.set(1, 1, "Haftalık değerlendirme", title)
    wr.row(3, ["Hafta", "Başlangıç", "Bitiş", "Planlanan görev", "Tamamlanan", "% Tamamlanma", "Planlanan dk", "Tamamlanan dk",
               "Eksik kalan konular", "Sonraki hafta hedefleri", "Notlar"], hdr)
    for i, (a, b, name) in enumerate(plan["weeks"], start=4):
        wr.set(i, 1, name, cell)
        wr.set(i, 2, serial(a), dcell)
        wr.set(i, 3, serial(b), dcell)
        bd = f'{rng("B")},">="&$B{i},{rng("B")},"<="&$C{i}'
        wr.set(i, 4, None, icell, f=f"COUNTIFS({bd})")
        wr.set(i, 5, None, icell, f=f'COUNTIFS({bd},{rng("J")},"Completed")')
        wr.set(i, 6, None, pcell, f=f"IF(D{i}=0,0,E{i}/D{i})")
        wr.set(i, 7, None, icell, f=f"SUMIFS({rng('G')},{bd})")
        wr.set(i, 8, None, icell, f=f'SUMIFS({rng("G")},{bd},{rng("J")},"Completed")')
        for j in (9, 10, 11):
            wr.set(i, j, None, inp)
        wr.heights[i] = 42
    wr.cf.append((f"F4:F{3 + len(plan['weeks'])}", "bar", None, 0))
    for c, w in zip(range(1, 12), [18, 12, 12, 13, 12, 14, 13, 14, 36, 36, 30]):
        wr.widths[c] = w
    wr.heights[3] = 32

    # ---------------- Dashboard (ilk sekme)
    db = Workbook.__new__(Workbook)
    dsh = wb.add("Dashboard", "111827")
    wb.sheets.insert(0, wb.sheets.pop())
    dsh.set(1, 1, "Academic Success Plan — Dashboard", title)
    dsh.set(2, 1, "Bugün:", bold)
    dsh.set(2, 2, None, S.get(font=1, fmt="date", h="left"), f="TODAY()")
    dsh.set(2, 4, "Tamamlanma ≠ öğrenme seviyesi. Öğrenme için Topic Mastery'yi doldur.", sub)
    kl = ["Toplam görev", "Tamamlanan", "% Tamamlanma", "% Min plan", "Planlanan saat", "Tamamlanan saat", "Geciken görev"]
    for j, k in enumerate(kl, start=1):
        dsh.set(4, j, k, kpi_l)
    dsh.heights[4] = 30
    tot = sum(x["tot"] for x in cached.values())
    done = sum(x["done"] for x in cached.values())
    dsh.set(5, 1, None, kpi_v, f="'Course Progress'!B11", cached=tot)
    dsh.set(5, 2, None, kpi_v, f="'Course Progress'!C11", cached=done)
    dsh.set(5, 3, None, kpi_p, f="'Course Progress'!D11", cached=(done / tot if tot else 0))
    dsh.set(5, 4, None, kpi_p, f="'Course Progress'!G11", cached=0)
    dsh.set(5, 5, None, S.get(font=5, border=1, fmt="dec", h="center"), f="'Course Progress'!H11/60", cached=round(sum(x["pm"] for x in cached.values()) / 60, 2))
    dsh.set(5, 6, None, S.get(font=5, border=1, fmt="dec", h="center"), f="'Course Progress'!I11/60", cached=0)
    dsh.set(5, 7, None, kpi_v, f="'Course Progress'!J11")
    dsh.heights[5] = 28
    dsh.set(7, 1, "Ders bazlı ilerleme", S.get(font=5))
    dsh.row(8, ["Ders", "Ad", "% Tamamlanma", "% Min plan", "Tamamlanan / Toplam", "Geciken", "Ort. öğrenme skoru"], hdr)
    for i, c in enumerate(COURSE_ORDER, start=9):
        cr = i - 4
        dsh.set(i, 1, c, cellc)
        dsh.set(i, 2, plan["courses"][c]["name"], cell)
        dsh.set(i, 3, None, pcell, f=f"'Course Progress'!D{cr}", cached=0)
        dsh.set(i, 4, None, pcell, f=f"'Course Progress'!G{cr}", cached=0)
        dsh.set(i, 5, None, cellc, f=f"'Course Progress'!C{cr}&\" / \"&'Course Progress'!B{cr}", cached=f"0 / {cached[c]['tot']}")
        dsh.set(i, 6, None, icell, f=f"'Course Progress'!J{cr}")
        dsh.set(i, 7, None, pcell, f=f"IFERROR(AVERAGEIFS('Topic Mastery'!$E${r0}:$E${tmN},'Topic Mastery'!$A${r0}:$A${tmN},A{i}),\"—\")", cached="—")
    dsh.cf += [("C9:C14", "bar", None, 0), ("D9:D14", "bar", None, 0), ("F9:F14", "expr", "$F9>0", 2)]
    dsh.set(16, 1, "Yaklaşan sınav / teslim (Exam Countdown'dan)", S.get(font=5))
    dsh.row(17, ["Ders", "Başlık", "Tarih", "Gün kaldı", "Durum"], hdr)
    for k in range(len(evs)):
        i = 18 + k
        er = 5 + k
        dsh.set(i, 1, None, cellc, f=f"'Exam Countdown'!A{er}", cached=evs[k]["course"])
        dsh.set(i, 2, None, cell, f=f"'Exam Countdown'!B{er}", cached=evs[k]["title"])
        dsh.set(i, 3, None, dcol, f=f"IF('Exam Countdown'!C{er}=\"\",\"\",'Exam Countdown'!C{er})", cached=(serial(evs[k]["date"]) if evs[k]["date"] else ""))
        dsh.set(i, 4, None, icell, f=f"'Exam Countdown'!G{er}")
        dsh.set(i, 5, None, cell, f=f"'Exam Countdown'!F{er}", cached=label[evs[k]["status"]])
    dN = 17 + len(evs)
    dsh.cf += [(f"A18:E{dN}", "expr", "AND(ISNUMBER($D18),$D18>=0,$D18<=7)", 2), (f"A18:E{dN}", "expr", "AND(ISNUMBER($D18),$D18>7,$D18<=14)", 1),
               (f"A18:E{dN}", "expr", "AND(ISNUMBER($D18),$D18<0)", 3)]
    for c, w in zip(range(1, 8), [13, 40, 15, 12, 26, 11, 16]):
        dsh.widths[c] = w
    return wb, plan, lblocks, placed


PENDING_TXT = "Materyal bekleniyor"


def write_slide_sheet(sc, S, plan, lblocks, placed, hdr, cell, cellc, dcell, icell, inp, title, sub):
    sc.set(1, 1, "SLIDE_COVERAGE_MATRIX — slayt/dosya kapsama matrisi", title)
    sc.set(2, 1, "Hiç slayt/PDF paylaşılmadı → tüm satırlar 'Materyal bekleniyor'. Dosyalar gelince Dosya ve Sayfa aralığı sütunlarını doldur; hiçbir sayfa/içerik UYDURULMADI.", sub)
    sc.row(4, ["Ders", "Dosya", "Sayfa/slayt aralığı", "Syllabus konusu", "Zorluk (1–5)", "Tahmini dk", "Öğrenme çıktısı (uygulama)", "Çalışma tarihi", "Tekrar tarihi (D+1)", "Durum"], hdr)
    for i, b in enumerate(lblocks, start=5):
        sd = date.fromisoformat(placed[b["id"]])
        sc.set(i, 1, b["course"], cellc)
        sc.set(i, 2, PENDING_TXT, inp)
        sc.set(i, 3, "—", inp)
        sc.set(i, 4, b["topics"], cell)
        sc.set(i, 5, plan["courses"][b["course"]]["diff"], icell)
        sc.set(i, 6, b["minutes"], icell)
        sc.set(i, 7, b["practice"], cell)
        sc.set(i, 8, serial(sd), dcell)
        sc.set(i, 9, serial(sd + timedelta(days=1)), dcell)
        sc.set(i, 10, "Not Started", inp)
    n = 4 + len(lblocks)
    sc.dv.append((f"J5:J{n}", STATUS_LIST))
    sc.cf.append((f"A5:J{n}", "expr", '$J5="Completed"', 0))
    for c, w in zip(range(1, 11), [11, 22, 16, 46, 10, 10, 50, 12, 13, 13]):
        sc.widths[c] = w
    sc.freeze = (4, 0)
    sc.filter = f"A4:J{n}"


def main():
    wb, plan, lblocks, placed = build()
    out = os.path.join(ROOT, "06_Progress_Tracker")
    wb.save(os.path.join(out, "Academic_Study_Tracker_2026.xlsx"))
    # tek sayfalık kapsama matrisi (xlsx + csv)
    w2 = Workbook()
    S = w2.styles
    hdr = S.get(font=2, fill=2, border=1, wrap=1, h="center", v="center")
    cell = S.get(border=1, wrap=1, v="top")
    cellc = S.get(border=1, h="center", v="top")
    dcell = S.get(border=1, fmt="date", h="center", v="top")
    icell = S.get(border=1, fmt="int", h="center", v="center")
    inp = S.get(border=1, fill=8, wrap=1, v="top")
    write_slide_sheet(w2.add("Slide Coverage", "37474F"), S, plan, lblocks, placed, hdr, cell, cellc, dcell, icell, inp, S.get(font=3), S.get(font=4))
    w2.save(os.path.join(out, "SLIDE_COVERAGE_MATRIX.xlsx"))
    with open(os.path.join(out, "SLIDE_COVERAGE_MATRIX.csv"), "w", encoding="utf-8-sig", newline="") as f:
        cw = csv.writer(f)
        cw.writerow(["Ders", "Dosya", "Sayfa/slayt aralığı", "Syllabus konusu", "Zorluk", "Tahmini dk", "Öğrenme çıktısı", "Çalışma tarihi", "Tekrar tarihi (D+1)", "Durum"])
        for b in lblocks:
            sd = date.fromisoformat(placed[b["id"]])
            cw.writerow([b["course"], PENDING_TXT, "—", b["topics"], plan["courses"][b["course"]]["diff"], b["minutes"], b["practice"],
                         sd.isoformat(), (sd + timedelta(days=1)).isoformat(), "Not Started"])
    print("XLSX yazıldı:", len(lblocks), "konu satırı")


if __name__ == "__main__":
    main()

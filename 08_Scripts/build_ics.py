# -*- coding: utf-8 -*-
"""plan.json + progress.json -> Study_Plan_2026.ics ve Exams_Deadlines_2026.ics
UID'ler sabittir: dosyayı tekrar içe aktarmak aynı etkinlikleri GÜNCELLER (mükerrer oluşturmaz)."""
import os
from datetime import date, timedelta
from common import *

STAMP = "20261027T000000Z"
VTZ = ["BEGIN:VTIMEZONE", "TZID:Europe/Istanbul", "BEGIN:STANDARD", "DTSTART:19700101T000000",
       "TZOFFSETFROM:+0300", "TZOFFSETTO:+0300", "TZNAME:+03", "END:STANDARD", "END:VTIMEZONE"]


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r", "").replace("\n", "\\n")


def fold(line):
    """RFC 5545: satırlar ≤75 oktet; çok baytlı UTF-8 karakter bölünmez."""
    b = line.encode("utf-8")
    if len(b) <= 75:
        return [line]
    out, cur, n = [], "", 0
    limit = 75
    for ch in line:
        cb = len(ch.encode("utf-8"))
        if n + cb > limit:
            out.append(cur)
            cur, n, limit = " " + ch, 1 + cb, 75
        else:
            cur += ch
            n += cb
    out.append(cur)
    return out


def ymd(s):
    return s.replace("-", "")


def next_day(s):
    return (date.fromisoformat(s) + timedelta(days=1)).isoformat()


def alarm(trigger, desc):
    return ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(desc)}", f"TRIGGER:{trigger}", "END:VALARM"]


def calendar(name, events, desc):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Academic Success Plan 2026//TR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             f"X-WR-CALNAME:{esc(name)}", "X-WR-TIMEZONE:Europe/Istanbul", f"X-WR-CALDESC:{esc(desc)}"] + VTZ
    for ev in events:
        lines += ev
    lines.append("END:VCALENDAR")
    out = []
    for l in lines:
        out += fold(l)
    return "\r\n".join(out) + "\r\n"


def study_events(plan, prog):
    seq = prog.get("calendar_sequence", 0)
    evs = []
    for d in plan["days"]:
        sts = prog["tasks"]
        core = [t for t in d["tasks"] if t["tier"] == "core"]
        ext = [t for t in d["tasks"] if t["tier"] == "ext"]
        all_done = core and all(sts.get(t["id"], {}).get("status") == "Completed" for t in core)
        main = d["main"]
        top = next((t for t in core if t["course"] == main and t["kind"] != "T"), None)
        prio = "P1" if d["ranking"] and d["ranking"][0] == main else "P2"
        minh = f"{d['core_min'] / 60:.1f}".replace(".", ",")
        summ = f"{'✓ ' if all_done else ''}{main} · {top['title'] if top else 'Plan'} · {prio} · Min {minh}sa"

        def line(t):
            st = sts.get(t["id"], {}).get("status", "Not Started")
            mark = "[x]" if st == "Completed" else "[ ]"
            return f"{mark} {t['course']} ({t['minutes']} dk): {t['text']}"
        desc = [d["goal"], f"Faz: {d['phase']}", "", f"MİNİMUM PLAN (≈{d['core_min']} dk):"] + [line(t) for t in core]
        if ext:
            desc += ["", f"İSTEĞE BAĞLI EK (toplam ≈{d['ext_min']} dk):"] + [line(t) for t in ext]
        desc += ["", "Tamamlanma kriteri: min görevler işaretli + her blok sonunda soru/yanlış analizi yapıldı.",
                 "Yapamadığın görev: ertesi güne YIĞMA; REPLAN_GUIDE.md adımlarıyla yeniden planla."]
        evs.append(["BEGIN:VEVENT", f"UID:study-{d['date']}@academic-success-2026", f"DTSTAMP:{STAMP}", f"SEQUENCE:{seq}",
                    f"DTSTART;VALUE=DATE:{ymd(d['date'])}", f"DTEND;VALUE=DATE:{ymd(next_day(d['date']))}",
                    f"SUMMARY:{esc(summ)}", f"DESCRIPTION:{esc(chr(10).join(desc))}", "CATEGORIES:STUDY", "TRANSP:TRANSPARENT"]
                   + alarm("PT8H", f"Bugünün planı: {main} ({d['goal'][:60]})") + ["END:VEVENT"])
    return evs


def status_label(e):
    return {"confirmed": "Kesin (syllabus)", "user": "Kullanıcı teyitli", "tentative": "Teyit Bekliyor",
            "window": "Teyit Bekliyor (tarih aralığı)"}.get(e["status"], "")


def exam_events(plan, prog):
    seq = prog.get("calendar_sequence", 0)
    evs = []
    for e in plan["evals"]:
        if not e["date"]:
            continue
        tent = e["status"] in ("tentative", "window")
        title = ("[TEYİT BEKLİYOR] " if tent else "") + e["title"]
        desc = f"{status_label(e)}\n{e['note']}\nHatırlatma saati 08:00 (çalışma saati DEĞİL)."
        ev = ["BEGIN:VEVENT", f"UID:eval-{e['id']}@academic-success-2026", f"DTSTAMP:{STAMP}", f"SEQUENCE:{seq}"]
        timed = e.get("time")
        if timed:
            ev += [f"DTSTART;TZID=Europe/Istanbul:{ymd(e['date'])}T{timed[0].replace(':', '')}00",
                   f"DTEND;TZID=Europe/Istanbul:{ymd(e['date'])}T{timed[1].replace(':', '')}00"]
        else:
            end = e["end"] or e["date"]
            ev += [f"DTSTART;VALUE=DATE:{ymd(e['date'])}", f"DTEND;VALUE=DATE:{ymd(next_day(end))}"]
        ev += [f"SUMMARY:{esc(title)}", f"DESCRIPTION:{esc(desc)}", "CATEGORIES:" + ("TENTATIVE" if tent else "EXAM"),
               "STATUS:" + ("TENTATIVE" if tent else "CONFIRMED")]
        deadline = e["id"] in ("sum-str", "sum-vid", "sig-hw1")
        days_before = (3, 1) if deadline else (7, 3, 1)
        for n in days_before:
            if timed:
                trig = f"-P{n}DT10H"        # sınav 18:00 → hatırlatma 08:00
            else:
                trig = f"-P{n - 1}DT16H" if n > 1 else "-PT16H"  # tüm gün etkinliği 00:00 → 08:00
            ev += alarm(trig, f"{e['title']} — {n} gün kaldı")
        ev.append("END:VEVENT")
        evs.append(ev)
    # plan iç tarihleri (replan'a duyarlı): STR/video iç kontrol ve yükleme günleri
    internal = {"U7": "STR iç kontrol", "U9": "STR yükleme günü (resmi son: 22 Kas)", "VD5": "Video kalite kontrol",
                "VD6": "Video yükleme günü (resmi son: 29 Kas)"}
    for d in plan["days"]:
        for t in d["tasks"]:
            if t["block"] in internal:
                evs.append(["BEGIN:VEVENT", f"UID:internal-{t['block']}@academic-success-2026", f"DTSTAMP:{STAMP}",
                            f"SEQUENCE:{seq}", f"DTSTART;VALUE=DATE:{ymd(d['date'])}", f"DTEND;VALUE=DATE:{ymd(next_day(d['date']))}",
                            f"SUMMARY:{esc('İÇ HEDEF: ' + internal[t['block']])}",
                            "DESCRIPTION:Plan iç tarihi (resmi teslim değildir).", "CATEGORIES:INTERNAL", "TRANSP:TRANSPARENT",
                            "END:VEVENT"])
    return evs


def main():
    plan = load_plan()
    prog = load_progress(plan)
    out = os.path.join(ROOT, "04_Calendar")
    with open(os.path.join(out, "Study_Plan_2026.ics"), "w", encoding="utf-8", newline="") as f:
        f.write(calendar("Study Plan 2026 (Günlük görevler)", study_events(plan, prog),
                         "Günlük akademik plan; tüm gün etkinlikleri. Sabah 08:00 hatırlatma."))
    with open(os.path.join(out, "Exams_Deadlines_2026.ics"), "w", encoding="utf-8", newline="") as f:
        f.write(calendar("Exams & Deadlines 2026", exam_events(plan, prog),
                         "Sınav ve teslimler. [TEYİT BEKLİYOR] = doğrulanmamış tarih."))
    print("ICS yazıldı")


if __name__ == "__main__":
    main()

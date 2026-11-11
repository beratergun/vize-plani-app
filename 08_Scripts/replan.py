# -*- coding: utf-8 -*-
"""Akıllı yeniden planlama.
  py replan.py --today 2026-11-05            # önizleme (dry-run, hiçbir şey yazmaz)
  py replan.py --today 2026-11-05 --apply    # uygula + çıktıları yeniden üret
  py replan.py --apply --from-xlsx           # önce Excel'deki durumları oku
Kurallar: tamamlananlara dokunmaz · kritik/yaklaşan sınav önce · günlük kapasiteyi aşmaz · ders içi sıra korunur
(önkoşullar atlanmaz) · sığmayan düşük öncelikli tekrar 'Postponed' olur · mevcut dosyalar yedeklenir."""
import argparse
import os
import shutil
import time
from datetime import date, timedelta
from common import *

PRIO = {"P1": 0, "P2": 1, "P3": 2}


def recalc(day):
    day["core_min"] = sum(t["minutes"] for t in day["tasks"] if t["tier"] == "core")
    day["ext_min"] = day["core_min"] + sum(t["minutes"] for t in day["tasks"] if t["tier"] == "ext")


def next_eval(plan, course, today):
    ds = [e["date"] for e in plan["evals"] if e["course"] == course and e["date"] and e["date"] >= today]
    return min(ds) if ds else None


def replan(today, apply=False, from_xlsx=False):
    if from_xlsx:
        from sync_from_xlsx import sync
        sync(os.path.join(ROOT, "06_Progress_Tracker", "Academic_Study_Tracker_2026.xlsx"))
    plan, prog = load_plan(), load_progress()
    caps = plan["caps"]
    days = {d["date"]: d for d in plan["days"]}
    sts = prog["tasks"]
    iso = today.isoformat()
    missed = []
    for d in plan["days"]:
        if d["date"] < iso:
            for t in d["tasks"]:
                if sts.get(t["id"], {}).get("status", "Not Started") != "Completed":
                    missed.append((d, t))
    # kritik ext → min (teslim yaklaşırken)
    promoted = 0
    for d in plan["days"]:
        if d["date"] >= iso and d["date"] <= (today + timedelta(days=7)).isoformat():
            for t in d["tasks"]:
                if t.get("critical") and t["tier"] == "ext" and sts.get(t["id"], {}).get("status") != "Completed":
                    t["tier"] = "core"
                    promoted += 1
    # ders içi sıra korunur: her ders için ayrı kuyruk (orijinal tarih sırası); kuyruklar öncelikle birleştirilir
    def exam_passed(t, orig):
        ev = [e["date"] for e in plan["evals"] if e["course"] == t["course"] and e["date"] and e["status"] != "unknown" and e["date"] >= orig]
        return bool(ev) and min(ev) < iso

    queues = {}
    dropped = []
    for d0, t in sorted(missed, key=lambda x: (x[0]["date"], x[1]["id"])):
        if t["kind"] == "P" and exam_passed(t, d0["date"]):  # sınav geçti: hazırlık görevi anlamsız → Postponed (final tekrarına bırakılır)
            dropped.append((d0, t))
            continue
        queues.setdefault((t["course"], "T" if t["kind"] == "T" else "N"), []).append((d0, t))
    last_for_course = {}
    moves = []
    future = [d for d in plan["days"] if d["date"] >= iso]
    while any(queues.values()):
        key = min((k for k, q in queues.items() if q),
                  key=lambda k: (not queues[k][0][1].get("critical", False), queues[k][0][1]["tier"] != "core", PRIO[queues[k][0][1]["priority"]], queues[k][0][0]["date"]))
        d0, t = queues[key].pop(0)
        c = t["course"]
        E = next_eval(plan, c, iso)
        floor = last_for_course.get(c, iso) if key[1] == "N" else iso
        placed = None
        for pass_ in (0, 1):
            for d in future:
                if d["date"] < floor:
                    continue
                if pass_ == 0 and E and d["date"] >= E and t["tier"] == "core" and not t.get("critical"):
                    continue
                cap_core, cap_ext = caps[d["dtype"]]
                if t["tier"] == "core" and d["core_min"] + t["minutes"] > cap_core + 70:
                    continue
                if d["ext_min"] + t["minutes"] > cap_ext + 20:
                    continue
                placed = d
                break
            if placed:
                break
        if placed is None:
            dropped.append((d0, t))
            continue
        placed["tasks"].append(t)
        d0["tasks"].remove(t)
        t.setdefault("orig_date", d0["date"])
        recalc(placed)
        recalc(d0)
        if key[1] == "N":
            last_for_course[c] = placed["date"]
        moves.append((d0["date"], placed["date"], t))
    # ---- önkoşul onarımı: taşınan bir öğrenme bloğundan SONRA gelen blok daha erkene kalmasın (zorunlu önkoşullar atlanmaz)
    def locate(bid):
        for d in plan["days"]:
            for t in d["tasks"]:
                if t["block"] == bid:
                    return d, t
        return None, None

    def slot(t, floor):
        for d in future:
            if d["date"] < floor:
                continue
            cap_core, cap_ext = caps[d["dtype"]]
            if t["tier"] == "core" and d["core_min"] + t["minutes"] > cap_core + 70:
                continue
            if d["ext_min"] + t["minutes"] > cap_ext + 20:
                continue
            return d
        return None

    pushed = 0
    for c in {t["course"] for _, _, t in moves}:
        prev = None
        blocked = False  # sığmayan bir önkoşuldan sonra gelen bloklar da ertelenir (önkoşul atlanmaz)
        for bid in [b["id"] for b in plan["blocks"].values() if b["course"] == c and b["kind"] == "L"]:
            d, t = locate(bid)
            if t is None or sts.get(t["id"], {}).get("status") == "Completed" or d["date"] < iso:
                continue
            if blocked:
                if not any(x is t for _, x in dropped):
                    dropped.append((d, t))
                continue
            if any(x is t for _, x in dropped):
                blocked = True
                continue
            if prev and d["date"] < prev:
                nd = slot(t, prev)
                if nd is None:
                    dropped.append((d, t))
                    blocked = True
                    continue
                d["tasks"].remove(t)
                nd["tasks"].append(t)
                t.setdefault("orig_date", d["date"])
                recalc(d)
                recalc(nd)
                moves.append((d["date"], nd["date"], t))
                pushed += 1
                d = nd
            prev = d["date"]
    if pushed:
        print(f"Önkoşul sırası için {pushed} ek görev ileri itildi.")
    print(f"Bugün: {iso} · kaçan görev: {len(missed)} · taşınan: {len(moves)} · kapasite yok→Postponed: {len(dropped)} · min'e terfi (kritik): {promoted}")
    for a, b, t in moves[:40]:
        print(f"  {a} → {b} [{t['tier']}] {t['course']} {t['title'][:50]}")
    if len(moves) > 40:
        print(f"  … +{len(moves) - 40} görev daha")
    for d0, t in dropped:
        print(f"  DÜŞTÜ (Postponed) {d0['date']} {t['course']} {t['title'][:50]}")
    if not apply:
        print("Önizleme — uygulamak için --apply ekle.")
        return plan, moves, dropped
    # yedek
    bk = os.path.join(ROOT, "01_Master_Plan", "backups")
    os.makedirs(bk, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    shutil.copy(PLAN, os.path.join(bk, f"plan_{stamp}.json"))
    if os.path.exists(PROGRESS):
        shutil.copy(PROGRESS, os.path.join(bk, f"progress_{stamp}.json"))
    prog = load_progress()
    for d0, t in dropped:
        prog["tasks"][t["id"]] = {"status": "Postponed", "note": f"Replan {iso}: sınav geçti veya kapasite yok — gerekirse kümülatif tekrara kat"}
    for a, b, t in moves:
        st = prog["tasks"].setdefault(t["id"], {"status": "Not Started", "note": ""})
        st["note"] = (st.get("note") or "") + f" [taşındı {a}→{b}]"
        if st["status"] in ("Postponed", "Blocked"):
            st["status"] = "Not Started"
    prog["calendar_sequence"] = prog.get("calendar_sequence", 0) + 1
    prog["last_replan"] = iso
    prog["history"].append(dict(date=iso, moved=len(moves), dropped=len(dropped), promoted=promoted))
    save_plan(plan)
    save_progress(prog)
    import build_ics, build_xlsx, build_pdf, build_md, build_simple, build_site
    for m in (build_ics, build_xlsx, build_md, build_pdf, build_simple, build_site):
        m.main()
    print("Plan güncellendi. ICS'yi tekrar içe aktar: UID'ler sabit olduğu için etkinlikler GÜNCELLENİR (mükerrer olmaz).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--from-xlsx", action="store_true")
    a = ap.parse_args()
    replan(date.fromisoformat(a.today), a.apply, a.from_xlsx)

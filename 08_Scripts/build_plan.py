# -*- coding: utf-8 -*-
"""plan_data.py -> plan.json (günlük görevler, tekrarlar, öncelikler)."""
import json
import os
from datetime import date, timedelta
from plan_data import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TR_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
TR_MON = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def d2s(d):
    return d.isoformat()


def s2d(s):
    return date.fromisoformat(s)


def day_type(d):
    return "sunday" if d.weekday() == 6 else "saturday" if d.weekday() == 5 else "weekday"


def all_days():
    d = START
    while d <= END:
        yield d
        d += timedelta(days=1)


def urgency(course, d):
    best = None
    for ds, w in NEXT_EVAL.get(course, []):
        dd = (s2d(ds) - d).days
        if dd >= 0 and (best is None or dd < best[0]):
            best = (dd, w)
    if best is None:
        return 0.0, 999, 0
    dd, w = best
    u = 1.0 if dd <= 3 else .85 if dd <= 7 else .65 if dd <= 14 else .45 if dd <= 21 else .3 if dd <= 35 else .15
    return u, dd, w


def ranking(d):
    """Öncelik puanı: aciliyet .35, zorluk .25, not ağırlığı .20, önkoşul .10, birikmiş eksik .10 (başlangıçta 0).
    Sınava ≤3 gün kalan ders puandan bağımsız en üste çıkar."""
    out = []
    for c, m in COURSES.items():
        if c not in NEXT_EVAL:
            continue
        u, dd, w = urgency(c, d)
        score = .35 * u + .25 * m["diff"] / 5 + .20 * min(w / 40, 1) + .10 * m["prereq"] + .10 * 0
        if dd <= 3:
            score += 10 + (3 - dd)  # en yakın sınav her zaman önde
        elif dd <= 7:
            score += 5 - dd * 0.05  # yaklaşan sınav: en yakın olan önde
        out.append((score, c, dd))
    out.sort(reverse=True)
    return out


def rev_items(placed, d):
    """d günü için tekrar listesi: [(interval, block_id)] (yalnızca d'den ÖNCE yerleşmiş öğrenme blokları)."""
    items = []
    for bid, bd in placed.items():
        if not BLOCKS[bid]["rev"]:
            continue
        delta = (d - bd).days
        if delta in REV_INTERVALS:
            items.append((delta, bid))
    return sorted(items)


def rev_minutes(items):
    core = sum(8 for i, _ in items if i in (1, 3))
    ext = sum(8 for i, _ in items if i in (7, 14))
    return core, ext


def build():
    placed = {}  # block -> date
    sched = {}   # date -> dict(core=[], ext=[])
    for d in all_days():
        sched[d] = dict(core=[], ext=[])
    for ds, (core, ext) in MANUAL.items():
        d = s2d(ds)
        sched[d]["core"] = list(core)
        sched[d]["ext"] = list(ext)
        for b in core + ext:
            placed[b] = d

    # ---- otomatik kuyruk: günü günü EDF (en yakın son hedef önce), ders başına günde ≤2 blok
    queues = {}
    for c, q in QUEUES.items():
        win = 0 if c[:2] in ("F-", "K-") else 6  # öğrenme blokları son hedefe en fazla 6 gün kala serbest kalır (dengeli dağılım)
        queues[c] = [(b, max(s2d("2026-" + r), s2d("2026-" + t) - timedelta(days=win)) if win else s2d("2026-" + r), s2d("2026-" + t)) for b, r, t in q]
    d = AUTO_START
    while d <= END:
        if d in (s2d(x) for x in MANUAL):  # manuel günler (ör. 27 Kas) de kapasite kullanır
            pass
        core_cap, ext_cap = CAPS[day_type(d)]
        rc, re_ = rev_minutes(rev_items({b: x for b, x in placed.items() if x < d}, d))
        used_core = sum(BLOCKS[b]["minutes"] for b in sched[d]["core"]) + rc
        used_ext = used_core + sum(BLOCKS[b]["minutes"] for b in sched[d]["ext"]) + re_
        per_course = {}
        for tier, cap in (("core", core_cap), ("ext", ext_cap)):
            while True:
                cands = []
                for c, q in queues.items():
                    if not q:
                        continue
                    b, rel, due = q[0]
                    if rel > d or per_course.get(BLOCKS[b]["course"], 0) >= 2:
                        continue
                    cands.append((due, b, c))
                if not cands:
                    break
                cands.sort()
                due, b, c = cands[0]
                m = BLOCKS[b]["minutes"]
                cur = used_core if tier == "core" else used_ext
                if cur + m > cap and not (cur == (rc if tier == "core" else used_core) and tier == "core"):
                    break
                # ext'e yalnızca yakın hedefli (≤4 gün) veya çok erken serbest kalmış işleri çek
                if tier == "ext" and (due - d).days > 2:
                    break
                queues[c].pop(0)
                sched[d][tier].append(b)
                placed[b] = d
                cc = BLOCKS[b]["course"]
                per_course[cc] = per_course.get(cc, 0) + 1
                used_core += m if tier == "core" else 0
                used_ext += m
            used_ext = max(used_ext, used_core)
        d += timedelta(days=1)
    leftover = [b for q in queues.values() for b, _, _ in q]
    assert not leftover, f"Yerleşmeyen bloklar: {leftover}"

    # ---- görev listesi
    days = []
    tid = {}
    for d in all_days():
        rk = ranking(d)
        top = [c for _, c, dd in rk]
        rank_of = {c: i for i, c in enumerate(top)}
        near = {c: dd for _, c, dd in rk}
        tasks = []

        def pr(course, kind):
            if course == "GENEL":
                return "P1"
            r = rank_of.get(course, 9)
            if near.get(course, 99) <= 3 or r == 0:
                return "P1"
            return "P2" if r <= 2 else "P3"

        n = 0
        for tier in ("core", "ext"):
            for b in sched[d][tier]:
                B = BLOCKS[b]
                n += 1
                tasks.append(dict(id=f"{d2s(d)}-{n:02d}", block=b, course=B["course"], tier=tier, kind=B["kind"],
                                  minutes=B["minutes"], priority=pr(B["course"], B["kind"]), title=B["title"],
                                  text=f"{B['title']} — {B['what']}. ▸ {B['practice']}", ref=B["ref"] if B["kind"] in "LP" else "",
                                  critical=(b[:2] in ("U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", "VD", "BP", "SH", "UP", "AS") or b[0] in "UV" and b != "V1"),
                                  topics=B["topics"]))
        ri = rev_items({b: x for b, x in placed.items() if x < d}, d)
        for tier, ivs in (("core", (1, 3)), ("ext", (7, 14))):
            by_course = {}
            for iv, b in ri:
                if iv in ivs:
                    by_course.setdefault(BLOCKS[b]["course"], []).append((iv, b))
            for c, lst in by_course.items():
                n += 1
                names = "; ".join(f"{BLOCKS[b]['title']} (D+{iv})" for iv, b in lst)
                tasks.append(dict(id=f"{d2s(d)}-{n:02d}", block="REV:" + ",".join(b for _, b in lst), course=c, tier=tier, kind="T",
                                  minutes=8 * len(lst), priority="P3" if near.get(c, 99) > 3 else "P2",
                                  title="Tekrar", text=f"Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): {names}", ref="", topics=names))
        core_min = sum(t["minutes"] for t in tasks if t["tier"] == "core")
        ext_min = sum(t["minutes"] for t in tasks if t["tier"] == "ext")
        # ana odak: çekirdek dakikası en yüksek ders
        mins = {}
        for t in tasks:
            if t["tier"] == "core" and t["course"] != "GENEL":
                mins[t["course"]] = mins.get(t["course"], 0) + t["minutes"]
        main = max(mins, key=mins.get) if mins else top[0]
        nxt = next(((c, dd) for _, c, dd in rk if c == main), (main, 0))
        ev = [e for e in EVALS if e["date"] and e["course"] == main and s2d(e["date"]) >= d]
        ev.sort(key=lambda e: e["date"])
        goal = f"Ana odak: {main}"
        if ev:
            goal += f" → {ev[0]['title']} ({(s2d(ev[0]['date']) - d).days} gün)"
        firsts = [t["title"] for t in tasks if t["tier"] == "core" and t["course"] == main and t["kind"] != "T"][:2]
        if firsts:
            goal += " · " + " + ".join(firsts)
        days.append(dict(date=d2s(d), weekday=TR_DAYS[d.weekday()], dtype=day_type(d), core_min=core_min, ext_min=core_min + ext_min,
                         ranking=[c for c in top if c != "GENEL"], main=main, goal=goal, tasks=tasks,
                         phase=next(p[2] for p in PHASES if p[0] <= d2s(d) <= p[1])))
    plan = dict(version=1, start=d2s(START), end=d2s(END), courses=COURSES, evals=EVALS, blocks=BLOCKS, days=days,
                phases=PHASES, weeks=WEEKS, caps=CAPS)
    return plan


if __name__ == "__main__":
    plan = build()
    out = os.path.join(ROOT, "01_Master_Plan", "plan.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    cap_bad = []
    for dd in plan["days"]:
        cc, ec = CAPS[dd["dtype"]]
        flag = ""
        if dd["core_min"] > cc + 70:
            flag += " CORE+"
        if dd["ext_min"] > ec + 40:
            flag += " EXT+"
        print(dd["date"], dd["weekday"][:3], f"core {dd['core_min']:3d} ext {dd['ext_min']:3d}", dd["main"], flag)

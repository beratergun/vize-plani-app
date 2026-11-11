# -*- coding: utf-8 -*-
"""Ortak yükleme/kaydetme: plan.json (görev programı) + progress.json (durumlar)."""
import json
import os
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAN = os.path.join(ROOT, "01_Master_Plan", "plan.json")
PROGRESS = os.path.join(ROOT, "06_Progress_Tracker", "progress.json")
STATUSES = ["Not Started", "In Progress", "Completed", "Postponed", "Blocked"]
TR_MON = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def load_plan():
    with open(PLAN, encoding="utf-8") as f:
        return json.load(f)


def save_plan(plan):
    with open(PLAN, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)


def load_progress(plan=None):
    """progress.json yoksa tüm görevler 'Not Started' ile oluşturulur; mevcut durumlar KORUNUR."""
    prog = {"version": 1, "calendar_sequence": 0, "last_replan": None, "history": [], "tasks": {}}
    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding="utf-8") as f:
            prog.update(json.load(f))
    if plan:
        for d in plan["days"]:
            for t in d["tasks"]:
                prog["tasks"].setdefault(t["id"], {"status": "Not Started", "note": ""})
    return prog


def save_progress(prog):
    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=1)


def fmt_date(s):
    d = date.fromisoformat(s)
    return f"{d.day} {TR_MON[d.month]}"


def hours(m):
    h = m / 60
    return f"{h:.1f}".replace(".", ",") + " sa"

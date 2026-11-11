# -*- coding: utf-8 -*-
"""Tüm çıktıları üretir.  py build_all.py          → mevcut plan.json'dan
                         py build_all.py --regen  → plan_data.py'den planı baştan kur (durumlar blok bazında korunur)"""
import os
import sys
from common import *
import build_plan


def regen():
    old_plan = load_plan() if os.path.exists(PLAN) else None
    old_prog = load_progress() if os.path.exists(PROGRESS) else None
    by_block = {}
    if old_plan and old_prog:
        for d in old_plan["days"]:
            for t in d["tasks"]:
                st = old_prog["tasks"].get(t["id"])
                if st and st["status"] != "Not Started":
                    by_block[t["block"]] = st
    plan = build_plan.build()
    save_plan(plan)
    prog = {"version": 1, "calendar_sequence": (old_prog or {}).get("calendar_sequence", 0) + (1 if old_prog else 0),
            "last_replan": (old_prog or {}).get("last_replan"), "history": (old_prog or {}).get("history", []), "tasks": {}}
    for d in plan["days"]:
        for t in d["tasks"]:
            prog["tasks"][t["id"]] = dict(by_block.get(t["block"], {"status": "Not Started", "note": ""}))
    save_progress(prog)
    print(f"Plan yeniden kuruldu; {len(by_block)} blok durumu korundu.")


if __name__ == "__main__":
    import os
    if "--regen" in sys.argv or not os.path.exists(PLAN):
        regen()
    prog = load_progress(load_plan())
    save_progress(prog)
    import build_ics, build_xlsx, build_md, build_pdf, build_simple, build_site
    for m in (build_ics, build_xlsx, build_md, build_pdf, build_simple, build_site):
        m.main()
    print("Tamam.")

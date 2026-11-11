# -*- coding: utf-8 -*-
"""Excel'de işaretlediğin durumları (Daily Tasks sayfası: ID, Durum, Not) progress.json'a aktarır.
Kullanım:  py sync_from_xlsx.py [yol/Academic_Study_Tracker_2026.xlsx]
Excel kaydettikten sonra paylaşılan-dize (sharedStrings) biçimini de okur."""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from common import *

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def col_idx(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def read_sheet(path, sheet_name):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2target = {r.get("Id"): r.get("Target") for r in rels}
    target = None
    for s in wb.find("m:sheets", NS):
        if s.get("name") == sheet_name:
            target = rid2target[s.get("{%s}id" % NS["r"])]
    if target is None:
        raise SystemExit(f"'{sheet_name}' sayfası bulunamadı")
    target = target.lstrip("/")
    sheet = ET.fromstring(z.read(target if target.startswith("xl/") else "xl/" + target))
    rows = []
    for row in sheet.find("m:sheetData", NS):
        cells = {}
        for c in row:
            t = c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            else:
                v = c.find("m:v", NS)
                val = None if v is None else v.text
                if t == "s" and val is not None:
                    val = shared[int(val)]
            cells[col_idx(c.get("r"))] = val
        rows.append(cells)
    return rows


def sync(path, quiet=False):
    plan = load_plan()
    prog = load_progress(plan)
    rows = read_sheet(path, "Daily Tasks")
    changed = bad = 0
    for cells in rows[1:]:
        tid, st, note = cells.get(1), cells.get(10), cells.get(11) or ""
        if not tid or tid not in prog["tasks"]:
            continue
        if st not in STATUSES:
            bad += 1
            continue
        cur = prog["tasks"][tid]
        if cur["status"] != st or cur.get("note", "") != note:
            changed += 1
            cur["status"], cur["note"] = st, note
    save_progress(prog)
    if not quiet:
        print(f"{changed} görev güncellendi, {bad} geçersiz durum atlandı.")
    return changed


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "06_Progress_Tracker", "Academic_Study_Tracker_2026.xlsx")
    sync(p)

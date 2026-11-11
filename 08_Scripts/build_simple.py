# -*- coding: utf-8 -*-
"""SADE PLAN: her hafta tek sayfa, her gün birkaç kısa satır. plan.json'dan üretilir."""
import os
import subprocess
from datetime import date
from html import escape as E
from common import *
from build_pdf import render_pdf

SHORT = {"BIO110": "BIO", "CMPE371": "SİNYAL", "CMPE327": "OTOMAT", "CMPE421": "YZ", "CMPE453": "MİKRO", "CMPE499": "STAJ", "GENEL": "GENEL"}
CSS = """
@page { size: A4; margin: 11mm 11mm 13mm 11mm;
  @bottom-center { content: "Sade Plan · Sayfa " counter(page) " / " counter(pages); font: 8pt 'Segoe UI', Arial; color:#555; } }
* { box-sizing:border-box; } body { font: 8.8pt/1.25 'Segoe UI', Arial, sans-serif; color:#111; margin:0; }
h1 { font-size:20pt; margin:0 0 2mm; } h2 { font-size:15pt; margin:0; }
.pb { break-after: page; }
.head { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2pt solid #111; padding-bottom:1.5mm; margin-bottom:2.5mm; }
.sub { font-size:9pt; color:#333; }
.banner { border:1.4pt solid #111; padding:1.6mm 3mm; margin-bottom:3mm; font-weight:600; }
.day { display:grid; grid-template-columns: 27mm 1fr 17mm; border:1pt solid #111; margin-bottom:1.5mm; break-inside:avoid; }
.day .d { background:#e9e9e9; padding:1mm 2mm; border-right:1pt solid #111; }
.day .d b { font-size:11pt; display:block; } .day .d span { font-size:8pt; color:#333; }
.day .m { padding:.9mm 2.4mm; } .day .t { padding:1.4mm 2mm; text-align:center; border-left:1pt solid #111; font-size:9pt; }
.row { margin:.15mm 0; } .tag { display:inline-block; min-width:14mm; text-align:center; font-weight:700; font-size:8pt; border:.8pt solid #111; border-radius:1.6mm; padding:0 1mm; margin-right:1.6mm; }
.main .tag { background:#111; color:#fff; }
.box { display:inline-block; width:3.8mm; height:3.8mm; border:.9pt solid #111; vertical-align:-.7mm; margin-right:1.6mm; }
.opt { margin-top:.7mm; padding-top:.5mm; border-top:.6pt dotted #777; font-size:7.8pt; color:#333; }
.exam { background:#111; color:#fff; font-weight:700; padding:.8mm 2mm; margin:0 0 1.2mm; font-size:9.5pt; }
.rule { border:1pt solid #111; padding:1.4mm 3mm; margin-top:2.5mm; } .rule li { margin:1mm 0; }
table { border-collapse:collapse; width:100%; } th, td { border:.7pt solid #777; padding:1.2mm 2mm; text-align:left; } th { background:#e6e6e6; }
.cover { text-align:center; padding-top:10mm; } .cover h1 { font-size:30pt; }
"""


def short_title(t):
    s = t["title"]
    for a, b in (("The Chemical Context of Life", "Chemical Context of Life"), ("Programming AVR (C + bit işlemleri)", "AVR programlama + bit işlemleri"),
                 ("Course overview + ATmega328P architecture", "ATmega328P mimari"), ("Central concepts + mathematical preliminaries", "Temel kavramlar + matematik önbilgi")):
        s = s.replace(a, b)
    return s[:52]


def line(plan, t, sts):
    if t["kind"] == "T":
        ids = t["block"].replace("REV:", "")
        names = [plan["blocks"][b]["title"][:26] for b in ids.split(",") if b in plan["blocks"]]
        txt = "Tekrar (kapalı kitap): " + "; ".join(names[:3]) + (f" +{len(names) - 3}" if len(names) > 3 else "")
    else:
        txt = short_title(t)
    star = "★ " if t.get("critical") else ""
    done = sts.get(t["id"], {}).get("status") == "Completed"
    box = "<span class='box' style='background:#111'></span>" if done else "<span class='box'></span>"
    return f"<div class='row'>{box}<span class='tag'>{SHORT[t['course']]}</span>{star}{E(txt)} <span class='sub'>({t['minutes']} dk)</span></div>"


def main():
    plan = load_plan()
    prog = load_progress(plan)
    sts = prog["tasks"]
    ev_by_day = {}
    for e in plan["evals"]:
        if e["date"] and not e["end"]:
            ev_by_day.setdefault(e["date"], []).append(e)
    h = []
    A = h.append
    A("<div class='cover pb'><div class='sub'>BİLGİSAYAR MÜHENDİSLİĞİ · 2026 GÜZ</div><h1>SADE PLAN<br>Hafta hafta · gün gün</h1>"
      "<p style='font-size:11pt'>30 Ekim – 31 Aralık 2026 · 14. haftanın sonuna kadar (final hazırlığı dahil) · Hedef: AA'ya yönelik düzenli çalışma</p>"
      "<table style='margin-top:6mm;text-align:left'><tr><th>Tarih</th><th>Sınav / teslim</th><th>Durum</th></tr>"
      "<tr><td>3 Kasım</td><td>BIO110 Midterm 1</td><td>senin tarihin</td></tr>"
      "<tr><td>12 Kasım 18:00–20:00</td><td>CMPE453 Midterm</td><td>syllabus (kesin)</td></tr>"
      "<tr><td>15 Kasım 13:00–14:00</td><td>CMPE327 Quiz</td><td>hoca duyurusu</td></tr>"
      "<tr><td>20 Kasım 18:00–20:00</td><td>CMPE421 Midterm</td><td>hoca duyurusu</td></tr>"
      "<tr><td>26 Kasım 23:59</td><td>CMPE421 Assignment-1 (Code + Report + Q&A)</td><td>LMS</td></tr>"
      "<tr><td>29 Kasım 13:00–15:00</td><td>CMPE327 Midterm (W1–W8)</td><td>hoca duyurusu</td></tr>"
      "<tr><td>30 Kasım 18:00–20:00</td><td>CMPE371 Midterm</td><td>hoca duyurusu</td></tr>"
      "<tr><td>22 Kasım / 29 Kasım</td><td>CMPE499 Rapor / Video (plan: 20 ve 25 Kasım'da yükle)</td><td>syllabus (kesin)</td></tr>"
      "<tr><td>23–27 Kasım</td><td>CMPE371 Midterm · BIO110 Midterm 2 (26/27)</td><td>Teyit Bekliyor</td></tr>"
      "<tr><td>7–18 Aralık</td><td>CMPE371 Quiz 1 · CMPE327 Quiz-2 · BIO proje sunumu (10–31 Ara)</td><td>Teyit Bekliyor</td></tr>"
      "<tr><td>Final haftası</td><td>Tüm finaller</td><td>tarih duyurulacak</td></tr></table>"
      "<div class='rule' style='text-align:left'><b>Her gün 3 kural</b><ol><li><b>Siyah etiketli ders</b> o günün ana işi; önce onu bitir.</li>"
      "<li>Üstteki satırlar <b>zorunlu</b>, \"İstersen\" altındakiler enerjin varsa.</li><li>Yetişmediysen ertesi güne yığma; yalnızca zorunlu satırları yap, sonra yeniden planla.</li></ol></div></div>")
    for a, b, name in plan["weeks"]:
        days = [d for d in plan["days"] if a <= d["date"] <= b]
        wk_ev = [e for e in plan["evals"] if e["date"] and e["end"] and not (e["end"] < a or e["date"] > b)]
        A(f"<div class='pb'><div class='head'><h2>{name}</h2><span class='sub'>{fmt_date(a)} – {fmt_date(b)}</span></div>")
        if wk_ev:
            A("<div class='banner'>Bu hafta (günü teyit bekliyor): " + " · ".join(E(e["title"]) for e in wk_ev) + "</div>")
        for d in days:
            dt = date.fromisoformat(d["date"])
            tasks = [t for t in d["tasks"] if t["tier"] == "core"]
            extra = [t for t in d["tasks"] if t["tier"] == "ext"]
            main_c = d["main"]
            A(f"<div class='day'><div class='d'><b>{dt.day} {TR_MON[dt.month]}</b><span>{d['weekday']}</span></div><div class='m'>")
            for e in ev_by_day.get(d["date"], []):
                tm = f" {e['time'][0]}–{e['time'][1]}" if e.get("time") else ""
                A(f"<div class='exam'>▲ {E(e['title'])}{tm}</div>")
            work = sorted([t for t in tasks if t["kind"] != "T"], key=lambda t: t["course"] != main_c)
            revs = [t for t in tasks if t["kind"] == "T"]
            for t in work:
                A(("<div class='main'>" if t["course"] == main_c else "<div>") + line(plan, t, sts) + "</div>")
            if revs:
                rm = sum(t["minutes"] for t in revs)
                rc = " · ".join(dict.fromkeys(SHORT[t["course"]] for t in revs))
                done = all(sts.get(t["id"], {}).get("status") == "Completed" for t in revs)
                bx = "<span class='box' style='background:#111'></span>" if done else "<span class='box'></span>"
                A(f"<div class='row'>{bx}<span class='tag'>TEKRAR</span>kapalı kitap, önceki günlerin konuları: {rc} <span class='sub'>({rm} dk)</span></div>")
            opt = [t for t in extra if t["kind"] != "T"]
            if opt:
                A("<div class='opt'><b>İstersen:</b> " + " · ".join(f"{SHORT[t['course']]} {E(short_title(t))}" for t in opt[:4]) + "</div>")
            A(f"</div><div class='t'><b>{d['core_min'] // 60}s {d['core_min'] % 60:02d}</b><br><span class='sub'>zorunlu</span></div></div>")
        A("<div class='rule'><b>Hafta sonu:</b> bitirdiğin satır sayısı ____ / ____ &nbsp; En zayıf konu: ______________ &nbsp; Gelecek hafta ilk iş: ______________</div></div>")
    import syllabus as _SY
    A("<div><div class='head'><h2>Syllabus haftalık konu haritası</h2><span class='sub'>Hafta 1 = 28 Eylül · her dersin konusunun ilk parçası; ayrıntı sitede</span></div>" + _SY.html_grid(E) + "<p class='sub'>Syllabus dosyalarından alındı; hocanın güncel programı değişebilir. Ayrıntılı tablo: Dersler sekmesi.</p></div>")
    html = "<!doctype html><html lang='tr'><head><meta charset='utf-8'><title>Sade Plan</title><style>" + CSS + "</style></head><body>" + "".join(h) + "</body></html>"
    out = os.path.join(ROOT, "05_Printable_PDF")
    hp, pp = os.path.join(out, "SADE_PLAN_Hafta_Hafta.html"), os.path.join(out, "SADE_PLAN_Hafta_Hafta.pdf")
    open(hp, "w", encoding="utf-8").write(html)
    render_pdf(hp, pp)
    print("Sade PDF yazıldı:", os.path.getsize(pp), "bayt")


if __name__ == "__main__":
    main()

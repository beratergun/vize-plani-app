# -*- coding: utf-8 -*-
"""plan.json + progress.json -> A4 yazdırılabilir HTML -> Edge (headless) ile PDF. Siyah-beyaz yazıcıya uygun."""
import os
import subprocess
from datetime import date
from html import escape as E
from common import *

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ORDER = ["BIO110", "CMPE371", "CMPE327", "CMPE421", "CMPE453", "CMPE499"]
TIER = {"core": "●", "ext": "○"}
STATUS_TR = {"confirmed": "KESİN", "user": "KULLANICI TEYİTLİ", "tentative": "TEYİT BEKLİYOR", "window": "TEYİT BEKLİYOR", "unknown": "DUYURULACAK"}

CSS = """
@page { size: A4; margin: 12mm 11mm 14mm 11mm;
  @bottom-center { content: "Academic Success Plan · 2026 Fall · Sayfa " counter(page) " / " counter(pages); font: 8pt 'Segoe UI', Arial; color:#555; }
}
* { box-sizing: border-box; }
body { font: 9pt/1.32 'Segoe UI', Arial, sans-serif; color:#111; margin:0; }
h1 { font-size: 22pt; margin: 0 0 2mm; letter-spacing:-.3px; }
h2 { font-size: 13pt; margin: 0 0 2.5mm; padding-bottom:1.2mm; border-bottom: 1.6pt solid #111; }
h3 { font-size: 10pt; margin: 3mm 0 1.2mm; }
.pb { break-after: page; }
.small { font-size: 7.6pt; color:#444; }
table { border-collapse: collapse; width:100%; }
th, td { border: .6pt solid #777; padding: 1.2mm 1.6mm; vertical-align: top; }
th { background:#e6e6e6; font-weight:700; text-align:left; }
.cover { text-align:center; padding-top:22mm; }
.cover .big { font-size: 34pt; font-weight:800; letter-spacing:-1px; line-height:1.05; }
.cover .goal { margin:8mm auto; padding:4mm 6mm; border:1.6pt solid #111; width:150mm; font-size:11pt; font-weight:700; }
.cover table { width:150mm; margin: 6mm auto 0; text-align:left; }
.tag { display:inline-block; border:.8pt solid #111; border-radius:2mm; padding:0 1.4mm; font-weight:700; font-size:7.6pt; }
.tagk { background:#111; color:#fff; }
.box { display:inline-block; width:3.6mm; height:3.6mm; border:.9pt solid #111; vertical-align:-0.7mm; margin-right:1.4mm; }
.grid2 { display:grid; grid-template-columns: 1fr 1fr; gap:3mm; }
.card { border:.8pt solid #111; padding:1.4mm 2mm; margin-bottom:2.2mm; break-inside: avoid; }
.card table td, .card table th { font-size:7.9pt; padding:.6mm 1.4mm; }
.dots { letter-spacing:1px; font-size:10pt; }
.day { border:1pt solid #111; margin-bottom:3.2mm; break-inside: avoid; }
.dh { display:flex; justify-content:space-between; align-items:center; background:#111; color:#fff; padding:1mm 2.2mm; font-weight:700; }
.dh .t { font-size:10pt; }
.dg { padding:1.2mm 2.2mm; border-bottom:.6pt solid #777; font-weight:600; background:#f1f1f1; }
.day table td, .day table th { border-left:none; border-right:none; padding:.8mm 1.4mm; font-size:8.3pt; }
.day td.c { width:6mm; text-align:center; }
.day td.m { width:9mm; text-align:right; white-space:nowrap; }
.day td.k { width:15mm; font-weight:700; white-space:nowrap; }
.crit { font-weight:800; }
.dfoot { display:flex; gap:4mm; padding:1mm 2.2mm; border-top:.6pt solid #777; font-size:7.6pt; flex-wrap:wrap; }
.week { border:1.2pt dashed #111; padding:2mm 3mm; margin-bottom:4mm; break-inside: avoid; }
.week .lines span { display:block; border-bottom:.5pt solid #999; height:5.2mm; }
.sep { margin: 2mm 0 3mm; font-weight:800; font-size:11pt; border-bottom:1pt solid #111; }
.rm td { height:8mm; }
"""


def d(s):
    return date.fromisoformat(s)


def dots(n):
    return "●" * n + "○" * (5 - n)


def build_html(plan, prog):
    sts = {k: v["status"] for k, v in prog["tasks"].items()}
    h = []
    A = h.append
    first, last = fmt_date(plan["start"]), fmt_date(plan["end"])
    # ------------------------------------------------ kapak
    A("<div class='cover pb'><div class='small'>2026 FALL SEMESTER · BİLGİSAYAR MÜHENDİSLİĞİ</div>"
      "<div class='big'>ACADEMIC<br>SUCCESS PLAN</div>"
      f"<div style='margin-top:4mm;font-size:12pt'>Başlangıç: <b>30 Ekim 2026 (Cuma)</b> · Dönem haftası: 5 · Plan: {first} – {last} 2026</div>"
      "<div class='goal'>HEDEF: AA odaklı akademik başarı<br><span style='font-weight:400;font-size:9pt'>Garanti değil — sistem bu hedefe hizmet edecek biçimde optimize edildi.</span></div>"
      "<table><tr><th>Ders</th><th>Ad</th><th>Zorluk</th></tr>")
    for c in ORDER:
        m = plan["courses"][c]
        A(f"<tr><td><b>{c}</b></td><td>{E(m['name'])}</td><td class='dots'>{dots(m['diff'])}</td></tr>")
    A("</table><div class='small' style='margin-top:8mm'>Nasıl kullanılır: her gün sayfasındaki kutuları işaretle · ● = minimum plan (mutlaka) · ○ = genişletilmiş (enerji varsa) · "
      "★ = kritik teslim işi · Aksayan günü yığma, REPLAN_GUIDE adımlarını uygula.</div></div>")

    # ------------------------------------------------ yönetici özeti
    A("<div><h2>1 · Yönetici özeti</h2><div class='grid2'><div>")
    A("<h3 style='margin-top:0'>Kritik tarihler</h3><table><tr><th>Tarih</th><th>Olay</th><th>Durum</th></tr>")
    upcoming = sorted([e for e in plan["evals"] if e["date"]], key=lambda e: e["date"])
    for e in upcoming:
        rng = fmt_date(e["date"]) + (f" – {fmt_date(e['end'])}" if e["end"] else "") + (f" {e['time'][0]}–{e['time'][1]}" if e.get("time") else "")
        A(f"<tr><td>{rng}</td><td>{E(e['title'])}</td><td><span class='tag{' tagk' if e['status'] in ('confirmed','user') else ''}'>{STATUS_TR[e['status']]}</span></td></tr>")
    A("<tr><td>—</td><td>Final sınavları (W14 sonrası)</td><td><span class='tag'>DUYURULACAK</span></td></tr></table>")
    A("<p class='small'>Not: <b>BIO110</b> midterm syllabus'ta 5–6 Kasım satırında görünüyor; senin tarihin (3 Kasım) esas alındı. <b>CMPE327</b> quiz 15 Kasım 13:00–14:00 ve midterm 29 Kasım 13:00–15:00 (Week 08 dahil), <b>CMPE421</b> midterm 20 Kasım 18:00–20:00, <b>CMPE421</b> Assignment-1 26 Kasım 23:59, <b>CMPE371</b> midterm 30 Kasım 18:00–20:00 (hoca duyuruları; kullanıcı bildirimi). "
      "Kapsamlar 30 Ekim doğrulama görevinde teyit edilir.</p>")
    A("</div><div><h3 style='margin-top:0'>Öncelik sırası (dinamik)</h3>"
      "<table><tr><th>Dönem</th><th>Ana odak</th></tr>")
    for a, b, name, note in plan["phases"]:
        A(f"<tr><td>{fmt_date(a)} – {fmt_date(b)}</td><td><b>{E(name)}</b><br><span class='small'>{E(note)}</span></td></tr>")
    A("</table><h3>Çalışma yaklaşımı</h3><div class='small' style='font-size:8.3pt'>"
      "① Her konu: temel → slayt/kitap → <b>çözüme bakmadan</b> uygulama.<br>② Tekrar: D+1, D+3, D+7, D+14 (sınav yaklaşınca sıkışır).<br>"
      "③ Her yanlışın sebebi Mistake Log'a; tekrar eden hata → düzeltici çalışma.<br>④ Min plan mutlak, ekstra isteğe bağlı; dinlen, uyu.<br>"
      "⑤ Öncelik = aciliyet %35 + zorluk %25 + not ağırlığı %20 + önkoşul %10 + birikmiş eksik %10; sınava ≤3 gün kalan ders her zaman 1. sıra."
      "</div></div></div>"
      "<div class='grid2' style='margin-top:4mm'><div class='card'><b>Bir günü kaçırırsan (4 kural)</b><div class='small' style='font-size:8.3pt'>"
      "1) Yığma: kaçan ● görevleri ertesi güne ekleme. 2) Yaklaşan sınavın görevleri önce; düşük öncelikli tekrar (D+7/D+14) ertelenir. "
      "3) Zorunlu önkoşul bloklarını atlama. 4) 08_Scripts/replan.py çalıştır (REPLAN_GUIDE.md); günlük kapasite aşılmaz.</div></div>"
      "<div class='card'><b>Tekrar döngüsü (aktif hatırlama)</b><div class='small' style='font-size:8.3pt'>"
      "D+1 kısa hatırlama · D+3 · D+7 · D+14 · sınav öncesi karma. Konu iyi öğrenildiyse (≥%85) tekrar yükünü azalt, "
      "zayıfsa (&lt;%70) artır; sınav yaklaşınca döngüyü sıkıştır.</div></div>"
      "<div class='card'><b>Yanlış analizi kuralı</b><div class='small' style='font-size:8.3pt'>"
      "Her yanlış için sebebi yaz: konu bilinmiyor / formül / işlem / kavram karışıklığı / algoritma mantığı / soruyu yanlış yorumlama / dikkat. "
      "Aynı hata 2 kez tekrarlanırsa o konuya düzeltici blok ekle.</div></div>"
      "<div class='card'><b>Varsayımlar</b><div class='small' style='font-size:8.3pt'>"
      "Cumartesi kapasitesi bildirilmedi: min 3 sa, 6 saate kadar varsayıldı. Slayt/PDF paylaşılmadı → slayt referansları 'Materyal bekleniyor'. "
      "Plan 14. haftanın sonuna (31 Aralık) kadar sürer; final tarihleri duyurulunca eklenir. Saatler taahhüt değil, tahmindir.</div></div></div></div><div class='pb'></div>")

    # ------------------------------------------------ yol haritası
    A("<h2>2 · Akademik yol haritası (hafta hafta)</h2><table><tr><th style='width:22mm'>Hafta</th>")
    for c in ORDER:
        A(f"<th>{c}</th>")
    A("</tr>")
    for a, b, name in plan["weeks"]:
        A(f"<tr><td><b>{name}</b><br><span class='small'>{fmt_date(a)}–{fmt_date(b)}</span></td>")
        for c in ORDER:
            items, evs = [], []
            for dd in plan["days"]:
                if a <= dd["date"] <= b:
                    for t in dd["tasks"]:
                        if t["course"] == c and t["kind"] in "LPWR" and t["tier"] == "core" and t["block"] in plan["blocks"]:
                            tt = plan["blocks"][t["block"]]["topics"]
                            if tt not in items and len(items) < 3:
                                items.append(tt)
            for e in plan["evals"]:
                if e["course"] == c and e["date"] and not (e["end"] or e["date"]) < a and e["date"] <= b:
                    evs.append(f"<b>▲ {E(e['title'].split(' (')[0][len(c) + 1:] or e['title'])}</b>")
            txt = "<br>".join(evs + [E(i[:40]) for i in items]) or "—"
            A(f"<td class='small' style='font-size:7.4pt;line-height:1.22'>{txt}</td>")
        A("</tr>")
    A("</table><p class='small'>▲ = sınav/teslim (Teyit Bekliyor olanlar dahil — kesin tarih için Exam Countdown'a bak). Final sınavları W14 sonrası; tarihleri duyurulunca plan güncellenir.</p><div class='pb'></div>")

    # ------------------------------------------------ ders analizi
    A("<h2>3 · Ders bazlı analiz</h2>")
    info = COURSE_INFO
    for c in ORDER:
        m, x = plan["courses"][c], info[c]
        A(f"<div class='card'><b style='font-size:10.5pt'>{c} — {E(m['name'])}</b> &nbsp; <span class='dots'>{dots(m['diff'])}</span> "
          f"<span class='small'>zorluk {m['diff']}/5</span><table style='margin-top:1.2mm'>"
          f"<tr><th style='width:24mm'>Değerlendirme</th><td>{E(x['eval'])}</td></tr>"
          f"<tr><th>Sınav/teslim</th><td>{E(x['dates'])}</td></tr>"
          f"<tr><th>Önkoşul</th><td>{E(x['pre'])}</td></tr>"
          f"<tr><th>Çalışma yaklaşımı</th><td>{E(m['method'])}</td></tr>"
          f"<tr><th>Riskler</th><td>{E(x['risk'])}</td></tr></table></div>")
    A("<div class='pb'></div>")

    # ------------------------------------------------ günlük sayfalar
    A("<h2>4 · Günlük çalışma sayfaları</h2><div class='small' style='margin-bottom:2mm'>● min plan · ○ genişletilmiş · ★ kritik · P1/P2/P3 öncelik · her satırın kutusunu bitirince işaretle.</div>")
    wk_end = {b: (name, a) for a, b, name in plan["weeks"]}
    for dd in plan["days"]:
        dt = d(dd["date"])
        label = {"weekday": "Hafta içi", "saturday": "Cumartesi", "sunday": "Pazar"}[dd["dtype"]]
        planlbl = f"Min ≈{hours(dd['core_min'])} · Genişletilmiş ≈{hours(dd['ext_min'])}" + (" · Pazar: 7–8 sa kapasite" if dd["dtype"] == "sunday" else "")
        A(f"<div class='day'><div class='dh'><span class='t'>{dt.day} {TR_MON[dt.month]} {dd['weekday']}</span>"
          f"<span class='small' style='color:#fff'>{label} · {planlbl}</span></div><div class='dg'>{E(dd['goal'])}"
          f"<span class='small'> &nbsp;|&nbsp; Sıra: {' › '.join(dd['ranking'][:3])}</span></div><table>")
        for t in dd["tasks"]:
            st = sts.get(t["id"], "Not Started")
            box = "<span class='box' style='background:#111'></span>" if st == "Completed" else "<span class='box'></span>"
            star = "<span class='crit'>★</span> " if t.get("critical") else ""
            txt = E(t["text"])
            if t["kind"] == "T":
                txt = E(t["text"])
            A(f"<tr><td class='c'>{box}</td><td class='k'>{TIER[t['tier']]} {plan['courses'][t['course']]['short']} <span class='small'>{t['priority']}</span></td>"
              f"<td>{star}{txt}</td><td class='m'>{t['minutes']}′</td></tr>")
        A("</table><div class='dfoot'><span><span class='box'></span>Konu öğrenildi</span><span><span class='box'></span>Slaytlar tamam</span>"
          "<span><span class='box'></span>Sorular çözüldü</span><span><span class='box'></span>Yanlışlar incelendi</span>"
          "<span><span class='box'></span>Tekrar yapıldı</span><span><span class='box'></span>Günlük hedef tamam</span>"
          "<span class='small' style='width:100%'>Bitirme kriteri: ● görevler işaretli + yanlış analizi yazıldı. Yapılamayanlar → ertesi güne yığma, replan et.</span></div></div>")
        if dd["date"] in wk_end:
            name, a = wk_end[dd["date"]]
            A(f"<div class='week'><b>{name} değerlendirmesi</b> ({fmt_date(a)}–{fmt_date(dd['date'])}) &nbsp; Planlanan: ____ &nbsp; Tamamlanan: ____ &nbsp; % ____"
              "<div class='lines' style='margin-top:1.5mm'><span>Eksik kalan konular:</span><span>Gelecek hafta hedefleri:</span></div></div>")

    # ------------------------------------------------ sınav hazırlık listeleri
    A("<div class='pb'></div><h2>5 · Sınav hazırlık kontrol listeleri</h2><div class='grid2'>")
    ex_list = [("BIO110 Midterm 1 — 3 Kasım", "B01–B09 (kapsam doğrula)"), ("CMPE453 Midterm — 12 Kasım 18:00–20:00", "W1–W7 (kapsam doğrula)"),
               ("CMPE327 Quiz — 15 Kasım 13:00–14:00", "kapsamı ayrıca doğrula"), ("CMPE421 Midterm — 20 Kasım 18:00–20:00", "I1–I9 (kapsam doğrula)"), ("CMPE421 Assignment-1 — 26 Kasım 23:59", "Code + Report + Q&A"), ("CMPE327 Midterm — 29 Kasım 13:00–15:00", "W1–W8 (Week 08 dahil, kesin)"),
               ("CMPE371 Midterm — 30 Kasım 18:00–20:00", "S1–S7 (kapsam doğrula)"), ("BIO110 Midterm 2 — 26/27 Kas (Teyit Bekliyor)", "B10–B16"), ("CMPE371 Quiz 1 — 7–11 Ara (Teyit Bekliyor)", "S9–S10"), ("CMPE327 Quiz-2 — 14–18 Ara (Teyit Bekliyor)", "A14–A18"), ("Finaller — tarih duyurulacak", "Tüm dönem (F-blokları)")]
    for name, scope in ex_list:
        A(f"<div class='card'><b>{E(name)}</b><div class='small'>Kapsam: {E(scope)}</div>")
        for item in ["Sorumlu konular öğrenildi", "Konu soruları çözüldü", "Karma test çözüldü", "Yanlışlar tekrar edildi",
                     "Formüller / şemalar / algoritmalar tekrarlandı", "Deneme yapıldı (süreli)", "Sınav tarih-saat-salon-kapsam doğrulandı"]:
            A(f"<div><span class='box'></span>{item}</div>")
        A("</div>")
    A("</div><div class='pb'></div>")

    # ------------------------------------------------ takip
    A("<h2>6 · İlerleme takibi</h2><h3>Genel ilerleme tablosu</h3><table><tr><th>Ders</th><th>Toplam görev</th><th>Tamamlanan</th><th>Görev %</th><th>Öğrenme skoru (test)</th><th>Eksik konular</th></tr>")
    for c in ORDER:
        n = sum(1 for dd in plan["days"] for t in dd["tasks"] if t["course"] == c)
        done = sum(1 for dd in plan["days"] for t in dd["tasks"] if t["course"] == c and sts.get(t["id"]) == "Completed")
        A(f"<tr class='rm'><td><b>{c}</b></td><td>{n}</td><td>{done}</td><td>{round(100 * done / n) if n else 0}%</td><td>% ____</td><td></td></tr>")
    A("</table><p class='small'>Görev % = tamamlanma. Öğrenme seviyesi ayrı: Güçlü ≥85 · İyi 70–84 · Eksik 50–69 · Yeniden çalış &lt;50 (başlangıç politikasıdır, garanti değildir).</p>")
    A("<h3>Yanlış defteri (hızlı)</h3><table><tr><th style='width:16mm'>Tarih</th><th style='width:18mm'>Ders</th><th>Konu / soru</th><th style='width:38mm'>Hata türü*</th><th>Düzeltici adım</th></tr>")
    for _ in range(9):
        A("<tr class='rm'><td></td><td></td><td></td><td></td><td></td></tr>")
    A("</table><p class='small'>*Konu bilinmiyor · Formül hatası · İşlem hatası · Kavram karışıklığı · Algoritma mantığı hatası · Soruyu yanlış yorumlama · Dikkat hatası</p>")
    A("<h3>Notlar</h3><div class='lines'>" + "".join("<div style='border-bottom:.5pt solid #999;height:6mm'></div>" for _ in range(7)) + "</div>")
    return "<!doctype html><html lang='tr'><head><meta charset='utf-8'><title>Akademik Başarı Planı</title><style>" + CSS + "</style></head><body>" + "".join(h) + "</body></html>"


COURSE_INFO = {
    "BIO110": dict(eval="Midterm 1 %25 · Midterm 2 %25 · Proje sunumu %20 · Final %30 (+5 puan: ≥%70 devam — otomatik varsayılmadı)",
                   dates="Midterm 1: 3 Kas (kullanıcı teyitli) · Midterm 2: 26/27 Kas (gün teyit bekliyor) · Proje: 10–31 Ara (15–20 slayt, bireysel) · Final: duyurulacak",
                   pre="Yok; ama kimya/hücre temelini sıfırdan kur (B01–B03 önce).", risk="Konu hacmi büyük (9 konu / 5 gün); ezber yığılması. Çözüm: şema+flashcard+gün sonu test."),
    "CMPE371": dict(eval="Midterm %30 · Final %40 · Quiz %15 · Homework %15",
                    dates="HW1: 2–6 Kas haftası (teyit) · Midterm: 23–27 Kas (teyit) · Quiz 1: 7–11 Ara (teyit) · Final: duyurulacak",
                    pre="Karmaşık sayılar/Euler, trigonometri, üstel, türev-integral (30–31 Eki).", risk="En zor ders; bilgi birikimli. Yalnız izleyerek öğrenilmez → her blokta problem çöz."),
    "CMPE327": dict(eval="Quiz-1/2, Midterm, Final (ağırlıklar syllabus'ta görünmüyor)",
                    dates="Quiz: 15 Kas 13:00–14:00 · Midterm: 29 Kas 13:00–15:00 (W1–W8) · Quiz-2: syllabus (gün doğrula) · Final: duyurulacak",
                    pre="Küme, ilişki, fonksiyon, tümevarım/çelişki ile ispat (A1).", risk="İspat ve dönüşüm algoritmalarında hata birikir; DFA/NFA'yı el ile çok çiz."),
    "CMPE421": dict(eval="Homework %30 · Midterm %30 · Final %40 · Katılım bonus",
                    dates="Midterm: 20 Kasım (kullanıcı teyitli; saat belli değil) · Homework tarihleri syllabus'ta yok · Final: duyurulacak",
                    pre="Temel olasılık, grafik/ağaç gösterimi, temel Python (opsiyonel).", risk="Midterm kapsamı belirsiz; arama algoritmalarını elle yürüt, karşılaştırma tablosu çıkar."),
    "CMPE453": dict(eval="Midterm 12 Kas 18:00–20:00 (kesin) · diğer ağırlıklar syllabus'ta yok",
                    dates="Midterm: 12 Kasım 2026 18:00–20:00 · Lab 1–6 (donanım varsayılmadı) · Final: duyurulacak",
                    pre="İkilik/onaltılık, bit işlemleri, temel C.", risk="Donanım yok → kağıt üstünde register/kod izleme; kapsam doğrulanmalı."),
    "CMPE499": dict(eval="Rapor %70 · Sunum %30",
                    dates="STR: 22 Kas (Pazar) · Video: 29 Kas (Pazar) · Evaluation Form: 7 Eki (teslim edildi)",
                    pre="Bölüm rapor yönergesi/şablonu (materyal bekleniyor).", risk="Son güne bırakma riski. Plan: STR 20 Kas, video 25 Kas yükleme; iç kontrol 19 Kas."),
}


def render_pdf(html_path, pdf_path):
    """Edge/Chrome'u ayrı profille çalıştırır (çalışan bir Edge'e devretmesin) ve PDF yazılana kadar bekler."""
    import tempfile
    import time
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    browser = EDGE if os.path.exists(EDGE) else CHROME
    prof = tempfile.mkdtemp(prefix="pdfprof_")
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={prof}", f"--print-to-pdf={pdf_path}",
                    "file:///" + html_path.replace("\\", "/")], timeout=240, capture_output=True)
    last = -1
    for _ in range(90):
        if os.path.exists(pdf_path):
            sz = os.path.getsize(pdf_path)
            if sz > 0 and sz == last:
                return sz
            last = sz
        time.sleep(1)
    raise RuntimeError("PDF üretilemedi: " + pdf_path)


def main():
    plan = load_plan()
    prog = load_progress(plan)
    html = build_html(plan, prog)
    outdir = os.path.join(ROOT, "05_Printable_PDF")
    hp = os.path.join(outdir, "Akademik_Basari_Plani_30_Ekim_2026.html")
    pp = os.path.join(outdir, "Akademik_Basari_Plani_30_Ekim_2026.pdf")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html)
    render_pdf(hp, pp)
    print("PDF yazıldı:", os.path.getsize(pp), "bayt")


if __name__ == "__main__":
    main()

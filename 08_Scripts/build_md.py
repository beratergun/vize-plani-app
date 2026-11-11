# -*- coding: utf-8 -*-
"""plan.json -> MASTER_STUDY_PLAN.md, haftalık günlük dosyalar, ders planları, COURSE_ANALYSIS, SOURCE_EXTRACTION, SOURCES, README, REPLAN_GUIDE."""
import os
from datetime import date
from common import *
from build_pdf import COURSE_INFO, STATUS_TR
import syllabus as SY

ORDER = ["BIO110", "CMPE371", "CMPE327", "CMPE421", "CMPE453", "CMPE499"]

SYLLABUS = {
    "BIO110": "W1 First Meeting · 8/9 Eki: Chemical Context of Life, Water and Life, Carbon · 15/16 Eki: Large Biological Molecules, Tour of the Cell, Membrane · "
              "22/23 Eki: Metabolism, Cellular Respiration, Photosynthesis · Midterm 1 (3 Kas — kullanıcı tarihi) · 12/13 Kas: Cell Cycle, Mendel, Chromosomal Basis, Molecular Basis of Inheritance · "
              "19/20 Kas: Gene Expression, Regulation, DNA Tools · 26/27 Kas: Midterm 2 · 3/4 Ara: Descent with Modification, Evolution of Populations · 10/11 Ara–31 Ara: Project Presentations",
    "CMPE371": "W1 Intro · W2 Sinusoids · W3 Special Signals, System Properties · W4–5 LTI Systems · W6 Differential/Difference Equations (HW1) · W7 CTFS · W8 CTFT · W9 Midterm (23–27 Kas) · "
               "W10 DTFS · W11 DTFT (Quiz 1) · W12 Filtering · W13 Sampling · W14 Z-Transform · Final haftası (tarih duyurulacak)",
    "CMPE327": "W1 History/Central Concepts · W2 Math Prelim, DFA · W3 NFA, Closure · W4 DFA≡NFA · W5 Regular Languages, Pattern Matching, Regex, DFA Minimization (Quiz-1) · W6 Minimization, Myhill–Nerode, Derivatives · "
               "W7 Myhill–Nerode, Derivatives, Equivalence of REs · W8 DFA Equivalence, CFG, Ambiguity · Quiz 15 Kas · Midterm 29 Kas (W1–W8, kullanıcı bildirimi) · W9–10 CNF, CYK, Pumping Lemma, Non-regularity · W11–12 PDA, Ogden (Quiz-2) · W13–14 Turing Machines, Decision Problems · Final",
    "CMPE421": "W1 Intro · W2 Agents/Problem Solving · W3 Uninformed Search · W4 Informed Search · W5 Game Playing · W6 CSP/Adversarial · W7 Planning · W8 KR + Theorem Proving · W9 Uncertainty · Midterm (20 Kas — kullanıcı tarihi) · "
               "W10 ML Fundamentals + Classification/Regression · W11 NN/Deep Learning · W12 NLP/LLMs · W13 RL · W14 Ethics/XAI/Responsible AI + Review · Final",
    "CMPE453": "W1 Overview + ATmega328P · W2 Programming AVR · W3 AVR I/O (Lab1) · W4 Digital Input (Lab2) · W5 USART · W6 SPI, I2C (Lab3) · W7 ADC · Midterm 12 Kas 18:00–20:00 · W8 Interrupts · W9 Timers (Lab4) · "
               "W10 PWM · W11 ARM Cortex/STM32 Discovery · W12 GPIO + LED (Lab5) · W13 PWM for ARM (Lab6) · Final",
    "CMPE499": "Report %70 · Presentation %30 · Evaluation Form 7 Eki (teslim edildi) · STR 22 Kas · Video 29 Kas",
}


def day_md(d, sts):
    L = [f"### {fmt_date(d['date'])} {d['weekday']} — Min ≈{hours(d['core_min'])} · Genişletilmiş ≈{hours(d['ext_min'])}",
         f"**{d['goal']}** · Öncelik sırası: {' › '.join(d['ranking'][:3])} · {d['phase']}", ""]
    for t in d["tasks"]:
        mark = "x" if sts.get(t["id"], {}).get("status") == "Completed" else " "
        tier = "●" if t["tier"] == "core" else "○"
        star = "★ " if t.get("critical") else ""
        L.append(f"- [{mark}] {tier} **{t['course']}** `{t['priority']}` ({t['minutes']} dk) {star}{t['text']}")
    L += ["", "Kontrol: [ ] Konu öğrenildi [ ] Slaytlar tamam [ ] Sorular çözüldü [ ] Yanlışlar incelendi [ ] Tekrar yapıldı [ ] Günlük hedef tamam", ""]
    return "\n".join(L)


def main():
    plan = load_plan()
    prog = load_progress(plan)
    sts = prog["tasks"]
    R = ROOT
    # ---- MASTER_STUDY_PLAN.md
    head = ["# MASTER STUDY PLAN — 30 Ekim 2026 → 31 Aralık 2026 (14. haftanın sonu)", "",
            "● = minimum plan (≈3–4 sa) · ○ = genişletilmiş · ★ = kritik teslim işi · P1/P2/P3 = öncelik. "
            "Pazar günleri 7–8 saat kapasite; Cumartesi 3–6 sa (**varsayım**). Slayt referansları: *Materyal bekleniyor* (hiç slayt paylaşılmadı).", "",
            "## Kritik tarihler", "", "| Tarih | Olay | Durum |", "|---|---|---|"]
    for e in sorted([e for e in plan["evals"] if e["date"]], key=lambda e: e["date"]):
        rng = fmt_date(e["date"]) + (f" – {fmt_date(e['end'])}" if e["end"] else "") + (f" {e['time'][0]}–{e['time'][1]}" if e.get("time") else "")
        head.append(f"| {rng} | {e['title']} | {STATUS_TR[e['status']]} — {e['note']} |")
    head += ["| — | Final sınavları (W14 sonrası) | DUYURULACAK — tarih uydurulmadı |", ""]
    body = []
    cur_phase = None
    for d in plan["days"]:
        if d["phase"] != cur_phase:
            cur_phase = d["phase"]
            body.append(f"\n## {cur_phase}\n")
        body.append(day_md(d, sts))
    with open(os.path.join(R, "01_Master_Plan", "MASTER_STUDY_PLAN.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(head + body))
    # ---- haftalık günlük dosyalar
    for a, b, name in plan["weeks"]:
        days = [d for d in plan["days"] if a <= d["date"] <= b]
        fn = f"{name.split()[0]}_{name.split()[1]}_{a}.md".replace(" ", "_")
        with open(os.path.join(R, "02_Daily_Study", fn), "w", encoding="utf-8") as f:
            f.write(f"# {name} ({fmt_date(a)} – {fmt_date(b)})\n\n" + "\n".join(day_md(d, sts) for d in days) +
                    "\n## Haftalık değerlendirme\n\nPlanlanan: ___ Tamamlanan: ___ %___\n\nEksik konular:\n\nGelecek hafta hedefleri:\n")
    # ---- ders planları
    for c in ORDER:
        L = [f"# {c} — {plan['courses'][c]['name']}", "", f"Yaklaşım: {plan['courses'][c]['method']}", f"Kaynak: {plan['courses'][c]['ref']}", "",
             "| Tarih | Seviye | Süre | Görev | Slayt/materyal |", "|---|---|---|---|---|"]
        for d in plan["days"]:
            for t in d["tasks"]:
                if t["course"] == c:
                    L.append(f"| {fmt_date(d['date'])} | {'Min' if t['tier'] == 'core' else 'Ext'} | {t['minutes']} dk | {t['text'].replace('|', '/')} | "
                             f"{'Materyal bekleniyor' if t['kind'] in 'LP' else '—'} |")
        with open(os.path.join(R, "03_Course_Plans", f"{c}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
    # ---- COURSE_ANALYSIS.md
    L = ["# COURSE ANALYSIS", "",
         "## Öncelik modeli", "",
         "Puan = aciliyet %35 + zorluk %25 + not ağırlığı %20 + önkoşul bağımlılığı %10 + birikmiş eksik %10 (başlangıçta 0). "
         "Sınavına ≤3 gün kalan ders puandan bağımsız 1. sıradadır; ≤7 gün kalan ders kalan arasında öne çıkar. Oranlar gerekçeli başlangıç değerleridir; "
         "birikmiş eksik arttıkça (Postponed/yanlış) o dersin payı büyür. Yakın bir sınav için çalışırken zor dersler tamamen bırakılmaz (her gün ≥1 min görev).", "",
         "| Ders | Zorluk | Önkoşul bağı | Not |", "|---|---|---|---|"]
    for c in ORDER:
        m = plan["courses"][c]
        L.append(f"| {c} | {m['diff']}/5 | {m['prereq']} | {m['name']} |")
    for c in ORDER:
        m, x = plan["courses"][c], COURSE_INFO[c]
        L += ["", f"## {c} — {m['name']}", "", f"- **Değerlendirme:** {x['eval']}", f"- **Tarihler:** {x['dates']}", f"- **Önkoşullar:** {x['pre']}",
              f"- **Çalışma yaklaşımı:** {m['method']}", f"- **Riskler:** {x['risk']}", f"- **Syllabus akışı:** {SYLLABUS[c]}",
              "", "**Hafta hafta konu haritası** (Hafta 1 = 28 Eylül):", "", SY.md_table(c)]
    L += ["", "## Örtük tarih/kapsam kararları", "",
          "- BIO110 Midterm 1 kapsamı **B01–B09** (syllabus 5/6 Kas satırına kadar olan konular) varsayıldı; 30 Ekim'de doğrulanır.",
          "- CMPE453 Midterm kapsamı W1–W7 (ADC dahil) varsayıldı; Interrupts (W8) sonrası.",
          "- CMPE327 Midterm (29 Kas) kapsamı kesin: W1–W8 (Week 08 dahil). CMPE327 Quiz (15 Kas) kapsamı ayrıca doğrulanacak. CMPE421 Midterm (20 Kas) W1–W9 varsayımı.",
          "- CMPE371 Midterm W1–W8 (CTFT dahil) varsayıldı."]
    with open(os.path.join(R, "00_Analysis", "COURSE_ANALYSIS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    # ---- SOURCE_EXTRACTION.md
    SE = """# SOURCE EXTRACTION — syllabus görsellerinden çıkarım

8 görsel incelendi (CMPE453 görseli iki kez gönderilmiş). Slayt/PDF/ders notu **paylaşılmadı** → slayt kapsama matrisi geçici (Materyal bekleniyor).

| Ders | Görselden doğrulananlar | Çelişki / belirsizlik |
|---|---|---|
| BIO110 | Haftalık konu listesi (1–9 → 5/6 Kas sınav, 12/13 Kas, 19/20 Kas, 26/27 Kas 2. midterm, 3/4 Ara, 10/11 Ara–31 Ara proje); değerlendirme %25/25/20/30; ≥%70 devamlılık → +5; 15–20 slayt bireysel sunum | Syllabus satırı 5/6 Kasım; kullanıcı tarihi **3 Kasım** teyit etti → esas alındı |
| CMPE371 | W1–W14 konuları; HW1 W6; Midterm W9 (23–27 Kas); Quiz 1 W11; Final haftası duyurulacak; %30/40/15/15 | Gün/saat yok |
| CMPE327 | W1–W14; Quiz-1 W5, Midterm W8, Quiz-2 W12; Final | El yazısı **15.11.2026** (Pazar): kullanıcı midterm olduğunu teyit etti; syllabus W8 (16–20 Kas) diyor → kullanıcı tarihi esas |
| CMPE421 | 14 haftalık konu listesi; HW %30, Midterm %30, Final %40, bonus katılım | El yazısı "20 November": kullanıcı midterm olduğunu teyit etti; saat yok |
| CMPE453 | W1–W13; **Midterm 12 Kasım 18:00–20:00**; Lab 1–6; Elliot Ch.1–10, STM32 Manual | Ağırlıklar görünmüyor |
| CMPE499 | Report %70, Presentation %30; Evaluation Form 7 Eki, STR 22 Kas, Video 29 Kas | Evaluation Form kullanıcıya göre teslim edildi; sunum formatı belirsiz |

Kural: kullanıcının teyit ettiği tarihler esas alındı; teyitsiz tarihler 'Teyit Bekliyor' kaldı. Finaller W14 sonrası; tarihleri hiçbir derste yok, uydurulmadı.
"""
    with open(os.path.join(R, "00_Analysis", "SOURCE_EXTRACTION.md"), "w", encoding="utf-8") as f:
        f.write(SE)
    # ---- SOURCES.md
    SRC = """# SOURCES — kaynak stratejisi (3 seviye)

Not: İnternet bağlantıları bu çalışmada **doğrulanmadı**; aşağıda yalnızca kaynak adları var. Ücretli/ücretsiz bilgisi genel bilgidir, güncelliği teyit edilmedi.

**Seviye 1 (öncelikli):** hocanın syllabus'ı, slaytları, ödev/örnek soruları → şu an *Materyal bekleniyor*.
**Seviye 2 (syllabus'ta belirtilen):** BIO110 Campbell Biology; CMPE453 Elliot (Ch.1–10) ve STM32 Manual. Diğer derslerde kitap belirtilmemiş.
**Seviye 3 (yardımcı; ders başına ana + destek + alıştırma):**

| Ders | Ana | Destek | Alıştırma |
|---|---|---|---|
| BIO110 | Hoca slaytı + Campbell | Khan Academy Biology (ücretsiz) | Bölüm sonu soruları + Anki/kendi flashcard |
| CMPE371 | Hoca slaytı | MIT OCW 6.003 Signals and Systems (ücretsiz) | Oppenheim–Willsky problemleri (kitap ücretli) + HW |
| CMPE327 | Hoca slaytı | Sipser "Introduction to the Theory of Computation" (ücretli) | Kitap problemleri; JFLAP (ücretsiz, opsiyonel) |
| CMPE421 | Hoca slaytı | Russell & Norvig AIMA (ücretli); UC Berkeley CS188 materyalleri | AIMA alıştırmaları; kağıt üstünde algoritma izleme |
| CMPE453 | Hoca slaytı + Elliot | ATmega328P datasheet (Microchip) ve STM32 reference manual (ST) — ücretsiz PDF | Kağıt üstünde register soruları; simülatör (Wokwi/SimulIDE vb.) **varsayılmadı** |
| CMPE499 | Bölüm rapor yönergesi | — | Eski örnek raporlar (varsa) |
"""
    with open(os.path.join(R, "07_Sources", "SOURCES.md"), "w", encoding="utf-8") as f:
        f.write(SRC)
    write_static(R)
    print("MD belgeleri yazıldı")


def write_static(R):
    README = """# Academic Success 2026 — Kullanım

Başlangıç: **30 Ekim 2026** · Plan: 31 Aralık 2026'ya kadar (14. hafta sonu; final hazırlığı dahil, final tarihleri duyurulunca eklenir) · Hedef: AA odaklı sistematik çalışma (garanti değildir).

## Dosyalar
| Ne | Nerede |
|---|---|
| **TAKİP SİTESİ** (her gün: nereden, nasıl, kaç soru; tıklanabilir bağlantılar) | **Herkese açık adres (telefon + PC, giriş gerekmez): https://beratergun.github.io/vize-plani-app/** · Hesapla senkronlu özel sürüm: https://claude.ai/artifact/J1dwyWQPfLRdddHvrJ7dHM · Çevrimdışı: `10_Website/index.html` (çift tıkla aç) |
| **SADE PLAN (önce bunu yazdır)** — hafta başı 1 sayfa, 11 sayfa | `05_Printable_PDF/SADE_PLAN_Hafta_Hafta.pdf` |
| Ayrıntılı PDF (günlük kutulu sayfalar, 28 sayfa) | `05_Printable_PDF/Akademik_Basari_Plani_30_Ekim_2026.pdf` |
| Günlük görevler (Excel; durum seç, % otomatik) | `06_Progress_Tracker/Academic_Study_Tracker_2026.xlsx` |
| Takvim — günlük görevler | `04_Calendar/Study_Plan_2026.ics` |
| Takvim — sınav/teslimler (+hatırlatıcılar) | `04_Calendar/Exams_Deadlines_2026.ics` |
| Gün gün plan (Markdown) | `01_Master_Plan/MASTER_STUDY_PLAN.md` |
| Ders analizi | `00_Analysis/COURSE_ANALYSIS.md` |
| Slayt kapsama matrisi | `06_Progress_Tracker/SLIDE_COVERAGE_MATRIX.xlsx/.csv` |
| Kaynak veri | `01_Master_Plan/plan.json` (+ `08_Scripts/plan_data.py`) |
| İlerleme durumu | `06_Progress_Tracker/progress.json` |
| Doğrulama raporu | `09_Quality_Assurance/VALIDATION_REPORT.md` |
| Yeniden planlama | `REPLAN_GUIDE.md` |

## Her gün
1. PDF'te/telefondaki takvimde bugünün kartını aç. 2. ● görevleri bitir, ○ enerjin varsa. 3. Kutuları işaretle (PDF) ve/veya Excel'de **Daily Tasks → Durum** seç.
4. Yanlışları Excel **Mistake Log**'a sebebiyle yaz. 5. Haftalık sayfayı Pazar akşamı doldur.

## Takvime ekleme (otomatik ekleme YAPILMADI)
Hesaplarına hiçbir değişiklik yapılmadı. İki `.ics` dosyasını içe aktar: Google Calendar → Ayarlar → İçe aktar; Apple Takvim → Dosya → İçe Aktar; Outlook → Takvim ekle → Dosyadan yükle.
Yeni takvim olarak içe aktarmak, mevcut takvimine karışmasını önler. UID'ler sabittir: dosyayı güncelleyip tekrar içe aktarmak etkinlikleri **günceller**, çoğaltmaz (Google bazen çoğaltabilir; sorun olursa eski takvimi silip yenisini içe aktar — kendi eklediğin takvimi). Hatırlatıcı saatleri 08:00'dir (çalışma saati değil); platformlar hatırlatmaları farklı destekleyebilir.

## Yeniden üretme
```
cd 08_Scripts
py build_all.py            # mevcut plan.json'dan tüm çıktıları (ICS, XLSX, PDF, MD) yeniden üretir
py build_all.py --regen    # plan_data.py değişince planı baştan kurar (durumlar blok bazında korunur)
py sync_from_xlsx.py       # Excel'de işaretlediklerini progress.json'a al
py replan.py --today 2026-11-05            # önizleme
py replan.py --today 2026-11-05 --apply    # uygula
py validate.py             # kalite kontrolleri + VALIDATION_REPORT.md
```
Python 3.12 yeterlidir; ek paket gerekmez. PDF için Microsoft Edge veya Chrome gerekir.

## Varsayımlar
Cumartesi: min 3 sa / 6 saate kadar. Saatler taahhüt değil tahmindir. Hiç slayt paylaşılmadı. Önceki konular bilinmiyor (sıfırdan başlangıç).
"""
    REPLAN = """# REPLAN GUIDE

## Bir günü kaçırdım / geride kaldım
1. Excel'de **Daily Tasks → Durum** sütununu doldur (Completed / In Progress / Postponed / Blocked) ve kaydet.
2. `cd 08_Scripts` → `py replan.py --from-xlsx --today 2026-MM-DD` (önizleme). Çıktıyı oku.
3. Uygun görünüyorsa `--apply` ekle. Script: tamamlananlara dokunmaz, kritik/yaklaşan sınav görevlerini önce yerleştirir, günlük kapasiteyi aşmaz, ders içi sırayı korur
   (önkoşullar atlanmaz), sığmayan düşük öncelikli tekrarları **Postponed** yapıp nedenini yazar, eski dosyaları `01_Master_Plan/backups/` içine yedekler.
4. Güncellenen `Study_Plan_2026.ics`'i takvimine tekrar içe aktar (UID sabit → güncellenir). PDF yeniden üretilir; yeni sürümü yazdır.

## Sınav/teslim tarihi değişti
1. `08_Scripts/plan_data.py` → `EVALS` listesinde ilgili satırın `date`, `end`, `time`, `status` alanlarını düzenle (`status`: confirmed/user/tentative/window/unknown).
2. Aciliyet hesabı için `NEXT_EVAL` tablosunu da güncelle. Plan günlerini baştan kurmak istiyorsan `py build_all.py --regen` (durumlar blok bazında taşınır); sadece takvim/PDF/Excel etiketleri yeterliyse `py build_all.py`.
3. Yeni tarih günlük planı değiştirecekse (ör. sınav öne alındı) `plan_data.py` içindeki `MANUAL` / `QUEUES` tarihlerini düzenleyip `--regen` çalıştır.

## Excel'den ilerleme alma
`py sync_from_xlsx.py` yalnızca **Durum** ve **Not** sütunlarını okur; başka hiçbir şeyi değiştirmez. Excel dosyasını yeniden üretmek (build_all) durumları progress.json'dan geri yazar — önce sync yap!

## Altın kurallar
- Kaçan görevi ertesi güne yığma; replan et. - Min plan, her koşulda sınavı yakın dersin min görevi korunur. - Hasta/yorgun günde yalnızca ● görevleri yap.
"""
    with open(os.path.join(R, "README.md"), "w", encoding="utf-8") as f:
        f.write(README)
    with open(os.path.join(R, "REPLAN_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(REPLAN)


if __name__ == "__main__":
    main()

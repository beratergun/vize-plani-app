# -*- coding: utf-8 -*-
"""GitHub deposu hazırlar: README.md + proje klasörleri + site. Kullanım: py build_repo.py <hedef_klasor>
Hedef klasör bir git deposu olabilir; içindeki .git korunur, diğer her şey yeniden yazılır."""
import json
import os
import shutil
import sys
from datetime import date
from common import *

REPO_URL = "https://github.com/beratergun/vize-plani-app"
SITE_URL = "https://beratergun.github.io/vize-plani-app/"
COPY = ["00_Analysis", "01_Master_Plan", "02_Daily_Study", "03_Course_Plans", "04_Calendar", "05_Printable_PDF", "06_Progress_Tracker", "07_Sources", "08_Scripts", "09_Quality_Assurance"]
SHORT = {"BIO110": "BIO", "CMPE371": "SİNYAL", "CMPE327": "OTOMAT", "CMPE421": "YZ", "CMPE453": "MİKRO", "CMPE499": "STAJ"}
STAT = {"confirmed": "Kesin (syllabus)", "user": "Kullanıcı teyitli", "tentative": "Teyit bekliyor", "window": "Teyit bekliyor (aralık)", "unknown": "Duyurulacak"}


def week_rows(plan):
    rows = []
    for a, b, name in plan["weeks"]:
        by = {}
        for d in plan["days"]:
            if a <= d["date"] <= b:
                for t in d["tasks"]:
                    if t["kind"] in "LW" and t["course"] in SHORT and t["block"] in plan["blocks"]:
                        title = plan["blocks"][t["block"]]["title"]
                        by.setdefault(t["course"], [])
                        if title not in by[t["course"]]:
                            by[t["course"]].append(title)
        parts = [f"**{SHORT[c]}**: " + "; ".join(x[:34] for x in by[c][:2]) for c in SHORT if c in by]
        fin = {t["course"] for d in plan["days"] if a <= d["date"] <= b for t in d["tasks"] if t["kind"] == "R" and t["course"] in SHORT}
        if fin:
            parts.append("**Final hazırlığı** (" + ", ".join(SHORT[c] for c in SHORT if c in fin) + "): kümülatif tekrar, süreli karma deneme, yanlış defteri turu, son tur özet")
        ev = [e["title"].split(" (")[0] for e in plan["evals"] if e["date"] and not (e["end"] or e["date"]) < a and e["date"] <= b]
        rows.append(f"| {name} | {fmt_date(a)} – {fmt_date(b)} | {' · '.join(parts) or '—'} | {'; '.join(ev) or '—'} |")
    return rows


def readme(plan):
    n_days, n_tasks = len(plan["days"]), sum(len(d["tasks"]) for d in plan["days"])
    vids = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos.json"), encoding="utf-8"))
    n_vid = sum(len(v) for v in vids.values())
    ev_rows = []
    for e in sorted([e for e in plan["evals"] if e["date"]], key=lambda e: e["date"]):
        rng = fmt_date(e["date"]) + (f" – {fmt_date(e['end'])}" if e["end"] else "") + (f" · {e['time'][0]}–{e['time'][1]}" if e.get("time") else "")
        ev_rows.append(f"| {rng} | {e['title']} | {STAT[e['status']]} |")
    crs = []
    for c, m in plan["courses"].items():
        if c == "GENEL":
            continue
        crs.append(f"| **{c}** | {m['name']} | {'●' * m['diff']}{'○' * (5 - m['diff'])} | {m['method']} |")
    return f"""# Vize & Final Planı — 14 haftalık akademik başarı sistemi

Bilgisayar Mühendisliği 2026 Güz dönemi için, **30 Ekim – 31 Aralık 2026** arasını (dönemin 5.–14. haftaları) gün gün planlayan ve her gün **ne, nereden, nasıl** çalışacağını gösteren kişisel çalışma sistemi. Telefondan ve bilgisayardan açılan bir takip sitesi, yazdırılabilir planlar, takvim dosyaları ve Excel takipçisi içerir.

> **Canlı site:** **{SITE_URL}** &nbsp;·&nbsp; Telefonda tarayıcıdan aç, "Ana ekrana ekle" ile uygulama gibi kullan.

<p align="center">
  <img src="10_Website/screenshots/masaustu.jpg" alt="Masaüstü görünümü" width="62%">
  &nbsp;
  <img src="10_Website/screenshots/telefon-bugun.jpg" alt="Telefon görünümü" width="17%">
  &nbsp;
  <img src="10_Website/screenshots/telefon-panel.jpg" alt="Telefon yan panel" width="17%">
</p>

## Bu ne için?
Altı derste (BIO110, CMPE371, CMPE327, CMPE421, CMPE453, CMPE499) aynı anda sınav, quiz, ödev ve teslim yetiştirmek için **ne zaman neyi çalışacağını** bilmek. Plan; sınava kalan süreyi, dersin zorluğunu, not ağırlığını ve konuların birbirine bağımlılığını hesaba katar. Hiçbir önbilgi varsayılmaz: konular sıfırdan, kolaydan zora öğretilir. Garanti verilmez; amaç, AA hedefine hizmet edecek düzenli ve ölçülebilir bir çalışma düzeni kurmaktır.

## Öne çıkan özellikler
| Alan | Ne yapar |
|---|---|
| **Günlük plan** | {n_days} gün, {n_tasks} görev. Her günde *zorunlu* (≈3–5 saat) ve *istersen* (ekstra) görevler. Pazar günleri daha uzun kapasiteyle planlı. |
| **Görev kartı** | Ne yapacağın, ana ve destek kaynak, adım adım yöntem, soru hedefi, "bitti sayılır" ölçütü. |
| **Kaynaklar** | Her konu için OpenStax, MIT OCW, Stanford CS103, Berkeley CS188, CS50 AI, ATmega328P veri sayfası gibi doğrulanmış bağlantılar; **{n_vid} doğrulanmış YouTube videosu** (başlık, kanal, süre) ve konuya özel arama bağlantıları. |
| **Kronometre ve Pomodoro** | Görev başına süre tutar; 25/5, 50/10, 15/3 pomodoro modu, mola ve bildirim. |
| **Yaptım / Yapmadım** | Her görev işaretlenir; yapılmayanlar *Geride* sekmesine düşer, günün önerisi buna göre değişir. |
| **Hafıza kartları** | Konu kavramlarından otomatik kartlar; aralıklı tekrar (1, 3, 7, 14, 30 gün). |
| **Yanlış defteri** | Hata türüyle kayıt, 3. ve 7. gün tekrar hatırlatması, hata deseni analizi. |
| **Notlar** | Görev başına ve genel notlar; Claude yanıtlarını kaydetme. |
| **Not hesaplayıcı** | Aldığın puanlardan hedef toplam için kalan bileşenlerde gereken ortalama. |
| **Deneme sınavı modu** | Süreli deneme, 10 dakika kala uyarı, bitince yanlış defterine yönlendirme. |
| **Motivasyon** | Puan, seviye, gün serisi, 17 rozet, günün sözü, tamamlayınca ödül mesajı. |
| **Hatırlatıcılar** | Sabah ve akşam kontrolü (sayfa açıkken) + telefon takvimi için `.ics` dosyaları. |
| **Claude ile çalış** | Her konuyu seviyene göre anlattırma, örnekle, 5 soru, hafıza kartı, sınav gibi sorular. *(claude.ai sürümünde)* |
| **Çıktılar** | Yazdırılabilir PDF'ler, Excel takipçi, iki `.ics` takvimi, Markdown plan. |

## Plan özeti (hafta hafta)
| Hafta | Tarih | Odak | Sınav / teslim |
|---|---|---|---|
{chr(10).join(week_rows(plan))}

Final sınavları W14 sonrasıdır; tarihleri hiçbir derste duyurulmadığı için **uydurulmadı**. Duyurulunca `08_Scripts/plan_data.py` içine eklenip plan yeniden üretilir.

## Sınav ve teslim takvimi
| Tarih | Olay | Durum |
|---|---|---|
{chr(10).join(ev_rows)}

*Teyit bekleyen tarihler* yalnızca syllabus haftası biliniyor demektir; kesinleşince güncellenir.

## Dersler
| Ders | Ad | Zorluk | Çalışma yaklaşımı |
|---|---|---|---|
{chr(10).join(crs)}

## Slayt kütüphanesi ve ödev takibi (yerel sürüm)
`08_Scripts/import_slides.py` kendi ders ZIP'inin içindeki PDF/PPTX/DOCX dosyalarını sayfa sayfa dizinler (pdftotext + python-pptx); `slides.py` konu bloklarını dosyalarla eşler. Site, claude.ai sürümünde **Kütüphane** (sayfa başlığında arama) ve **Ödevler** (Code / Report / Q&A ayrı izlenen ödev takibi, LMS onayı olmadan "teslim edildi" sayılmaz) sekmelerini gösterir. **Ders materyalleri ve hocanın soruları bu depoda ve herkese açık sitede yoktur**; yalnızca senin makinende dizinlenir.

## Haftalık konu haritası (syllabus)
Her dersin 14 haftalık konu akışı (Hafta 1 = 28 Eylül) sitede **Dersler** sekmesinde, `00_Analysis/COURSE_ANALYSIS.md` içinde ve ayrıntılı PDF'in son sayfalarında bulunur. Site ayrıca Bugün sekmesinde "bu hafta derslerde ne işleniyor" kartını gösterir.

| Ders | Haftalık akış (kısa) |
|---|---|
| BIO110 | H2 kimya/su/karbon · H3 makromolekül, hücre, zar · H4 metabolizma, solunum, fotosentez · H6 Midterm 1 · H7 hücre döngüsü, Mendel, kalıtım, DNA · H8 gen ifadesi, biyoteknoloji · H9 Midterm 2 · H10 evrim · H11–14 proje sunumları |
| CMPE371 | H1 giriş · H2 sinüzoidler · H3 özel sinyaller, sistem özellikleri · H4–5 LTI · H6 diferansiyel/fark denklemleri · H7 CTFS · H8 CTFT · H9 Midterm · H10 DTFS · H11 DTFT · H12 filtreleme · H13 örnekleme · H14 Z dönüşümü |
| CMPE327 | H1–2 temeller, DFA · H3–4 NFA, DFA–NFA denkliği · H5–7 düzenli ifadeler, minimizasyon, Myhill–Nerode · H8 CFG · H9–10 CNF, CYK, pumping · H11–12 PDA, Ogden · H13–14 Turing makineleri |
| CMPE421 | H1–2 ajanlar · H3–4 arama · H5–6 oyun, CSP · H7 planlama · H8 bilgi gösterimi · H9 belirsizlik · H10 ML temelleri · H11 sinir ağları · H12 NLP/LLM · H13 pekiştirmeli öğrenme · H14 etik |
| CMPE453 | H1 AVR mimarisi · H2–4 programlama, G/Ç · H5 USART · H6 SPI, I2C · H7 ADC · H8 kesmeler · H9 zamanlayıcılar · H10 PWM · H11–13 ARM Cortex / STM32 |

Her öğrenme bloğunda ayrıca **2 örnek soru ve cevap** (toplam 166) bulunur; sitede cevabı gizli açılır ve "Yanlış yaptım → deftere ekle" ile yanlış defterine kaydolur. Sorular konuya göre yazılmış özgün alıştırmalardır, hocanın soruları değildir.

## Okul bağlantıları (TEDU LMS)
Sitenin sağ üstündeki **TEDU LMS** düğmesi ve Kaynaklar sekmesindeki "Okul / TEDU LMS" kartı şunlara götürür: [LMS](https://lms.tedu.edu.tr/), [LMS giriş](https://lms.tedu.edu.tr/login/index.php), [MyTEDU](https://my.tedu.edu.tr/), [TED Üniversitesi](https://www.tedu.edu.tr/). Giriş bilgisi bu projede saklanmaz.

## Nasıl kullanılır?
1. **Siteyi aç:** {SITE_URL} — her gün **Bugün** sekmesi o günün görevlerini gösterir.
2. **Çalış:** Görevde **▶ Başlat** ile sayacı aç, bitince **✓ Yaptım** de. Yapamadığını **✗ Yapmadım** işaretle.
3. **Tekrar et:** Her sabah **Kartlar** sekmesindeki kartlara bak; yanlışlarını **Yanlışlar** sekmesine yaz.
4. **Hatırlatma al:** Telefon takvimine `Study_Plan_2026.ics` ve `Exams_Deadlines_2026.ics` dosyalarını ekle (aşağıdaki not).
5. **Geride kaldıysan** ertesi güne yığma; yalnızca zorunlu görevleri yap, sonra planı güncelle (`REPLAN_GUIDE.md`).

### Takvim dosyaları
[`Study_Plan_2026.ics`](Study_Plan_2026.ics) günlük görevleri, [`Exams_Deadlines_2026.ics`](Exams_Deadlines_2026.ics) sınav ve teslimleri tüm gün etkinliği olarak ekler (sabah 08:00 hatırlatma; sınavlar için 7/3/1 gün önce). Telefonda dosyayı açıp takvim uygulamasıyla içe aktar. Sabit UID kullanıldığı için güncel dosyayı tekrar içe aktarmak etkinlikleri günceller, çoğaltmaz. Kendi takvimini bozmamak için önce yeni bir takvim olarak içe aktarmanı öneririm.

### İlerleme nerede saklanır?
* **GitHub Pages sürümü:** ilerleme o tarayıcıda saklanır. Telefon ile bilgisayarı eşlemek için *Kaynaklar → Cihazlar arası aktarım* bölümündeki kodu kopyala/yapıştır.
* **claude.ai sürümü:** aynı hesapla açılınca telefon ve bilgisayar anlık eşleşir; konuları Claude'a anlattırma özelliği de yalnızca orada çalışır.

## Depo yapısı
```
index.html                 Takip sitesi (GitHub Pages bunu yayınlar)
Study_Plan_2026.ics        Günlük plan takvimi
Exams_Deadlines_2026.ics   Sınav ve teslim takvimi
00_Analysis/               Syllabus çıkarımı ve ders analizi
01_Master_Plan/            plan.json (tek kaynak) + MASTER_STUDY_PLAN.md (gün gün plan)
02_Daily_Study/            Haftalık Markdown planlar
03_Course_Plans/           Ders ders görev listeleri
04_Calendar/               .ics takvim dosyaları
05_Printable_PDF/          SADE_PLAN (hafta başı 1 sayfa) ve ayrıntılı PDF
06_Progress_Tracker/       Excel takipçi ve slayt kapsama matrisi
07_Sources/                Kaynak stratejisi
08_Scripts/                Planı, PDF/Excel/ICS çıktılarını ve siteyi üreten Python betikleri
09_Quality_Assurance/      Doğrulama raporu
10_Website/                Site kaynağı ve ekran görüntüleri
```

## Planı kendi bilgilerinle güncelle
Her şey tek bir kaynaktan üretilir: `08_Scripts/plan_data.py` (dersler, sınavlar, konu blokları, günlük program). Python 3.12 yeterlidir; ek paket gerekmez. PDF için Microsoft Edge veya Chrome gerekir.
```bash
cd 08_Scripts
py build_all.py --regen   # plan_data.py'den planı baştan kurar; ICS, XLSX, PDF, MD ve siteyi yeniden üretir
py validate.py            # otomatik kalite kontrolleri (VALIDATION_REPORT.md'yi yazar)
py replan.py --today 2026-11-05          # kaçırılan görevleri taşıma önizlemesi (--apply ile uygular)
py curate_videos.py       # eksik konular için doğrulanmış video arar
```
Sınav tarihi değişince `plan_data.py` içindeki `EVALS` satırını düzenleyip `build_all.py --regen` çalıştırman yeterli. Ayrıntı: [`REPLAN_GUIDE.md`](REPLAN_GUIDE.md).

## Doğrulama ve sınırlar
* Otomatik kontroller (`validate.py`): her takvim günü mevcut, her syllabus konusu planda, her blok bir kez programlı, takvim dosyası yapısı, sınav tarihleri ve etiketleri, site verisi = plan, **site bağlantılarının hepsi açılıyor ve {n_vid} videonun hepsi YouTube'da doğrulandı**.
* **Doğrulanamayanlar:** vize kapsamları syllabus'tan tahmindir (hocadan teyit edilmeli); teyit bekleyen sınav günleri; Khan Academy sayfalarının içeriği (bot korumalı); Excel formülleri Excel'de hesaplanmadı; iki cihazda anlık eşleşme ve telefon bildirimleri gerçek cihazlarda denenmedi.
* **Slayt/ders notu yok:** hiç slayt paylaşılmadığı için "Hocanın materyali" satırlarında sayfa aralığı bulunmaz; slaytlar eklenince kapsama matrisi güncellenir.
* Saatler taahhüt değil tahmindir; Cumartesi kapasitesi bildirilmediği için 3–6 saat varsayılmıştır.

## Kaynaklar ve telif
Bu depo yalnızca plan, bağlantı ve kendi yazdığım çalışma yöntemlerini içerir; **ders içeriği, video veya kitap kopyalanmamıştır**. Bağlantılar OpenStax Biology 2e, MIT OpenCourseWare, Stanford CS103, UC Berkeley CS188, Harvard CS50 AI, Khan Academy, Microchip ve YouTube kanallarının (Amoeba Sisters, Neso Academy, Easy Theory, 3Blue1Brown, Computerphile ve diğerleri) herkese açık sayfalarına gider; içerik hakları sahiplerine aittir.

---
*Hazırlanma: {date.today().isoformat()} · Kişisel çalışma planı; kendi derslerine uyarlayabilirsin.*
"""


def main():
    dest = os.path.abspath(sys.argv[1])
    plan = load_plan()
    os.makedirs(dest, exist_ok=True)
    for name in os.listdir(dest):
        if name == ".git":
            continue
        p = os.path.join(dest, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    ign = shutil.ignore_patterns("__pycache__", "*.pyc", "progress.json", "backups", "*.html", "questions_orig.py", "questions_review.py", "QA_V7", "prep453.py", "inventory_v8.py", "slides.py", "build_library_extra.py", "e2e_prep453.py", "explanations.json")  # hoca materyalinden türetilen betikler herkese açık depoya GİRMEZ
    for d in COPY + ["10_Website"]:
        shutil.copytree(os.path.join(ROOT, d), os.path.join(dest, d), ignore=ign if d != "10_Website" else shutil.ignore_patterns("__pycache__", "artifact_page.html", "artifact_candidate_v7.html", "index.html", "*.ics"))
    # PDF kaynak HTML'leri depoya alınmaz; site tek dosya
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "build_site.py")], env=dict(os.environ, PUBLIC="1"), check=True)  # hoca materyali olmayan herkese açık sürüm
    site = os.path.join(ROOT, "10_Website")
    import pwa
    pub = open(os.path.join(site, "index.html"), encoding="utf-8").read()
    pub_pwa, ver = pwa.make_pwa(dest, pub)   # bağımsız site: manifest + ikonlar + service worker (özel materyal YOK)
    open(os.path.join(dest, "index.html"), "w", encoding="utf-8").write(pub_pwa)
    shutil.copy(os.path.join(site, "index.html"), os.path.join(dest, "10_Website", "index.html"))
    print("PWA sürümü:", ver)
    subprocess.run([sys.executable, os.path.join(here, "build_site.py")], check=True)  # yerel tam sürümü geri yaz
    for f in ("Study_Plan_2026.ics", "Exams_Deadlines_2026.ics"):
        shutil.copy(os.path.join(ROOT, "04_Calendar", f), os.path.join(dest, f))
    for f in ("REPLAN_GUIDE.md",):
        shutil.copy(os.path.join(ROOT, f), os.path.join(dest, f))
    open(os.path.join(dest, "README.md"), "w", encoding="utf-8").write(readme(plan))
    open(os.path.join(dest, ".nojekyll"), "w").write("")
    open(os.path.join(dest, ".gitignore"), "w", encoding="utf-8").write("__pycache__/\n*.pyc\n06_Progress_Tracker/progress.json\n01_Master_Plan/backups/\n*.html.bak\n")
    n = sum(len(fs) for _, _, fs in os.walk(dest) if ".git" not in _)
    import privacy_audit
    rc = privacy_audit.audit(dest)
    if rc:
        raise SystemExit("GİZLİLİK DENETİMİ BAŞARISIZ: yukarıdaki bulguları gider")
    print("Depo hazır:", dest, "·", n, "dosya")


if __name__ == "__main__":
    main()

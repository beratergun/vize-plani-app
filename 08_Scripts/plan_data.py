# -*- coding: utf-8 -*-
"""Tek veri kaynağı: dersler, sınavlar, öğrenme blokları ve program iskeleti.
PDF / XLSX / ICS / MD çıktıları build_all.py tarafından bu dosyadan üretilir.
Tarih veya içerik değişirse YALNIZCA bu dosyayı düzenleyip build_all.py çalıştırın."""
from datetime import date

START = date(2026, 10, 30)
END = date(2026, 12, 31)
PENDING = "Materyal bekleniyor"

# ------------------------------------------------------------------ DERSLER
COURSES = {
    "BIO110":  dict(short="BIO", name="Introduction to Modern Biology", diff=3, prereq=0.3, color="#2e7d32",
                    method="Kavram → şema → karşılaştırma tablosu → aktif hatırlama (flashcard) → konu testi",
                    ref="Campbell Biology (ilgili bölüm; baskıya göre numara değişir) + hoca slaytı"),
    "CMPE371": dict(short="SIG", name="Signals and Systems", diff=5, prereq=1.0, color="#1565c0",
                    method="Önkoşul → çözümlü örnek → kolaydan zora problem (çözüme bakmadan) → yanlış analizi",
                    ref="Hoca slaytı + ders kitabı (syllabus'ta belirtilmemiş: Materyal bekleniyor)"),
    "CMPE327": dict(short="AUT", name="Automata / Theory of Computation", diff=4, prereq=0.8, color="#6a1b9a",
                    method="Otomat çizme → örnek/karşı örnek üretme → dönüşüm algoritmaları → kısa ispat yazma",
                    ref="Hoca slaytı + ders kitabı (syllabus'ta belirtilmemiş: Materyal bekleniyor)"),
    "CMPE421": dict(short="AI", name="Artificial Intelligence", diff=4, prereq=0.5, color="#ef6c00",
                    method="Algoritmayı elle yürüt (arama ağacı, tablo) → karşılaştır → küçük Python deneyi (opsiyonel)",
                    ref="Hoca slaytı (syllabus kitap belirtmiyor: Materyal bekleniyor)"),
    "CMPE453": dict(short="MCU", name="Microprocessors (ATmega328P / STM32)", diff=4, prereq=0.6, color="#c62828",
                    method="Register haritası → bit işlemleri → kod okuma/yazma (kağıt üstünde) → davranış yorumlama",
                    ref="Elliot (syllabus: Ch.1–10) + STM32 Manual + hoca slaytı"),
    "CMPE499": dict(short="SUM", name="Summer Training (rapor + video)", diff=2, prereq=0.0, color="#455a64",
                    method="Taslak → revizyon → format/kaynakça kontrolü → erken teslim",
                    ref="Bölüm staj raporu şablonu/yönergesi: Materyal bekleniyor"),
    "GENEL":   dict(short="GEN", name="Doğrulama / Genel", diff=0, prereq=0.0, color="#000000", method="", ref=""),
}

# ------------------------------------------------------------------ DEĞERLENDİRMELER
# status: confirmed | user (kullanıcı bildirimi) | tentative (Teyit Bekliyor) | window | unknown
EVALS = [
    dict(id="bio-m1", course="BIO110", title="BIO110 Midterm 1", date="2026-11-03", end=None, weight=25, status="user",
         note="Kullanıcı teyitli: 3 Kasım (syllabus satırı 5/6 Kas'ı gösteriyor ama kullanıcının tarihi esas). Kapsam B01–B09 varsayımı; saat belli değil."),
    dict(id="mcu-m", course="CMPE453", title="CMPE453 Midterm", date="2026-11-12", end=None, weight=32, status="confirmed",
         time=("18:00", "20:00"), note="Syllabus (dosyadan okundu): 12 Kasım 18:00–20:00; Midterm %32, Lab %18, Final %50. Kapsam W1–W7 varsayımı; Mock Exam PDF'i yüklendi."),
    dict(id="aut-q1", course="CMPE327", title="CMPE327 Quiz (15 Kasım)", date="2026-11-15", end=None, weight=20, status="user",
         time=("13:00", "14:00"), note="Kullanıcı bildirimi (hoca duyurusu): ertelenen quiz 15 Kasım 13:00–14:00'e alındı. Quiz kapsamı Midterm'den AYRI doğrulanacak. Quizler toplam %20."),
    dict(id="aut-m", course="CMPE327", title="CMPE327 Midterm (29 Kasım)", date="2026-11-29", end=None, weight=30, status="user",
         time=("13:00", "15:00"), note="Kullanıcı bildirimi: 29 Kasım 13:00–15:00. KESİN KAPSAM: Week 08 DAHİL olmak üzere W1–W8. Eski kayıt: 15 Kasım (el yazısı) → 15 Kasım artık Quiz tarihidir."),
    dict(id="ai-20", course="CMPE421", title="CMPE421 Midterm (20 Kasım)", date="2026-11-20", end=None, weight=30, status="user",
         time=("18:00", "20:00"), note="Kullanıcı bildirimi (hoca duyurusu): 20 Kasım 18:00–20:00. Kapsam resmî olarak duyurulmadı; W1–W9 varsayımı."),
    dict(id="ai-a1", course="CMPE421", title="CMPE421 Assignment-1 (son teslim 23:59)", date="2026-11-26", end=None, weight=30, status="user",
         note="LMS: 26 Kasım 23:59. Bileşenler: PDF, Code Submission, Report Submission, Q&A. PDF içeriği bu ortamda okunamadı (LMS oturumu gerekir) → gereksinimler doğrulanana kadar 'Needs Verification'. Syllabus: ödevler bireysel, LLM/AI araçlarıyla hazırlama intihal sayılır. HW toplam %30."),
    dict(id="sig-hw1", course="CMPE371", title="CMPE371 HW1 (2–6 Kas haftası)", date="2026-11-06", end=None, weight=15, status="tentative",
         note="Syllabus W6: HW 1. Tam teslim günü yok; en erken Cuma varsayıldı."),
    dict(id="sum-str", course="CMPE499", title="CMPE499 Summer Training Report (STR)", date="2026-11-22", end=None, weight=70, status="confirmed",
         note="Syllabus: Due Nov 22, 2026 (Pazar). Saat belli değil. Plan: 20 Kasım'da yükle."),
    dict(id="sum-vid", course="CMPE499", title="CMPE499 Summer Training Video", date="2026-11-29", end=None, weight=30, status="confirmed",
         note="Syllabus: Due Nov 29, 2026 (Pazar). Saat belli değil. Plan: 26 Kasım'da yükle."),
    dict(id="bio-m2", course="BIO110", title="BIO110 Midterm 2 (26/27 Kas)", date="2026-11-26", end="2026-11-27", weight=25, status="tentative",
         note="Syllabus: 26/27.11 Second Midterm Review and Exam. Gün/saat belli değil."),
    dict(id="sig-m", course="CMPE371", title="CMPE371 Midterm (30 Kasım)", date="2026-11-30", end=None, weight=30, status="user",
         time=("18:00", "20:00"), note="Kullanıcı bildirimi: 30 Kasım 18:00–20:00 (syllabus W9 23–27 Kas diyordu; duyuru esas). Kapsam W1–W8 (CTFT dahil) varsayımı; resmî kapsam doğrulanacak."),
    dict(id="sig-q1", course="CMPE371", title="CMPE371 Quiz 1 (7–11 Ara haftası)", date="2026-12-07", end="2026-12-11", weight=15, status="tentative",
         note="Syllabus W11: Quiz 1 ('Quiz 1 will be in Week 11')."),
    dict(id="aut-q2", course="CMPE327", title="CMPE327 Quiz-2 (14–18 Ara haftası)", date="2026-12-14", end="2026-12-18", weight=0, status="tentative",
         note="Syllabus W12: Quiz-2."),
    dict(id="bio-pr", course="BIO110", title="BIO110 Proje sunumları (10–31 Ara)", date="2026-12-10", end="2026-12-31", weight=20, status="window",
         note="Syllabus: 10/11.12 – 31.12 Project Presentations. Bireysel 15–20 slayt. Sıra/gün belli değil; 9 Aralık'a hazır ol."),
    dict(id="finals", course="GENEL", title="Final sınavları (W14 sonrası)", date=None, end=None, weight=0, status="unknown",
         note="Tarihler duyurulacak. Kesin tarih UYDURULMADI; plan 31 Aralık'a kadar kümülatif tekrarla biter."),
]
# Aciliyet hesabı için sınav proxy'si (yalnızca sıralama; takvime YAZILMAZ)
NEXT_EVAL = {  # course -> [(date, weight)]
    "BIO110":  [("2026-11-03", 25), ("2026-11-26", 25), ("2026-12-10", 20), ("2027-01-04", 30)],
    "CMPE371": [("2026-11-06", 15), ("2026-11-30", 30), ("2026-12-07", 15), ("2027-01-04", 40)],
    "CMPE327": [("2026-11-15", 20), ("2026-11-29", 30), ("2027-01-04", 50)],
    "CMPE421": [("2026-11-20", 30), ("2026-11-26", 30), ("2027-01-04", 40)],
    "CMPE453": [("2026-11-12", 32), ("2027-01-04", 50)],
    "CMPE499": [("2026-11-22", 70), ("2026-11-29", 30)],
}

# ------------------------------------------------------------------ BLOKLAR
BLOCKS = {}
ORDER = []


def blk(bid, course, title, what, practice, minutes, kind="L", rev=True, topics="", ref=None):
    assert bid not in BLOCKS, bid
    BLOCKS[bid] = dict(id=bid, course=course, title=title, what=what, practice=practice, minutes=minutes,
                       kind=kind, rev=rev and kind == "L", topics=topics or title,
                       ref=ref or (COURSES[course]["ref"] if course in COURSES else ""))
    ORDER.append(bid)


# ---- GENEL
blk("V1", "GENEL", "Doğrulama paketi",
    "(1) BIO110 midterm 1 kapsamı (hangi bölümler); (2) CMPE327 (15 Kas) ve CMPE421 (20 Kas) vize kapsamları; (3) CMPE453 vize kapsamı; "
    "(4) CMPE371 HW1 teslim günü; (5) CMPE327 Quiz-1 (syllabus W5) yapıldı mı",
    "Sonuçları Exam Countdown sayfasına/plana not et; tarih değişirse REPLAN_GUIDE'a göre güncelle", 25, "V", topics="Tarih/kapsam doğrulama")
blk("BX", "BIO110", "Sınav günü hazırlığı", "Kimlik/öğrenci kartı, kalem, saat, salon; yeni konu YOK", "Gece uykusu önce, sabah 20 dk şema gözden geçirme", 10, "V")
blk("PA", "GENEL", "Sınav sonrası analiz", "Biten sınavların yanlış/eksik konularını Mistake Log'a işle", "Zayıf konular için Revision Schedule'a ek tekrar yaz", 30, "V")

# ---- BIO110 (Midterm 1 kapsamı: syllabus 1–9 konu; doğrulanacak)
blk("B01", "BIO110", "The Chemical Context of Life", "atom, element, izotop, elektron kabukları, kovalent/iyonik/hidrojen bağı, kimyasal reaksiyon ve denge",
    "15 kavram sorusu + 10 flashcard (bağ türleri tablosu)", 75, topics="Chemical Context of Life")
blk("B02", "BIO110", "Water and Life", "suyun polaritesi, H-bağı, kohezyon/adezyon, özgül ısı, çözücülük, pH ve tampon",
    "15 kavram sorusu + özellik→örnek tablosu + 10 flashcard", 70, topics="Water and Life")
blk("B03", "BIO110", "Carbon and Molecular Diversity", "karbon iskeleti, hidrokarbonlar, izomer türleri, 7 fonksiyonel grup",
    "Fonksiyonel grup kartları (7) + 12 izomer/grup sorusu", 60, topics="Carbon and the Molecular Diversity of Life")
blk("B04a", "BIO110", "Büyük moleküller I: karbonhidrat + lipid", "monomer/polimer, dehidrasyon-hidroliz, glikozidik bağ, nişasta/glikojen/selüloz, yağ asidi, fosfolipid",
    "Karşılaştırma tablosu + 15 soru", 70, topics="Large Biological Molecules (carbs, lipids)")
blk("B04b", "BIO110", "Büyük moleküller II: protein + nükleik asit", "amino asit, peptit bağı, 4 yapı düzeyi, denatürasyon, DNA/RNA yapısı",
    "Protein yapı basamaklarını belleğten çiz + 15 soru", 80, topics="Large Biological Molecules (proteins, nucleic acids)")
blk("B05a", "BIO110", "Hücre turu I", "prokaryot/ökaryot, çekirdek, ribozom, endomembran sistemi (ER, Golgi, lizozom, vakuol)",
    "Hücre şemasını boş çizip etiketle + 15 soru", 70, topics="A Tour of the Cell (1)")
blk("B05b", "BIO110", "Hücre turu II", "mitokondri, kloroplast, sitoiskelet, hücre dışı matriks, hücre bağlantıları",
    "Organel → görev tablosu + 12 soru", 60, topics="A Tour of the Cell (2)")
blk("B06", "BIO110", "Membrane Structure and Function", "akışkan mozaik model, seçici geçirgenlik, difüzyon/ozmoz, tonisite, aktif taşıma, kotransport",
    "Ozmoz/tonisite 6 senaryo + 15 soru", 80, topics="Membrane Structure and Function")
blk("B07", "BIO110", "An Introduction to Metabolism", "enerji, termodinamik, ΔG, ATP döngüsü, enzimler, inhibisyon, regülasyon",
    "Enzim grafiği yorumlama 5 soru + 15 soru", 80, topics="An Introduction to Metabolism")
blk("B08", "BIO110", "Cellular Respiration", "glikoliz, piruvat oksidasyonu, Krebs, ETZ/oksidatif fosforilasyon, fermentasyon; net ATP/NADH hesabı",
    "Yolu bellekten çiz (girdi/çıktı tablosu) + 20 soru", 110, topics="Cellular Respiration")
blk("B09", "BIO110", "Photosynthesis", "ışık reaksiyonları, Calvin döngüsü, C3/C4/CAM, solunumla karşılaştırma",
    "Kloroplast şeması + solunum–fotosentez karşılaştırma tablosu + 15 soru", 90, topics="Photosynthesis")
blk("BR0", "BIO110", "Hızlı hatırlama", "B01–B02 kartları", "20 soru kapalı kitap", 25, "P", topics="B01–B02 recall")
blk("BQ2", "BIO110", "Konu testi (B01–B08)", "karma test", "40 soru + yanlış analizi", 60, "P", topics="Test B01–B08")
blk("BQ3", "BIO110", "Karma deneme 1 (B01–B09)", "tam kapsam deneme", "50 soru, sınav hızında", 60, "P", topics="Mock Midterm 1")
blk("BQE", "BIO110", "Deneme yanlış analizi", "her yanlış için sebep: bilgi/kavram/dikkat", "Yanlış konuları 15'er dk yeniden çalış", 40, "P")
blk("BS", "BIO110", "Şema ve tablo seti", "solunum, fotosentez, membran, hücre şemaları", "Boş kağıda 6 şemayı belleğten çiz", 40, "P")
blk("BF", "BIO110", "Son kontrollü tekrar", "yalnızca zayıf konular + şemalar, yeni konu yok", "Flashcard son tur, 30 soru karışık", 60, "P")
blk("BPX", "BIO110", "Midterm 1 sonrası analiz", "hangi konulardan soru geldi/zayıf kaldı", "Mistake Log + sonraki sınav için kapsam notu", 30, "V")
blk("B10", "BIO110", "The Cell Cycle and Cellular Reproduction", "hücre döngüsü, mitoz evreleri, sitokinez, kontrol noktaları, siklin-CDK, kanser",
    "Mitoz evreleri çizimi + 15 soru", 80, topics="Cell Cycle and Cellular Reproduction")
blk("B11", "BIO110", "Mendel and the Gene Idea", "Mendel yasaları, Punnett, test cross, dihibrit, olasılık kuralları, baskınlık türleri",
    "10 genetik problem (kolaydan zora) + 10 soru", 90, topics="Mendel and the Gene Idea")
blk("B12", "BIO110", "Chromosomal Basis of Inheritance", "bağlantılı genler, rekombinasyon sıklığı, eşeye bağlı kalıtım, nondisjunction",
    "8 problem + 10 soru", 90, topics="Chromosomal Basis of Inheritance")
blk("B13", "BIO110", "Molecular Basis of Inheritance", "DNA yapısı, replikasyon (enzimler), onarım, telomer",
    "Replikasyon çatalı çizimi + 15 soru", 90, topics="Molecular Basis of Inheritance")
blk("B14", "BIO110", "Gene Expression: Gene to Protein", "transkripsiyon, RNA işleme, translasyon, kod tablosu, mutasyon",
    "mRNA→protein 8 alıştırma + süreç şeması + 15 soru", 100, topics="Gene Expression: From Gene to Protein")
blk("B15", "BIO110", "Regulation of Gene Expression", "operonlar, epigenetik, ökaryot düzenleme, transkripsiyon faktörleri",
    "lac/trp operon 6 senaryo + 12 soru", 80, topics="Regulation of Gene Expression")
blk("B16", "BIO110", "DNA Tools and Biotechnology", "PCR, jel elektroforezi, klonlama, CRISPR, DNA dizileme",
    "PCR/jel yorumlama 5 soru + 12 soru", 70, topics="DNA Tools and Biotechnology")
blk("BT1", "BIO110", "Konu testi 3 (B10–B13)", "karma test", "35 soru + yanlış analizi", 45, "P", topics="Test B10–B13")
blk("BT2", "BIO110", "Konu testi 4 (B14–B16)", "karma test", "35 soru + yanlış analizi", 60, "P", topics="Test B14–B16")
blk("BM2", "BIO110", "Karma deneme 2 (B10–B16)", "tam kapsam deneme", "60 soru, sınav hızında", 90, "P", topics="Mock Midterm 2")
blk("BM2E", "BIO110", "Deneme 2 yanlış analizi", "sebep etiketle", "Zayıf konuları yeniden çalış", 40, "P")
blk("BF2", "BIO110", "Midterm 2 son tekrar", "şemalar + genetik problem tipleri", "25 karışık soru + flashcard", 60, "P")
blk("BF2b", "BIO110", "Midterm 2 son gün", "yalnızca kısa not/şema", "yeni konu yok", 45, "P")

# ---- CMPE371
blk("S0a", "CMPE371", "Önkoşul: karmaşık sayılar ve Euler", "a+jb, kutupsal gösterim, |z|, ∠z, e^{jθ}=cosθ+j sinθ, çarpma/bölme",
    "8 temel problem (kutupsal↔kartezyen)", 40, topics="Prerequisite: complex numbers")
blk("S0b", "CMPE371", "Önkoşul: trigonometri, üstel, türev/integral", "sin/cos özdeşlikleri, e^x kuralları, temel türev ve belirli integral",
    "10 problem", 50, topics="Prerequisite: trig/exp/calculus")
blk("S1", "CMPE371", "Introduction to Signals and Systems", "sürekli/ayrık sinyal, enerji/güç, zaman kaydırma-ölçekleme-ters çevirme, sistem kavramı",
    "8 temel + 5 orta sinyal dönüşüm problemi", 70, topics="Introduction to Signals and Systems")
blk("S2", "CMPE371", "Sinusoids", "genlik, frekans, faz, periyot, fazör gösterimi, sinüzoid toplamı",
    "8 temel + 5 orta problem, yanlış analizi", 70, topics="Sinusoids")
blk("S3", "CMPE371", "Special signals", "birim basamak, impuls, rampa, üstel, çift/tek, periyodiklik",
    "8 temel + 5 orta problem", 70, topics="Special Signals")
blk("S3b", "CMPE371", "System properties", "bellek, nedensellik, doğrusallık, zamanla değişmezlik, kararlılık, tersinirlik",
    "10 sistemi özelliklere göre sınıflandır (gerekçeli)", 80, topics="System Properties")
blk("S4a", "CMPE371", "LTI I: ayrık konvolüsyon", "impuls yanıtı, konvolüsyon toplamı, tablo/grafik yöntem",
    "6 temel + 4 orta hesap", 80, topics="LTI Systems (DT convolution)")
blk("S4b", "CMPE371", "LTI II: sürekli konvolüsyon", "konvolüsyon integrali, grafik yöntem, standart sinyal çiftleri",
    "5 temel + 4 orta hesap", 90, topics="LTI Systems (CT convolution)")
blk("S4c", "CMPE371", "LTI III: özellikler", "değişme/birleşme/dağılma, impuls-basamak yanıtı, nedensellik/kararlılık koşulu, bağlantılar",
    "6 problem + blok diyagram 3 örnek", 60, topics="LTI Systems (properties)")
blk("S5", "CMPE371", "Differential and difference equations", "homojen+özel çözüm, başlangıç koşulu, fark denklemi özyineleme, impuls yanıtı",
    "5 temel + 4 orta çözüm", 90, topics="Differential and Difference Equations")
blk("S6", "CMPE371", "CTFS", "periyodik sinyal, Fourier serisi katsayıları, simetri, özellikler",
    "5 katsayı hesabı + 3 yorum sorusu", 90, topics="Continuous-Time Fourier Series")
blk("S7", "CMPE371", "CTFT", "tanım, standart çiftler, özellikler (kaydırma, ölçekleme, konvolüsyon), frekans yanıtı",
    "6 dönüşüm + 4 özellik sorusu", 100, topics="Continuous-Time Fourier Transform")
blk("SP7", "CMPE371", "CTFS/CTFT problem seti", "karışık", "10 karma problem, çözüme bakmadan", 60, "P", topics="CTFS/CTFT practice")
blk("SH1a", "CMPE371", "HW1 çalışma 1", "ödev metnini oku, S1–S4 ile çözülebilenleri bitir", "ödevin ilk yarısı", 60, "W", topics="Homework 1")
blk("SH1b", "CMPE371", "HW1 çalışma 2", "kalanlar + kontrol + teslim", "ödevi bitir ve teslim et", 60, "W", topics="Homework 1")
blk("SCU", "CMPE371", "Yakalama: CMPE371", "ext'te yapılmayan S4–S6 bloklarını bitir (hepsi yapıldıysa SP7'ye geç)", "eksik blok başına 3 problem", 60, "P", topics="Catch-up")
blk("SMk", "CMPE371", "Vize özeti", "S1–S7 formül/dönüşüm tablosu tek sayfada", "Tek sayfalık özet yaz", 90, "P", topics="Midterm summary")
blk("SM", "CMPE371", "Vize provası", "S1–S7 karma sınav", "10 soru / 120 dk, süreli", 120, "P", topics="Mock midterm")
blk("SR1", "CMPE371", "Yanlış analizi + problem seti", "prova yanlışları", "yanlış konulardan 10 problem", 90, "P")
blk("SR2", "CMPE371", "Problem seti 2", "karma", "10 karma problem", 90, "P")
blk("SR3", "CMPE371", "Formül/dönüşüm tablosu son tekrar", "tek sayfa özet", "kapalı kitap yeniden yaz", 45, "P")

# ---- CMPE327
blk("A1", "CMPE327", "Central concepts + mathematical preliminaries", "alfabe, string, dil, işlemler; küme, ilişki, fonksiyon; tümevarım ve çelişki ile ispat",
    "6 dil tanımlama + 2 tümevarım ispatı", 80, topics="History; Central Concepts; Mathematical Preliminaries")
blk("A2", "CMPE327", "DFA", "tanım (5'li), geçiş tablosu/diyagramı, dil tanıma, tasarım",
    "8 DFA çiz (son iki sembol, mod sayma, alt dize)", 80, topics="Deterministic Finite Automata")
blk("A3", "CMPE327", "DFA tasarım pratiği", "karma dil kalıpları", "15 DFA tasarla; her birine 3 test string", 60, "P", topics="DFA practice")
blk("A4", "CMPE327", "NFA ve ε-NFA", "tanım, belirsizlik, ε-geçişleri, tasarım", "8 NFA çiz + string izleme", 70, topics="Nondeterministic Finite Automata")
blk("A5", "CMPE327", "DFA ≡ NFA (altküme yapısı)", "altküme dönüştürmesi, ε-kapanış", "6 NFA→DFA dönüştürme", 70, topics="Equivalence of DFA and NFA")
blk("A6", "CMPE327", "Closure properties", "birleşim, kesişim, tümleyen, çarpım (product) yapısı", "5 yapı + 3 kısa ispat", 60, topics="Closure Properties; Regular Languages")
blk("A7", "CMPE327", "Regular expressions", "regex sözdizimi, regex↔NFA, pattern matching", "8 regex yaz + 4 dönüşüm", 80, topics="Regular Expressions; Pattern Matching")
blk("A8", "CMPE327", "DFA state minimization", "ayırt edilebilir durumlar, tablo doldurma", "5 minimizasyon", 70, topics="DFA State Minimization")
blk("A9", "CMPE327", "Myhill–Nerode", "denklik sınıfları, minimal DFA ile ilişki, düzenlilik kanıtı", "4 problem + 2 kısa ispat", 70, topics="Myhill–Nerode Relations")
blk("A10", "CMPE327", "Derivatives + regex denkliği", "Brzozowski türevleri, regex denkliği", "6 türev hesabı + 3 denklik", 70, topics="Derivatives; Equivalence of Regular Expressions")
blk("A11", "CMPE327", "Context-free grammars", "CFG tanımı, türetme, ayrıştırma ağacı", "8 CFG tasarla", 70, topics="Context-Free Grammars")
blk("A12", "CMPE327", "Ambiguity + DFA eşdeğerlik kontrolü", "belirsiz gramer, belirsizlik giderme; DFA denklik", "4 gramer + 3 denklik kontrolü", 60, topics="Ambiguity; DFA Equivalence Checking")
blk("A13", "CMPE327", "Vize provası", "A1–A12 karma", "8 soru / 90 dk, süreli", 90, "P", topics="Mock midterm")
blk("AE", "CMPE327", "Prova yanlış analizi", "sebep etiketle", "yanlış konulardan 6 yeni soru", 40, "P")
blk("AQ1", "CMPE327", "Karma tekrar (DFA-NFA-regex)", "15 Kas quiz'i için (kapsamı ayrıca doğrula)", "20 kısa soru, süreli", 60, "P", topics="Quiz-1 prep")
blk("AM2", "CMPE327", "Vize karma tekrar 2 (29 Kas, W1–W8)", "A1–A12", "15 soru", 60, "P")
blk("AF", "CMPE327", "Vize son tekrar", "algoritma adımları (altküme, minimizasyon, regex dönüşümü)", "her algoritmayı 1 kez baştan sona uygula", 60, "P")
blk("AF2", "CMPE327", "Vize günü hafif tekrar", "özet kartları, yeni konu yok", "10 hızlı soru", 45, "P")
blk("AP1", "CMPE327", "Slayt soruları 1 (Slide01–03: DFA, NFA)", "yüklenen Slide01–03 içindeki örnek/alıştırma sayfalarını önce kendin çöz", "her slayttan 5 soru; çözümü kapalı kitap yaz", 75, "P", topics="Slide questions DFA NFA")
blk("AP2", "CMPE327", "Slayt soruları 2 (Slide04–05: DFA-NFA denkliği, regex, kapanış)", "Slide04–05 örnekleri: altküme yapısı, regex→NFA, kapanış özellikleri", "her slayttan 5 soru", 75, "P", topics="Slide questions regex closure")
blk("AP3", "CMPE327", "Slayt soruları 3 (Slide06–07: Arden, minimizasyon)", "Arden teoremi ile FA→RE ve DFA minimizasyon örnekleri", "6 Arden + 4 minimizasyon problemi", 75, "P", topics="Slide questions Arden minimization")
blk("AP4", "CMPE327", "W7–W8 problem seti (Myhill–Nerode, türev, CFG, belirsizlik)", "bu konuların slaytları henüz yüklenmedi: LMS'ten indir; kitap Linz ilgili bölümleri", "8 karma problem; yanlışları deftere yaz", 75, "P", topics="Myhill-Nerode derivatives CFG ambiguity practice")

# ---- CMPE421
blk("I1", "CMPE421", "Intro to AI + intelligent agents", "AI tanımı, PEAS, ortam türleri, ajan türleri", "6 PEAS tanımı + 10 kavram sorusu", 60, topics="Introduction to AI; Intelligent Agents")
blk("I2", "CMPE421", "Problem solving + uninformed search", "problem formülasyonu, BFS, DFS, UCS, DLS, IDS; tam/optimal/karmaşıklık",
    "5 arama ağacı izle + karşılaştırma tablosu", 80, topics="Uninformed Search Algorithms")
blk("I3", "CMPE421", "Informed search", "greedy, A*, admissible/consistent sezgisel, sezgisel tasarım",
    "5 A* izleme + 3 sezgisel kanıt", 80, topics="Informed Search Algorithms")
blk("I4", "CMPE421", "Game playing", "minimax, alfa-beta budama", "5 oyun ağacı (budama sırası)", 70, topics="Game Playing")
blk("I5", "CMPE421", "CSP", "değişken/alan/kısıt, backtracking, MRV/LCV, forward checking, AC-3", "4 CSP elle çöz", 70, topics="Constraint Satisfaction; Adversarial Search")
blk("I6", "CMPE421", "Planning", "STRIPS/PDDL, ileri/geri planlama", "4 plan problemi", 70, topics="Planning")
blk("I7", "CMPE421", "Knowledge representation", "önerme mantığı, çıkarım, FOL temelleri", "10 mantık sorusu", 80, topics="Knowledge Representation and Reasoning")
blk("I8", "CMPE421", "Theorem proving", "CNF dönüşümü, çözümleme (resolution), birleştirme", "5 resolution ispatı", 80, topics="Theorem Proving")
blk("I9", "CMPE421", "Uncertainty", "olasılık, Bayes kuralı, Bayes ağları temeli", "8 olasılık problemi", 80, topics="Uncertainty")
blk("IM", "CMPE421", "Vize provası", "I1–I9 karma (kapsam doğrulanana kadar)", "8 soru / 90 dk, süreli", 90, "P", topics="Mock midterm")
blk("IMR", "CMPE421", "Prova yanlış analizi", "sebep etiketle", "yanlış konulardan 6 yeni soru", 60, "P")
blk("IF", "CMPE421", "Vize son tekrar", "algoritma karşılaştırma tabloları", "tüm aramaları 1 kez elle yürüt", 60, "P")
blk("IF2", "CMPE421", "Vize son kısa tekrar", "özet", "10 hızlı soru", 45, "P")

# ---- CMPE453
blk("M1", "CMPE453", "Course overview + ATmega328P architecture", "CPU, Flash/SRAM/EEPROM, register dosyası, pinler, saat",
    "Blok şemayı belleğten çiz + 10 kavram sorusu", 70, topics="Course Overview; Architecture of AVR (Elliot Ch.1)")
blk("M2", "CMPE453", "Programming AVR (C + bit işlemleri)", "register erişimi, &,|,^,~,<<,>>; bit set/clear/toggle/test",
    "12 bit işlemi alıştırması + 5 kod oku", 80, topics="Programming AVR Microcontroller (Elliot Ch.2–4)")
blk("M3", "CMPE453", "AVR I/O portları", "DDRx, PORTx, PINx; LED desenleri, çıkış yapılandırma",
    "8 kod parçasını izle + 4 kod yaz (kağıt)", 70, topics="AVR Microcontroller I/O (Lab 1)")
blk("M4", "CMPE453", "Digital input", "pull-up/pull-down, polling, buton, bounce ve yazılım debounce",
    "6 kod okuma + 3 buton-LED uygulaması (kağıt)", 60, topics="Programming Digital Input (Lab 2, Elliot Ch.5)")
blk("M5", "CMPE453", "USART", "UBRR hesabı, çerçeve formatı, UCSR0A/B/C, gönder/al",
    "5 baud/UBRR hesabı + 4 kod okuma", 80, topics="Serial Communication: USART (Elliot Ch.5)")
blk("M6", "CMPE453", "SPI ve I2C", "master/slave, SPCR/SPSR, saat modları; I2C start/stop/ACK, adresleme",
    "Zaman diyagramı çiz + 6 soru", 80, topics="Serial Communication: SPI, I2C (Lab 3, Elliot Ch.7)")
blk("M7", "CMPE453", "ADC", "ADMUX, ADCSRA, Vref, prescaler, 10-bit sonuç formülü",
    "6 dönüşüm hesabı + 3 kod okuma", 70, topics="Analog-to-Digital Conversion (Elliot Ch.7)")
blk("MM", "CMPE453", "Vize provası (register/kod)", "M1–M7 karma", "15 soru / 90 dk, süreli (kağıt)", 90, "P", topics="Mock midterm")
blk("MME", "CMPE453", "Prova yanlış analizi", "sebep etiketle", "yanlış konulardan 6 yeni soru", 40, "P")
blk("MF", "CMPE453", "Vize son tekrar (gündüz)", "register tabloları, formüller (UBRR, ADC), bit kalıpları", "Tek sayfa özeti belleğten yaz; 12 hızlı soru", 60, "P")

# ---- CMPE499
blk("U2", "CMPE499", "Rapor: yönerge + içerik planı", "bölüm yönergesi/şablon, sayfa sınırı, başlık iskeleti", "İskelet + her başlığa 2 madde", 45, "W", topics="STR outline")
blk("U3a", "CMPE499", "Rapor: taslak 1", "kurum/staj tanıtımı + görev tanımı", "Bölümü yaz", 60, "W", topics="STR draft")
blk("U3b", "CMPE499", "Rapor: taslak 2", "yapılan işler (teknik anlatım)", "Bölümü yaz", 60, "W", topics="STR draft")
blk("U3c", "CMPE499", "Rapor: taslak 3", "teknik detay, kod/akış, sonuçlar", "Bölümü yaz", 60, "W", topics="STR draft")
blk("U3d", "CMPE499", "Rapor: taslak 4 + sonuç", "kazanımlar, sonuç, tamamlanmamış kısımlar", "Taslağı bitir", 60, "W", topics="STR draft")
blk("U4", "CMPE499", "Rapor: görseller/tablolar", "şekil, ekran görüntüsü, tablo numaralandırma", "Tüm görselleri yerleştir", 45, "W", topics="STR figures")
blk("U5", "CMPE499", "Rapor: format + kaynakça", "yazı tipi, kenar, başlık stili, içindekiler, kaynakça", "Yönerge kontrol listesi", 45, "W", topics="STR format")
blk("U6", "CMPE499", "Rapor: okuma 1", "yazım, tutarlılık, teknik doğruluk", "Baştan sona oku, düzelt", 45, "W", topics="STR proofreading")
blk("U7", "CMPE499", "Rapor: iç kontrol", "yönerge listesi ile son karşılaştırma", "Eksik varsa listele", 45, "W", topics="STR internal check")
blk("U8", "CMPE499", "Rapor: son okuma + PDF", "son okuma, PDF çıktısı", "PDF'i aç, sayfa/şekil kontrolü", 45, "W", topics="STR final")
blk("U9", "CMPE499", "Rapor TESLİM", "STR yükle (son tarih 22 Kas; 2 gün erken)", "Yükleme onayını kaydet", 20, "W", topics="STR submission")
blk("VD1", "CMPE499", "Video: akış + senaryo iskeleti", "video süresi/format gereksinimi, bölüm akışı", "Akış ve süre planı", 45, "W", topics="Video")
blk("VD2", "CMPE499", "Video: senaryo + materyal", "konuşma metni, ekran/slayt materyalleri", "Metni bitir, materyalleri topla", 60, "W", topics="Video")
blk("VD3", "CMPE499", "Video: kayıt", "ses kontrolü, kayıt", "En az 2 tam kayıt", 60, "W", topics="Video")
blk("VD4", "CMPE499", "Video: düzenleme", "kes/birleştir, altyazı/başlık", "İlk düzenlenmiş sürüm", 90, "W", topics="Video")
blk("VD5", "CMPE499", "Video: kalite kontrolü", "ses, süre, çözünürlük, dosya boyutu", "Hataları düzelt", 40, "W", topics="Video")
blk("VD6", "CMPE499", "Video TESLİM", "Video yükle (son tarih 29 Kas; 3 gün erken)", "Yükleme onayını kaydet", 20, "W", topics="Video submission")
blk("UP1", "CMPE499", "Sunum (%30) formatını doğrula + hazırla", "sunum/video ayrı mı? tarih ve format", "Gerekirse 10 dk'lık sunum iskeleti", 60, "W", topics="Presentation (30%)")

blk("SR4", "CMPE371", "Vize son gün hafif tekrar", "formül/dönüşüm özet sayfası", "10 hızlı soru, yeni konu yok", 30, "P", topics="Midterm eve review")

blk("B17", "BIO110", "Descent with Modification", "doğal seçilim, Darwin, adaptasyon, kanıtlar, filogeni temelleri",
    "Kavram kartları + 12 soru", 60, topics="Descent with Modification")
blk("B18", "BIO110", "The Evolution of Populations", "gen havuzu, Hardy–Weinberg, genetik sürüklenme, gen akışı, seçilim türleri",
    "6 Hardy–Weinberg problemi + 12 soru", 80, topics="Evolution of Populations")
blk("BP1", "BIO110", "Proje: konu seçimi", "hoca listesinden konu (Brain-Inspired AI, Embodied AI, Biorobotics, Synthetic Biology, Quantum Biology, Industrial Biotech, Biomimetics…)",
    "Konuyu seç, hocaya/duyuruya göre doğrula", 20, "W", topics="Project Presentation")
blk("BP2", "BIO110", "Proje: 15–20 slayt iskeleti", "slayt başlıkları, kaynak listesi", "İskeleti yaz, 5 ana kaynak bul", 40, "W", topics="Project Presentation")
blk("BP3", "BIO110", "Proje: içerik araştırma/yazım", "slayt içeriği taslağı", "Her slayt için 3 madde", 90, "W", topics="Project Presentation")
blk("BP4", "BIO110", "Proje: slayt tasarımı", "görseller, akış, kaynakça", "Tüm slaytları bitir", 90, "W", topics="Project Presentation")
blk("BP5", "BIO110", "Proje: prova", "süreli sunum provası", "2 tam prova, süre ≤ hoca sınırı", 60, "W", topics="Project Presentation")
blk("BP6", "BIO110", "Proje: son kontrol", "dosya yedeği, soru-cevap hazırlığı", "PDF + PPT yedeği", 40, "W", topics="Project Presentation")
blk("S9", "CMPE371", "DTFS", "ayrık periyodik sinyaller, katsayılar, CTFS ile karşılaştırma", "5 katsayı hesabı + 3 yorum", 80, topics="Discrete-Time Fourier Series")
blk("S10", "CMPE371", "DTFT", "tanım, çiftler, özellikler, LTI frekans yanıtı", "6 dönüşüm + 4 özellik sorusu", 90, topics="Discrete-Time Fourier Transform")
blk("SQ1", "CMPE371", "Quiz-1 hazırlık", "DTFS/DTFT + önceki konulardan karma", "15 kısa soru, süreli", 60, "P", topics="Quiz 1 prep")
blk("S11", "CMPE371", "Filtering", "alçak/yüksek/bant geçiren filtre, ideal vs gerçek, frekans yanıtı", "6 filtre problemi", 80, topics="Filtering")
blk("S12", "CMPE371", "Sampling", "örnekleme teoremi, aliasing, yeniden oluşturma", "6 problem (Nyquist, aliasing)", 90, topics="Sampling")
blk("S13", "CMPE371", "Z-Transform", "tanım, ROC, çiftler, ters Z, fark denklemi çözümü", "6 dönüşüm + 4 ters Z", 100, topics="Z-Transform")
blk("A14", "CMPE327", "Chomsky Normal Form", "ε/birim/yararsız kural eleme, CNF dönüşümü", "5 CNF dönüştürme", 70, topics="Chomsky Normal Form")
blk("A15", "CMPE327", "CYK algoritması", "CYK tablosu, üyelik testi", "6 CYK tablosu", 70, topics="CYK Algorithm")
blk("A16", "CMPE327", "Pumping lemma + non-regularity", "pumping lemma ispat şablonu, karşı örnek seçimi", "8 dil için düzenli değil ispatı", 90, topics="Pumping Lemma; Nonregularity")
blk("A17", "CMPE327", "Pushdown automata", "PDA tanımı, tasarım, CFG↔PDA", "6 PDA tasarla/izle", 90, topics="Pushdown Automata")
blk("A18", "CMPE327", "Ogden's lemma", "tanım, pumping lemma farkı, uygulama", "4 problem", 60, topics="Ogden's Lemma")
blk("AQ2", "CMPE327", "Quiz-2 hazırlık", "CNF/CYK/PDA/pumping", "15 kısa soru, süreli", 60, "P", topics="Quiz-2 prep")
blk("A19", "CMPE327", "Turing machines", "TM tanımı, tasarım, konfigürasyon izleme", "5 TM tasarla/izle", 90, topics="Turing Machines")
blk("A20", "CMPE327", "Decision problems", "karar verilebilirlik, tanınabilir diller, temel problemler", "kavram soruları + 4 örnek", 60, topics="Decision Problems")
blk("I10", "CMPE421", "ML fundamentals", "denetimli/denetimsiz, overfitting, bias-variance, değerlendirme", "10 kavram + 3 metrik hesabı", 70, topics="Machine Learning Fundamentals")
blk("I11", "CMPE421", "Classification and regression", "kNN, karar ağacı, lineer/lojistik regresyon, metrikler", "4 elle hesap", 80, topics="Classification and Regression")
blk("I12", "CMPE421", "Neural networks and deep learning", "perceptron, aktivasyon, geri yayılım, CNN/RNN temelleri", "3 ileri-geri yayılım hesabı", 80, topics="Neural Networks and Deep Learning")
blk("I13", "CMPE421", "NLP and LLMs", "tokenizasyon, gömme, dikkat/transformer, LLM sınırları", "10 kavram sorusu", 70, topics="NLP and LLMs")
blk("I14", "CMPE421", "Reinforcement learning", "MDP, ödül, Q-learning, keşif–sömürü", "3 Q-learning güncellemesi", 80, topics="Reinforcement Learning")
blk("I15", "CMPE421", "Ethics, explainability, responsible AI", "önyargı, açıklanabilirlik, sorumlu AI ilkeleri", "kısa yazılı cevap 3 adet", 50, topics="Ethics, Explainability and Responsible AI")
blk("AS1", "CMPE421", "Assignment-1: yönergeyi oku, gereksinim listesi çıkar", "LMS'teki Assignment-1 PDF'ini (mod/resource id=16460) oku; istenenleri, dosya adlarını, teslim biçimini ve puanlamayı tabloya yaz; bu ortamda PDF okunamadı", "gereksinim listesini 1 sayfada yaz; Q&A bağlantısının zorunlu teslim olup olmadığını doğrula", 45, "W", topics="Assignment-1 requirements")
blk("AS2", "CMPE421", "Assignment-1: tasarım ve ilk sürüm (kod)", "ilgili ders slaytlarını aç; algoritmayı kâğıtta tasarla; ilk çalışan sürümü KENDİN yaz (syllabus: LLM/AI araçlarıyla hazırlama intihaldir)", "ilk çalışan sürüm + 3 elle test", 120, "W", topics="Assignment-1 code")
blk("AS3", "CMPE421", "Assignment-1: kodu bitir ve test et", "kenar durumlar, hata mesajları, dosya adları şartnameye uysun", "tüm gereksinimleri tek tek işaretle", 120, "W", topics="Assignment-1 code tests")
blk("AS4", "CMPE421", "Assignment-1: rapor taslağı", "şartnamedeki rapor bölümleri, şekiller, sonuçlar, kaynaklar", "rapor taslağını tamamla", 90, "W", topics="Assignment-1 report")
blk("AS5", "CMPE421", "Assignment-1: son kontrol ve paketleme", "kod + rapor tutarlılığı, dosya adlandırma, biçim; yükleme dosyalarını hazırla", "kontrol listesi: kod, rapor, adlandırma, biçim", 60, "W", topics="Assignment-1 final check")
blk("AS6", "CMPE421", "Assignment-1: LMS'e yükle (son 26 Kas 23:59)", "Code ve Report ayrı yüklenir; yükleme onay ekranını/e-postasını kaydet; Q&A bölümünü kontrol et", "iki bileşenin de 'Submitted' durumunu LMS'te gör", 30, "W", topics="Assignment-1 submission")
blk("IH", "CMPE421", "Homework çalışma", "ödev metni (tarih doğrulanınca ayarla)", "ödevi bitir + kontrol", 90, "W", topics="Homework (30%)")
blk("M8", "CMPE453", "Interrupts", "vektör tablosu, ISR, SREG/I-bit, harici kesmeler", "5 ISR kod okuma + 3 yazma (kağıt)", 80, topics="Interrupts (Elliot Ch.8)")
blk("M9", "CMPE453", "Timers/counters", "Timer0/1 modları, prescaler, taşma/karşılaştırma, süre hesabı", "6 zaman hesabı + 3 kod", 90, topics="Timers/counters (Lab 4, Elliot Ch.9)")
blk("M10", "CMPE453", "PWM (AVR)", "Fast/Phase-correct PWM, OCRx, duty hesabı", "6 duty/frekans hesabı", 80, topics="PWM (Elliot Ch.10)")
blk("M11", "CMPE453", "ARM Cortex / STM32 Discovery temelleri", "Cortex-M mimarisi, kart donanımı, saat ağacı", "10 kavram sorusu", 60, topics="Basics of ARM Cortex (STM32) (STM32 Manual)")
blk("M12", "CMPE453", "STM32 GPIO + LED", "GPIO modları, RCC saat açma, MODER/ODR, LED yakma", "5 register yapılandırması (kağıt) (Lab 5)", 80, topics="GPIO Configuration and LED Blinking")
blk("M13", "CMPE453", "PWM for ARM Cortex", "Timer, ARR/PSC/CCR, PWM modları", "5 hesap + 2 kod (Lab 6)", 80, topics="PWM for ARM Cortex")
blk("ZF", "GENEL", "Final bilgilerini doğrula", "resmi final tarih/saat/salon ve kapsamlar; açıklanmadıysa bölüm duyurularına bak", "Exam Countdown'a işle; plan_data.py EVALS güncelle", 20, "V", topics="Final dates")

# ---- Final kümülatif tekrar blokları
FINAL_NAMES = {"BIO110": "BIO", "CMPE371": "SIG", "CMPE327": "AUT", "CMPE421": "AI", "CMPE453": "MCU"}
for c, s in FINAL_NAMES.items():
    blk(f"K1{s}", c, "Kümülatif tekrar: önceki konulardan karma", "dönemin ilk konularından unutulanları yakala (Topic Mastery'de düşük olanlar)", "20 karışık soru + zayıf konu notu", 60, "R", topics="Cumulative spaced review")
    blk(f"F1{s}", c, "Final: konu haritası + zayıf alanlar", "tüm syllabus konularını işaretle: güçlü/orta/zayıf (Topic Mastery)", "Zayıf konuları sırala", 90, "R", topics="Cumulative review")
    blk(f"F2{s}", c, "Final: karma deneme", "tüm dönem karma", "Süreli deneme (≈ final formatı, tahmini)", 120, "R", topics="Cumulative mock")
    blk(f"F3{s}", c, "Final: yanlış defteri turu", "Mistake Log'daki tekrar eden hatalar", "Yanlış konulardan 15 soru", 60, "R", topics="Mistake log round")
    blk(f"F5{s}", c, "Final: karma deneme 2", "ikinci tam dönem denemesi", "Süreli deneme, ardından yanlış analizi", 120, "R", topics="Cumulative mock 2")
    blk(f"F7{s}", c, "Final: yanlış defteri son tur", "Mistake Log'da hâlâ tekrar eden hatalar", "10 soru + hata türü kontrolü", 45, "R", topics="Final mistake round")
    blk(f"F6{s}", c, "Final: son gün hafif tekrar", "yalnızca özet sayfası ve zayıf konu kartları, yeni konu yok", "20 dk özet + 10 hızlı soru, erken uyu", 30, "R", topics="Final eve light review")
    blk(f"F4{s}", c, "Final: son tur formül/şema/algoritma", "tek sayfa özet", "kapalı kitap yeniden yaz", 60, "R", topics="Final last pass")


# ------------------------------------------------------------------ MANUEL PROGRAM (29 Eki – 26 Kas)
MANUAL = {
    "2026-10-30": (["V1", "B01", "B02", "B03", "S0a"], ["BR0", "A1"]),
    "2026-10-31": (["B04a", "B04b", "B05a"], ["S0b", "A2"]),
    "2026-11-01": (["B05b", "B06", "B07", "B08"], ["BQ2", "S1"]),
    "2026-11-02": (["B09", "BQ3", "BQE"], ["BS", "S2"]),
    "2026-11-03": (["BF", "BX"], ["S3", "A3", "I1", "U2"]),
    "2026-11-04": (["BPX", "M1", "A4"], ["S3b", "I2"]),
    "2026-11-05": (["M2", "A5"], ["S4a", "S4b"]),
    "2026-11-06": (["M3", "A6", "SH1a"], ["S4c", "U3a"]),
    "2026-11-07": (["M4", "A7"], ["S5", "I3"]),
    "2026-11-08": (["M5", "A8", "SH1b"], ["S6", "I4"]),
    "2026-11-09": (["M6", "A9"], ["I5", "U3b"]),
    "2026-11-10": (["M7", "A10"], ["I6", "U3c", "U4"]),
    "2026-11-11": (["MM", "MME"], ["A11", "I7"]),
    "2026-11-12": (["MF"], ["A12", "I8"]),
    "2026-11-13": (["A13", "U3d", "B10"], ["AQ1"]),
    "2026-11-14": (["AE", "B11"], ["I9", "AP1"]),
    "2026-11-15": (["S7", "B12"], ["U6", "M8"]),
    "2026-11-16": (["IM", "B13"], ["SP7", "U5"]),
    "2026-11-17": (["IMR", "B14"], ["M9", "SCU"]),
    "2026-11-18": (["IF", "B15"], ["AP2", "AS1"]),
    "2026-11-19": (["U8", "U7", "IF2", "B16"], ["BT1"]),
    "2026-11-20": (["U9", "SMk", "VD1"], []),
    "2026-11-21": (["AS2", "VD2", "AP3"], []),
    "2026-11-22": (["AS3", "BT2", "VD3"], ["SM"]),
    "2026-11-23": (["AS4", "VD4", "AM2"], ["SR1"]),
    "2026-11-24": (["AS5", "BM2", "VD5"], ["BM2E", "SR2"]),
    "2026-11-25": (["AS6", "BF2", "VD6"], ["AP4"]),
    "2026-11-26": (["BF2b"], []),
    "2026-11-27": (["AF", "UP1"], []),
    "2026-11-28": (["SR3"], []),
    "2026-11-29": (["AF2", "SR4"], []),
    "2026-12-01": (["PA"], []),
    "2026-12-28": (["ZF"], []),
}

# ------------------------------------------------------------------ OTOMATİK KUYRUKLAR (27 Kas → 31 Ara)
AUTO_START = date(2026, 11, 27)
# (blok, serbest bırakma tarihi, son hedef tarihi)
QUEUES = {
    "CMPE327": [("A14", "11-30", "12-02"), ("A15", "11-30", "12-04"), ("A16", "11-30", "12-06"), ("A17", "11-30", "12-09"),
                ("A18", "11-27", "12-11"), ("AQ2", "12-01", "12-13"), ("A19", "12-01", "12-16"), ("A20", "12-01", "12-18")],
    "CMPE371": [("S9", "12-01", "12-03"), ("S10", "12-01", "12-05"), ("SQ1", "12-01", "12-06"), ("S11", "12-01", "12-12"),
                ("S12", "12-01", "12-15"), ("S13", "12-01", "12-19")],
    "CMPE421": [("I10", "11-27", "12-02"), ("I11", "11-27", "12-04"), ("I12", "11-27", "12-07"), ("IH", "11-27", "12-09"),
                ("I13", "11-27", "12-10"), ("I14", "11-27", "12-13"), ("I15", "11-27", "12-15")],
    "CMPE453": [("M10", "11-27", "11-30"), ("M11", "11-27", "12-06"), ("M12", "11-27", "12-10"), ("M13", "11-27", "12-14")],
    "BIO110":  [("BP1", "11-27", "11-30"), ("B17", "11-27", "12-03"), ("BP2", "11-27", "12-04"), ("B18", "11-27", "12-05"),
                ("BP3", "11-27", "12-06"), ("BP4", "11-27", "12-08"), ("BP5", "11-27", "12-09"), ("BP6", "11-27", "12-09")],
    "CMPE499": [],
}
for c, s in FINAL_NAMES.items():
    QUEUES["F-" + c] = [(f"F1{s}", "12-14", "12-19"), (f"F2{s}", "12-17", "12-23"), (f"F3{s}", "12-19", "12-25"),
                        (f"F5{s}", "12-22", "12-28"), (f"F4{s}", "12-27" if s in ("BIO", "SIG", "AUT") else "12-28", "12-29"),
                        (f"F7{s}", "12-29" if s in ("BIO", "SIG", "AUT") else "12-30", "12-30"), (f"F6{s}", "12-31", "12-31")]
    QUEUES["K-" + c] = [(f"K1{s}", "12-07", "12-13")]
CAPS = dict(weekday=(210, 360), saturday=(210, 380), sunday=(330, 480))  # (min/core, genişletilmiş toplam) dk
REV_INTERVALS = [1, 3, 7, 14]
PHASES = [
    ("2026-10-30", "2026-11-03", "Faz 1 — BIO110 Midterm 1", "BIO ağırlıklı; diğer derslerde kritik görevler"),
    ("2026-11-04", "2026-11-12", "Faz 2 — CMPE453 Midterm", "MCU ana hedef; 327/421/371/499 paralel"),
    ("2026-11-13", "2026-11-20", "Faz 3 — CMPE327 Quiz (15 Kas) ve CMPE421 Midterm (20 Kas)", "Assignment-1 yönergesi okunur; STR yüklenir"),
    ("2026-11-21", "2026-11-30", "Faz 4 — Assignment-1 (26 Kas), CMPE327 Midterm (29 Kas), CMPE371 Midterm (30 Kas)", "BIO Midterm 2 ve video teslimi paralel"),
    ("2026-12-01", "2026-12-31", "Faz 5 — Kalan konular, quizler, proje, final hazırlığı", "kümülatif tekrar; final tarihleri duyurulunca güncelle"),
]
WEEKS = [("2026-10-30", "2026-11-01", "Hafta 5 (kalan)"), ("2026-11-02", "2026-11-08", "Hafta 6"), ("2026-11-09", "2026-11-15", "Hafta 7"),
         ("2026-11-16", "2026-11-22", "Hafta 8"), ("2026-11-23", "2026-11-29", "Hafta 9"), ("2026-11-30", "2026-12-06", "Hafta 10"),
         ("2026-12-07", "2026-12-13", "Hafta 11"), ("2026-12-14", "2026-12-20", "Hafta 12"), ("2026-12-21", "2026-12-27", "Hafta 13"),
         ("2026-12-28", "2026-12-31", "Hafta 14")]

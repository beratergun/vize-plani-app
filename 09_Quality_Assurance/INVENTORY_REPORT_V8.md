# V8 envanter raporu (gerçek dosyalardan)

Taranan gerçek dosya (DERSLER + ders; çevrilmiş PDF kopyaları ve proje klasörü hariç): **68** PDF/PPTX/DOCX, 900 MB.
DERSLER.zip: 62 dosya; SHA-256'ya göre diskte olmayan: **0**. Mükerrer (aynı SHA): 0. PPTX→PDF: 13/13.
Dizinde olmayan gerçek dosyalar: yok

| Ders | Dosya | Slayt/sayfa | Metni okunan | OCR (≥30 kr) | OCR zayıf | Okunamayan görsel | Soru adayı | Doğrulanan | İnceleme gerek | PPTX→PDF |
|---|---|---|---|---|---|---|---|---|---|---|
| BIO110 | 2 | 165 | 112 | 61 | 0 | 1 | 0 | 0 | 0 | 1 |
| CMPE327 | 10 | 411 | 329 | 90 | 4 | 0 | 11 | 7 | 4 | 0 |
| CMPE371 | 8 | 151 | 151 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| CMPE421 | 23 | 1158 | 1126 | 156 | 83 | 15 | 37 | 22 | 15 | 12 |
| CMPE453 | 18 | 202 | 170 | 43 | 0 | 1 | 9 | 9 | 0 | 0 |
| CMPE499 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| EK | 20 | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ENGR490 | 5 | 68 | 67 | 6 | 0 | 0 | 11 | 11 | 0 | 0 |
| **Toplam** | 87 | 2176 | 1976 | 356 | 87 | 17 | 69 | 50 | 19 | 13 |

## Konu denetimi (tam metin + OCR)

- **CMPE327 · Myhill–Nerode** — bulundu: Slide07.pdf ("DFA Minimization – Myhill-Nerode Method", 13 sayfada geçer); ders kitabı Linz s.124–132. Önceki 'eksik' notu YANLIŞTI.
- **CMPE327 · Derivatives (regex türevi)** — yok: Hiçbir slayt/kitap sayfasında yok; yalnızca syllabus çizelgesinde başlık olarak geçiyor (W11/W13, vize sonrası). LMS'te yeni slayt gelirse ekle.
- **CMPE327 · CFG (bağlamdan bağımsız gramer)** — kısmen: Ders slaytı yok (yalnızca Slide01'de genel bakış). Ders kitabı Linz'de 121 sayfada geçer (ör. s.230–233). Slayt henüz yüklenmedi.
- **CMPE327 · Ambiguity (belirsizlik)** — kısmen: Ders slaytı yok; Linz kitabında 33 sayfada geçer (ör. s.138, 179, 207).
- **CMPE371 · CTFT (sürekli zaman Fourier dönüşümü)** — yok: CTFT dersi (W8) dosyalarda yok; yalnızca syllabus + Introduction'da yol haritası. Bağlantılı: 7_CTFS_2026Fall.pdf (Fourier SERİSİ) mevcut, 'CourseHero 02_Fourier_Series_and_Transform.pdf' harici özet not.
- **CMPE453 · ADC** — yok: Ayrı ADC dersi/slaytı dosyalarda yok; yalnızca Lecture0/1'de içindekiler/AVR özelliği olarak geçiyor ve syllabus'ta.
- **CMPE453 · Interrupt** — kısmen: Ayrı Interrupt dersi yok; Lecture6.1'de SPI kesme bitleri (SPIE/SPIF) var, Lecture0/1'de genel anma.
- **BIO110 · Ders materyalleri** — bulundu: Masaüstü 'ders' klasöründe: '1st week slides_.pdf' (51 sayfa: Chemical Context + Water) ve '2nd week presentation slides.pptx' (114 slayt: makromoleküller, hücre turu, zar, taşıma). Önceki 'eksik' notu YANLIŞTI.
- **BIO110 · Karbon & fonksiyonel gruplar, Metabolizma/Enzim** — yok: Bu iki haftalık dosyada yok (3. hafta+ gelirse ekle).

## Notlar
- OCR: Windows.Media.Ocr (Türkçe motor), düşük güvenilirlik; formül/diyagram/kod görsellerini OCR metnine dayanarak yorumlama.
- Okunamayan görsel = OCR boş döndü; içeriği slayttan okuman gerekir.
- Soru adayı sayısı 'Soru değil' (False Positive) hariç.
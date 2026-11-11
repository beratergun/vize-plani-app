# CMPE453 — Microprocessors (ATmega328P / STM32)

Yaklaşım: Register haritası → bit işlemleri → kod okuma/yazma (kağıt üstünde) → davranış yorumlama
Kaynak: Elliot (syllabus: Ch.1–10) + STM32 Manual + hoca slaytı

| Tarih | Seviye | Süre | Görev | Slayt/materyal |
|---|---|---|---|---|
| 4 Kasım | Min | 70 dk | Course overview + ATmega328P architecture — CPU, Flash/SRAM/EEPROM, register dosyası, pinler, saat. ▸ Blok şemayı belleğten çiz + 10 kavram sorusu | Materyal bekleniyor |
| 5 Kasım | Min | 80 dk | Programming AVR (C + bit işlemleri) — register erişimi, &,/,^,~,<<,>>; bit set/clear/toggle/test. ▸ 12 bit işlemi alıştırması + 5 kod oku | Materyal bekleniyor |
| 5 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Course overview + ATmega328P architecture (D+1) | — |
| 6 Kasım | Min | 70 dk | AVR I/O portları — DDRx, PORTx, PINx; LED desenleri, çıkış yapılandırma. ▸ 8 kod parçasını izle + 4 kod yaz (kağıt) | Materyal bekleniyor |
| 6 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Programming AVR (C + bit işlemleri) (D+1) | — |
| 7 Kasım | Min | 60 dk | Digital input — pull-up/pull-down, polling, buton, bounce ve yazılım debounce. ▸ 6 kod okuma + 3 buton-LED uygulaması (kağıt) | Materyal bekleniyor |
| 7 Kasım | Min | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): AVR I/O portları (D+1); Course overview + ATmega328P architecture (D+3) | — |
| 8 Kasım | Min | 80 dk | USART — UBRR hesabı, çerçeve formatı, UCSR0A/B/C, gönder/al. ▸ 5 baud/UBRR hesabı + 4 kod okuma | Materyal bekleniyor |
| 8 Kasım | Min | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Digital input (D+1); Programming AVR (C + bit işlemleri) (D+3) | — |
| 9 Kasım | Min | 80 dk | SPI ve I2C — master/slave, SPCR/SPSR, saat modları; I2C start/stop/ACK, adresleme. ▸ Zaman diyagramı çiz + 6 soru | Materyal bekleniyor |
| 9 Kasım | Min | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): USART (D+1); AVR I/O portları (D+3) | — |
| 10 Kasım | Min | 70 dk | ADC — ADMUX, ADCSRA, Vref, prescaler, 10-bit sonuç formülü. ▸ 6 dönüşüm hesabı + 3 kod okuma | Materyal bekleniyor |
| 10 Kasım | Min | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): SPI ve I2C (D+1); Digital input (D+3) | — |
| 11 Kasım | Min | 90 dk | Vize provası (register/kod) — M1–M7 karma. ▸ 15 soru / 90 dk, süreli (kağıt) | Materyal bekleniyor |
| 11 Kasım | Min | 40 dk | Prova yanlış analizi — sebep etiketle. ▸ yanlış konulardan 6 yeni soru | Materyal bekleniyor |
| 11 Kasım | Min | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ADC (D+1); USART (D+3) | — |
| 11 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Course overview + ATmega328P architecture (D+7) | — |
| 12 Kasım | Min | 60 dk | Vize son tekrar (gündüz) — register tabloları, formüller (UBRR, ADC), bit kalıpları. ▸ Tek sayfa özeti belleğten yaz; 12 hızlı soru | Materyal bekleniyor |
| 12 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): SPI ve I2C (D+3) | — |
| 12 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Programming AVR (C + bit işlemleri) (D+7) | — |
| 13 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ADC (D+3) | — |
| 13 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): AVR I/O portları (D+7) | — |
| 14 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Digital input (D+7) | — |
| 15 Kasım | Ext | 80 dk | Interrupts — vektör tablosu, ISR, SREG/I-bit, harici kesmeler. ▸ 5 ISR kod okuma + 3 yazma (kağıt) | Materyal bekleniyor |
| 15 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): USART (D+7) | — |
| 16 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Interrupts (D+1) | — |
| 16 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): SPI ve I2C (D+7) | — |
| 17 Kasım | Ext | 90 dk | Timers/counters — Timer0/1 modları, prescaler, taşma/karşılaştırma, süre hesabı. ▸ 6 zaman hesabı + 3 kod | Materyal bekleniyor |
| 17 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ADC (D+7) | — |
| 18 Kasım | Min | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Timers/counters (D+1); Interrupts (D+3) | — |
| 18 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Course overview + ATmega328P architecture (D+14) | — |
| 19 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Programming AVR (C + bit işlemleri) (D+14) | — |
| 20 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Timers/counters (D+3) | — |
| 20 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): AVR I/O portları (D+14) | — |
| 21 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Digital input (D+14) | — |
| 22 Kasım | Ext | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Interrupts (D+7); USART (D+14) | — |
| 23 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): SPI ve I2C (D+14) | — |
| 24 Kasım | Ext | 16 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Timers/counters (D+7); ADC (D+14) | — |
| 28 Kasım | Min | 80 dk | PWM (AVR) — Fast/Phase-correct PWM, OCRx, duty hesabı. ▸ 6 duty/frekans hesabı | Materyal bekleniyor |
| 29 Kasım | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM (AVR) (D+1) | — |
| 29 Kasım | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Interrupts (D+14) | — |
| 1 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM (AVR) (D+3) | — |
| 1 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): Timers/counters (D+14) | — |
| 4 Aralık | Min | 60 dk | ARM Cortex / STM32 Discovery temelleri — Cortex-M mimarisi, kart donanımı, saat ağacı. ▸ 10 kavram sorusu | Materyal bekleniyor |
| 5 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ARM Cortex / STM32 Discovery temelleri (D+1) | — |
| 5 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM (AVR) (D+7) | — |
| 7 Aralık | Min | 80 dk | STM32 GPIO + LED — GPIO modları, RCC saat açma, MODER/ODR, LED yakma. ▸ 5 register yapılandırması (kağıt) (Lab 5) | Materyal bekleniyor |
| 7 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ARM Cortex / STM32 Discovery temelleri (D+3) | — |
| 8 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): STM32 GPIO + LED (D+1) | — |
| 10 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): STM32 GPIO + LED (D+3) | — |
| 11 Aralık | Min | 60 dk | Kümülatif tekrar: önceki konulardan karma — dönemin ilk konularından unutulanları yakala (Topic Mastery'de düşük olanlar). ▸ 20 karışık soru + zayıf konu notu | — |
| 11 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ARM Cortex / STM32 Discovery temelleri (D+7) | — |
| 12 Aralık | Min | 80 dk | PWM for ARM Cortex — Timer, ARR/PSC/CCR, PWM modları. ▸ 5 hesap + 2 kod (Lab 6) | Materyal bekleniyor |
| 12 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM (AVR) (D+14) | — |
| 13 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM for ARM Cortex (D+1) | — |
| 14 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): STM32 GPIO + LED (D+7) | — |
| 15 Aralık | Min | 90 dk | Final: konu haritası + zayıf alanlar — tüm syllabus konularını işaretle: güçlü/orta/zayıf (Topic Mastery). ▸ Zayıf konuları sırala | — |
| 15 Aralık | Min | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM for ARM Cortex (D+3) | — |
| 18 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): ARM Cortex / STM32 Discovery temelleri (D+14) | — |
| 19 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM for ARM Cortex (D+7) | — |
| 20 Aralık | Min | 120 dk | Final: karma deneme — tüm dönem karma. ▸ Süreli deneme (≈ final formatı, tahmini) | — |
| 21 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): STM32 GPIO + LED (D+14) | — |
| 22 Aralık | Min | 60 dk | Final: yanlış defteri turu — Mistake Log'daki tekrar eden hatalar. ▸ Yanlış konulardan 15 soru | — |
| 26 Aralık | Min | 120 dk | Final: karma deneme 2 — ikinci tam dönem denemesi. ▸ Süreli deneme, ardından yanlış analizi | — |
| 26 Aralık | Ext | 8 dk | Tekrar (kapalı kitap aktif hatırlama, konu başına ~8 dk): PWM for ARM Cortex (D+14) | — |
| 28 Aralık | Min | 60 dk | Final: son tur formül/şema/algoritma — tek sayfa özet. ▸ kapalı kitap yeniden yaz | — |
| 30 Aralık | Min | 45 dk | Final: yanlış defteri son tur — Mistake Log'da hâlâ tekrar eden hatalar. ▸ 10 soru + hata türü kontrolü | — |
| 31 Aralık | Min | 30 dk | Final: son gün hafif tekrar — yalnızca özet sayfası ve zayıf konu kartları, yeni konu yok. ▸ 20 dk özet + 10 hızlı soru, erken uyu | — |

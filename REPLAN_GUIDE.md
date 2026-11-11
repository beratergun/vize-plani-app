# REPLAN GUIDE

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

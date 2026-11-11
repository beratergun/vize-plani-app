# -*- coding: utf-8 -*-
"""V10.3: Çalışma görünümü / Slayt görünümü / tam genişlik okuyucu; ENGR490 Sustainable_Development.pdf sayfa 3 (3Ps) gerçek öğrenme deneyimi.
NOT: Canlı AI yoktur; hazır açıklama örneği yalnızca YERLEŞİM + slayt metniyle tutarlılık için denenir, anlatım KALİTESİ canlı AI ile ölçülmedi.
Önkoşul: yerel sunucu 8790. py e2e_v103.py [chromium|webkit]"""
import sys, os, json, time, shutil, tempfile
import e2e_core as T
from e2e_core import rec, skip, sync_playwright, SHOTS
from e2e_viewer import canvas_state
from e2e_slide import until, LOCAL, TOK
from e2e_studio import wait_page

F = "Sustainable_Development.pdf"


def open_doc(pg, page=3, view="study"):
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.6)
    pg.select_option("#vw-c1", label="ENGR490"); time.sleep(0.4); pg.select_option("#vw-f", value=F); wait_page(pg, 1, 60)
    if pg.locator(f'.seg:not(.mobseg) button[data-act="vw-view"][data-v="{view}"]').count() and pg.locator(f'.seg:not(.mobseg) button[data-act="vw-view"][data-v="{view}"]').is_visible():
        pg.click(f'.seg:not(.mobseg) button[data-act="vw-view"][data-v="{view}"]'); time.sleep(0.6)
    pg.fill("#vw-p", str(page)); pg.press("#vw-p", "Enter"); wait_page(pg, page, 60); time.sleep(0.8)
    pg.click('button[data-act="vw-tab"][data-v="anlat"]'); time.sleep(0.4)


def rect(pg, sel):
    return pg.evaluate("(s)=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); return {w:b.width,h:b.height,t:b.top,b:b.bottom,l:b.left,r:b.right}}", sel)


def main(p):
    errs = []
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    open_doc(pg, 3, "study")
    slide = pg.evaluate("(DATA.ft||{})['%s'][2]" % F)
    st, cv, sd = rect(pg, "#vw-cv"), rect(pg, "#vw-c"), rect(pg, "#vw-study"); cs = canvas_state(pg)
    rec(f"[{T.BR}][v103][1] ENGR490 s.3 Çalışma görünümü: ORİJİNAL slayt kesilmeden görünüyor (canvas sahne içinde, gerçek sayfa çizildi)", cs and cs["ink"] > 3 and cv["w"] <= st["w"] + 1 and cv["h"] <= st["h"] + 1 and cv["l"] >= st["l"] - 1 and cv["r"] <= st["r"] + 1, {"stage": [round(st["w"]), round(st["h"])], "canvas": [round(cv["w"]), round(cv["h"])]})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v103_study_engr490_p3.png"))
    rec(f"[{T.BR}][v103][3] anlatım alanı dar değil: Çalışma görünümünde panel ≥ 560 px, slayt sahnesi ≥ 600 px", sd["w"] >= 560 and st["w"] >= 600, {"panel": round(sd["w"]), "stage": round(st["w"])})
    txt = pg.locator(".sbody").inner_text()
    rec(f"[{T.BR}][v103][4] 3Ps: Özet + 'Important English Terms' tablosu (Triple bottom line, 3Ps, Stakeholders, Resource base) ve 'Hazır açıklama · canlı AI değil' etiketi", all(k in txt for k in ("Özet", "Triple bottom line", "3Ps", "Stakeholders", "Resource base", "Profit", "People", "Planet")) and "canlı AI değil" in txt, "")
    claims = ["triple bottom line", "3ps", "profit", "people", "planet", "stakeholders", "shareholders", "employees", "customers", "governments", "communities", "resource base", "ad infinitum", "msc", "walmart"]
    low = slide.lower(); missing = [c for c in claims if c not in low]
    rec(f"[{T.BR}][v103][5] açıklamadaki İngilizce terimlerin hepsi gerçekten slayt metninde var (uydurma terim yok)", not missing, {"slayt metninde olmayan": missing})
    fs = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.sbody p')).fontSize)"); lh = pg.evaluate("(()=>{const e=document.querySelector('.sbody p'); const c=getComputedStyle(e); return parseFloat(c.lineHeight)/parseFloat(c.fontSize)})()"); pw = rect(pg, ".sbody p")["w"]
    rec(f"[{T.BR}][v103][2] okunabilirlik: yazı ≥ 16 px, satır aralığı ≥ 1.5, satır uzunluğu ≤ ~80 karakter", fs >= 16 and lh >= 1.5 and pw / (fs * 0.5) <= 80, {"font": fs, "lh": round(lh, 2), "yaklaşık karakter/satır": round(pw / (fs * 0.5))})
    short_len = len(txt); short_h = rect(pg, "#vw-cv")["h"]; sec0 = pg.locator(".sbody .xs").count()
    pg.click('button[data-act="vw-lvl"]'); time.sleep(0.6)
    txt2 = pg.locator(".sbody").inner_text(); st2 = rect(pg, "#vw-cv"); cv2 = rect(pg, "#vw-c"); sec1 = pg.locator(".sbody .xs").count()
    rec(f"[{T.BR}][v103][8] 'Detaylı anlat': kısa özetten FARKLI ve daha uzun (Nedir?, Basit anlatım, Kısa örnek, Sınav odağı, Sık yapılan hatalar bölümleri)", len(txt2) > short_len * 1.8 and sec1 > sec0 and all(k in txt2 for k in ("What is this?", "Simple Explanation", "Short Example", "Exam Focus", "Common Mistakes")), {"kısa": short_len, "detay": len(txt2), "bölüm": [sec0, sec1]})
    rec(f"[{T.BR}][v103][7] uzun anlatım slayt alanını bozmuyor: sahne/canvas boyutu ve slayt aynı kaldı", abs(st2["h"] - short_h) < 2 and abs(st2["w"] - st["w"]) < 2 and abs(cv2["w"] - cv["w"]) < 2 and canvas_state(pg)["ink"] > 3, {"stage_h": [short_h, st2["h"]]})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth"); rec(f"[{T.BR}][v103][7] uzun anlatımda yatay taşma yok", ov <= 1, ov)
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v103_study_detay.png"))
    heads = pg.locator(".sbody h5").all_inner_texts()
    rec(f"[{T.BR}][v103][6] uzun anlatımda başlıklar/bölümler ayrı ve tutarlı (Türkçe + İngilizce başlık)", len(heads) >= 6 and all("·" in h or h.startswith("Ayrıntı") for h in heads), heads)
    pg.click('button[data-act="vw-lvl"]'); time.sleep(0.4)
    # AI yok: AI düğmeleri devre dışı ve dürüst
    dis = pg.evaluate("[...document.querySelectorAll('.sbody [data-act=vw-aiq]')].map(b=>b.disabled)")
    rec(f"[{T.BR}][v103] canlı AI yokken 'Başka örnek' / 'Adım adım çöz' devre dışı (çalışıyormuş gibi gösterilmiyor)", dis and all(dis), dis)
    # Orijinal sorular (s.2 Verified)
    pg.fill("#vw-p", "2"); pg.press("#vw-p", "Enter"); wait_page(pg, 2, 30); time.sleep(0.5)
    pg.click('button[data-act="vw-tab"][data-v="soru"]'); time.sleep(0.4); qt = pg.locator(".sbody").inner_text()
    rec(f"[{T.BR}][v103] Sorular: ORİJİNAL SORU etiketi, doğrulama durumu ve 'doğrulanmış resmî cevap yok' dürüstçe belirtiliyor; AI üretimiyle karışmıyor", "ORİJİNAL SORU" in qt and "slayttan doğrulandı" in qt and "doğrulanmış resmî cevap yok" in qt and "AI ÜRETİMİ" not in qt, qt[:120].replace("\n", " "))
    # not / yer imi / durum korunuyor
    pg.fill("#vw-p", "3"); pg.press("#vw-p", "Enter"); wait_page(pg, 3, 30); pg.click('button[data-act="vw-tab"][data-v="not"]'); time.sleep(0.3)
    pg.fill('textarea[data-act="mynote"]', "3Ps: Profit People Planet notum"); time.sleep(1.2); pg.select_option('select[data-act="pg-bm"]', "exam"); time.sleep(0.4); pg.select_option('select[data-act="pg-st"]', "st"); time.sleep(0.4)
    pg.evaluate("document.activeElement&&document.activeElement.blur(); 0"); pg.keyboard.press("ArrowRight"); wait_page(pg, 4, 30); pg.keyboard.press("ArrowLeft"); wait_page(pg, 3, 30); time.sleep(0.5); pg.click('button[data-act="vw-tab"][data-v="not"]'); time.sleep(0.3)
    v = pg.evaluate("[document.querySelector('textarea[data-act=mynote]').value, document.querySelector('select[data-act=pg-bm]').value, document.querySelector('select[data-act=pg-st]').value]")
    rec(f"[{T.BR}][v103][10] not, yer imi ve çalışma durumu sayfa değiştirip dönünce korunuyor", v == ["3Ps: Profit People Planet notum", "exam", "st"], v)
    # tam genişlik okuyucu
    pg.click('button[data-act="vw-tab"][data-v="anlat"]'); pg.click('button[data-act="vw-lvl"]'); time.sleep(0.4)
    pg.evaluate("document.activeElement&&document.activeElement.blur(); 0"); pg.keyboard.press("r"); time.sleep(0.8)
    rd = pg.locator(".reader").is_visible(); rt = rect(pg, ".rtext"); fs2 = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.rtext p')).fontSize)"); img = pg.evaluate("(document.querySelector('#rd-snap')||{}).src||''")
    rec(f"[{T.BR}][v103] tam genişlik okuyucu (R): geniş sütun ≥ 640 px, yazı ≥ 17 px, yanında orijinal slaytın gerçek küçük görüntüsü (data:image)", rd and rt["w"] >= 640 and fs2 >= 17 and img.startswith("data:image"), {"w": round(rt["w"]), "font": fs2, "img": img[:20]})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v103_reader.png"))
    pg.keyboard.press("Escape"); time.sleep(0.6)
    rec(f"[{T.BR}][v103] Esc ile okuyucudan çıkış; aynı sayfa (3) ve slayt canvas'ı yerinde", (not pg.locator(".reader").count()) and pg.evaluate("document.querySelector('#vw-p').value") == "3" and canvas_state(pg)["ink"] > 3, "")
    # Slayt görünümü ↔ Çalışma görünümü
    pg.click('.seg:not(.mobseg) button[data-act="vw-view"][data-v="present"]'); time.sleep(0.8)
    th = pg.locator("#vw-th").count(); stp = rect(pg, "#vw-cv")
    pg.click('.seg:not(.mobseg) button[data-act="vw-view"][data-v="study"]'); time.sleep(0.8)
    rec(f"[{T.BR}][v103] Slayt görünümü (küçük resimler + büyük sahne) ile Çalışma görünümü arasında geçiş, sayfa korunuyor", th == 1 and stp["w"] > st["w"] and pg.evaluate("document.querySelector('#vw-p').value") == "3", {"present stage": round(stp["w"]), "study stage": round(st["w"])})
    pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2); wait_page(pg, 3, 60)
    rec(f"[{T.BR}][v103] yenilemeden sonra görünüm tercihi (Çalışma) ve sayfa korunuyor", pg.evaluate("document.querySelector('.seg button[data-act=vw-view][data-v=study]').getAttribute('aria-pressed')") == "true", "")
    rec(f"[{T.BR}][v103] konsol/istisna yok (masaüstü)", not errs, errs[:3]); b.close()
    # ---- tablet
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 820, "height": 1180}); pg = ctx.new_page(); pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    pg.evaluate("localStorage.clear(); 0"); open_doc(pg, 3, "study")
    st, sd = rect(pg, "#vw-cv"), rect(pg, "#vw-study"); ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    rec(f"[{T.BR}][v103][9] tablet 820px Çalışma görünümü: slayt üstte, anlatım altta tam genişlikte (≥ 700 px), taşma yok", st["w"] >= 700 and sd["w"] >= 700 and sd["t"] >= st["b"] - 2 and ov <= 1 and canvas_state(pg)["ink"] > 3, {"stage": [round(st["w"]), round(st["h"])], "panel": round(sd["w"]), "ov": ov})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v103_tablet.png"), full_page=True); b.close()
    # ---- mobil
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page(); pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    pg.evaluate("localStorage.setItem('x','1'); 0"); pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.6)
    pg.select_option("#vw-c1", label="ENGR490"); time.sleep(0.4); pg.select_option("#vw-f", value=F); wait_page(pg, 1, 60)
    pg.fill("#vw-p", "3"); pg.press("#vw-p", "Enter"); wait_page(pg, 3, 60)
    seg = pg.locator(".mobseg").count() and pg.locator(".mobseg").is_visible()
    # mobilde görünüm: tercih 'study' değilse bile slayt görünür; çalışma için görünüm anahtarını menüden değil mobseg'den kullan
    if not seg:
        pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('vizeplan.v2')||'{}'); s.notes=s.notes||{}; s.notes['pref:view']={v:'study',t:Date.now()}; localStorage.setItem('vizeplan.v2',JSON.stringify(s));})()"); pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2); wait_page(pg, 3, 60)
        seg = pg.locator(".mobseg").count() and pg.locator(".mobseg").is_visible()
    ok_slide = canvas_state(pg)["ink"] > 3 and pg.locator(".study").evaluate("e=>getComputedStyle(e).display") == "none"
    pg.click('.mobseg button[data-v="read"]'); time.sleep(0.6); pg.click('button[data-act="vw-tab"][data-v="anlat"]'); time.sleep(0.4)
    read_ok = pg.locator(".study").is_visible() and not pg.locator("#vw-cv").is_visible() and "Özet" in pg.locator(".sbody").inner_text(); ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v103_mobile_read.png"))
    pg.click('.mobseg button[data-v="slide"]'); time.sleep(0.8); back = pg.locator("#vw-cv").is_visible() and canvas_state(pg)["ink"] > 3
    rec(f"[{T.BR}][v103][9] mobil 390px: Slayt | Anlatım anahtarı — slayt tam görünür, Anlatım tam ekran okunur, geri dönünce slayt yerinde, taşma yok", bool(seg) and ok_slide and read_ok and back and ov <= 1, {"seg": bool(seg), "slide": ok_slide, "read": read_ok, "back": back, "ov": ov})
    b.close()
    # ---- yeni dosya: ders + hafta eşleme, eski veriler korunur
    tmp = tempfile.mkdtemp(); d = os.path.join(tmp, "cmpe 327"); os.makedirs(d); shutil.copy(os.path.join(T.DERS, "cmpe 327", "Slide04.pdf"), os.path.join(d, "Week9_Yeni_Konu.pdf"))
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page(); pg.goto(f"{LOCAL.replace('8790', '8765')}/index.html" if False else f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.5)
    pg.select_option("#vw-c1", label="CMPE327"); time.sleep(0.4); pg.select_option("#vw-f", value="Slide04.pdf"); wait_page(pg, 1, 60); pg.fill("#vw-p", "26"); pg.press("#vw-p", "Enter"); wait_page(pg, 26, 60)
    pg.click('button[data-act="vw-tab"][data-v="not"]'); time.sleep(0.3); pg.fill('textarea[data-act="mynote"]', "ESKI NOT KORUNMALI"); time.sleep(1.5)
    pg.set_input_files("#vw-dir", d); time.sleep(3)
    pv = pg.locator("body").inner_text()
    rec(f"[{T.BR}][v103][7] yeni dosya (cmpe 327/Week9_Yeni_Konu.pdf): ders CMPE327 ve Hafta 9 otomatik algılandı, onay ekranı gösteriliyor (sessizce yanlış derse bağlanmıyor)", "Hafta 9" in pv and ("CMPE327" in pv), pv[pv.find("Önizleme"):][:200].replace("\n", " "))
    if pg.locator('button[data-act="imp-go"]').count():
        pg.click('button[data-act="imp-go"]'); until(pg, "document.body.innerText.includes('Özet:')", 90); time.sleep(1)
        info = pg.evaluate("(()=>{const d=(DATA.lib||[]).find(x=>x.f==='Week9_Yeni_Konu.pdf'); const s=JSON.parse(localStorage.getItem('vizeplan.v2')||'{}'); return {d: d? [d.c,d.w,d.n]:null, not:(s.mynotes||{})['pg:Slide04.pdf:26']&&s.mynotes['pg:Slide04.pdf:26'].v}})()")
        rec(f"[{T.BR}][v103][7] içe aktarma sonrası belge CMPE327 / Hafta 9 / 33 sayfa olarak kaydedildi; eski sayfa notu silinmedi", info["d"] == ["CMPE327", 9, 33] and info["not"] == "ESKI NOT KORUNMALI", info)
        pg.evaluate("indexedDB.deleteDatabase('vizeplan-files'); 0")
    rec(f"[{T.BR}][v103] konsol/istisna yok (tümü)", not errs, errs[:3]); b.close(); shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_v103_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

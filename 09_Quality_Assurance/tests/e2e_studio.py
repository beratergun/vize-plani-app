# -*- coding: utf-8 -*-
"""V10 Slide Studio: küçük resimler, sığdırma modları, yer imi/durum, kaldığı yerden devam, belge içi arama, kısayollar, mobil, tüm belgelerde ilk/orta/son sayfa.
Önkoşul: yerel sunucu --port 8790. Kullanım: py e2e_studio.py [chromium|webkit] [all]"""
import sys, os, json, time
import e2e_core as T
from e2e_core import rec, skip, sync_playwright, SHOTS
from e2e_viewer import canvas_state
from e2e_slide import until, ST, open_doc, stage_text, LOCAL, TOK

ALL = "all" in sys.argv[2:]


def page_no(pg):
    s = pg.evaluate("(document.querySelector('#vw-st')||{}).textContent||''")
    try: return int(s.split()[1])
    except Exception: return None


def wait_page(pg, n, t=40):
    return until(pg, f"(()=>{{const e=document.querySelector('#vw-st'); return e && e.textContent.startsWith('sayfa {n} /')}})()", t)


def main(p):
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1500, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
    open_doc(pg, "CMPE327", "Slide04.pdf", 26); wait_page(pg, 26)
    # 1) küçük resimler: gerçek sayfa görüntüsü (lazy), aktif vurgu, tıklayınca sayfa
    n_th = pg.locator("#vw-th .th").count()
    until(pg, "document.querySelectorAll('#vw-th .thimg img').length>=3", 40)
    n_img = pg.locator("#vw-th .thimg img").count()
    rec(f"[{T.BR}][studio] küçük resim şeridi: 33 sayfa, görünenler gerçek PDF'ten çizildi, hepsi aynı anda yüklenmedi (lazy)", n_th == 33 and 3 <= n_img < 33, {"şerit": n_th, "çizilen": n_img})
    rec(f"[{T.BR}][studio] aktif sayfa (26) vurgulu", pg.evaluate("(document.querySelector('#vw-th .th.on')||{dataset:{}}).dataset.p") == "26", "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_studio_thumbs.png"))
    pg.click('#vw-th .th[data-p="10"]'); ok = wait_page(pg, 10)
    rec(f"[{T.BR}][studio] küçük resme tıkla → sayfa 10", bool(ok), "")
    # 2) sığdırma modları
    pg.click('button[data-act="vw-fit"]'); time.sleep(1.2); wp = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width"); hp = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().height"); sh = pg.evaluate("document.querySelector('#vw-cv').clientHeight")
    pg.click('button[data-act="vw-fitw"]'); time.sleep(1.2); ww = pg.evaluate("document.querySelector('#vw-c').getBoundingClientRect().width"); sw = pg.evaluate("document.querySelector('#vw-cv').clientWidth")
    rec(f"[{T.BR}][studio] Sayfaya sığdır: tüm sayfa sahneye sığar; Genişliğe sığdır: sahne genişliğini doldurur", hp <= sh and ww >= wp - 1 and abs(ww - (sw - 24)) < 3, {"page w": wp, "page h": hp, "stage h": sh, "width w": ww, "stage w": sw})
    pg.click('button[data-act="vw-fit"]'); time.sleep(1)
    # 3) yer imi + durum
    pg.select_option('select[data-act="pg-bm"]', "exam"); time.sleep(0.5); pg.select_option('select[data-act="pg-st"]', "rev"); time.sleep(0.5)
    ind = pg.evaluate("(document.querySelector('#vw-th .th.on .thm')||{}).textContent||''")
    rec(f"[{T.BR}][studio] yer imi (Sınav kritik) + durum (Tekrar gerek) küçük resimde görünür", "⚑" in ind and "↻" in ind, ind)
    # 4) not
    pg.fill('textarea[data-act="mynote"]', "deneme notu s10"); pg.keyboard.press("Tab"); time.sleep(0.6)
    # yazı alanında kısayol devreye girmemeli
    pg.click('textarea[data-act="mynote"]'); pg.keyboard.type(" f e a  "); time.sleep(0.4)
    rec(f"[{T.BR}][studio] not alanında F/E/A/Space kısayolları tetiklenmiyor", not pg.evaluate("!!document.querySelector('.vw.full')") and page_no(pg) == 10, page_no(pg))
    # 5) belge içi arama
    pg.click('button[data-act="vw-tab"][data-v="ara"]'); time.sleep(0.3)
    pg.fill("#vw-q", "DFA"); pg.press("#vw-q", "Enter"); time.sleep(0.8)
    nh = pg.locator(".shits button").count()
    rec(f"[{T.BR}][studio] belgede ara: 'DFA' sonuçları sayfa numarasıyla listelendi", nh > 0, nh)
    if nh:
        first = pg.locator(".shits button").first; tp = int(first.get_attribute("data-p")); first.click(); ok = wait_page(pg, tp)
        rec(f"[{T.BR}][studio] arama sonucu → tam sayfa (s.{tp})", bool(ok), "")
    pg.click('button[data-act="vw-tab"][data-v="not"]'); time.sleep(0.3)
    # 6) kısayollar
    pg.click("body", position={"x": 5, "y": 5}) if False else pg.evaluate("document.activeElement && document.activeElement.blur(); 0")
    pg.keyboard.press("Home"); r1 = wait_page(pg, 1); pg.keyboard.press("Space"); r2 = wait_page(pg, 2); pg.keyboard.press("PageDown"); r3 = wait_page(pg, 3); pg.keyboard.press("PageUp"); r4 = wait_page(pg, 2); pg.keyboard.press("End"); r5 = wait_page(pg, 33)
    rec(f"[{T.BR}][studio] Home/Space/PageDown/PageUp/End", all([r1, r2, r3, r4, r5]), [bool(x) for x in (r1, r2, r3, r4, r5)])
    pg.keyboard.press("Home"); wait_page(pg, 1); pg.keyboard.press("f"); time.sleep(0.8)
    full = pg.evaluate("!!document.querySelector('.vw.full')"); thfull = pg.locator("#vw-th").count()
    pg.keyboard.press("ArrowRight"); r = wait_page(pg, 2)
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_studio_present.png"))
    pg.keyboard.press("Escape"); time.sleep(0.8)
    rec(f"[{T.BR}][studio] F ile sunum modu (küçük resim gizli, ok ile ilerleme), Esc ile çıkış", full and thfull == 0 and bool(r) and not pg.evaluate("!!document.querySelector('.vw.full')"), {"full": full, "th": thfull})
    # 7) başka sekmeye git-gel: ders+sayfa kalsın
    pg.keyboard.press("End"); wait_page(pg, 33); pg.evaluate("location.hash='#bugun'; 0"); time.sleep(0.6); pg.evaluate("location.hash='#slayt'; 0"); ok = wait_page(pg, 33)
    rec(f"[{T.BR}][studio] sekme değiştirip dönünce aynı belge/sayfa", bool(ok), "")
    # 8) yeniden yükle → kaldığın yerden devam
    pg.goto(f"{LOCAL}/?t={TOK}&r=2#slayt"); pg.reload(); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
    ok = wait_page(pg, 33, 60)
    rec(f"[{T.BR}][studio] yenilemeden sonra son belge/sayfa otomatik açıldı (CMPE327 Slide04 sayfa 33)", bool(ok) and pg.evaluate("document.querySelector('#vw-c1').value") == "CMPE327", ok)
    pg.fill('button[data-act="nope"]', "") if False else None
    pg.locator('#vw-th .th[data-p="10"]').click(); wait_page(pg, 10)
    v = pg.evaluate("[document.querySelector('select[data-act=pg-bm]').value, document.querySelector('select[data-act=pg-st]').value, document.querySelector('textarea[data-act=mynote]').value]")
    rec(f"[{T.BR}][studio] yer imi, durum ve not yenilemeden sonra korundu", bool(ok) and v[:2] == ["exam", "rev"] and v[2].startswith("deneme notu s10"), v)
    rec(f"[{T.BR}][studio] konsol/istisna yok", not errs, errs[:2])
    # Yedek: S.notes içinde
    keys = pg.evaluate("Object.keys((JSON.parse(localStorage.getItem('vizeplan.v2')||'{}').notes)||{}).filter(k=>/^(bm|pgs|last):/.test(k))")
    rec(f"[{T.BR}][studio] yer imi/durum/son sayfa kalıcı durumda (yedeğe dahil)", len(keys) >= 3, keys)
    b.close()
    # 9) mobil
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 390, "height": 800}, has_touch=True, is_mobile=True); pg = ctx.new_page()
    pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
    open_doc(pg, "CMPE327", "Slide04.pdf", 5); okm = wait_page(pg, 5)
    ov = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    cs = canvas_state(pg)
    rec(f"[{T.BR}][studio] mobil 390px: sayfa çizildi, yatay taşma yok", bool(okm) and cs and cs["ink"] > 3 and ov <= 1, {"taşma px": ov})
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_studio_mobile.png"))
    if T.BR == "chromium":
        pg.evaluate("""(()=>{const s=document.getElementById('vw-cv'); const mk=(x,y)=>new Touch({identifier:1,target:s,clientX:x,clientY:y}); const f=(t,x,y)=>s.dispatchEvent(new TouchEvent(t,{bubbles:true,touches:t==='touchend'?[]:[mk(x,y)],changedTouches:[mk(x,y)]})); f('touchstart',300,300); f('touchend',100,305);})(); 0""")
        ok = wait_page(pg, 6, 15); rec(f"[{T.BR}][studio] mobil: sola kaydır → sonraki sayfa", bool(ok), "")
    else:
        skip(f"[{T.BR}][studio] mobil kaydırma", "WebKit'te sentetik Touch olayı oluşturulamıyor; gerçek dokunmatik cihazda denenmedi")
    b.close()
    # 10) tablet
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 820, "height": 1180}); pg = ctx.new_page()
    pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2); open_doc(pg, "CMPE327", "Slide04.pdf", 5); okt = wait_page(pg, 5)
    rec(f"[{T.BR}][studio] tablet 820px: sayfa çizildi, yatay taşma yok", bool(okt) and pg.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 1, "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_studio_tablet.png")); b.close()
    # 11) tüm belgeler: ilk / orta / son sayfa
    if ALL:
        b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1500, "height": 900}); pg = ctx.new_page(); pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(2)
        pg.evaluate("location.hash='#slayt'; 0"); time.sleep(1.0); courses = pg.evaluate("[...document.querySelectorAll('#vw-c1 option')].map(o=>o.textContent)")
        bad, n_doc, n_pg = [], 0, 0
        for course in courses:
            pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.3); pg.select_option("#vw-c1", label=course); time.sleep(0.5)
            for f, label in pg.evaluate("[...document.querySelectorAll('#vw-f option')].filter(o=>o.value).map(o=>[o.value,o.textContent])"):
                if f.lower().endswith(".docx"): continue
                n_doc += 1; exp = int(label.rsplit("(", 1)[1].split(")")[0]); pg.select_option("#vw-f", value=f)
                for target in sorted({1, max(1, exp // 2), exp}):
                    if target != 1:
                        until(pg, ST, 90); pg.fill("#vw-p", str(target)); pg.press("#vw-p", "Enter")
                    okp = wait_page(pg, target, 90); cs = canvas_state(pg); n_pg += 1
                    if not (okp and cs and cs["ink"] > 0 and pg.locator("[data-noslide]").count() == 0):
                        bad.append((course, f, target, bool(okp), cs and cs["ink"]))
        rec(f"[{T.BR}][studio] TÜM belgeler ilk/orta/son sayfa render ({n_doc} belge, {n_pg} sayfa denendi), boş canvas/yanlış dosya yok", n_doc >= 80 and not bad, bad[:6])
        b.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_studio_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in []:
        print(r["result"], r["name"] if "name" in r else r)
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

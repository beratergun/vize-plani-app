# -*- coding: utf-8 -*-
"""V10.2 UI/UX: gerçek etkileşim ve ölçüm (yalnızca 'eleman var' değil). Önkoşul: yerel sunucu 8790. py e2e_v102.py [chromium|webkit]"""
import sys, os, json, time
import e2e_core as T
from e2e_core import rec, skip, sync_playwright, SHOTS
from e2e_viewer import canvas_state
from e2e_slide import until, LOCAL, TOK
from e2e_studio import wait_page

SIZES = [(1920, 1080), (1366, 768), (1024, 768), (768, 1024), (390, 844), (375, 812)]


def open_s04(pg, page=26):
    pg.evaluate("location.hash='#slayt'; 0"); time.sleep(0.6)
    pg.select_option("#vw-c1", label="CMPE327"); time.sleep(0.4); pg.select_option("#vw-f", value="Slide04.pdf"); wait_page(pg, 1, 60)
    pg.fill("#vw-p", str(page)); pg.press("#vw-p", "Enter"); wait_page(pg, page, 60); time.sleep(0.8)


def metrics(pg):
    return pg.evaluate("""()=>{const r=s=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); return {x:b.x,y:b.y,w:b.width,h:b.height,b:b.bottom,r:b.right}}; const small=[...document.querySelectorAll('.vw .bar button,.vw .bar select,.vw .bar input,.vw .bar summary')].filter(e=>{const b=e.getBoundingClientRect(); return b.width>0&&b.height>0&&b.height<34}).length; const st=document.querySelector('#vw-cv'); const c=document.querySelector('#vw-c'); return {ov:document.documentElement.scrollWidth-innerWidth, bar:r('.vw .bar'), stage:r('#vw-cv'), canvas:r('#vw-c'), vh:innerHeight, small, hscroll: st? st.scrollWidth-st.clientWidth:0}}""")


def lum(c):
    def f(v):
        v /= 255; return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = c; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb) + .05) / (min(la, lb) + .05)


def main(p):
    errs = []
    for w, h in SIZES:
        b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": w, "height": h}, has_touch=w < 800, is_mobile=w < 800); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
        open_s04(pg); m = metrics(pg); cs = canvas_state(pg)
        st, cv, bar = m["stage"], m["canvas"], m["bar"]
        ok = m["ov"] <= 1 and cs and cs["ink"] > 3 and cv["w"] <= st["w"] + 1 and cv["h"] <= st["h"] + 1 and m["hscroll"] <= 1
        if w >= 1024: ok = ok and st["b"] <= h + 1 and bar["h"] <= 64   # sahne ekrana sığıyor, araç çubuğu tek satır
        else: ok = ok and bar["h"] <= 170
        rec(f"[{T.BR}][v102] {w}x{h}: slayt çizildi, yatay taşma yok, canvas sahne içinde kesilmiyor" + (", sahne ekrana sığıyor, araç çubuğu tek satır" if w >= 1024 else ", araç çubuğu ≤170px"), ok, {"stage": [round(st["w"]), round(st["h"]), round(st["b"])], "canvas": [round(cv["w"]), round(cv["h"])], "bar_h": round(bar["h"]), "ov": m["ov"]})
        rec(f"[{T.BR}][v102] {w}x{h}: araç çubuğu kontrolleri dokunmaya uygun (≥34px)", m["small"] == 0, m["small"])
        if (w, h) in ((1366, 768), (390, 844)): pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v102_{w}x{h}.png"))
        b.close()
    # ---- ayrıntılı etkileşimler (1440x900)
    b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5); open_s04(pg)
    # sekmeler
    got = {}
    for t, key in (("anlat", "Sayfa 26"), ("soru", "soru"), ("not", "Otomatik kaydedilir"), ("metin", "slayt DEĞİL"), ("ara", "")):
        pg.click(f'button[data-act="vw-tab"][data-v="{t}"]'); time.sleep(0.3)
        got[t] = (pg.evaluate("document.querySelector('button[data-act=vw-tab][data-v=%s]').getAttribute('aria-selected')" % t) == "true") and (key.lower() in pg.locator(".sbody").inner_text().lower())
    rec(f"[{T.BR}][v102] çalışma paneli sekmeleri (Anlatım/Sorular/Notlar/Metin/Ara) tek tek açılıyor, içerik değişiyor", all(got.values()), got)
    pg.click('button[data-act="vw-tab"][data-v="metin"]'); time.sleep(0.3)
    rec(f"[{T.BR}][v102] metin katmanı yalnızca panelde ('slayt DEĞİL'); slayt alanında OCR/metin yok", "slayt DEĞİL" in pg.locator(".study").inner_text() and pg.locator("#vw-cv").inner_text().replace("‹", "").replace("›", "").strip().startswith("sayfa"), "")
    pg.click('button[data-act="vw-tab"][data-v="soru"]'); time.sleep(0.3)
    info = pg.evaluate("(()=>{const m={}; (DATA.qb||[]).forEach(q=>{(m[q.f]=m[q.f]||new Set()).add(q.p)}); const f=Object.keys(m).find(k=>m[k].size>=2 && DATA.lib.find(d=>d.f===k && d.k!=='kitap')); return f? {f, c:DATA.lib.find(d=>d.f===f).c, ps:[...m[f]].sort((a,b)=>a-b)}: null})()")
    if info:
        pg.select_option("#vw-c1", label=info["c"]); time.sleep(0.4); pg.select_option("#vw-f", value=info["f"]); wait_page(pg, 1, 60)
        pg.fill("#vw-p", str(info["ps"][0])); pg.press("#vw-p", "Enter"); wait_page(pg, info["ps"][0], 60)
        pg.click('button[data-act="vw-tab"][data-v="soru"]'); time.sleep(0.4)
        btn = pg.locator('.sbody .shits button[data-act="vw-goto"]'); nq = btn.count()
        if nq:
            tp = int(btn.first.get_attribute("data-p")); btn.first.click(); ok = wait_page(pg, tp, 30)
            rec(f"[{T.BR}][v102] Sorular sekmesinde başka sayfadaki soruya tıkla → o sayfa çiziliyor ({info['f']} s.{tp})", bool(ok), "")
        else:
            rec(f"[{T.BR}][v102] Sorular sekmesi diğer soruları listeliyor", False, info)
        open_s04(pg)
    else:
        skip(f"[{T.BR}][v102] soru → sayfa geçişi", "indekste 2+ sayfada sorusu olan belge yok")
    # panel kapat → slayt genişler
    pg.click('button[data-act="vw-tab"][data-v="not"]'); wait_page(pg, 26, 20) if False else None
    w_open = pg.evaluate("document.querySelector('#vw-cv').getBoundingClientRect().width"); pg.keyboard.press("a"); time.sleep(0.9)
    w_closed = pg.evaluate("document.querySelector('#vw-cv').getBoundingClientRect().width"); cs = canvas_state(pg)
    rec(f"[{T.BR}][v102] panel kapanınca (A) sahne genişliyor ve slayt yeniden en büyük boyda çiziliyor", w_closed > w_open + 150 and cs and cs["ink"] > 3, {"açık": round(w_open), "kapalı": round(w_closed)})
    pg.keyboard.press("a"); time.sleep(0.8)
    # menü
    pg.click(".vw details.more summary"); time.sleep(0.3)
    vis = pg.locator(".vw .menu").is_visible(); txt = pg.locator(".vw .menu").inner_text()
    pg.mouse.click(700, 500); time.sleep(0.3); closed = not pg.evaluate("document.querySelector('.vw details.more').open")
    rec(f"[{T.BR}][v102] ⋯ menüsü: ikincil seçenekler (Konuya git, Genişlik, Küçük resim/Çalışma paneli, Dosya/Klasör) içeride; dışına tıklayınca kapanıyor", vis and all(k in txt for k in ("Konuya git", "Küçük resim", "Çalışma paneli", "Dosya ekle", "Klasör ekle")) and closed, txt[:80].replace("\n", " "))
    ttl = pg.evaluate("[...document.querySelectorAll('.vw .bar .ib, .vw .bar [title]')].filter(e=>e.tagName==='BUTTON'&&!e.title).length")
    rec(f"[{T.BR}][v102] araç çubuğu düğmelerinin hepsinde tooltip (title) var", ttl == 0, ttl)
    # not otomatik kayıt
    pg.click('button[data-act="vw-tab"][data-v="not"]'); time.sleep(0.3)
    pg.fill('textarea[data-act="mynote"]', "v102 not testi"); time.sleep(0.2); s1 = pg.locator("#note-st").inner_text(); time.sleep(1.4); s2 = pg.locator("#note-st").inner_text()
    rec(f"[{T.BR}][v102] not durum göstergesi: 'Kaydediliyor…' → 'Kaydedildi ✓'", "Kaydediliyor" in s1 and "Kaydedildi" in s2, [s1, s2])
    pg.evaluate("document.activeElement&&document.activeElement.blur(); 0")
    # titreme yok: sayfa değişiminde canvas boş kalmıyor
    pg.keyboard.press("ArrowRight"); ink_now = pg.evaluate("""()=>{const c=document.querySelector('#vw-c'); if(!c||!c.width) return -1; const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data; let k=0; for(let i=0;i<d.length;i+=148){ if(d[i]<240) k++ } return k}""")
    rec(f"[{T.BR}][v102] sayfa değişiminde ilk karede canvas boş/beyaz kalmıyor (eski görüntü yeni sayfa gelene kadar korunuyor)", ink_now > 3, ink_now)
    ok27 = wait_page(pg, 27, 30); rec(f"[{T.BR}][v102] ok tuşu ile sonraki sayfa (27) çizildi", bool(ok27), "")
    # sunum modu
    pg.keyboard.press("f"); time.sleep(0.6); bar_vis = pg.locator(".vw.full .bar").is_visible(); time.sleep(3.4)
    idle = pg.evaluate("!!document.querySelector('.vw.full.idle')"); pg.mouse.move(300, 300); time.sleep(0.3); woke = not pg.evaluate("!!document.querySelector('.vw.full.idle')")
    st = pg.evaluate("(()=>{const e=document.querySelector('#vw-cv').getBoundingClientRect(); return [e.width,e.height]})()"); vw_, vh_ = pg.evaluate("[innerWidth, innerHeight]")
    nstudy = pg.locator(".vw.full .study").count()
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v102_present.png"))
    pg.keyboard.press("ArrowRight"); wait_page(pg, 28, 30); pg.keyboard.press("Escape"); time.sleep(0.8)
    back = pg.locator(".vw .study").count() == 1 and not pg.evaluate("!!document.querySelector('.vw.full')")
    rec(f"[{T.BR}][v102] sunum modu: araç çubuğu sunum başında görünür, 3 sn sonra gizlenir, fare hareketiyle geri gelir; sahne tüm ekranı kaplar; panel kapalı", bar_vis and idle and woke and abs(st[0] - vw_) < 3 and abs(st[1] - vh_) < 3 and nstudy == 0, {"stage": st, "view": [vw_, vh_]})
    rec(f"[{T.BR}][v102] sunumdan çıkınca (Esc) sayfa korundu (28) ve çalışma paneli geri geldi", back and (pg.evaluate("document.querySelector('#vw-p').value") == "28"), "")
    # reduced motion
    ctx2 = b.new_context(viewport={"width": 1200, "height": 800}, reduced_motion="reduce"); p2 = ctx2.new_page(); p2.goto(f"{LOCAL}/?t={TOK}"); p2.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5); open_s04(p2, 3)
    an = p2.evaluate("getComputedStyle(document.querySelector('#vw-c')).animationName"); tr = p2.evaluate("getComputedStyle(document.querySelector('.vw .btn')).transitionDuration")
    rec(f"[{T.BR}][v102] reduced-motion tercihi: animasyon/geçiş kapalı", an == "none" and tr in ("0s", "0.000001s", "1e-06s"), {"anim": an, "trans": tr})
    ctx2.close(); b.close()
    # ---- kontrast (açık/koyu)
    for scheme in ("dark", "light"):
        b = getattr(p, T.BR).launch(); ctx = b.new_context(viewport={"width": 1440, "height": 900}, color_scheme=scheme); pg = ctx.new_page(); pg.goto(f"{LOCAL}/?t={TOK}"); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5); open_s04(pg, 3)
        cols = pg.evaluate("""()=>{const pc=s=>{const m=getComputedStyle(s).color.match(/[\\d.]+/g).map(Number); return m.slice(0,3)}; const bg=e=>{while(e){const c=getComputedStyle(e).backgroundColor.match(/[\\d.]+/g).map(Number); if(c.length<4||c[3]>0.5) return c.slice(0,3); e=e.parentElement} return [255,255,255]}; const t=document.querySelector('.stabs [role=tab][aria-selected=false]'), n=document.querySelector('.sbody .note'), a=document.querySelector('.stabs [role=tab][aria-selected=true]'); return [[pc(t),bg(t)],[pc(n),bg(n)],[pc(a),bg(a)]]}""")
        cr = [round(contrast(c[0], c[1]), 2) for c in cols]
        rec(f"[{T.BR}][v102][{scheme}] metin kontrastı (pasif sekme, ikincil metin, aktif sekme) ≥ 4.5:1", all(x >= 4.5 for x in cr), cr)
        pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_v102_{scheme}_slide.png")); b.close()
    rec(f"[{T.BR}][v102] konsol/istisna yok", not errs, errs[:3])


if __name__ == "__main__":
    with sync_playwright() as p:
        main(p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_v102_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in T.RES), "PASS /", sum(r["result"] == "FAIL" for r in T.RES), "FAIL")

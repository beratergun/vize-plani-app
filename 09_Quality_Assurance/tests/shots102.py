# -*- coding: utf-8 -*-
"""Önce/sonra ekran görüntüleri + ölçümler. py shots102.py onceki|sonraki [chromium|webkit]"""
import sys, os, json, time
from playwright.sync_api import sync_playwright
TAG = sys.argv[1]; BR = sys.argv[2] if len(sys.argv) > 2 else "chromium"
OUT = os.path.join(r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V102", TAG); os.makedirs(OUT, exist_ok=True)
TOK = open(os.path.join(os.environ["APPDATA"], "VizePlani", "token.txt"), encoding="utf-8").read().strip()
URL = f"http://127.0.0.1:8790/?t={TOK}"
SIZES = [(1920, 1080), (1366, 768), (1024, 768), (768, 1024), (390, 844), (375, 812)]
ST = "(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \d+ \/ \d+/.test(e.textContent) ? e.textContent : ''})()"
def until(pg, js, t=60):
    s = time.time()
    while time.time() - s < t:
        try:
            v = pg.evaluate(js)
            if v: return v
        except Exception: pass
        time.sleep(0.4)
M = []
with sync_playwright() as p:
    for scheme in ("dark", "light"):
        for w, h in SIZES:
            b = getattr(p, BR).launch(); ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, has_touch=w < 800, is_mobile=w < 800); pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(URL); pg.wait_for_selector("nav.tabs a", state="attached"); time.sleep(1.5)
            pg.evaluate("location.hash='#slayt'; 0"); time.sleep(1.5)
            m = {"size": f"{w}x{h}", "scheme": scheme}
            pg.screenshot(path=os.path.join(OUT, f"{w}x{h}_{scheme}_home.png"))
            m["home_overflow"] = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            try:
                pg.select_option("#vw-c1", label="CMPE327"); time.sleep(0.4); pg.select_option("#vw-f", value="Slide04.pdf"); until(pg, ST, 60)
                pg.fill("#vw-p", "26"); pg.press("#vw-p", "Enter"); until(pg, "(document.querySelector('#vw-st')||{}).textContent==='sayfa 26 / 33'", 60); time.sleep(1.5)
            except Exception as e:
                m["err"] = str(e)[:100]
            pg.screenshot(path=os.path.join(OUT, f"{w}x{h}_{scheme}_slide.png"))
            m.update(pg.evaluate("""()=>{const r=s=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); return [Math.round(b.width),Math.round(b.height),Math.round(b.top)]}; const c=document.querySelector('#vw-c'); const small=[...document.querySelectorAll('.vw button,.vw select,.vw input')].filter(e=>{const b=e.getBoundingClientRect(); return b.width>0&&(b.height<36)}).length; return {overflow:document.documentElement.scrollWidth-window.innerWidth, bar:r('.vw .bar'), stage:r('#vw-cv'), canvas:c?[Math.round(c.getBoundingClientRect().width),Math.round(c.getBoundingClientRect().height)]:null, thumbs:r('#vw-th'), small_controls:small, page_h:document.documentElement.scrollHeight}}"""))
            m["errs"] = errs[:2]; M.append(m)
            if (w, h) == (1366, 768) and scheme == "dark":
                pg.keyboard.press("f"); time.sleep(1.2); pg.screenshot(path=os.path.join(OUT, f"{w}x{h}_{scheme}_present.png"))
            b.close()
json.dump(M, open(os.path.join(OUT, f"metrics_{BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for m in M: print(m)

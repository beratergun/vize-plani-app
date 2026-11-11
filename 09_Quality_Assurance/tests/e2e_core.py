# -*- coding: utf-8 -*-
"""V7 uçtan uca testler (Playwright). Kullanım: py e2e_core.py [chromium|webkit] [URL]
Her test gerçek kullanıcı etkileşimi yapar ve sonucu doğrular. Sonuçlar results_<browser>.json'a yazılır."""
import sys, os, json, time, re
from playwright.sync_api import sync_playwright

BR = sys.argv[1] if len(sys.argv) > 1 else "chromium"
URL = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8765/index.html"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\berat\Desktop\DERSLER\_Vize_Plani_Proje\QA_V7"
SHOTS = os.path.join(OUT, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
DERS = r"C:\Users\berat\Desktop\DERSLER"
F453 = os.path.join(DERS, "cmpe 453", "Lecture2.2 (1).pdf")
F421 = os.path.join(DERS, "_pdf_donusum", "cmpe 421", "Ch.3.pdf")
RES = []


def rec(name, ok, detail=""):
    RES.append({"test": name, "result": "PASS" if ok else "FAIL", "detail": str(detail)[:400]})
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + str(detail)[:200]) if detail else ""), flush=True)


def skip(name, why):
    RES.append({"test": name, "result": "NOT TESTED", "detail": why}); print("NOT TESTED " + name + " :: " + why, flush=True)


VIEWPORTS = [("desktop-1920x1080", 1920, 1080), ("laptop-1366x768", 1366, 768), ("mobile-390x844", 390, 844), ("mobile-375x812", 375, 812), ("tablet-768x1024", 768, 1024)]


def newctx(p, w=1366, h=768, mobile=False):
    b = getattr(p, BR).launch()
    c = b.new_context(viewport={"width": w, "height": h}, accept_downloads=True, has_touch=mobile)
    pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append("console." + m.type + ": " + m.text) if m.type in ("error", "warning") else None)
    pg.on("requestfailed", lambda r: errs.append("requestfailed: " + r.url[:100]))
    ext = []
    pg.on("request", lambda r: ext.append(r.url) if not r.url.startswith(("http://127.0.0.1", "data:", "blob:")) else None)
    pg.errs = errs; pg.ext = ext
    if os.environ.get('FREEZE'): pg.clock.install(time=os.environ['FREEZE'])  # tarihe bağlı testler (planlayıcı) için sabit saat
    pg.goto(URL); pg.wait_for_selector("nav.tabs a", state="attached")
    return b, c, pg


def tab(pg, t):
    pg.evaluate(f"location.hash='#{t}'; 0")
    pg.wait_for_function(f'location.hash=="#{t}"')
    pg.wait_for_timeout(300)  # render tamamlansın


def main():
    with sync_playwright() as p:
        # ---------- 1. Sekmeler / taşma / erişilebilirlik (5 ekran boyutu)
        for vn, w, h in VIEWPORTS:
            b, c, pg = newctx(p, w, h, mobile=w < 800)
            tabs = pg.eval_on_selector_all('nav.tabs a[data-tab]', 'els=>els.map(e=>e.dataset.tab)')
            bad = []
            for t in tabs:
                if w <= 760:   # mobil: alt gezinme (4 ana ekran) + "Daha fazla" sayfası; gerçek dokunma/tıklama
                    if t in ("bugun", "takvim", "hazirlan", "slayt"):
                        a = pg.locator(f'.bnav a[data-bt="{t}"]')
                    else:
                        pg.click('.bnav [data-bmore]'); pg.wait_for_timeout(100); a = pg.locator(f'#bsheet a[data-bt="{t}"]')
                    if not a.is_visible(): bad.append(t + ":gizli(mobil)"); continue
                    bb = a.bounding_box()
                    if not bb or bb["height"] < 44: bad.append(t + ":küçük-dokunma-hedefi")
                else:
                    a = pg.locator(f'nav.tabs a[data-tab="{t}"]')
                    if not a.is_visible():  # 980+ geniş ekranda panel sekmesi bilerek gizli (yan panel görünür)
                        if t == "panel" and w >= 980: continue
                        bad.append(t + ":gizli"); continue
                    a.scroll_into_view_if_needed()
                try:
                    a.click(timeout=3000)
                    pg.wait_for_function(f'location.hash=="#{t}"', timeout=3000)
                    pg.wait_for_timeout(120)
                except Exception as e:
                    bad.append(t + ":tıklanamadı"); continue
                if pg.evaluate("document.documentElement.scrollWidth > innerWidth + 2"): bad.append(t + ":yatay-taşma")
                if pg.locator("#view").inner_text().strip() == "": bad.append(t + ":boş-ekran")
            real = [e for e in pg.errs if "fonts.g" not in e]
            rec(f"[{BR}] konsol hata/uyarı yok, yakalanmamış istisna yok {vn}", not real, real[:3])
            rec(f"[{BR}] sekmeler+taşma {vn} ({len(tabs)} sekme)", not bad, bad)
            # Kütüphane ekranda mı
            tab(pg, "kutuphane")
            box = (pg.locator('.bnav').bounding_box() if w <= 760 else pg.locator('nav.tabs a[data-tab="kutuphane"]').bounding_box())
            rec(f"[{BR}] gezinme (üst sekme / mobil alt çubuk) viewport içinde {vn}", box and 0 <= box["x"] and box["x"] + box["width"] <= w + 1 and box["y"] >= 0 and box["y"] + box["height"] <= h + 1, box)
            pg.screenshot(path=os.path.join(SHOTS, f"{BR}_kutuphane_{vn}.png"))
            b.close()
        # klavye erişimi
        b, c, pg = newctx(p, 1366, 768)
        pg.focus('nav.tabs a[data-tab="bugun"]')
        n = 0
        while n < 30 and pg.evaluate("document.activeElement.dataset && document.activeElement.dataset.tab") != "kutuphane":
            pg.keyboard.press("Tab"); n += 1
        pg.keyboard.press("Enter"); pg.wait_for_timeout(200)
        rec(f"[{BR}] Kütüphane klavye (Tab+Enter)", pg.evaluate("location.hash") == "#kutuphane", f"{n} tab")
        # harici bağımlılık
        rec(f"[{BR}] harici script/CDN isteği yok", not [u for u in pg.ext if u.endswith(".js") or "cdn" in u], pg.ext[:5])
        b.close()
        return


if __name__ == "__main__":
    main()
    out = os.path.join(OUT, f"results_{BR}.json")
    json.dump(RES, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("özet:", sum(r["result"] == "PASS" for r in RES), "PASS /", sum(r["result"] == "FAIL" for r in RES), "FAIL /", sum(r["result"] == "NOT TESTED" for r in RES), "NOT TESTED")

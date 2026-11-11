# -*- coding: utf-8 -*-
"""Arama (PORTB), yedek round-trip, içe aktarma, planlayıcı. Kullanım: py e2e_features.py [chromium|webkit]"""
import sys, os, json, re, shutil, tempfile, hashlib
import e2e_core as T
from e2e_core import rec, skip, newctx, tab, sync_playwright, SHOTS
from e2e_viewer import canvas_state, wait_render, status

SEED = {"task": {}, "time": {}, "notes": {"qs:x1": {"v": "Verified", "t": 1000}}, "con": {}, "badges": {}, "pomo": {}, "cards": {},
        "mist": {"m1": {"c": "CMPE327", "top": "TEST yanlış", "why": "x", "note": "n", "fix": "f", "d": "2026-11-08", "r3": 0, "r7": 0, "t": 1000}},
        "mynotes": {"pg:Slide01.pdf:3": {"v": "TEST sayfa notu ÖĞĞ", "t": 1000}}, "grades": {}, "mocks": {}, "moves": {}, "locks": {}, "reset": 0, "theme": "", "ts": 1000}
KEYS = ["task", "time", "notes", "con", "badges", "pomo", "cards", "mist", "mynotes", "grades", "mocks", "moves", "locks"]


def find_file(name):
    for root, _, fs in os.walk(T.DERS):
        if name in fs and "_Vize_Plani_Proje" not in root:
            return os.path.join(root, name)
    return None


def seeded(p, w=1366, h=768):
    b = getattr(p, T.BR).launch()
    c = b.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
    pg = c.new_page(); pg.errs = []
    pg.on("pageerror", lambda e: pg.errs.append(str(e)))
    # her açılışta değil, yalnızca depo boşken tohumla (reload'da test verisi ezilmesin)
    c.add_init_script("try{ if(!localStorage.getItem('vizeplan.v2')) localStorage.setItem('vizeplan.v2', %s) }catch(e){}" % json.dumps(json.dumps(SEED)))
    pg.goto(T.URL); pg.wait_for_selector("nav.tabs a", state="attached")
    return b, c, pg


def ls_state(pg):
    raw = pg.evaluate("localStorage.getItem('vizeplan.v2')"); d = json.loads(raw) if raw else {}
    for k in KEYS: d.setdefault(k, {})
    return d


def test_search(p):
    b, c, pg = newctx(p)
    tab(pg, "kutuphane")
    pg.fill("#lib-q", "PORTB")
    pg.wait_for_selector("#lib-res .qi")
    n = pg.locator("#lib-res .qi").count()
    hits = pg.evaluate("[...document.querySelectorAll('#lib-res .qi')].slice(0,5).map(q=>({f:q.querySelector('b').textContent,p:q.querySelector('.min').textContent,t:q.querySelector('.snip').textContent.toLowerCase().includes('portb')}))")
    rec(f"[{T.BR}] PORTB: sonuç var, kaynak+sayfa gösteriliyor, snippet 'PORTB' içeriyor", n > 0 and all(h["t"] for h in hits), {"adet": n, "ilk": hits[:2]})
    first = hits[0]; pno = int(re.search(r"\d+", first["p"]).group())
    pg.locator("#lib-res .qi").first.locator('button[data-act="vw-open"]').click()
    pg.wait_for_function("location.hash=='#slayt'")
    try: pg.wait_for_selector('text=Orijinal slayt dosyası bağlı değil', timeout=15000)
    except Exception: pass
    body = pg.locator("#view").text_content()  # <option> metni WebKit inner_text'inde yok
    pageval = pg.evaluate("(document.querySelector('#vw-p')||{}).value")
    rec(f"[{T.BR}] PORTB 'Slaytı aç': doğru dosya+sayfa, dosya yoksa 'Orijinal slayt dosyası bağlı değil' açıkça yazıyor",
        first["f"] in body and str(pageval) == str(pno) and ("Orijinal slayt dosyası bağlı değil" in body), {"beklenen": [first["f"], pno], "sayfa_kutusu": pageval})
    rec(f"[{T.BR}] PORTB eksik-dosya ekranında dizinli metin gösteriliyor", "portb" in pg.locator(".pgtxt").first.text_content().lower(), "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_portb_missing.png"))
    # gerçek dosya varsa ekle ve doğru sayfanın çizildiğini doğrula
    real = find_file(first["f"])
    if real and real.lower().endswith(".pdf"):
        pg.set_input_files("#vw-files", real)
        pg.wait_for_function("(()=>{const e=document.querySelector('#vw-st'); return e && /^sayfa \d+ \/ \d+/.test(e.textContent)})()", timeout=40000)
        tab(pg, "bugun"); tab(pg, "kutuphane"); pg.fill("#lib-q", "PORTB"); pg.wait_for_selector("#lib-res .qi")
        pg.locator("#lib-res .qi").first.locator('button[data-act="vw-open"]').click()
        try:
            wait_render(pg, 40000); ok = True
        except Exception:
            ok = False
        cs = canvas_state(pg)
        rec(f"[{T.BR}] PORTB → gerçek dosya eklenince doğru sayfa ÇİZİLİYOR", ok and f"sayfa {pno} /" in status(pg) and cs and cs["ink"] > 3, {"durum": status(pg), "dosya": first["f"]})
        pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_portb_rendered.png"))
    else:
        skip(f"[{T.BR}] PORTB sonucu gerçek PDF ile çizim", f"{first['f']} PDF olarak diskte yok (PPTX/yok): çizim yalnızca metin görünümüyle doğrulandı")
    b.close()


def test_backup(p):
    b, c, pg = seeded(p)
    tab(pg, "kaynaklar")
    with pg.expect_download(timeout=15000) as dl:
        pg.click('button[data-act="bk-export"]')
    d = dl.value; path = os.path.join(tempfile.gettempdir(), "bk_test_" + d.suggested_filename); d.save_as(path)
    raw = open(path, "rb").read()
    rec(f"[{T.BR}] yedek indirildi, boş değil", len(raw) > 200, f"{d.suggested_filename} {len(raw)} bayt")
    o = json.loads(raw.decode("utf-8"))
    body_sha = hashlib.sha256(json.dumps(o["data"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    rec(f"[{T.BR}] yedek biçimi geçerli (format/version/sha256)", o["meta"]["format"] == "vizeplan-backup" and o["meta"]["version"] == 3 and len(o["sha256"]) == 64, o["meta"]["counts"])
    rec(f"[{T.BR}] yedek içeriği: not + yanlış defteri + soru durumu korunmuş",
        o["data"]["mynotes"]["pg:Slide01.pdf:3"]["v"] == "TEST sayfa notu ÖĞĞ" and "m1" in o["data"]["mist"] and "qs:x1" in o["data"]["notes"], "")
    clean = lambda st: {k: {i: v for i, v in st[k].items() if not (k == "notes" and i in ("bk:last", "plan:day"))} for k in KEYS}
    before = clean(ls_state(pg))
    # veriyi uygulama KAPALIYKEN değiştir (açık uygulama çıkışta kendi durumunu geri yazar)
    pg.goto(T.URL.rsplit("/", 1)[0] + "/yok.html")
    pg.evaluate("""()=>{const s=JSON.parse(localStorage.getItem('vizeplan.v2')); s.mynotes={}; s.mist={}; s.notes={}; s.ts=Date.now(); localStorage.setItem('vizeplan.v2',JSON.stringify(s));}""")
    pg.goto(T.URL); pg.wait_for_selector("nav.tabs a", state="attached")
    mid = ls_state(pg)
    rec(f"[{T.BR}] veri gerçekten değiştirildi (round-trip ön koşulu)", not mid["mynotes"] and not mid["mist"], "")
    tab(pg, "kaynaklar")
    pg.set_input_files('input[data-act="bk-file"]', path)
    pg.wait_for_selector("text=Geri yükleme önizlemesi")
    rec(f"[{T.BR}] geri yükleme önizlemesi + bütünlük ✓ gösteriliyor", "bütünlük ✓" in pg.locator("#view").inner_text(), "")
    btn = pg.locator('button[data-act="bk-replace"]')
    btn.click(); pg.wait_for_timeout(600)
    after = clean(ls_state(pg))
    same = all(json.dumps(after[k], sort_keys=True) == json.dumps(before[k], sort_keys=True) for k in KEYS)
    rec(f"[{T.BR}] export→bozma→import round-trip: başlangıç verisiyle birebir eşleşiyor", same, [k for k in KEYS if json.dumps(after[k], sort_keys=True) != json.dumps(before[k], sort_keys=True)])
    # bozuk yedek reddedilir
    bad = json.loads(raw.decode("utf-8")); bad["data"]["mynotes"]["pg:Slide01.pdf:3"]["v"] = "DEĞİŞTİRİLDİ"
    bp = os.path.join(tempfile.gettempdir(), "bk_tampered.json"); open(bp, "w", encoding="utf-8").write(json.dumps(bad))
    tab(pg, "kaynaklar"); pg.set_input_files('input[data-act="bk-file"]', bp); pg.wait_for_timeout(700)
    rec(f"[{T.BR}] elle değiştirilmiş yedek REDDEDİLİYOR", "bütünlük" in pg.locator("#view").inner_text() and "Geri yüklenemedi" in pg.locator("#view").inner_text(), "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_backup.png"))
    b.close()


IDBCOUNT = """()=>new Promise((res,rej)=>{const r=indexedDB.open('vizeplan-files'); r.onerror=()=>rej(r.error); r.onsuccess=()=>{const d=r.result; const q=d.transaction('files').objectStore('files').getAllKeys(); q.onsuccess=()=>{res(q.result)}}})"""


def stage(pg, f):
    pg.set_input_files('input[data-act="imp-files"] >> nth=0', f); pg.wait_for_timeout(1200)


def test_import(p):
    import zipfile
    b, c, pg = newctx(p); pg.set_default_timeout(25000)
    if not os.path.exists(T.F421):
        skip(f"[{T.BR}] Ch.3.pdf içe aktarma", "dosya yok"); b.close(); return
    tab(pg, "kutuphane")
    stage(pg, T.F421)
    txt = pg.locator("#view").inner_text()
    rec(f"[{T.BR}] içe aktarma önizlemesi: Ch.3.pdf → CMPE421, PPTX eşleşmesi gösteriliyor", "CMPE421" in txt and "Ch.3.pptx" in txt, "")
    pg.click('button[data-act="imp-go"]'); pg.wait_for_selector("text=Özet:")
    txt = pg.locator("#view").inner_text()
    rec(f"[{T.BR}] Ch.3: 1 eklendi, 0 hata, sayfa sayısı 56 doğrulandı", "eklenen 1" in txt and "hata 0" in txt and "56 sayfa" in txt, re.findall(r"Özet:[^\n]*", txt))
    keys = pg.evaluate(IDBCOUNT)
    rec(f"[{T.BR}] depoda tam 1 dosya (duplicate yok)", len(keys) == 1, keys)
    # ikinci kez
    stage(pg, T.F421); pg.click('button[data-act="imp-go"]'); pg.wait_for_function("document.body.innerText.includes('aynı (atlandı) 1')")
    keys = pg.evaluate(IDBCOUNT)
    rec(f"[{T.BR}] aynı dosya ikinci kez: 'aynı (atlandı) 1', duplicate oluşmadı", len(keys) == 1, keys)
    # indeks/ilerleme korundu
    m = re.search(r"(\d+) sayfa/slayt dizinli", pg.locator("#view").inner_text())
    rec(f"[{T.BR}] dizin korundu (>= 2697 sayfa)", bool(m) and int(m.group(1)) >= 2697, m and m.group(0))
    # görüntüleyicide aç
    tab(pg, "slayt"); pg.select_option("#vw-c1", label="CMPE421"); pg.select_option("#vw-f", value="Ch.3.pptx")
    try:
        wait_render(pg, 40000); ok = True
    except Exception:
        ok = False
    cs = canvas_state(pg)
    rec(f"[{T.BR}] PPTX→PDF dönüşümü slayt görüntüleyicide çiziliyor (sayfa=slayt)", ok and status(pg).startswith("sayfa 1 / 56") and cs and cs["ink"] > 3, status(pg))
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_ch3_rendered.png"))
    # yanlış dosya: başka PDF'i Ch.3.pdf adıyla ver
    tmp = tempfile.mkdtemp(); wrong = os.path.join(tmp, "Ch.3.pdf"); shutil.copy(T.F453, wrong)
    b2, c2, pg2 = newctx(p); pg2.set_default_timeout(25000)
    tab(pg2, "kutuphane"); stage(pg2, wrong)
    t2 = pg2.locator("#view").inner_text()
    if pg2.locator('button[data-act="imp-go"]').count(): pg2.click('button[data-act="imp-go"]'); pg2.wait_for_timeout(2500)
    t2 = pg2.locator("#view").inner_text()
    keys2 = pg2.evaluate(IDBCOUNT)
    rec(f"[{T.BR}] yanlış dosya (Lecture2.2'yi Ch.3.pdf diye verme) REDDEDİLİYOR", len(keys2) == 0 and ("eşleşmedi" in t2 or "uyuşmuyor" in t2 or "hata 1" in t2 or "uyarı" in t2.lower()), {"depo": keys2, "ipucu": [l for l in t2.split("\n") if "Ch.3" in l or "hata" in l][:3]})
    b2.close()
    # küçük ZIP fixture
    zp = os.path.join(tmp, "mini.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(T.F453, "cmpe 453/Lecture2.2 (1).pdf"); z.writestr("cmpe 453/notlar.txt", "x")
    b3, c3, pg3 = newctx(p); pg3.set_default_timeout(25000)
    tab(pg3, "kutuphane"); stage(pg3, zp)
    t3 = pg3.locator("#view").inner_text()
    pg3.click('button[data-act="imp-go"]'); pg3.wait_for_selector("text=Özet:")
    k3 = pg3.evaluate(IDBCOUNT); t3 = pg3.locator("#view").inner_text()
    rec(f"[{T.BR}] küçük ZIP: PDF çıkarıldı+eklendi, .txt atlandı/uyarıldı (sessiz atlama yok)", "Lecture2.2 (1).pdf" in k3 and ("notlar.txt" in t3), {"depo": k3, "özet": re.findall(r"Özet:[^\n]*", t3)})
    b3.close(); b.close(); shutil.rmtree(tmp, ignore_errors=True)


CARDS = """()=>[...document.querySelectorAll('#view .qi')].map(q=>{const r=q.getBoundingClientRect(),v=document.querySelector('#view').getBoundingClientRect();return {t:q.querySelector('b').textContent,badges:[...q.querySelectorAll('.badge2')].map(x=>x.textContent),why:(q.querySelector('.note')||{}).textContent||'',w:r.width,vw:v.width,r:r.right}})"""


def test_planner(p):
    # 1) kartlar, 5 ekran boyutunda
    for vn, w, h in T.VIEWPORTS:
        b, c, pg = newctx(p, w, h, mobile=w < 800)
        tab(pg, "planlayici"); pg.wait_for_selector("#view .qi", timeout=15000)
        cards = pg.evaluate(CARDS)
        ok = len(cards) == 14 and all(len(x["badges"]) == 2 and "→" not in x["badges"][0] and len(x["why"]) > 15 and x["w"] >= x["vw"] * 0.85 and x["r"] <= w for x in cards)
        rec(f"[{T.BR}] planlayıcı kartları {vn}: 14 kart, eski+yeni gün, gerekçe okunur, genişlik ≥%85, taşma yok", ok, {"ilk": cards[0] if cards else None})
        if w in (1366, 390): pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_planner_{vn}.png"))
        b.close()
    # 2) onay olmadan değişmiyor; uygula; geri al; sınav tarihleri değişmez
    b, c, pg = newctx(p); pg.set_default_timeout(15000)
    tab(pg, "sinavlar"); ex0 = pg.locator("#view").inner_text()
    tab(pg, "planlayici"); pg.wait_for_selector("#view .qi", timeout=15000)
    st = ls_state(pg)
    rec(f"[{T.BR}] önizleme tek başına planı DEĞİŞTİRMİYOR (onay yok → moves boş)", not st.get("moves"), st.get("moves"))
    first = pg.evaluate(CARDS)[0]
    pg.click('button[data-act="plan-apply"]'); pg.wait_for_timeout(500)
    st = ls_state(pg); nm = len([k for k, v in st["moves"].items() if not v.get("del")])
    rec(f"[{T.BR}] 'Önizlemeyi uygula' planı gerçekten değiştiriyor (14 taşıma kaydı)", nm == 14, nm)
    tab(pg, "sinavlar"); ex1 = pg.locator("#view").inner_text()
    rec(f"[{T.BR}] uygulamadan sonra sınav/ödev tarihleri değişmedi", ex0 == ex1, "")
    tab(pg, "planlayici"); pg.wait_for_timeout(400)
    rec(f"[{T.BR}] uygulanınca öneri kalmadı (boş durum mesajı)", "Taşınacak görev yok" in pg.locator("#view").inner_text() or pg.locator("#view .qi").count() == 0, "")
    pg.click('button[data-act="plan-undo"]'); pg.wait_for_timeout(500)
    st = ls_state(pg); nm = len([k for k, v in st["moves"].items() if not v.get("del")])
    rec(f"[{T.BR}] 'Geri al' önceki plana döndürüyor (0 taşıma, 14 öneri geri geldi)", nm == 0 and pg.locator("#view .qi").count() == 14, nm)
    b.close()
    # 3) kilitli görev: kilitliyi hiç taşımıyor
    b, c, pg = newctx(p); pg.set_default_timeout(15000)
    ids = pg.evaluate("""()=>{const o={}; DATA.days.forEach(d=>(d.tasks||d.t||[]).forEach(t=>{o[t.ti||t.title||t.n]=t.id})); return o}""")
    tab(pg, "planlayici"); ft = pg.evaluate(CARDS)[0]["t"]
    tid = ids.get(ft)
    if not tid:
        skip(f"[{T.BR}] kilitli görev testi", "görev kimliği bulunamadı"); b.close(); return
    pg.goto(T.URL.rsplit("/", 1)[0] + "/yok.html")
    pg.evaluate("(id)=>{const s=JSON.parse(localStorage.getItem('vizeplan.v2')||'{}'); s.locks=s.locks||{}; s.locks[id]={v:1,t:Date.now()}; s.task=s.task||{}; localStorage.setItem('vizeplan.v2',JSON.stringify(s))}", tid)
    pg.goto(T.URL); pg.wait_for_selector("nav.tabs a", state="attached"); tab(pg, "planlayici"); pg.wait_for_selector("#view .qi", timeout=15000)
    titles = [x["t"] for x in pg.evaluate(CARDS)]
    rec(f"[{T.BR}] kilitli görev ('{ft}') öneriden çıkarıldı, diğer 13 duruyor", ft not in titles and len(titles) == 13, len(titles))
    b.close()
    # 4) boş program: plan başlamadan önceki tarih
    b = getattr(p, T.BR).launch(); c = b.new_context(viewport={"width": 1366, "height": 768}); pg = c.new_page()
    pg.clock.install(time="2026-09-05T10:00:00+03:00")
    pg.goto(T.URL); pg.wait_for_selector("nav.tabs a", state="attached"); tab(pg, "planlayici")
    rec(f"[{T.BR}] boş durum: geride görev yokken anlamlı mesaj ('Taşınacak görev yok')", "Taşınacak görev yok" in pg.locator("#view").inner_text(), "")
    pg.screenshot(path=os.path.join(SHOTS, f"{T.BR}_planner_empty.png"))
    b.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        for fn in os.environ.get("TESTS", "search,backup").split(","):
            globals()["test_" + fn](p)
    json.dump(T.RES, open(os.path.join(T.OUT, f"results_features_{T.BR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

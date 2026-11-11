# -*- coding: utf-8 -*-
"""Her öğrenme bloğu için güvenilir kanallardan, konuyla alakalı videoları bulur ve oEmbed ile varlığını doğrular.
Çıktı: videos.json  {blok: [{id, t, ch, d}]}   (t=başlık, ch=kanal, d=süre)
Kural: kanal tercih listesinde olmalı, başlık konu sözcüklerinden en az 2'sini içermeli, süre 3–75 dk olmalı."""
import concurrent.futures as cf
import json
import os
import re
import urllib.parse
import urllib.request
import resources as R
import plan_data as P

UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
PREF = {
    "BIO110": ["Amoeba Sisters", "Khan Academy", "CrashCourse", "Bozeman Science", "Professor Dave Explains", "Ninja Nerd", "Khan Academy Organic Chemistry"],
    "CMPE371": ["MIT OpenCourseWare", "Neso Academy", "3Blue1Brown", "Khan Academy", "Brian Douglas", "Professor Leonard", "Iain Explains Signals, Systems, and Digital Comms", "ALL ABOUT ELECTRONICS"],
    "CMPE327": ["Neso Academy", "Easy Theory", "MIT OpenCourseWare", "Gate Smashers", "Computerphile", "Stanford Online", "Jeff Erickson", "Tom Scott"],
    "CMPE421": ["Computerphile", "MIT OpenCourseWare", "CS50", "Stanford Online", "StatQuest with Josh Starmer", "3Blue1Brown", "Spanning Tree", "Neso Academy", "Gate Smashers", "Pieter Abbeel"],
    "CMPE453": ["Microchip Technology", "Patrick Hood-Daniel", "newbiehack", "ElectroNoobs", "Jacob Sorber", "Low Level Learning", "GreatScott!", "Ben Eater", "Learn Electronics Online", "Embedded Systems Academy", "ControllersTech"],
}
STOP = set("a an the and or of to in on for with is are vs how what why video explained review examples example basics basic introduction intro".split())


OVR = {
    "S0b": ("trigonometric identities explained", ["trig"]),
    "S2": ("sinusoids amplitude frequency phase signals and systems", ["sinusoid"], ["ac voltage", "circuit"]),
    "S4a": ("discrete-time convolution sum signals and systems", ["convolution"], ["fourier", "continuous"]),
    "S4b": ("continuous-time convolution integral signals and systems", ["convolution"], ["fourier", "discrete"]),
    "S6": ("continuous-time Fourier series coefficients", ["fourier series"], ["discrete"]),
    "I8": ("resolution theorem proving propositional logic", ["resolution"], []),
    "I3": ("A* search algorithm explained heuristic", ["a*"]),
    "I5": ("constraint satisfaction problems backtracking", ["constraint"]),
    "I6": ("AI planning STRIPS PDDL", ["planning", "strips", "pddl"]),
    "M1": ("ATmega328P architecture AVR registers memory", ["atmega", "avr"]),
    "M3": ("AVR GPIO DDR PORT PIN registers", ["avr", "ddr", "gpio"]),
    "M4": ("AVR push button input pull-up register", ["avr", "pull", "button"]),
    "M5": ("AVR UART USART register programming", ["uart", "usart"]),
    "M7": ("AVR ADC register ADMUX programming", ["adc"]),
    "M8": ("AVR interrupts ISR tutorial", ["interrupt"]),
    "M9": ("AVR timer counter prescaler tutorial", ["timer"]),
    "M10": ("AVR PWM fast PWM tutorial", ["pwm"]),
    "M11": ("STM32 Discovery board getting started tutorial", ["stm32"]),
}


def get(url, tries=2):
    for _ in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")
        except Exception:
            pass
    return ""


def search(q):
    html = get("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q) + "&hl=en")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    out = []
    if not m:
        return out

    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                try:
                    out.append(dict(id=v["videoId"], t=v["title"]["runs"][0]["text"], ch=v["ownerText"]["runs"][0]["text"], d=v.get("lengthText", {}).get("simpleText", ""), vw=int(re.sub(r"\D", "", v.get("viewCountText", {}).get("simpleText", "0")) or 0)))
                except Exception:
                    pass
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(json.loads(m.group(1)))
    return out


def secs(d):
    p = [int(x) for x in d.split(":")] if re.fullmatch(r"\d+(:\d+){1,2}", d or "") else []
    return sum(v * 60 ** i for i, v in enumerate(reversed(p))) if p else 0


def toks(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


def oembed_ok(vid):
    try:
        j = json.loads(get("https://www.youtube.com/oembed?url=" + urllib.parse.quote("https://www.youtube.com/watch?v=" + vid) + "&format=json"))
        return bool(j.get("title"))
    except Exception:
        return False


def curate_override(bid, c):
    q, req, *rest = OVR[bid]
    ban = rest[0] if rest else []
    need = toks(q)
    picked = []
    for v in search(q):
        s = secs(v["d"])
        if 240 <= s <= 3600 and any(r in v["t"].lower() for r in req) and not any(b in v["t"].lower() for b in ban) and (v["ch"] in PREF.get(c, []) or v["vw"] >= 50000) and v["id"] not in [p["id"] for p in picked] and len(need & toks(v["t"])) >= 1:
            picked.append(v)
        if len(picked) >= 2:
            break
    picked = [p for p in picked if oembed_ok(p["id"])]
    return bid, [dict(id=p["id"], t=p["t"], ch=p["ch"], d=p["d"]) for p in picked]


def curate(bid):
    b = P.BLOCKS[bid]
    c = b["course"]
    if bid in OVR:
        return curate_override(bid, c)
    yt = R.M.get(bid, ([], [], [], ""))[3]
    if not yt or c not in PREF:
        return bid, []
    need = toks(yt)
    cands = []
    for q in (yt, PREF[c][0] + " " + yt, PREF[c][1] + " " + yt):
        cands += search(q)
    picked, seen_ch = [], set()
    # tercih sırasına göre kanal başına en iyi 1 video
    for ch in PREF[c]:
        for v in cands:
            if v["ch"].lower() != ch.lower() or v["id"] in [p["id"] for p in picked]:
                continue
            ov = len(need & toks(v["t"]))
            s = secs(v["d"])
            if ov >= 2 and 180 <= s <= 4500 and ch not in seen_ch:
                picked.append(dict(v, ov=ov))
                seen_ch.add(ch)
                break
        if len(picked) >= 2:
            break
    picked = [p for p in picked if oembed_ok(p["id"])]
    return bid, [dict(id=p["id"], t=p["t"], ch=p["ch"], d=p["d"]) for p in picked]


def main():
    """Yalnızca videos.json'da olmayan öğrenme bloklarını arar; var olanları korur. Tümünü yenilemek için videos.json'u sil."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos.json")
    old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    ids = [i for i, b in P.BLOCKS.items() if b["kind"] == "L"]
    todo = [i for i in ids if i not in old]
    with cf.ThreadPoolExecutor(6) as ex:
        for bid, v in ex.map(curate, todo):
            old[bid] = v
            print(bid, [(x["ch"], x["t"][:50], x["d"]) for x in v])
    res = {i: old.get(i, []) for i in ids}
    seen = set()
    for bid in ids:
        keep = []
        for v in res[bid]:
            key = re.sub(r"[^a-z0-9]+", " ", v["t"].lower()).strip()
            if v["id"] not in seen and key not in seen:
                seen.add(v["id"])
                seen.add(key)
                keep.append(v)
        res[bid] = keep
    json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("bulunan:", sum(1 for v in res.values() if v), "/", len(ids), "blok; toplam video:", sum(len(v) for v in res.values()))


if __name__ == "__main__":
    main()

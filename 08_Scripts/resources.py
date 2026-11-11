# -*- coding: utf-8 -*-
"""Kaynak bağlantıları (hepsi curl ile açılış kontrolünden geçti; OpenStax bölüm numaraları sayfa özetleriyle doğrulandı).
Khan Academy sayfaları bot korumalı: açıldığı görüldü, içerik başlığı otomatik doğrulanamadı → destek kaynağı olarak işaretli."""

OS = "https://openstax.org/books/biology-2e/pages/{}-introduction"
KA = "https://www.khanacademy.org/science/ap-biology/"

# id: (etiket, url, not)
LINKS = {
    "os2": ("OpenStax Biology 2e · Bölüm 2: Yaşamın kimyası (atom, bağlar, su, pH, karbon)", OS.format(2), ""),
    "os3": ("OpenStax Biology 2e · Bölüm 3: Biyolojik makromoleküller", OS.format(3), ""),
    "os4": ("OpenStax Biology 2e · Bölüm 4: Hücre yapısı", OS.format(4), ""),
    "os5": ("OpenStax Biology 2e · Bölüm 5: Plazma zarı yapısı ve işlevi", OS.format(5), ""),
    "os6": ("OpenStax Biology 2e · Bölüm 6: Metabolizma", OS.format(6), ""),
    "os7": ("OpenStax Biology 2e · Bölüm 7: Hücresel solunum", OS.format(7), ""),
    "os8": ("OpenStax Biology 2e · Bölüm 8: Fotosentez", OS.format(8), ""),
    "os10": ("OpenStax Biology 2e · Bölüm 10: Hücre çoğalması ve döngüsü", OS.format(10), ""),
    "os12": ("OpenStax Biology 2e · Bölüm 12: Mendel ve kalıtım", OS.format(12), ""),
    "os13": ("OpenStax Biology 2e · Bölüm 13: Kalıtımın kromozomal temeli", OS.format(13), ""),
    "os14": ("OpenStax Biology 2e · Bölüm 14: DNA yapısı ve işlevi", OS.format(14), ""),
    "os15": ("OpenStax Biology 2e · Bölüm 15: Genler ve proteinler", OS.format(15), ""),
    "os16": ("OpenStax Biology 2e · Bölüm 16: Gen anlatımının düzenlenmesi", OS.format(16), ""),
    "os17": ("OpenStax Biology 2e · Bölüm 17: Biyoteknoloji", OS.format(17), ""),
    "ka_chem": ("Khan Academy · AP Biology: Yaşamın kimyası", KA + "chemistry-of-life", "bot korumalı"),
    "ka_cell": ("Khan Academy · AP Biology: Hücre yapısı ve işlevi", KA + "cell-structure-and-function", "bot korumalı"),
    "ka_energy": ("Khan Academy · AP Biology: Hücresel enerji", KA + "cellular-energetics", "bot korumalı"),
    "ka_cycle": ("Khan Academy · AP Biology: Hücre döngüsü", KA + "cell-communication-and-cell-cycle", "bot korumalı"),
    "ka_heredity": ("Khan Academy · AP Biology: Kalıtım", KA + "heredity", "bot korumalı"),
    "ka_gene": ("Khan Academy · AP Biology: Gen anlatımı ve düzenlenmesi", KA + "gene-expression-and-regulation", "bot korumalı"),
    "amoeba": ("Amoeba Sisters (YouTube kanalı) — kısa, görsel biyoloji videoları", "https://www.youtube.com/@AmoebaSisters", ""),
    "ka_complex": ("Khan Academy · Karmaşık sayılar", "https://www.khanacademy.org/math/precalculus/x9e81a4f98389efdf:complex", "bot korumalı"),
    "lamar": ("Paul's Online Math Notes (trigonometri, türev, integral özetleri)", "https://tutorial.math.lamar.edu/", ""),
    "desmos": ("Desmos grafik hesaplayıcı (sinyalleri çizip dene)", "https://www.desmos.com/calculator", ""),
    "ocw607": ("MIT OCW RES.6-007 Signals and Systems (Oppenheim video dersleri)", "https://ocw.mit.edu/courses/res-6-007-signals-and-systems-spring-2011/", ""),
    "ocw603": ("MIT OCW 6.003 Signals and Systems (notlar, problem setleri)", "https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/", ""),
    "b3b1": ("3Blue1Brown · Fourier dönüşümü sezgisi (video)", "https://www.youtube.com/watch?v=spUNpyF58BY", ""),
    "cs103": ("Stanford CS103 (kümeler, ispatlar, otomatlar, regex, CFG) ders sayfası", "https://web.stanford.edu/class/cs103/", ""),
    "jeffe": ("Jeff Erickson · Algorithms kitabı ve ders notları (ücretsiz)", "https://jeffe.cs.illinois.edu/teaching/algorithms/", ""),
    "ocw18404": ("MIT OCW 18.404 Theory of Computation (Sipser dersleri)", "https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/", ""),
    "jflap": ("JFLAP — otomat çizme ve simülasyon programı (ücretsiz)", "https://www.jflap.org/", ""),
    "autosim": ("Automaton Simulator — tarayıcıda DFA/NFA dene", "https://automatonsimulator.com/", ""),
    "regex101": ("regex101 — regex dene ve açıklamasını gör", "https://regex101.com/", ""),
    "cs188": ("UC Berkeley CS188 Artificial Intelligence (slaytlar, notlar, ödevler)", "https://inst.eecs.berkeley.edu/~cs188/", ""),
    "aima": ("AIMA (Russell & Norvig) kitap sitesi", "https://aima.cs.berkeley.edu/", ""),
    "cs50ai": ("Harvard CS50 AI with Python (arama, bilgi, belirsizlik, öğrenme)", "https://cs50.harvard.edu/ai/2024/", ""),
    "pathfind": ("PathFinding.js görsel: BFS/A*/Dijkstra'yı adım adım izle", "https://qiao.github.io/PathFinding.js/visual/", ""),
    "ocw6034": ("MIT OCW 6.034 Artificial Intelligence", "https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/", ""),
    "datasheet": ("ATmega328P veri sayfası (Microchip, PDF) — register tabloları", "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061A.pdf", ""),
    "avrlibc": ("AVR Libc kullanım kılavuzu (avr-gcc, makrolar, bit işlemleri)", "https://avrdudes.github.io/avr-libc/avr-libc-user-manual/", ""),
    "elliot": ("Elliot Williams · AVR Programming kitabı örnek kodları (GitHub)", "https://github.com/hexagon5un/AVR-Programming", "syllabus'taki 'Elliot' kitabı olduğu varsayıldı"),
    "wokwi": ("Wokwi — tarayıcıda Arduino/AVR simülatörü (isteğe bağlı)", "https://wokwi.com/projects/new/arduino-uno", ""),
    "tinkercad": ("Tinkercad Circuits — devre simülatörü (isteğe bağlı)", "https://www.tinkercad.com/circuits", ""),
    "obs": ("OBS Studio — ekran ve ses kaydı (ücretsiz)", "https://obsproject.com/", ""),
    "resolve": ("DaVinci Resolve — video düzenleme (ücretsiz sürüm var)", "https://www.blackmagicdesign.com/products/davinciresolve", ""),
    "zotero": ("Zotero — kaynakça yöneticisi (ücretsiz)", "https://www.zotero.org/", ""),
    "langtool": ("LanguageTool — yazım ve dil denetimi", "https://languagetool.org/", ""),
    "anki": ("Anki — aralıklı tekrar kartları (ücretsiz)", "https://apps.ankiweb.net/", ""),
    "pomo": ("Pomofocus — çalışma/mola sayacı", "https://pomofocus.io/", ""),
}

LINKS.update({
    "os18": ("OpenStax Biology 2e · Bölüm 18: Evrim ve türlerin kökeni (Darwin, doğal seçilim, kanıtlar)", "https://openstax.org/books/biology-2e/pages/18-introduction", ""),
    "os19": ("OpenStax Biology 2e · Bölüm 19: Popülasyonların evrimi (Hardy–Weinberg, sürüklenme)", "https://openstax.org/books/biology-2e/pages/19-introduction", ""),
    "ka_nat": ("Khan Academy · AP Biology: Doğal seçilim", KA + "natural-selection", "bot korumalı"),
    "cs50n0": ("CS50 AI ders notu 0: Arama (BFS, DFS, A*, minimax)", "https://cs50.harvard.edu/ai/2024/notes/0/", ""),
    "cs50n1": ("CS50 AI ders notu 1: Bilgi ve mantık (çıkarım, resolution)", "https://cs50.harvard.edu/ai/2024/notes/1/", ""),
    "cs50n2": ("CS50 AI ders notu 2: Belirsizlik (olasılık, Bayes)", "https://cs50.harvard.edu/ai/2024/notes/2/", ""),
    "cs50n3": ("CS50 AI ders notu 3: Optimizasyon (CSP, arama)", "https://cs50.harvard.edu/ai/2024/notes/3/", ""),
    "cs50n4": ("CS50 AI ders notu 4: Öğrenme (sınıflandırma, regresyon, pekiştirmeli öğrenme)", "https://cs50.harvard.edu/ai/2024/notes/4/", ""),
    "cs50n5": ("CS50 AI ders notu 5: Sinir ağları", "https://cs50.harvard.edu/ai/2024/notes/5/", ""),
    "cs50n6": ("CS50 AI ders notu 6: Dil (NLP, dil modelleri)", "https://cs50.harvard.edu/ai/2024/notes/6/", ""),
    "cs231n": ("Stanford CS231n: Sinir ağları notları (aktivasyon, geri yayılım)", "https://cs231n.github.io/neural-networks-1/", ""),
    "tfplay": ("TensorFlow Playground — sinir ağını tarayıcıda dene", "https://playground.tensorflow.org/", ""),
})

# blok -> (ana, destek, uygulama linkleri [id...], youtube arama sorgusu)
M = {}


def m(ids, main, support=(), practice=(), yt=""):
    for i in ids.split():
        M[i] = (list(main), list(support), list(practice), yt)


# ---- BIO110
m("B01", ["os2"], ["ka_chem"], ["os2"], "atoms bonds ionic covalent hydrogen bond biology")
m("B02", ["os2"], ["ka_chem"], ["os2"], "water properties hydrogen bonding cohesion adhesion pH buffer biology")
m("B03", ["os2"], ["ka_chem"], ["os2"], "carbon functional groups isomers biology")
m("B04a", ["os3"], ["ka_chem"], ["os3"], "carbohydrates lipids biology macromolecules")
m("B04b", ["os3"], ["ka_chem"], ["os3"], "protein structure levels nucleic acids biology")
m("B05a", ["os4"], ["ka_cell"], ["os4"], "endomembrane system nucleus ribosome cell biology")
m("B05b", ["os4"], ["ka_cell"], ["os4"], "mitochondria chloroplast cytoskeleton biology")
m("B06", ["os5"], ["ka_cell"], ["os5"], "membrane transport osmosis tonicity active transport")
m("B07", ["os6"], ["ka_energy"], ["os6"], "enzymes ATP free energy metabolism biology")
m("B08", ["os7"], ["ka_energy"], ["os7"], "cellular respiration glycolysis krebs electron transport")
m("B09", ["os8"], ["ka_energy"], ["os8"], "photosynthesis light reactions calvin cycle")
m("B10", ["os10"], ["ka_cycle"], ["os10"], "cell cycle mitosis phases checkpoints cyclin")
m("B11", ["os12"], ["ka_heredity"], ["os12"], "mendelian genetics punnett square dihybrid cross")
m("B12", ["os13"], ["ka_heredity"], ["os13"], "linked genes recombination sex linked inheritance")
m("B13", ["os14"], ["ka_gene"], ["os14"], "DNA replication enzymes leading lagging strand")
m("B14", ["os15"], ["ka_gene"], ["os15"], "transcription translation RNA processing genetic code")
m("B15", ["os16"], ["ka_gene"], ["os16"], "lac operon trp operon gene regulation")
m("B16", ["os17"], ["ka_gene"], ["os17"], "PCR gel electrophoresis CRISPR biotechnology")
m("BR0", ["os2"], ["ka_chem"], ["os2"])
m("BQ2 BQ3 BQE BS BF", ["os2", "os3", "os4", "os5", "os6", "os7", "os8"], ["ka_chem", "ka_energy"], ["os6"])
m("BT1", ["os10", "os12", "os13", "os14"], ["ka_heredity"], ["os12"])
m("BT2 BM2 BM2E BF2 BF2b", ["os14", "os15", "os16", "os17"], ["ka_gene", "ka_cycle"], ["os15"])
# ---- CMPE371
m("S0a", ["ka_complex"], ["lamar"], ["desmos"], "complex numbers euler formula polar form")
m("S0b", ["lamar"], ["ka_complex"], ["desmos"], "trigonometric identities exponent rules derivative integral review")
m("S1", ["ocw607"], ["ocw603"], ["desmos"], "signals and systems introduction time shift scaling reversal")
m("S2", ["ocw607"], ["ocw603"], ["desmos"], "sinusoids amplitude frequency phase period phasor")
m("S3", ["ocw607"], ["ocw603"], ["desmos"], "unit step impulse even odd periodic signals")
m("S3b", ["ocw607"], ["ocw603"], [], "system properties linearity time invariance causality stability")
m("S4a", ["ocw607"], ["ocw603"], [], "discrete time convolution sum")
m("S4b", ["ocw607"], ["ocw603"], [], "continuous time convolution integral graphical")
m("S4c", ["ocw607"], ["ocw603"], [], "LTI system properties impulse response step response")
m("S5", ["ocw607"], ["ocw603"], [], "differential equations difference equations LTI solving")
m("S6", ["ocw607", "b3b1"], ["ocw603"], ["desmos"], "continuous time Fourier series coefficients")
m("S7", ["ocw607", "b3b1"], ["ocw603"], ["desmos"], "continuous time Fourier transform pairs properties")
m("SP7 SCU SMk SM SR1 SR2 SR3 SR4", ["ocw603"], ["ocw607"], [], "")
# ---- CMPE327
m("A1", ["cs103"], ["jeffe"], [], "sets relations functions proof by induction discrete math")
m("A2", ["cs103"], ["ocw18404"], ["jflap", "autosim"], "DFA design examples deterministic finite automata")
m("A3", ["cs103"], ["ocw18404"], ["jflap", "autosim"], "DFA design practice problems")
m("A4", ["cs103"], ["ocw18404"], ["jflap", "autosim"], "NFA epsilon transitions design")
m("A5", ["cs103"], ["ocw18404"], ["jflap"], "NFA to DFA subset construction")
m("A6", ["cs103"], ["ocw18404"], ["jflap"], "closure properties regular languages product construction")
m("A7", ["cs103"], ["ocw18404"], ["regex101", "jflap"], "regular expression to NFA conversion")
m("A8", ["cs103"], ["ocw18404"], ["jflap"], "DFA minimization table filling algorithm")
m("A9", ["cs103"], ["ocw18404"], [], "Myhill Nerode theorem")
m("A10", ["cs103"], ["ocw18404"], ["regex101"], "Brzozowski derivatives regular expressions equivalence")
m("A11", ["cs103"], ["ocw18404"], ["jflap"], "context free grammars derivation parse tree")
m("A12", ["cs103"], ["ocw18404"], ["jflap"], "ambiguous grammar DFA equivalence checking")
m("A13 AE AQ1 AM2 AF AF2", ["cs103"], ["ocw18404"], ["jflap", "autosim"], "")
# ---- CMPE421
m("I1", ["cs188"], ["aima"], [], "intelligent agents PEAS environment types")
m("I2", ["cs188", "cs50ai"], ["aima"], ["pathfind"], "BFS DFS uniform cost iterative deepening search")
m("I3", ["cs188"], ["aima"], ["pathfind"], "A* search admissible consistent heuristic")
m("I4", ["cs188", "cs50ai"], ["aima"], [], "minimax alpha beta pruning")
m("I5", ["cs188", "cs50ai"], ["aima"], [], "constraint satisfaction backtracking forward checking AC-3")
m("I6", ["aima"], ["cs188"], [], "STRIPS PDDL planning forward backward search")
m("I7", ["cs188", "cs50ai"], ["aima"], [], "propositional logic inference first order logic")
m("I8", ["aima", "cs50ai"], ["cs188"], [], "resolution theorem proving CNF unification")
m("I9", ["cs188", "cs50ai"], ["aima"], [], "probability bayes rule bayesian networks")
m("IM IMR IF IF2", ["cs188"], ["aima", "ocw6034"], ["pathfind"], "")
# ---- CMPE453
m("M1", ["datasheet"], ["avrlibc", "elliot"], [], "ATmega328P architecture memory registers")
m("M2", ["avrlibc"], ["datasheet", "elliot"], ["wokwi"], "AVR C bit manipulation set clear toggle register")
m("M3", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR DDR PORT PIN registers")
m("M4", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR digital input pull-up debounce")
m("M5", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR USART UBRR baud rate")
m("M6", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR SPI I2C TWI protocol timing")
m("M7", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR ADC ADMUX ADCSRA conversion")
m("MM MME MF", ["datasheet"], ["avrlibc"], ["wokwi"], "")
# ---- CMPE499
m("U2 U3a U3b U3c U3d U4 U5 U6 U7 U8 U9", [], ["langtool", "zotero"], [], "")
m("VD1 VD2 VD3 VD4 VD5 VD6", [], ["obs", "resolve"], [], "")

# ---- Aralık / 14. haftaya kadar olan konular
m("A14", ["cs103"], ["ocw18404"], ["jflap"], "Chomsky normal form conversion")
m("A15", ["cs103"], ["ocw18404"], [], "CYK algorithm example")
m("A16", ["cs103"], ["ocw18404"], [], "pumping lemma regular languages proof")
m("A17", ["cs103"], ["ocw18404"], ["jflap"], "pushdown automata design examples")
m("A18", ["ocw18404"], ["cs103"], [], "Ogden's lemma context free languages")
m("A19", ["cs103"], ["ocw18404"], ["jflap"], "Turing machine design examples")
m("A20", ["cs103"], ["ocw18404"], [], "decidable languages halting problem undecidability")
m("AQ2", ["cs103"], ["ocw18404"], ["jflap"])
m("S9", ["ocw607"], ["ocw603"], ["desmos"], "discrete-time Fourier series DTFS")
m("S10", ["ocw607"], ["ocw603"], ["desmos"], "discrete-time Fourier transform DTFT")
m("SQ1", ["ocw603"], ["ocw607"], [])
m("S11", ["ocw607"], ["ocw603"], ["desmos"], "ideal filters low pass high pass frequency response")
m("S12", ["ocw607"], ["ocw603"], ["desmos"], "sampling theorem aliasing Nyquist")
m("S13", ["ocw607"], ["ocw603"], [], "Z-transform region of convergence")
m("I10", ["cs50n4"], ["cs188", "aima"], [], "machine learning overfitting bias variance")
m("I11", ["cs50n4"], ["cs188"], [], "k nearest neighbors decision tree logistic regression")
m("I12", ["cs50n5", "cs231n"], ["cs188"], ["tfplay"], "neural networks backpropagation explained")
m("I13", ["cs50n6"], ["cs188"], [], "transformers attention LLM explained")
m("I14", ["cs50n4"], ["aima", "cs188"], [], "reinforcement learning Q-learning explained")
m("I15", ["aima"], ["cs188"], [], "AI ethics explainability bias fairness")
m("M8", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR interrupts ISR external interrupt")
m("M9", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR timer counter registers prescaler")
m("M10", ["datasheet"], ["avrlibc", "elliot"], ["wokwi"], "AVR PWM fast PWM phase correct OCR")
m("M11", [], ["elliot"], [], "STM32 Discovery board getting started")
m("M12", [], ["elliot"], [], "STM32 GPIO register LED blink")
m("M13", [], ["elliot"], [], "STM32 timer PWM ARR PSC CCR")
m("B17", ["os18"], ["ka_nat"], ["os18"], "natural selection Darwin evidence for evolution")
m("B18", ["os19"], ["ka_nat"], ["os19"], "Hardy Weinberg genetic drift gene flow")
for _id, _x in {"I2": ["cs50n0"], "I4": ["cs50n0"], "I5": ["cs50n3"], "I7": ["cs50n1"], "I8": ["cs50n1"], "I9": ["cs50n2"]}.items():
    M[_id][1].extend(_x)
_HUB = {"BIO": (["os2", "os8", "os14"], ["ka_chem", "ka_gene"]), "SIG": (["ocw603"], ["ocw607", "desmos"]), "AUT": (["cs103"], ["ocw18404", "jflap"]),
        "AI": (["cs188"], ["aima", "cs50n0"]), "MCU": (["datasheet"], ["avrlibc", "elliot"])}
for _s, (_a, _b) in _HUB.items():
    m(" ".join(f"{p}{_s}" for p in ("K1", "F1", "F2", "F3", "F4", "F5", "F6", "F7")), _a, _b, [])

COURSE_HOME = {  # Kaynaklar sekmesi: ders başına katalog
    "BIO110": ["os2", "os3", "os4", "os5", "os6", "os7", "os8", "os10", "os12", "os13", "os14", "os15", "os16", "os17", "ka_chem", "ka_cell", "ka_energy", "ka_cycle", "ka_heredity", "ka_gene", "os18", "os19", "ka_nat", "amoeba"],
    "CMPE371": ["ocw607", "ocw603", "b3b1", "ka_complex", "lamar", "desmos"],
    "CMPE327": ["cs103", "ocw18404", "jeffe", "jflap", "autosim", "regex101"],
    "CMPE421": ["cs188", "aima", "cs50ai", "cs50n0", "cs50n1", "cs50n2", "cs50n3", "cs50n4", "cs50n5", "cs50n6", "ocw6034", "pathfind", "cs231n", "tfplay"],
    "CMPE453": ["datasheet", "avrlibc", "elliot", "wokwi", "tinkercad"],
    "CMPE499": ["langtool", "zotero", "obs", "resolve"],
    "ARAÇLAR": ["anki", "pomo"],
}

HOW = {
    "L_BIO": ["10 dk · Kaynağın başlıklarına ve şekillerine göz at; alt başlıkları kağıda yaz.",
              "35–45 dk · Oku veya izle. Her alt başlıktan sonra ekranı kapat, 3 cümleyle bellekten anlat.",
              "20–30 dk · {practice}",
              "10 dk · Yanlış ve eksikleri Mistake Log'a yaz, 5 flashcard hazırla (Anki)."],
    "L_TECH": ["10 dk · Slayt veya kaynakta konuyu hızlıca gez; tanım ve formül listesi çıkar.",
               "30–40 dk · Çözümlü bir örneği izle. Sonra kapat ve aynısını sıfırdan çöz.",
               "30–40 dk · {practice} (çözüme bakmadan; takılırsan 10 dk dene, sonra bak).",
               "10 dk · Hataları sebebiyle Mistake Log'a yaz."],
    "P": ["Telefonu uzağa koy, süre tut.", "Kitap ve slayt kapalı çöz.", "Bitince her yanlışı sebebiyle yaz (bilgi, işlem, dikkat).",
          "En çok hata yaptığın konuya 15 dk geri dön."],
    "R": ["Telefonu uzağa koy, süre tut.", "Kitap ve slayt kapalı çöz.", "Bitince her yanlışı sebebiyle yaz.", "En zayıf konuya 15 dk dön."],
    "W": ["5 dk · Görev tanımını ve teslim koşulunu oku.", "Tek oturumda işi ilerlet, parçalama.", "Bitirince dosyayı ikinci bir yere yedekle.",
          "Eksik kalanı ertesi güne tek satırla not et."],
    "V": ["Hoca duyurularına, ders grubuna veya ÖBS'ye bak.", "Cevabı Sınavlar sekmesindeki not alanına yaz.", "Tarih veya kapsam değiştiyse planı güncellettir."],
    "T": ["Notları ve kartları kapat.", "Konu başına 8 dk: 3 cümleyle anlat, 2 soru çöz.", "Takıldığın konuyu işaretle, gün sonunda 10 dk geri dön."],
}
DONE = {
    "L": "Kaynağı kapatıp konuyu 3 cümleyle anlatabiliyorsun ve uygulama kısmını çözüme bakmadan bitirdin.",
    "P": "Süreli bitirdin ve her yanlışın sebebi yazıldı.",
    "R": "Süreli bitirdin ve her yanlışın sebebi yazıldı.",
    "W": "Çıktı dosyası kaydedildi ve yedeklendi.",
    "V": "Cevabı not ettin; değişiklik varsa plana bildirdin.",
    "T": "Her konuyu bellekten anlatabildin.",
}


# TEDU okul bağlantıları (29 Ekim 2026'da açılış testinden geçti; /my/ giriş sayfasına yönlenir)
LMS = [
    ["TEDU LMS ana sayfa", "https://lms.tedu.edu.tr/", "ders slaytları, ödev teslimi, duyurular"],
    ["LMS giriş", "https://lms.tedu.edu.tr/login/index.php", "TEDUPass ile giriş yap"],
    ["Derslerim (giriş sonrası)", "https://lms.tedu.edu.tr/my/", "kayıtlı olduğun derslerin listesi"],
    ["Ders kataloğu (LMS)", "https://lms.tedu.edu.tr/course/index.php", "bölüme göre ders ara"],
    ["MyTEDU", "https://my.tedu.edu.tr/", "not, ders programı, öğrenci işleri"],
    ["TED Üniversitesi", "https://www.tedu.edu.tr/", "akademik takvim ve duyurular"],
]


# ---- V5: Assignment-1 (LMS) ve CMPE327 slayt pratiği
LINKS["lms_a1"] = ("CMPE421 Assignment-1 PDF (TEDU LMS; giriş gerekir)", "https://lms.tedu.edu.tr/mod/resource/view.php?id=16460", "TEDUPass ile giriş; PDF'i bu sitede okuyamadım")
m("AS1 AS2 AS3 AS4 AS5 AS6", ["lms_a1"], [], [], "")
m("AP1 AP2 AP3 AP4", ["cs103"], ["ocw18404", "jflap"], [], "theory of computation DFA NFA regular expression solved problems")

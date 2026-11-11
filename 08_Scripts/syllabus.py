# -*- coding: utf-8 -*-
"""Syllabus görsellerinden çıkarılan 14 haftalık konu haritası + her konunun planda hangi bloklarla çalışıldığı.
Hafta tarihleri: W1 = 28 Eylül 2026 (Pzt). Boş hafta = syllabus'ta konu listelenmemiş."""
from datetime import date, timedelta

W0 = date(2026, 9, 28)

# (hafta, syllabus konusu, not, [plandaki bloklar])
SYL = {
    "BIO110": [
        (1, "First Meeting (tanışma, ders düzeni)", "", []),
        (2, "The Chemical Context of Life · Water and Life · Carbon and the Molecular Diversity of Life", "8/9 Eki", ["B01", "B02", "B03"]),
        (3, "Structure and Function of Large Biological Molecules · A Tour of the Cell · Membrane Structure and Function", "15/16 Eki", ["B04a", "B04b", "B05a", "B05b", "B06"]),
        (4, "An Introduction to Metabolism · Cellular Respiration · Photosynthesis", "22/23 Eki", ["B07", "B08", "B09"]),
        (5, "Konu listelenmemiş (gözden geçirme haftası)", "", ["BR0", "BQ2"]),
        (6, "First Midterm Review and Exam", "Midterm 1: 3 Kasım (senin tarihin; syllabus 5/6 Kas)", ["BQ3", "BQE", "BS", "BF", "BX", "BPX"]),
        (7, "The Cell Cycle and Cellular Reproduction · Mendel and the Gene Idea · The Chromosomal Basis of Inheritance · The Molecular Basis of Inheritance", "12/13 Kas", ["B10", "B11", "B12", "B13"]),
        (8, "Gene Expression: From Gene to Protein · Regulation of Gene Expression · DNA Tools and Biotechnology", "19/20 Kas", ["B14", "B15", "B16", "BT1", "BT2"]),
        (9, "Second Midterm Review and Exam", "Midterm 2: 26/27 Kas (gün teyit bekliyor)", ["BM2", "BM2E", "BF2", "BF2b"]),
        (10, "Descent with Modification: A Darwinian View of Life · The Evolution of Populations", "3/4 Ara", ["B17", "B18"]),
        (11, "Project Presentations (bireysel, 15–20 slayt)", "10/11 Ara – 31 Ara arası; gün teyit bekliyor", ["BP1", "BP2", "BP3", "BP4", "BP5", "BP6"]),
        (12, "Project Presentations", "", []),
        (13, "Project Presentations", "", []),
        (14, "Project Presentations", "", []),
    ],
    "CMPE371": [
        (1, "Introduction to Signals and Systems", "", ["S0a", "S0b", "S1"]),
        (2, "Sinusoids", "", ["S2"]),
        (3, "Special Signals, System Properties", "", ["S3", "S3b"]),
        (4, "Linear Time-Invariant (LTI) Systems", "", ["S4a", "S4b"]),
        (5, "Linear Time-Invariant (LTI) Systems", "", ["S4c"]),
        (6, "Differential and Difference Equations", "HW 1", ["S5", "SH1a", "SH1b"]),
        (7, "Continuous-Time Fourier Series (CTFS)", "", ["S6"]),
        (8, "Continuous-Time Fourier Transform (CTFT)", "", ["S7", "SP7", "SCU"]),
        (9, "Midterm Exam", "Midterm: 30 Kas 18:00–20:00 (hoca duyurusu; syllabus W9 23–27 Kas diyor)", ["SMk", "SM", "SR1", "SR2", "SR3", "SR4"]),
        (10, "Discrete-Time Fourier Series (DTFS)", "", ["S9"]),
        (11, "Discrete-Time Fourier Transform (DTFT)", "Quiz 1 (7–11 Ara, teyit bekliyor)", ["S10", "SQ1"]),
        (12, "Filtering", "", ["S11"]),
        (13, "Sampling", "", ["S12"]),
        (14, "Z-Transform", "", ["S13"]),
    ],
    "CMPE327": [
        (1, "History of Computing · Central Concepts of Automata Theory", "", ["A1"]),
        (2, "Mathematical Preliminaries · Deterministic Finite Automata (DFA)", "", ["A1", "A2", "A3"]),
        (3, "Non-Deterministic Finite Automata (NFA) · Closure Properties", "", ["A4", "A6"]),
        (4, "Equivalence of DFA and NFA", "", ["A5"]),
        (5, "Regular Languages · Pattern Matching · Regular Expressions · DFA State Minimization", "Quiz-1 (syllabus; durumu doğrula)", ["A7", "A8"]),
        (6, "DFA State Minimization · Myhill–Nerode Relations · Derivatives", "", ["A8", "A9", "A10"]),
        (7, "Myhill–Nerode Relations · Derivatives · Equivalence of Regular Expressions", "", ["A9", "A10"]),
        (8, "DFA Equivalence Checking · Context Free Grammars · Ambiguity", "Quiz: 15 Kas 13:00–14:00 · Midterm: 29 Kas 13:00–15:00 (W1–W8, Week 08 dahil; hoca duyurusu)", ["A11", "A12", "A13", "AE", "AQ1", "AM2", "AF", "AF2", "AP1", "AP2", "AP3", "AP4"]),
        (9, "Chomsky Normal Form · CYK Algorithm · Pumping Lemma · Non-regularity", "", ["A14", "A15"]),
        (10, "Chomsky Normal Form · CYK Algorithm · Pumping Lemma · Non-regularity", "", ["A16"]),
        (11, "Push Down Automata · Ogden's Lemma", "", ["A17"]),
        (12, "Push Down Automata · Ogden's Lemma", "Quiz-2 (14–18 Ara, teyit bekliyor)", ["A18", "AQ2"]),
        (13, "Turing Machines · Decision Problems", "", ["A19"]),
        (14, "Turing Machines · Decision Problems", "", ["A20"]),
    ],
    "CMPE421": [
        (1, "Introduction to Artificial Intelligence", "", ["I1"]),
        (2, "Intelligent Agents and Problem Solving", "", ["I1", "I2"]),
        (3, "Uninformed Search Algorithms", "", ["I2"]),
        (4, "Informed Search Algorithms", "", ["I3"]),
        (5, "Game Playing", "", ["I4"]),
        (6, "Constraint Satisfaction Problems and Adversarial Search", "", ["I5"]),
        (7, "Planning", "", ["I6"]),
        (8, "Knowledge Representation and Reasoning · Theorem Proving", "", ["I7", "I8"]),
        (9, "Uncertainty", "", ["I9", "IM", "IMR", "IF", "IF2", "AS1", "AS2", "AS3", "AS4", "AS5", "AS6"]),
        (10, "Machine Learning Fundamentals · Classification and Regression Techniques", "Midterm: 20 Kas 18:00–20:00 · Assignment-1: 26 Kas 23:59 (LMS)", ["I10", "I11"]),
        (11, "Neural Networks and Deep Learning", "", ["I12"]),
        (12, "Natural Language Processing and LLMs", "", ["I13"]),
        (13, "Reinforcement Learning", "", ["I14"]),
        (14, "Ethics, Explainability and Responsible AI · Review", "", ["I15"]),
    ],
    "CMPE453": [
        (1, "Course overview · Architecture of AVR microcontroller (ATmega328P)", "Elliot Ch.1", ["M1"]),
        (2, "Programming AVR microcontroller", "Elliot Ch.2–4", ["M2"]),
        (3, "Programming AVR microcontroller – I/O", "Lab 1", ["M3"]),
        (4, "Programming AVR – digital input", "Lab 2 · Elliot Ch.5", ["M4"]),
        (5, "Serial Communication: USART", "Elliot Ch.5", ["M5"]),
        (6, "Serial Communication: SPI, I2C", "Lab 3 · Elliot Ch.7", ["M6"]),
        (7, "Analog-to-Digital Conversion (ADC)", "Midterm: 12 Kas 18:00–20:00 (%32; Lab %18; Final %50) · Elliot Ch.7", ["M7", "MM", "MME", "MF"]),
        (8, "Interrupts", "Elliot Ch.8", ["M8"]),
        (9, "Timers/counters", "Lab 4 · Elliot Ch.9", ["M9"]),
        (10, "PWM", "Elliot Ch.10", ["M10"]),
        (11, "Basics of ARM Cortex (STM32 Discovery Board Hardware)", "STM32 Manual", ["M11"]),
        (12, "GPIO Configuration and LED Blinking", "Lab 5", ["M12"]),
        (13, "PWM for ARM Cortex", "Lab 6", ["M13"]),
        (14, "Konu listelenmemiş (final hazırlığı)", "", []),
    ],
    "CMPE499": [
        (1, "—", "", []),
        (2, "Evaluation Form submission", "Son: 7 Eki 2026 (teslim edildi)", []),
        (3, "—", "", []),
        (4, "—", "", []),
        (5, "—", "", ["U2"]),
        (6, "—", "", ["U3a", "U3b"]),
        (7, "—", "", ["U3c", "U3d", "U4", "U5", "U6"]),
        (8, "Summer Training Report (STR) Submission", "Son: 22 Kas 2026 (plan: 20 Kas'ta yükle)", ["U7", "U8", "U9"]),
        (9, "Summer Training Video Submission", "Son: 29 Kas 2026 (plan: 25 Kas'ta yükle)", ["VD1", "VD2", "VD3", "VD4", "VD5", "VD6", "UP1"]),
        (10, "—", "", []),
        (11, "—", "", []),
        (12, "—", "", []),
        (13, "—", "", []),
        (14, "—", "", []),
    ],
}


def week_range(w):
    s = W0 + timedelta(days=7 * (w - 1))
    return s, s + timedelta(days=4)  # Pzt–Cum


def week_of(d):
    return max(1, min(14, (d - W0).days // 7 + 1))


def as_json():
    out = {}
    for c, rows in SYL.items():
        out[c] = [[w, t, n, b] for (w, t, n, b) in rows]
    return out


_MON = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
_BLANK = ("—", "Konu listelenmemiş")


def _short(d):
    return f"{d.day} {_MON[d.month - 1]}"


def rows(course):
    """(hafta, 'D Ay – D Ay', konu, not) satırları; boş haftalar da dahil."""
    out = []
    for w, t, n, _b in SYL[course]:
        a, b = week_range(w)
        out.append((w, f"{_short(a)} – {_short(b)}", t, n))
    return out


def md_table(course):
    L = ["| Hf | Tarih | Syllabus konusu | Not |", "|---|---|---|---|"]
    for w, rng, t, n in rows(course):
        L.append(f"| {w} | {rng} | {t} | {n} |")
    return "\n".join(L)


def html_table(course, esc):
    h = ["<table style='font-size:7.5pt;margin:0 0 2mm'><tr><th style='width:8mm'>Hf</th><th style='width:24mm'>Tarih</th><th>Syllabus konusu</th><th style='width:42mm'>Not</th></tr>"]
    for w, rng, t, n in rows(course):
        if t.startswith(_BLANK) and not n:
            continue
        h.append(f"<tr><td>{w}</td><td>{esc(rng)}</td><td>{esc(t)}</td><td>{esc(n)}</td></tr>")
    h.append("</table>")
    return "".join(h)


def html_grid(esc, courses=("BIO110", "CMPE371", "CMPE327", "CMPE421", "CMPE453")):
    """Tek sayfalık özet: satır = hafta, sütun = ders (konunun ilk parçası)."""
    def short(t):
        if t.startswith(_BLANK):
            return "—"
        return t.split(" · ")[0][:44]
    h = ["<table style='font-size:7pt;width:100%'><tr><th style='width:7mm'>Hf</th><th style='width:20mm'>Tarih</th>" + "".join(f"<th>{c}</th>" for c in courses) + "</tr>"]
    for w in range(1, 15):
        a, b = week_range(w)
        h.append(f"<tr><td>{w}</td><td>{esc(_short(a))}–{esc(_short(b))}</td>" + "".join(f"<td>{esc(short(SYL[c][w - 1][1]))}</td>" for c in courses) + "</tr>")
    h.append("</table>")
    return "".join(h)

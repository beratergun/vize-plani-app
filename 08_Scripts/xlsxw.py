# -*- coding: utf-8 -*-
"""Bağımlılıksız minimal .xlsx yazıcı (zipfile + XML). Formül, doğrulama listesi, koşullu biçim, dondurma, filtre destekler."""
import zipfile
from datetime import date
from xml.sax.saxutils import escape

EPOCH = date(1899, 12, 30)


def col_letter(i):  # 1-based
    s = ""
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def serial(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return (d - EPOCH).days


class Styles:
    FONTS = [("Calibri", 10, 0, "000000", 0), ("Calibri", 10, 1, "000000", 0), ("Calibri", 10, 1, "FFFFFF", 0),
             ("Calibri", 16, 1, "111827", 0), ("Calibri", 9, 0, "6B7280", 1), ("Calibri", 12, 1, "111827", 0)]
    FILLS = [None, "gray125", "1F2937", "F3F4F6", "DCFCE7", "FEF3C7", "FEE2E2", "DBEAFE", "FFFBEB"]
    NUMFMT = {"date": 164, "pct": 9, "int": 1, "text": 0, "dec": 2, "general": 0}

    def __init__(self):
        self.xfs = [(0, 0, 0, 0, 0, None, None)]
        self.idx = {self.xfs[0]: 0}

    def get(self, font=0, fill=0, border=0, fmt="general", wrap=0, h=None, v=None):
        key = (font, fill, border, self.NUMFMT[fmt], wrap, h, v)
        if key not in self.idx:
            self.idx[key] = len(self.xfs)
            self.xfs.append(key)
        return self.idx[key]

    def xml(self):
        f = "".join(f'<font>{"<b/>" if b else ""}{"<i/>" if it else ""}<sz val="{sz}"/><color rgb="FF{c}"/><name val="{n}"/></font>'
                    for n, sz, b, c, it in self.FONTS)
        fl = ""
        for x in self.FILLS:
            if x is None:
                fl += '<fill><patternFill patternType="none"/></fill>'
            elif x == "gray125":
                fl += '<fill><patternFill patternType="gray125"/></fill>'
            else:
                fl += f'<fill><patternFill patternType="solid"><fgColor rgb="FF{x}"/><bgColor indexed="64"/></patternFill></fill>'
        side = '<{0} style="thin"><color rgb="FFD1D5DB"/></{0}>'
        borders = '<border><left/><right/><top/><bottom/><diagonal/></border><border>' + "".join(side.format(s) for s in ("left", "right", "top", "bottom")) + '<diagonal/></border>'
        xfs = ""
        for (fo, fi, bo, nf, wr, h, v) in self.xfs:
            al = ""
            if wr or h or v:
                al = "<alignment" + (f' horizontal="{h}"' if h else "") + (f' vertical="{v}"' if v else "") + (' wrapText="1"' if wr else "") + "/>"
            xfs += (f'<xf numFmtId="{nf}" fontId="{fo}" fillId="{fi}" borderId="{bo}" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1"'
                    + (' applyAlignment="1">' + al + "</xf>" if al else "/>"))
        dxfs = ("".join(f'<dxf><fill><patternFill><bgColor rgb="FF{c}"/></patternFill></fill></dxf>' for c in ("DCFCE7", "FEF3C7", "FEE2E2", "E5E7EB"))
                + '<dxf><font><b/><color rgb="FF991B1B"/></font><fill><patternFill><bgColor rgb="FFFEE2E2"/></patternFill></fill></dxf>')
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<numFmts count="1"><numFmt numFmtId="164" formatCode="dd\\.mm\\.yyyy"/></numFmts>'
                f'<fonts count="{len(self.FONTS)}">{f}</fonts><fills count="{len(self.FILLS)}">{fl}</fills><borders count="2">{borders}</borders>'
                '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                f'<cellXfs count="{len(self.xfs)}">{xfs}</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
                f'<dxfs count="5">{dxfs}</dxfs></styleSheet>')


class Sheet:
    def __init__(self, wb, name, tab=None):
        self.wb, self.name, self.tab = wb, name, tab
        self.cells = {}   # (r,c) -> (kind, value, style, cached)
        self.widths, self.freeze, self.filter = {}, None, None
        self.merges, self.dv, self.cf = [], [], []
        self.heights = {}

    def set(self, r, c, value=None, style=0, f=None, cached=None):
        self.cells[(r, c)] = (f, value, style, cached)

    def row(self, r, values, style=0, c0=1):
        for i, v in enumerate(values):
            st = style[i] if isinstance(style, (list, tuple)) else style
            self.set(r, c0 + i, v, st)

    def xml(self):
        rows = {}
        for (r, c), v in self.cells.items():
            rows.setdefault(r, {})[c] = v
        maxr = max(rows) if rows else 1
        maxc = max(c for (_, c) in self.cells) if self.cells else 1
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
        if self.tab:
            out.append(f'<sheetPr><tabColor rgb="FF{self.tab}"/></sheetPr>')
        out.append(f'<dimension ref="A1:{col_letter(maxc)}{maxr}"/>')
        pane = ""
        if self.freeze:
            fr, fc = self.freeze
            tl = f"{col_letter(fc + 1)}{fr + 1}"
            attrs = (f' xSplit="{fc}"' if fc else "") + (f' ySplit="{fr}"' if fr else "")
            active = "bottomRight" if fr and fc else "bottomLeft" if fr else "topRight"
            pane = f'<pane{attrs} topLeftCell="{tl}" activePane="{active}" state="frozen"/>'
        out.append(f'<sheetViews><sheetView workbookViewId="0" showGridLines="0">{pane}</sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/>')
        if self.widths:
            out.append("<cols>" + "".join(f'<col min="{c}" max="{c}" width="{w}" customWidth="1"/>' for c, w in sorted(self.widths.items())) + "</cols>")
        out.append("<sheetData>")
        for r in sorted(rows):
            ht = f' ht="{self.heights[r]}" customHeight="1"' if r in self.heights else ""
            out.append(f'<row r="{r}"{ht}>')
            for c in sorted(rows[r]):
                f, v, st, cached = rows[r][c]
                ref = f"{col_letter(c)}{r}"
                if f is not None:
                    if isinstance(cached, str):
                        out.append(f'<c r="{ref}" s="{st}" t="str"><f>{escape(f)}</f><v>{escape(cached)}</v></c>')
                    elif cached is None:
                        out.append(f'<c r="{ref}" s="{st}"><f>{escape(f)}</f></c>')
                    else:
                        out.append(f'<c r="{ref}" s="{st}"><f>{escape(f)}</f><v>{cached}</v></c>')
                elif v is None or v == "":
                    out.append(f'<c r="{ref}" s="{st}"/>')
                elif isinstance(v, bool):
                    out.append(f'<c r="{ref}" s="{st}" t="b"><v>{int(v)}</v></c>')
                elif isinstance(v, (int, float)):
                    out.append(f'<c r="{ref}" s="{st}"><v>{v}</v></c>')
                else:
                    out.append(f'<c r="{ref}" s="{st}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>')
            out.append("</row>")
        out.append("</sheetData>")
        if self.filter:
            out.append(f'<autoFilter ref="{self.filter}"/>')
        if self.merges:
            out.append(f'<mergeCells count="{len(self.merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in self.merges) + "</mergeCells>")
        pr = 1
        for sq, kind, arg, dxf in self.cf:
            if kind == "expr":
                out.append(f'<conditionalFormatting sqref="{sq}"><cfRule type="expression" dxfId="{dxf}" priority="{pr}"><formula>{escape(arg)}</formula></cfRule></conditionalFormatting>')
            elif kind == "bar":
                out.append(f'<conditionalFormatting sqref="{sq}"><cfRule type="dataBar" priority="{pr}"><dataBar><cfvo type="num" val="0"/><cfvo type="num" val="1"/><color rgb="FF22C55E"/></dataBar></cfRule></conditionalFormatting>')
            pr += 1
        if self.dv:
            out.append(f'<dataValidations count="{len(self.dv)}">' + "".join(
                f'<dataValidation type="list" allowBlank="1" showErrorMessage="1" sqref="{sq}"><formula1>{escape(lst)}</formula1></dataValidation>' for sq, lst in self.dv) + "</dataValidations>")
        out.append('<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/><pageSetup paperSize="9" orientation="landscape"/>')
        out.append("</worksheet>")
        return "".join(out)


class Workbook:
    def __init__(self):
        self.sheets, self.styles = [], Styles()

    def add(self, name, tab=None):
        s = Sheet(self, name, tab)
        self.sheets.append(s)
        return s

    def save(self, path):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            n = len(self.sheets)
            z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                       '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                       '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                       '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                       + "".join(f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(n))
                       + "</Types>")
            z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            z.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                       '<bookViews><workbookView activeTab="0"/></bookViews><sheets>'
                       + "".join(f'<sheet name="{escape(s.name)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, s in enumerate(self.sheets))
                       + '</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
            z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       + "".join(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i + 1}.xml"/>' for i in range(n))
                       + f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
            for i, s in enumerate(self.sheets):
                z.writestr(f"xl/worksheets/sheet{i + 1}.xml", s.xml())
            z.writestr("xl/styles.xml", self.styles.xml())

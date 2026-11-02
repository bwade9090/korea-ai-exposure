"""The brief as a Word document: ``report/brief.docx`` from ``brief_text`` and the figures, with
every reported number resolved from ``outputs/facts.json`` (run ``make figures`` and ``make facts``
first). The layout follows a central-bank policy note: a cover with the summary, numbered
paragraphs with a lead sentence, exhibits with a headline, notes and sources, and footnotes.

Exhibits follow the paragraph given in ``brief_text.PLACEMENT``, so that text fills a page before
an exhibit moves to the next one. ``report/brief.pdf`` is exported from Word. Rebuilding replaces
``report/brief.docx``, including any edits made in Word.
"""

import json
import os
import re

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.opc.part import Part
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor, Twips

from korea_ai_exposure import brief_text, paths

FACTS_FILE = paths.OUTPUTS / "facts.json"
FIGURES = paths.OUTPUTS / "figures"
BRIEF = paths.ROOT / "report" / "brief.docx"

NAVY, GREY, DARK, LIGHT, RULE = "1F3A5F", "5A6470", "222222", "EAF0F6", "A9B4C2"
SERIF, SANS, EAST_ASIAN = "Georgia", "Arial", "Malgun Gothic"
TEXT_WIDTH_CM = 16.8
MINUS = chr(0x2212)
ORDINALS = [
    "zeroth",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
    "sixteenth",
    "seventeenth",
    "eighteenth",
    "nineteenth",
    "twentieth",
]
PLACEHOLDER = re.compile(r"\{([A-Za-z0-9_.\-]+)(?:!([a-z]+))?(?::([^}]+))?\}")
FOOTNOTE = re.compile(r"\[\^(\w+)\]")

_facts: dict[str, dict] = {}
_footnotes: dict[str, int] = {}


def resolve(text: str, facts: dict[str, dict] | None = None) -> str:
    """``text`` with every placeholder replaced from ``facts`` (the loaded facts by default);
    an unknown fact id is a KeyError. Negative numbers take a minus sign."""
    facts = _facts if facts is None else facts

    def substitute(match: re.Match) -> str:
        fact_id, conversion, spec = match.groups()
        value, display = facts[fact_id]["value"], facts[fact_id]["display"]
        if conversion == "ordw":
            out = ORDINALS[int(value)]
        elif conversion == "total":
            out = re.search(r"of (\d+)", display).group(1)
        elif conversion == "num":
            out = re.sub(r" \(N = \d+\)$", "", display)
        elif conversion == "abs":
            out = format(abs(value), spec or "")
        elif conversion is None:
            out = format(value, spec) if spec else display
        else:
            raise ValueError(f"unknown conversion {conversion!r}")
        return MINUS + out[1:] if re.match(r"-\d", out) else out

    return PLACEHOLDER.sub(substitute, text)


def texts() -> list[str]:
    """Every string of the brief that may hold placeholders."""
    strings = [lead + " " + body for lead, body in brief_text.SUMMARY]
    strings += [" ".join(item[1:]) for item in brief_text.BODY]
    strings += list(brief_text.FOOTNOTES.values())
    for spec in brief_text.FIGURES.values():
        strings += spec["notes"]
    strings += [cell for row in brief_text.TABLE_1["rows"] for cell in row]
    strings += [text for _, text in brief_text.ANNEX]
    return strings


# --- formatting helpers: Word's schema fixes the order of properties ----------------------------

PPR_ORDER = [
    "pStyle",
    "keepNext",
    "keepLines",
    "pageBreakBefore",
    "framePr",
    "widowControl",
    "numPr",
    "suppressLineNumbers",
    "pBdr",
    "shd",
    "tabs",
    "suppressAutoHyphens",
    "kinsoku",
    "wordWrap",
    "overflowPunct",
    "topLinePunct",
    "autoSpaceDE",
    "autoSpaceDN",
    "bidi",
    "adjustRightInd",
    "snapToGrid",
    "spacing",
    "ind",
    "contextualSpacing",
    "mirrorIndents",
    "suppressOverlap",
    "jc",
    "textDirection",
    "textAlignment",
    "textboxTightWrap",
    "outlineLvl",
    "divId",
    "cnfStyle",
    "rPr",
    "sectPr",
    "pPrChange",
]
TCPR_ORDER = [
    "cnfStyle",
    "tcW",
    "gridSpan",
    "hMerge",
    "vMerge",
    "tcBorders",
    "shd",
    "noWrap",
    "tcMar",
    "textDirection",
    "tcFitText",
    "vAlign",
    "hideMark",
]
TBLPR_ORDER = [
    "tblStyle",
    "tblpPr",
    "tblOverlap",
    "bidiVisual",
    "tblStyleRowBandSize",
    "tblStyleColBandSize",
    "tblW",
    "jc",
    "tblCellSpacing",
    "tblInd",
    "tblBorders",
    "shd",
    "tblLayout",
    "tblCellMar",
    "tblLook",
    "tblCaption",
    "tblDescription",
]


def _insert_ordered(parent, child, order: list[str]) -> None:
    """Insert ``child`` before the first existing sibling that the schema puts after it."""
    later = {qn(f"w:{tag}") for tag in order[order.index(child.tag.split("}")[1]) + 1 :]}
    for existing in parent:
        if existing.tag in later:
            existing.addprevious(child)
            return
    parent.append(child)


def _set_fonts(element, font: str) -> None:
    """Explicit fonts on a style or run, replacing the theme fonts of the default template."""
    properties = element.get_or_add_rPr()
    fonts = properties.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        properties.insert(0, fonts)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(attr), None)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        fonts.set(qn(attr), font)
    fonts.set(qn("w:eastAsia"), EAST_ASIAN)


def _style_font(style, font, size=None, color=None, bold=None, italic=None) -> None:
    _set_fonts(style.element, font)
    if size is not None:
        style.font.size = Pt(size)
    if color is not None:
        style.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic


def _run(paragraph, text, font=SERIF, size=None, color=None, bold=None, italic=None):
    run = paragraph.add_run(text)
    _set_fonts(run._element, font)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    return run


def _border(paragraph, side: str, size: int, color: str, space: int = 1) -> None:
    properties = paragraph._p.get_or_add_pPr()
    borders = properties.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        _insert_ordered(properties, borders, PPR_ORDER)
    edge = OxmlElement(f"w:{side}")
    for attr, value in (("val", "single"), ("sz", size), ("space", space), ("color", color)):
        edge.set(qn(f"w:{attr}"), str(value))
    borders.append(edge)


def _shading(fill: str):
    shading = OxmlElement("w:shd")
    for attr, value in (("val", "clear"), ("color", "auto"), ("fill", fill)):
        shading.set(qn(f"w:{attr}"), value)
    return shading


def _shade_cell(cell, fill: str) -> None:
    _insert_ordered(cell._tc.get_or_add_tcPr(), _shading(fill), TCPR_ORDER)


def _cell_margins(cell, top=0, bottom=0, left=0, right=0) -> None:
    margins = OxmlElement("w:tcMar")
    for side, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        edge = OxmlElement(f"w:{side}")
        edge.set(qn("w:w"), str(value))
        edge.set(qn("w:type"), "dxa")
        margins.append(edge)
    _insert_ordered(cell._tc.get_or_add_tcPr(), margins, TCPR_ORDER)


def _table_borders(table, spec: dict[str, tuple[int, str]]) -> None:
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge = OxmlElement(f"w:{side}")
        if side in spec:
            size, color = spec[side]
            for attr, value in (("val", "single"), ("sz", size), ("color", color)):
                edge.set(qn(f"w:{attr}"), str(value))
        else:
            edge.set(qn("w:val"), "nil")
        borders.append(edge)
    _insert_ordered(table._tbl.tblPr, borders, TBLPR_ORDER)


def _spacing(paragraph, before=None, after=None, line=None, keep_next=None) -> None:
    layout = paragraph.paragraph_format
    if before is not None:
        layout.space_before = Pt(before)
    if after is not None:
        layout.space_after = Pt(after)
    if line is not None:
        layout.line_spacing = line
    if keep_next is not None:
        layout.keep_with_next = keep_next


def _page_number(paragraph) -> None:
    field = parse_xml(
        f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"><w:r><w:rPr><w:rFonts w:ascii="{SANS}" '
        f'w:hAnsi="{SANS}" w:cs="{SANS}"/><w:color w:val="{GREY}"/><w:sz w:val="16"/></w:rPr>'
        "<w:t>1</w:t></w:r></w:fldSimple>"
    )
    paragraph._p.append(field)


# --- footnotes and paragraph numbering, which python-docx does not provide ---------------------

NUM_ID = 90


def _footnote_reference(paragraph, key: str) -> None:
    _footnotes.setdefault(key, len(_footnotes) + 1)
    run = paragraph.add_run()
    style = OxmlElement("w:rStyle")
    style.set(qn("w:val"), "FootnoteReference")
    run._element.get_or_add_rPr().append(style)
    reference = OxmlElement("w:footnoteReference")
    reference.set(qn("w:id"), str(_footnotes[key]))
    run._element.append(reference)


def _footnotes_part(document) -> None:
    def escape(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    notes = "".join(
        f'<w:footnote w:id="{number}"><w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>'
        '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
        f'<w:r><w:t xml:space="preserve"> {escape(resolve(brief_text.FOOTNOTES[key]))}</w:t>'
        "</w:r></w:p></w:footnote>"
        for key, number in _footnotes.items()
    )
    separators = "".join(
        f'<w:footnote w:type="{kind}" w:id="{number}"><w:p><w:pPr><w:spacing w:after="0" '
        f'w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:{element}/></w:r></w:p></w:footnote>'
        for kind, number, element in (
            ("separator", -1, "separator"),
            ("continuationSeparator", 0, "continuationSeparator"),
        )
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f"<w:footnotes {nsdecls('w')}>{separators}{notes}</w:footnotes>"
    )
    part = Part(
        PackURI("/word/footnotes.xml"),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
        xml.encode("utf-8"),
        document.part.package,
    )
    document.part.relate_to(part, RT.FOOTNOTES)
    settings = document.settings.element
    zoom = settings.find(qn("w:zoom"))
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")  # required by the schema, missing in the template
    properties = parse_xml(
        f'<w:footnotePr {nsdecls("w")}><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr>'
    )
    anchor = settings.find(qn("w:endnotePr"))
    if anchor is None:
        anchor = settings.find(qn("w:compat"))
    if anchor is None:
        settings.append(properties)
    else:
        anchor.addprevious(properties)


def _add_numbering(document) -> None:
    """One list, numbered 1., 2., ... through the whole brief, as in the sample notes."""
    numbering = document.part.numbering_part.element
    abstract = parse_xml(
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{NUM_ID}">'
        '<w:multiLevelType w:val="singleLevel"/>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
        '<w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>'
        '<w:pPr><w:ind w:left="397" w:hanging="397"/></w:pPr>'
        f'<w:rPr><w:rFonts w:ascii="{SERIF}" w:hAnsi="{SERIF}" w:cs="{SERIF}"/><w:b/>'
        f'<w:color w:val="{NAVY}"/></w:rPr></w:lvl></w:abstractNum>'
    )
    first = numbering.find(qn("w:num"))
    if first is None:
        numbering.append(abstract)
    else:
        first.addprevious(abstract)
    numbering.append(
        parse_xml(
            f'<w:num {nsdecls("w")} w:numId="{NUM_ID}"><w:abstractNumId w:val="{NUM_ID}"/></w:num>'
        )
    )


def _number(paragraph) -> None:
    properties = paragraph._p.get_or_add_pPr()
    numbering = parse_xml(
        f'<w:numPr {nsdecls("w")}><w:ilvl w:val="0"/><w:numId w:val="{NUM_ID}"/></w:numPr>'
    )
    style = properties.find(qn("w:pStyle"))
    if style is None:
        properties.insert(0, numbering)
    else:
        style.addnext(numbering)


# --- the document -------------------------------------------------------------------------------


def _styles(document) -> None:
    normal = document.styles["Normal"]
    _style_font(normal, SERIF, 10.5, DARK)
    layout = normal.paragraph_format
    layout.space_before, layout.space_after, layout.line_spacing = Pt(0), Pt(6), 1.27
    heading = document.styles["Heading 1"]
    _style_font(heading, SANS, 13, NAVY, bold=True, italic=False)
    layout = heading.paragraph_format
    layout.space_before, layout.space_after, layout.keep_with_next = Pt(16), Pt(8), True
    layout.line_spacing = 1.0
    note_text = document.styles.add_style("Footnote Text", WD_STYLE_TYPE.PARAGRAPH)
    note_text.base_style = normal
    _style_font(note_text, SERIF, 8, GREY)
    note_text.paragraph_format.space_after, note_text.paragraph_format.line_spacing = Pt(2), 1.0
    note_reference = document.styles.add_style("Footnote Reference", WD_STYLE_TYPE.CHARACTER)
    note_reference.font.superscript = True


def _header_footer(section) -> None:
    section.different_first_page_header_footer = True
    header = section.header.paragraphs[0]
    tabs = header.paragraph_format.tab_stops
    for inherited in (4680, 9360):  # the Header style's centre and right tabs, in twips
        tabs.add_tab_stop(Twips(inherited), WD_TAB_ALIGNMENT.CLEAR)
    tabs.add_tab_stop(Cm(TEXT_WIDTH_CM), WD_TAB_ALIGNMENT.RIGHT)
    _run(header, brief_text.TITLE, SANS, 7.5, GREY)
    _run(header, f"\t{brief_text.SERIES.title()}  |  {brief_text.DATE}", SANS, 7.5, GREY)
    _border(header, "bottom", 12, NAVY, 4)
    for footer in (section.footer, section.first_page_footer):
        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _page_number(paragraph)


def _text(paragraph, text: str, font=SERIF, size=None, color=None) -> None:
    """Runs of ``text`` with its numbers resolved and its [^key] markers as footnotes."""
    text = resolve(text)
    position = 0
    for match in FOOTNOTE.finditer(text):
        _run(paragraph, text[position : match.start()], font, size, color)
        _footnote_reference(paragraph, match.group(1))
        position = match.end()
    _run(paragraph, text[position:], font, size, color)


def _cover(document) -> None:
    bar = document.add_paragraph()
    _border(bar, "top", 36, NAVY, 0)
    _spacing(bar, after=0, line=0.5)
    panel = document.add_table(rows=1, cols=1)
    panel.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = panel.cell(0, 0)
    cell.width = Cm(TEXT_WIDTH_CM)
    _shade_cell(cell, LIGHT)
    _cell_margins(cell, top=340, bottom=340, left=420, right=420)
    series = cell.paragraphs[0]
    _run(series, f"{brief_text.SERIES}  |  {brief_text.DATE.upper()}", SANS, 8.5, NAVY, True)
    _spacing(series, after=22, line=1.0)
    for text, size, color, bold, after, line in (
        (brief_text.TITLE, 22, NAVY, False, 6, 1.05),
        (brief_text.SUBTITLE, 13, GREY, False, 26, 1.0),
        (brief_text.AUTHOR, 10, DARK, True, 0, 1.0),
    ):
        paragraph = cell.add_paragraph()
        _run(paragraph, text, SANS, size, color, bold)
        _spacing(paragraph, after=after, line=line)
    _spacing(document.add_paragraph(), after=4, line=1.0)
    label = document.add_paragraph()
    _run(label, "Summary", SANS, 11, NAVY, bold=True)
    _spacing(label, before=6, after=8, line=1.0)
    for index, (lead, text) in enumerate(brief_text.SUMMARY, start=1):
        point = document.add_paragraph()
        point.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        layout = point.paragraph_format
        layout.left_indent, layout.first_line_indent = Cm(0.8), Cm(-0.8)
        layout.tab_stops.add_tab_stop(Cm(0.8))
        badge = _run(point, f" {index} ", SANS, 9.5, "FFFFFF", bold=True)
        badge._element.get_or_add_rPr().append(_shading(NAVY))
        _run(point, "\t")
        _run(point, resolve(lead) + " ", SERIF, 10, NAVY, bold=True)
        _text(point, text, SERIF, 10)
        _spacing(point, after=9, line=1.22)
    note = document.add_paragraph()
    _border(note, "top", 4, RULE, 6)
    _run(note, brief_text.DISCLAIMER, SANS, 7.5, GREY, italic=True)
    _spacing(note, before=10, after=0, line=1.1)
    document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def _numbered(document, lead: str, text: str) -> None:
    paragraph = document.add_paragraph()
    _number(paragraph)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    layout = paragraph.paragraph_format
    layout.left_indent, layout.first_line_indent = Cm(0.7), Cm(-0.7)
    _run(paragraph, resolve(lead) + " ", SERIF, None, NAVY, bold=True)
    _text(paragraph, text)
    _spacing(paragraph, after=8)


def _exhibit_heading(document, headline: str, title: str) -> None:
    head = document.add_paragraph()
    _border(head, "top", 6, RULE, 4)
    _run(head, headline, SANS, 9, DARK, bold=True)
    _spacing(head, before=8, after=2, line=1.1, keep_next=True)
    caption = document.add_paragraph()
    _run(caption, title, SANS, 9, NAVY, bold=True)
    _spacing(caption, after=4, line=1.1, keep_next=True)


def _exhibit_notes(document, notes: list[str], source: str) -> None:
    for line in notes:
        paragraph = document.add_paragraph()
        _text(paragraph, line, SANS, 7.5, GREY)
        _spacing(paragraph, after=0, line=1.1, keep_next=True)
    paragraph = document.add_paragraph()
    _run(paragraph, source, SANS, 7.5, GREY)
    _spacing(paragraph, after=12, line=1.1)


def _figure(document, key: str) -> None:
    spec = brief_text.FIGURES[key]
    _exhibit_heading(document, spec["headline"], spec["title"])
    document.add_picture(str(FIGURES / f"{key}.png"), width=Cm(spec["width_cm"]))
    picture = document.paragraphs[-1]
    picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(picture, after=4, line=1.0, keep_next=True)
    _exhibit_notes(document, spec["notes"], spec["source"])


def _table_1(document) -> None:
    spec = brief_text.TABLE_1
    _exhibit_heading(document, spec["headline"], spec["title"])
    rows = [spec["header"], *spec["rows"]]
    widths = [2.6, 2.9, 2.5, 2.9, 2.5, 3.4]
    table = document.add_table(rows=len(rows), cols=len(widths))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _table_borders(table, {"top": (12, NAVY), "bottom": (12, NAVY), "insideH": (2, RULE)})
    for i, values in enumerate(rows):
        for j, value in enumerate(values):
            cell = table.cell(i, j)
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            _cell_margins(cell, top=50, bottom=50, left=80, right=80)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            _spacing(paragraph, after=0, line=1.0, keep_next=True)
            if i == 0:
                _shade_cell(cell, "DCE4EE")
                _run(paragraph, value, SANS, 8, NAVY, bold=True)
            else:
                _run(paragraph, resolve(value), SANS, 8.5, DARK, bold=(j == 0 and i == 1))
    _spacing(document.add_paragraph(), after=0, line=0.6, keep_next=True)
    _exhibit_notes(document, spec["notes"], spec["source"])


def _annex(document) -> None:
    document.add_paragraph("Annex. Data and Methods", style="Heading 1")
    for label, text in brief_text.ANNEX:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _run(paragraph, label + " ", SERIF, 9.5, NAVY, bold=True)
        _text(paragraph, text, SERIF, 9.5)
        _spacing(paragraph, after=6, line=1.2)
    document.add_paragraph("References", style="Heading 1")
    for reference in brief_text.REFERENCES:
        paragraph = document.add_paragraph()
        layout = paragraph.paragraph_format
        layout.left_indent, layout.first_line_indent = Cm(0.6), Cm(-0.6)
        _run(paragraph, reference, SERIF, 9)
        _spacing(paragraph, after=4, line=1.15)


def build() -> None:
    """Write ``report/brief.docx``."""
    _facts.clear()
    _facts.update({fact["id"]: fact for fact in json.loads(FACTS_FILE.read_text("utf-8"))})
    _footnotes.clear()
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.left_margin = section.right_margin = Cm((21.0 - TEXT_WIDTH_CM) / 2)
    section.top_margin, section.bottom_margin = Cm(2.3), Cm(2.0)
    section.header_distance, section.footer_distance = Cm(1.1), Cm(1.0)
    _styles(document)
    _add_numbering(document)
    _header_footer(section)
    _cover(document)
    paragraphs = 0
    for item in brief_text.BODY:
        if item[0] == "h1":
            document.add_paragraph(item[1], style="Heading 1")
            continue
        _numbered(document, item[1], item[2])
        paragraphs += 1
        for key, after in brief_text.PLACEMENT:
            if after == paragraphs:
                if key == "T1":
                    _table_1(document)
                else:
                    _figure(document, key)
    _annex(document)
    _footnotes_part(document)
    document.core_properties.title = brief_text.TITLE
    document.core_properties.author = brief_text.AUTHOR
    temporary = BRIEF.with_name(".brief.tmp.docx")
    document.save(temporary)
    os.replace(temporary, BRIEF)  # Word may hold the previous file open


def main() -> int:
    build()
    used = {match.group(1) for text in texts() for match in PLACEHOLDER.finditer(text)}
    print(f"wrote {BRIEF.relative_to(paths.ROOT).as_posix()}: {len(used)} facts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

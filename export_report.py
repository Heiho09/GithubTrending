"""Export the weekly Markdown digest to a self-contained, linked A4 PDF."""

import argparse
from html import escape
from io import BytesIO
from pathlib import Path
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString
import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer


FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
INK = colors.HexColor("#13283F")
MUTED = colors.HexColor("#52677D")
BLUE = colors.HexColor("#245CC5")


def inline_text(node) -> str:
    """Translate only the inline markup used by our reports to ReportLab XML."""
    if isinstance(node, NavigableString):
        return escape(str(node))
    content = "".join(inline_text(child) for child in node.children)
    if node.name == "a":
        href = node.get("href", "")
        if urlparse(href).scheme == "https":
            return f'<a href="{escape(href, quote=True)}" color="#245CC5">{content}</a>'
    if node.name in ("strong", "b"):
        return f"<b>{content}</b>"
    if node.name == "br":
        return "<br/>"
    return content


def export_pdf(source: Path) -> Path:
    """Convert an existing digest offline. The Markdown is never modified."""
    document = BeautifulSoup(markdown.markdown(source.read_text(encoding="utf-8")), "html.parser")
    title = document.find("h1")
    if title is None or not document.find("h2"):
        raise ValueError(f"주간 보고서의 제목이나 저장소 항목이 없습니다: {source}")

    for name, filename in (("Nanum", "NanumGothic-Regular.ttf"), ("NanumBold", "NanumGothic-Bold.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
    pdfmetrics.registerFontFamily("Nanum", normal="Nanum", bold="NanumBold", italic="Nanum", boldItalic="NanumBold")

    base = ParagraphStyle("body", fontName="Nanum", fontSize=10, leading=15.5,
                          textColor=INK, alignment=TA_LEFT, wordWrap="CJK", spaceAfter=7)
    styles = {
        "title": ParagraphStyle("title", parent=base, fontName="NanumBold", fontSize=19, leading=27, spaceAfter=12),
        "heading": ParagraphStyle("heading", parent=base, fontName="NanumBold", fontSize=12, leading=18, spaceAfter=7),
        "meta": ParagraphStyle("meta", parent=base, fontSize=8.2, leading=12.5, textColor=MUTED, spaceAfter=2),
        "stats": ParagraphStyle("stats", parent=base, fontSize=8.8, leading=13, textColor=BLUE, spaceAfter=0),
    }
    story = [
        Paragraph("GITHUB / WEEKLY DIGEST", styles["meta"]),
        Spacer(1, 5),
        Paragraph(inline_text(title), styles["title"]),
        HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=12),
    ]
    section = []

    def finish_section():
        if section:
            story.append(KeepTogether(section.copy()))
            story.append(Spacer(1, 13))
            section.clear()

    for element in document.children:
        if isinstance(element, NavigableString) or element.name == "h1":
            continue
        if element.name == "ul":
            for item in element.find_all("li", recursive=False):
                story.append(Paragraph(inline_text(item), styles["meta"]))
            story.append(Spacer(1, 15))
        elif element.name == "h2":
            finish_section()
            section.append(Paragraph(inline_text(element), styles["heading"]))
        elif element.name == "p":
            style = styles["stats"] if "· 최근 1주 ★" in element.get_text() else base
            section.append(Paragraph(inline_text(element), style))
    finish_section()

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                           topMargin=16 * mm, bottomMargin=18 * mm,
                           title=title.get_text(), author="GithubTrending", invariant=1)

    def footer(canvas, _document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DEE5ED"))
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.setFont("Nanum", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 9 * mm, "GitHub Trending / Weekly snapshot")
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, str(canvas.getPageNumber()))
        canvas.restoreState()

    pdf.build(story, onFirstPage=footer, onLaterPages=footer)
    destination = source.with_suffix(".pdf")
    data = buffer.getvalue()
    if not destination.exists() or destination.read_bytes() != data:
        destination.write_bytes(data)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path, help="기존 주간 Markdown 보고서")
    args = parser.parse_args(argv)
    try:
        for source in args.reports:
            if source.suffix.lower() != ".md":
                raise ValueError(f"Markdown(.md) 파일을 지정하세요: {source}")
            print(f"PDF 저장: {export_pdf(source)}")
    except (OSError, ValueError) as error:
        print(f"PDF 생성 실패: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

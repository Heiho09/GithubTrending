from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader

from export_report import export_pdf
from weekly_trending import KST, Repository, render_report


class PdfTests(unittest.TestCase):
    def report(self, directory, description="한글 소개와 <agent> & 도구", count=5):
        source = Path(directory) / "2026-W47-all.md"
        repos = [Repository(f"owner/repo{index}", description, "Python", 1234, 12345)
                 for index in range(1, count + 1)]
        source.write_text(render_report(repos, datetime(2026, 11, 16, 9, tzinfo=KST), ""), encoding="utf-8")
        return source

    def test_a4_pdf_has_korean_text_links_and_embedded_fonts(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.report(directory)
            original = source.read_bytes()
            pdf = PdfReader(export_pdf(source))
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(len(pdf.pages), 1)
            page = pdf.pages[0]
            self.assertAlmostEqual(float(page.mediabox.width), 595.28, places=1)
            self.assertAlmostEqual(float(page.mediabox.height), 841.89, places=1)
            text = page.extract_text()
            self.assertIn("한글 소개와 <agent> & 도구", text)
            self.assertIn("2026-11-16 09:00:00 KST", text)
            self.assertIn("최근 1주 ★ +1,234", text)
            self.assertIn("owner/repo5", text)
            urls = {annotation.get_object()["/A"]["/URI"] for annotation in page["/Annots"]}
            self.assertIn("https://github.com/trending?since=weekly", urls)
            self.assertTrue({f"https://github.com/owner/repo{i}" for i in range(1, 6)} <= urls)
            fonts = [font.get_object() for font in page["/Resources"]["/Font"].values()]
            embedded = [font for font in fonts if "/FontDescriptor" in font and
                        "/FontFile2" in font["/FontDescriptor"]]
            self.assertEqual(len(embedded), 2)

    def test_reexport_is_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.report(directory)
            pdf = export_pdf(source)
            original = pdf.read_bytes()
            original_mtime = pdf.stat().st_mtime_ns
            export_pdf(source)
            self.assertEqual(pdf.read_bytes(), original)
            self.assertEqual(pdf.stat().st_mtime_ns, original_mtime)

    def test_long_descriptions_continue_across_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.report(directory, description="긴 설명을 안전하게 다음 페이지에 이어서 표시합니다. " * 100)
            pdf = PdfReader(export_pdf(source))
            self.assertGreater(len(pdf.pages), 1)
            text = "".join(page.extract_text() for page in pdf.pages)
            for index in range(1, 6):
                self.assertIn(f"owner/repo{index}", text)
            self.assertEqual(text.count("전체 ★ 12,345"), 5)

    def test_invalid_markdown_does_not_replace_existing_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.report(directory)
            pdf = export_pdf(source)
            original = pdf.read_bytes()
            source.write_text("Not a report", encoding="utf-8")
            with self.assertRaises(ValueError):
                export_pdf(source)
            self.assertEqual(pdf.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()

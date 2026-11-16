from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

import weekly_trending as trending


def article(name, *, description="A tool &amp; toolkit", language="Python", stars="1,234"):
    return f"""
    <article class="Box-row">
      <a href="/login?return_to={name}">Star</a>
      <h2><a href="/{name}"><span>{name.split('/')[0]} /</span> repository</a></h2>
      {f'<p>{description}</p>' if description else ''}
      <div><span itemprop="programmingLanguage">{language}</span>
      <a href="/{name}/stargazers"><svg><path /></svg>12,345</a>
      <a href="/{name}/forks">99</a>
      <span class="d-inline-block float-sm-right"><svg></svg>{stars} stars this week</span>
      </div>
    </article>
    """


PAGE = "<html><body>" + "".join(
    article(f"owner/repo{index}") for index in range(1, 7)
) + "</body></html>"


class ParsingTests(unittest.TestCase):
    def test_order_limit_links_and_distinct_star_counts(self):
        repos = trending.parse_repositories(PAGE, 5)
        self.assertEqual([r.name for r in repos], [f"owner/repo{i}" for i in range(1, 6)])
        self.assertEqual(repos[0].weekly_stars, 1234)
        self.assertEqual(repos[0].total_stars, 12345)
        self.assertEqual(repos[0].description, "A tool & toolkit")
        self.assertEqual(repos[0].language, "Python")

    def test_missing_optional_fields_and_zero_stars(self):
        html = article("a/b", description="", stars="0").replace(
            '<span itemprop="programmingLanguage">Python</span>', ""
        ) + article("c/d") + article("e/f")
        repo = trending.parse_repositories(html, 3)[0]
        self.assertEqual(repo.description, "설명 없음")
        self.assertEqual(repo.language, "미표기")
        self.assertEqual(repo.weekly_stars, 0)

    def test_empty_short_changed_and_duplicate_pages_fail(self):
        for html in (
            "<html>Rate limited</html>",
            article("a/b"),
            PAGE.replace("stars this week", "stars today"),
            PAGE.replace('href="/owner/repo1"', 'href="https://example.com/owner/repo1"'),
            PAGE.replace("owner/repo2", "owner/repo1"),
            PAGE.replace("/stargazers", "/followers"),
        ):
            with self.subTest(html=html[:60]), self.assertRaises(ValueError):
                trending.parse_repositories(html, 5)

    def test_only_three_to_five_are_supported(self):
        with self.assertRaises(ValueError):
            trending.parse_repositories(PAGE, 2)


class ReportTests(unittest.TestCase):
    def test_korean_time_and_iso_week_year_boundary(self):
        instant = datetime(2025, 12, 28, 16, 0, tzinfo=timezone.utc)
        path = trending.report_path(Path("reports"), instant, "")
        self.assertEqual(path.name, "2026-W01-all.md")
        text = trending.render_report(trending.parse_repositories(PAGE, 3), instant, "")
        self.assertIn("2025-12-29 01:00:00 KST", text)
        self.assertIn("2026-W01", text)
        self.assertIn("최근 1주 ★ +1,234 · 전체 ★ 12,345", text)
        self.assertIn("[owner/repo1](https://github.com/owner/repo1)", text)
        self.assertEqual(text.count("\n## "), 3)

    def test_descriptions_remain_plain_text(self):
        text = trending.markdown_text('<img src=x> [click](https://example.com) **bold**\nnext')
        self.assertNotIn("<img", text)
        self.assertIn(r"\[click\]\(https://example.com\)", text)
        self.assertIn(r"\*\*bold\*\* next", text)

    def test_language_is_encoded_in_url_and_filename(self):
        self.assertEqual(trending.trending_url("c++"), "https://github.com/trending/c%2B%2B?since=weekly")
        instant = datetime(2026, 11, 16, tzinfo=timezone.utc)
        self.assertEqual(trending.report_path(Path("reports"), instant, "c++").name, "2026-W47-c%2B%2B.md")


class CommandTests(unittest.TestCase):
    def test_creation_idempotence_and_explicit_refresh(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(trending, "fetch_page", return_value=PAGE) as fetch:
            args = ["--output-dir", directory]
            with redirect_stdout(StringIO()):
                self.assertEqual(trending.main(args), 0)
                reports = list(Path(directory).glob("*.md"))
                self.assertEqual(len(reports), 1)
                original = reports[0].read_bytes()
                self.assertEqual(trending.main(args), 0)
                self.assertEqual(fetch.call_count, 1)
                self.assertEqual(reports[0].read_bytes(), original)
                fetch.return_value = PAGE.replace("A tool", "Updated tool")
                self.assertEqual(trending.main(args + ["--overwrite"]), 0)
                self.assertIn("Updated tool", reports[0].read_text())

    def test_failed_fetch_creates_no_report(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(trending, "fetch_page", side_effect=URLError("unavailable")):
            with redirect_stderr(StringIO()):
                self.assertEqual(trending.main(["--output-dir", directory]), 1)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_parse_failure_preserves_existing_report_on_refresh(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(trending, "fetch_page", return_value=PAGE) as fetch:
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                args = ["--output-dir", directory]
                self.assertEqual(trending.main(args), 0)
                report = next(Path(directory).glob("*.md"))
                original = report.read_bytes()
                fetch.return_value = "<html>Unavailable</html>"
                self.assertEqual(trending.main(args + ["--overwrite"]), 1)
                self.assertEqual(report.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()

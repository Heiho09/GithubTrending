"""Collect a small weekly GitHub Trending digest without an API key."""

import argparse
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
import re
import sys
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from export_report import export_pdf


KST = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class Repository:
    name: str
    description: str
    language: str
    weekly_stars: int
    total_stars: int


def trending_url(language: str = "") -> str:
    suffix = f"/{quote(language, safe='')}" if language else ""
    return f"https://github.com/trending{suffix}?since=weekly"


def fetch_page(url: str) -> str:
    request = Request(url, headers={"User-Agent": "GithubTrending-weekly-digest/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_repositories(html: str, limit: int) -> list[Repository]:
    if limit not in (3, 4, 5):
        raise ValueError("저장소 개수는 3~5개여야 합니다.")
    rows = BeautifulSoup(html, "html.parser").select("article.Box-row")
    if len(rows) < limit:
        raise ValueError(f"요청한 {limit}개 중 {len(rows)}개만 발견했습니다. 페이지를 확인하세요.")

    repositories = []
    seen = set()
    for row in rows[:limit]:
        link = row.select_one("h2 a[href]")
        href = str(link.get("href", "")) if link else ""
        if not re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", href):
            raise ValueError("저장소 링크를 읽지 못했습니다. Trending 페이지 구조를 확인하세요.")
        name = href.lstrip("/")
        if name in seen:
            raise ValueError(f"중복 저장소를 발견했습니다: {name}")
        seen.add(name)

        weekly = row.select_one("span.float-sm-right")
        weekly_text = weekly.get_text(" ", strip=True) if weekly else ""
        weekly_match = re.fullmatch(r"([0-9][0-9,]*) stars? this week", weekly_text)
        total = row.find("a", href=f"{href}/stargazers")
        total_text = total.get_text(" ", strip=True) if total else ""
        if not weekly_match or not re.fullmatch(r"[0-9][0-9,]*", total_text):
            raise ValueError(f"{name}의 주간/전체 별 수를 읽지 못했습니다.")

        description = row.select_one("p")
        language = row.select_one('[itemprop="programmingLanguage"]')
        repositories.append(Repository(
            name=name,
            description=" ".join(description.get_text(" ", strip=True).split()) if description else "설명 없음",
            language=language.get_text(strip=True) if language else "미표기",
            weekly_stars=int(weekly_match.group(1).replace(",", "")),
            total_stars=int(total_text.replace(",", "")),
        ))
    return repositories


def markdown_text(value: str) -> str:
    # Treat repository descriptions as text, never embedded HTML/Markdown.
    value = escape(" ".join(value.split()), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#!|~])", r"\\\1", value)


def render_report(repositories: list[Repository], collected_at: datetime, language: str) -> str:
    local_time = collected_at.astimezone(KST)
    year, week, _ = local_time.isocalendar()
    lines = [
        f"# GitHub 주간 Trending — {year}-W{week:02d}",
        "",
        f"- 수집: {local_time:%Y-%m-%d %H:%M:%S} KST",
        f"- 대상: {markdown_text(language) if language else '전체 언어'} · 상위 {len(repositories)}개",
        f"- 출처: <{trending_url(language)}>",
        "- 조회 시점의 최근 1주 Trending 순서입니다. 주차는 수집한 주차를 뜻합니다.",
        "- 소개는 저장소 설명 원문입니다.",
        "",
    ]
    for rank, repo in enumerate(repositories, 1):
        lines.extend([
            f"## {rank}. [{markdown_text(repo.name)}](https://github.com/{repo.name})",
            "",
            markdown_text(repo.description),
            "",
            f"{markdown_text(repo.language)} · 최근 1주 ★ +{repo.weekly_stars:,} · 전체 ★ {repo.total_stars:,}",
            "",
        ])
    return "\n".join(lines)


def report_path(output_dir: Path, collected_at: datetime, language: str) -> Path:
    year, week, _ = collected_at.astimezone(KST).isocalendar()
    return output_dir / f"{year}-W{week:02d}-{quote(language, safe='') or 'all'}.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, choices=(3, 4, 5), default=5)
    parser.add_argument("--language", default="", help="Trending 언어 경로 값 (예: python, c++)")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--overwrite", action="store_true", help="이번 주의 기존 보고서 갱신")
    args = parser.parse_args(argv)
    language = args.language.strip().lower()
    now = datetime.now(KST)
    destination = report_path(args.output_dir, now, language)
    try:
        if destination.exists() and not args.overwrite:
            pdf = export_pdf(destination)
            print(f"기존 기록 보존: {destination} (--overwrite로 갱신 가능)")
            print(f"PDF 저장: {pdf}")
            return 0
        repositories = parse_repositories(fetch_page(trending_url(language)), args.limit)
        report = render_report(repositories, now, language)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w" if args.overwrite else "x", encoding="utf-8") as output:
            output.write(report)
        pdf = export_pdf(destination)
    except (URLError, OSError, ValueError) as error:
        print(f"수집 실패: {error}", file=sys.stderr)
        return 1
    print(f"보고서 저장: {destination}")
    print(f"PDF 저장: {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

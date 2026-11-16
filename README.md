# GithubTrending

GitHub Trending의 주간 목록에서 상위 3~5개 저장소를 골라 Markdown과 PDF로 기록합니다.
기본값은 **전체 언어 상위 5개**이며, 소개는 저장소에 등록된 설명 원문을 사용합니다.
별도 API 키나 요약 서비스는 필요하지 않습니다.

## 로컬 실행

Python 3.12 기준:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python weekly_trending.py
```

`reports/2026-W47-all.md`와 `reports/2026-W47-all.pdf`처럼
**수집일의 한국 시간 ISO 주차**로 보고서를 저장합니다.
보고서에는 순위, 링크, 한 줄 소개, 언어, 주간 신규 별 수, 전체 별 수가 포함됩니다.

```bash
# Python 저장소 3개만 수집
.venv/bin/python weekly_trending.py --language python --limit 3

# 같은 주의 기록을 명시적으로 갱신
.venv/bin/python weekly_trending.py --overwrite

# 네트워크 없이 테스트
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

`--language`에는 GitHub Trending의 언어 경로 값(예: `python`, `typescript`, `c++`)을
사용합니다. `--output-dir`로 출력 위치를 바꿀 수 있습니다. 같은 주·언어의 보고서가
이미 있으면 재수집하지 않고 해당 Markdown에서 PDF만 생성합니다.
개수를 바꿔 다시 수집할 때도 `--overwrite`가 필요합니다.
네트워크 오류나 페이지 구조 변경으로 요청한 수만큼 읽지 못하면 실패하며 보고서를 만들지 않습니다.

## 문서 보기와 내보내기

상세 검토용 초안: [PDF](reports/2026-W47-analysis-draft.pdf) ·
[Markdown](reports/2026-W47-analysis-draft.md). 각 저장소의 목적·기능·구성 방식·활용 대상과
근거 링크를 포함합니다. 이 초안은 6.1 Terra / Medium 분석 에이전트로 작성했으며,
예약 워크플로의 무인 API 요약은 아직 연결하지 않았습니다.
작성 기준은 [상세 요약 지침](docs/summary-guidelines.md)을 참고하세요.

- **GitHub에서 읽기:** [첫 Markdown 초안](reports/2026-W47-all.md)
- **다운로드·공유·인쇄:** [첫 PDF 초안](reports/2026-W47-all.pdf)

PDF는 A4 문서이며, 저장소 링크를 클릭할 수 있습니다. 한글 글꼴을 PDF 안에 포함해
읽는 컴퓨터에 별도 글꼴이나 Python을 설치하지 않아도 됩니다. 설명이 길면 여러 페이지로 이어집니다.
Markdown이 원본이며 PDF는 같은 내용을 표시합니다. 소개는 자동 번역하지 않은 저장소 설명 원문입니다.

이미 저장한 보고서는 인터넷 연결 없이 PDF로 다시 내보낼 수 있습니다.

```bash
.venv/bin/python export_report.py reports/2026-W47-all.md
# 모든 기존 보고서를 변환
.venv/bin/python export_report.py reports/*.md
```

이 명령은 Markdown이나 수집 시각을 바꾸지 않으며, 같은 이름의 PDF를 갱신합니다.
PDF 생성이 실패해도 수집한 Markdown은 남으므로, 문제를 해결한 뒤 위 명령으로 다시 생성할 수 있습니다.
번들 글꼴의 출처와 라이선스는 [assets/fonts/README.md](assets/fonts/README.md)에 있습니다.

## 주간 자동 실행

`.github/workflows/weekly-trending.yml`은 매주 월요일 **09:00 KST (00:00 UTC)**에
전체 언어 상위 5개를 수집해 Markdown과 PDF를 모두 `reports/`에 커밋합니다.
GitHub Actions 예약 실행은 지연될 수 있습니다.

1. 이 코드를 GitHub 저장소의 기본 브랜치에 반영합니다.
2. 저장소에서 GitHub Actions 실행 및 워크플로의 `contents: write` 권한이 허용되어야 합니다.
3. Actions의 **Weekly GitHub Trending → Run workflow**로 수동 실행할 수도 있습니다.

자동 실행에는 GitHub가 제공하는 `GITHUB_TOKEN`을 사용하며 개인 토큰은 필요하지 않습니다.
브랜치 보호 규칙이 봇의 직접 커밋을 막으면 자동 저장 단계는 실패합니다.
이 경우에도 해당 실행의 `weekly-trending-report` 아티팩트에서 Markdown과 PDF를 받을 수 있습니다.
아티팩트에는 보관 기한이 있으므로 장기 보관본은 저장소의 `reports/` 파일입니다.
테스트 워크플로는 push와 pull request에서 실행됩니다.

## 데이터의 의미

- 출처: <https://github.com/trending?since=weekly>
- GitHub가 보여주는 Trending 순서를 유지합니다. 주간 별 수로 다시 정렬한 순위가 아닙니다.
- `weekly`는 **조회 시점의 최근 1주**입니다. 월요일~일요일의 확정 통계나 전체 GitHub의 인기 순위가 아닙니다.
- 파일의 주차는 수집한 주차입니다. 정확한 수집 시간과 출처 URL도 보고서에 기록합니다.
- 과거 주차를 조회하는 공식 Trending API는 없으므로, 실행 시점부터 기록을 쌓습니다.
- HTML 페이지를 수집하므로 GitHub 페이지 구조가 바뀌면 파서 수정이 필요할 수 있습니다.

## 무료 상세 분석: 자동 수집 + 요청 시 작성

예약 실행은 유료 AI API를 호출하지 않습니다. Trending 보고서와 함께 상위 저장소의
공개 README를 `collections/YYYY-Www-all.json`에 보관하고 `collections/latest.json`에
최신 파일명을 기록합니다. README마다 원본 URL과 수집 시각을 저장하며 실패는 `error`에
남습니다. 원문은 제3자 자료이므로 공유·재배포 전에 각 저장소의 라이선스를 확인하세요.

상세 해설은 예약 실행만으로 만들어지지 않습니다. 저장소를 읽을 수 있는 ChatGPT/Codex에서
다음처럼 요청하거나, 최신 JSON을 내려받아 채팅에 첨부하세요.

> collections/latest.json이 가리키는 자료를 읽고 docs/summary-guidelines.md 기준으로
> 상위 저장소의 목적, 기능, 구성 방식과 출처를 한국어로 정리해 Markdown과 PDF 초안을
> 만들어줘. 수집 실패는 명시하고, 유료 AI API는 호출하지 마.

채팅의 이용 한도는 사용하는 서비스와 플랜에 따릅니다. 작성된 문서는 검토 후 GitHub에
별도로 저장해야 합니다. 예약 시간에는 채팅이나 알림이 자동으로 시작되지 않습니다.
GitHub Actions의 무료 제공량 및 저장 공간은 저장소 공개 여부와 플랜에 따라 다릅니다.

로컬 수동 수집: `.venv/bin/python collect_evidence.py reports/2026-W47-all.md`.
기존 자료는 보존하며 `--overwrite`를 지정할 때만 다시 수집합니다. 성공 건수와 개별
오류를 확인하세요. GitHub 반영 후 Actions 수동 실행으로 수집과 저장을 검증할 수 있습니다.

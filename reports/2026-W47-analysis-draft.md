# GitHub 주간 Trending 저장소 분석 — 2026-W47

2026-11-16 16:04 KST에 공개 README와 저장소 화면을 확인했다. 아래 기능과 구조는 그 시점의 문서 기준이며, 순위·언어·별 수는 2026-11-16 15:47 KST에 수집한 주간 Trending 스냅샷 기준이다. 두 자료의 시점과 의미는 다르다.

작성 모델: gpt-6.1-terra · reasoning medium. 공개 문서에 근거한 검토용 초안이며, 각 프로젝트를 설치하거나 기능을 실행 검증한 결과는 아니다.

## 1. meta/astryx

**목적:** 사람과 AI 에이전트가 함께 사용할 수 있도록 만든 오픈소스 디자인 시스템이다. React 19 이상을 사용하는 제품 개발자와 디자인 시스템 팀이 주요 대상이다. README는 현재 베타라고 밝힌다.

**기능:** 접근성을 고려한 150개 이상의 컴포넌트, 브랜드 테마, 다크 모드와 템플릿을 제공한다. CSS 사용자 정의 속성으로 테마를 바꾸고, CLI의 swizzle로 컴포넌트 소스를 프로젝트에 가져와 수정할 수 있다.

**구조:** React와 StyleX를 기반으로 하며 `packages/`에 core·cli·build·themes, `apps/`에 문서 사이트와 Storybook, `internal/`에 내부 도구가 있다. 사용자는 미리 빌드된 CSS와 타입이 있는 React 컴포넌트를 사용한다.

**스냅샷:** TypeScript · 최근 1주 별 +13,501 · 전체 별 29,108. **출처:** [README 및 저장소](https://github.com/meta/astryx), [패키지](https://github.com/meta/astryx/tree/main/packages).

## 2. anthropics/skills

**목적:** Claude가 전문 작업에 활용할 수 있는 스킬 예제와 스킬 작성 방식을 공개한다. 자체 업무용 스킬을 만들거나 Claude Code에서 활용하려는 개발자에게 유용하다.

**기능:** 문서 생성과 편집, 웹 앱 테스트, MCP 서버 생성, 디자인 및 기업 커뮤니케이션 등의 예제를 제공한다. Claude Code에서는 저장소를 플러그인 마켓플레이스로 등록해 document-skills 또는 example-skills를 설치할 수 있다. README는 예제가 교육·시연용이므로 중요한 작업 전에 직접 테스트하라고 안내한다.

**구조:** 각 스킬은 지침과 메타데이터가 담긴 `SKILL.md`를 포함한 독립 폴더다. `skills/`에 예제가 있고 `spec/`에 명세, `template/`에 스킬 템플릿이 있다. docx·pdf·pptx·xlsx 스킬도 포함된다.

**스냅샷:** Python · 최근 1주 별 +6,077 · 전체 별 195,508. **출처:** [README 및 저장소](https://github.com/anthropics/skills), [스킬 목록](https://github.com/anthropics/skills/tree/main/skills).

## 3. sherlock-project/sherlock

**목적:** 사용자 이름을 이용해 여러 소셜 네트워크의 계정을 찾는 명령줄 도구다. 여러 서비스에 걸친 공개 사용자 이름 조사에 활용할 수 있다.

**기능:** README는 400개 이상의 소셜 네트워크를 대상으로 한다고 설명한다. 한 번에 여러 사용자 이름을 검색할 수 있으며 특정 사이트로 범위를 제한하거나 CSV·XLSX 출력과 프록시를 지정할 수 있다. 결과는 조사 단서이며 계정 소유자의 동일성까지 확정하지는 않는다.

**구조:** 저장소의 Python 프로젝트 설정은 `pyproject.toml`에 있고 `sherlock_project/`, `tests/`, `docs/` 디렉터리가 있다. README는 루트가 아닌 `docs/README.md`에 있으며 pipx와 Docker 설치 방법을 안내한다.

**스냅샷:** Python · 최근 1주 별 +10,412 · 전체 별 112,683. **출처:** [README](https://github.com/sherlock-project/sherlock/blob/master/docs/README.md), [저장소 파일](https://github.com/sherlock-project/sherlock).

## 4. backnotprop/plannotator

**목적:** 코딩 에이전트가 만든 계획과 결과물을 사람이 검토하고 피드백을 전달하는 로컬 브라우저 기반 작업 공간이다. 여러 에이전트와 함께 개발하는 개인과 팀을 겨냥한다.

**기능:** 계획·명세·HTML 등에 주석을 달고 에이전트에 피드백을 보낼 수 있다. 로컬 변경이나 원격 PR의 diff를 검토하고, Inbox에서 여러 에이전트의 질문과 파일을 모아 볼 수 있다. Claude Code, Codex 등과 플러그인·훅·명령을 통해 연결한다.

**구조:** 저장소에 `apps/`, `packages/`, `docs/`, `tests/`가 있으며 README는 `apps/codex/`, `apps/hook/` 등 에이전트별 연동 문서를 연결한다. 연결 및 설치 절차는 에이전트마다 다르다.

**스냅샷:** TypeScript · 최근 1주 별 +1,719 · 전체 별 12,048. **출처:** [README 및 저장소](https://github.com/backnotprop/plannotator), [Codex 연동](https://github.com/backnotprop/plannotator/tree/main/apps/codex).

## 5. vercel-labs/agent-browser

**목적:** AI 에이전트가 셸 명령으로 브라우저를 조작하도록 만든 네이티브 Rust CLI다. 브라우저 자동화를 에이전트에 연결하려는 개발자가 사용할 수 있다.

**기능:** `snapshot`으로 접근성 트리와 요소 참조를 읽은 뒤 참조를 사용해 클릭하고 결과를 다시 확인할 수 있다. 스크린샷·PDF 캡처와 세션도 지원하며 MCP 서버로 실행할 수 있다. 페이지가 바뀌면 새 스냅샷을 받아야 한다.

**구조:** README에 따르면 CLI는 첫 명령에서 시작하는 백그라운드 데몬에 명령을 보내고, 데몬은 Chrome DevTools Protocol로 브라우저를 제어한다. 저장소에는 Rust 검사 명령을 실행하는 `cli/`와 `docs/`, `examples/`, `skills/` 등이 있다.

**스냅샷:** Rust · 최근 1주 별 +4,217 · 전체 별 51,744. **출처:** [README 및 저장소](https://github.com/vercel-labs/agent-browser), [CLI 디렉터리](https://github.com/vercel-labs/agent-browser/tree/main/cli).

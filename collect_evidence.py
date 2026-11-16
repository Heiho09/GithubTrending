"""Archive public README evidence for an existing weekly Trending snapshot."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


def collect(report: Path, output: Path, overwrite: bool = False):
    snapshot = report.read_text(encoding='utf-8')
    names = re.findall(r'^## \d+\. \[[^\]]+\]\(https://github\.com/([\w.-]+/[\w.-]+)\)', snapshot, re.M)
    if not 3 <= len(names) <= 5 or len(set(names)) != len(names):
        raise ValueError('보고서에서 3~5개의 고유 저장소를 찾지 못했습니다.')
    target = output / (report.stem + '.json')
    if target.exists() and not overwrite:
        print(f'기존 자료 보존: {target}')
        return target
    entries = []
    for name in names:
        item = {'repository': name, 'readme_url': None, 'readme': None, 'error': None}
        errors = []
        for filename in ('README.md', 'docs/README.md', 'readme.md'):
            url = f'https://raw.githubusercontent.com/{name}/HEAD/{filename}'
            try:
                request = Request(url, headers={'User-Agent': 'GithubTrending-evidence/1.0'})
                with urlopen(request, timeout=20) as response:
                    data = response.read(500001)
                if len(data) > 500000:
                    raise ValueError('README가 500KB 제한을 초과했습니다.')
                item.update(readme_url=url, readme=data.decode('utf-8'), error=None)
                break
            except (HTTPError, URLError, TimeoutError, UnicodeError, OSError, ValueError) as exc:
                errors.append(f'{filename}: {exc}')
        if not item['readme']:
            item['error'] = '; '.join(errors)
        entries.append(item)
    output.mkdir(parents=True, exist_ok=True)
    payload = {'collected_at': datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),
               'trending_snapshot': report.name, 'snapshot_markdown': snapshot,
               'repositories': entries}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'latest.json').write_text(json.dumps({'path': target.name, 'collected_at': payload['collected_at']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'자료 저장: {target}; README 성공 {sum(bool(x["readme"]) for x in entries)}/{len(entries)}')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('collections'))
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    collect(args.report, args.output_dir, args.overwrite)

if __name__ == '__main__':
    main()

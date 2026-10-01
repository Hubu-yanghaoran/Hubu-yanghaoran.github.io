"""Check public resource entry points without downloading projects or executing code."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent

def check(item):
    url = item['source']
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        return dict(name=item['name'], source=url, state='unverified', reason='Unsupported public URL')
    request = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'PersonalHomepageResourceAudit/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return dict(name=item['name'], source=url, status=response.status,
                        final_url=response.url, state='reachable')
    except urllib.error.HTTPError as error:
        return dict(name=item['name'], source=url, status=error.code,
                    state='unavailable' if error.code in {404, 410} else 'unverified')
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return dict(name=item['name'], source=url, state='unverified', reason=type(error).__name__)

def main():
    items = json.loads((ROOT / 'template-data.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, items))
    report = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Public entry point reachability; compilation is not verified.', 'results': results}
    (ROOT / 'resource-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({state: sum(item['state'] == state for item in results)
                      for state in ('reachable', 'unavailable', 'unverified')}))

if __name__ == '__main__':
    main()

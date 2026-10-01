"""Check local HTML links, resources and fragment targets after building."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])

def check(root):
    root = Path(root).resolve()
    documents = {}
    for path in root.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text(encoding='utf-8'))
        documents[path.resolve()] = parser
    failures = []
    count = 0
    for path, parser in documents.items():
        for link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            count += 1
            target = ((root / unquote(parsed.path).lstrip('/')) if parsed.path.startswith('/') else path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_relative_to(root) or not target.is_file():
                failures.append(f'{path.relative_to(root)}: missing/outside {link}')
            elif parsed.fragment and target in documents and unquote(parsed.fragment) not in documents[target].ids:
                failures.append(f'{path.relative_to(root)}: missing anchor {link}')
    if failures:
        raise ValueError('\n'.join(failures))
    print(f'Checked {len(documents)} pages and {count} local links/resources')

if __name__ == '__main__':
    check(Path(__file__).resolve().parent.parent / '_site')

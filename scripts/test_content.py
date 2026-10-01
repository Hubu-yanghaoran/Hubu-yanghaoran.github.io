import json
import tempfile
import unittest
from pathlib import Path
from content import collect_content, validate_item
from markdown_reader import markdown_document
from layout import public_pages

class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root / 'content/example'
        (self.folder / 'chapters/assets').mkdir(parents=True)
        self.main = self.folder / 'chapters/main.md'
        self.main.write_text('# 测试\n\n## 图示\n\n![中文图片](assets/格点.png)\n\n$x_1 + x_2$\n', encoding='utf-8')
        (self.folder / 'chapters/assets/格点.png').write_bytes(b'fixture')
        self.item = {'title': '测试', 'category': '数学', 'date': '2026-10-01',
                     'main': 'chapters/main.md', 'attachments': [{'file': 'chapters/main.md'}]}
        self.save()

    def save(self):
        (self.folder / 'note.json').write_text(json.dumps(self.item, ensure_ascii=False), encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def test_nested_chinese_image_is_copied_and_linked_from_detail(self):
        _, files, pages, _ = collect_content(self.root)
        self.assertIn('content/example/chapters/assets/格点.png', files)
        page = pages['content/example/index.html']
        self.assertIn('src="chapters/assets/%E6%A0%BC%E7%82%B9.png"', page)
        self.assertIn('本文目录', page)
        self.assertIn('class="math inline"', page)

    def test_missing_or_outside_image_rejected(self):
        for value in ['missing.png', '../../../outside.png', 'https://example.com/a.png', '%2e%2e/%2e%2e/%2e%2e/a.png']:
            self.main.write_text(f'![图]({value})', encoding='utf-8')
            with self.subTest(value=value), self.assertRaises(ValueError):
                collect_content(self.root)

    def test_table_quote_nested_list_and_escaped_html(self):
        rendered, _, _ = markdown_document('| A | B |\n|---|---|\n|1|2|\n\n> 引用\n\n- 外层\n  - 内层\n\n<script>alert(1)</script>')
        self.assertIn('<table>', rendered)
        self.assertIn('<blockquote>', rendered)
        self.assertEqual(rendered.count('<ul>'), 2)
        self.assertNotIn('<script>', rendered)

    def test_math_preserves_underscores_and_ignores_code(self):
        rendered, _, _ = markdown_document('$x_1 * y_2$\n\n$$\n\\begin{pmatrix}1 & 0\\\\0 & 1\\end{pmatrix}\n$$\n\n`$code$`\n\n```\n$not_math$\n```')
        self.assertIn('x_1 * y_2', rendered)
        self.assertIn('class="math block"', rendered)
        self.assertEqual(rendered.count('class="math inline"'), 1)
        self.assertIn('<code>$code$</code>', rendered)

    def test_duplicate_heading_anchors(self):
        rendered, toc, _ = markdown_document('## 定义\n\n## 定义')
        self.assertIn('id="定义"', rendered)
        self.assertIn('id="定义-2"', rendered)
        self.assertIn('href="#定义-2"', toc)

    def test_matching_document_title_removed_with_anchor_and_hierarchy_preserved(self):
        rendered, toc, _ = markdown_document('# **My title**\n\n## Definition\n\n### Example', page_title='My title')
        self.assertNotIn('<h2 id="my-title"', rendered)
        self.assertIn('id="my-title"', rendered)
        self.assertIn('<h2 id="definition"', rendered)
        self.assertIn('<h3 id="example"', rendered)
        self.assertNotIn('href="#my-title"', toc)

    def test_different_or_nonleading_title_is_kept(self):
        for source in ('# Other title\n\n## Definition', 'Intro\n\n# My title'):
            rendered, _, _ = markdown_document(source, page_title='My title')
            self.assertIn('<h2', rendered)

    def test_explicit_document_title_does_not_change_source_download(self):
        source = self.main.read_text(encoding='utf-8')
        self.item.update(title='页面标题（测试）', document_title='测试')
        self.save()
        _, _, pages, _ = collect_content(self.root)
        self.assertNotIn('<h2 id="测试">测试</h2>', pages['content/example/index.html'])
        self.assertEqual(self.main.read_text(encoding='utf-8'), source)

    def test_bracket_math_is_escaped_and_preserved(self):
        rendered, _, _ = markdown_document(r'\(x_1 + y_2\)' + '\n\n' + r'\[a<b\]')
        self.assertIn('class="math inline"', rendered)
        self.assertIn('class="math block"', rendered)
        self.assertIn('a&lt;b', rendered)

    def test_unsafe_links_not_rendered(self):
        rendered, _, _ = markdown_document('[click](javascript:alert%281%29)')
        self.assertNotIn('href="javascript:', rendered)

    def test_date_and_field_types(self):
        for field, value in [('date', '2026-99-01'), ('updated', 123), ('tags', 'wrong'), ('attachments', None)]:
            self.item[field] = value
            self.save()
            with self.subTest(field=field), self.assertRaises((ValueError, TypeError)):
                collect_content(self.root)
            del self.item[field]

    def test_static_catalog_and_home_include_note_without_javascript(self):
        pages = public_pages([{'title':'Unique note', 'category':'数学', 'url':'content/example/index.html'}], [])
        for name in ('index.html','notes.html'):
            self.assertIn('Unique note', pages[name])
            self.assertIn('content/example/index.html', pages[name])

    def test_unlisted_local_link_rejected(self):
        self.main.write_text('[private](private.txt)', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '登记'):
            collect_content(self.root)

if __name__ == '__main__':
    unittest.main()

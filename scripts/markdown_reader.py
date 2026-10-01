"""Shared Markdown rendering for published pages and local previews."""
import html
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'vendor'))
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.texmath import texmath_plugin

IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}


def local_resource(value, source, folder):
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith('/') or '\\' in value:
        raise ValueError(f'图片应使用笔记目录内的相对路径：{value}')
    relative = unquote(parsed.path)
    if ':' in relative or '\\' in relative:
        raise ValueError(f'非法资源路径：{value}')
    path = source.parent / relative
    if any(part.is_symlink() for part in [path, *path.parents] if part.is_relative_to(folder)):
        raise ValueError(f'图片不能使用符号链接：{value}')
    path = path.resolve()
    if not path.is_relative_to(folder.resolve()) or not path.is_file():
        raise ValueError(f'图片不存在或越出笔记目录：{value}')
    if path.suffix.lower() not in IMAGE_TYPES:
        raise ValueError(f'不支持的正文图片格式：{value}')
    return path


def markdown_document(text, image_handler=None, link_handler=None, page_title=None):
    parser = MarkdownIt('commonmark', {'html': False, 'breaks': False}).enable('table')
    parser.use(dollarmath_plugin, allow_labels=False, allow_space=False,
               allow_digits=False, double_inline=True)
    parser.use(texmath_plugin, delimiters='brackets')
    def math_inline(renderer, tokens, index, options, env):
        return '<span class="math inline">' + html.escape(tokens[index].content) + '</span>'
    def math_block(renderer, tokens, index, options, env):
        return '<div class="math block">' + html.escape(tokens[index].content) + '</div>\n'
    parser.add_render_rule('math_inline', math_inline)
    parser.add_render_rule('math_block', math_block)
    parser.add_render_rule('math_block_eqno', math_block)
    tokens = parser.parse(text)
    toc, used = [], set()
    title_anchor, heading_shift = '', 1
    def heading_text(inline):
        return ''.join(child.content for child in inline.children or []
                       if child.type in {'text', 'code_inline', 'math_inline'})
    normalize = lambda value: ' '.join(unicodedata.normalize('NFKC', value).split()).casefold()
    if (page_title and len(tokens) >= 3 and tokens[0].type == 'heading_open'
            and tokens[0].tag == 'h1' and normalize(heading_text(tokens[1])) == normalize(page_title)):
        title = heading_text(tokens[1])
        title_anchor = re.sub(r'[^\w-]+', '-', title.casefold()).strip('-') or 'section'
        used.add(title_anchor)
        tokens = tokens[3:]
        heading_shift = 0
    plain = []
    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            inline = tokens[index + 1]
            title = heading_text(inline)
            base = re.sub(r'[^\w-]+', '-', title.casefold()).strip('-') or 'section'
            anchor, count = base, 2
            while anchor in used:
                anchor = f'{base}-{count}'
                count += 1
            used.add(anchor)
            token.attrSet('id', anchor)
            # Page title occupies h1; article headings start at h2.
            level = min(max(int(token.tag[1:]) + heading_shift, 2), 6)
            token.tag = f'h{level}'
            tokens[index + 2].tag = token.tag
            toc.append((level, anchor, title))
        if token.type == 'inline':
            for child in token.children or []:
                if child.type == 'image':
                    if image_handler is None:
                        raise ValueError('图片需要明确的笔记资源目录。')
                    child.attrSet('src', image_handler(child.attrGet('src')))
                    child.attrSet('loading', 'lazy')
                elif child.type == 'link_open':
                    href = child.attrGet('href') or ''
                    parsed = urlsplit(href)
                    if parsed.scheme not in {'', 'https', 'http', 'mailto'} or href.startswith('//'):
                        raise ValueError(f'不支持的链接：{href}')
                    if link_handler:
                        child.attrSet('href', link_handler(href))
            plain.append(token.content)
    rendered = parser.renderer.render(tokens, parser.options, {})
    if title_anchor:
        rendered = '<span class="article-title-anchor" id="' + html.escape(title_anchor, quote=True) + '" aria-hidden="true"></span>' + rendered
    toc_html = ''
    if toc:
        links = ''.join(f'<li class="toc-level-{level}"><a href="#{html.escape(anchor, quote=True)}">{html.escape(title)}</a></li>'
                        for level, anchor, title in toc)
        toc_html = f'<nav class="article-toc" aria-label="文章目录"><details class="toc-disclosure" open><summary>本文目录</summary><ol>{links}</ol></details></nav>'
    return rendered, toc_html, '\n'.join(plain)


def render_markdown(text):
    return markdown_document(text)[0]

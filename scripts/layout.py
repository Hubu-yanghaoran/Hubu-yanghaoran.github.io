"""One layout for homepage, catalogs, and article detail pages."""
import html
import hashlib
import json
from pathlib import Path
from string import Template
from collections import Counter
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parent.parent

def esc(value):
    return html.escape(str(value), quote=True)

def config():
    return json.loads((ROOT / 'site-config.json').read_text(encoding='utf-8'))

def template(filename, **values):
    return Template((ROOT / 'templates' / filename).read_text(encoding='utf-8')).substitute(values)

def asset_url(filename, prefix=''):
    version = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()[:12]
    return prefix + filename + '?v=' + version

def safe_link(url):
    parsed = urlsplit(url)
    if parsed.scheme not in {'', 'https', 'http'} or url.startswith('//'):
        raise ValueError(f'Unsupported public URL: {url}')
    return esc(url)

def entry(item, kind='notes'):
    title = item.get('title') or item.get('name', '')
    href = item.get('url', '')
    heading = f'<a href="{safe_link(href)}">{esc(title)}</a>' if href else esc(title)
    metadata = item.get('engine', '') if kind == 'templates' else ' · '.join(filter(None, [item.get('updated') or item.get('date', ''), item.get('category', '')]))
    tags = ''.join(f'<span class="tag">{esc(tag)}</span>' for tag in item.get('tags', []))
    source = f'<div class="links"><a href="{safe_link(item["source"])}">原作者与项目说明</a></div>' if item.get('source') else ''
    return f'<article class="entry"><h3>{heading}</h3><p>{esc(item.get("description") or item.get("style", ""))}</p><p class="meta">{esc(metadata)}</p><div>{tags}</div>{source}</article>'

def profile(site, prefix=''):
    avatar = site.get('avatar', '')
    if avatar:
        image_url = avatar if urlsplit(avatar).scheme else prefix + avatar
        portrait = f'<img class="profile-avatar" src="{safe_link(image_url)}" alt="{esc(site["name"])}" width="144" height="144">'
    else:
        portrait = '<div class="profile-avatar profile-monogram" aria-hidden="true"><span>YHR</span></div>'
    extra = ''.join(f'<li><span class="profile-symbol" aria-hidden="true">{symbol}</span>{esc(site[field])}</li>'
                    for field, symbol in [('affiliation', '◇'), ('location', '⌖')] if site.get(field))
    email = f'<li><a href="mailto:{esc(site["email"])}"><span class="profile-symbol" aria-hidden="true">✉</span>Email</a></li>' if site.get('email') else ''
    topics = ''.join(f'<li>{esc(topic)}</li>' for topic in site['interests'])
    return f'''<div class="profile-card">{portrait}
<div class="profile-details"><h2 id="profile-name">{esc(site["name"])}</h2>
<p id="profile-subtitle">{esc(site["subtitle"])}</p>
<ul class="profile-links">{extra}{email}<li><a id="profile-github" href="{safe_link(site["github"])}"><span class="profile-symbol" aria-hidden="true">↗</span>GitHub</a></li></ul></div></div>
<div class="profile-directions"><h3>关注方向</h3><ul id="profile-topics">{topics}</ul></div>
<nav class="profile-sections" aria-label="主页章节"><h3>页面索引</h3><a href="{prefix}index.html#about">关于我</a><a href="{prefix}index.html#recent">最近更新</a><a href="{prefix}index.html#resources">推荐工具</a></nav>'''

def render_layout(title, description, main, page='home', prefix='', sidebar=None, head='', scripts='', body_class='', sidebar_label=None):
    site = config()
    nav = []
    for key, label, filename in [('home', '关于我', 'index.html'), ('notes', '学习笔记', 'notes.html'), ('templates', '模板与资源', 'templates.html')]:
        active = ' aria-current="page"' if key == page else ''
        nav.append(f'<a data-page="{key}" href="{prefix}{filename}"{active}>{label}</a>')
    nav.append(f'<a href="{safe_link(site["github"])}">GitHub</a>')
    return template('base.html', title=esc(title), name=esc(site['name']), description=esc(description),
        prefix=prefix, navigation=''.join(nav), sidebar=profile(site, prefix) if sidebar is None else sidebar,
        sidebar_label=sidebar_label or ('个人信息' if sidebar is None else '笔记导航'), main=main,
        page=page, head=head, scripts=scripts, body_class=body_class, stylesheet=asset_url('styles.css', prefix))

def public_pages(notes, resources):
    site = config()
    notes = sorted(notes, key=lambda item: item.get('updated') or item.get('date', ''), reverse=True)
    counts = Counter(item.get('category', '未分类') for item in notes)
    categories = ''.join(f'<a class="topic-link" href="notes.html?{esc(urlencode({"category": category}))}">{esc(category)}<span>{count}</span></a>' for category, count in sorted(counts.items()))
    empty = '<p class="empty">尚未发布公开笔记。</p>'
    home = template('home.html', name=esc(site['name']), bio=''.join(f'<p>{esc(p)}</p>' for p in site['bio']),
        recent=''.join(entry(item) for item in notes[:3]) or empty, categories=categories or empty,
        note_count=len(notes), topic_count=len(counts), resource_count=len(resources),
        publications_hidden='' if site['publications'] else 'hidden',
        publications=''.join(entry(item) for item in site['publications']))
    data_scripts = [('site-config.js', site), ('notes-data.js', notes), ('template-data.js', resources)]
    scripts = ''
    for name, data in data_scripts:
        version = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:12]
        scripts += f'<script src="{name}?v={version}" defer></script>'
    scripts += f'<script src="{asset_url("app.js")}" defer></script>'
    pages = {'index.html': render_layout('个人知识库', 'Yang Haoran 的数学学习笔记、排版工具与公开资料。', home, scripts=scripts)}
    groups = []
    for category, count in sorted(counts.items()):
        body = ''.join(entry(item) for item in notes if item.get('category', '未分类') == category)
        groups.append(f'<details class="note-category"><summary><span class="category-name">{esc(category)}</span><span class="category-count">{count} 篇笔记</span></summary><div class="category-body">{body}</div></details>')
    for kind in ('notes', 'templates'):
        is_notes = kind == 'notes'
        heading = '学习笔记' if is_notes else 'LaTeX 模板与资源'
        featured = '' if is_notes else '<div class="callout"><h2>Lumina 中文适配版</h2><p>支持中英文数学笔记，附编译示例与说明。</p><div class="links"><a href="lumina-guide.html">使用说明</a><a href="lumina-preview.pdf">PDF 预览</a><a href="lumina-xelatex.zip">下载源码</a></div></div>'
        main = template('catalog.html', eyebrow='Learning notes / 学习笔记' if is_notes else 'Resources / 排版资源',
            heading=heading, intro='课程学习、阅读记录与专题整理。按分类浏览，也可搜索标题、摘要和标签。' if is_notes else '整理的第三方模板与自己的适配版本。编译环境以各项目说明为准。',
            featured=featured, search_label='搜索笔记' if is_notes else '搜索模板', category_label='内容分类' if is_notes else '编译环境',
            sort_control='<div class="control"><label for="sort">排序</label><select id="sort"><option value="updated">最近更新</option><option value="date">最新发布</option><option value="title">标题</option></select></div>' if is_notes else '',
            count=f'{len(notes) if is_notes else len(resources)} 项内容', results=(''.join(groups) or empty) if is_notes else ''.join(entry(item, 'templates') for item in resources))
        pages[f'{kind}.html'] = render_layout(heading, heading + '目录与使用资料。', main, page=kind, scripts=scripts)
    guide = (ROOT / 'templates/lumina.html').read_text(encoding='utf-8')
    guide_sections = [('environment', '编译环境'), ('compile', '编译与运行'), ('structure', '文件与修改入口'),
                      ('example', '正文示例'), ('all-environments', '全部环境索引与示例'), ('verification', '验证与限制'), ('attribution', '作者与许可')]
    guide_toc = ''.join(f'<li><a href="#{anchor}">{index:02d} · {label}</a></li>' for index, (anchor, label) in enumerate(guide_sections, 1))
    guide_sidebar = '<h2>排版资源</h2><p>Lumina 中文适配版</p><a href="templates.html">全部模板与资源</a>'
    guide_sidebar += '<nav class="article-toc" aria-label="说明目录"><details class="toc-disclosure" open><summary>本文目录</summary><ol>' + guide_toc + '</ol></details></nav>'
    pages['lumina-guide.html'] = render_layout('Lumina 中文版使用说明', 'Lumina XeLaTeX 中文适配版下载与使用说明。', guide, page='templates', sidebar=guide_sidebar, body_class='article-page', sidebar_label='排版导航', scripts=f'<script src="{asset_url("reader.js")}" defer></script>')
    return pages

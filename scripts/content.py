"""One note schema and one detail renderer for files and multi-file collections."""
import html
import json
import re
import datetime
from pathlib import Path
from urllib.parse import quote, urlsplit

from markdown_reader import render_markdown, markdown_document, local_resource

def validate_item(item):
    for field in ('category', 'description', 'main', 'author', 'license', 'engine', 'repository', 'document_title'):
        if field in item and not isinstance(item[field], str):
            raise ValueError(f'{field} 必须是字符串')
    for field in ('tags', 'instructions', 'legacy_sources'):
        if field in item and (not isinstance(item[field], list) or not all(isinstance(v, str) for v in item[field])):
            raise ValueError(f'{field} 必须是字符串数组')
    for field in ('date', 'updated'):
        value = item.get(field, '')
        if not isinstance(value, str):
            raise ValueError(f'{field} 必须是 YYYY-MM-DD 字符串')
        if value:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError(f'{field} 日期格式应为 YYYY-MM-DD')
            datetime.date.fromisoformat(value)

def detail_page(item, resources, prefix="../../"):
    esc = lambda value: html.escape(str(value), quote=True)
    main = item.get("main", "")
    links, files, body, toc = [], [], "", ""
    pdfs = []
    for resource in resources:
        url, label = resource["url"], resource["label"]
        url = prefix + url if not urlsplit(url).scheme else url
        if Path(resource.get("file", "")).suffix.lower() == '.pdf':
            pdfs.append((resource, url))
        if resource.get("file") == main:
            if "markdown" in resource:
                links.append('<a href="#note-body">阅读主文档</a>')
                rendered, toc, _ = markdown_document(resource["markdown"], resource.get("image_handler"), resource.get("link_handler"), item.get('document_title', item['title']))
                body = '<section id="note-body" class="section note-body" aria-label="笔记正文">' + rendered + '</section>'
            elif Path(main).suffix.lower() == '.pdf':
                links.append('<a href="#pdf-reader">在线阅读</a>')
                links.append(f'<a href="{esc(url)}" download>下载 PDF</a>')
            else:
                links.append(f'<a href="{esc(url)}">阅读主文档</a>')
        files.append(f'<li><a href="{esc(url)}">{esc(label)}</a></li>')
    if item.get("repository"):
        url = item["repository"]
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("repository must use HTTPS")
        links.append(f'<a href="{esc(url)}">项目仓库</a>')
    paragraphs = item.get("instructions", [])
    if not isinstance(paragraphs, list):
        raise ValueError("instructions must be an array")
    sections = body
    if pdfs:
        selected, selected_url = next(((r, u) for r, u in pdfs if r.get('file') == main), pdfs[0])
        viewer_url = lambda resource: prefix + 'assets/pdfjs/viewer.html?file=' + quote('../../' + resource['url'], safe='')
        choices = ''.join(
            f'<a class="pdf-choice" href="{esc(u)}" data-pdf-url="{esc(u)}" data-viewer-url="{esc(viewer_url(r))}"'
            f' aria-current="{"true" if r is selected else "false"}">{esc(r["label"])}</a>'
            for r, u in pdfs)
        sections += f'''<section id="pdf-reader" class="pdf-reader section" aria-labelledby="pdf-heading">
<div class="reader-heading"><div><div class="eyebrow">READING ROOM / 在线阅读</div><h2 id="pdf-heading">留在这里，读完这一篇。</h2></div><span class="reader-format">PDF</span></div>
<nav class="pdf-choices" aria-label="选择阅读文档">{choices}</nav>
<div class="pdf-toolbar"><span id="pdf-current" role="status">{esc(selected['label'])}</span><div class="reader-actions">
<a id="pdf-open" href="{esc(selected_url)}" target="_blank" rel="noopener">独立窗口 ↗</a>
<a id="pdf-download" href="{esc(selected_url)}" download>下载</a>
<button id="pdf-expand" type="button" aria-pressed="false" hidden>展开阅读</button></div></div>
<iframe id="pdf-frame" class="pdf-frame" src="{esc(viewer_url(selected))}" title="{esc(selected['label'])}在线预览" allow="fullscreen"></iframe>
<p class="pdf-help">可在预览中滚动、缩放。若浏览器未显示 PDF，请选择“独立窗口”或下载阅读。</p>
</section>'''
    if files:
        sections += '<section class="section"><h2 class="section-title">文档与附件</h2><ul>' + "".join(files) + "</ul></section>"
    if item.get("engine") or paragraphs:
        sections += '<section class="section"><h2 class="section-title">环境与使用说明</h2>'
        if item.get("engine"):
            sections += f'<p>编译环境：{esc(item["engine"])}</p>'
        sections += "".join(f"<p>{esc(p)}</p>" for p in paragraphs) + "</section>"
    if item.get("author") or item.get("license"):
        sections += f'<section class="section"><h2 class="section-title">作者与许可</h2><p>{esc(item.get("author", ""))}</p><p>{esc(item.get("license", ""))}</p></section>'
    from layout import render_layout, asset_url
    heading = f'<header class="document-header"><div class="eyebrow">Learning notes / 学习笔记</div><h1>{esc(item["title"])}</h1><p class="lead">{esc(item.get("description", ""))}</p>'
    dates = '发布：' + esc(item.get('date', ''))
    if item.get('updated'):
        dates += ' · 更新：' + esc(item['updated'])
    heading += f'<p class="meta">{dates}</p><div class="links">{"".join(links)}</div></header>'
    sidebar = f'<h2>学习笔记</h2><p>{esc(item.get("category", "学习笔记"))}</p><a href="{prefix}notes.html">全部笔记</a>{toc}'
    head = f'<link rel="stylesheet" href="{prefix}assets/katex/katex.min.css"><script src="{prefix}assets/katex/katex.min.js" defer></script>' if body else ''
    scripts = f'<script src="{asset_url("reader.js", prefix)}" defer></script>'
    return render_layout(item['title'], item.get('description', ''), heading + sections,
                         page='notes', prefix=prefix, sidebar=sidebar, head=head, scripts=scripts,
                         body_class='article-page pdf-page' if pdfs else 'article-page')


def collect_content(root):
    entries, copies, pages, migrated = [], {}, {}, set()
    directory = root / "content"
    if not directory.exists():
        return entries, copies, pages, migrated
    if directory.is_symlink():
        raise ValueError("content cannot be a symlink")
    for folder in sorted(directory.iterdir()):
        if not folder.is_dir():
            continue
        if folder.is_symlink() or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", folder.name):
            raise ValueError(f"Use ASCII letters/numbers/hyphens for note directory: {folder.name}")
        manifest = folder / "note.json"
        if not manifest.exists():
            print(f"Skipping note without note.json: {folder.name}")
            continue
        if manifest.is_symlink():
            raise ValueError("note.json cannot be a symlink")
        item = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(item, dict) or not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError(f"Missing title: {manifest}")
        validate_item(item)
        attachments = item.get("attachments", [])
        if not isinstance(attachments, list):
            raise ValueError("attachments must be an array")
        resources, seen = [], set()
        for attachment in attachments:
            if not isinstance(attachment, dict) or 'file' not in attachment:
                raise ValueError('附件必须是包含 file 的对象')
            if 'label' in attachment and not isinstance(attachment['label'], str):
                raise ValueError('附件 label 必须是字符串')
            value = attachment["file"]
            if not isinstance(value, str) or not value or "\\" in value or Path(value).is_absolute() or ".." in Path(value).parts:
                raise ValueError(f"Unsafe attachment: {value}")
            path = folder / value
            if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()) or not path.is_file():
                raise ValueError(f"Missing/unsafe attachment: {value}")
            # Do not serve active HTML/JS as note attachments on the website origin.
            if path.suffix.lower() not in {".pdf", ".zip", ".txt", ".md", ".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                raise ValueError(f"Unsupported attachment; package source code into ZIP: {value}")
            if value in seen:
                raise ValueError(f"Duplicate attachment: {value}")
            seen.add(value)
            relative = path.relative_to(root).as_posix()
            copies[relative] = path
            resources.append({"file": value, "label": attachment.get("label", path.name), "url": quote(relative, safe="/")})
            if path.suffix.lower() == ".md" and value == item.get("main"):
                resources[-1]["markdown"] = path.read_text(encoding="utf-8-sig")
                def image_handler(value, source=path, note_folder=folder):
                    image = local_resource(value, source, note_folder)
                    copies[image.relative_to(root).as_posix()] = image
                    return quote(image.relative_to(note_folder).as_posix(), safe="/")
                def link_handler(value, source=path, note_folder=folder):
                    parsed = urlsplit(value)
                    if parsed.scheme or parsed.netloc or value.startswith("#"):
                        return value
                    from urllib.parse import unquote
                    destination = (source.parent / unquote(parsed.path)).resolve()
                    if not destination.is_relative_to(note_folder.resolve()):
                        raise ValueError(f"链接越出笔记目录：{value}")
                    name = destination.relative_to(note_folder).as_posix()
                    if name not in seen and name not in {a["file"] for a in attachments}:
                        raise ValueError(f"本地链接必须引用已登记的附件：{value}")
                    return quote(name, safe="/") + ("#" + quote(parsed.fragment) if parsed.fragment else "")
                resources[-1]["image_handler"] = image_handler
                resources[-1]["link_handler"] = link_handler
        if item.get("main") and item["main"] not in seen:
            raise ValueError("main must reference a listed attachment")
        if not resources and not item.get("repository"):
            raise ValueError("A note needs attachments or a repository URL")
        sources = item.get("legacy_sources", [])
        if not isinstance(sources, list) or not all(isinstance(s, str) for s in sources):
            raise ValueError("legacy_sources must be an array of strings")
        migrated.update(sources)
        url = f"content/{folder.name}/index.html"
        entries.append({"title": item["title"], "description": item.get("description", ""),
                        "category": item.get("category", "学习笔记"), "date": item.get("date", ""),
                        "updated": item.get("updated", item.get("date", "")),
                        "tags": item.get("tags", []), "format": Path(item.get('main', '')).suffix.lstrip('.').upper(),
                        "kind": "note", "url": url})
        pages[url] = detail_page(item, resources)
    return entries, copies, pages, migrated

"""One note schema and one detail renderer for files and multi-file collections."""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

def detail_page(item, resources, prefix="../../"):
    esc = lambda value: html.escape(str(value), quote=True)
    main = item.get("main", "")
    links, files = [], []
    for resource in resources:
        url, label = resource["url"], resource["label"]
        url = prefix + url if not urlsplit(url).scheme else url
        if resource.get("file") == main:
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
    sections = ""
    if files:
        sections += '<section class="section"><h2 class="section-title">文档与附件</h2><ul>' + "".join(files) + "</ul></section>"
    if item.get("engine") or paragraphs:
        sections += '<section class="section"><h2 class="section-title">环境与使用说明</h2>'
        if item.get("engine"):
            sections += f'<p>编译环境：{esc(item["engine"])}</p>'
        sections += "".join(f"<p>{esc(p)}</p>" for p in paragraphs) + "</section>"
    if item.get("author") or item.get("license"):
        sections += f'<section class="section"><h2 class="section-title">作者与许可</h2><p>{esc(item.get("author", ""))}</p><p>{esc(item.get("license", ""))}</p></section>'
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(item["title"])} · 学习笔记</title><link rel="stylesheet" href="{prefix}styles.css"></head><body><header><div class="masthead"><a class="brand" href="{prefix}index.html">Yang Haoran</a><nav class="nav"><a href="{prefix}notes.html">返回学习笔记</a><a href="{prefix}templates.html">LaTeX 模板</a></nav></div></header><div class="layout"><aside class="sidebar"><div class="identity" aria-hidden="true">YHR</div><h2>学习笔记</h2><p>{esc(item.get("category", "学习笔记"))}</p><a href="{prefix}notes.html">全部笔记</a></aside><main><div class="eyebrow">Learning notes / 学习笔记</div><h1>{esc(item["title"])}</h1><p class="lead">{esc(item.get("description", ""))}</p><p class="meta">{esc(item.get("date", ""))}</p><div class="links">{"".join(links)}</div>{sections}</main></div><footer>公开学习资料 · 请遵循作者许可</footer></body></html>"""

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
        attachments = item.get("attachments", [])
        if not isinstance(attachments, list):
            raise ValueError("attachments must be an array")
        resources, seen = [], set()
        for attachment in attachments:
            value = attachment["file"]
            if not isinstance(value, str) or not value or "\\" in value or Path(value).is_absolute() or ".." in Path(value).parts:
                raise ValueError(f"Unsafe attachment: {value}")
            path = folder / value
            if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()) or not path.is_file():
                raise ValueError(f"Missing/unsafe attachment: {value}")
            # Do not serve active HTML/JS as note attachments on the website origin.
            if path.suffix.lower() not in {".pdf", ".zip", ".txt", ".md", ".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError(f"Unsupported attachment; package source code into ZIP: {value}")
            if value in seen:
                raise ValueError(f"Duplicate attachment: {value}")
            seen.add(value)
            relative = path.relative_to(root).as_posix()
            copies[relative] = path
            resources.append({"file": value, "label": attachment.get("label", path.name), "url": quote(relative, safe="/")})
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
                        "tags": item.get("tags", []), "kind": "note", "url": url})
        pages[url] = detail_page(item, resources)
    return entries, copies, pages, migrated

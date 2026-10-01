"""Adapt legacy project.json to the shared note renderer without moving files."""
import json
import re
from pathlib import Path
from urllib.parse import quote
from content import detail_page


def collect_projects(root):
    entries, copies, pages = [], {}, {}
    projects = root / "projects"
    if not projects.exists():
        return entries, copies, pages
    if projects.is_symlink():
        raise ValueError("projects cannot be a symlink")
    for folder in sorted(projects.iterdir()):
        if not folder.is_dir():
            continue
        if folder.is_symlink() or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", folder.name):
            raise ValueError(f"Unsafe project directory: {folder.name}")
        manifest = folder / "project.json"
        if not manifest.is_file():
            print(f"Skipping unconfigured project: {folder.name}")
            continue
        if manifest.is_symlink():
            raise ValueError("Project manifest cannot be a symlink")
        item = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(item, dict) or not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError(f"Project title required: {manifest}")
        resources = []

        def resource(value, extension, label):
            if not isinstance(value, str) or not value or "\\" in value or Path(value).is_absolute() or ".." in Path(value).parts:
                raise ValueError(f"Unsafe resource path: {value!r}")
            path = folder / value
            if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()) or not path.is_file() or path.suffix.lower() != extension:
                raise ValueError(f"Missing/unsafe project resource: {value}")
            relative = path.relative_to(root).as_posix()
            copies[relative] = path
            resources.append({"file": value, "label": label, "url": quote(relative, safe="/")})

        for key, label, extension in [("main_pdf", "主文档 PDF", ".pdf"), ("source_zip", "源码 ZIP", ".zip")]:
            if item.get(key):
                resource(item[key], extension, label)
        for chapter in item.get("chapters", []):
            resource(chapter["file"], ".pdf", chapter["title"])
        if not resources and not item.get("repository"):
            raise ValueError(f"Project needs at least one resource: {folder.name}")
        url = f"projects/{folder.name}/index.html"
        entries.append({"title": item["title"], "description": item.get("description", ""),
                        "category": item.get("category", "学习笔记"), "date": item.get("date", ""),
                        "tags": item.get("tags", []), "kind": "note", "url": url})
        pages[url] = detail_page(dict(item, main=item.get("main_pdf", "")), resources)
    return entries, copies, pages

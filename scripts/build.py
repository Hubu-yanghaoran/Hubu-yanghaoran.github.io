"""Build a static site and derive a public notes index using standard Python."""
import json
import hashlib
import shutil
from pathlib import Path
from urllib.parse import quote
from projects import collect_projects
from content import collect_content, detail_page
from layout import public_pages, config

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_site"
metadata_path = ROOT / "notes-metadata.json"
metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
notes = []
unified_entries, unified_files, unified_pages, migrated_sources = collect_content(ROOT)
legacy_note_pages = {}
for path in sorted((ROOT / "notes").rglob("*.pdf")):
    if path.is_symlink() or not path.resolve().is_relative_to((ROOT / "notes").resolve()):
        raise ValueError(f"Unsafe note path: {path}")
    relative = path.relative_to(ROOT).as_posix()
    item = metadata.get(relative, {})
    if relative in migrated_sources:
        continue
    detail_url = "legacy-notes/" + hashlib.sha256(relative.encode("utf-8")).hexdigest()[:20] + ".html"
    note_item = {
        "title": item.get("title", path.stem.replace("-", " ").replace("_", " ")),
        "description": item.get("description", "公开学习笔记 · PDF"),
        "category": item.get("category", "学习笔记"),
        "date": item.get("date", ""),
        "tags": item.get("tags", []),
        "url": detail_url,
        "kind": "note",
    }
    notes.append(note_item)
    note_detail = dict(note_item, main=relative)
    depth = len(Path(detail_url).parts) - 1
    legacy_note_pages[detail_url] = detail_page(note_detail, [{"file": relative, "label": "阅读 PDF", "url": quote(relative, safe="/")}], "../" * depth)
for manifest in (ROOT / "notes").rglob("project.json"):
    raise ValueError(f"Move project folder from notes/ to projects/: {manifest}")
project_entries, project_files, project_pages = collect_projects(ROOT)
notes.extend(item for item in project_entries if item["url"] not in migrated_sources)
notes.extend(unified_entries)
project_files.update(unified_files)
project_pages.update(legacy_note_pages)
project_pages.update(unified_pages)
required = ["styles.css", "app.js", "reader.js",
            "lumina-preview.pdf", "lumina-xelatex.zip"]
for name in required:
    if not (ROOT / name).is_file():
        raise FileNotFoundError(name)
if OUTPUT.is_symlink() or OUTPUT.resolve() != ROOT.resolve() / "_site":
    raise RuntimeError("Unsafe output directory")
if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
OUTPUT.mkdir()
for name in required:
    shutil.copy2(ROOT / name, OUTPUT / name)
shutil.copytree(ROOT / 'assets', OUTPUT / 'assets')
for path in sorted((ROOT / "notes").rglob("*.pdf")):
    destination = OUTPUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
for relative, path in project_files.items():
    destination = OUTPUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
for relative, content in project_pages.items():
    destination = OUTPUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
(OUTPUT / "notes-data.js").write_text("window.NOTES = " + json.dumps(notes, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
(OUTPUT / 'site-config.js').write_text('window.SITE = ' + json.dumps(config(), ensure_ascii=False) + ';\n', encoding='utf-8')
resources = json.loads((ROOT / 'template-data.json').read_text(encoding='utf-8'))
(OUTPUT / 'template-data.js').write_text('window.TEMPLATES = ' + json.dumps(resources, ensure_ascii=False) + ';\n', encoding='utf-8')
for name, page in public_pages(notes, resources).items():
    (OUTPUT / name).write_text(page, encoding='utf-8')
(OUTPUT / ".nojekyll").touch()
print(f"Built {len(notes)} entries and {len(project_pages)} detail pages in {OUTPUT}")

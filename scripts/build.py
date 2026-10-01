"""Build a static site and derive a public notes index using standard Python."""
import json
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_site"
metadata_path = ROOT / "notes-metadata.json"
metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
notes = []
for path in sorted((ROOT / "notes").rglob("*.pdf")):
    relative = path.relative_to(ROOT).as_posix()
    item = metadata.get(relative, {})
    notes.append({
        "title": item.get("title", path.stem.replace("-", " ").replace("_", " ")),
        "description": item.get("description", "公开学习笔记 · PDF"),
        "category": item.get("category", "学习笔记"),
        "date": item.get("date", ""),
        "tags": item.get("tags", []),
        "url": quote(relative, safe="/"),
    })
required = ["index.html", "notes.html", "templates.html", "lumina-guide.html",
            "styles.css", "app.js", "site-config.js", "template-data.js",
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
for path in sorted((ROOT / "notes").rglob("*.pdf")):
    destination = OUTPUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
(OUTPUT / "notes-data.js").write_text("window.NOTES = " + json.dumps(notes, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
(OUTPUT / ".nojekyll").touch()
print(f"Built {len(notes)} public PDF notes in {OUTPUT}")

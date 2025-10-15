#!/usr/bin/env python3
"""Generate gallery table in README.md from images under wallpapers/.

Usage: python scripts/generate_readme_gallery.py

Behavior:
- Scans the 'wallpapers' directory for image files (jpg,jpeg,png,gif,webp).
- For each image, looks for an optional JSON metadata file with the same basename and extension '.json'
  (e.g. 'photo.jpg' -> 'photo.jpg.json') containing {"name": "...", "author": "..."}.
- If no metadata is found, uses the filename as Name and 'Unknown' as Author.
- Replaces the Gallery table in README.md between markers <!-- GALLERY_START --> and <!-- GALLERY_END -->.

This is safe to run repeatedly and intended to be used before committing changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
WALLPAPERS_DIR = ROOT / "wallpapers"
README_PATH = ROOT / "README.md"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def find_images() -> List[Path]:
    files: List[Path] = []
    for p in WALLPAPERS_DIR.rglob("*"):
        if p.suffix.lower() in IMAGE_EXTS and p.is_file():
            files.append(p)
    files.sort()
    return files


def read_metadata(img: Path) -> Tuple[str, str]:
    meta_path = img.with_name(img.name + ".json")
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            name = data.get("name") or img.stem
            author = data.get("author") or "Unknown"
            return name, author
        except Exception:
            pass
    # default
    return img.name, "Unknown"


def md_row(img: Path, name: str, author: str) -> str:
    rel = img.relative_to(ROOT)
    # URL-encode the path for Markdown links (spaces, parentheses, etc.)
    # normalize to forward slashes so GitHub paths work on all platforms
    rel_str = str(rel).replace("\\", "/")
    # keep forward slashes safe so they are not percent-encoded
    rel_quoted = quote(rel_str, safe="/")
    alt = name.replace("|", "\u2014")
    return f"| ![{alt}]({rel_quoted}) | {name} | {author} | [Repo link]({rel_quoted}) |"


def build_table(rows: List[str]) -> str:
    header = "| Preview | Name | Author | Link |\n|---:|:---|:---|:---|"
    return header + "\n" + "\n".join(rows)


def replace_gallery_in_readme(new_table_md: str) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    start_marker = "<!-- GALLERY_START -->"
    end_marker = "<!-- GALLERY_END -->"
    if start_marker in text and end_marker in text:
        before, rest = text.split(start_marker, 1)
        _, after = rest.split(end_marker, 1)
        new_text = before + start_marker + "\n\n" + new_table_md + "\n\n" + end_marker + after
    else:
        # Append markers and table at end
        new_text = text.rstrip() + "\n\n" + start_marker + "\n\n" + new_table_md + "\n\n" + end_marker + "\n"
    README_PATH.write_text(new_text, encoding="utf-8")


def main() -> int:
    images = find_images()
    rows: List[str] = []
    for img in images:
        name, author = read_metadata(img)
        rows.append(md_row(img, name, author))

    table_md = build_table(rows)
    replace_gallery_in_readme(table_md)
    print(f"Updated {README_PATH} with {len(rows)} images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

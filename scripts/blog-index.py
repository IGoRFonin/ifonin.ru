#!/usr/bin/env python3
"""
Управление двухуровневым индексом блога ifonin.ru.

Подкоманды:
  update  - пересобрать .blog-index.json из front matter постов
  add     - добавить запись в .blog-index.json и .blog-summaries.json
  query   - вывести саммари для конкретных slugs
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / ".blog-index.json"
SUMMARIES_PATH = ROOT / ".blog-summaries.json"
BLOG_DIR = ROOT / "content" / "blog"


def parse_frontmatter(text: str) -> dict:
    """Парсит YAML front matter из markdown-файла (без PyYAML)."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        # Убираем кавычки
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        # Парсим массив тегов: ["a", "b", "c"]
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1]
            tags = []
            for t in inner.split(","):
                t = t.strip().strip('"').strip("'")
                if t:
                    tags.append(t)
            val = tags
        fm[key] = val
    return fm


def load_json(path: Path) -> list | dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return [] if path == INDEX_PATH else {}


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_update(_args):
    """Пересобрать .blog-index.json из front matter постов в content/blog/."""
    entries = []
    for md in sorted(BLOG_DIR.glob("*.md")):
        if md.name == "_index.md":
            continue
        fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        if not fm.get("slug"):
            fm["slug"] = md.stem
        entry = {
            "slug": fm.get("slug", md.stem),
            "title": fm.get("title", ""),
            "date": fm.get("date", ""),
            "tags": fm.get("tags", []),
        }
        entries.append(entry)
    # Сортировка по дате (новые первыми)
    entries.sort(key=lambda e: e["date"], reverse=True)
    save_json(INDEX_PATH, entries)
    print(json.dumps({"status": "ok", "count": len(entries), "file": str(INDEX_PATH)}, ensure_ascii=False))


def cmd_add(args):
    """Добавить запись в .blog-index.json и .blog-summaries.json."""
    index = load_json(INDEX_PATH)
    summaries = load_json(SUMMARIES_PATH)

    slug = args.slug
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    # Обновить или добавить в индексе
    existing = next((e for e in index if e["slug"] == slug), None)
    entry = {
        "slug": slug,
        "title": args.title or (existing["title"] if existing else ""),
        "date": args.date or (existing["date"] if existing else ""),
        "tags": tags or (existing["tags"] if existing else []),
    }
    if existing:
        index = [entry if e["slug"] == slug else e for e in index]
    else:
        index.append(entry)

    # Сортировка по дате (новые первыми)
    index.sort(key=lambda e: e["date"], reverse=True)
    save_json(INDEX_PATH, index)

    # Обновить саммари
    if args.summary:
        summaries[slug] = args.summary
        save_json(SUMMARIES_PATH, summaries)

    print(json.dumps({"status": "ok", "slug": slug}, ensure_ascii=False))


def cmd_query(args):
    """Вывести саммари для конкретных slugs."""
    summaries = load_json(SUMMARIES_PATH)
    slugs = [s.strip() for s in args.slugs.split(",")]
    for slug in slugs:
        if slug in summaries:
            print(f"{slug}: {summaries[slug]}")
        else:
            print(f"{slug}: (саммари не найдено)")


def main():
    parser = argparse.ArgumentParser(description="Управление индексом блога ifonin.ru")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("update", help="Пересобрать .blog-index.json из front matter")

    add_p = sub.add_parser("add", help="Добавить запись в индекс и саммари")
    add_p.add_argument("--slug", required=True)
    add_p.add_argument("--title", default="")
    add_p.add_argument("--date", default="")
    add_p.add_argument("--tags", default="")
    add_p.add_argument("--summary", default="")

    query_p = sub.add_parser("query", help="Вывести саммари для slugs")
    query_p.add_argument("--slugs", required=True, help="slug1,slug2,slug3")

    args = parser.parse_args()
    if args.command == "update":
        cmd_update(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "query":
        cmd_query(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate web/data/<lang>.json from a language folder's markdown.

Markdown is the human source of truth (readable, diffable). The web UI reads
JSON. Run this after editing a language folder's markdown:

    python3 scripts/build_data.py zh-tw

Writes web/data/<lang>.json (vocab + grammar patterns).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_vocab(md: str):
    rows = []
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        rows.append({
            "rank": int(cells[0]),
            "word": cells[1],
            "pinyin": cells[2],
            "meaning": cells[3],
            "example": cells[4],
        })
    return rows


def parse_patterns(md: str):
    patterns = []
    blocks = re.split(r"^###\s+", md, flags=re.M)[1:]
    for block in blocks:
        lines = block.splitlines()
        header = lines[0].strip()
        m = re.match(r"(\d+)\.\s+(.*)", header)
        num = int(m.group(1)) if m else len(patterns) + 1
        name = m.group(2).strip() if m else header
        body = lines[1:]
        does = structure = ""
        examples = []
        in_examples = False
        for ln in body:
            if "**Examples:**" in ln:
                in_examples = True
                continue
            if "**Status:**" in ln:
                in_examples = False
                continue
            md_does = re.search(r"\*\*Does:\*\*\s*(.+)", ln)
            if md_does:
                does = md_does.group(1).strip()
                continue
            md_st = re.search(r"\*\*Structure:\*\*\s*(.+)", ln)
            if md_st:
                structure = md_st.group(1).strip()
                continue
            if in_examples and re.match(r"^\s+-\s+", ln):
                examples.append(re.sub(r"^\s+-\s+", "", ln).strip())
        patterns.append({
            "n": num,
            "name": name,
            "does": does,
            "structure": structure,
            "examples": examples,
        })
    return patterns


def build(lang: str):
    folder = ROOT / lang
    if not folder.is_dir():
        sys.exit(f"no such language folder: {lang}")

    vocab_md = (folder / "vocab-frequency.md").read_text(encoding="utf-8")
    grammar_md = (folder / "grammar-patterns.md").read_text(encoding="utf-8")

    # Title from the language README's first heading, e.g. "zh-tw — Traditional Chinese (Taiwan)"
    readme = (folder / "README.md").read_text(encoding="utf-8")
    title = readme.splitlines()[0].lstrip("# ").strip()

    data = {
        "language": lang,
        "title": title,
        "vocab": parse_vocab(vocab_md),
        "patterns": parse_patterns(grammar_md),
    }

    out_dir = ROOT / "web" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{lang}.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    # Index of available languages for the app
    avail = sorted(p.stem for p in out_dir.glob("*.json"))
    (out_dir / "index.json").write_text(
        json.dumps({"languages": avail}, indent=1), encoding="utf-8")

    print(f"wrote {out.relative_to(ROOT)}: {len(data['vocab'])} words, "
          f"{len(data['patterns'])} patterns")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "zh-tw")

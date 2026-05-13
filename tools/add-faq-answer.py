#!/usr/bin/env python3
"""Add an approved answer to the Better Beds FAQ widget knowledge base.

Usage:
  tools/add-faq-answer.py "Question?" "Approved answer." "keyword one, keyword two"
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "faq-knowledge.json"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:60] or "custom-answer"


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    question = sys.argv[1].strip()
    answer = sys.argv[2].strip()
    keywords = []
    if len(sys.argv) >= 4:
        keywords = [item.strip() for item in sys.argv[3].split(",") if item.strip()]
    if not keywords:
        keywords = [word for word in re.split(r"\W+", question.lower()) if len(word) > 3][:8]

    data = json.loads(KB_PATH.read_text())
    existing_ids = {entry.get("id") for entry in data.get("entries", [])}
    base_id = slugify(question)
    entry_id = base_id
    counter = 2
    while entry_id in existing_ids:
        entry_id = f"{base_id}-{counter}"
        counter += 1

    data.setdefault("entries", []).append({
        "id": entry_id,
        "question": question,
        "keywords": keywords,
        "answer": answer,
    })

    KB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Added FAQ answer: {entry_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

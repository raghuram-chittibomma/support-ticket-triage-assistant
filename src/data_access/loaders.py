"""File-based loaders for the synthetic data under data/. See ARCHITECTURE.md."""

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def load_products() -> list[dict[str, Any]]:
    """Load the synthetic NorthPeak Audioworks product catalog."""
    with open(DATA_DIR / "sample" / "products.json", encoding="utf-8") as f:
        return json.load(f)


def load_sample_tickets() -> list[dict[str, Any]]:
    """Load the synthetic sample tickets, including eval ground-truth fields."""
    with open(DATA_DIR / "sample" / "tickets.json", encoding="utf-8") as f:
        return json.load(f)


def load_knowledge_base() -> list[dict[str, Any]]:
    """Load every synthetic knowledge-base article under data/knowledge_base/."""
    kb_dir = DATA_DIR / "knowledge_base"
    articles = []
    for path in sorted(kb_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            articles.append(json.load(f))
    return articles

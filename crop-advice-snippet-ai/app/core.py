"""Core milestone functions for Crop Advice Snippet AI."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "agriculture.jsonl"
REQUIRED_FIELDS = ("id", "crop", "topic", "text", "source_name", "source_url")


def load_agricultural_corpus(data_path: str | Path | None = None) -> list[dict[str, str]]:
    """Load and validate the project's JSONL agricultural advice corpus.

    Each non-empty line must be a JSON object with id, crop, topic, text,
    source_name and source_url fields. Duplicate IDs are rejected.
    """
    path = Path(data_path) if data_path is not None else DEFAULT_DATA_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"Agricultural dataset not found: {path}. "
            "Expected data/raw/agriculture.jsonl."
        )

    records: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as dataset_file:
        for line_number, raw_line in enumerate(dataset_file, start=1):
            if not raw_line.strip():
                continue
            try:
                item: Any = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"Line {line_number} must contain a JSON object.")
            missing = [field for field in REQUIRED_FIELDS if not isinstance(item.get(field), str) or not item[field].strip()]
            if missing:
                raise ValueError(f"Line {line_number} is missing non-empty string fields: {', '.join(missing)}")
            record = {field: item[field].strip() for field in REQUIRED_FIELDS}
            record["crop"] = record["crop"].lower()
            record["topic"] = record["topic"].lower()
            if record["id"] in seen_ids:
                raise ValueError(f"Duplicate record id on line {line_number}: {record['id']}")
            seen_ids.add(record["id"])
            records.append(record)

    if not records:
        raise ValueError(f"The agricultural dataset is empty: {path}")
    return records


def milestone_1(data_path: str | Path | None = None) -> list[dict[str, str]]:
    """Milestone 1: collect/load a small, source-attributed advice corpus."""
    return load_agricultural_corpus(data_path)


# Milestones 2-6 will be implemented after the corpus is verified.
def milestone_2():
    raise NotImplementedError("TODO(milestone 2): BPE tokenizer and embeddings")


def milestone_3():
    raise NotImplementedError("TODO(milestone 3): causal self-attention and transformer block")


def milestone_4():
    raise NotImplementedError("TODO(milestone 4): GPT training loop")


def milestone_5():
    raise NotImplementedError("TODO(milestone 5): text generation")


def milestone_6():
    raise NotImplementedError("TODO(milestone 6): farmer CLI")

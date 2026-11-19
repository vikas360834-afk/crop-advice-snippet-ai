"""Tests for the Crop Advice Snippet AI milestones."""
import json
from pathlib import Path

import pytest

from app.core import load_agricultural_corpus, milestone_1


def test_milestone_1_loads_source_attributed_corpus():
    records = milestone_1()
    assert len(records) >= 15
    assert {"rice", "maize", "wheat", "tomato"}.issubset({r["crop"] for r in records})
    assert all(r["text"] and r["source_url"].startswith("https://") for r in records)


def test_milestone_1_rejects_duplicate_ids(tmp_path: Path):
    row = {"id":"same", "crop":"rice", "topic":"water", "text":"Advice text", "source_name":"Example", "source_url":"https://example.org"}
    path = tmp_path / "duplicate.jsonl"
    path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate record id"):
        load_agricultural_corpus(path)


def test_milestone_1_rejects_missing_fields(tmp_path: Path):
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"id":"x", "crop":"rice"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing non-empty string fields"):
        load_agricultural_corpus(path)


@pytest.mark.skip(reason="start milestone 2 after milestone 1 is verified")
def test_milestone_2():
    raise NotImplementedError


@pytest.mark.skip(reason="start milestone 3 after milestone 2 is verified")
def test_milestone_3():
    raise NotImplementedError


@pytest.mark.skip(reason="start milestone 4 after milestone 3 is verified")
def test_milestone_4():
    raise NotImplementedError


@pytest.mark.skip(reason="start milestone 5 after milestone 4 is verified")
def test_milestone_5():
    raise NotImplementedError


@pytest.mark.skip(reason="start milestone 6 after milestone 5 is verified")
def test_milestone_6():
    raise NotImplementedError

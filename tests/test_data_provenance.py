"""Tests for source attribution and metadata quality of the bundled JSONL corpus."""

from pathlib import Path

from tools.validate_source_dataset import DEFAULT_DATASET, audit_dataset


def test_bundled_source_dataset_has_complete_attribution():
    report = audit_dataset(DEFAULT_DATASET)

    assert report["errors"] == []
    assert report["record_count"] == 20
    assert report["crop_counts"] == {"maize": 5, "rice": 5, "tomato": 5, "wheat": 5}
    assert report["missing_source_urls"] == 0
    assert report["duplicate_ids"] == []


def test_missing_publication_dates_are_reported_without_invention(tmp_path: Path):
    dataset = tmp_path / "sample.jsonl"
    dataset.write_text(
        '{"id":"sample-1","crop":"rice","topic":"irrigation","text":"Use local guidance.",'
        '"source_name":"TNAU Agritech","source_url":"https://agritech.tnau.ac.in/example.html"}\n',
        encoding="utf-8",
    )

    report = audit_dataset(dataset)

    assert report["errors"] == []
    assert report["missing_publication_dates"] == 1

"""Validate source metadata for the checked-in agricultural JSONL dataset."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "data" / "raw" / "agriculture.jsonl"
REQUIRED_FIELDS = ("id", "crop", "topic", "text", "source_name", "source_url")


def audit_dataset(path: Path | str = DEFAULT_DATASET) -> dict[str, Any]:
    """Return a reproducible metadata audit; missing dates are reported, not guessed."""
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, raw_line in enumerate(dataset_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON ({exc.msg})")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {line_number}: each JSONL row must be an object")
            continue
        missing = [field for field in REQUIRED_FIELDS if not str(record.get(field, "")).strip()]
        if missing:
            errors.append(f"line {line_number}: missing required fields: {', '.join(missing)}")
            continue
        parsed_url = urlparse(str(record["source_url"]))
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            errors.append(f"line {line_number}: source_url must be a valid HTTPS URL")
            continue
        records.append(record)

    ids = [str(record["id"]) for record in records]
    duplicate_ids = sorted(value for value, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        errors.append("duplicate record IDs: " + ", ".join(duplicate_ids))

    return {
        "path": str(dataset_path),
        "record_count": len(records),
        "crop_counts": dict(sorted(Counter(record["crop"] for record in records).items())),
        "source_counts": dict(sorted(Counter(record["source_name"] for record in records).items())),
        "missing_publication_dates": sum(
            not (record.get("publication_date") or record.get("updated_at")) for record in records
        ),
        "missing_source_urls": sum(not record.get("source_url") for record in records),
        "duplicate_ids": duplicate_ids,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the agricultural source dataset metadata.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="JSONL dataset path")
    args = parser.parse_args(argv)

    try:
        report = audit_dataset(args.dataset)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Dataset audit failed: {exc}\n")

    print(f"Dataset: {report['path']}")
    print(f"Records: {report['record_count']}")
    print(f"Crops: {report['crop_counts']}")
    print(f"Source labels: {len(report['source_counts'])}")
    print(f"Missing publication dates: {report['missing_publication_dates']}")
    print(f"Duplicate IDs: {len(report['duplicate_ids'])}")
    for error in report["errors"]:
        print(f"ERROR: {error}")
    if report["missing_publication_dates"]:
        print("WARNING: publication dates are absent; no dates were inferred.")
    print("RESULT: " + ("FAILED" if report["errors"] else "PASSED"))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

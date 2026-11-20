"""Measure where each advice answer comes from.

Each answer is labelled by the path the tool took:
  model   - the GPT model's own text passed the coherence check
  record  - the model's text failed, so a stored record's advice was used
  generic - the model's text and records failed, so the built-in sentence was used
  empty   - no advice text at all

Run from the project root:  python -m tools.measure_advice
Writes results/measure_advice.csv and prints a summary.
"""

import csv
from collections import Counter
from pathlib import Path

from app.core import query_crop_advice
from app.records import RecordManager

QUERIES = [
    ("Tomato", "early blight"),
    ("Tomato", "irrigation"),
    ("Rice", "yellow stem borer"),
    ("Rice", "blast disease"),
    ("Wheat", "rust disease"),
    ("Maize", "fall armyworm"),
    ("Potato", "late blight"),
    ("Mango", "anthracnose"),
    ("Chilli", "leaf curl"),
    ("Cotton", "bollworm"),
]

GENERIC_MARKER = "maintain balanced fertilization, ensure good drainage, and scout regularly"


def classify(advice: str, record_texts: set) -> str:
    if not advice.strip():
        return "empty"
    if GENERIC_MARKER in advice:
        return "generic"
    if advice in record_texts:
        return "record"
    return "model"


def main() -> None:
    manager = RecordManager()
    manager.load()
    record_texts = {r.advice for r in manager.records.values()}

    rows = []
    for crop, problem in QUERIES:
        result = query_crop_advice(crop=crop, problem=problem)
        advice = result["advice"]
        rows.append({
            "crop": crop,
            "problem": problem,
            "path": classify(advice, record_texts),
            "advice": advice,
        })

    out = Path("results") / "measure_advice.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["crop", "problem", "path", "advice"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["path"] for r in rows)
    total = len(rows)
    print(f"Queries: {total}")
    for label in ("model", "record", "generic", "empty"):
        n = counts.get(label, 0)
        print(f"{label:8} {n:3}  ({n / total:.0%})")
    print(f"Details written to {out}")


if __name__ == "__main__":
    main()

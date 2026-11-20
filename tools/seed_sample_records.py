"""Create a small sample records file so the records CLI and tests have data.

Run from the project root:  python tools/seed_sample_records.py
"""

from app.records import AgriculturalRecord, RecordManager

SAMPLES = [
    AgriculturalRecord(
        id="tomato-001",
        crop="Tomato",
        topic="Disease",
        advice="Remove infected leaves and apply a copper-based fungicide at first symptoms of early blight.",
        source_name="ICAR-IIHR Bengaluru",
        source_url="https://icar-iihr.org.in",
        symptoms="Concentric brown rings on lower leaves",
        severity="High",
        confidence=0.90,
        tags=["disease", "fungal"],
        review_status="reviewed",
    ),
    AgriculturalRecord(
        id="tomato-002",
        crop="Tomato",
        topic="Irrigation",
        advice="Irrigate at regular intervals with drip systems; avoid waterlogging to reduce fruit cracking.",
        source_name="TNAU Agritech Portal",
        source_url="https://agritech.tnau.ac.in",
        severity="Medium",
        confidence=0.88,
        tags=["irrigation", "water"],
        review_status="reviewed",
    ),
]


def main() -> None:
    manager = RecordManager()
    manager.load()
    for record in SAMPLES:
        manager.add(record, overwrite=True)
    manager.save()
    print(f"Wrote {len(SAMPLES)} sample records to {manager.storage_path}")


if __name__ == "__main__":
    main()

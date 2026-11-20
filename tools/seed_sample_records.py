"""Create a small sample records file so the records CLI and tests have data.

Each advice text is limited to what its cited source says.

Run from the project root:  python -m tools.seed_sample_records
"""

from app.records import AgriculturalRecord, RecordManager

SAMPLES = [
    AgriculturalRecord(
        id="tomato-001",
        crop="Tomato",
        topic="Disease",
        advice="At the first symptoms of early blight, spray a registered fungicide such as propineb or a tebuconazole-based product, and follow the label dose and interval.",
        source_name="Plant Archives: early blight fungicide evaluation",
        source_url="https://www.plantarchives.org/",
        severity="High",
        confidence=0.80,
        tags=["disease", "fungal"],
        review_status="reviewed",
    ),
    AgriculturalRecord(
        id="tomato-002",
        crop="Tomato",
        topic="Irrigation",
        advice="Irrigate at regular intervals, about every 8 to 12 days, to keep the water supply even. Drip irrigation is economical and suits tomato. Avoid long dry spells followed by sudden heavy irrigation, which can crack the fruit.",
        source_name="TNAU Agritech Portal",
        source_url="https://agritech.tnau.ac.in/org_farm/orgfarm_tomato_water.html",
        severity="Medium",
        confidence=0.85,
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

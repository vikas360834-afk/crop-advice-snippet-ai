"""Regression tests for visible handling of malformed JSONL records."""

import json
import logging

from app.feedback import FarmerFeedback, FeedbackManager
from app.records import AgriculturalRecord, RecordManager
from app.soil_intel import SoilManager, SoilRecord
from app.weather_intel import WeatherManager, WeatherRecord


def test_jsonl_managers_warn_about_corrupt_rows_and_keep_valid_rows(tmp_path, caplog):
    cases = [
        ("feedback", FeedbackManager, FarmerFeedback(id="fb-1", crop="Rice", rating=5).to_dict(), "feedback_list"),
        (
            "agricultural",
            RecordManager,
            AgriculturalRecord(
                id="ag-1",
                crop="Rice",
                topic="irrigation",
                advice="Follow local irrigation guidance.",
                source_name="TNAU Agritech",
                source_url="https://agritech.tnau.ac.in/",
            ).to_dict(),
            "records",
        ),
        (
            "soil",
            SoilManager,
            SoilRecord(id="soil-1", field_name="Plot A", location="Farm", soil_type="Loam", soil_ph=6.5).to_dict(),
            "records",
        ),
        (
            "weather",
            WeatherManager,
            WeatherRecord(
                id="weather-1",
                location="Farm",
                date="2026-11-20",
                temperature_c=25,
                humidity_pct=60,
            ).to_dict(),
            "records",
        ),
    ]

    for label, manager_type, valid_record, collection_name in cases:
        path = tmp_path / f"{label}.jsonl"
        # Use real line breaks so the reader sees one corrupt row and one valid row.
        path.write_text("{malformed json}\\n" + json.dumps(valid_record) + "\\n", encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            manager = manager_type(path)

        assert len(getattr(manager, collection_name)) == 1, label
        assert f"Skipping invalid {label} record" in caplog.text
        caplog.clear()

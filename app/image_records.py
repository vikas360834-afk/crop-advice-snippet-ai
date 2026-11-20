"""Crop Image Observations and Metadata Registry.

Manages farmer crop photographs and observation metadata:
- Image file path
- Crop name
- Field / Plot ID
- Observed visual symptoms
- Date & GPS / Field Location
- Farmer observations & tags

Maintains an interface for future computer vision classification while
clearly stating that diagnosis requires agronomic confirmation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_IMAGE_RECORDS_PATH = Path("data/image_records.jsonl")


class CropImageRecord:
    def __init__(
        self,
        id: str,
        image_path: str,
        crop: str,
        field_id: str = "Field-1",
        symptoms: str = "",
        location: str = "Farm",
        date: str = "",
        observations: str = "",
        tags: Optional[List[str]] = None,
    ):
        self.id = str(id).strip()
        self.image_path = str(image_path).strip()
        self.crop = str(crop).strip().title()
        self.field_id = str(field_id).strip()
        self.symptoms = str(symptoms).strip()
        self.location = str(location).strip()
        self.date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.observations = str(observations).strip()
        self.tags = tags if tags is not None else []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "crop": self.crop,
            "field_id": self.field_id,
            "symptoms": self.symptoms,
            "location": self.location,
            "date": self.date,
            "observations": self.observations,
            "tags": self.tags,
            "cv_status": "Ready for validated vision classifier integration. Human expert verification required.",
        }


class ImageRecordManager:
    def __init__(self, path: Path | str = DEFAULT_IMAGE_RECORDS_PATH):
        self.path = Path(path)
        self.records: Dict[str, CropImageRecord] = {}
        self.load()

    def load(self) -> None:
        self.records = {}
        if not self.path.exists():
            return
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                rec = CropImageRecord(
                    id=data["id"],
                    image_path=data["image_path"],
                    crop=data["crop"],
                    field_id=data.get("field_id", "Field-1"),
                    symptoms=data.get("symptoms", ""),
                    location=data.get("location", "Farm"),
                    date=data.get("date", ""),
                    observations=data.get("observations", ""),
                    tags=data.get("tags", []),
                )
                self.records[rec.id] = rec
            except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
                logging.warning(
                    "Skipping invalid image record in %s at line %d: %s",
                    self.path, line_number, exc,
                )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r.to_dict()) for r in self.records.values()]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def add(self, record: CropImageRecord) -> None:
        self.records[record.id] = record
        self.save()

    def get(self, record_id: str) -> Optional[CropImageRecord]:
        return self.records.get(record_id)

    def list_all(self, crop: Optional[str] = None) -> List[CropImageRecord]:
        results = list(self.records.values())
        if crop:
            results = [r for r in results if r.crop.lower() == crop.strip().lower()]
        return results

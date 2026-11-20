"""Advanced Agricultural Record Management and Schema Validation.

Supports rich JSONL agricultural records with:
- Unique record ID
- Crop, topic, advice, recommended action, prevention
- Source name, source URL, region, season, growth stage
- Soil type, soil pH (validated 0-14), weather conditions
- Symptoms, severity, confidence score (0-1), tags, review status
- Full CRUD, import/export, dataset analytics, and audit
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

DEFAULT_RECORDS_PATH = Path("data/agricultural_records.jsonl")

VALID_SEVERITIES = {"Low", "Medium", "High", "Critical"}
VALID_REVIEW_STATUSES = {"verified", "reviewed", "pending", "rejected"}
VALID_SEASONS = {"Kharif", "Rabi", "Zaid", "Year-round", "Spring", "Summer", "Autumn", "Winter"}


class AgriculturalRecord:
    """Represents a validated agricultural knowledge record."""

    def __init__(
        self,
        id: str,
        crop: str,
        topic: str,
        advice: str,
        source_name: str,
        source_url: str = "",
        region: str = "All regions",
        season: str = "Year-round",
        growth_stage: str = "All stages",
        soil_type: str = "All soils",
        soil_ph: Optional[float] = None,
        weather: str = "Standard conditions",
        symptoms: str = "",
        severity: str = "Medium",
        recommended_action: str = "",
        prevention: str = "",
        confidence: float = 0.90,
        tags: Optional[List[str]] = None,
        language: str = "en",
        review_status: str = "reviewed",
        reviewer: str = "Agronomy Expert Team",
        last_reviewed_date: str = "",
        created_at: str = "",
    ):
        self.id = str(id).strip()
        self.crop = str(crop).strip().title()
        self.topic = str(topic).strip()
        self.advice = str(advice).strip()
        self.source_name = str(source_name).strip()
        self.source_url = str(source_url).strip()
        self.region = str(region).strip()
        self.season = str(season).strip()
        self.growth_stage = str(growth_stage).strip()
        self.soil_type = str(soil_type).strip()
        self.soil_ph = float(soil_ph) if soil_ph is not None else None
        self.weather = str(weather).strip()
        self.symptoms = str(symptoms).strip()
        self.severity = str(severity).strip().capitalize()
        self.recommended_action = str(recommended_action).strip() or self.advice
        self.prevention = str(prevention).strip()
        self.confidence = float(confidence)
        self.tags = tags if tags is not None else []
        self.language = str(language).strip()
        self.review_status = str(review_status).strip().lower()
        self.reviewer = str(reviewer).strip()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.last_reviewed_date = last_reviewed_date or now_str
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

        self.validate()

    def validate(self) -> None:
        """Validate all field constraints."""
        if not self.id:
            raise ValueError("Record 'id' cannot be empty.")
        if not self.crop:
            raise ValueError("Record 'crop' cannot be empty.")
        if not self.topic:
            raise ValueError("Record 'topic' cannot be empty.")
        if not self.advice:
            raise ValueError("Record 'advice' cannot be empty.")
        if not self.source_name:
            raise ValueError("Record 'source_name' cannot be empty.")

        if self.soil_ph is not None:
            if not (0.0 <= self.soil_ph <= 14.0):
                raise ValueError(f"Soil pH must be between 0.0 and 14.0 (got {self.soil_ph}).")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0 (got {self.confidence}).")

        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"Severity must be one of {VALID_SEVERITIES} (got '{self.severity}').")

        if self.review_status not in VALID_REVIEW_STATUSES:
            raise ValueError(f"Review status must be one of {VALID_REVIEW_STATUSES} (got '{self.review_status}').")

        if self.source_url:
            parsed = urlparse(self.source_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid source URL format: '{self.source_url}'.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "crop": self.crop,
            "topic": self.topic,
            "advice": self.advice,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "region": self.region,
            "season": self.season,
            "growth_stage": self.growth_stage,
            "soil_type": self.soil_type,
            "soil_ph": self.soil_ph,
            "weather": self.weather,
            "symptoms": self.symptoms,
            "severity": self.severity,
            "recommended_action": self.recommended_action,
            "prevention": self.prevention,
            "confidence": self.confidence,
            "tags": self.tags,
            "language": self.language,
            "review_status": self.review_status,
            "reviewer": self.reviewer,
            "last_reviewed_date": self.last_reviewed_date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgriculturalRecord":
        return cls(
            id=data["id"],
            crop=data["crop"],
            topic=data.get("topic", "General Advice"),
            advice=data.get("advice", ""),
            source_name=data.get("source_name", "ICAR Extension"),
            source_url=data.get("source_url", ""),
            region=data.get("region", "All regions"),
            season=data.get("season", "Year-round"),
            growth_stage=data.get("growth_stage", "All stages"),
            soil_type=data.get("soil_type", "All soils"),
            soil_ph=data.get("soil_ph"),
            weather=data.get("weather", "Standard conditions"),
            symptoms=data.get("symptoms", ""),
            severity=data.get("severity", "Medium"),
            recommended_action=data.get("recommended_action", ""),
            prevention=data.get("prevention", ""),
            confidence=data.get("confidence", 0.90),
            tags=data.get("tags", []),
            language=data.get("language", "en"),
            review_status=data.get("review_status", "reviewed"),
            reviewer=data.get("reviewer", "Agronomy Expert Team"),
            last_reviewed_date=data.get("last_reviewed_date", ""),
            created_at=data.get("created_at", ""),
        )

    def to_training_text(self) -> str:
        """Converts structured record into a clean training format string."""
        parts = [f"[CROP: {self.crop}"]
        if self.topic:
            parts.append(f"TOPIC: {self.topic}")
        if self.growth_stage and self.growth_stage != "All stages":
            parts.append(f"STAGE: {self.growth_stage}")
        if self.soil_type and self.soil_type != "All soils":
            parts.append(f"SOIL: {self.soil_type}")
        if self.weather and self.weather != "Standard conditions":
            parts.append(f"WEATHER: {self.weather}")
        if self.symptoms:
            parts.append(f"SYMPTOMS: {self.symptoms}")
        header = " | ".join(parts) + "]"

        advice_body = f"ADVICE: {self.advice}"
        if self.recommended_action and self.recommended_action != self.advice:
            advice_body += f" ACTION: {self.recommended_action}"
        if self.prevention:
            advice_body += f" PREVENTION: {self.prevention}"

        return f"{header} {advice_body}"


class RecordManager:
    """Manages agricultural records in JSONL storage."""

    def __init__(self, storage_path: Path | str = DEFAULT_RECORDS_PATH):
        self.storage_path = Path(storage_path)
        self.records: Dict[str, AgriculturalRecord] = {}
        self.load()

    def load(self) -> None:
        """Load records from JSONL."""
        self.records = {}
        if not self.storage_path.exists():
            return
        lines = self.storage_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                data = json.loads(line)
                rec = AgriculturalRecord.from_dict(data)
                self.records[rec.id] = rec
            except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
                logging.warning(
                    "Skipping invalid agricultural record in %s at line %d: %s",
                    self.storage_path, idx, exc,
                )

    def save(self) -> None:
        """Save all records to JSONL."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r.to_dict(), ensure_ascii=False) for r in self.records.values()]
        self.storage_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def add(self, record: AgriculturalRecord, overwrite: bool = False) -> None:
        """Add a record, preventing duplicate IDs unless overwrite=True."""
        record.validate()
        if record.id in self.records and not overwrite:
            raise ValueError(f"Record with ID '{record.id}' already exists.")
        self.records[record.id] = record
        self.save()

    def get(self, record_id: str) -> Optional[AgriculturalRecord]:
        return self.records.get(record_id)

    def delete(self, record_id: str) -> bool:
        if record_id in self.records:
            del self.records[record_id]
            self.save()
            return True
        return False

    def list_all(
        self,
        crop: Optional[str] = None,
        topic: Optional[str] = None,
        region: Optional[str] = None,
        season: Optional[str] = None,
        review_status: Optional[str] = None,
    ) -> List[AgriculturalRecord]:
        """List records with optional filtering."""
        results = list(self.records.values())
        if crop:
            results = [r for r in results if r.crop.lower() == crop.strip().lower()]
        if topic:
            results = [r for r in results if topic.strip().lower() in r.topic.lower()]
        if region:
            results = [r for r in results if region.strip().lower() in r.region.lower()]
        if season:
            results = [r for r in results if season.strip().lower() in r.season.lower()]
        if review_status:
            results = [r for r in results if r.review_status == review_status.strip().lower()]
        return results

    def search(self, query: str) -> List[AgriculturalRecord]:
        """Keyword search across all fields."""
        tokens = [t.lower() for t in query.split() if t]
        if not tokens:
            return list(self.records.values())

        matched = []
        for r in self.records.values():
            haystack = f"{r.crop} {r.topic} {r.advice} {r.recommended_action} {r.prevention} {r.symptoms} {r.weather} {r.soil_type} {' '.join(r.tags)}".lower()
            if any(t in haystack for t in tokens):
                matched.append(r)
        return matched

    def import_from_jsonl(self, file_path: Path | str, overwrite: bool = False) -> Tuple[int, int]:
        """Import records from another JSONL file. Returns (imported_count, skipped_count)."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        imported = 0
        skipped = 0
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                data = json.loads(line)
                rec = AgriculturalRecord.from_dict(data)
                if rec.id in self.records and not overwrite:
                    skipped += 1
                else:
                    self.records[rec.id] = rec
                    imported += 1
            except Exception:
                skipped += 1
        self.save()
        return imported, skipped

    def export_to_jsonl(self, file_path: Path | str) -> int:
        """Export records to a JSONL file."""
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r.to_dict(), ensure_ascii=False) for r in self.records.values()]
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return len(lines)

    def get_analytics(self) -> Dict[str, Any]:
        """Calculate comprehensive dataset statistics and analytics."""
        records = list(self.records.values())
        crops: Dict[str, int] = {}
        topics: Dict[str, int] = {}
        regions: Dict[str, int] = {}
        seasons: Dict[str, int] = {}
        review_statuses: Dict[str, int] = {}

        has_soil = 0
        has_weather = 0
        has_symptoms = 0
        has_prevention = 0
        has_action = 0

        for r in records:
            crops[r.crop] = crops.get(r.crop, 0) + 1
            topics[r.topic] = topics.get(r.topic, 0) + 1
            regions[r.region] = regions.get(r.region, 0) + 1
            seasons[r.season] = seasons.get(r.season, 0) + 1
            review_statuses[r.review_status] = review_statuses.get(r.review_status, 0) + 1

            if r.soil_type and r.soil_type != "All soils":
                has_soil += 1
            if r.weather and r.weather != "Standard conditions":
                has_weather += 1
            if r.symptoms:
                has_symptoms += 1
            if r.prevention:
                has_prevention += 1
            if r.recommended_action:
                has_action += 1

        return {
            "total_records": len(records),
            "total_crops": len(crops),
            "records_per_crop": dict(sorted(crops.items(), key=lambda x: x[1], reverse=True)),
            "records_per_topic": dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)),
            "records_per_region": dict(sorted(regions.items(), key=lambda x: x[1], reverse=True)),
            "records_per_season": dict(sorted(seasons.items(), key=lambda x: x[1], reverse=True)),
            "records_by_review_status": review_statuses,
            "records_with_soil_info": has_soil,
            "records_with_weather_info": has_weather,
            "records_with_disease_symptoms": has_symptoms,
            "records_with_prevention_methods": has_prevention,
            "records_with_recommended_actions": has_action,
        }

    def audit(self) -> Dict[str, Any]:
        """Audit dataset for quality, integrity, and potential issues."""
        issues: List[str] = []
        warnings: List[str] = []
        valid_count = 0

        for r in self.records.values():
            try:
                r.validate()
                valid_count += 1
            except Exception as e:
                issues.append(f"Record '{r.id}' failed validation: {e}")

            if not r.source_url:
                warnings.append(f"Record '{r.id}' has no source URL.")
            if r.review_status == "pending":
                warnings.append(f"Record '{r.id}' review is still pending.")

        return {
            "total_audited": len(self.records),
            "valid_records": valid_count,
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "issues": issues,
            "warnings": warnings,
            "health_score": round((valid_count / max(1, len(self.records))) * 100, 1),
        }

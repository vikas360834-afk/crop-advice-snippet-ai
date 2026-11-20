"""Soil Intelligence Module.

Stores and evaluates soil test records:
- Soil type
- Soil pH
- Electrical Conductivity (EC in dS/m)
- Organic Carbon (OC %)
- Available Nitrogen (N in kg/ha)
- Available Phosphorus (P2O5 in kg/ha)
- Available Potassium (K2O in kg/ha)
- Soil moisture (%)
- Soil testing date and location

Provides science-backed fertility interpretations and amendment guidelines.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_SOIL_RECORDS_PATH = Path("data/soil_records.jsonl")


class SoilRecord:
    def __init__(
        self,
        id: str,
        field_name: str,
        location: str,
        soil_type: str,
        soil_ph: float,
        ec: float = 0.4,
        organic_carbon_pct: float = 0.5,
        nitrogen_kg_ha: float = 220.0,
        phosphorus_kg_ha: float = 18.0,
        potassium_kg_ha: float = 180.0,
        moisture_pct: Optional[float] = None,
        test_date: str = "",
        crop_planned: str = "",
        notes: str = "",
    ):
        self.id = str(id).strip()
        self.field_name = str(field_name).strip()
        self.location = str(location).strip()
        self.soil_type = str(soil_type).strip()
        self.soil_ph = float(soil_ph)
        self.ec = float(ec)
        self.organic_carbon_pct = float(organic_carbon_pct)
        self.nitrogen_kg_ha = float(nitrogen_kg_ha)
        self.phosphorus_kg_ha = float(phosphorus_kg_ha)
        self.potassium_kg_ha = float(potassium_kg_ha)
        self.moisture_pct = float(moisture_pct) if moisture_pct is not None else None
        self.test_date = test_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.crop_planned = str(crop_planned).strip()
        self.notes = str(notes).strip()

        self.validate()

    def validate(self) -> None:
        if not (0.0 <= self.soil_ph <= 14.0):
            raise ValueError(f"Soil pH must be between 0.0 and 14.0 (got {self.soil_ph}).")
        if self.ec < 0.0:
            raise ValueError("Electrical conductivity (EC) cannot be negative.")
        if self.organic_carbon_pct < 0.0:
            raise ValueError("Organic carbon % cannot be negative.")

    def evaluate_fertility(self) -> Dict[str, Any]:
        """Interprets soil test values based on Indian Soil Science standards."""
        # pH interpretation
        if self.soil_ph < 5.5:
            ph_status = "Strongly Acidic"
            ph_action = "Apply agricultural limestone or dolomite (2-4 t/ha) to neutralize aluminum toxicity."
        elif self.soil_ph < 6.5:
            ph_status = "Moderately Acidic"
            ph_action = "Suitable for most crops; add organic matter and bone meal."
        elif self.soil_ph <= 7.5:
            ph_status = "Neutral / Optimal"
            ph_action = "Optimal pH for maximum nutrient availability. Maintain with regular organic manure."
        elif self.soil_ph <= 8.5:
            ph_status = "Moderately Alkaline / Calcareous"
            ph_action = "Apply farmyard manure (FYM) or green manure to release organic acids; monitor zinc availability."
        else:
            ph_status = "Strongly Alkaline / Sodic"
            ph_action = "Apply gypsum (calcium sulfate) based on gypsum requirement test to displace exchangeable sodium."

        # Salinity (EC)
        salinity_status = "Normal (<1.0 dS/m)" if self.ec < 1.0 else ("Critical Salinity (>2.0 dS/m)" if self.ec > 2.0 else "Slight Salinity")

        # Organic Carbon
        if self.organic_carbon_pct < 0.5:
            oc_status = "Low (<0.5%)"
            oc_action = "Add 10-15 tons/ha well-decomposed FYM or compost; practice green manuring with Sesbania."
        elif self.organic_carbon_pct <= 0.75:
            oc_status = "Medium (0.5 - 0.75%)"
            oc_action = "Maintain organic matter by incorporating crop residue after harvest."
        else:
            oc_status = "High (>0.75%)"
            oc_action = "Excellent soil biology and moisture holding capacity."

        # Nitrogen (kg/ha): Low <280, Medium 280-560, High >560
        n_status = "Low (<280 kg/ha)" if self.nitrogen_kg_ha < 280 else ("Medium (280-560 kg/ha)" if self.nitrogen_kg_ha <= 560 else "High (>560 kg/ha)")

        # Phosphorus (kg/ha P2O5): Low <23, Medium 23-56, High >56
        p_status = "Low (<23 kg/ha)" if self.phosphorus_kg_ha < 23 else ("Medium (23-56 kg/ha)" if self.phosphorus_kg_ha <= 56 else "High (>56 kg/ha)")

        # Potassium (kg/ha K2O): Low <130, Medium 130-330, High >330
        k_status = "Low (<130 kg/ha)" if self.potassium_kg_ha < 130 else ("Medium (130-330 kg/ha)" if self.potassium_kg_ha <= 330 else "High (>330 kg/ha)")

        return {
            "soil_ph": self.soil_ph,
            "ph_status": ph_status,
            "ph_action": ph_action,
            "salinity_ec": f"{self.ec} dS/m ({salinity_status})",
            "organic_carbon": f"{self.organic_carbon_pct}% ({oc_status})",
            "oc_action": oc_action,
            "nitrogen_status": n_status,
            "phosphorus_status": p_status,
            "potassium_status": k_status,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "field_name": self.field_name,
            "location": self.location,
            "soil_type": self.soil_type,
            "soil_ph": self.soil_ph,
            "ec": self.ec,
            "organic_carbon_pct": self.organic_carbon_pct,
            "nitrogen_kg_ha": self.nitrogen_kg_ha,
            "phosphorus_kg_ha": self.phosphorus_kg_ha,
            "potassium_kg_ha": self.potassium_kg_ha,
            "moisture_pct": self.moisture_pct,
            "test_date": self.test_date,
            "crop_planned": self.crop_planned,
            "notes": self.notes,
        }


class SoilManager:
    def __init__(self, path: Path | str = DEFAULT_SOIL_RECORDS_PATH):
        self.path = Path(path)
        self.records: Dict[str, SoilRecord] = {}
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
                rec = SoilRecord(**data)
                self.records[rec.id] = rec
            except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
                logging.warning(
                    "Skipping invalid soil record in %s at line %d: %s",
                    self.path, line_number, exc,
                )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r.to_dict()) for r in self.records.values()]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def add(self, record: SoilRecord) -> None:
        record.validate()
        self.records[record.id] = record
        self.save()

    def get(self, record_id: str) -> Optional[SoilRecord]:
        return self.records.get(record_id)

    def list_all(self) -> List[SoilRecord]:
        return list(self.records.values())

"""Weather Intelligence and Advisory Module.

Stores:
- Temperature (Celsius)
- Relative Humidity (%)
- Rainfall (mm)
- Wind speed (km/h)
- Observation vs Forecast status
- Date, location, and source

Provides rule-based agronomic risk assessment:
- Fungal disease sporulation risk
- Heat stress & flower drop warning
- Frost damage alert
- Waterlogging & hypoxic root risk
- Pesticide spray suitability check (wind drift & rain wash-off)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_WEATHER_RECORDS_PATH = Path("data/weather_records.jsonl")


class WeatherRecord:
    def __init__(
        self,
        id: str,
        location: str,
        date: str,
        temperature_c: float,
        humidity_pct: float,
        rainfall_mm: float = 0.0,
        wind_speed_kmh: float = 8.0,
        is_forecast: bool = False,
        source: str = "IMD (India Meteorological Department)",
        notes: str = "",
    ):
        self.id = str(id).strip()
        self.location = str(location).strip()
        self.date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.temperature_c = float(temperature_c)
        self.humidity_pct = float(humidity_pct)
        self.rainfall_mm = float(rainfall_mm)
        self.wind_speed_kmh = float(wind_speed_kmh)
        self.is_forecast = bool(is_forecast)
        self.source = str(source).strip()
        self.notes = str(notes).strip()

    def assess_crop_risks(self, crop: str = "General", stage: str = "General") -> Dict[str, Any]:
        """Assess immediate agricultural risks based on meteorological parameters."""
        risks = []
        advisories = []

        # 1. Fungal disease risk
        if self.humidity_pct >= 85 and (15.0 <= self.temperature_c <= 28.0):
            risks.append("CRITICAL: High Fungal Disease Risk (Blight / Rust / Mildew)")
            advisories.append(
                "High relative humidity combined with mild temperatures strongly favors fungal spore germination. "
                "Inspect lower leaf canopies and consider preventive protective sprays (mancozeb or chlorothalonil)."
            )
        elif self.humidity_pct >= 75:
            risks.append("MODERATE: Fungal sporulation warning")

        # 2. Heat stress & flower abortion
        if self.temperature_c >= 35.0:
            risks.append("HIGH: Thermal Heat Stress / Pollen Desiccation Risk")
            advisories.append(
                "Midday temperatures above 35C cause pollen sterility and flower abortion in crops like tomato, chilli, and maize. "
                "Maintain uniform soil moisture through evening drip irrigations and erect shade netting if applicable."
            )

        # 3. Frost alert
        if self.temperature_c <= 4.0:
            risks.append("CRITICAL: Frost Hazard Warning")
            advisories.append(
                "Near-freezing temperatures threaten tender foliage of potato, tomato, and mustard. "
                "Run micro-sprinklers before midnight or create protective smoke borders along windward boundaries."
            )

        # 4. Waterlogging & excess rain
        if self.rainfall_mm >= 40.0:
            risks.append("HIGH: Soil Waterlogging & Root Asphyxiation Risk")
            advisories.append(
                "Clear field drainage trenches immediately to prevent standing water in maize, cotton, and vegetable beds. "
                "Withhold granular fertilizer until fields drain."
            )

        # 5. Pesticide Spray Suitability
        can_spray = True
        spray_notes = []
        if self.wind_speed_kmh > 15.0:
            can_spray = False
            spray_notes.append(f"Wind speed ({self.wind_speed_kmh} km/h) exceeds safe threshold (15 km/h); high drift risk.")
        if self.rainfall_mm > 5.0 or (self.is_forecast and self.rainfall_mm > 0):
            can_spray = False
            spray_notes.append("Rainfall imminent; applied chemical wash-off will occur.")

        if can_spray:
            spray_suitability = "FAVOURABLE for pesticide and foliar fertilizer spraying."
        else:
            spray_suitability = "UNFAVOURABLE: Postpone spraying. " + " ".join(spray_notes)

        return {
            "record_type": "Forecast" if self.is_forecast else "Observed",
            "temperature": f"{self.temperature_c} C",
            "humidity": f"{self.humidity_pct}%",
            "rainfall": f"{self.rainfall_mm} mm",
            "wind_speed": f"{self.wind_speed_kmh} km/h",
            "risks_identified": risks if risks else ["Low meteorological risk"],
            "advisories": advisories if advisories else ["Weather conditions are generally favorable for standard farm operations."],
            "spray_suitability": spray_suitability,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "location": self.location,
            "date": self.date,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "rainfall_mm": self.rainfall_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "is_forecast": self.is_forecast,
            "source": self.source,
            "notes": self.notes,
        }


class WeatherManager:
    def __init__(self, path: Path | str = DEFAULT_WEATHER_RECORDS_PATH):
        self.path = Path(path)
        self.records: Dict[str, WeatherRecord] = {}
        self.load()

    def load(self) -> None:
        self.records = {}
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                rec = WeatherRecord(**data)
                self.records[rec.id] = rec
            except Exception:
                pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r.to_dict()) for r in self.records.values()]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def add(self, record: WeatherRecord) -> None:
        self.records[record.id] = record
        self.save()

    def get(self, record_id: str) -> Optional[WeatherRecord]:
        return self.records.get(record_id)

    def list_all(self) -> List[WeatherRecord]:
        return list(self.records.values())

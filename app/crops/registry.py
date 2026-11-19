"""Crop Registry and Search Engine for 120+ Agricultural Crops.

Supports:
- Centralized crop registry (140 crops across 11 categories)
- Search by English, scientific, and regional Indian names (Hindi, Kannada, Tamil, Telugu, Marathi, etc.)
- Filtering by crop category, region, and season
- Comprehensive agronomic statistics
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

REGISTRY_PATH = Path("data/crops/crop_registry.json")


class CropEntry:
    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.name = data["name"]
        self.scientific_name = data.get("scientific_name", "")
        self.category = data.get("category", "General")
        self.common_indian_names = data.get("common_indian_names", [])
        self.regional_names = data.get("regional_names", {})
        self.growing_regions = data.get("growing_regions", [])
        self.seasons = data.get("seasons", [])
        self.duration_days = data.get("duration_days")
        self.soil_preferences = data.get("soil_preferences", {})
        self.water_requirements = data.get("water_requirements", "")
        self.nutrient_requirements = data.get("nutrient_requirements", "")
        self.growth_stages = data.get("growth_stages", [])
        self.common_diseases = data.get("common_diseases", [])
        self.common_pests = data.get("common_pests", [])
        self.source_references = data.get("source_references", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "category": self.category,
            "common_indian_names": self.common_indian_names,
            "regional_names": self.regional_names,
            "growing_regions": self.growing_regions,
            "seasons": self.seasons,
            "duration_days": self.duration_days,
            "soil_preferences": self.soil_preferences,
            "water_requirements": self.water_requirements,
            "nutrient_requirements": self.nutrient_requirements,
            "growth_stages": self.growth_stages,
            "common_diseases": self.common_diseases,
            "common_pests": self.common_pests,
            "source_references": self.source_references,
        }


class CropRegistry:
    def __init__(self, path: Path | str = REGISTRY_PATH):
        self.path = Path(path)
        self.crops: Dict[str, CropEntry] = {}
        self.load()

    def load(self) -> None:
        self.crops = {}
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for item in data:
            entry = CropEntry(item)
            self.crops[entry.id] = entry

    def list_crops(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[CropEntry]:
        results = list(self.crops.values())
        if category:
            cat_clean = category.strip().lower()
            results = [c for c in results if c.category.lower() == cat_clean or cat_clean in c.category.lower()]
        if region:
            reg_clean = region.strip().lower()
            results = [c for c in results if any(reg_clean in r.lower() for r in c.growing_regions)]
        if season:
            sea_clean = season.strip().lower()
            results = [c for c in results if any(sea_clean in s.lower() for s in c.seasons)]
        return results

    def get_crop(self, identifier: str) -> Optional[CropEntry]:
        """Fetch crop by exact ID, English name, or alias."""
        clean = identifier.strip().lower().replace("-", "_").replace(" ", "_")
        if clean in self.crops:
            return self.crops[clean]

        for c in self.crops.values():
            if c.name.lower() == identifier.strip().lower():
                return c
            if c.scientific_name.lower() == identifier.strip().lower():
                return c
            if any(alias.lower() == identifier.strip().lower() for alias in c.common_indian_names):
                return c
            for reg_name in c.regional_names.values():
                if identifier.strip().lower() in reg_name.lower():
                    return c
        return None

    def search_crops(self, query: str) -> List[CropEntry]:
        """Search crops by query across names, scientific names, aliases, and regions."""
        tokens = [t.lower() for t in query.split() if t]
        if not tokens:
            return list(self.crops.values())

        matched = []
        for c in self.crops.values():
            haystack = (
                f"{c.id} {c.name} {c.scientific_name} {c.category} "
                f"{' '.join(c.common_indian_names)} {' '.join(c.regional_names.values())} "
                f"{' '.join(c.growing_regions)} {' '.join(c.seasons)}"
            ).lower()
            if any(t in haystack for t in tokens):
                matched.append(c)
        return matched

    def filter_by_category(self, category: str) -> List[CropEntry]:
        return self.list_crops(category=category)

    def get_crop_stats(self) -> Dict[str, Any]:
        """Calculate database statistics."""
        categories: Dict[str, int] = {}
        seasons: Dict[str, int] = {}
        regions: Dict[str, int] = {}

        for c in self.crops.values():
            categories[c.category] = categories.get(c.category, 0) + 1
            for s in c.seasons:
                seasons[s] = seasons.get(s, 0) + 1
            for r in c.growing_regions:
                regions[r] = regions.get(r, 0) + 1

        return {
            "total_crops": len(self.crops),
            "categories_count": len(categories),
            "crops_by_category": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            "crops_by_season": dict(sorted(seasons.items(), key=lambda x: x[1], reverse=True)),
            "top_regions": dict(sorted(regions.items(), key=lambda x: x[1], reverse=True)[:10]),
        }

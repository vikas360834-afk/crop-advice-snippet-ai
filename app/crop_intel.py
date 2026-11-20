"""Crop Intelligence Module.

Provides agronomic profiles, growth stages, and soil suitability evaluations
backed by the centralized 120+ crop registry.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.crops.registry import CropRegistry

_registry = CropRegistry()

POPULAR_VARIETIES: Dict[str, List[str]] = {
    "wheat": ["DBW 187", "DBW 222", "HD 3086", "HD 2967", "PBW 550", "WH 1105", "GW 322"],
    "rice": ["Pusa Basmati 1121", "Pusa Basmati 1509", "IR 64", "Swarna (MTU 7029)", "MTU 1010", "Samba Mahsuri"],
    "maize": ["Pusa HM 4", "DHM 117", "HQPM 1", "Bio 9681", "Pioneer 30V92"],
    "chickpea": ["JG 11", "JAKO 9218", "Pusa 362", "Pusa 547", "KWR 108"],
    "pigeon pea": ["BDN 711", "ICPL 87119 (Asha)", "Pusa 992", "CO 8"],
    "tomato": ["Pusa Ruby", "Pusa Early Dwarf", "Arka Rakshak", "Arka Vikas", "Himsona"],
    "potato": ["Kufri Jyoti", "Kufri Chandramukhi", "Kufri Pukhraj", "Kufri Bahar", "Kufri Chipsona 1"],
    "cotton": ["Bt Cotton (Bollgard II)", "RCH 659", "MCU 5", "Suraj", "DCH 32"],
    "mustard": ["Pusa Mustard 25", "Pusa Jai Kisan", "Varuna (T-59)", "RH 749", "Kranti"],
    "groundnut": ["TMV 2", "TAG 24", "JL 24", "Kadiri 6", "TG 37A"],
    "sugarcane": ["Co 0238", "Co 86032", "CoLk 94184", "Co 0118", "Co 15023"],
    "soybean": ["JS 335", "JS 9560", "JS 20-34", "NRC 37", "RVS 2001-4"],
}


def get_crop_profile(crop_name: str) -> Optional[Dict[str, Any]]:
    """Fetch agronomic profile for any of the 120+ crops."""
    crop = _registry.get_crop(crop_name)
    if not crop:
        return None
    ph_range = crop.soil_preferences.get("ph_range", [6.0, 7.5])
    crop_key = crop.name.lower().strip()
    varieties = POPULAR_VARIETIES.get(
        crop_key,
        [f"{crop.name} Improved Hybrid", f"{crop.name} Desi Selection"]
    )
    return {
        "crop": crop.name,
        "scientific_name": crop.scientific_name,
        "category": crop.category,
        "season": ", ".join(crop.seasons),
        "varieties": varieties,
        "growth_stages": crop.growth_stages,
        "soil_requirements": crop.soil_preferences.get("type", "Well-drained soil"),
        "optimal_ph_range": tuple(ph_range) if isinstance(ph_range, (list, tuple)) else (6.0, 7.5),
        "irrigation_needs": crop.water_requirements,
        "npk_ratio": crop.nutrient_requirements,
        "common_pests": crop.common_pests,
        "common_diseases": crop.common_diseases,
        "common_indian_names": crop.common_indian_names,
        "regional_names": crop.regional_names,
        "growing_regions": crop.growing_regions,
    }


def list_supported_crops() -> List[str]:
    """Return all crops supported in crop intelligence (120+ crops)."""
    return [c.name for c in _registry.list_crops()]


def query_crop_stages(crop_name: str) -> List[str]:
    """Return growth stages for a crop."""
    profile = get_crop_profile(crop_name)
    if profile:
        return profile.get("growth_stages", [])
    return []


def check_soil_suitability(crop_name: str, soil_ph: float, soil_type: str = "Loam") -> Dict[str, Any]:
    """Evaluate soil suitability for a specific crop."""
    profile = get_crop_profile(crop_name)
    if not profile:
        return {"status": "unknown_crop", "message": f"Crop '{crop_name}' is not in database."}

    min_ph, max_ph = profile["optimal_ph_range"]
    ph_suitable = min_ph <= soil_ph <= max_ph

    ph_advice = "Soil pH is optimal."
    if soil_ph < min_ph:
        ph_advice = f"Soil is slightly acidic (pH {soil_ph}). Consider applying agricultural lime or dolomite."
    elif soil_ph > max_ph:
        ph_advice = f"Soil is alkaline (pH {soil_ph}). Apply gypsum or organic compost to buffer pH."

    return {
        "crop": profile["crop"],
        "category": profile.get("category", "General"),
        "tested_ph": soil_ph,
        "optimal_ph_range": f"{min_ph} - {max_ph}",
        "ph_suitable": ph_suitable,
        "soil_type_notes": profile["soil_requirements"],
        "ph_advice": ph_advice,
    }

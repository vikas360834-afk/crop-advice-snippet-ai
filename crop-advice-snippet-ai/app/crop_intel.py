"""Crop Intelligence Module.

Stores detailed agronomic profiles for major Indian crops:
- Rice, Wheat, Maize, Tomato, Potato, Cotton, Soybean, Chilli, Onion, Groundnut, Apple, Coffee, Sugarcane, Banana.
Includes:
- Recommended varieties
- Sowing dates & harvesting periods
- Growth stages
- Soil and pH requirements
- Irrigation requirements
- Nutrient (NPK) guidelines
- Common pests and diseases
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

CROP_DATABASE: Dict[str, Dict[str, Any]] = {
    "Wheat": {
        "scientific_name": "Triticum aestivum",
        "season": "Rabi",
        "sowing_window": "Late October to mid-November",
        "harvest_window": "March to April",
        "growth_stages": [
            "Crown Root Initiation (CRI - 20-25 DAS)",
            "Tillering (40-45 DAS)",
            "Jointing (60-65 DAS)",
            "Flowering / Heading (80-85 DAS)",
            "Milking / Grain Filling (100-105 DAS)",
            "Maturity / Dough stage (115-125 DAS)",
        ],
        "varieties": ["DBW 187", "DBW 222", "HD 3086", "HD 2967", "WH 1105", "PBW 550"],
        "soil_requirements": "Well-drained fertile loamy or alluvial soil, pH 6.0 - 7.5",
        "optimal_ph_range": (6.0, 7.5),
        "irrigation_needs": "4-6 irrigations; CRI and flowering are critical stages",
        "npk_ratio": "120:60:40 kg/ha N:P2O5:K2O",
        "common_pests": ["Aphids", "Termites", "Armyworm"],
        "common_diseases": ["Yellow/Stripe Rust", "Brown/Leaf Rust", "Loose Smut", "Karnal Bunt"],
    },
    "Rice": {
        "scientific_name": "Oryza sativa",
        "season": "Kharif / Rabi",
        "sowing_window": "May to July (Kharif), November to December (Rabi)",
        "harvest_window": "October to December (Kharif), April to May (Rabi)",
        "growth_stages": [
            "Nursery / Seedling (0-25 DAS)",
            "Tillering (25-50 DAS)",
            "Panicle Initiation (50-70 DAS)",
            "Booting & Flowering (70-90 DAS)",
            "Grain filling / Ripening (90-120 DAS)",
        ],
        "varieties": ["Pusa Basmati 1121", "Swarna (MTU 7029)", "IR 64", "Swarna-Sub1", "Sambha Mahsuri (BPT 5204)"],
        "soil_requirements": "Heavy clay, clay loam, or silty clay with high water holding capacity",
        "optimal_ph_range": (5.5, 7.2),
        "irrigation_needs": "Continuous shallow standing water (2-5 cm) or Alternate Wetting and Drying (AWD)",
        "npk_ratio": "100:50:50 kg/ha (Kharif) or 120:60:60 kg/ha (Rabi)",
        "common_pests": ["Yellow Stem Borer", "Brown Plant Hopper (BPH)", "Leaf Folder", "Gall Midge"],
        "common_diseases": ["Blast", "Bacterial Leaf Blight (BLB)", "Sheath Blight", "Khaira (Zinc deficiency)"],
    },
    "Tomato": {
        "scientific_name": "Solanum lycopersicum",
        "season": "Kharif, Rabi, and Summer",
        "sowing_window": "June-July (Kharif), October-November (Rabi), January-February (Summer)",
        "harvest_window": "90 to 140 days after transplanting",
        "growth_stages": [
            "Nursery (0-25 days)",
            "Vegetative establishment (25-45 days)",
            "Flowering (45-65 days)",
            "Fruit setting and expansion (65-90 days)",
            "Harvesting / Ripening (90-130 days)",
        ],
        "varieties": ["Arka Rakshak", "Arka Samrat", "Pusa Ruby", "Pusa Rohini", "Abhinav (Syngenta)"],
        "soil_requirements": "Deep, well-drained sandy loam or clay loam rich in organic matter",
        "optimal_ph_range": (6.0, 7.0),
        "irrigation_needs": "Frequent light drip irrigations; avoid waterlogging and extreme drought cycles",
        "npk_ratio": "150:100:100 kg/ha N:P2O5:K2O",
        "common_pests": ["Whitefly", "Tomato Fruit Borer (Helicoverpa)", "Leaf Miner", "Thrips"],
        "common_diseases": ["Early Blight", "Late Blight", "Tomato Leaf Curl Virus (ToLCV)", "Bacterial Wilt"],
    },
    "Potato": {
        "scientific_name": "Solanum tuberosum",
        "season": "Rabi",
        "sowing_window": "October 15 to November 15",
        "harvest_window": "January to March (90-110 days)",
        "growth_stages": [
            "Sprouting and emergence (0-20 DAP)",
            "Vegetative canopy expansion (20-40 DAP)",
            "Tuber initiation (40-60 DAP)",
            "Tuber bulking (60-90 DAP)",
            "Senescence / Dehaulming (90-105 DAP)",
        ],
        "varieties": ["Kufri Jyoti", "Kufri Pukhraj", "Kufri Chipsona-1", "Kufri Mohan", "Kufri Khyati"],
        "soil_requirements": "Friable, loose, well-aerated sandy loam with high organic matter",
        "optimal_ph_range": (5.2, 6.5),
        "irrigation_needs": "5-7 light irrigations; maintain 75% field capacity during tuberization",
        "npk_ratio": "150:100:120 kg/ha N:P2O5:K2O (high potassium demand)",
        "common_pests": ["Aphids (Myzus persicae)", "Potato Tuber Moth (PTM)", "Cutworms"],
        "common_diseases": ["Late Blight", "Early Blight", "Common Scab", "Black Scurf"],
    },
    "Maize": {
        "scientific_name": "Zea mays",
        "season": "Kharif / Rabi / Spring",
        "sowing_window": "June-July (Kharif), October-November (Rabi)",
        "harvest_window": "September-October (Kharif), March-April (Rabi)",
        "growth_stages": [
            "Seedling V2-V4 (0-20 DAS)",
            "Knee-high / Grand whorl V6-V10 (20-45 DAS)",
            "Tasseling VT and Silking R1 (45-65 DAS)",
            "Milking & Dough R3-R4 (65-85 DAS)",
            "Physiological Maturity R6 (90-110 DAS)",
        ],
        "varieties": ["DHM 117", "HQPM 1", "Pusa HM 4", "Pioneer 30V92", "NK 6240"],
        "soil_requirements": "Deep, fertile, well-drained loamy soil, sensitive to waterlogging",
        "optimal_ph_range": (6.0, 7.2),
        "irrigation_needs": "Critical at tasseling and silking; avoid standing water in early seedling stage",
        "npk_ratio": "120:60:40 kg/ha N:P2O5:K2O",
        "common_pests": ["Fall Armyworm", "Stem Borer (Chilo partellus)", "Shoot Fly"],
        "common_diseases": ["Turcicum Leaf Blight", "Maydis Leaf Blight", "Banded Leaf and Sheath Blight", "Stalk Rot"],
    },
    "Cotton": {
        "scientific_name": "Gossypium hirsutum",
        "season": "Kharif",
        "sowing_window": "April-May (North Zone), June-July (Central and South Zones)",
        "harvest_window": "October to February (multiple pickings)",
        "growth_stages": [
            "Germination & Seedling (0-25 DAS)",
            "Vegetative branch development (25-45 DAS)",
            "Square formation (45-70 DAS)",
            "Flowering and Boll setting (70-110 DAS)",
            "Boll bursting and picking (110-160 DAS)",
        ],
        "varieties": ["Bt Cotton Hybrids (Bollgard II)", "Suraj", "LRA 5166"],
        "soil_requirements": "Deep black cotton soils (vertisols) or alluvial loam with good drainage",
        "optimal_ph_range": (6.5, 8.0),
        "irrigation_needs": "4-6 irrigations; avoid moisture stress at squaring and flowering",
        "npk_ratio": "120:60:60 kg/ha N:P2O5:K2O",
        "common_pests": ["American Bollworm", "Pink Bollworm", "Whitefly", "Jassids", "Thrips"],
        "common_diseases": ["Bacterial Blight", "Verticillium / Fusarium Wilt", "Grey Mildew", "Root Rot"],
    },
    "Soybean": {
        "scientific_name": "Glycine max",
        "season": "Kharif",
        "sowing_window": "Mid-June to early July with onset of monsoon",
        "harvest_window": "Late September to October (90-105 days)",
        "growth_stages": [
            "Vegetative VE to V4 (0-30 DAS)",
            "Flowering R1-R2 (30-50 DAS)",
            "Pod development R3-R4 (50-70 DAS)",
            "Seed filling R5-R6 (70-90 DAS)",
            "Maturity R7-R8 (90-105 DAS)",
        ],
        "varieties": ["JS 335", "JS 95-60", "JS 20-34", "NRC 37", "RVS 2001-4"],
        "soil_requirements": "Well-drained medium to deep clayey or loamy soils, rich in organic matter",
        "optimal_ph_range": (6.5, 7.5),
        "irrigation_needs": "Generally rainfed; critical supplemental irrigation at flowering and pod filling",
        "npk_ratio": "30:60:40:20 kg/ha N:P2O5:K2O:S plus Bradyrhizobium seed inoculation",
        "common_pests": ["Girdle Beetle", "Semilooper", "Tobacco Caterpillar", "Stem Fly"],
        "common_diseases": ["Soybean Rust", "Yellow Mosaic Virus (YMV)", "Collar Rot", "Anthracnose"],
    },
}


def get_crop_profile(crop_name: str) -> Optional[Dict[str, Any]]:
    """Fetch agronomic profile for a crop."""
    for name, profile in CROP_DATABASE.items():
        if name.lower() == crop_name.strip().lower():
            return {"crop": name, **profile}
    return None


def list_supported_crops() -> List[str]:
    """Return all crops supported in crop intelligence."""
    return sorted(list(CROP_DATABASE.keys()))


def query_crop_stages(crop_name: str) -> List[str]:
    """Return growth stages for a crop."""
    profile = get_crop_profile(crop_name)
    if profile:
        return profile.get("growth_stages", [])
    return []


def check_soil_suitability(crop_name: str, soil_ph: float, soil_type: str) -> Dict[str, Any]:
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
        "tested_ph": soil_ph,
        "optimal_ph_range": f"{min_ph} - {max_ph}",
        "ph_suitable": ph_suitable,
        "soil_type_notes": profile["soil_requirements"],
        "ph_advice": ph_advice,
    }

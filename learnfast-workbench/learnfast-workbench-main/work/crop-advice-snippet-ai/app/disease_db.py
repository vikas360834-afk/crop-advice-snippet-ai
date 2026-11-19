"""Disease and Pest Knowledge Database.

Stores:
- Disease / pest name
- Affected crop
- Symptoms and affected plant parts
- Severity level
- Favourable environmental triggers (weather, temperature, humidity)
- Integrated Pest Management (IPM) methods & prevention
- Verified treatment references
- Safety disclaimer: Does not diagnose with certainty from symptoms alone.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

DISEASE_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "DIS-TOM-01",
        "name": "Early Blight",
        "causal_agent": "Alternaria solani (Fungus)",
        "crop": "Tomato",
        "plant_parts": "Leaves, stems, fruits",
        "symptoms": "Concentric dark brown rings resembling a target board, yellow halos around spots, lower leaf defoliation",
        "severity": "High",
        "favourable_conditions": "Warm temperatures (24-29C), high relative humidity, frequent dew or rain splash",
        "ipm_prevention": "Prune lower leaves up to 30 cm; use plastic mulch; 3-year rotation away from Solanaceae; drip irrigation.",
        "verified_treatment": "Preventive: Mancozeb 75 WP (2 g/L) or Chlorothalonil (2 g/L). Curative: Difenoconazole 25 EC (0.5 ml/L).",
        "expert_source": "ICAR-IIVR Varanasi & TNAU Plant Pathology",
    },
    {
        "id": "DIS-TOM-02",
        "name": "Late Blight",
        "causal_agent": "Phytophthora infestans (Oomycete)",
        "crop": "Tomato",
        "plant_parts": "Foliage, petioles, green and ripe fruits",
        "symptoms": "Water-soaked irregular pale green lesions turning dark brown to black, white moldy growth on leaf undersides in morning",
        "severity": "Critical",
        "favourable_conditions": "Cool cloudy weather (12-19C), persistent drizzle, relative humidity >90%",
        "ipm_prevention": "Avoid overhead watering; space plants widely for airflow; destroy volunteer potato and tomato plants.",
        "verified_treatment": "Systemic: Metalaxyl 8% + Mancozeb 64% WP (2.5 g/L) or Cymoxanil 8% + Mancozeb 64% WP (2 g/L).",
        "expert_source": "CPRI Shimla & FAO Plant Protection",
    },
    {
        "id": "DIS-TOM-03",
        "name": "Tomato Leaf Curl Virus (ToLCV)",
        "causal_agent": "Begomovirus (transmitted by Bemisia tabaci whitefly)",
        "crop": "Tomato",
        "plant_parts": "New leaves, shoots, flower buds",
        "symptoms": "Upward curling and puckering of leaves, vein clearing, stunted upright bushy plant growth, drastic flower drop",
        "severity": "Critical",
        "favourable_conditions": "Dry warm conditions (28-34C) favoring rapid whitefly vector reproduction",
        "ipm_prevention": "Raise seedlings under 40-mesh nylon net; hang yellow sticky cards (25/ha); plant barrier crops like maize.",
        "verified_treatment": "Target whitefly vector: Acetamiprid 20 SP (0.3 g/L) or NSKE 5% neem seed kernel extract.",
        "expert_source": "IIHR Bengaluru Tomato Protection Guide",
    },
    {
        "id": "DIS-WHT-01",
        "name": "Yellow / Stripe Rust",
        "causal_agent": "Puccinia striiformis f. sp. tritici (Fungus)",
        "crop": "Wheat",
        "plant_parts": "Leaves, leaf sheaths, glumes",
        "symptoms": "Bright yellow powder pustules arranged in narrow linear stripes parallel to leaf veins",
        "severity": "Critical",
        "favourable_conditions": "Cool humid weather (10-15C night, 15-20C day), morning dews, windblown spores",
        "ipm_prevention": "Sow recommended rust-resistant varieties (DBW 187, DBW 222, HD 3086); timely sowing in early November.",
        "verified_treatment": "Foliar spray Propiconazole 25 EC (0.1%) or Tebuconazole 250 EC at 500 ml/ha in 500 liters water.",
        "expert_source": "ICAR-IIWBR Karnal Rust Advisory",
    },
    {
        "id": "DIS-RIC-01",
        "name": "Rice Blast",
        "causal_agent": "Magnaporthe oryzae (Fungus)",
        "crop": "Rice",
        "plant_parts": "Leaves, nodes, panicle neck",
        "symptoms": "Spindle-shaped elliptical lesions with gray or whitish centers and brown margins; rotten black neck lesions",
        "severity": "Critical",
        "favourable_conditions": "High humidity (>90%), overcast skies, cool night temperatures (20-24C), excessive nitrogen",
        "ipm_prevention": "Treat seed with Carbendazim 2 g/kg seed; split nitrogen applications into 3 doses; avoid standing water drainage stagnation.",
        "verified_treatment": "Spray Tricyclazole 75 WP at 0.6 g/L or Azoxystrobin 18.2% + Difenoconazole 11.4% SC at 1 ml/L.",
        "expert_source": "ICAR-NRRI Cuttack Blast Management Bulletin",
    },
    {
        "id": "DIS-RIC-02",
        "name": "Bacterial Leaf Blight (BLB)",
        "causal_agent": "Xanthomonas oryzae pv. oryzae (Bacterium)",
        "crop": "Rice",
        "plant_parts": "Leaf blades, leaf sheaths",
        "symptoms": "Water-soaked lesions on leaf margins turning wavy yellowish-white stripes, milky bacterial ooze droplets in morning",
        "severity": "High",
        "favourable_conditions": "High temperature (25-34C), strong stormy winds, typhoons, excessive nitrogen top-dressing",
        "ipm_prevention": "Do not clip seedling leaf tips at transplanting; drain excess water; grow resistant cultivars like Improved Sambha Mahsuri.",
        "verified_treatment": "Spray Copper Hydroxide 77 WP (2 g/L) + Validamycin 3L (2 ml/L); suspend nitrogen top-dressing.",
        "expert_source": "IRRI & ICAR Rice Knowledge Portal",
    },
    {
        "id": "DIS-MAZ-01",
        "name": "Fall Armyworm (FAW)",
        "causal_agent": "Spodoptera frugiperda (Insect Pest)",
        "crop": "Maize",
        "plant_parts": "Central whorl leaves, tassels, cobs",
        "symptoms": "Pinhole window-pane feeding on young leaves, large ragged holes, heavy sawdust-like moist frass in whorl",
        "severity": "Critical",
        "favourable_conditions": "Warm dry spells followed by rain (26-32C)",
        "ipm_prevention": "Intercrop with cowpea; erect pheromone traps at 10/ha; drop sand-lime or wood ash into whorls.",
        "verified_treatment": "Direct spray Emamectin Benzoate 5 SG (0.4 g/L) or Spinetoram 11.7 SC (0.5 ml/L) into whorls at dawn or dusk.",
        "expert_source": "ICAR-IIMR Ludhiana & CIMMYT FAW Portal",
    },
    {
        "id": "DIS-POT-01",
        "name": "Late Blight of Potato",
        "causal_agent": "Phytophthora infestans (Oomycete)",
        "crop": "Potato",
        "plant_parts": "Foliage, stems, tubers",
        "symptoms": "Dark brown water-soaked blotches on leaf tips and margins with white fuzzy mildew underneath in morning mist; tuber dry rot",
        "severity": "Critical",
        "favourable_conditions": "Cool foggy weather (10-18C), relative humidity >90%, persistent cloudy weather",
        "ipm_prevention": "High earthing up to protect tubers from spore washing; use certified tubers; destroy wild potato heaps.",
        "verified_treatment": "Metalaxyl 8% + Mancozeb 64% WP at 2.5 g/L or Dimethomorph 50% WP (1 g/L) + Mancozeb (2 g/L).",
        "expert_source": "ICAR-CPRI Shimla Late Blight Warning Service",
    },
]

DISCLAIMER = (
    "DISCLAIMER: This diagnostic guide provides reference information based on published agronomic literature. "
    "Foliar symptoms can overlap between diseases, nutrient disorders, and weather stress. "
    "Always consult your local State Agricultural University or District Extension Officer before applying chemical pesticides."
)


def search_diseases(crop: Optional[str] = None, symptoms_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search diseases by crop and symptoms keywords."""
    results = list(DISEASE_DATABASE)
    if crop:
        results = [d for d in results if d["crop"].lower() == crop.strip().lower()]

    if symptoms_query:
        tokens = [t.lower() for t in symptoms_query.split() if t]
        matched = []
        for d in results:
            text = f"{d['name']} {d['symptoms']} {d['plant_parts']}".lower()
            if any(t in text for t in tokens):
                matched.append(d)
        results = matched

    return results


def get_disease_by_id(disease_id: str) -> Optional[Dict[str, Any]]:
    for d in DISEASE_DATABASE:
        if d["id"].lower() == disease_id.strip().lower():
            return d
    return None

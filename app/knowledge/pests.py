"""Agricultural Pest Knowledge Database.

Provides structured pest records:
- Pest name & scientific classification
- Affected crop
- Plant parts damaged & field symptoms
- Severity level
- Favourable environmental triggers
- Integrated Pest Management (IPM) & biological controls
- Chemical intervention guidelines
- Source verification references
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

PEST_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "PEST-RIC-01",
        "name": "Yellow Stem Borer",
        "scientific_name": "Scirpophaga incertulas",
        "crop": "Rice",
        "plant_parts": "Central tillers, growing points, panicle stems",
        "symptoms": "Dead hearts (central vegetative tillers dry up) and White heads (empty white panicles at heading)",
        "severity": "Critical",
        "favourable_conditions": "Warm humid weather (25-30C), relative humidity >80%, dense planting",
        "ipm_methods": "Clip seedling leaf tips before transplanting to remove egg masses; install pheromone traps at 20 traps/ha; release Trichogramma japonicum egg parasitoids at 100000/ha weekly.",
        "verified_treatment": "Apply Cartap Hydrochloride 4G at 25 kg/ha or Chlorantraniliprole 0.4G at 10 kg/ha in standing water when dead hearts exceed 5%.",
        "source": "ICAR-NRRI Cuttack",
    },
    {
        "id": "PEST-RIC-02",
        "name": "Brown Plant Hopper (BPH)",
        "scientific_name": "Nilaparvata lugens",
        "crop": "Rice",
        "plant_parts": "Lower stem base, tillers",
        "symptoms": "Hopper burn: circular patches of plants turning yellow, rapidly drying up and lodging, giving a burnt appearance",
        "severity": "Critical",
        "favourable_conditions": "High humidity, stagnant water in canopy, excessive nitrogen fertilizer, close spacing",
        "ipm_methods": "Provide 30 cm alleyways every 2-3 meters (skipping one row); alternate wetting and drying (AWD); conserve mirid bugs and spiders.",
        "verified_treatment": "Direct spray to the base of the plant: Triflumezopyrim 10 SC (94 ml/acre) or Pymetrozine 50 WG (120 g/acre). Avoid synthetic pyrethroids which cause resurgence.",
        "source": "IRRI & ICAR-NRRI",
    },
    {
        "id": "PEST-WHT-01",
        "name": "Wheat Aphid",
        "scientific_name": "Rhopalosiphum maidis / Sitobion avenae",
        "crop": "Wheat",
        "plant_parts": "Leaves, tender shoots, emerging ear heads",
        "symptoms": "Colonies of tiny greenish-black insects sucking sap, sticky honeydew with black sooty mold, shriveled grains",
        "severity": "High",
        "favourable_conditions": "Cloudy cool days (15-22C) followed by sudden warming in February-March",
        "ipm_methods": "Conserve Coccinellid ladybird predators (Coccinella septempunctata); spray 5% neem seed kernel extract (NSKE).",
        "verified_treatment": "Spray Thiamethoxam 25 WG at 0.2 g/liter or Imidacloprid 17.8 SL at 0.3 ml/liter if population exceeds 5 aphids per ear head.",
        "source": "ICAR-IIWBR Karnal",
    },
    {
        "id": "PEST-MAZ-01",
        "name": "Fall Armyworm (FAW)",
        "scientific_name": "Spodoptera frugiperda",
        "crop": "Maize",
        "plant_parts": "Central leaf whorl, emerging tassels, young ear cobs",
        "symptoms": "Pinhole window-paning on whorl leaves, extensive ragged torn leaves, moist sawdust-like fecal frass in central whorls",
        "severity": "Critical",
        "favourable_conditions": "Warm dry spells followed by rain (26-32C)",
        "ipm_methods": "Intercrop with cowpea or desmodium (push-pull strategy); install pheromone traps at 10/ha; drop sand-lime or wood ash mixture into whorls.",
        "verified_treatment": "Direct knapsack nozzle into central whorl: Emamectin Benzoate 5 SG at 0.4 g/liter or Spinetoram 11.7 SC at 0.5 ml/liter during dawn or dusk.",
        "source": "ICAR-IIMR Ludhiana",
    },
    {
        "id": "PEST-TOM-01",
        "name": "Whitefly",
        "scientific_name": "Bemisia tabaci",
        "crop": "Tomato",
        "plant_parts": "Underside of leaves, growing shoots",
        "symptoms": "Upward leaf curling, chlorosis, sooty mold, transmission of destructive Tomato Leaf Curl Virus (ToLCV)",
        "severity": "Critical",
        "favourable_conditions": "Dry warm conditions (28-34C)",
        "ipm_methods": "Erect yellow sticky cards at canopy level (25 cards/ha); grow barrier crops like maize/sorghum around border; raise nursery under 40-mesh net.",
        "verified_treatment": "Spray Acetamiprid 20 SP at 0.3 g/liter or Pyriproxyfen 10 EC at 1.5 ml/liter.",
        "source": "IIHR Bengaluru",
    },
    {
        "id": "PEST-COT-01",
        "name": "Pink Bollworm",
        "scientific_name": "Pectinophora gossypiella",
        "crop": "Cotton",
        "plant_parts": "Flowers (rosetted flowers), green bolls",
        "symptoms": "Rosetted flowers that fail to open properly; premature boll opening with stained lint and destroyed seeds",
        "severity": "Critical",
        "favourable_conditions": "Humid warm weather during square and boll development",
        "ipm_methods": "Install pheromone traps (PBW lure) at 5 traps/ha for monitoring; terminate crop by December to break cycle; release Trichogrammatoidea bactrae.",
        "verified_treatment": "Spray Chlorantraniliprole 18.5 SC at 0.3 ml/liter or Profenofos 50 EC at 2 ml/liter when moth catches exceed 8 moths/trap/night.",
        "source": "ICAR-CICR Nagpur",
    },
    {
        "id": "PEST-POT-01",
        "name": "Potato Tuber Moth (PTM)",
        "scientific_name": "Phthorimaea operculella",
        "crop": "Potato",
        "plant_parts": "Leaves (mines) and tubers in field and country storage",
        "symptoms": "Mined leaf veins; irregular tunnels in stored and exposed tubers filled with dark larval excrement",
        "severity": "High",
        "favourable_conditions": "Warm dry weather; shallow planted exposed tubers",
        "ipm_methods": "High earthing up to ensure no tubers are exposed to egg-laying moths; cover stored seed potatoes with 2.5 cm layer of dried Lantana camara leaves.",
        "verified_treatment": "Spray Chlorantraniliprole 18.5 SC (0.3 ml/L) in field before harvest; pheromone traps in godowns.",
        "source": "ICAR-CPRI Shimla",
    },
]


def search_pests(crop: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search agricultural pests by crop name and symptoms/name query."""
    results = list(PEST_DATABASE)
    if crop:
        results = [p for p in results if p["crop"].lower() == crop.strip().lower()]

    if query:
        tokens = [t.lower() for t in query.split() if t]
        matched = []
        for p in results:
            text = f"{p['name']} {p['scientific_name']} {p['symptoms']} {p['plant_parts']}".lower()
            if any(t in text for t in tokens):
                matched.append(p)
        results = matched

    return results

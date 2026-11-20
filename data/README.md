# Agricultural dataset provenance

Audit snapshot: 2026-11-20. This is the date this repository copy was inspected, not a claimed download date for the source material.

## Structured source dataset

The checked-in `raw/agriculture.jsonl` contains 20 short, normalized advice records:

| Crop | Records |
|---|---:|
| Rice | 5 |
| Maize | 5 |
| Wheat | 5 |
| Tomato | 5 |
| **Total** | **20** |

Each record has these fields: `id`, `crop`, `topic`, `text`, `source_name`, and `source_url`. The audit found 20 unique IDs, 20 non-empty source names, and 20 HTTPS source URLs.

Source attribution by record:

| Attribution label in JSONL | Records |
|---|---:|
| TNAU Agritech - Rice irrigation management | 3 |
| TNAU Agritech - Rice nutrient management | 1 |
| TNAU Agritech - Rice cultivation FAQs | 1 |
| TNAU Agritech - Maize irrigation management | 2 |
| TNAU Agritech - Wheat crop management | 4 |
| TNAU Agritech - Good Agricultural Practices for fertilizer use | 1 |
| TNAU Agritech - Tomato soil and field preparation | 2 |
| TNAU Agritech - Organic tomato water requirements | 1 |
| TNAU Agritech - Tomato cultural practices | 1 |
| TNAU Agritech - Tomato fertigation | 1 |
| ICAR - Kharif Agro-Advisories for Farmers 2025 | 3 |
| **Total** | **20** |

The record-level `source_url` is the canonical attribution for each JSONL row. The source URLs currently represented are:

- Rice irrigation: https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_cereals_rice1.html
- Rice irrigation / critical stages: https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_cereals_rice.html
- Rice nutrient management: https://www.agritech.tnau.ac.in/agriculture/agri_cropproduction_cereals_rice_tranpudlow_mainfield_nutrient_mgmt_inorganic.html
- Rice cultivation FAQs: https://www.agritech.tnau.ac.in/expert_system/paddy/faqs.html
- Maize irrigation: https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html
- ICAR Kharif advisory (2025): https://icar.gov.in/sites/default/files/Circulars/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf
- Wheat crop management: https://agritech.tnau.ac.in/agriculture/agri_cropproduction_wheat_aftercultivation.html
- Fertilizer good agricultural practices: https://agritech.tnau.ac.in/gap_gmp_glp/gmp_fertilizer%20use.html
- Tomato soil / field preparation: https://agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_Soil.html
- Tomato water requirements: https://www.agritech.tnau.ac.in/org_farm/orgfarm_tomato_water.html
- Tomato cultural practices: https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_cultural%20practices.html
- Tomato fertigation: https://agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_fertigation.html

## Date and verification limits

The JSONL schema currently has no publication-date or source-retrieval-date field. All 20 rows therefore have an unknown publication date. No date has been inferred or fabricated. Some TNAU pages expose page-level update or copyright information (for example, the maize irrigation page says it was updated in 2013 and the tomato fertigation page says June 2023); those page notices have not been assigned to individual records.

The TNAU rice irrigation, maize irrigation, wheat crop-management, and tomato fertigation pages were spot-checked during the 2026-11-20 audit. The ICAR 2025 PDF URL is present in the three attributed records, but the full PDF was not independently re-reviewed during this audit. A source URL proves attribution metadata is present; it does not by itself prove that every sentence in a record is a complete or current recommendation.

The records are concise summaries, not a copy of the full source publications. Before using a recommendation in practice, check the linked source, current local label and regional agricultural guidance. This repository is an educational software project, not an agronomy authority.

## Separate model-training text

The root-level `data/agricultural_corpus.txt` is a separate expanded training-text file. Its plain-text entries do not carry a record-level `source_name` and `source_url` alongside each advice item. The 20-row JSONL attribution above must not be assumed to establish provenance for every line in that separate text file. Treat those entries as unverified training material until a line-by-line source map and review are added.

## Re-run the metadata audit

From the repository root:

```powershell
python -m tools.validate_source_dataset
```

The validator checks JSONL parsing, required fields, unique IDs, HTTPS source URLs, crop/source counts, and reports missing publication dates as a warning rather than inventing them.

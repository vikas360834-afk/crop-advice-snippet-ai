# Crop Advice Snippet AI

A command-line tool that gives short, crop-specific agricultural advice. It combines a small GPT model trained from scratch on farming text (byte-pair tokenizer, embeddings, causal self-attention) with a crop registry, a disease and pest database, weather checks, and a records store.

## Quick start

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python tools/generate_crop_registry.py   # builds data/crops/crop_registry.json
python -m tools.seed_sample_records      # writes two sample tomato records
pytest -q
python -m app.cli hello
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1` and copy the environment file with `Copy-Item .env.example .env`.

## Example commands

```bash
python -m app.cli advice --crop Tomato --problem "early blight"
python -m app.cli crops search --query mango
python -m app.cli records list --crop tomato
python -m tools.measure_advice
```

Example output from `advice`. It matches the stored sample record for tomato early blight:

```
[*] CROP ADVICE SNIPPET AI: TOMATO
Issue/Problem : early blight
Advice Snippet:
Remove infected leaves and apply a copper-based fungicide at first symptoms of early blight.
```

## Example results

Pest and IPM lookup (`python -m app.cli pest search --crop rice`), first entry:

```
[PEST-RIC-01] Yellow Stem Borer (Scirpophaga incertulas)
  Crop      : Rice | Parts: Central tillers, growing points, panicle stems
  Symptoms  : Dead hearts (central vegetative tillers dry up) and White heads (empty white panicles at heading)
  Severity  : Critical | Weather: Warm humid weather (25-30C), relative humidity >80%, dense planting
  Source    : ICAR-NRRI Cuttack
```

Weather advisory (`python -m app.cli weather --crop Tomato --temp 32 --humidity 85 --rainfall 40`):

```
METEOROLOGICAL RISK ADVISORY FOR TOMATO
Conditions : Temp 32.0 C | Humidity 85.0% | Rain 40.0 mm | Wind 8.0 km/h
Identified Risks:
  - MODERATE: Fungal sporulation warning
  - HIGH: Soil Waterlogging & Root Asphyxiation Risk
Spraying Window: UNFAVOURABLE: Postpone spraying. Rainfall imminent; applied chemical wash-off will occur.
```

## How advice is produced

The GPT model writes advice from the crop and problem. If its text is too short, too repetitive, or lacks agricultural terms, the tool uses the stored record for that crop. If there is no record, it uses a generic sentence.

## Evaluation

- **Automated tests:** 20 tests cover the CLI, the crop registry, the records store, and the tokenizer and embedding code. They run on every push in GitHub Actions.
- **Where answers come from:** `python -m tools.measure_advice` ran 10 fixed crop and problem queries. 6 answers (60%) came from the model's own text, 2 (20%) from a stored record, and 2 (20%) from the generic sentence. Details are in `results/measure_advice.csv`.
- **Quality (source-checked):** all 8 model and record answers were checked against published guidance. The checks were done by an AI assistant, not an expert.

| Crop | Problem | Source | Verdict | What the source says |
|---|---|---|---|---|
| Tomato | early blight | record | unverified | The checked guidance names other fungicides, not copper, and does not mention removing infected leaves. |
| Tomato | irrigation | record | partial | Regular irrigation and drip are supported. The source ties cracking to drought followed by sudden watering, not to waterlogging. |
| Rice | yellow stem borer | model | partial | Products and the 10 kg/ha granule rate are confirmed. Moth-flight timing is not supported, and the pheromone trap count was not found. |
| Rice | blast disease | model | partial | Azoxystrobin is confirmed. The advice to drain standing water contradicts the source, which warns against drainage and excess nitrogen. Tricyclazole was not found. |
| Wheat | rust disease | model | pass | Propiconazole and tebuconazole are listed for use before flag leaf emergence. |
| Maize | fall armyworm | model | unverified | The source page had no article text. |
| Potato | late blight | model | partial | Metalaxyl is listed only in mixtures, cymoxanil needs a partner, and metalaxyl resistance is documented. |
| Mango | anthracnose | generic | fail | The answer is about a different problem. |
| Chilli | leaf curl | generic | fail | The answer is about a different problem. |
| Cotton | bollworm | model | partial | Rotating insecticides and indoxacarb as a monitored product are confirmed. Spinosad, Bt, and egg counts are not. |

Overall: 1 pass, 5 partial, 2 unverified, 2 fail. Of the 8 model and record answers, 1 is confirmed, 5 are partly confirmed, and 2 are not confirmed.

Notes on the partial answers: the rice advice applies granules during moth flight rather than at the dead-heart stage, and the potato advice offers metalaxyl or cymoxanil alone, while resistance management calls for mixtures. No answer gives dosages.

## Limitations

- The bundled sample has only two tomato records, so the record fallback covers tomato only.
- About 40% of answers in the test set used a fallback, so the model's own text is not always usable.
- The measurement covers only 10 queries.
- The crop registry is generated from hand-entered data that has not been independently checked.
- The weather advisory uses only the values you type in and fixed rules. It does not fetch live weather.
- This is a learning project. Check any advice with a local agronomist before acting on it.

## Origin

This project started from a course starter template, which provided the milestone structure, the CI workflow, and the test scaffolding. The crop registry data, disease and pest database, records store, weather checks, and CLI commands were written for this project.

## Settings and secrets

Model settings live in `.env`, which is ignored by git. Never commit `.env` or paste a key into code. If a key ever reaches GitHub, treat it as leaked and make a new one.

## Stretch ideas

- Curate a larger and more diverse agricultural dataset.
- Let users add soil type, weather, and growth stage to tailor advice. The CLI already accepts these options; the next step is to measure whether they change the output.
- Add a feedback command so users can rate advice.

## License

MIT. See [LICENSE](LICENSE).




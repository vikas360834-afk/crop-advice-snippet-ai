# Agricultural dataset provenance

The model's training corpus is generated from the checked-in `raw/agriculture.jsonl` file. The former 59-entry plain-text corpus had no reliable per-entry source mapping, so it has been removed from the training path and deleted rather than assigning invented citations.

## Trusted source dataset

The JSONL file contains 20 normalized advice records: 5 each for rice, maize, wheat and tomato. Every row includes:
- `id`, `crop`, `topic`, and `text`;
- `source_name` and an exact HTTPS `source_url`.

The 20 rows have unique IDs, non-empty source names and HTTPS source URLs. Source attribution is attached to each record and is included in the generated training text. The loader rejects rows missing any of these required fields.

## Source and date limitations

The dataset does not currently contain publication dates or retrieval dates. These dates remain unknown and are not guessed. The presence of a source URL records attribution; it does not prove that every summarized sentence is complete, current or suitable for every region.

Sources represented include Tamil Nadu Agricultural University (TNAU) Agritech pages and the ICAR Kharif Agro-Advisories for Farmers 2025 PDF. See [`SOURCES.md`](SOURCES.md) for a readable register mapping every record ID to its exact source URL; the canonical record-level metadata remains in `raw/agriculture.jsonl`.

These are concise educational summaries. Check the linked publication, current product labels and regional agricultural guidance before acting on a recommendation. The project is not an agronomy authority.

## Rebuild and audit

From the repository root:

```powershell
python -m tools.validate_source_dataset
python -m pytest -q
```

The runtime corpus at `data/trusted_training_corpus.txt` is generated from the attributed JSONL rows and is ignored by git. It is rebuilt rather than loaded from an older plain-text corpus.

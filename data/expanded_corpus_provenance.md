# Expanded agricultural training corpus: provenance status

Audit date: 2026-11-20.

The plain-text training corpus contains 59 advice entries. It is separate from `raw/agriculture.jsonl`, which has 20 structured records with record-level source URLs.

## Provenance limitation

The current plain-text entries do not contain a per-entry source URL, source publication title, publication date, or retrieval date. The sources for individual lines cannot be established reliably from the text alone. The structured JSONL file's citations must not be used as blanket citations for these separate entries.

Accordingly, the expanded text corpus is classified as **unverified training material** until each entry has been traced to a current, authoritative publication and reviewed. Do not rely on it as an agronomic recommendation dataset in production. In particular, do not infer a source from crop/topic similarity or attach a general TNAU/ICAR portal URL to an entry without verifying the content.

## Required curation format

For each retained training entry, maintain a companion provenance manifest with:
- stable entry ID (for example, `wheat-001`);
- crop and topic;
- source institution and publication/page title;
- exact source URL;
- publication or update date as stated by the source (otherwise `unknown`);
- retrieval date;
- reviewer and review status;
- notes on whether the advice accurately reflects the source and applies to the target region.

Only after independent source review should an entry be copied into a trusted training corpus. Remove or quarantine entries that cannot be traced or contain recommendations inconsistent with current local guidance.

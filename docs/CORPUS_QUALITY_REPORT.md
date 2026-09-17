# AfriBERTa Afaan Oromoo Corpus — Initial Quality Report

## Dataset

- Dataset: AfriBERTa Corpus
- Subset: afaanoromoo
- Language: Afaan Oromoo
- ISO 639-3: orm
- Modality: Text
- Intended use: Language-model pretraining
- Source: CastorAI / AfriBERTa
- License: Apache-2.0
- Upstream sources: Primarily BBC News with additional Common Crawl data
- Acquisition date: 2026-09-13

## Raw Acquisition

The original archives were downloaded without modification.

### Training archive

- File: `data/raw/afriberta_oromo/train.zip`
- Contents: `train.txt`
- Archive SHA-256:
  `06061756970746d77188461866c859523170731395217978372791bf0ccc22f5`
- Integrity: VERIFIED

### Evaluation archive

- File: `data/raw/afriberta_oromo/eval.zip`
- Contents: `eval.txt`
- Archive SHA-256:
  `0dbf7a83bcf153a49ad9dea41e478c9526fcdf781e8f7a01168279f24cdc78e5`
- Integrity: VERIFIED

## Initial Observations

Manual inspection of the first records shows genuine Afaan Oromoo text with:

- Qubee orthography
- Oromo-specific vocabulary
- Oromo diacritics
- proper names
- political and historical content
- foreign names and terminology
- web/editorial extraction artifacts

The corpus must therefore be treated as a mixed web/news corpus rather than perfectly curated literary Oromo.

## Web Artifact Signals

Initial train-corpus scan:

| Signal | Occurrences |
|---|---:|
| Read More | 1,110 |
| Embed markers | 15 |
| URLs | 172 |
| Comments Off | 167 |
| HTML-like markup | 32 |

These measurements are diagnostic only. No cleaning has been applied.

## Orthographic Observations

Observed Unicode character counts in the training corpus:

| Character | Count |
|---|---:|
| Q | 41,695 |
| q | 340,997 |
| X | 9,027 |
| x | 67,411 |
| C | 35,367 |
| c | 330,451 |
| G | 86,002 |
| g | 782,016 |
| `ʼ` | 217 |
| `’` | 172,838 |
| `'` | 189,312 |

These values demonstrate substantial representation of Oromo orthographic patterns.

Apostrophe-like characters must not be normalized blindly because they may represent different linguistic or punctuation functions.

## English-Language Signal

A broad English stopword-pattern scan produced:

- 26,946 English common-word matches

This is **not classified as contamination**. Individual English words may occur legitimately in Oromo text through:

- proper names
- quoted material
- titles
- technical terminology
- bilingual passages
- URLs
- source metadata

Record-level language analysis is required before removing any material.

## Evaluation Set Policy

The evaluation corpus is considered a held-out resource.

It must not be:

- used for training
- deduplicated against training data
- used to tune cleaning rules
- used to make training-set decisions
- modified during corpus preprocessing

Any future contamination analysis of the evaluation set must be diagnostic and non-destructive.

## Current Decision

Status: **ACQUIRED — RAW DATA VERIFIED — QUALITY AUDIT IN PROGRESS**

The corpus is not yet approved for model training.

No cleaning or destructive transformation has been written to the raw corpus. Cleaning was evaluated only in memory during the non-destructive dry-run; no processed corpus was produced.

## Next Steps

1. Complete quantitative train-corpus profiling.
2. Establish conservative cleaning rules.
3. Implement cleaning as reproducible code.
4. Test cleaning rules against representative examples.
5. Deduplicate after normalization.
6. Generate a processed dataset and processing manifest.
7. Validate the processed corpus.
8. Keep the original raw archives immutable.

---

## Dry-Run Verification Checkpoint

**Status:** NON-DESTRUCTIVE AUDIT COMPLETE — PRODUCTION CLEANING NOT YET APPROVED

### Exact Audited Source

The extracted AfriBERTa Afaan Oromoo training corpus used for the dry-run is:

`data/raw/afriberta_oromo/train/train.txt`

Source fingerprint:

- SHA-256: `269cde87d84ad34463b7bd654b16737aeef756adbe2463518353004660187d6a`
- Parsed records: `410,841`
- File size: approximately `51 MB`
- `wc -l`: `410,840` (expected when the final record has no trailing newline)

### Dry-Run Results

The complete training corpus was processed in non-destructive audit mode.

- Input records: `410,841`
- KEEP: `409,916`
- CLEAN: `360`
- REJECT: `565`
- Changed records: `264`
- Unchanged CLEAN decisions: `96`
- Empty after cleaning: `0`
- Repetition signals: `156`
- Input characters: `52,285,106`
- Simulated post-clean characters: `52,280,019`
- Characters removed: `5,087`
- Change rate: `0.0643%`
- Character reduction: `0.0097%`

### Audit Interpretation

The audit indicates that the selected corpus is predominantly usable Oromo text, with a small number of records requiring conservative cleaning or rejection.

The current decision policy intentionally preserves potentially legitimate linguistic, cultural, historical, political, religious, technical, quoted, dialectal, and code-switching content unless there is sufficient structural evidence that a record is contamination, extraction garbage, or another clearly unsuitable payload.

Repetition signals remain diagnostic and are not automatically rejected.

URLs and CMS artifacts are treated conservatively. Cleaning decisions do not authorize semantic rewriting.

### Non-Destructive Guarantee

The dry-run:

- did not modify the raw source;
- did not delete records;
- did not write a cleaned training corpus;
- did not modify the evaluation corpus;
- produced a machine-readable JSON report.

Report:

`reports/afriberta_oromo_train_dry_run.json`

Dry-run implementation version:

`0.1.0`

### Current Decision

**The corpus has passed the initial contamination audit checkpoint, but production cleaning is still pending.**

Before training approval, the project must:

1. Implement the production line-oriented cleaning pipeline.
2. Preserve the raw corpus unchanged.
3. Apply decisions deterministically.
4. Validate cleaned records.
5. Reject records that become empty or fail validation.
6. Deduplicate after cleaning.
7. Generate a complete provenance manifest.
8. Re-audit the resulting processed corpus.
9. Verify record counts and character statistics.
10. Keep the evaluation split isolated and untouched.
11. Perform final human review of representative CLEAN and REJECT samples.
12. Only then consider the resulting corpus for model training.

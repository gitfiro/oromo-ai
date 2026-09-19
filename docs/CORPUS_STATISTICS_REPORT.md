# Afaan Oromoo Corpus Statistics Report

<p align="center">
  <strong>Oromo AI — Production Corpus Statistics</strong><br>
  <em>AfriBERTa Afaan Oromoo Corpus — v0.1.2</em>
</p>

---

## 1. Report Purpose

This document records the statistical profile and validation state of the current production Afaan Oromoo corpus used by the Oromo AI project.

The report is intended to provide:

* reproducible dataset statistics
* corpus-size measurements
* token and character distributions
* quality diagnostics
* rejection statistics
* version-to-version comparisons
* integrity checks
* provenance information
* evidence for downstream tokenizer and model decisions

This report describes the **processed v0.1.2 dataset**.

It does not replace the raw source dataset.

---

# 2. Dataset Identity

| Field                   | Value                          |
| ----------------------- | ------------------------------ |
| Dataset                 | AfriBERTa Afaan Oromoo corpus  |
| Dataset subset          | `afaanoromoo`                  |
| Project dataset version | `afriberta_oromo_v0.1.2`       |
| Language                | Afaan Oromoo                   |
| ISO 639-3               | `orm`                          |
| Country metadata        | ET                             |
| Source                  | `castorini/afriberta-corpus`   |
| License                 | Apache-2.0                     |
| Processing approach     | Conservative, provenance-first |
| Raw source format       | Text / line-oriented           |
| Processed format        | JSONL                          |
| Processing version      | `0.1.0`                        |

The source corpus is retained separately from the processed corpus.

---

# 3. Source Integrity

The authoritative raw training text is:

```text
data/raw/afriberta_oromo/train/train.txt
```

Raw training file SHA-256:

```text
269cde87d84ad34463b7bd654b16737aeef756adbe2463518353004660187d6a
```

This hash is used as an input integrity anchor.

The processed dataset must never be interpreted independently of its source and processing metadata.

---

# 4. Production Dataset

Current production output:

```text
data/processed/afriberta_oromo_v0.1.2/train.jsonl
```

Validated processed SHA-256:

```text
6f990088c8fb319b46c9a25a1c463e7a700cc8d292da781cfcc44ac4391ee0f6
```

## Core statistics

| Metric                           |      Value |
| -------------------------------- | ---------: |
| Raw input records                |    410,841 |
| Processed records                |    410,193 |
| Primary rejected records         |        614 |
| Duplicate-after-cleaning records |         34 |
| Clean decisions                  |        360 |
| Changed records                  |        264 |
| Processed characters             | 52,122,367 |
| Rejection-ledger entries         |        648 |

The 648 ledger entries consist of:

```text
614 primary rejection records
+
34 duplicate-after-cleaning records
=
648 ledger entries
```

---

# 5. Processing Accounting

The production accounting is:

```text
410,841 input records
        │
        ├── 410,193 processed records
        │
        ├── 614 primary rejections
        │
        └── 34 duplicates removed
```

Therefore:

```text
410,193 + 614 + 34 = 410,841
```

This invariant passes.

The 34 duplicate records are represented in the rejection ledger so that deduplication remains auditable.

---

# 6. v0.1.1 → v0.1.2 Comparison

Version `0.1.2` is a targeted update to the previous production dataset.

| Metric                      |     v0.1.1 |     v0.1.2 | Delta |
| --------------------------- | ---------: | ---------: | ----: |
| Records                     |    410,242 |    410,193 |   -49 |
| Characters                  | 52,122,995 | 52,122,367 |  -628 |
| Records under 20 chars      |        694 |        645 |   -49 |
| High single-character ratio |        321 |        272 |   -49 |
| Placeholder records         |        188 |        139 |   -49 |
| URL records                 |         46 |         46 |     0 |
| HTML records                |          0 |          0 |     0 |
| English-signal records      |      3,988 |      3,988 |     0 |

The comparison demonstrates that the v0.1.2 change was narrowly targeted.

Exactly:

```text
49 records
628 characters
```

were removed.

No change occurred in the reported URL, HTML, or English-signal counts.

---

# 7. Short-Record Investigation

The initial v0.1.1 corpus contained:

```text
694 records under 20 characters
```

Shortness alone was not considered sufficient evidence of corruption.

The short records were therefore investigated by structural characteristics.

Observed categories included:

* potential linguistic text
* numeric/table fragments
* symbol-heavy text
* spaced-letter extraction
* control-character cases
* records without meaningful word content

Examples included:

```text
a f a a n i
```

```text
2 H * 1 amu = 2 amu
```

```text
K U T A A – 1
```

```text
TA 1 E E ■ ■
```

These examples demonstrate why a blanket short-record filter would be unsafe.

---

# 8. Targeted Extraction-Artifact Rule

The v0.1.2 processor introduced a narrow rule for a specific extraction-artifact pattern.

A record is classified as a short extraction artifact only when all relevant structural conditions are met:

```text
length < 20 characters
+
at least 3 tokens
+
≥75% single-character tokens
+
placeholder/replacement glyph present
```

Placeholder/replacement indicators include:

```text
■
□
�
```

The rule is intentionally narrow.

It does not reject a record simply because:

* it is short
* it contains one-character tokens
* it contains numbers
* it resembles a formula
* it contains repeated letters

---

# 9. Effect of the Targeted Rule

The rule identified:

```text
49 records
```

for rejection.

Before the rule:

```text
placeholder records = 188
```

After the rule:

```text
placeholder records = 139
```

Difference:

```text
188 - 139 = 49
```

The high single-character-ratio population changed by the same amount:

```text
321 → 272
```

This correspondence is consistent with the intended narrow targeting.

---

# 10. Ambiguous Oromo Text

The following type of text is deliberately preserved when there is insufficient evidence of corruption:

```text
a f a a n i
```

A spaced character sequence could represent:

* extraction corruption
* OCR behavior
* typography
* a linguistic artifact
* legitimate source formatting

Without sufficient evidence, the pipeline does not silently destroy it.

This is particularly important for low-resource-language corpus construction.

---

# 11. Formula and Numeric Preservation

Numeric and formula-like records are not automatically rejected.

For example:

```text
2 H * 1 amu = 2 amu
```

and similar records may originate from educational or scientific material.

The pipeline therefore distinguishes:

```text
numeric signal
```

from:

```text
confirmed unusable extraction
```

The presence of numbers alone is not sufficient for deletion.

---

# 12. Rejection Statistics

The v0.1.2 rejection ledger contains:

| Rejection reason           |   Count |
| -------------------------- | ------: |
| Scientific/genomic payload |     308 |
| Social-media spam          |     144 |
| Obvious extraction garbage |     111 |
| Short extraction artifact  |      49 |
| Duplicate after cleaning   |      34 |
| Technical/code payload     |       1 |
| Base64/data URI            |       1 |
| **Total**                  | **648** |

The first six categories represent content-processing decisions.

The duplicate category represents post-cleaning deduplication.

---

# 13. Scientific / Genomic Payloads

The decision engine identifies strong scientific/genomic contamination signals such as combinations involving:

* DNA
* genomic sequences
* PCR
* primers
* amplicons
* nucleotide sequences
* chromosomes
* microsatellites
* cDNA
* sequencing
* genotype/genotyping

Long sequence-like payloads and domain-specific scientific structures are also considered.

These rules are deliberately stronger than the general diagnostic audit.

Consequently, the decision-engine count for scientific/genomic payloads should not be expected to equal the narrower diagnostic audit category count.

---

# 14. Social-Media Spam

The corpus contains records exhibiting combinations of:

* excessive hashtags
* excessive handles
* low lexical diversity
* social-media formatting
* spam-like structures

These are evaluated as corpus-quality signals rather than as evidence that every social-media-derived record is inherently unusable.

The production processor currently rejects records that meet the project's strong spam criteria.

---

# 15. Cleaning Statistics

The production processor reports:

```text
clean decisions: 360
changed records: 264
```

Cleaning is applied only when a record meets a supported cleaning condition.

The cleaner may perform operations such as:

```text
Unicode NFC normalization
whitespace normalization
HTML removal
URL removal
CMS boilerplate removal
embed-marker removal
terminal/bracketed Read More cleanup
```

The cleaner does not perform semantic rewriting.

---

# 16. Read More Handling

`Read More` was specifically investigated because it appeared in multiple forms.

Observed classes included:

```text
bracketed_read_more
terminal_read_more
other
embedded_read_more
```

Not every occurrence is treated as corruption.

For example:

```text
Read more about Mitikkuu Maddaa...
```

can be legitimate prose.

Therefore the production cleaner removes only structurally obvious CMS artifacts while preserving ambiguous linguistic content.

---

# 17. Deduplication

Deduplication occurs after cleaning.

The normalization used for hashing includes:

* Unicode NFC normalization
* whitespace collapsing

The deduplication process intentionally does not:

* lowercase text
* remove punctuation
* ASCII-fold characters
* perform semantic normalization

This protects Oromo orthographic distinctions.

The v0.1.2 validation confirms:

```text
duplicate cleaned hashes = 0
```

in the final processed output.

---

# 18. Corpus Length Statistics

The previous production statistics provide the following distribution for v0.1.1:

| Statistic          | Value |
| ------------------ | ----: |
| Minimum characters |     1 |
| Median characters  |   103 |
| Mean characters    | 127.1 |
| 95th percentile    |   289 |
| 99th percentile    |   483 |
| Maximum characters | 3,680 |

Whitespace-token statistics:

| Statistic                |     Value |
| ------------------------ | --------: |
| Total whitespace tokens  | 6,882,693 |
| Unique whitespace tokens |   537,014 |
| Type-token ratio         |  0.078024 |
| Median tokens / record   |        14 |
| Mean tokens / record     |      16.8 |
| 95th percentile          |        37 |
| 99th percentile          |        61 |
| Maximum                  |       343 |

These values describe the previously generated corpus-statistics snapshot and should be regenerated against v0.1.2 if exact final-distribution statistics are required.

---

# 19. Corpus Size Interpretation

The corpus contains approximately:

```text
6.9 million whitespace tokens
```

This is a valuable Oromo-language seed corpus, but it is not sufficient by itself to represent a modern large-scale foundation-model training mixture.

The official expansion objective is:

| Milestone | Target |
| --- | ---: |
| OromoCorpus v0.2 | **50 million net unique OromoLM-tokenizer tokens minimum** |
| OromoCorpus v0.3 | **100 million net unique OromoLM-tokenizer tokens preferred** |

These targets are not raw download totals. They are measured after conservative cleaning and cross-source exact/near-duplicate removal. Evaluation holdouts are excluded, and synthetic or machine-translated datasets are tracked separately from the primary natural-language total.

The corpus should therefore be treated as:

```text
high-value seed data
```

rather than:

```text
complete Oromo pretraining corpus
```

Future acquisition should expand:

* domain coverage
* document length
* literary material
* educational content
* conversational language
* dialect coverage
* parallel text
* terminology
* high-quality curated sources

---

# 20. Short-Record Distribution

The v0.1.2 dataset contains:

```text
645 records under 20 characters
```

This remains a small but important population for future inspection.

The project intentionally does not assume that all short records are corrupted.

Future corpus versions may use:

* document reconstruction
* source metadata
* neighboring-record analysis
* source-specific structure
* human linguistic review

to determine whether short records can safely be improved.

---

# 21. English-Signal Statistics

The previous corpus statistics identified:

```text
3,988 records
```

containing matches to a small common-English signal list in the processed corpus.

This represents approximately:

```text
3,988 / 410,242 ≈ 0.97%
```

for the v0.1.1 snapshot.

This should **not** be interpreted as:

```text
0.97% English contamination
```

The diagnostic can capture:

* names
* organizations
* borrowed terminology
* technical vocabulary
* quoted text
* URLs or metadata
* legitimate bilingual material

English-signal detection is therefore diagnostic only.

---

# 22. URLs and HTML

The v0.1.1 → v0.1.2 comparison shows:

```text
URL records:
46 → 46

HTML records:
0 → 0
```

The unchanged URL count demonstrates that the short-extraction rule did not alter this population.

HTML detection reports zero residual HTML records in both versions.

---

# 23. Integrity Validation

The production v0.1.2 dataset passed the following checks:

```text
raw_hash_correct       = True
manifest_count_matches = True
manifest_chars_match   = True
no_malformed_json      = True
no_empty_records       = True
no_duplicate_hashes    = True
source_lines_unique    = True
accounting_correct     = True
```

### Raw hash

```text
269cde87d84ad34463b7bd654b16737aeef756adbe2463518353004660187d6a
```

### Processed hash

```text
6f990088c8fb319b46c9a25a1c463e7a700cc8d292da781cfcc44ac4391ee0f6
```

These values provide reproducibility anchors for the current dataset version.

---

# 24. JSON Integrity

Production validation found:

```text
malformed_json = 0
empty_records = 0
```

The processed JSONL therefore passes the current structural integrity checks.

Each processed record remains traceable through deterministic source-line identifiers.

---

# 25. Source-Line Uniqueness

The production validation reports:

```text
unique_source_lines = 410,193
```

This means every surviving processed source line has a unique source-line identity.

The raw source line number is retained as part of deterministic record provenance.

---

# 26. Manifest

The production manifest records metadata required to identify the dataset version.

Important fields include:

```text
dataset name
dataset version
language
license
source
source URL
record count
character count
processing version
source hash
processing statistics
decision counts
rejection information
```

The manifest should be considered part of the dataset artifact, not optional documentation.

---

# 27. Why Statistics Matter for the Model

Corpus statistics directly influence later engineering decisions.

For example:

### Tokenizer

Character and word distributions help determine whether an existing tokenizer represents Oromo efficiently.

### Continued pretraining

Corpus size determines how much additional Oromo text must be acquired before meaningful continued pretraining.

### Data mixture

Short-record and domain distributions help identify missing sources.

### Evaluation

Corpus weaknesses can become benchmark categories.

### Model architecture

Token fertility and sequence lengths influence context-window and training-cost decisions.

---

# 28. Limitations

This dataset should not be treated as a complete representation of Afaan Oromoo.

Known limitations include:

* limited total corpus size
* source-domain concentration
* possible news-domain bias
* Common Crawl-derived material
* limited explicit dialect metadata
* limited document-boundary information
* short extracted records
* possible residual web artifacts
* limited conversational coverage
* incomplete literary coverage

These limitations are documented rather than hidden.

---

# 29. Next Corpus Work

The next data-engineering priorities are:

```text
1. Acquire additional licensed Oromo sources
2. Improve document-level reconstruction
3. Expand dialect metadata
4. Expand domain metadata
5. Build source-specific quality profiles
6. Add additional parallel corpora
7. Build instruction data
8. Build evaluation data
9. Measure tokenizer efficiency
10. Construct the broader OromoCorpus
11. Reach 50M net unique OromoLM-tokenizer tokens for v0.2
12. Expand toward 100M tokens with stronger domain and dialect balance for v0.3
```

The goal is not merely to increase record count.

The goal is to increase:

```text
quality
coverage
diversity
provenance
linguistic usefulness
```

Progress toward 50M and 100M must be reported by source, license, domain, dialect where known, raw size, retained size, duplicate loss, and final OromoLM-tokenizer count. No source's advertised size should be counted before it passes the production pipeline.

---

# 30. Production Dataset Principle

The current corpus pipeline follows:

```text
RAW SOURCE
    │
    ▼
HASH
    │
    ▼
AUDIT
    │
    ▼
DECISION ENGINE
    │
    ├───────────────┐
    ▼               ▼
  KEEP             CLEAN
    │               │
    │               ▼
    │            VALIDATE
    │               │
    └───────┬───────┘
            ▼
       DEDUPLICATE
            │
            ▼
     PROCESSED CORPUS
            │
            ├── manifest
            │
            └── rejection ledger
```

This architecture is designed to make every production dataset version explainable.

---

# 31. Current Conclusion

`afriberta_oromo_v0.1.2` is the current validated production corpus version.

Its most important properties are:

```text
410,193 processed records
52,122,367 characters
0 malformed JSON records
0 empty processed records
0 duplicate cleaned hashes
648 auditable ledger entries
validated source and processed hashes
```

The v0.1.2 update removed exactly:

```text
49 targeted short extraction artifacts
```

without introducing a blanket short-record deletion policy.

The corpus is now ready to serve as a **seed dataset for tokenizer research and subsequent corpus expansion**.

It should not yet be treated as the final Oromo foundation-model training corpus.

---

# 32. Dataset Status

```text
┌──────────────────────────────────────────┐
│  OROMO AI — CORPUS STATUS                │
├──────────────────────────────────────────┤
│  Source acquisition       COMPLETE       │
│  Provenance               COMPLETE       │
│  Audit pipeline           COMPLETE       │
│  Conservative cleaning    COMPLETE       │
│  Deduplication            COMPLETE       │
│  Rejection ledger         COMPLETE       │
│  v0.1.2 processing        COMPLETE       │
│  Integrity validation     COMPLETE       │
│                                          │
│  Corpus expansion         NEXT           │
│  Tokenizer research       NEXT           │
│  Model training           LATER          │
└──────────────────────────────────────────┘
```

**Current principle:**

> **Build the data foundation first. Then build the model on top of evidence.**

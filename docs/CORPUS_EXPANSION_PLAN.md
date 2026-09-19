# OromoCorpus Expansion Plan

## Purpose

This document defines the official path from the validated `afriberta_oromo_v0.1.2` seed corpus to a diverse, training-ready OromoCorpus for OromoLM continued pretraining.

The project is targeting:

| Release | Official target | Purpose |
| --- | ---: | --- |
| **OromoCorpus v0.2** | **50M net unique OromoLM-tokenizer tokens minimum** | First major multi-source corpus release |
| **OromoCorpus v0.3** | **100M net unique OromoLM-tokenizer tokens preferred** | Broader and better-balanced training corpus |

The project optimizes for quality, diversity, licensing clarity, and reproducibility—not the largest possible raw download.

## Counting Standard

The official milestone count is measured as:

```text
licensed and accepted natural Oromo text
        ↓
source-specific extraction
        ↓
conservative cleaning
        ↓
exact + near-duplicate removal across every source
        ↓
evaluation exclusion
        ↓
tokenization with the selected OromoLM tokenizer
        ↓
net unique training tokens
```

Every release must also report:

- raw and retained documents;
- raw and retained characters;
- whitespace-token count;
- OromoLM-tokenizer count;
- exact and near-duplicate losses;
- per-source and per-domain contribution;
- license and redistribution status;
- excluded evaluation and synthetic counts.

Tokenizer changes alter model-token counts. Therefore each published count must name and version the tokenizer used, while whitespace-token counts provide a tokenizer-independent comparison.

## Corpus Boundaries

The 50M–100M natural-language target includes only accepted, provenance-bearing Afaan Oromoo text.

It excludes:

- OromoBench and all evaluation holdouts;
- text without an acceptable provenance and license decision;
- rejected corruption, spam, extraction garbage, and unsafe sensitive data;
- duplicates already represented elsewhere in OromoCorpus;
- synthetic or machine-translated text, which must use a separate dataset identity;
- instruction-tuning conversations unless explicitly released as a separately versioned dataset.

## Source Portfolio

Expansion should seek multiple independent source families, including:

- public and appropriately licensed web corpora;
- Oromo Wikipedia and other open reference material;
- licensed books and public-domain literature;
- educational resources;
- government and public-service documents;
- news and magazines with explicit permission or compatible terms;
- health, agriculture, science, and technical material;
- Oromo history, culture, and Gadaa-related works;
- interviews, speeches, subtitles, and transcriptions;
- community-contributed writing with documented consent and terms;
- parallel corpora retained with alignment and source metadata.

No source should be accepted merely because it is large. Each source requires a license/provenance decision, quality sample, and measured net contribution after cross-source deduplication.

## Source Registry

Before ingestion, register at least:

```text
source_id
source_name
owner_or_publisher
source_url
acquisition_method
acquired_at
license
training_permission
redistribution_permission
attribution_requirements
domain
dialect_or_region_if_known
language_risk
pii_or_sensitive_data_risk
raw_artifact_hash
review_status
```

Unclear fields must remain explicit; they must not be replaced by guesses.

## Acceptance Pipeline

Each candidate source passes through:

1. provenance and license review;
2. immutable raw capture and hashing;
3. structural profiling;
4. Oromo-language and Qubee diagnostics;
5. native-speaker quality sampling where feasible;
6. source-specific extraction and conservative cleaning;
7. exact, paragraph-level, and near-duplicate comparison against all accepted sources;
8. PII and sensitive-content review appropriate to the source;
9. domain and dialect labeling where evidence exists;
10. evaluation-leakage checks;
11. OromoLM-tokenizer measurement;
12. manifest, rejection ledger, and release report generation.

Language identification is diagnostic rather than an automatic deletion rule. Legitimate names, code-switching, borrowed terms, regional forms, and unusual Oromo orthography require conservative handling.

## Release Gates

### OromoCorpus v0.2 — 50M minimum

Release only when:

- at least 50M net unique OromoLM-tokenizer tokens survive the full pipeline;
- multiple independent source families are represented;
- no evaluation material is present;
- every included source has a documented provenance/license decision;
- cross-source exact and near-duplicate checks pass;
- source and domain mixture statistics are published;
- hashes, manifests, processing configuration, and rejection summaries are reproducible.

### OromoCorpus v0.3 — 100M preferred

In addition to the v0.2 gates:

- at least 100M net unique OromoLM-tokenizer tokens survive;
- domain concentration is reviewed and justified;
- dialect and regional coverage are measured where metadata permits;
- literary, educational, technical, public-information, and conversational coverage gaps are documented;
- native-speaker quality review samples span the major source families.

## Immediate Execution Order

1. Create the machine-readable source registry and manifest schema additions.
2. Audit the first large licensed Oromo candidate source.
3. Ingest it without modifying existing raw or processed releases.
4. Cross-deduplicate it against `afriberta_oromo_v0.1.2`.
5. Publish raw-versus-retained and net-new-token results.
6. Repeat with smaller curated sources that improve domain or dialect coverage.
7. Freeze v0.2 only after the 50M release gates pass.
8. Continue acquisition toward the preferred 100M v0.3 target.

## Decision Principle

> **Fifty million diverse, traceable, deduplicated tokens are more valuable than one hundred million repeated or legally ambiguous tokens.**

Corpus growth must remain compatible with the project's core rule: data before model, evidence before scale.

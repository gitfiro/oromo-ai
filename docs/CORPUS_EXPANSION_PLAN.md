# OromoCorpus Expansion Plan

## Purpose

This document defines the official path from the validated `afriberta_oromo_v0.1.2` seed corpus to a diverse, training-ready OromoCorpus for OromoLM continued pretraining.

The project is targeting:

| Release | Official target | Purpose |
| --- | ---: | --- |
| **OromoCorpus v0.2** | **50M net unique OromoLM-tokenizer tokens minimum** | First major multi-source corpus release |
| **OromoCorpus v0.3** | **100M net unique OromoLM-tokenizer tokens preferred** | Broader and better-balanced training corpus |

The project optimizes for quality, diversity, licensing clarity, and reproducibility—not the largest possible raw download.

## Current Measured Progress — 2026-09-27

The current accepted multi-source corpus measures **14,492,686 tokens** under the Oromo Unigram 48K + byte-fallback tokenizer used as a planning reference. This tokenizer is not yet the final OromoLM tokenizer, so the number is a versioned planning measurement rather than the final release count.

| Source | Final accepted records | 48K reference tokens | Registry status |
| --- | ---: | ---: | --- |
| AfriBERTa Afaan Oromoo v0.1.2 | 410,193 | 9,587,934 | approved |
| Wikimedia omwiki v0.1 | 2,254 | 1,070,896 | approved |
| VOA Afaan Oromoo via WURA v0.1 | 9,510 | 1,899,811 | approved |
| WaxalNLP Oromo ASR v0.1 | 44,194 | 1,934,045 | approved |
| **Accepted total** | **466,151** | **14,492,686** | — |

### Research-qualified HOLD pool

| Source | Research-clean records | 48K reference tokens | Status |
|---|---:|---:|---|
| MADLAD-400 Oromo v0.1 | 18,704 | 17,873,390 | research hold |

MADLAD-400 has passed the project's technical and language-quality gates but
does **not** count toward the accepted OromoCorpus natural-language target.

Its dataset-level ODC-BY terms do not independently resolve the rights of all
underlying Common Crawl publisher content. A follow-up audit recovered
official MADLAD v1.5 URL/timestamp provenance for **1,917 final research-clean
records / 1,874,398 48K-reference tokens (10.49%)**, but **16,787 records /
15,998,992 reference tokens** remain unresolved.

For planning visibility only:

Accepted OromoCorpus: **14,492,686**

MADLAD research-clean HOLD: **17,873,390**

Combined technical pool: **32,366,076**

Technical-pool gap to 50M: **17,633,924**

The official accepted-corpus gap to 50M remains **35,507,314 tokens**.

Progress:

```text
50M minimum:  28.99% complete
remaining:    35,507,314 reference tokens

100M target:  14.49% complete
```

`castorini-wura-orm` remains `reviewing`. WURA is used as a provenance-discovery layer; only source subsets that independently pass rights review and the full acceptance pipeline count toward OromoCorpus.

`allenai-madlad-400-om-clean` is `research_hold`. Its research-clean artifact
contains **18,704 records / 17,873,390 48K-reference tokens**. Provenance is
partially recovered for 1,917 final records across 182 domains; the remaining
16,787 records are unresolved. A recovered `voaafaanoromoo.com` tranche of
326 records / 128,693 tokens is under separate rights screening. No MADLAD
tokens currently count toward accepted OromoCorpus accounting.

Frozen source reports:

- `docs/sources/WIKIMEDIA_OMWIKI_REPORT.md`
- `docs/sources/VOA_AFAAN_OROMOO_WURA_REPORT.md`
- `docs/sources/MADLAD_400_OROMO_REPORT.md`
- `docs/sources/MADLAD400_PROVENANCE_REVIEW.md`

The next acquisition priority is no longer tiny opportunistic sources. Prefer sources or publisher clusters capable of contributing roughly **5M–15M+ net-new tokens**, unless a smaller source provides unusually valuable domain, dialect, literary, conversational, or evaluation-safe diversity.

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

1. Preserve the current approved-source baseline and frozen source manifests.
2. Audit the next rights-clear Oromo source or publisher cluster with a realistic **5M–15M+ net-new-token** yield.
3. Keep unclear sources in `reviewing` or `hold`; do not infer permission from crawlability or dataset-wrapper licenses.
4. Ingest accepted source subsets without modifying prior frozen releases.
5. Apply conservative quality filtering, within-source exact/near deduplication, and cross-source deduplication against every accepted source.
6. Publish raw-versus-retained, provenance, licensing, and net-new-token results for each source.
7. Use smaller curated sources selectively when they materially improve domain or dialect coverage.
8. Freeze OromoCorpus v0.2 only after the 50M release gates pass, then continue toward the preferred 100M v0.3 target.

## Decision Principle

> **Fifty million diverse, traceable, deduplicated tokens are more valuable than one hundred million repeated or legally ambiguous tokens.**

Corpus growth must remain compatible with the project's core rule: data before model, evidence before scale.

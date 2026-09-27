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

The current accepted multi-source corpus measures **52,137,803 tokens** under the Oromo Unigram 48K + byte-fallback tokenizer used as a planning reference. The 50M v0.2 minimum has been achieved; expansion now continues toward the preferred 100M target. This tokenizer is not yet the final OromoLM tokenizer, so the number is a versioned planning measurement rather than the final release count.

| Source | Final accepted records | 48K reference tokens | Registry status |
| --- | ---: | ---: | --- |
| AfriBERTa Afaan Oromoo v0.1.2 | 410,193 | 9,587,934 | approved |
| Wikimedia omwiki v0.1 | 2,254 | 1,070,896 | approved |
| VOA Afaan Oromoo via WURA v0.1 | 9,510 | 1,899,811 | approved |
| WaxalNLP Oromo ASR v0.1 | 44,194 | 1,934,045 | approved |
| MADLAD-400 Oromo v0.2 | 18,704 | 17,873,390 | approved — ODC-BY |
| HPLT 3.0 gaz_Latn v0.1 | 26,655 | 19,771,727 | approved — CC0 packaging / underlying-text caveat |
| **Accepted total** | **511,510** | **52,137,803** | — |

### MADLAD-400 licensing decision

MADLAD-400 Oromo v0.2 is approved for OromoCorpus under the upstream
AllenAI/MADLAD-400 dataset's published **ODC-BY** license.

The project records this as a dataset-level licensing decision: attribution to
AllenAI / MADLAD-400 must be preserved, and Oromo AI does not represent that it
independently cleared copyright for every individual Common Crawl page.
Source-level provenance was nevertheless recovered for 1,917 final records /
1,874,398 reference tokens (10.49%), and those findings remain in the audit
trail.

MADLAD accepted contribution: **17,873,390**

Full licensing rationale:
`docs/sources/MADLAD_400_LICENSE_DECISION.md`.

### HPLT 3.0 milestone contribution

HPLT 3.0 `gaz_Latn` v0.1 contributes **26,655 records / 19,771,727
48K-reference tokens**. The release is restricted to WDS bins 8–10 and
excludes 315 structurally flagged records, 164 language-ambiguous records,
1,112 strong non-Oromo records, and all WDS 5–7 material.

The final accepted HPLT artifact passed exact and canonical near deduplication
against every previously accepted source and full GlotLID v3 verification.
Its frozen SHA-256 is
`b39bae97f09990d3ccfac141ae86ecfeb2c75ab30ce6674ee73e5504b419f856`.

HPLT publishes its packaging under CC0 while stating that it does not own the
underlying extracted text. Oromo AI records underlying individual-content
rights as not independently verified. See
`docs/sources/HPLT3_LICENSE_DECISION.md`.

Accepted OromoCorpus: **52,137,803**

Margin above 50M: **2,137,803**

Progress:

```text
50M minimum:  104.28% complete — achieved
margin:        2,137,803 reference tokens

100M target:   52.14% complete
```

`castorini-wura-orm` remains `reviewing`. WURA is used as a provenance-discovery layer; only source subsets that independently pass rights review and the full acceptance pipeline count toward OromoCorpus.

`allenai-madlad-400-om-clean` is now `approved` under the upstream ODC-BY
dataset license. Its frozen artifact contributes **18,704 records / 17,873,390
48K-reference tokens** to accepted OromoCorpus. The v0.1 HOLD manifest is
retained historically; approval is recorded in the v0.2 manifest. Underlying
individual content rights remain `not_independently_verified`.

Frozen source reports:

- `docs/sources/WIKIMEDIA_OMWIKI_REPORT.md`
- `docs/sources/VOA_AFAAN_OROMOO_WURA_REPORT.md`
- `docs/sources/MADLAD_400_OROMO_REPORT.md`
- `docs/sources/MADLAD400_PROVENANCE_REVIEW.md`
- `docs/sources/MADLAD_400_LICENSE_DECISION.md`
- `docs/sources/HPLT3_OROMO_REPORT.md`
- `docs/sources/HPLT3_LICENSE_DECISION.md`

With the 50M minimum achieved, acquisition now serves two goals: progress toward the preferred **100M** target and improved corpus balance. Prefer sources that add underrepresented domain, dialect, literary, educational, technical, public-information, or conversational material; raw volume alone is no longer the primary selection criterion.

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
2. Continue expansion toward 100M while prioritizing underrepresented domains and dialects; large sources remain valuable but are no longer required merely to clear the minimum.
3. Keep unclear sources in `reviewing` or `hold`; do not infer permission from crawlability or dataset-wrapper licenses.
4. Ingest accepted source subsets without modifying prior frozen releases.
5. Apply conservative quality filtering, within-source exact/near deduplication, and cross-source deduplication against every accepted source.
6. Publish raw-versus-retained, provenance, licensing, and net-new-token results for each source.
7. Use smaller curated sources selectively when they materially improve domain or dialect coverage.
8. Treat the 50M token-volume gate as achieved; complete the remaining v0.2 release checks, then continue toward the preferred 100M v0.3 target.

## Decision Principle

> **Fifty million diverse, traceable, deduplicated tokens are more valuable than one hundred million repeated or legally ambiguous tokens.**

Corpus growth must remain compatible with the project's core rule: data before model, evidence before scale.

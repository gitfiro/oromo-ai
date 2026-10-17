# FineWeb2 Oromo `gaz_Latn` v0.1 — Qualification Report

## Decision

**Approved / frozen for OromoCorpus.**

FineWeb2 West Central Oromo (`gaz_Latn`) v0.1 contributes **22,205 records / 7,399,789 whitespace words / 11,706,955 48K-reference tokens** after full-partition exact cross-source deduplication, canonical near deduplication, and a narrow evidence-based quality pass.

After promotion, OromoCorpus contains:

```text
accepted sources:      10
accepted records:      852,513
48K reference tokens:  74,820,956
progress to 100M:      74.82%
remaining to 100M:     25,179,044
```

## Upstream source

- Dataset: `HuggingFaceFW/fineweb-2`
- Config: `gaz_Latn`
- Split: `train`
- Language label: West Central Oromo
- Origin: Common Crawl
- Dataset packaging license: **ODC-By 1.0**
- Underlying individual content rights: **not independently verified**

The project relies on the upstream dataset-level license representation for dataset use. This approval does not assert that Oromo AI independently cleared copyright for every underlying Common Crawl page.

## Full raw inventory

The complete streamed train partition was frozen locally before qualification.

| Metric | Value |
| --- | ---: |
| Records | 47,883 |
| Whitespace words | 17,158,432 |
| Characters | 131,513,305 |
| UTF-8 text bytes | 134,349,859 |
| JSONL bytes | 152,294,513 |
| Unique domains | 1,140 |
| Common Crawl dumps | 96 |
| Mean upstream language score | 0.9926567231 |
| Raw artifact SHA-256 | `d73a942287573bec1b48fb7054cc2818afc6c63e0e8b0f64948208beb8c987b0` |

## Exact cross-source deduplication

The raw partition was compared against all nine previously accepted OromoCorpus sources using normalized-text SHA-256.

| Metric | Value |
| --- | ---: |
| Internal exact duplicates | 0 |
| Cross-source exact duplicates | 11,622 |
| Cross-source duplicate words | 4,206,684 |
| Exact-net-new records | 36,261 |
| Exact-net-new words | 12,951,748 |
| Exact-net-new record rate | 75.73% |
| Exact-net-new word rate | 75.48% |

Exact duplicate destinations were dominated by HPLT3:

| Existing source | Exact duplicates |
| --- | ---: |
| HPLT3 | 11,430 |
| Glot500 | 95 |
| Wikimedia | 47 |
| VOA | 30 |
| AfriBERTa | 20 |

## Canonical near deduplication

The exact-net-new candidate then used the project canonical protocol:

- Unicode-aware word normalization;
- 5-word shingles;
- exact Jaccard similarity;
- duplicate threshold: **0.85**;
- deterministic first-record-wins within source;
- cross-source comparison against all nine accepted sources.

Results:

| Metric | Value |
| --- | ---: |
| Exact-new input | 36,261 records / 12,951,748 words |
| Within-source near duplicates | 10 |
| Cross-source near duplicates | 13,819 |
| Cross-source words removed | 5,345,384 |
| Post-near-dedup records | 22,432 |
| Post-near-dedup words | 7,603,710 |
| Near-stage word retention | 58.71% |
| Overall raw-word retention | 44.31% |

Best-match near-duplicate destinations:

| Existing source | Near duplicates |
| --- | ---: |
| VOA | 7,373 |
| HPLT3 | 5,153 |
| MADLAD-400 | 936 |
| Wikimedia | 245 |
| Glot500 | 99 |
| AfriBERTa | 13 |

## Domain-diversity audit

The initial 10k audit sample retained 3,430 records / 1,216,333 words after exact and canonical near deduplication across 325 domains. In the full post-near-dedup candidate, **909 domains** remained. The top 10 domains represented **48.89%** of words and the top 20 represented **61.31%**.

Concentration was therefore documented but not used as an automatic exclusion rule. Domain caps were not imposed merely because a source was political, religious, historical, governmental, journalistic, or otherwise domain-specific.

## Quality audit

The post-near-dedup candidate contained **22,432 records / 7,603,710 words**.

Language-score distribution:

| Bucket | Records |
| --- | ---: |
| >=0.99 | 20,423 |
| 0.95–0.99 | 870 |
| 0.90–0.95 | 333 |
| 0.80–0.90 | 304 |
| <0.80 | 502 |

A conservative review queue flagged **1,553 records / 1,303,725 words**. Flags were treated as review signals rather than automatic rejection criteria.

The final narrow exclusion policy rejected only:

1. a low upstream language score **plus at least one additional quality signal**;
2. high repeated-line ratio;
3. many embedded URLs.

The policy explicitly did **not** automatically reject records solely for:

- English marker dominance;
- Ethiopic-script content;
- low upstream language score;
- very long length;
- political, religious, historical, legal, news, or other legitimate content categories.

The narrow pass rejected **227 records / 203,921 words (2.68%)**, corresponding to **422,858 48K-reference tokens**.

## Frozen accepted artifact

| Metric | Value |
| --- | ---: |
| Final records | **22,205** |
| Final whitespace words | **7,399,789** |
| Final characters | **56,438,459** |
| Final UTF-8 bytes | **58,146,701** |
| Final 48K reference tokens | **11,706,955** |
| Reference tokens / word | **1.5820660562** |
| Final SHA-256 | `d1a6c58c2298d37ae49df6bafd6a4d03963ebc99cdac831490448cb21cfc56ec` |
| Reference tokenizer SHA-256 | `79d64021d85877c1544e7e3a26bb21d2ad15f0aa7c6e76aeeeed3efddc5c3d2f` |

The accepted corpus payload remains outside normal Git tracking. Git stores the registry entry, manifest, qualification report, and reproducibility metadata rather than the corpus JSONL itself.

## OromoCorpus impact

Before FineWeb2:

```text
830,308 records
63,114,001 reference tokens
63.11% of 100M
```

FineWeb2 contribution:

```text
22,205 records
11,706,955 reference tokens
```

After FineWeb2:

```text
852,513 records
74,820,956 reference tokens
74.82% of 100M
25,179,044 tokens remaining
```

## Reproducibility and licensing notes

The frozen metrics are tied to the Oromo Unigram 48K + byte-fallback planning tokenizer with SHA-256 `79d64021d85877c1544e7e3a26bb21d2ad15f0aa7c6e76aeeeed3efddc5c3d2f`.

FineWeb2 is recorded under its upstream **ODC-By 1.0** dataset license. Because FineWeb2 is derived from Common Crawl, Oromo AI separately records underlying individual content rights as `not_independently_verified`. Downstream model-weight licensing remains a separate release-review question.

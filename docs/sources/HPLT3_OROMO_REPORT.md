# HPLT 3.0 Oromo Source Report

## Decision

**Status: approved / frozen as `hplt3-gaz-latn.v0.1`**

HPLT 3.0 West Central Oromo (`gaz_Latn`) is accepted into OromoCorpus as a deliberately conservative subset restricted to WDS quality bins **8, 9, and 10**, followed by project-level structural quality review, exact and near-duplicate removal, and full GlotLID verification of the structurally clean candidate pool.

The final frozen artifact contributes **26,655 records / 104,275,394 characters / 13,581,841 whitespace tokens / 19,771,727 Oromo Unigram 48K reference tokens**.

## Upstream source

- Project: HPLT 3.0
- Language-script slice: `gaz_Latn`
- Upstream catalogue: https://hplt-project.org/datasets/v3.0
- Hugging Face metadata/card: `HPLT/HPLT3.0`
- Upstream origin: Internet Archive / Common Crawl
- Raw HPLT Oromo shards downloaded: WDS bins 5 through 10
- Raw records: **63,063**
- Raw characters: **251,115,477**
- Raw whitespace tokens: **32,787,737**
- Raw 48K-reference tokens: **57,174,408**
- URL coverage observed during profiling: **100%**

## Quality-bin strategy

The project did not automatically accept the whole HPLT Oromo slice. Tokenization and structural profiling showed a strong quality gradient from higher to lower WDS bins. The first approved HPLT release therefore uses only bins 8–10.

Near-dedup net-new yield before the bin restriction:

| WDS bin | Records | 48K reference tokens |
| --- | ---: | ---: |
| 10 | 12 | 34,674 |
| 9 | 4,655 | 7,044,063 |
| 8 | 23,579 | 18,394,094 |
| 7 | 15,450 | 11,919,175 |
| 6 | 6,114 | 7,097,550 |
| 5 | 4,247 | 8,574,668 |
| **All** | **54,057** | **53,064,224** |

Bins 5–7 remain research material and are not included in v0.1.

## Deduplication

### Exact deduplication

From 63,063 raw records:

- within-HPLT exact duplicates: **3**
- cross-source exact duplicates: **994**
- exact-net-new records: **62,066**
- exact-net-new 48K-reference tokens: **56,960,928**

Exact cross-source matches were concentrated in VOA and Wikimedia.

### Near deduplication

Canonical policy:

- 5-word shingles
- bottom-k candidate signature size: 32
- exact Jaccard verification threshold: **0.85**
- deterministic first-record-wins ordering

Results:

- within-HPLT near duplicates: **100**
- after within-source near dedup: **61,966**
- cross-source near duplicates: **7,909**
- final near-dedup net-new records: **54,057**
- final near-dedup 48K-reference tokens: **53,064,224**

Cross-source near matches:

| Accepted source | Matches |
| --- | ---: |
| VOA Afaan Oromoo via WURA v0.1 | 6,346 |
| MADLAD-400 Oromo v0.2 | 1,111 |
| Wikimedia omwiki v0.1 | 441 |
| AfriBERTa Afaan Oromoo v0.1.2 | 11 |
| WaxalNLP Oromo ASR v0.1 | 0 |

## Structural quality review

The initial v0.1 candidate was restricted to WDS 8–10:

- records before structural screening: **28,246**
- structurally clean candidates: **27,931**
- structural-review records excluded from v0.1: **315**

The 315 records were routed to review for signals such as multiple boilerplate markers, many embedded URLs, unusual length, repeated lines, or replacement glyphs. These signals were not treated as proof of bad language; the records were simply excluded because they were unnecessary to reach the corpus milestone.

The structurally clean candidate pool contained **22,206,734 48K-reference tokens**.

## Language verification

A deterministic 1,000-record audit sample first showed that a full language-ID pass was justified. GlotLID v3 was then run over all **27,931** structurally clean candidates.

Classification result:

| Bucket | Records | 48K reference tokens | v0.1 decision |
| --- | ---: | ---: | --- |
| Oromo top-1 | 26,655 | 19,771,727 | accepted |
| Ambiguous review | 164 | 578,127 | excluded |
| Strong non-Oromo review | 1,112 | 1,856,880 | excluded |

Accepted top-1 labels:

- `__label__gaz_Latn`: **26,570**
- `__label__hae_Latn`: **85**

The final subset spans **1,091 unique source domains**.

## Frozen artifact

```text
data/interim/hplt3-gaz-latn/final/hplt3-gaz-latn.v0.1.jsonl
```

Final corpus SHA-256:

```text
b39bae97f09990d3ccfac141ae86ecfeb2c75ab30ce6674ee73e5504b419f856
```

Frozen statistics:

```text
data/interim/hplt3-gaz-latn/final/hplt3-gaz-latn.v0.1.stats.json
```

Statistics SHA-256:

```text
0860a7d309f25245d5d288973fd94c30ec4431a7bfb91d553e2c6c00586f53cb
```

Final WDS mixture:

| Bin | Records | 48K reference tokens |
| --- | ---: | ---: |
| 10 | 12 | 34,674 |
| 9 | 4,511 | 6,344,963 |
| 8 | 22,132 | 13,392,090 |
| **Total** | **26,655** | **19,771,727** |

## OromoCorpus impact

Before HPLT:

- accepted reference-token total: **32,366,076**

HPLT v0.1 contribution:

- **19,771,727**

After HPLT:

- **52,137,803 reference tokens**
- **104.28% of the 50M minimum**
- **52.14% of the 100M preferred target**
- margin above 50M: **2,137,803**

## Licensing and provenance

The HPLT 3.0 project states that it does not own the underlying extracted text and licenses the **packaging** under **CC0**. Original document URLs are preserved in the HPLT data and the project provides a notice-and-takedown process.

Oromo AI therefore records the license scope conservatively:

- packaging license: **CC0-1.0**
- underlying individual-content rights: **not independently verified**
- source URLs/provenance: preserved
- downstream trained-model weight licensing: **separate review required**

This is a project corpus-acceptance decision, not a legal opinion or an assertion that every underlying webpage is CC0.

See `docs/sources/HPLT3_LICENSE_DECISION.md` for the full decision record.

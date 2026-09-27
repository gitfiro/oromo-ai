# MADLAD-400 Oromo Corpus Audit Report

## Status

**Source:** AllenAI MADLAD-400  
**Configuration:** `om`  
**Language:** Afaan Oromoo / Oromo  
**Source family:** Common Crawl-derived web corpus  
**Manifest version:** `0.1`

### Current decision

- Technical qualification: **PASS**
- Exact deduplication: **PASS**
- Near deduplication: **PASS**
- Language-quality audit: **PASS**
- Tokenizer-reference measurement: **PASS**
- Corpus status: **RESEARCH HOLD**
- Approved for accepted OromoCorpus release: **NO**
- Licensing/provenance review: **REQUIRED**

MADLAD is therefore a technically qualified and quality-cleaned
research corpus, but it is not part of the accepted OromoCorpus release.

---

## 1. Acquisition

The released Oromo clean shard from `allenai/MADLAD-400` was acquired
for technical and provenance evaluation.

Raw artifact:

`data/interim/allenai-madlad-400-om-clean/raw/om_clean_0000.jsonl.gz`

Raw records:

**18,895**

Raw characters:

**88,508,841**

Raw whitespace tokens:

**11,175,240**

Raw SHA-256:

`ad80e759be2ae6585c595a01a336ebceb15dd2e558fb3e7eb71c0bb118d9d342`

---

## 2. Exact Deduplication

Exact comparison was performed against the currently accepted
OromoCorpus sources.

Results:

- Input records: **18,895**
- Within-source exact duplicates: **0**
- Cross-source exact duplicates: **0**
- Exact net-new records: **18,895**

Exact-net-new SHA-256:

`ef6bfdfbbb3b2676f45e15fd0679a69caf5c805f418a6b34dc547c2ae22c23d3`

---

## 3. Near Deduplication

The canonical OromoCorpus near-deduplication policy was used:

- word shingles: **5**
- exact Jaccard threshold: **0.85**
- bottom-k candidate signature: **32**
- within-source survivor policy:
  **first record in source order wins**

Results:

- Exact-new input: **18,895**
- Within-source near duplicates: **7**
- After within-source near dedup: **18,888**
- Cross-source near duplicates: **25**
- Final near-dedup net-new records: **18,863**

Cross-source near matches:

- VOA Afaan Oromoo: **18**
- Wikimedia omwiki: **7**
- AfriBERTa: **0**
- WaxalNLP: **0**

Near-dedup artifact SHA-256:

`04073c041f2e32b1bded6e12907d5bb14cb78770f390ac64a4a5f55c58a7a823`

---

## 4. Initial Quality Triage

The 18,863 near-deduplicated documents were divided into conservative
audit buckets.

| Bucket | Records | 48K reference tokens |
|---|---:|---:|
| Keep candidates | 18,541 | 16,189,835 |
| Long-document review | 100 | 1,630,013 |
| Language review | 102 | 128,091 |
| Strong non-Oromo candidates | 120 | 87,601 |
| **Total** | **18,863** | **18,035,540** |

Quality flags included:

- high English marker ratio: **178**
- low Oromo marker ratio: **164**
- over 5,000 words: **101**
- low letter ratio: **1**

These flags were used for review only.

Document length, subject matter, political content, religious content,
dialectal variation, unusual spelling, foreign names, and occasional
English were not treated as automatic rejection criteria.

---

## 5. Long-Document Review

The long-document bucket contained substantial high-value Afaan Oromoo
material including:

- academic research
- educational modules
- literature
- legal material
- health material
- history
- religious material
- cultural material
- long-form essays

Length alone was therefore explicitly rejected as a quality-removal rule.

---

## 6. Secondary Language Identification

The ambiguous language-review set was evaluated with:

**GlotLID v3**

Confirmed Oromo-family labels available in the model:

- `__label__gaz_Latn`
- `__label__hae_Latn`

Results for the 102 ambiguous documents:

| Classification | Records |
|---|---:|
| Strong Oromo | 57 |
| Probable Oromo | 4 |
| Possible Oromo | 2 |
| Non-Oromo or uncertain | 39 |

Top-1 `gaz_Latn` predictions:

**61**

The remaining 39 records were manually inspected.

---

## 7. Final Language Decision

The following were rejected:

- strong non-Oromo bucket: **120 records**
- final non-Oromo / mixed / uncertain review: **39 records**

Total language-quality rejects:

**159 records**

The rejected evidence is preserved at:

`data/interim/allenai-madlad-400-om-clean/quality_decisions/rejected_language_contamination.jsonl`

Rejected-evidence SHA-256:

`9d78b82c14501a8d2831391f85b09af15fe4479e5af1bb4d53abd7bde0bd0e92`

---

## 8. Research-Clean Artifact

Final quality-cleaned MADLAD research corpus:

`data/interim/allenai-madlad-400-om-clean/madlad-om.research-clean.jsonl`

Final metrics:

- Records: **18,704**
- Characters: **87,930,775**
- Whitespace tokens: **11,088,537**
- 48K reference tokens: **17,873,390**
- Characters/token: **4.9196**
- Tokens/whitespace-token: **1.6119**

Research-clean SHA-256:

`4a28bde40c0c3f973fa2d503edee80a7a5e06330ddb74d7249f23bc662dcaf11`

The quality pipeline retained approximately **99.10%** of the original
near-deduplicated 48K-reference token yield.

---

## 9. Licensing and Provenance

MADLAD-400 is derived from Common Crawl.

The distributed dataset has a dataset-level **ODC-BY** license.
However, dataset-level licensing does not by itself establish that every
underlying web publisher granted the rights required for every intended
downstream use.

The released Oromo text schema does not provide sufficient per-document
URL/domain provenance for the project to independently reconstruct and
clear underlying publisher rights.

Therefore:

- technical research use: **qualified**
- quality status: **passed**
- accepted OromoCorpus release: **not approved**
- training use for the release corpus: **on hold**
- text redistribution: **on hold**
- downstream model-weight licensing: **separate review required**

The quality decision and legal/provenance decision are deliberately
independent.

---

## 10. Corpus Accounting

Accepted OromoCorpus remains:

**14,492,686 48K-reference tokens**

MADLAD research-clean HOLD:

**17,873,390 48K-reference tokens**

Combined technical research pool:

**32,366,076 48K-reference tokens**

MADLAD is **not included** in the accepted OromoCorpus total.

If it were eventually cleared, the combined pool would represent:

**64.73% of the 50M-token minimum target**

Remaining to 50M in that technical scenario:

**17,633,924 tokens**

---

## 11. Final Decision

MADLAD-400 Oromo v0.1 is frozen as:

**TECHNICALLY QUALIFIED / QUALITY PASSED / RESEARCH HOLD**

No future documentation or corpus statistics should count its
17,873,390 reference tokens toward the accepted OromoCorpus total unless
a later provenance/licensing decision explicitly changes its status.

Any change to processing, quality decisions, or release status requires
a new manifest version.


---

## Provenance Recovery Follow-up

A subsequent provenance-recovery audit successfully mapped **1,917 records**
from the final research-clean corpus to official MADLAD v1.5 URLs and
timestamps, representing **1,874,398 48K-reference tokens (10.49%)**.

The remaining MADLAD material remains provenance-unresolved.

See:

`docs/sources/MADLAD400_PROVENANCE_REVIEW.md`

# MADLAD-400 Oromo Provenance Recovery Review

## Status

**Source:** AllenAI MADLAD-400 Oromo  
**Legacy research-clean corpus:** 18,704 records  
**48K reference tokens:** 17,873,390  
**Overall corpus status:** `approved` under upstream dataset-level ODC-BY  
**Provenance status:** partially recovered

This review records the provenance-recovery investigation performed against
the official MADLAD v1.5 release.

---

## 1. Official v1.5 Provenance Discovery

The official MADLAD v1.5 Oromo clean shard exposes:

- `text`
- `timestamp`
- `url`

Available shard:

`data-v1p5/om/clean_docs_v2-00003-of-00010.jsonl.gz`

Records:

**1,935**

All 1,935 records were deterministically mapped to the legacy MADLAD Oromo
release:

- byte-exact matches: **1,934**
- normalized deterministic matches: **1**
- unresolved: **0**
- ambiguous: **0**

Provenance-map SHA-256:

`33c5f93534b6efbd6586b81dae94b5b65866a95651eb6ad2b5af16d80bbcd146`

---

## 2. Final Research-Clean Intersection

After intersecting recovered provenance with the final MADLAD
research-clean artifact:

- final research-clean records: **18,704**
- provenance-recovered records: **1,917**
- record coverage: **10.25%**
- unique recovered domains: **182**

Recovered-provenance artifact SHA-256:

`5133542e9836b6b4638bb8508c4035a3a326500a8310fa997486b321b5df4cc5`

Token measurements:

- recovered characters: **9,068,639**
- recovered whitespace tokens: **1,143,145**
- recovered 48K-reference tokens: **1,874,398**
- MADLAD token provenance coverage: **10.49%**

Remaining unresolved:

- records: **16,787**
- 48K-reference tokens: **15,998,992**

Those records remain without directly recovered source-level provenance. Under the later v0.2 licensing decision, this limitation is retained in the audit trail but does not block corpus acceptance under the upstream MADLAD-400 ODC-BY dataset license.

---

## 3. Missing v1.5 Shards

Repository-history inspection found public history only for:

`clean_docs_v2-00003-of-00010.jsonl.gz`

No public history was found for Oromo clean shards:

- 00000
- 00001
- 00002
- 00004
- 00005
- 00006
- 00007
- 00008
- 00009

The project therefore does not infer that these missing shard numbers were
ever publicly available.

---

## 4. URL Companion Dataset

The `nhagar/madlad-400_urls_clean` derivative was investigated as a possible
recovery path.

It contains only:

- `url`
- `domain`

The generation pipeline:

1. selects MADLAD v1.5 clean JSON shards;
2. sorts source files by descending file size for batching;
3. reads multiple files through DuckDB;
4. writes URL/domain projections without preserving source filename,
   source row index, text hash, language, or another deterministic join key.

Therefore positional reconstruction from the URL-only Parquet batches is
**not accepted as provenance evidence**.

---

## 5. Recovered Domain Inventory

The final research-clean provenance subset contains **182 unique domains**.

Highest-token recovered domains include:

- sammubani.com — 213,304
- bbc.com — 161,061
- bilisummaa.com — 132,304
- voaafaanoromoo.com — 128,693
- kichuu.com — 114,050
- ayyaantuu.org — 103,222
- nuuralhudaa.com — 55,518
- elearning.jcte.edu.et — 53,556
- beekanguluma.org — 51,514
- gubirmans.com — 41,522
- qeerroo.org — 39,888
- help.libreoffice.org — 29,926
- ethpress.gov.et — 26,961
- fanabc.com — 25,470

Recovered provenance does not itself establish permission for training,
redistribution, or downstream model release.

---

## 6. VOA Candidate Investigation

Recovered final research-clean records from:

`voaafaanoromoo.com`

- records: **326**
- 48K reference tokens: **128,693**

Candidate artifact SHA-256:

`6bc008ca46d05ff637a924c3d88e695ff99fdc1ad2358f8bdddbbfe6477206be`

VOA exclusively produced material may qualify under VOA's public-domain
framework, but third-party material must be screened separately.

An automated marker audit identified:

- records containing third-party organization names: **12**
- records with likely source/credit context: **3**

Manual-review artifact:

- records: **12**
- SHA-256:
  `05fcc80293eb7faf3d401ab58e6505678a2f649b0f09c2c39b0b1e75da4e4a98`

### Manual classification

#### A — clean candidate

No evidence in the reviewed text that the VOA article itself is third-party
content:

- research_clean_index **2165**
- research_clean_index **8600**

#### B — manual hold / removable third-party fragment

Contains third-party media or caption material embedded in otherwise
potentially VOA-produced text:

- research_clean_index **4140**
- research_clean_index **12915**
- research_clean_index **14923**

These records are not approved in their current form.

#### C — exclude from rights-cleared VOA subset

Substantive reliance on third-party reporting, interviews, or source material:

- research_clean_index **1792**
- research_clean_index **8398**
- research_clean_index **11261**
- research_clean_index **16479**
- research_clean_index **17214**
- research_clean_index **17984**
- research_clean_index **18153**

---

## 7. Current Decision

The provenance findings above remain unchanged. A later project licensing
decision approved MADLAD-400 Oromo v0.2 by relying on the upstream
AllenAI/MADLAD-400 dataset's published **ODC-BY** license.

Current status:

- technical status: **qualified**
- quality status: **passed**
- provenance status: **partially recovered**
- dataset license: **ODC-BY**
- approval basis: **upstream dataset-level ODC-BY**
- underlying individual content rights: **not independently verified**
- OromoCorpus status: **approved**
- approved for OromoCorpus release: **true**
- downstream model-weight licensing: **separate review required**

MADLAD now contributes:

**17,873,390 48K-reference tokens**

Updated accepted OromoCorpus:

**32,366,076 48K-reference tokens**

The provenance work remains valuable because it documents source composition
and limitations; approval does not erase or reinterpret that evidence.

See the controlling licensing decision:

`docs/sources/MADLAD_400_LICENSE_DECISION.md`.

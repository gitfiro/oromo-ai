# MADLAD-400 Oromo License and Acceptance Decision

## Decision

**Project source:** `allenai/MADLAD-400`  
**Oromo configuration:** `om`  
**Upstream dataset license:** **Open Data Commons Attribution License (ODC-BY)**  
**Oromo AI source status:** **APPROVED**  
**Approved artifact:** frozen research-clean Oromo subset  
**Records:** **18,704**  
**48K-reference tokens:** **17,873,390**  
**Acceptance manifest:** `data/sources/manifests/allenai-madlad-400-om-clean.v0.2.json`

Oromo AI approves this frozen MADLAD-400 Oromo subset for inclusion in
OromoCorpus by relying on the upstream MADLAD-400 dataset's published
**ODC-BY** license representation.

This is a project corpus-governance decision. It does not rewrite, expand, or
replace the upstream license.

---

## 1. Upstream licensing basis

The official `allenai/MADLAD-400` Hugging Face dataset metadata identifies the
dataset license as:

`odc-by`

MADLAD-400 is a multilingual, Common Crawl-derived document corpus maintained
by AllenAI.

Oromo AI records the upstream license exactly at the dataset level as:

**Open Data Commons Attribution License (ODC-BY)**

The approval is therefore based on the license under which the upstream
dataset is distributed, rather than on a claim that Oromo AI independently
obtained permission from every website represented in Common Crawl.

---

## 2. What ODC-BY means for this project

ODC-BY is a database-focused license. Oromo AI treats the following as the
minimum project obligations when using or redistributing this MADLAD-derived
corpus material:

- preserve attribution to **AllenAI / MADLAD-400**;
- identify **MADLAD-400** as the upstream dataset;
- identify the upstream dataset license as **ODC-BY**;
- preserve an ODC-BY license notice or link where the corpus, a substantial
  database-derived portion, or relevant dataset documentation is distributed;
- do not imply that AllenAI, MADLAD-400 authors, Common Crawl publishers, or
  source websites endorse Oromo AI or downstream models;
- preserve this source and license decision in corpus manifests and release
  documentation.

Recommended attribution notice:

> Contains data derived from AllenAI MADLAD-400, made available under the
> Open Data Commons Attribution License (ODC-BY).

---

## 3. Important scope limitation

ODC-BY governs rights in the database and associated attribution obligations.
It should not be documented as though it independently licenses every
individual underlying web page or content item contained in a Common
Crawl-derived dataset.

Accordingly, Oromo AI records:

`underlying_content_rights = not_independently_verified`

This means:

- Oromo AI is relying on the upstream MADLAD-400 dataset license
  representation for corpus acceptance;
- Oromo AI is **not** asserting that it independently cleared the copyright
  status of every underlying publisher page;
- the provenance investigation remains part of the permanent audit trail;
- downstream users remain responsible for evaluating obligations that may
  apply to their particular jurisdiction, distribution method, or use case.

Approval does not erase these limitations.

---

## 4. Provenance investigation retained

Before approval, Oromo AI performed an additional source-level provenance
investigation.

Official MADLAD v1.5 provenance was deterministically recovered for:

- **1,917** final research-clean records;
- **1,874,398** 48K-reference tokens;
- **10.49%** of the final MADLAD token mass;
- **182** recovered domains.

Remaining without directly recovered source-level provenance:

- **16,787** records;
- **15,998,992** 48K-reference tokens.

These findings remain documented even though the project now accepts the
dataset under the upstream dataset-level ODC-BY licensing basis.

See:

- `docs/sources/MADLAD400_PROVENANCE_REVIEW.md`
- `docs/sources/MADLAD_400_OROMO_REPORT.md`

---

## 5. Quality and deduplication gates

Licensing approval does not bypass technical corpus gates.

The approved artifact had already passed:

- within-source exact deduplication;
- cross-source exact deduplication;
- canonical word-5-gram near deduplication;
- cross-source near deduplication;
- conservative quality triage;
- GlotLID-assisted language review;
- manual language-quality review;
- removal of **159** non-Oromo / mixed / unresolved language records;
- 48K-reference tokenizer measurement;
- immutable artifact hashing.

Frozen research-clean SHA-256:

`4a28bde40c0c3f973fa2d503edee80a7a5e06330ddb74d7249f23bc662dcaf11`

---

## 6. Corpus accounting decision

Effective with manifest **v0.2**, the frozen MADLAD-400 Oromo research-clean
artifact counts toward accepted OromoCorpus.

Contribution:

- records: **18,704**
- characters: **87,930,775**
- whitespace tokens: **11,088,537**
- 48K-reference tokens: **17,873,390**

Updated accepted OromoCorpus:

- records: **484,855**
- characters: **165,874,131**
- 48K-reference tokens: **32,366,076**
- progress toward 50M: **64.73%**
- remaining to 50M: **17,633,924**
- progress toward 100M: **32.37%**

---

## 7. Redistribution and model-use policy

For Oromo AI corpus governance:

- corpus training use: **approved under upstream ODC-BY dataset license**;
- corpus inclusion: **approved**;
- corpus accounting: **included**;
- text redistribution: **approved under upstream dataset license with
  attribution and this scope notice**;
- downstream trained-model weight licensing: **separate review required**.

The model-weight question remains separate because a trained model is a
different artifact from the source database.

---

## 8. Versioning

The previous manifest:

`allenai-madlad-400-om-clean.v0.1.json`

is retained as the historical **research_hold** decision.

The approval is recorded in:

`allenai-madlad-400-om-clean.v0.2.json`

This preserves an auditable history instead of rewriting the earlier decision.

---

## Final status

```text
technical_status: qualified
quality_status: passed
dataset_license: ODC-BY
approval_basis: upstream_dataset_level_ODC-BY
underlying_content_rights: not_independently_verified
corpus_status: approved
approved_for_oromocorpus_release: true
counts_toward_accepted_oromocorpus: true
downstream_model_weight_license: separate_review_required
```

**Decision:** MADLAD-400 Oromo is accepted into OromoCorpus under the upstream
MADLAD-400 ODC-BY dataset license, with attribution and scope limitations
explicitly preserved.

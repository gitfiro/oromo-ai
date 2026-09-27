# HPLT 3.0 License Decision

## Decision

**Project status: approved for OromoCorpus v0.1 subset**

Oromo AI approves the frozen `hplt3-gaz-latn.v0.1` subset for inclusion in OromoCorpus under a documented project policy that preserves the distinction between HPLT's CC0 packaging and the rights in the underlying crawled text.

This document records the project's data-governance decision. It is **not legal advice** and does not claim independent copyright clearance of every underlying webpage.

## Upstream terms recorded

HPLT 3.0 states in its published Terms of Use that:

1. HPLT does **not own the underlying text** from which the released text data were extracted.
2. HPLT licenses the **actual packaging of the text data under Creative Commons CC0**.
3. HPLT operates a notice-and-takedown process for rightsholders.
4. Users remain responsible for ensuring that their use complies with applicable law.

Current project references:

- https://hplt-project.org/datasets/v3.0
- https://huggingface.co/datasets/HPLT/HPLT3.0

## Project interpretation and scope

Oromo AI records:

```text
packaging_license: CC0-1.0
underlying_text_ownership_by_hplt: no
underlying_content_rights: not_independently_verified
document_urls_preserved: yes
notice_and_takedown: available upstream
approval_scope: filtered gaz_Latn WDS 8-10 research subset
downstream_model_weight_license: separate_review_required
```

The CC0 designation is **not** represented in this repository as an independent CC0 grant over every individual source webpage.

## Why the subset is accepted

The corpus decision considers the combination of:

- explicit upstream packaging terms;
- preserved document-level URL provenance;
- a bounded and reproducible selected subset;
- exact and near-duplicate removal against all previously accepted OromoCorpus sources;
- conservative WDS-bin restriction;
- structural-quality screening;
- full GlotLID verification of the structurally clean candidate population;
- immutable final hashes and source manifest;
- exclusion of ambiguous/non-Oromo and structurally flagged material from v0.1.

The approved frozen subset contains:

- **26,655 records**
- **104,275,394 characters**
- **13,581,841 whitespace tokens**
- **19,771,727 48K-reference tokens**
- **1,091 unique domains**

## Excluded material

The v0.1 approval does not automatically extend to:

- HPLT `gaz_Latn` WDS bins 5–7;
- 315 structural-review records from WDS 8–10;
- 164 language-ambiguous records;
- 1,112 strong non-Oromo records;
- other HPLT languages or future HPLT releases.

Each future expansion must be separately versioned and audited.

## Redistribution

The HPLT packaging is published under CC0, but Oromo AI does not represent that CC0 independently resolves every right that may attach to the underlying text. Any redistribution of corpus text should preserve provenance and this scope notice, and should account for applicable upstream/rightsholder obligations and takedown requirements.

The large frozen text artifact is not committed to Git; the repository publishes its manifest, hashes, measurements, processing decision, and audit documentation.

## Training and model weights

For project corpus governance, this subset is approved as natural-language training material.

A future public release of trained OromoLM weights requires a separate model-release licensing review that considers the selected base model, all training-source obligations, model architecture/license terms, and the intended distribution format.

## Final record

```text
source_id: hplt3-gaz-latn
version: v0.1
review_status: approved
corpus_status: approved
packaging_license: CC0-1.0
underlying_content_rights: not_independently_verified
final_records: 26,655
reference_48k_tokens: 19,771,727
final_sha256: b39bae97f09990d3ccfac141ae86ecfeb2c75ab30ce6674ee73e5504b419f856
```

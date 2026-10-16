# 🟩 Oromo AI

<p align="center">
  <strong>Open research infrastructure for Afaan Oromoo AI</strong><br>
  <em>Building OromoCorpus, OromoTokenizer, OromoLM, and OromoBench.</em>
</p>

<p align="center">
  🌐 <strong><a href="https://gitfiro.github.io/oromo-ai-research-hub/">Explore the Oromo AI Research Hub</a></strong><br>
  <em>Browse our research, documentation, corpus work, tokenizer experiments, model roadmap, and project progress as an interactive website.</em>
</p>

<p align="center">
  <strong>OromoCorpus → OromoTokenizer → OromoLM → OromoBench → Applications</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Transformers-Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="Transformers">
</p>

---

## What is Oromo AI?

**Oromo AI** is an independent open-source research and engineering project focused on building high-quality AI infrastructure for **Afaan Oromoo**.

The project follows a data-first path:

```text
licensed sources
      ↓
provenance + audit
      ↓
cleaning + deduplication
      ↓
OromoCorpus
      ↓
tokenizer research
      ↓
OromoLM continued pretraining
      ↓
OromoBench
      ↓
instruction tuning + applications
```

The goal is not to build a quick chatbot. The goal is to create reusable, documented, and reproducible infrastructure for Afaan Oromoo language modeling, translation, retrieval, evaluation, and future speech systems.

---

## Project components

| Component | Purpose | Status |
| --- | --- | --- |
| **OromoCorpus** | Versioned, provenance-tracked Afaan Oromoo training corpus | ✅ 50M minimum achieved; expanding toward 100M |
| **OromoTokenizer** | Tokenization research and Oromo-aware tokenizer candidates | ✅ Gemma +4K is the strongest current model-level candidate under the frozen gate |
| **OromoLM** | Continued-pretrained Afaan Oromoo causal language models | ✅ +4K v0.3 ablation crosses native and +8K Oromo BPB references while passing WikiText retention |
| **OromoBench** | Afaan Oromoo evaluation framework | 🔄 In development |

Canonical naming is documented in [`docs/NAMING.md`](docs/NAMING.md).

---

## Current status

### OromoCorpus

The current accepted corpus planning total is measured with the **Oromo Unigram 48K + byte-fallback tokenizer** as a research reference. It is **not yet the final OromoLM tokenizer**.

| Accepted source | Net-new records | 48K reference tokens |
| --- | ---: | ---: |
| AfriBERTa Afaan Oromoo v0.1.2 | 410,193 | 9,587,934 |
| Wikimedia omwiki v0.1 | 2,254 | 1,070,896 |
| VOA Afaan Oromoo via WURA v0.1 | 9,510 | 1,899,811 |
| WaxalNLP Oromo ASR v0.1 | 44,194 | 1,934,045 |
| MADLAD-400 Oromo v0.2 | 18,704 | 17,873,390 |
| HPLT 3.0 gaz_Latn v0.1 | 26,655 | 19,771,727 |
| Michsethowusu Oromo Sentiments cleaned subset v0.1 | 193,681 | 3,877,136 |
| Michsethowusu English–Oromo cleaned monolingual subset v0.1 | 45,048 | 1,185,406 |
| Glot500 Oromo source-partitioned subset v0.1 | 80,069 | 5,913,656 |
| **Accepted total** | **830,308** | **63,114,001** |

### MADLAD-400 licensing basis

MADLAD-400 Oromo v0.2 is now **accepted** into OromoCorpus under the upstream
AllenAI MADLAD-400 dataset's published **ODC-BY** license. The approved frozen
research-clean artifact contains **18,704 records / 17,873,390 48K-reference
tokens**.

This approval relies on the upstream dataset-level license representation and
preserves attribution to AllenAI / MADLAD-400. It does **not** claim that Oromo
AI independently cleared copyright for every underlying Common Crawl page.
That scope limitation, along with the completed provenance investigation, is
permanently documented in
[`MADLAD_400_LICENSE_DECISION.md`](docs/sources/MADLAD_400_LICENSE_DECISION.md).

Official v1.5 provenance was independently recovered for **1,917 final
records / 1,874,398 reference tokens (10.49%)** across **182 domains**. Those
findings remain part of the audit trail even though the full frozen subset is
accepted under the upstream dataset license.

### HPLT 3.0 qualification

HPLT 3.0 `gaz_Latn` v0.1 is now **accepted/frozen** as the sixth OromoCorpus
source. The approved subset is restricted to WDS bins **8–10**, passed exact
and canonical near-deduplication against all previously accepted sources,
passed structural review, and was fully checked with GlotLID v3. The final
artifact contains **26,655 records / 19,771,727 48K-reference tokens** across
**1,091 unique source domains**.

HPLT publishes the dataset packaging under **CC0**, while explicitly stating
that it does not own the underlying extracted text. Oromo AI therefore records
the underlying individual-content rights as **not independently verified** and
does not represent every source webpage as CC0. See
[`HPLT3_LICENSE_DECISION.md`](docs/sources/HPLT3_LICENSE_DECISION.md).

```text
OromoCorpus v0.2 minimum: 50,000,000 tokens
Current planning total:   63,114,001
Progress:                 114.40%
Margin above minimum:      13,114,001

OromoCorpus v0.3 target: 100,000,000 tokens
Current progress:         63.11%
```

The full WURA Oromo package remains under source-level review and does not count as an accepted source by itself. Only independently audited and rights-cleared subsets are admitted.

With the 50M minimum now achieved, corpus acquisition continues toward the preferred **100M** target with greater emphasis on domain, dialect, literary, educational, technical, and conversational diversity rather than raw volume alone.

### Michsethowusu cleaned-subset qualification

The upstream `michsethowusu/oromo-sentiments-corpus` was **not** accepted wholesale because the original 825,272 rows contain substantial multilingual/noisy material and heavy overlap with AfriBERTa. Oromo AI accepted only a frozen cleaned text subset after Oromo/noise screening, exact cross-source deduplication, and canonical 5-word-shingle near deduplication at Jaccard 0.85.

The accepted subset contributes **193,681 records / 3,877,136 48K-reference tokens**, raising the planning total to **56,014,939 tokens (56.01% of the 100M target)**. See [the source report](docs/sources/MICHSETHOWUSU_OROMO_SENTIMENTS_REPORT.md).

### English–Oromo cleaned monolingual qualification

The NLLB-derived `michsethowusu/english-oromo_sentence-pairs` source was highly noisy and redundant. Oromo AI therefore rejected its sentence-pair alignment for translation use and accepted only the cleaned Oromo-side monolingual residual after filtering plus exact and canonical near cross-source deduplication.

The frozen subset contributes **45,048 records / 1,185,406 48K-reference tokens**, raising OromoCorpus to **63,114,001 reference tokens (63.11% of the 100M target)**. See [the source report](docs/sources/MICHSETHOWUSU_ENGLISH_OROMO_REPORT.md).

### Glot500 Oromo source-partitioned qualification

Glot500 was audited as an aggregator rather than accepted wholesale. After excluding already represented and non-commercial source families, the priority Oromo candidate passed exact and canonical 5-word-shingle near cross-source deduplication against all eight previously accepted OromoCorpus sources.

The accepted source-partitioned subset contains **80,069 records / 5,913,656 48K-reference tokens** from CC100, AAU, HornMT, and TICO. The `mtdata` tranche remains held for source-specific licensing review. The accepted artifact is frozen at SHA-256 `a896acf3a88f40e017dd802f821c4bf8bc9278cd8483760b21e0229ffd10914f`.

See [the Glot500 Oromo qualification report](docs/sources/GLOT500_OROMO_REPORT.md).

### Latest corpus-expansion audit

The official upstream **CC100 Oromo** release was audited after the Glot500
CC100 tranche had already been accepted. After conservative filtering, 89.13%
of the candidate was removed as exact overlap and a further 57.59% of the
exact-net-new residual was removed by the canonical near-dedup gate. Only
**5,603 rows / 194,669 words** remained, so this residual was preserved but
**not promoted** into OromoCorpus.

The accepted corpus therefore remains **830,308 records / 63,114,001
48K-reference tokens (63.11% of the 100M planning target)**.

The next independent source family is **Mozilla Common Voice Oromo Scripted
Speech 27.0 (CC0-1.0)**. The archive has been downloaded locally, but transcript
extraction, deduplication, and token measurement are intentionally paused for
the next session.

See:
- [CC100 Oromo audit](docs/sources/CC100_OM_AUDIT.md)
- [Common Voice Oromo status](docs/sources/COMMON_VOICE_OROMO_STATUS.md)

### OromoTokenizer

Tokenizer research has established:

| Tokenizer | Vocabulary | Tokens/word | Fragmentation | UNK |
| --- | ---: | ---: | ---: | ---: |
| Oromo Unigram 48K + byte fallback | 48,000 | **1.4000** | **38.75%** | 0 |
| Oromo Unigram 32K + byte fallback | 32,000 | 1.4495 | 40.83% | 0 |
| AfriBERTa | 70,006 | 1.6765 | 39.83% | 0 |

Native causal-model tokenizers were also benchmarked on the frozen Oromo evaluation set. Whole-word vocabulary augmentation improved fragmentation substantially, but it did not match the custom Oromo tokenizer's sequence efficiency.

Full results: [`docs/TOKENIZER_RESEARCH_REPORT.md`](docs/TOKENIZER_RESEARCH_REPORT.md).

### OromoLM CPT pilot

The first controlled model-level CPT comparison is complete on `google/gemma-3-1b-pt`, comparing the native tokenizer against the frozen Gemma +8K Afaan Oromoo whole-word augmentation on the same six-source pilot text.

| Metric | Native Gemma | Oromo +8K | Change |
| --- | ---: | ---: | ---: |
| Training tokens | 5,708,421 | **4,811,939** | **-15.70%** |
| Optimizer steps | 349 | **294** | **-15.76%** |
| Train wall time | 1,437.05 s | **1,176.71 s** | **-18.12%** |
| Training throughput | 3,972.59 tok/s | **4,090.03 tok/s** | **+2.96%** |
| Peak reserved VRAM | 12.21 GiB | 12.55 GiB | +2.78% |

The comparison ran on the same NVIDIA A100-SXM4-80GB environment with sequence length 1024, BF16, gradient accumulation 16, and one epoch of identical underlying text exposure.

The efficiency result remains positive, but final tokenizer selection remains open. Exact document-reset, byte-normalized evaluation is now complete on the same frozen 1,503-record Oromo validation set:

| Model state | Exact BPB | Relative to base |
| --- | ---: | ---: |
| Original `google/gemma-3-1b-pt` | 2.670046 | baseline |
| Native tokenizer + Oromo CPT | **1.733832** | **-35.06%** |
| OromoLM +8K + Oromo CPT | 1.863339 | **-30.21%** |

Lower BPB is better. This establishes that OromoCorpus continued pretraining substantially improves held-out Afaan Oromoo modeling.

A later fresh-data +8K continuation experiment (v0.3) closed almost all of the remaining quality gap:

| +8K v0.3 step | Exact Oromo BPB |
| ---: | ---: |
| 250 | 1.799051 |
| 500 | 1.758330 |
| 750 | 1.741555 |
| 1,000 | 1.735902 |
| 1,250 | 1.734836 |
| 1,470 | **1.734823** |

The native-tokenizer CPT benchmark remains **1.733832395 BPB**. The best +8K v0.3 checkpoint therefore remains just above it by about **0.057%**, so the project does **not** claim a +8K quality win yet.

General-language retention remained within the predeclared gate. Untouched Gemma scored **1.013254631 WikiText BPB**, setting a +5% ceiling at **1.063917363**; the final +8K checkpoint scored **1.033754855** and passed.

The v0.3 result was preserved locally from the A100 environment and **53/53 hashed files matched with zero integrity failures**.

A controlled **Gemma +4K model-level ablation** has now completed both predeclared training stages **and the frozen evaluation gate**. Its Stage B exact Oromo BPB curve was:

| +4K step | Exact Oromo BPB |
| ---: | ---: |
| 250 | 1.781058836 |
| 500 | 1.744201370 |
| 750 | **1.727396376** |
| 1,000 | **1.721889019** |
| 1,250 | **1.720904266** |
| 1,500 | **1.720890953** |
| 1,517 | **1.720890950** |

The +4K path crosses both the native-tokenizer CPT reference (**1.733832395**) and the +8K v0.3 reference (**1.734823064**) by step 750. The final step-1517 result is about **0.75% lower/better than native CPT** and **0.80% lower/better than +8K v0.3** on the same frozen Oromo BPB protocol.

General-language retention also passes the predeclared WikiText gate. Checkpoint 1,250 scored **1.030453326 BPB** and checkpoint 1,517 scored **1.030463994 BPB**, both below the fixed ceiling of **1.063917363** and both slightly better/lower than the +8K final WikiText result of **1.033754855**.

Under the predeclared decision rules, **Gemma +4K is now the strongest current OromoLM tokenizer/model candidate**. This is a result on the declared frozen evaluation protocol, not a claim of universal superiority across every downstream task.

A source-level robustness check supports that result: +4K beats +8K on **all six** Oromo validation sources and beats native CPT on **five of six**. The only source-level regression versus native CPT is Wikimedia at **+0.345% BPB**. At the record level, +4K wins **57.22%** of matched records versus native CPT and **72.26%** versus +8K. The gain is therefore broad, but not universal; Wikimedia and the regression tail remain explicit follow-up targets. A paired 10,000-resample bootstrap further supports the result: +4K-vs-native has a 95% mean-delta interval of **[-0.020199325, -0.007414796] BPB**, and +4K-vs-+8K has **[-0.053106421, -0.043233026] BPB**; both intervals remain entirely below zero.

The complete +4K run was copied back from RunPod and verified against its preservation manifest: **66 files checked, 0 failures**, totaling about **18 GB** locally. Large model artifacts remain outside normal Git tracking.

Full experiment records: [`docs/CPT_PILOT_REPORT.md`](docs/CPT_PILOT_REPORT.md), [`docs/CPT_RERUN_V0_2_RESULTS.md`](docs/CPT_RERUN_V0_2_RESULTS.md), [`docs/CPT_LEARNING_CURVE_V0_3_RESULTS.md`](docs/CPT_LEARNING_CURVE_V0_3_RESULTS.md), and [`docs/CPT_4K_ABLATION_RESULTS.md`](docs/CPT_4K_ABLATION_RESULTS.md).

### Build verification

At the latest verified checkpoint:

```text
104 tests passed
```

The test suite covers corpus schema, ingestion, cleaning, quality decisions, deduplication, validation, and source-registry behavior.

---

## Data principles

Oromo AI uses a provenance-first corpus policy.

Every accepted source should have:

- identifiable origin and ownership;
- an explicit license or training-use decision;
- immutable raw-source handling;
- conservative cleaning;
- exact and near-duplicate removal;
- reproducible hashes and manifests;
- source-level acceptance/rejection records;
- evaluation-data separation.

The pipeline intentionally avoids destructive normalization that could erase Qubee orthography, dialectal variation, morphology, punctuation, or legitimate multilingual context.

Detailed policy: [`docs/CLEANING_POLICY.md`](docs/CLEANING_POLICY.md).

---

## Repository structure

```text
oromo-ai/
├── data/          # source registry, manifests, processed corpus metadata
├── docs/          # research reports, policies, roadmap, source audits
├── reports/       # generated research/evaluation outputs
├── scripts/       # reproducible corpus and research utilities
├── src/           # Python package and data pipeline
├── tests/         # automated tests
├── tokenizer/     # tokenizer training and evaluation artifacts
├── pyproject.toml
├── uv.lock
└── README.md
```

Generated raw/interim corpus artifacts are intentionally kept out of Git where appropriate.

---

## Quick start

Requirements:

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

Install dependencies:

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest -q
```

Inspect the source registry:

```bash
uv run python scripts/source_registry.py list
uv run python scripts/source_registry.py validate
```

The repository is research infrastructure under active development; commands and artifact formats may evolve as corpus and model work progresses.

---

## Research roadmap

```text
✅ Corpus pipeline and provenance framework
✅ AfriBERTa Oromo v0.1.2 validated
✅ Wikimedia omwiki source qualified
✅ VOA Afaan Oromoo subset qualified
✅ WaxalNLP Oromo ASR source qualified
✅ MADLAD-400 Oromo technical and quality qualification complete
✅ MADLAD-400 Oromo provenance recovery: 1,917 records / 1,874,398 tokens mapped
✅ MADLAD-400 Oromo v0.2 approved under upstream ODC-BY dataset license
✅ Frozen tokenizer evaluation set
✅ Custom tokenizer benchmark
✅ Native causal-tokenizer benchmark
✅ Whole-word augmentation study
✅ Cleaned Gemma +8K tokenizer frozen as a training candidate
✅ Dual-tokenizer workload audit and 1024-token packing
✅ Native-vs-+8K 10-step GPU smoke tests
✅ First controlled Gemma native-vs-+8K CPT pilot

✅ OromoCorpus 50M minimum achieved — current total 56,014,939 reference tokens
🔄 Expand OromoCorpus toward the preferred 100M target
✅ Exact byte-normalized three-way LM evaluation
✅ +8K v0.3 fresh-data learning curve + forgetting controls
✅ +4K two-stage CPT ablation training complete
✅ +4K exact Stage B Oromo BPB curve + WikiText retention evaluation
✅ +4K selected as strongest current candidate under the frozen gate
🔄 Develop OromoBench

✅ Tiny CPT proof
⏳ Scaled continued pretraining
⏳ Supervised instruction tuning
⏳ Model release engineering
⏳ Translation / retrieval / speech applications
```

The complete roadmap is maintained in [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## Documentation

Detailed technical material lives in `docs/` rather than being duplicated in this README.

| Document | Purpose |
| --- | --- |
| [Corpus Expansion Plan](docs/CORPUS_EXPANSION_PLAN.md) | 50M/100M acquisition and release strategy |
| [Corpus Statistics Report](docs/CORPUS_STATISTICS_REPORT.md) | Corpus measurements and validation |
| [Corpus Quality Report](docs/CORPUS_QUALITY_REPORT.md) | Quality analysis |
| [Cleaning Policy](docs/CLEANING_POLICY.md) | Conservative preprocessing rules |
| [Tokenizer Research Report](docs/TOKENIZER_RESEARCH_REPORT.md) | Tokenizer benchmarks and experiments |
| [CPT Pilot Report](docs/CPT_PILOT_REPORT.md) | Gemma native-vs-+8K workload, GPU, quality, and reproducibility evidence |
| [CPT Reproduction v0.2 Results](docs/CPT_RERUN_V0_2_RESULTS.md) | Exact three-way Oromo BPB results, rerun hashes, and next quality gate |
| [CPT +4K Ablation Protocol](docs/CPT_4K_ABLATION_PROTOCOL.md) | Predeclared two-stage +4K comparison design and decision rules |
| [CPT +4K Ablation Results](docs/CPT_4K_ABLATION_RESULTS.md) | Full +4K learning curve, retention result, preservation evidence, and candidate-selection outcome |
| [Evaluation](docs/EVALUATION.md) | OromoBench and normalized model-evaluation direction |
| [Roadmap](docs/ROADMAP.md) | Project phases and current milestone |
| [MADLAD License Decision](docs/sources/MADLAD_400_LICENSE_DECISION.md) | ODC-BY approval basis, attribution obligations, and scope limitations |
| [MADLAD Provenance Review](docs/sources/MADLAD400_PROVENANCE_REVIEW.md) | Partial source-level provenance recovery, URL/domain audit, and VOA review |
| [HPLT3 Oromo Report](docs/sources/HPLT3_OROMO_REPORT.md) | HPLT3 filtering, deduplication, quality, language verification, and frozen metrics |
| [HPLT3 License Decision](docs/sources/HPLT3_LICENSE_DECISION.md) | CC0 packaging scope, underlying-text caveat, and project acceptance basis |
| [Naming](docs/NAMING.md) | Canonical project naming |

Source-specific qualification reports are maintained under [`docs/sources/`](docs/sources/).

---

## Contribution priorities

Useful contributions include:

- rights-clear Afaan Oromoo corpora;
- linguistic review and annotations;
- dialect and domain metadata;
- parallel corpora;
- tokenizer and evaluation research;
- benchmark construction;
- reproducible data-engineering improvements.

All contributed data must preserve clear provenance and licensing information.

---

## Project principle

> **Data before model. Evidence before scale.**

Oromo AI is being built one validated layer at a time.

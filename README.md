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
| **OromoTokenizer** | Tokenization research and Oromo-aware tokenizer candidates | ✅ Core benchmarks complete |
| **OromoLM** | Continued-pretrained Afaan Oromoo causal language models | ⏳ Base-model strategy in progress |
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
| **Accepted total** | **511,510** | **52,137,803** |

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
Current planning total:   52,137,803
Progress:                 104.28%
Margin above minimum:      2,137,803

OromoCorpus v0.3 target: 100,000,000 tokens
Current progress:         52.14%
```

The full WURA Oromo package remains under source-level review and does not count as an accepted source by itself. Only independently audited and rights-cleared subsets are admitted.

With the 50M minimum now achieved, corpus acquisition continues toward the preferred **100M** target with greater emphasis on domain, dialect, literary, educational, technical, and conversational diversity rather than raw volume alone.

### OromoTokenizer

Tokenizer research has established:

| Tokenizer | Vocabulary | Tokens/word | Fragmentation | UNK |
| --- | ---: | ---: | ---: | ---: |
| Oromo Unigram 48K + byte fallback | 48,000 | **1.4000** | **38.75%** | 0 |
| Oromo Unigram 32K + byte fallback | 32,000 | 1.4495 | 40.83% | 0 |
| AfriBERTa | 70,006 | 1.6765 | 39.83% | 0 |

Native causal-model tokenizers were also benchmarked on the frozen Oromo evaluation set. Whole-word vocabulary augmentation improved fragmentation substantially, but it did not match the custom Oromo tokenizer's sequence efficiency.

Full results: [`docs/TOKENIZER_RESEARCH_REPORT.md`](docs/TOKENIZER_RESEARCH_REPORT.md).

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

✅ OromoCorpus 50M minimum achieved — 52,137,803 reference tokens
🔄 Expand OromoCorpus toward the preferred 100M target
🔄 Select OromoLM base-model + tokenizer strategy
🔄 Develop OromoBench

⏳ Tiny CPT proof
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
| [Evaluation](docs/EVALUATION.md) | OromoBench evaluation direction |
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

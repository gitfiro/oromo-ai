# 🟩 Oromo AI

<p align="center">
  <strong>Open research infrastructure for Afaan Oromoo AI</strong><br>
  <em>Building OromoCorpus, OromoTokenizer, OromoLM, and OromoBench.</em>
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
| **OromoCorpus** | Versioned, provenance-tracked Afaan Oromoo training corpus | 🔄 Active expansion |
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
| **Total** | **421,957** | **12,558,641** |

```text
OromoCorpus v0.2 minimum: 50,000,000 tokens
Current planning total:   12,558,641
Progress:                 25.12%
Remaining:                37,441,359

OromoCorpus v0.3 target: 100,000,000 tokens
Current progress:         12.56%
```

The full WURA Oromo package remains under source-level review and does not count as an accepted source by itself. Only independently audited and rights-cleared subsets are admitted.

The next corpus-expansion priority is to identify rights-clear sources or publisher clusters capable of contributing roughly **5M–15M+ net-new tokens**, while still accepting smaller sources when they add important domain or dialect diversity.

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
✅ Frozen tokenizer evaluation set
✅ Custom tokenizer benchmark
✅ Native causal-tokenizer benchmark
✅ Whole-word augmentation study

🔄 Expand OromoCorpus toward 50M net unique tokens
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

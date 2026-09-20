# Oromo AI Roadmap

## Project objective

Oromo AI is building an open, research-grade Afaan Oromoo AI stack with a deliberate progression from validated data to language modeling, instruction tuning, evaluation, and applications.

Canonical component names used throughout this roadmap are **OromoCorpus** for the corpus family, **OromoTokenizer** for tokenizer research, **OromoLM** for the model family, and **OromoBench** for evaluation. See `docs/NAMING.md`.

The working sequence is:

```text
OromoCorpus
  ↓
OromoTokenizer research
  ↓
Causal base-model selection
  ↓
Tiny CPT proof
  ↓
Scale experiments
  ↓
Instruction tuning
  ↓
OromoBench
  ↓
Inference/API/applications
```

The project should not skip ahead simply because later stages are more visible.

The active OromoCorpus objective is **50 million net unique OromoLM-tokenizer tokens minimum**, with **100 million tokens preferred**. Counts are taken after cleaning and cross-source deduplication; evaluation holdouts and separately labeled synthetic data do not count toward this natural-language target.

---

## Phase 0 — Repository and research foundation

**Status: complete**

Completed:

- repository structure;
- Python/uv environment;
- testing framework;
- project-level data directories;
- model/training/evaluation scaffolding.

---

## Phase 1 — Corpus ingestion and provenance

**Status: complete for initial production source**

Completed:

- AfriBERTa Oromo source ingestion;
- stable source identifiers;
- record schema;
- provenance metadata;
- source licensing documentation;
- raw/processed separation.

Initial source:

```text
castorini/afriberta-corpus
subset: afaanoromoo
license: Apache-2.0
```

---

## Phase 2 — Conservative cleaning and production corpus

**Status: complete for v0.1.2**

Current production corpus:

```text
afriberta_oromo_v0.1.2
```

Validated output:

```text
410,193 processed records
52,122,367 processed characters
614 primary quality rejections
34 duplicate-after-cleaning records
648 rejection-ledger entries
```

Processed SHA-256:

```text
6f990088c8fb319b46c9a25a1c463e7a700cc8d292da781cfcc44ac4391ee0f6
```

The cleaning philosophy remains conservative: remove demonstrable extraction/data noise without flattening dialect, orthography, politics, religion, style, or legitimate multilingual context.

---

## Phase 2B — OromoCorpus expansion

**Status: active**

Release milestones:

| Release | Net unique OromoLM tokens | Release requirement |
| --- | ---: | --- |
| OromoCorpus v0.2 | **50M minimum** | Multiple licensed source families, cross-source deduplication, and published mixture statistics |
| OromoCorpus v0.3 | **100M preferred** | Broader domain and dialect balance with reproducible source manifests |

The official total is calculated only after conservative cleaning and exact/near-duplicate removal across all included sources. The project will additionally report raw records, characters, whitespace tokens, and per-source retention so that the expansion remains auditable.

### Verified expansion progress — 2026-09-20

Using the Oromo Unigram 48K + byte-fallback research tokenizer as the current planning reference:

| Accepted source | Net-new records | 48K reference tokens | Status |
| --- | ---: | ---: | --- |
| AfriBERTa Afaan Oromoo v0.1.2 | 410,193 | 9,587,934 | approved seed |
| Wikimedia omwiki v0.1 | 2,254 | 1,070,896 | approved/frozen |
| VOA Afaan Oromoo via WURA v0.1 | 9,510 | 1,899,811 | approved/frozen |
| **Total** | **421,957** | **12,558,641** | **25.12% of v0.2 minimum** |

```text
remaining to 50M: 37,441,359 reference tokens
progress to 100M: 12.56%
```

The full WURA Oromo package remains under review and does not count toward the accepted total. WURA is currently used as a source-discovery/provenance layer; only independently rights-cleared subsets enter OromoCorpus.

Next-source selection now prioritizes rights-clear sources or publisher clusters with a realistic **5M–15M+ net-new-token** contribution. Smaller sources remain worthwhile when they materially improve domain, dialect, literary, conversational, or technical coverage.

Primary work:

- maintain a source registry containing ownership, license, provenance, acquisition date, domain, dialect metadata, and redistribution constraints;
- audit and ingest additional public or explicitly licensed Oromo sources;
- perform source-specific native-speaker quality sampling;
- deduplicate at document, paragraph, and near-duplicate levels across sources;
- balance education, literature, news, public documents, technical material, cultural material, and conversational language;
- isolate OromoBench and other evaluation material before any training export;
- keep synthetic and machine-translated datasets versioned separately from the natural-language corpus.

The first expansion audit should measure the net contribution of each candidate source against `afriberta_oromo_v0.1.2`; raw advertised source size is not treated as usable yield.

Detailed plan: `docs/CORPUS_EXPANSION_PLAN.md`

---

## Phase 3 — OromoTokenizer research

**Status: baseline and custom-candidate experiments complete**

Completed:

- reusable tokenizer metric layer;
- deterministic benchmark harness;
- frozen 10,000-record evaluation holdout;
- alignment audit;
- unknown-token audit;
- established multilingual baselines;
- custom SentencePiece Unigram candidates;
- 16K/24K/32K/48K vocabulary sweep;
- 32K and 48K byte-fallback variants;
- leakage-safe 400,193-record tokenizer training corpus.

Frozen tokenizer evaluation sample:

```text
10,000 records
seed: 20260919
SHA-256:
369c4438beab0d619336448eab7e27aae29d0722fd089088dbf0b2addc3d81f5
```

Serious OromoTokenizer research references:

```text
oromo-unigram-32k-byte
oromo-unigram-48k-byte
```

Current strongest sequence-efficiency reference:

```text
oromo-unigram-48k-byte
1.4000 tokens/word
38.75% word fragmentation
61.25% single-token words
0 unknown tokens
```

These are **OromoTokenizer research candidates**, not a final production tokenizer.

Detailed report:

`docs/TOKENIZER_RESEARCH_REPORT.md`

---

## Phase 4 — Causal-LM tokenizer and base-model research

**Status: Phase 4A and Phase 4B1 complete; strategy decision in progress**

### Phase 4A — native causal tokenizer benchmark

Completed on the frozen 10K Oromo holdout:

| Native tokenizer | Tok/Word | Frag % | Single % | UNK |
| --- | ---: | ---: | ---: | ---: |
| Gemma 3 1B | **2.7855** | **85.91%** | **14.09%** | 0 |
| Qwen3.5 0.8B | 2.9191 | 86.94% | 13.06% | 0 |
| Llama 3.2 1B | 3.0311 | 88.32% | 11.68% | 0 |
| Qwen3 0.6B | 3.0713 | 88.89% | 11.11% | 0 |
| Mistral 7B v0.3 | 3.3241 | 93.09% | 6.91% | 0 |

Gemma 3 currently has the most efficient native causal tokenizer of the tested families, but every native tokenizer remains substantially less sequence-efficient than the custom Oromo references.

### Phase 4B1 — whole-word vocabulary augmentation

Completed for:

- Llama 3.2 1B;
- Qwen3 0.6B;
- Gemma 3 1B.

Candidate words are derived only from the 400,193-record leakage-safe tokenizer-training split and ranked by:

```text
frequency × (native token pieces - 1)
```

Results:

| Model tokenizer | Native | +2K | +4K | +8K | +16K |
| --- | ---: | ---: | ---: | ---: | ---: |
| Llama 3.2 1B | 3.0311 | 2.5705 | 2.4715 | 2.3716 | **2.2821** |
| Qwen3 0.6B | 3.0713 | 2.6063 | 2.5058 | 2.4049 | **2.3140** |
| Gemma 3 1B | 2.7855 | 2.4475 | 2.3692 | 2.2903 | **2.2172** |

The largest early gain occurs in the first few thousand additions. At +4K, all three tokenizers reach approximately 38% word fragmentation, close to the custom Oromo 48K reference. Token-per-word efficiency, however, remains well above the custom reference of 1.4000.

### Current decision point

Phase 4 has established that:

- native causal tokenizers cover Oromo but tokenize it inefficiently;
- whole-word vocabulary augmentation is highly effective for frequent lexical forms;
- augmentation preserves the original tokenizer vocabulary/ID space and appends new IDs;
- whole-word augmentation alone does not fully solve Oromo subword inefficiency.

Before model-level CPT begins, the next research decision is whether to:

1. proceed with a practical whole-word augmentation budget;
2. run a Phase 4B2 Oromo subword-augmentation experiment;
3. retain the native tokenizer despite sequence inflation; or
4. pursue deeper tokenizer replacement only if the evidence justifies its pretrained-embedding cost.

The base model must ultimately be selected from the combined evidence of tokenizer efficiency, model quality, architecture, license, compute requirements, and CPT feasibility—not tokenizer metrics alone.

---

## Phase 5 — Tiny OromoLM continued-pretraining proof

**Status: planned**

Target:

A small, affordable OromoLM proof that validates the complete training pipeline before scaling.

The proof should test:

- causal-LM data packing;
- tokenizer/model compatibility;
- checkpoint loading/saving;
- optimizer/scheduler configuration;
- mixed precision;
- gradient accumulation;
- loss behavior;
- validation loss;
- held-out Oromo improvement;
- catastrophic-forgetting controls;
- reproducibility.

Approximate model scale under consideration:

```text
~0.5B class
```

The exact model depends on Phase 4 evidence.

Success means the training architecture works and produces measurable Oromo-language gains. It does not mean the model is release-ready.

---

## Phase 6 — OromoLM-1B-class experiment

**Status: planned**

Only proceed after the tiny proof demonstrates:

- stable training;
- reproducible checkpoints;
- useful validation improvement;
- manageable compute cost;
- no major tokenizer/data failure.

This phase should establish whether additional model capacity produces enough value to justify later scaling.

---

## Phase 7 — Continued pretraining at selected scale

**Status: planned**

Primary objective:

Transfer a capable pretrained model's general reasoning and language abilities toward stronger Afaan Oromoo modeling through raw-text continual pretraining.

Important controls:

- Oromo/general-language mixture strategy;
- replay data where appropriate;
- learning-rate conservatism;
- checkpoint evaluation;
- catastrophic-forgetting checks;
- training-token accounting;
- exact data manifests.

---

## Phase 8 — Supervised fine-tuning

**Status: planned**

Only after the base model demonstrates meaningful Afaan Oromoo language modeling suitable for the OromoLM family.

SFT goals may include:

- Oromo instruction following;
- question answering;
- summarization;
- translation;
- structured generation;
- conversational behavior.

LoRA or QLoRA may be used where appropriate, but parameter-efficient tuning does not substitute for language acquisition through CPT.

---

## Phase 9 — OromoBench

**Status: in development / expands alongside model work**

Evaluation categories:

- orthography;
- grammar;
- morphology;
- vocabulary;
- comprehension;
- summarization;
- translation;
- reasoning;
- factuality;
- instruction following;
- safety.

Benchmark data must remain separated from training data.

---

## Phase 10 — Model release engineering

**Status: planned**

Before public release:

- model card;
- tokenizer card;
- training-data summary;
- license review;
- reproducibility notes;
- benchmark report;
- inference examples;
- limitations;
- safety evaluation;
- artifact checksums.

Model releases must use the `OromoLM-<size>` family convention. Instruction-tuned and specialized variants add a clear suffix, such as `OromoLM-1B-Instruct` or `OromoLM-1B-Translate`.

---

## Phase 11 — Applications

**Status: future**

Potential downstream systems:

- OromoLM-Instruct chat model;
- translation;
- retrieval/RAG;
- search;
- spelling/grammar tools;
- embeddings;
- ASR;
- TTS;
- developer API.

Applications come after validated model infrastructure, not before it.

---

## Immediate next milestone

The project is currently here:

```text
✅ Production corpus v0.1.2
✅ Source registry + source-level manifest framework
✅ Wikimedia omwiki source qualified and frozen
✅ VOA Afaan Oromoo via WURA source qualified and frozen
✅ Current 48K-reference corpus measurement: 12,558,641 tokens
✅ Frozen tokenizer evaluation
✅ Multilingual/custom tokenizer baselines
✅ Native causal-LM tokenizer benchmark (Phase 4A)
✅ Whole-word augmentation study (Phase 4B1)
        ↓
🔄 Expand OromoCorpus from 12.56M toward 50M net unique tokens
        ↓
🔄 Audit next rights-clear 5M–15M+ token source / publisher cluster
        ↓
⏳ Continue base-model + tokenizer strategy decision
        ↓
⏳ Tiny CPT proof
```

The immediate data task is to identify and audit the next high-yield, rights-clear Afaan Oromoo source or publisher cluster. Each new source must pass provenance review, conservative quality processing, exact and near cross-source deduplication, and source-level manifest/report freezing before its tokens are added to the planning total.

Tokenizer/base-model research may continue in parallel, and a tiny CPT proof may validate the training architecture, but scaled continued pretraining waits for an evidence-backed expanded corpus.

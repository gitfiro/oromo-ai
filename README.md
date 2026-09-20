# 🟩 OROMO AI

<p align="center">
  <strong>Open AI infrastructure for Afaan Oromoo</strong><br>
  <em>Building OromoCorpus, OromoTokenizer, OromoLM, OromoBench, and the applications they enable.</em>
</p>

<p align="center">
  <strong>OromoCorpus → OromoTokenizer → OromoLM → Instruction Tuning → OromoBench → Applications</strong>
</p>

<p align="center">
  <a href="https://github.com/gitfiro/oromo-ai">
    <img src="https://img.shields.io/badge/GitHub-Oromo%20AI-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Hugging Face">
</p>

---

## 🌍 What Is Oromo AI?

**Oromo AI** is an independent open-source AI research and engineering project focused on building high-quality artificial intelligence infrastructure for **Afaan Oromoo**.

The project is not simply about fine-tuning an existing chatbot.

The long-term objective is to build a complete Oromo AI technology stack:

```text
                         ┌─────────────────────┐
                         │      OROMO AI       │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
        ┌───────────┐         ┌───────────┐        ┌───────────┐
        │   DATA    │         │   MODELS  │        │   TOOLS   │
        └─────┬─────┘         └─────┬─────┘        └─────┬─────┘
              │                     │                     │
              ▼                     ▼                     ▼
        OromoCorpus             OromoLM             Translation
        Data Pipeline        OromoLM-Instruct       ASR / TTS
        Provenance            Embeddings             Morphology
        Quality Control       Specialized Models     RAG / Search
        Evaluation Data       Future Foundation      APIs / Apps
```

The project is being developed as a **research-grade foundation**, not as a collection of disconnected demos.

---

## 🏷️ Project Naming

The repository uses a stable naming system so that the initiative, datasets, tokenizers, models, and evaluations are not confused with one another.

| Scope | Canonical name | Usage |
| --- | --- | --- |
| Research initiative | **Oromo AI** | The overall open research and engineering effort |
| GitHub repository | **`oromo-ai`** | Source code, research, documentation, and reproducible experiments |
| Corpus family | **OromoCorpus** | Versioned Afaan Oromoo training and evaluation corpora |
| Tokenizer family | **OromoTokenizer** | Custom tokenizer candidates and tokenizer-adaptation research |
| Foundation-model family | **OromoLM** | Continued-pretrained Afaan Oromoo causal language models |
| Evaluation suite | **OromoBench** | Versioned Afaan Oromoo model evaluation framework |

Planned release identifiers follow the model family and size:

```text
OromoLM-600M
OromoLM-1B
OromoLM-1B-Instruct
OromoLM-1B-Translate
```

Names for unreleased artifacts describe the intended family and **do not imply that a production model or tokenizer has already been selected**. Historical dataset IDs, experiment names, file paths, and third-party model identifiers remain unchanged for reproducibility.

See [`docs/NAMING.md`](docs/NAMING.md) for the canonical naming policy.

---

# 🎯 Vision

The goal is to make Afaan Oromoo a first-class language in modern AI systems.

That means building the infrastructure required to support:

* Afaan Oromoo language modeling with OromoLM
* OromoLM instruction-following variants
* Afaan Oromoo text generation
* Oromo ↔ English translation
* Oromo ↔ other Ethiopian and African languages
* morphology-aware NLP
* spelling and grammar tools
* question answering
* summarization
* information retrieval
* Oromo speech recognition
* Oromo text-to-speech
* RAG systems
* Oromo AI evaluation benchmarks
* developer APIs
* applications built on top of the models

The long-term architecture is:

```text
                         OROMO AI
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
        TEXT              VOICE              NLP
          │                 │                 │
    ┌─────┼─────┐       ┌───┴───┐       ┌────┼────┐
    │     │     │       │       │       │    │    │
 OromoLM RAG Search     ASR    TTS   Translation Morphology
    │
    ▼
 OromoLM-Instruct
    │
    ▼
 API / Applications
```

---

# 🧭 Core Principle

> **Data before model.**

A large language model trained on weak, duplicated, corrupted, poorly documented, or legally ambiguous data does not become high-quality merely because the model is large.

Therefore Oromo AI is intentionally being built in this order:

```text
1. Data acquisition
        ↓
2. Provenance and licensing
        ↓
3. Corpus auditing
        ↓
4. Conservative cleaning
        ↓
5. Deduplication
        ↓
6. Validation
        ↓
7. Dataset manifests
        ↓
8. Tokenizer research
        ↓
9. Model experiments
        ↓
10. Instruction tuning
        ↓
11. Evaluation
        ↓
12. Applications
```

This ordering is deliberate.

---

# 🚧 Current Project Status

| Area                         | Status            |
| ---------------------------- | ----------------- |
| Repository architecture      | ✅ Established     |
| Python environment           | ✅ Established     |
| Data schema                  | ✅ Established     |
| Data ingestion               | ✅ Established     |
| Unicode normalization        | ✅ Implemented     |
| Conservative cleaning        | ✅ Implemented     |
| Corpus auditing              | ✅ Implemented     |
| Rejection decision engine    | ✅ Implemented     |
| Deduplication                | ✅ Implemented     |
| Provenance tracking          | ✅ Implemented     |
| OromoCorpus processing       | ✅ Completed       |
| v0.1.2 validation            | ✅ Passed          |
| Corpus statistics            | ✅ Generated       |
| OromoCorpus expansion        | 🔄 12.56M / 50M reference tokens (25.12%) |
| OromoTokenizer research      | ✅ Native + custom benchmark complete |
| OromoTokenizer training      | ✅ Candidates benchmarked |
| Causal-LM tokenizer research | ✅ Phase 4A complete |
| Vocabulary augmentation      | ✅ Phase 4B1 complete |
| OromoLM base selection       | 🔄 In progress     |
| OromoLM continued pretraining | ⏳ Planned        |
| SFT                          | ⏳ Planned         |
| OromoBench                   | 🔄 In development |
| ASR                          | ⏳ Planned         |
| TTS                          | ⏳ Planned         |
| API                          | ⏳ Planned         |

---


## 🔤 OromoTokenizer Research — Current Results

OromoTokenizer research now includes frozen-set multilingual baselines, custom SentencePiece candidates, native causal-LM tokenizer benchmarks, and a whole-word vocabulary-augmentation feasibility study.

The canonical tokenizer evaluation set is a deterministic, frozen **10,000-record** holdout from `afriberta_oromo_v0.1.2`:

```text
tokenizer/evaluation/samples/afriberta_oromo_v0.1.2_n10000.jsonl
```

Evaluation sample SHA-256:

```text
369c4438beab0d619336448eab7e27aae29d0722fd089088dbf0b2addc3d81f5
```

The holdout is excluded by stable `record_id` from the tokenizer-training corpus:

```text
400,193 tokenizer-training records
10,000 frozen evaluation records
0 evaluation leakage
```

### OromoTokenizer research references

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oromo Unigram 48K + byte fallback | 48,000 | **1.4000** | **38.75%** | **61.25%** | **0** | **5.4562** |
| Oromo Unigram 32K + byte fallback | 32,000 | 1.4495 | 40.83% | 59.17% | **0** | 5.2699 |
| AfriBERTa | 70,006 | 1.6765 | 39.83% | 60.16% | **0** | 4.5563 |

The 48K byte-fallback tokenizer remains the strongest sequence-efficiency reference measured so far, but it is **not** automatically suitable as a drop-in replacement for a pretrained causal LM because tokenizer IDs and pretrained embedding rows are coupled.

### Native causal-LM tokenizers

All causal models below represent the frozen Oromo sample without unknown tokens, but they fragment Oromo much more heavily than the custom references.

| Native tokenizer | Tok/Word | Frag % | Single % | UNK |
| --- | ---: | ---: | ---: | ---: |
| Gemma 3 1B | **2.7855** | **85.91%** | **14.09%** | 0 |
| Qwen3.5 0.8B | 2.9191 | 86.94% | 13.06% | 0 |
| Llama 3.2 1B | 3.0311 | 88.32% | 11.68% | 0 |
| Qwen3 0.6B | 3.0713 | 88.89% | 11.11% | 0 |
| Mistral 7B v0.3 | 3.3241 | 93.09% | 6.91% | 0 |

Gemma 3 is the strongest native causal tokenizer tested so far, yet it still uses almost twice as many tokens per whitespace word as the custom Oromo 48K-byte reference.

### Phase 4B1 — whole-word vocabulary augmentation

Instead of immediately replacing a pretrained tokenizer with an OromoTokenizer candidate, Oromo AI tested a conservative strategy:

```text
existing pretrained tokenizer
        +
selected Oromo whole-word tokens
        ↓
preserve native vocabulary IDs
append only new Oromo vocabulary IDs
```

Candidates are derived only from the leakage-safe 400,193-record tokenizer-training split and ranked by estimated training-side savings:

```text
frequency × (native token pieces - 1)
```

Results on the frozen 10K holdout:

| Model tokenizer | Native | +2K | +4K | +8K | +16K |
| --- | ---: | ---: | ---: | ---: | ---: |
| Llama 3.2 1B | 3.0311 | 2.5705 | 2.4715 | 2.3716 | **2.2821** |
| Qwen3 0.6B | 3.0713 | 2.6063 | 2.5058 | 2.4049 | **2.3140** |
| Gemma 3 1B | 2.7855 | 2.4475 | 2.3692 | 2.2903 | **2.2172** |

At +4K, word-fragmentation rates fall to roughly the custom-tokenizer reference level:

```text
Llama +4K   38.19%
Qwen3 +4K   38.70%
Gemma +4K   38.21%
Oromo 48K   38.75%
```

However, token-per-word efficiency remains substantially worse than the best OromoTokenizer research reference. This shows that whole-word augmentation repairs frequent-word fragmentation very effectively but does not fully solve Oromo subword efficiency.

The current decision point is therefore:

```text
Phase 4A native benchmarking        ✅ complete
Phase 4B1 whole-word augmentation  ✅ complete
        ↓
compare augmentation cost / diminishing returns
        ↓
decide whether to test Oromo subword augmentation
        ↓
select base-model + tokenizer strategy
        ↓
tiny CPT proof
```

Full methodology and results:

[**docs/TOKENIZER_RESEARCH_REPORT.md**](docs/TOKENIZER_RESEARCH_REPORT.md)

---

# 📊 OromoCorpus — Current Release

The first versioned OromoCorpus release uses the **AfriBERTa Oromo corpus**, specifically the Afaan Oromoo portion of:

`castorini/afriberta-corpus`

The source is licensed under **Apache-2.0**.

The raw training split contains:

```text
410,841 source records
```

The current production dataset is:

```text
afriberta_oromo_v0.1.2
```

### v0.1.2 validated statistics

| Metric                           |      Value |
| -------------------------------- | ---------: |
| Input records                    |    410,841 |
| Processed records                |    410,193 |
| Rejected records                 |        614 |
| Duplicate-after-cleaning records |         34 |
| Clean decisions                  |        360 |
| Changed records                  |        264 |
| Processed characters             | 52,122,367 |
| Rejection-ledger entries         |        648 |
| Malformed JSON records           |          0 |
| Empty processed records          |          0 |
| Duplicate cleaned hashes         |          0 |

The complete statistics and validation methodology are documented in:

[`docs/CORPUS_STATISTICS_REPORT.md`](docs/CORPUS_STATISTICS_REPORT.md)

## 🎯 Official OromoCorpus Expansion Target

Oromo AI is now working toward a **50–100 million token** natural-language corpus:

| Milestone | Target | Meaning |
| --- | ---: | --- |
| **OromoCorpus v0.2** | **50M tokens minimum** | First corpus-expansion release suitable for meaningful OromoLM continued-pretraining experiments |
| **OromoCorpus v0.3** | **100M tokens preferred** | Broader, more balanced corpus for stronger OromoLM training and evaluation |

### Current measured planning snapshot — 2026-09-20

Using the current **Oromo Unigram 48K + byte-fallback research tokenizer as a planning reference** (not yet the final OromoLM tokenizer), the accepted corpus currently measures:

| Accepted source | Net-new records | 48K reference tokens | Status |
| --- | ---: | ---: | --- |
| AfriBERTa Afaan Oromoo v0.1.2 | 410,193 | 9,587,934 | Approved seed |
| Afaan Oromoo Wikipedia (omwiki) | 2,254 | 1,070,896 | Approved, frozen |
| VOA Afaan Oromoo via WURA | 9,510 | 1,899,811 | Approved provenance-cleared subset |
| **Current total** | **421,957** | **12,558,641** | **25.12% of 50M** |

```text
50M minimum target:     50,000,000
current planning total: 12,558,641
remaining:              37,441,359
progress:               25.12%
```

The WURA Oromo package remains under source-level review as a discovery layer; only the separately audited VOA subset is approved. Source-specific frozen reports are available at:

- [`docs/sources/WIKIMEDIA_OMWIKI_REPORT.md`](docs/sources/WIKIMEDIA_OMWIKI_REPORT.md)
- [`docs/sources/VOA_AFAAN_OROMOO_WURA_REPORT.md`](docs/sources/VOA_AFAAN_OROMOO_WURA_REPORT.md)
The official number means **net unique OromoLM-tokenizer tokens after cleaning and cross-source deduplication**. Raw source tokens, whitespace words, characters, and document counts will also be reported, but they do not replace the official post-processing token count.

The total excludes OromoBench and all other evaluation holdouts. Synthetic or machine-translated text must remain separately identified and does not count toward the primary natural-language target.

The expansion is governed by four requirements:

* multiple licensed source families;
* source-level provenance and reproducible manifests;
* cross-source exact and near-duplicate removal;
* domain and dialect diversity rather than token-count inflation.

See [`docs/CORPUS_EXPANSION_PLAN.md`](docs/CORPUS_EXPANSION_PLAN.md) for the release gates and acquisition strategy.

---

# 🔬 Why v0.1.2 Exists

Version `0.1.2` is not a wholesale rewrite of the corpus.

It is a **targeted correction** to the previous production dataset.

The investigation identified a narrow class of short extraction artifacts containing:

* very short text
* multiple tokens
* a high proportion of single-character tokens
* placeholder/replacement glyphs such as `■`, `□`, or `�`

A targeted rule was introduced rather than deleting every short record.

### The rule

```text
length < 20 characters
+
at least 3 tokens
+
≥75% single-character tokens
+
placeholder/replacement glyph
```

This removed exactly:

```text
49 records
628 characters
```

from v0.1.1.

No blanket rule such as:

```text
"delete every record under 20 characters"
```

was used.

This distinction matters because short Oromo text can be legitimate.

Examples such as:

```text
a f a a n i
```

are ambiguous and therefore preserved.

Likewise:

```text
2 H * 1 amu = 2 amu
```

is not automatically discarded simply because it is short or formula-like.

---

# 🧪 v0.1.1 → v0.1.2

The production comparison demonstrates that the new rule changed only the targeted artifact class.

| Metric                      |     v0.1.1 |     v0.1.2 | Delta |
| --------------------------- | ---------: | ---------: | ----: |
| Records                     |    410,242 |    410,193 |   -49 |
| Characters                  | 52,122,995 | 52,122,367 |  -628 |
| Records <20 chars           |        694 |        645 |   -49 |
| High single-character ratio |        321 |        272 |   -49 |
| Placeholder records         |        188 |        139 |   -49 |
| URL records                 |         46 |         46 |     0 |
| HTML records                |          0 |          0 |     0 |
| English-signal records      |      3,988 |      3,988 |     0 |

This is the kind of controlled change we want in a research dataset.

---

# 🧾 Rejection Ledger

The processor does not silently throw data away.

Rejected material is recorded in a separate ledger.

Current v0.1.2 rejection-ledger categories:

| Reason                     |   Count |
| -------------------------- | ------: |
| Scientific/genomic payload |     308 |
| Social-media spam          |     144 |
| Obvious extraction garbage |     111 |
| Short extraction artifact  |      49 |
| Duplicate after cleaning   |      34 |
| Technical/code payload     |       1 |
| Base64/data URI            |       1 |
| **Total ledger entries**   | **648** |

The difference between **614 primary rejected records** and **648 ledger entries** is intentional: the ledger also records **34 duplicate-after-cleaning entries**.

This preserves an auditable record of what happened during processing.

---

# 🧬 Data Philosophy

Oromo AI uses a provenance-first data model.

Each document should remain traceable to its origin.

The canonical record contains fields such as:

```text
text
language
source
source_url
license
author
title
domain
dialect
country
source_id
record_id
collected_at
quality_score
metadata
```

The language code for Afaan Oromoo is:

```text
orm
```

The project currently uses Ethiopia (`ET`) as the default country metadata where appropriate, but geographic metadata should not be interpreted as dialect information.

---

# 🧹 Conservative Cleaning

Cleaning is intentionally conservative.

The pipeline currently performs operations such as:

* Unicode NFC normalization
* whitespace normalization
* removal of obvious HTML tags
* removal of URLs where appropriate
* removal of terminal/bracketed CMS `Read More` artifacts
* removal of embed markers
* removal of obvious CMS boilerplate
* rejection of clearly corrupted extraction artifacts
* deduplication after normalization

It intentionally does **not**:

* lowercase the language
* ASCII-fold Oromo text
* remove normal punctuation
* translate Oromo into English
* rewrite sentences with an LLM
* normalize dialects into one artificial variety
* automatically delete every short sentence
* automatically delete every repeated vowel
* assume every English-looking token is contamination

The objective is to remove corruption without destroying linguistic information.

---

# 🧠 Oromo Linguistic Preservation

Afaan Oromoo contains linguistic information that generic cleaning systems can damage.

The project therefore preserves:

* Qubee orthography
* apostrophe forms
* long vowels
* Oromo-specific consonant sequences
* punctuation
* capitalization
* legitimate repetition
* dialect variation
* lexical variants
* morphological structure

Examples of characters and forms that require care include:

```text
Q / q
X / x
C / c
G / g
dh
ny
ph
ʼ
’
'
```

No simplistic ASCII-only normalization is acceptable for the production corpus.

---

# 🔍 English-Signal Detection

English-signal detection is treated as a **diagnostic**, not automatic contamination removal.

A record containing a common English word does not necessarily mean the record is English.

For example, Oromo text may contain:

* names
* technical terms
* organizations
* quoted material
* borrowed terminology
* URLs
* proper nouns

Therefore:

```text
English signal ≠ English contamination
```

Human-reviewable diagnostics are preferred over aggressive automatic deletion.

---

# 🧪 Validation

Every production corpus version must pass integrity checks.

Current v0.1.2 validation confirms:

```text
raw_sha256:
269cde87d84ad34463b7bd654b16737aeef756adbe2463518353004660187d6a

processed_sha256:
6f990088c8fb319b46c9a25a1c463e7a700cc8d292da781cfcc44ac4391ee0f6
```

Validation results:

```text
raw_hash_correct       = True
manifest_count_matches = True
manifest_chars_match   = True
no_malformed_json      = True
no_empty_records       = True
no_duplicate_hashes    = True
source_lines_unique    = True
accounting_correct     = True
```

This means the processed dataset is not merely "generated"; it has been checked against reproducible invariants.

---

# 🏗️ Repository Structure

```text
oromo-ai/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── manifests/
│   ├── instruction/
│   ├── parallel/
│   └── evaluation/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_POLICY.md
│   ├── DATA_SCHEMA.md
│   ├── DATA_PIPELINE.md
│   ├── CORPUS_STATISTICS_REPORT.md
│   └── ...
│
├── src/
│   └── oromo_ai/
│       └── data/
│           ├── schema.py
│           ├── ingest.py
│           ├── clean.py
│           ├── audit.py
│           ├── decide.py
│           ├── deduplicate.py
│           ├── validate.py
│           ├── process_text.py
│           └── ...
│
├── training/
│   ├── pretraining/
│   ├── sft/
│   └── preference/
│
├── evaluation/
│   └── oromobench/
│
├── tokenizer/
│
├── translation/
│
├── speech/
│   ├── asr/
│   └── tts/
│
├── inference/
├── api/
├── scripts/
├── configs/
├── models/
├── tests/
│
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# ⚙️ Development Tooling

The project uses a reproducible Python-based development and research stack.

Python:

```text
3.12.14
```

Environment manager:

```text
uv
```

Core ML stack:

```text
PyTorch
Transformers
Datasets
Tokenizers
Accelerate
PEFT
TRL
```

Data stack:

```text
PyArrow
DuckDB
Pandas
orjson
tqdm
```

Testing:

```text
pytest
```

The local machine is currently being used primarily for:

```text
development
data engineering
testing
auditing
experimentation
```

Large-scale model training will use appropriate GPU infrastructure rather than assuming the development laptop is the training cluster.

---

# 🧪 Testing

The repository uses automated tests for the data pipeline.

The current checkpoint passes:

```text
57 passed
```

Tests cover areas including:

* schema validation
* JSONL ingestion
* Unicode handling
* cleaning
* deduplication
* corpus decisions
* short-artifact detection
* validation behavior

Testing is part of the dataset engineering process, not an afterthought.

---

# 🤖 Model Strategy

The project will **not** immediately attempt to train a massive language model from scratch.

The initial strategy is:

```text
Versioned OromoCorpus
        ↓
Tokenizer research
        ↓
Small proof-of-concept model
        ↓
Validation
        ↓
1B-class experimentation
        ↓
Continued pretraining of an open-weight base
        ↓
Instruction tuning
        ↓
Evaluation
        ↓
Larger models when justified
```

The first model is not expected to be the final model.

It is an engineering and research milestone.

---

# 🧩 LoRA / QLoRA / SFT

Parameter-efficient fine-tuning will be used where appropriate.

### LoRA

Low-Rank Adaptation can train a small set of adapter parameters rather than updating the entire base model.

### QLoRA

QLoRA combines quantization with LoRA to reduce memory requirements during fine-tuning.

### SFT

Supervised Fine-Tuning will be used to produce OromoLM instruction variants that follow Afaan Oromoo instructions and generate useful structured responses.

These techniques become relevant **after** the underlying data and evaluation infrastructure are sufficiently mature.

---

# 📚 OromoCorpus

The project is building toward a broader corpus ecosystem rather than relying permanently on one source.

The active corpus goal is **50 million net unique OromoLM tokens minimum**, with **100 million tokens preferred**. These totals are measured only after cleaning and cross-source deduplication.

Future corpus sources may include appropriately licensed:

* books
* educational materials
* news
* public-domain literature
* government/public documents
* linguistic resources
* conversational datasets
* parallel corpora
* speech transcripts
* community-contributed datasets

Every source should carry provenance and licensing information.

The objective is:

```text
Many sources
    ↓
Common schema
    ↓
Source-specific auditing
    ↓
Quality filtering
    ↓
Deduplication
    ↓
Unified OromoCorpus
```

---

# 📐 OromoBench

A language model cannot be considered successful merely because it produces fluent-looking text.

Oromo AI therefore plans to build **OromoBench**, a dedicated evaluation framework.

Potential evaluation categories include:

### Language

* vocabulary
* spelling
* grammar
* morphology
* sentence completion
* reading comprehension
* paraphrasing
* summarization

### Translation

* Oromo → English
* English → Oromo
* Oromo → Amharic
* Amharic → Oromo
* additional African languages where data permits

### Reasoning

* basic reasoning
* mathematics
* multi-step instructions
* structured extraction

### Cultural and geographic knowledge

* Oromo history
* geography
* culture
* terminology
* regional variation

### Safety

* harmful requests
* misinformation
* privacy
* instruction following
* refusal behavior

Evaluation must distinguish between:

```text
language ability
knowledge
reasoning
instruction following
safety
```

rather than collapsing everything into one number.

---

# 🗣️ Speech

Text is only one part of the Oromo AI ecosystem.

Future speech work will investigate:

```text
Oromo Speech
     │
     ├── ASR
     │     ↓
     │   Oromo Text
     │
     └── TTS
           ↓
       Oromo Speech
```

Potential resources include openly licensed Oromo speech datasets and future community contributions.

Speech development will remain a separate pipeline so that audio licensing, speaker metadata, transcripts, and quality controls are handled correctly.

---

# 🌐 Translation

Translation will eventually become one component of the broader system.

The intended architecture is not simply:

```text
English → Oromo
```

but a multilingual African-language infrastructure capable of supporting:

```text
Oromo ↔ English
Oromo ↔ Amharic
Oromo ↔ other African languages
```

Translation quality will be evaluated separately from general language-model quality.

---

# 🔎 RAG and Knowledge

A language model should not be expected to memorize every piece of Oromo knowledge.

Future RAG infrastructure will allow models to retrieve trusted documents.

```text
User Question
     ↓
Retriever
     ↓
Trusted Oromo Knowledge
     ↓
Context
     ↓
Language Model
     ↓
Answer + Sources
```

This is particularly important for:

* current information
* specialized terminology
* educational material
* historical sources
* reference works

---

# 🛡️ Data Governance

The project follows several principles:

### Provenance

Every dataset should have a documented origin.

### Licensing

Training data should be used according to its license and permissions.

### Reproducibility

Dataset versions should be identifiable and hashable.

### Minimal transformation

Do not destroy linguistic information during preprocessing.

### Auditability

Rejected records should be explainable.

### Separation

Raw data should remain immutable.

Processed data should be generated from documented transformations.

### Human review

Ambiguous cases should remain reviewable rather than being aggressively deleted.

---

# 🔐 Raw Data Policy

Raw source material is treated as immutable input.

The pipeline follows:

```text
RAW
 │
 │ read only
 ▼
AUDIT
 │
 ▼
DECISION
 │
 ├── KEEP
 │
 ├── CLEAN
 │
 └── REJECT
        │
        ▼
     LEDGER
```

The raw source is never rewritten as part of normal processing.

This makes it possible to reproduce or improve a dataset version without losing the original evidence.

---

# 🧱 Engineering Philosophy

The project deliberately favors:

```text
Evidence over assumptions
Reproducibility over convenience
Quality over volume
Provenance over mystery
Conservative filtering over aggressive deletion
Evaluation over hype
Small validated experiments over giant guesses
```

The purpose is to build infrastructure that can survive future model changes.

The corpus should remain useful even if the model architecture changes.

---

# 🗺️ Roadmap

## Phase 1 — Infrastructure

* [x] Repository initialization
* [x] Project documentation
* [x] Python environment
* [x] Data schema
* [x] Data pipeline skeleton
* [x] Automated tests

## Phase 2 — Corpus Engineering

* [x] Acquire first OromoCorpus source
* [x] Preserve raw source
* [x] Establish source hashes
* [x] Implement audit pipeline
* [x] Implement conservative cleaning
* [x] Implement decision engine
* [x] Implement deduplication
* [x] Implement rejection ledger
* [x] Generate production dataset
* [x] Validate v0.1.2
* [ ] Audit and register additional licensed sources
* [ ] Reach OromoCorpus v0.2 at 50M net unique tokens
* [ ] Reach OromoCorpus v0.3 at 100M net unique tokens
* [ ] Publish domain, dialect, license, and source-mixture statistics

## Phase 3 — OromoTokenizer

* [ ] Analyze Oromo tokenization
* [ ] Compare existing tokenizers
* [ ] Measure fertility
* [ ] Evaluate Oromo-specific segmentation
* [ ] Train experimental tokenizer
* [ ] Establish tokenizer evaluation suite

## Phase 4 — OromoLM Experiments

* [ ] Establish tiny model baseline
* [ ] Train proof-of-concept OromoLM checkpoint
* [ ] Evaluate loss/perplexity
* [ ] Test continued pretraining
* [ ] Compare open-weight base models
* [ ] Establish reproducible training configuration

## Phase 5 — OromoLM Instruction Tuning

* [ ] Build OromoLM instruction dataset
* [ ] Build supervised examples
* [ ] SFT baseline
* [ ] LoRA/QLoRA experiments
* [ ] Human evaluation
* [ ] Safety evaluation

## Phase 6 — OromoBench

* [ ] Benchmark specification
* [ ] Dataset construction
* [ ] Evaluation harness
* [ ] Human validation
* [ ] Baseline model evaluation
* [ ] Public benchmark reports

## Phase 7 — Voice

* [ ] ASR data pipeline
* [ ] ASR baseline
* [ ] Oromo TTS baseline
* [ ] Speaker/data governance
* [ ] Voice evaluation

## Phase 8 — Applications

* [ ] Inference server
* [ ] FastAPI
* [ ] RAG
* [ ] Developer API
* [ ] Web applications
* [ ] Mobile integrations

---

# 🚦 What We Are NOT Doing Yet

To keep the project focused, several tempting directions are intentionally deferred.

We are **not** currently:

* building a giant 70B model
* scraping everything available on the internet
* blindly translating massive English datasets into Oromo
* generating huge quantities of synthetic Oromo text
* building a consumer chatbot before the model/data foundation exists
* mixing this project with unrelated application code
* replacing evidence-based corpus filtering with LLM-generated judgments
* treating benchmark scores as proof of general intelligence

The immediate priority remains:

```text
CORPUS → TOKENIZER → MODEL → EVALUATION
```

---

# 🤝 Contributions

The project can eventually benefit from contributors with experience in:

* Afaan Oromoo linguistics
* corpus construction
* NLP
* machine learning
* data engineering
* speech processing
* translation
* evaluation
* software engineering
* Oromo language resources

Especially valuable contributions include:

* high-quality licensed Oromo datasets
* linguistic annotations
* morphology resources
* parallel corpora
* speech data
* benchmark questions
* expert linguistic review

All contributions should preserve clear provenance and licensing.

---

# 📖 Documentation

Important project documentation is maintained under:

```text
docs/
```

Key documents include:

```text
ARCHITECTURE.md
DATA_POLICY.md
DATA_SCHEMA.md
DATA_PIPELINE.md
CORPUS_STATISTICS_REPORT.md
CORPUS_EXPANSION_PLAN.md
```

The documentation is intended to record not only **what** was built, but **why** specific decisions were made.

---

# 🧪 Reproducibility

A dataset version should be reproducible from:

```text
source
+
source hash
+
processing version
+
processing code
+
configuration
+
manifest
```

For v0.1.2, the authoritative source and processed hashes are recorded in the dataset manifest and corpus documentation.

---

# 📌 Current Milestone

### OromoCorpus expansion toward v0.2

The project has completed its first controlled production corpus-processing milestone in `afriberta_oromo_v0.1.2`. The active data milestone is now **OromoCorpus v0.2: at least 50 million net unique OromoLM-tokenizer tokens**, while preserving a preferred path to 100 million tokens in v0.3.

The important achievement is not simply the number of records.

It is that the project now has a repeatable process for:

```text
Acquire
  ↓
Hash
  ↓
Audit
  ↓
Classify
  ↓
Clean
  ↓
Validate
  ↓
Deduplicate
  ↓
Record rejections
  ↓
Generate manifest
  ↓
Verify invariants
```

That infrastructure is the foundation for everything that follows.

The next corpus cycle will use that infrastructure to add multiple licensed sources, run source-specific quality review, remove duplicates across source boundaries, and publish the resulting token and mixture statistics. A tiny CPT pipeline proof may use the validated seed corpus, but meaningful scaled OromoLM training will use the expanded corpus and must not consume OromoBench holdouts.

---

# 🌱 Long-Term Goal

The ultimate goal is an open, reproducible Oromo AI ecosystem in which researchers and developers can build on shared infrastructure rather than repeatedly solving the same foundational problems.

```text
                    OROMO AI
                       │
       ┌───────────────┼───────────────┐
       │               │               │
     DATA             MODELS        EVALUATION
       │               │               │
       ▼               ▼               ▼
 OromoCorpus         OromoLM         OromoBench
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
                  AI SERVICES
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Translate      Voice        RAG
          │            │            │
          └────────────┼────────────┘
                       ▼
                    APPS/API
```

**Oromo AI is being built one validated layer at a time.**

<p align="center">
  <strong>Afaan Oromoo deserves serious AI infrastructure.</strong><br>
  <em>We are building the foundation.</em>
</p>

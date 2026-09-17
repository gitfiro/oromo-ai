<div align="center">

# 🟩 OROMO AI

### Building open AI infrastructure for **Afaan Oromoo**

**Data → Tokenizer → Language Model → Instruction Tuning → Evaluation → Applications**

<br>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Research-EE4C2C?style=for-the-badge\&logo=pytorch\&logoColor=white)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Ecosystem-FFD21E?style=for-the-badge\&logo=huggingface\&logoColor=black)](https://huggingface.co/)
[![Status](https://img.shields.io/badge/Status-Research%20%2F%20Development-8A2BE2?style=for-the-badge)](#-current-status)

<br>

**Open research infrastructure for building high-quality AI and language-model technology for Afaan Oromoo.**

</div>

---

## 🌍 What Is Oromo AI?

**Oromo AI** is an open research and engineering project focused on building the foundations required for high-quality artificial intelligence for **Afaan Oromoo (Oromo)**.

The goal is not simply to wrap an existing model with an Oromo interface.

The goal is to build the underlying language technology pipeline:

```text
                    OROMO AI
                       │
                       ▼
              ┌─────────────────┐
              │  Oromo Corpora  │
              │  & Data Sources │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Corpus Auditing │
              │ & Provenance    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Cleaning &      │
              │ Normalization  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Deduplication & │
              │ Validation      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Training-Ready  │
              │ Oromo Dataset   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Oromo Tokenizer │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Language Model  │
              │ / Continued PT  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Instruction     │
              │ Tuning / SFT    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Evaluation &    │
              │ Benchmarking    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Oromo AI Models │
              │ & Applications  │
              └─────────────────┘
```

The repository is being developed **stage by stage**, with each stage producing measurable artifacts that can be inspected, tested, reproduced, and improved.

---

# 🎯 Vision

Afaan Oromoo deserves modern language technology that understands its:

* vocabulary
* morphology
* orthography
* sentence structure
* dialectal variation
* cultural terminology
* linguistic patterns
* written conventions
* real-world usage

Oromo AI aims to contribute open infrastructure and research toward that goal.

The long-term objective is a complete ecosystem capable of supporting tasks such as:

* 🇪🇹 Afaan Oromoo conversation
* 📚 Oromo knowledge retrieval and comprehension
* ✍️ Oromo writing assistance
* 🔤 spelling and orthography
* 🌐 Oromo ↔ English translation
* 🧠 question answering
* 📝 summarization
* 📖 educational applications
* 🔎 information extraction
* 🗣️ future speech and multimodal research
* 🤖 Oromo-focused AI assistants

The project begins with the part that determines much of the quality of everything downstream:

> **The data.**

---

# 🧭 Current Project Stage

<div align="center">

### `PHASE 1 — CORPUS ENGINEERING`

**RAW DATA → AUDIT → CLEAN → VALIDATE → DATASET v0.1**

</div>

This repository is **not yet a finished Oromo language model**.

The current engineering effort is focused on constructing a reliable and reproducible Oromo corpus pipeline before serious model training begins.

### Current status

| Component                          |     Status     |
| ---------------------------------- | :------------: |
| Python project structure           |  ✅ Implemented |
| Reproducible project configuration |  ✅ Implemented |
| Dataset ingestion infrastructure   |  ✅ Implemented |
| Raw corpus preservation            |  ✅ Implemented |
| Oromo corpus acquisition           |  ✅ Implemented |
| Corpus profiling / auditing        | 🟡 In progress |
| Conservative text cleaning         |  ✅ Implemented |
| Cleaning policy                    |  ✅ Documented  |
| Cleaning tests                     |  ✅ Implemented |
| Deduplication                      | 🟡 In progress |
| Dataset validation                 | 🟡 In progress |
| Dataset v0.1                       | 🟡 In progress |
| Oromo tokenizer                    |    ⬜ Planned   |
| Base language model                |    ⬜ Planned   |
| Continued pretraining              |    ⬜ Planned   |
| SFT / instruction tuning           |    ⬜ Planned   |
| LoRA / QLoRA                       |    ⬜ Planned   |
| Evaluation framework               |    ⬜ Planned   |
| Inference API                      |    ⬜ Planned   |
| Public model release               |    ⬜ Planned   |

### Legend

* ✅ **Implemented**
* 🟡 **In progress**
* ⬜ **Planned / not started**

This status is intentionally conservative. A planned research component is not described as completed until it actually exists in the repository and has been validated.

---

# 🧠 The Core Principle

## Data before model.

A language model cannot compensate indefinitely for poor training data.

Therefore, Oromo AI follows this sequence:

```text
                    ┌──────────────────┐
                    │    RAW CORPORA   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      AUDIT       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     CLEANING     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   VALIDATION     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  DATASET v0.1    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    TOKENIZER     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  LANGUAGE MODEL  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ INSTRUCTION TUNE │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    EVALUATION    │
                    └──────────────────┘
```

Every major transition should have evidence.

---

# 🧱 Engineering Philosophy

Oromo AI is being developed around several principles.

### 1. Preserve the raw source

Raw data should remain immutable.

Processing should create derived datasets rather than silently modifying the original source.

```text
RAW
 ↓
PROCESSED
 ↓
VALIDATED
 ↓
TRAINING
```

This makes experiments reproducible and allows processing decisions to be revisited.

---

### 2. Measure before deciding

Cleaning decisions should be supported by corpus statistics rather than intuition alone.

Examples include:

* document counts
* character counts
* token counts
* language distribution
* duplicate rates
* empty records
* malformed records
* URL density
* boilerplate frequency
* unusual character patterns
* sentence length
* document length
* vocabulary distribution

---

### 3. Clean conservatively

Afaan Oromoo contains linguistic information that aggressive generic text-cleaning systems can accidentally destroy.

Cleaning therefore needs to respect:

* Oromo orthography
* diacritics
* punctuation
* word boundaries
* sentence boundaries
* morphology
* meaningful repetition
* cultural terminology
* linguistic variation

The objective is **quality improvement without unnecessary information loss**.

---

### 4. Separate research stages

The project should not collapse every task into one script.

The system is intentionally divided into stages:

```text
Acquisition
     ↓
Schema
     ↓
Audit
     ↓
Cleaning
     ↓
Deduplication
     ↓
Validation
     ↓
Dataset Version
     ↓
Tokenizer
     ↓
Training
     ↓
Evaluation
```

This allows individual components to be tested independently.

---

### 5. Reproducibility matters

A dataset should not depend on an undocumented manual process.

Where possible, processing should be:

* deterministic
* versioned
* documented
* testable
* inspectable

---

# 📚 Corpus Engineering

The current repository is primarily a **corpus-engineering project**.

The first major objective is to construct a validated Oromo dataset suitable for downstream NLP and language-model research.

The corpus pipeline includes:

```text
SOURCE DISCOVERY
       ↓
SOURCE ACQUISITION
       ↓
PROVENANCE
       ↓
CANONICAL SCHEMA
       ↓
QUALITY AUDIT
       ↓
CONSERVATIVE CLEANING
       ↓
DEDUPLICATION
       ↓
VALIDATION
       ↓
DATASET MANIFEST
       ↓
DATASET v0.1
```

### Important distinction

The project does not assume that every available Oromo text belongs in the final training corpus.

Each source should be evaluated for:

* relevance
* quality
* duplication
* licensing
* provenance
* linguistic value
* formatting
* contamination
* boilerplate
* noise

---

# 🧪 Current Corpus Work

Current repository work includes infrastructure for:

* Oromo corpus ingestion
* raw-source preservation
* canonical data representation
* corpus profiling
* conservative cleaning
* cleaning validation
* automated testing
* dataset processing

The project's cleaning decisions are documented in:

* `docs/CLEANING_POLICY.md`
* `docs/CORPUS_QUALITY_REPORT.md`

These documents are intended to evolve as the corpus is measured and new evidence becomes available.

---

# 🧹 Cleaning Philosophy

Generic web-data cleaning can be dangerous for low-resource languages.

A cleaner designed for English-centric web corpora can remove or distort valuable Oromo information.

Oromo AI therefore favors:

```text
             REMOVE NOISE
                  │
                  ▼
       WITHOUT DESTROYING SIGNAL
```

The cleaner should avoid unnecessarily removing:

* Oromo diacritics
* meaningful punctuation
* linguistic markers
* legitimate short texts
* culturally meaningful terminology
* valid repeated structures
* sentence-level context

At the same time, obvious technical and web noise can be removed where justified.

Examples include:

* malformed records
* empty records
* obvious CMS boilerplate
* unusable markup
* technical artifacts
* clearly invalid text

The exact policy is maintained in the project's documentation rather than hard-coded as an undocumented assumption.

---

# 🗂️ Repository Structure

The repository is organized to separate research infrastructure from generated data and experiments.

```text
oromo-ai/
│
├── src/
│   └── oromo_ai/
│       └── data/
│           ├── ingestion/
│           ├── cleaning/
│           ├── ...
│           └── ...
│
├── tests/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CLEANING_POLICY.md
│   ├── CONTENT_INVENTORY.md
│   ├── CORPUS_QUALITY_REPORT.md
│   ├── DATA_PIPELINE.md
│   ├── DATA_POLICY.md
│   ├── DATA_SCHEMA.md
│   ├── EVALUATION.md
│   ├── MODEL_POLICY.md
│   ├── PROJECT_CHARTER.md
│   └── ROADMAP.md
│
├── pyproject.toml
├── README.md
└── ...
```

Some documentation files are intentionally being developed alongside the corresponding engineering phases.

The documentation should reflect the actual state of the repository rather than describe unfinished systems as complete.

---

# 🔬 Research Roadmap

## Phase 1 — Corpus Foundation

**Current phase**

```text
Source discovery
      ↓
Ingestion
      ↓
Raw preservation
      ↓
Schema
      ↓
Corpus audit
      ↓
Cleaning
      ↓
Deduplication
      ↓
Validation
      ↓
Dataset v0.1
```

### Objective

Produce a documented, reproducible and validated Oromo training corpus.

---

## Phase 2 — Tokenizer

Once the corpus is sufficiently validated, tokenizer research begins.

The tokenizer will be evaluated against Oromo-specific characteristics.

Important measurements include:

* vocabulary coverage
* token fertility
* sequence expansion
* word fragmentation
* morphology
* character coverage
* punctuation behavior
* orthographic patterns
* efficiency

The project should not assume that a custom tokenizer is automatically necessary.

Existing tokenizers should be evaluated first.

A specialized tokenizer should be introduced only if the measurements justify it.

---

## Phase 3 — Base Language Model

After the dataset and tokenizer foundations are sufficiently mature:

```text
TOKENIZER
    ↓
MODEL CONFIGURATION
    ↓
ARCHITECTURE
    ↓
TRAINING DATA
    ↓
CAUSAL LANGUAGE MODEL
    ↓
CHECKPOINTS
```

Research will include decisions around:

* model architecture
* parameter scale
* context length
* tokenizer integration
* training configuration
* hardware requirements
* checkpointing
* optimization
* reproducibility
* compute efficiency

---

## Phase 4 — Oromo Adaptation

A major research direction is adapting existing capable language models to Afaan Oromoo through continued pretraining or related language-adaptation techniques.

This phase may include comparisons between:

* training from scratch
* continued pretraining
* multilingual adaptation
* Oromo-focused adaptation
* parameter-efficient approaches

The decision should be based on measured results and available compute rather than assumptions.

---

## Phase 5 — Instruction Tuning

A language model that predicts text is not automatically a useful assistant.

Instruction tuning will eventually target tasks such as:

```text
Question Answering
Translation
Summarization
Explanation
Writing
Conversation
Educational Assistance
Linguistic Tasks
Knowledge Tasks
```

Potential methods include:

* supervised fine-tuning
* LoRA
* QLoRA
* other parameter-efficient fine-tuning methods

These are future stages, not current project accomplishments.

---

# 📊 Phase 6 — Evaluation

Evaluation is a core part of the project.

The objective is not simply:

> “Does the model produce Oromo text?”

The stronger question is:

> **How well does the system actually understand and generate Afaan Oromoo?**

Future evaluation may cover:

### Language modeling

* perplexity
* held-out loss
* token efficiency

### Linguistic quality

* spelling
* orthography
* morphology
* grammar
* lexical coverage
* sentence structure

### Language understanding

* comprehension
* question answering
* classification
* information extraction

### Generation

* coherence
* relevance
* fluency
* factuality
* instruction following

### Translation

* Oromo ↔ English
* additional language pairs where justified

### Robustness

* noisy input
* spelling variation
* dialectal variation
* long-context behavior
* unfamiliar terminology

Evaluation benchmarks will be developed and documented before final model claims are made.

---

# 🤖 What Does “Complete Oromo AI” Mean?

The long-term project is broader than a single checkpoint.

A complete Oromo AI stack can be thought of as:

```text
┌──────────────────────────────┐
│       OROMO APPLICATIONS     │
├──────────────────────────────┤
│      AI ASSISTANTS / APIs    │
├──────────────────────────────┤
│     INSTRUCTION-TUNED MODEL  │
├──────────────────────────────┤
│       LANGUAGE MODEL         │
├──────────────────────────────┤
│          TOKENIZER           │
├──────────────────────────────┤
│     VALIDATED CORPUS         │
├──────────────────────────────┤
│   DATA QUALITY INFRASTRUCTURE│
├──────────────────────────────┤
│        RAW DATA SOURCES      │
└──────────────────────────────┘
```

The project is therefore building **infrastructure**, not only a model.

---

# 🧩 Technology Stack

The repository currently uses a Python-based machine-learning and data-processing stack.

Core technologies include:

* **Python 3.12**
* **PyTorch**
* **Hugging Face Transformers**
* **Hugging Face Datasets**
* **Tokenizers**
* **TRL**
* **PEFT**
* **Accelerate**
* **Pandas**
* **PyArrow**
* **DuckDB**
* **tqdm**
* **regex**
* **ftfy**

The stack will evolve as the project progresses.

---

# 💻 Development Environment

The project is designed to be developed in a modern Python environment, including WSL/Linux development environments.

### Requirements

* Python `3.12`
* Git
* sufficient disk space for corpus/model artifacts
* additional GPU/compute resources as model training begins

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/gitfiro/oromo-ai.git
cd oromo-ai
```

Create a Python virtual environment:

```bash
python3.12 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project:

```bash
pip install -e .
```

For development/testing:

```bash
pip install pytest
```

---

# 🧪 Running Tests

Run the test suite:

```bash
pytest
```

Tests should pass before major pipeline changes are considered complete.

The project favors small, testable components rather than large scripts that combine acquisition, cleaning, training and evaluation into one process.

---

# 🔄 Development Workflow

The intended development cycle is:

```text
        INSPECT
           ↓
       DOCUMENT
           ↓
      IMPLEMENT
           ↓
         TEST
           ↓
        MEASURE
           ↓
        REVIEW
           ↓
        VERSION
```

Before changing a major component:

1. Inspect the current implementation.
2. Read the relevant documentation.
3. Determine what is actually implemented.
4. Make the smallest appropriate change.
5. Run tests.
6. Measure the result.
7. Update documentation.
8. Review for regressions.
9. Commit the change.

---

# 📖 Documentation

The `docs/` directory is intended to contain the project's technical record.

| Document                   | Purpose                                 |
| -------------------------- | --------------------------------------- |
| `PROJECT_CHARTER.md`       | Project mission, scope and boundaries   |
| `ROADMAP.md`               | Phase-by-phase development plan         |
| `ARCHITECTURE.md`          | System architecture                     |
| `DATA_PIPELINE.md`         | Dataset processing pipeline             |
| `DATA_SCHEMA.md`           | Canonical data representation           |
| `DATA_POLICY.md`           | Data governance and handling principles |
| `CLEANING_POLICY.md`       | Text-cleaning rules                     |
| `CORPUS_QUALITY_REPORT.md` | Corpus measurements and findings        |
| `MODEL_POLICY.md`          | Model-development principles            |
| `EVALUATION.md`            | Evaluation methodology                  |

Documentation is part of the engineering process, not an afterthought.

---

# 🔐 Data Provenance & Licensing

Data quality is not only about linguistic quality.

It is also about knowing:

> **Where did this text come from, and are we permitted to use it?**

For each corpus source, the project should preserve relevant provenance information whenever available, including:

* source
* collection method
* source URL or identifier
* acquisition date
* license
* processing version
* transformation history
* dataset inclusion/exclusion decision

The final licensing policy for datasets, trained models and code will be documented as the project's release strategy is finalized.

No license should be assumed merely because data is publicly accessible.

---

# 🛡️ Data Safety & Integrity

The repository follows several important data-integrity rules.

### Raw data should not be silently overwritten.

### Processing should produce derived artifacts.

### Every major transformation should be reproducible.

### Dataset versions should be identifiable.

### Training data should be auditable.

### Licensing should be considered before redistribution.

These principles become increasingly important as the corpus grows.

---

# 🔮 Future Research

Oromo AI may eventually expand into additional areas such as:

* multilingual Oromo models
* Oromo speech recognition
* Oromo text-to-speech
* OCR for Oromo documents
* document understanding
* retrieval-augmented generation
* Oromo embeddings
* semantic search
* information retrieval
* educational AI
* translation systems
* linguistic analysis
* morphology-aware NLP
* dialect-aware modeling
* multimodal Oromo AI

These are research directions rather than current implementation claims.

---

# 🧪 Research Standards

The project aims to distinguish clearly between:

```text
HYPOTHESIS
    ↓
IMPLEMENTATION
    ↓
EXPERIMENT
    ↓
MEASUREMENT
    ↓
RESULT
    ↓
CONCLUSION
```

A promising idea is not the same thing as a validated result.

Likewise:

* a downloaded dataset is not a training dataset
* a tokenizer is not a language model
* a language model is not an assistant
* an instruction-tuned model is not automatically a reliable system
* a benchmark score is not a complete evaluation

The repository should preserve these distinctions.

---

# 🏗️ Project Status Philosophy

This project intentionally avoids pretending that unfinished work is finished.

For example:

```text
"Tokenizer dependencies installed"
                ≠
"Tokenizer completed"

"Corpus downloaded"
                ≠
"Training corpus validated"

"Model architecture selected"
                ≠
"Model trained"

"Fine-tuning code exists"
                ≠
"Instruction model validated"

"Model generates Oromo"
                ≠
"Model understands Oromo reliably"
```

This distinction is essential for meaningful research.

---

# 🤝 Contributing

Contributions are welcome as the project develops.

Useful contributions may include:

* Oromo corpus discovery
* dataset quality analysis
* linguistic research
* tokenizer research
* NLP engineering
* evaluation design
* documentation
* testing
* Oromo language expertise
* computational linguistics
* machine-learning engineering

Contributions involving data should include provenance and licensing information whenever possible.

---

# 🗺️ Long-Term Roadmap

```text
                    OROMO AI
                       │
                       ▼
             ┌──────────────────┐
             │  1. DATA         │
             │  FOUNDATION      │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │  2. TOKENIZER    │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │  3. BASE MODEL   │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │  4. OROMO        │
             │  ADAPTATION      │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │  5. INSTRUCTION  │
             │  TUNING          │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │  6. EVALUATION   │
             │  & RELEASE       │
             └──────────────────┘
```

The project moves forward only when the evidence from one stage supports the next.

---

# 📌 Current Milestone

### Dataset v0.1

The immediate objective is:

> **Build a validated, reproducible Oromo corpus that can serve as a trustworthy foundation for tokenizer and model research.**

Before moving into serious model training, the corpus needs to be sufficiently understood in terms of:

* size
* quality
* duplication
* linguistic distribution
* noise
* provenance
* licensing
* preprocessing effects

Only then should the project proceed confidently toward tokenizer and model development.

---

# 🌱 Why This Matters

Low-resource language technology often faces a fundamental problem:

**There is not enough high-quality language data, infrastructure, evaluation and research.**

Oromo AI is intended to help address that infrastructure gap.

The project is being built so that future researchers and developers can inspect the pipeline rather than simply receiving an unexplained model checkpoint.

The objective is not only to produce a model.

It is to build the **engineering and research foundation needed to produce better Oromo models repeatedly.**

---

<div align="center">

## 🟩 Afaan Oromoo

### **Data first. Research carefully. Build openly.**

<br>

**Build the data.**

**Validate the data.**

**Build the tokenizer.**

**Train carefully.**

**Evaluate honestly.**

**Then release.**

<br>

---

### Oromo AI

*Open research infrastructure for Afaan Oromoo AI.*

</div>

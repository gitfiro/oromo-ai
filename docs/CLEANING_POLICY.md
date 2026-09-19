# 🧹 Oromo AI — Corpus Cleaning Policy

> **Purpose:** Define a conservative, reproducible, and provenance-preserving policy for transforming raw Afaan Oromoo corpora into high-quality training data.

<div align="center">

### 🛡️ Data Integrity First

**Conservative · Deterministic · Reproducible · Testable · Non-Destructive**

</div>

---

## 📋 Document Status

| Property                 | Value                                               |
| ------------------------ | --------------------------------------------------- |
| **Document**             | Corpus Cleaning Policy                              |
| **Project**              | Oromo AI                                            |
| **Policy Version**       | `0.1.0`                                             |
| **Current Status**       | 🟡 Policy Defined — Implementation Not Yet Approved |
| **Raw Data**             | 🔒 Immutable                                        |
| **Aggressive Filtering** | ❌ Not permitted                                     |
| **Semantic Rewriting**   | ❌ Not permitted                                     |
| **Machine Translation**  | ❌ Not permitted                                     |
| **AI Rewriting**         | ❌ Not permitted                                     |

> **Core rule:** **Measure first. Transform second. Train third.**

---

# 1. 🎯 Purpose

This document defines the rules for transforming raw **Afaan Oromoo** text corpora into training-ready text while preserving:

* linguistic information
* cultural information
* historical information
* dialectal variation
* orthographic variation
* legitimate stylistic variation
* domain-specific terminology

The cleaning pipeline must be:

* **Conservative**
* **Deterministic**
* **Reproducible**
* **Testable**
* **Provenance-preserving**
* **Non-destructive**

Raw source data must **never be modified in place**.

---

# 2. 🧠 Core Principle

The objective of corpus cleaning is to remove **demonstrable data-extraction noise** without removing legitimate Afaan Oromoo content.

Cleaning must **not** be based on assumptions such as:

* Political content is low quality.
* Religious content is low quality.
* Dialectal variation is incorrect.
* Unusual spelling is automatically an error.
* Foreign names indicate contamination.
* English words indicate contamination.
* Web-originated text is automatically unusable.

### Preservation Principle

> **If there is no strong evidence that something is corrupted or is extraction noise, preserve it.**

The system must preserve legitimate linguistic variation.

---

# 3. 🔄 Data Lifecycle

Raw data follows a controlled processing lifecycle:

```text
┌──────────────┐
│     RAW      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PROFILING   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   CLEANING   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ NORMALIZATION│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│DEDUPLICATION │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  VALIDATION  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ PROCESSED DATASET│
└──────────────────┘
```

Each stage must produce reproducible outputs and metadata.

**Raw data is immutable.**

---

# 4. 🔒 Raw Data Protection

The following directory is considered **raw-source storage**:

```text
data/raw/
```

The cleaning pipeline must **never**:

* overwrite raw files
* rename raw source files destructively
* rewrite raw archives
* modify the held-out evaluation corpus
* silently discard records

All transformations must write to:

```text
data/processed/
```

Diagnostic reports must be written to:

```text
data/manifests/
```

### Data Safety Rule

```text
data/raw/
    ↓
    READ ONLY
    ↓
processing pipeline
    ↓
data/processed/
    +
data/manifests/
```

---

# 5. 🧹 Cleaning Categories

Cleaning rules are divided into three categories.

## 🟢 Category A — Safe Removal

These are artifacts that are clearly non-linguistic extraction noise.

Examples:

* standalone `Read More` navigation markers
* WordPress embed markers
* obvious HTML tags
* obvious navigation boilerplate
* obvious duplicated page metadata
* malformed extraction wrappers

These may be removed automatically.

---

## 🟡 Category B — Conditional Removal

These require contextual analysis.

Examples:

* URLs
* email addresses
* social-media handles
* repeated website navigation
* publication metadata
* boilerplate phrases
* extremely repetitive records

These must only be removed when the pattern is clearly metadata or extraction noise.

### Important

A URL inside otherwise legitimate text must **not** automatically cause the entire record to be deleted.

Example:

```text
Odeeffannoo dabalataa https://example.com irraa argachuu dandeessu.
```

Expected behavior:

```text
Odeeffannoo dabalataa irraa argachuu dandeessu.
```

The linguistic content must remain.

---

## 🔵 Category C — Preserve

The following must be preserved unless there is independent evidence that they are corrupted:

* Oromo vocabulary
* Oromo grammar
* Qubee orthography
* Oromo-specific letters
* long vowels
* apostrophe-like characters
* proper names
* place names
* historical references
* political content
* religious content
* cultural content
* dialectal variation
* quoted material
* foreign names
* technical terminology
* legitimate English words occurring inside Oromo text
* code-switching
* punctuation
* sentence structure

---

# 6. 🌐 Web Artifact Cleaning

## 6.1 Read More

Remove standalone extraction markers such as:

```text
Read More
[Read More]
ReadMore
```

### Rule

Only the artifact itself should be removed.

Nearby legitimate text must be preserved.

---

## 6.2 Embed Markers

Remove obvious CMS embed markers such as:

```text
[embed]
[embedyt]
[/embed]
```

When an embed marker contains a URL, remove the embedding wrapper while retaining surrounding linguistic content.

---

## 6.3 HTML

Remove actual HTML markup such as:

```html
<p>
</p>
<br>
<div>
</div>
```

Do **not** remove ordinary Oromo text merely because angle brackets occur.

---

## 6.4 WordPress / CMS Boilerplate

Remove clearly identifiable boilerplate such as:

```text
Comments Off
```

Equivalent page-navigation metadata may also be removed when it is clearly not part of the linguistic content.

---

## 6.5 URLs

URLs should normally be removed from training text when they are clearly web metadata.

Examples:

```text
https://example.com
http://example.org/article
```

However:

> **The existence of a URL must never cause deletion of the entire record.**

The linguistic portion should remain after URL removal.

---

# 7. 📏 Whitespace Normalization

Normalize:

* repeated spaces
* repeated tabs
* excessive blank lines
* leading whitespace
* trailing whitespace

Collapse runs of whitespace to a single space where doing so does not destroy meaningful structure.

### Must Preserve

* punctuation
* meaningful sentence boundaries
* linguistic content

---

# 8. 🔤 Unicode Normalization

Apply **Unicode NFC normalization**.

NFC is preferred because it canonicalizes equivalent Unicode representations without aggressively changing visible linguistic characters.

### ❌ Prohibited Transformations

Do **not**:

* ASCII-fold Oromo text
* remove diacritics
* replace Oromo characters with English approximations
* convert all apostrophes to ASCII `'`
* lowercase all text
* uppercase all text

### Rule

> Unicode normalization must normalize representation, not rewrite language.

---

# 9. 🟩 Oromo Orthography Preservation

The cleaner must preserve Oromo orthographic distinctions.

Particular care is required for:

```text
Q/q
X/x
C/c
G/g
dh
ny
ph
long vowels
apostrophe-like characters
```

The cleaner must never use a generic English-language normalizer that could destroy Afaan Oromoo orthography.

---

# 10. `'` Apostrophe Policy

The corpus may contain multiple apostrophe-like characters:

```text
'
’
ʼ
```

These must **not** automatically be converted into one character.

Different apostrophe-like characters may originate from:

* Oromo orthography
* punctuation
* typography
* source formatting

Their linguistic role must be analyzed before any future normalization.

### Initial Policy

```text
preserve apostrophe-like characters
```

---

# 11. 🇬🇧 English-Language Content

English words must **not** be removed solely because they are English.

English may occur because of:

* proper names
* quotations
* titles
* technical terminology
* bilingual passages
* code-switching
* URLs
* metadata

Language identification may be used for diagnostics, but it must not automatically delete records from the Oromo corpus.

> **Language identification is diagnostic—not an automatic deletion mechanism.**

---

# 12. 🗑️ Record-Level Filtering

A record may be rejected only when there is strong evidence that it is not useful training text.

Potential rejection conditions include:

* empty text after cleaning
* text consisting almost entirely of extraction artifacts
* obviously corrupted encoding
* extreme repeated-character corruption
* duplicated content after normalization
* records containing no meaningful linguistic content

Every rejection must have a machine-readable reason.

### Example

```text
rejected_reason = "empty_after_cleaning"
```

or:

```text
rejected_reason = "extraction_artifact_only"
```

### Rejection Rule

> **Every rejected record must be explainable.**

Silent deletion is prohibited.

---

# 13. 📐 Length Policy

Length thresholds must be conservative.

Do **not**:

* remove short records merely because they are short
* remove long records merely because they are long

Initial filtering should focus on:

* empty records
* artifact-only records
* obvious corruption
* pathological repetition

Length statistics must be reported **before** deciding on hard limits.

---

# 14. 🔁 Repetition Detection

The pipeline should identify pathological repetition such as:

```text
ha ha ha ha ha ha ha ha ha ha ha ha
```

or repeated blocks caused by extraction errors.

However, normal repetition in legitimate language must be preserved.

### Detection Philosophy

Repetition detection should be based on:

* measurable thresholds
* structural analysis
* diagnostics

It must **not** rely on simplistic duplicate-word rules.

---

# 15. #️⃣ Deduplication

Deduplication occurs **after cleaning and normalization**.

The initial deduplication strategy is:

> **Exact normalized-text hashing**

### Hash Normalization

The normalization sequence is:

```text
1. Unicode NFC
2. Collapse whitespace
3. Strip leading/trailing whitespace
4. Generate hash
```

### Explicitly Prohibited

Do **not**:

* lowercase text for hashing
* remove punctuation for hashing
* aggressively normalize spelling for hashing

### Future Work

Near-duplicate detection may be added later, but it must be evaluated separately.

Potential future methods include:

* MinHash
* SimHash
* n-gram fingerprints
* locality-sensitive hashing

---

# 16. 🧪 Evaluation Set Protection

The evaluation corpus is **held out**.

It must **not** be:

* cleaned using rules developed from the evaluation set
* used to tune cleaning thresholds
* deduplicated against training data
* used for model training
* used to make training-data filtering decisions

The evaluation set may be inspected diagnostically, but its original content must remain immutable.

### Separation Principle

```text
TRAINING CORPUS
      │
      ├── profiling
      ├── cleaning
      ├── normalization
      └── deduplication

EVALUATION CORPUS
      │
      └── HELD OUT
```

This protects evaluation integrity and reduces the risk of data leakage.

---

# 17. 🔗 Provenance

Every processed dataset must retain provenance information.

At minimum:

| Provenance Field                  | Required |
| --------------------------------- | :------: |
| Source dataset                    |     ✅    |
| Source record ID                  |     ✅    |
| Source URL, when available        |     ✅    |
| License                           |     ✅    |
| Processing version                |     ✅    |
| Cleaning version                  |     ✅    |
| Transformation timestamp          |     ✅    |
| Rejection reason, when applicable |     ✅    |

A processed record must remain traceable to its source.

> **No orphaned processed data.**

---

# 18. 📊 Auditability

Every cleaning run must produce:

1. Processed dataset
2. Processing manifest
3. Cleaning statistics
4. Rejected-record statistics
5. Duplicate statistics
6. Pipeline version
7. Configuration used

### Required Statistics

```text
input_records
output_records
rejected_records
duplicates_removed
urls_removed
html_markers_removed
read_more_markers_removed
embed_markers_removed
```

Additional diagnostic statistics may be added without changing the core policy.

---

# 19. 🎯 Determinism

Given:

* identical input
* identical cleaning configuration
* identical pipeline version

the cleaner must produce **identical output**.

### Prohibited

Random transformations are prohibited.

If sampling is introduced for diagnostics, the random seed must be explicit.

Example:

```text
random_seed = 42
```

Determinism is required for reproducibility and regression testing.

---

# 20. 🏷️ Versioning

Cleaning rules are versioned independently from the dataset.

Example:

```text
cleaning_version = 0.1.0
```

A change to cleaning behavior requires a version change.

The pipeline must never silently reinterpret an older processed dataset under newer cleaning rules.

### Versioning Model

```text
Dataset Version
       +
Cleaning Version
       +
Pipeline Version
       ↓
Reproducible Processing State
```

---

# 21. 🧪 Testing Requirements

Every cleaning rule must have tests covering three classes.

## ✅ Positive Cases

Text that **should be cleaned**.

Example:

```text
Oromo text [Read More]
```

Expected:

```text
Oromo text
```

---

## ❌ Negative Cases

Text that **must not be altered**.

Example:

```text
Legitimate Afaan Oromoo content
```

Expected:

```text
Legitimate Afaan Oromoo content
```

---

## 🔀 Mixed Cases

Text containing both removable artifacts and legitimate Oromo content.

Example:

```text
Legitimate Oromo sentence + URL
```

Expected:

```text
Legitimate Oromo sentence
```

### Raw Data Requirement

The original raw text must remain unchanged.

---

# 22. 🚀 Initial Cleaning Scope — v0.1.0

Version `0.1.0` will implement **only conservative transformations**.

### Approved Operations

|  # | Operation                                   | Status |
| -: | ------------------------------------------- | :----: |
|  1 | Unicode NFC normalization                   |    ✅   |
|  2 | Whitespace normalization                    |    ✅   |
|  3 | Remove obvious `Read More` markers          |    ✅   |
|  4 | Remove obvious embed markers                |    ✅   |
|  5 | Remove HTML markup                          |    ✅   |
|  6 | Remove clearly identifiable CMS boilerplate |    ✅   |
|  7 | Remove URLs                                 |    ✅   |
|  8 | Empty-record detection                      |    ✅   |
|  9 | Basic pathological-repetition diagnostics   |    ✅   |
| 10 | Exact normalized-text deduplication         |    ✅   |

### Explicitly Out of Scope

The following are **not** part of v0.1.0:

```text
❌ Aggressive language filtering
❌ Semantic rewriting
❌ AI-generated rewriting
❌ Machine translation
❌ Automatic spelling correction
❌ Dialect normalization
❌ Forced apostrophe normalization
❌ English-content deletion
❌ Political-content filtering
❌ Religious-content filtering
❌ Cultural-content filtering
```

> **Version 0.1.0 cleans extraction noise. It does not rewrite Afaan Oromoo.**

---

# 23. 🔮 Future Cleaning

Future versions may introduce:

* language identification
* document-level quality scoring
* near-duplicate detection
* source-specific boilerplate detection
* sentence segmentation
* paragraph reconstruction
* OCR error detection
* dialect metadata
* contamination detection
* PII detection
* multilingual contamination analysis

Each future feature must be evaluated independently before becoming part of the production pipeline.

### Future Feature Rule

```text
PROPOSE
   ↓
IMPLEMENT
   ↓
TEST
   ↓
MEASURE
   ↓
AUDIT
   ↓
APPROVE
   ↓
VERSION
```

No future cleaning capability becomes part of the production pipeline merely because it appears technically useful.

---

# 24. 🏁 Approval Status

<div align="center">

## 🟡 POLICY DEFINED

### IMPLEMENTATION NOT YET APPROVED

</div>

The raw AfriBERTa Afaan Oromoo corpus remains **untouched**.

No processed training corpus should be generated until the cleaning implementation passes its:

* unit tests
* regression tests
* mixed-case tests
* preservation tests
* determinism tests
* provenance checks
* output-integrity checks

---

# 🔐 Final Data Integrity Principles

The Oromo AI corpus pipeline follows these rules:

```text
RAW DATA IS IMMUTABLE
        │
        ▼
MEASURE BEFORE MODIFYING
        │
        ▼
REMOVE NOISE — NOT LANGUAGE
        │
        ▼
PRESERVE ORTHOGRAPHY
        │
        ▼
PRESERVE LEGITIMATE VARIATION
        │
        ▼
TRACE EVERY TRANSFORMATION
        │
        ▼
TEST EVERY RULE
        │
        ▼
VERSION EVERY BEHAVIOR CHANGE
        │
        ▼
VALIDATE BEFORE TRAINING
```

### The governing principle

> **Clean the corpus without rewriting the language.**

The purpose of the pipeline is to produce a cleaner representation of the source data—not to impose an artificial version of Afaan Oromoo on the training corpus.

---

<div align="center">

**Oromo AI**

**Afaan Oromoo → Data → Models → Intelligence**

`Measure First · Transform Second · Train Third`

</div>

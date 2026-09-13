# Oromo AI Corpus Cleaning Policy

## 1. Purpose

This document defines the rules for transforming raw Afaan Oromoo text
corpora into training-ready text while preserving linguistic, cultural,
historical, dialectal, and stylistic information.

The cleaning pipeline must be:

- conservative
- deterministic
- reproducible
- testable
- provenance-preserving
- non-destructive

Raw source data must never be modified in place.

---

## 2. Core Principle

The objective is to remove demonstrable data-extraction noise without
removing legitimate Afaan Oromoo content.

Cleaning must NOT be based on assumptions such as:

- political content is low quality
- religious content is low quality
- dialectal variation is incorrect
- unusual spelling is automatically an error
- foreign names indicate contamination
- English words indicate contamination
- web-originated text is automatically unusable

The system must preserve legitimate linguistic variation.

---

## 3. Data Lifecycle

Raw data follows this lifecycle:

    RAW
      |
      v
    PROFILING
      |
      v
    CLEANING
      |
      v
    NORMALIZATION
      |
      v
    DEDUPLICATION
      |
      v
    VALIDATION
      |
      v
    PROCESSED DATASET

Each stage must produce reproducible outputs and metadata.

Raw data is immutable.

---

## 4. Raw Data Protection

The following directories are considered raw-source storage:

    data/raw/

The cleaning pipeline must never:

- overwrite raw files
- rename raw source files destructively
- rewrite raw archives
- modify the held-out evaluation corpus
- silently discard records

All transformations must write to:

    data/processed/

Diagnostic reports must be written to:

    data/manifests/

---

## 5. Cleaning Categories

Cleaning rules are divided into three categories.

### Category A — Safe Removal

These are artifacts that are clearly non-linguistic extraction noise.

Examples:

- standalone "Read More" navigation markers
- WordPress embed markers
- obvious HTML tags
- obvious navigation boilerplate
- obvious duplicated page metadata
- malformed extraction wrappers

These may be removed automatically.

### Category B — Conditional Removal

These require contextual analysis.

Examples:

- URLs
- email addresses
- social-media handles
- repeated website navigation
- publication metadata
- boilerplate phrases
- extremely repetitive records

These must only be removed when the pattern is clearly metadata or
extraction noise.

A URL inside otherwise legitimate text must not automatically cause the
entire record to be deleted.

### Category C — Preserve

The following must be preserved unless there is independent evidence that
they are corrupted:

- Oromo vocabulary
- Oromo grammar
- Qubee orthography
- Oromo-specific letters
- long vowels
- apostrophe-like characters
- proper names
- place names
- historical references
- political content
- religious content
- cultural content
- dialectal variation
- quoted material
- foreign names
- technical terminology
- legitimate English words occurring inside Oromo text
- code-switching
- punctuation
- sentence structure

---

## 6. Web Artifact Cleaning

### 6.1 Read More

Remove standalone extraction markers such as:

    Read More
    [Read More]
    ReadMore

Only the artifact itself should be removed.

Nearby legitimate text must be preserved.

### 6.2 Embed Markers

Remove obvious CMS embed markers such as:

    [embed]
    [embedyt]
    [/embed]

When an embed marker contains a URL, remove the embedding wrapper and
retain surrounding linguistic content.

### 6.3 HTML

Remove actual HTML markup such as:

    <p>
    </p>
    <br>
    <div>
    </div>

Do not remove ordinary Oromo text merely because angle brackets occur.

### 6.4 WordPress / CMS Boilerplate

Remove clearly identifiable boilerplate such as:

    Comments Off

and equivalent page-navigation metadata when it is not part of the
linguistic content.

### 6.5 URLs

URLs should normally be removed from training text when they are clearly
web metadata.

Examples:

    https://example.com
    http://example.org/article

However, the existence of a URL must not cause deletion of the entire
record.

Example:

    Odeeffannoo dabalataa https://example.com irraa argachuu dandeessu.

The linguistic portion should remain after URL removal.

---

## 7. Whitespace Normalization

Normalize:

- repeated spaces
- repeated tabs
- excessive blank lines
- leading whitespace
- trailing whitespace

Collapse runs of whitespace to a single space where doing so does not
destroy meaningful structure.

Do not remove punctuation.

---

## 8. Unicode Normalization

Apply Unicode NFC normalization.

NFC is preferred because it canonicalizes equivalent Unicode representations
without aggressively changing visible linguistic characters.

Do NOT:

- ASCII-fold Oromo text
- remove diacritics
- replace Oromo characters with English approximations
- convert all apostrophes to ASCII `'`
- lowercase all text
- uppercase all text

---

## 9. Oromo Orthography Preservation

The cleaner must preserve Oromo orthographic distinctions.

Particular care is required for:

- Q/q
- X/x
- C/c
- G/g
- dh
- ny
- ph
- long vowels
- apostrophe-like characters

The cleaner must never use a generic English-language normalizer that could
destroy Oromo orthography.

---

## 10. Apostrophe Policy

The following characters may occur in the corpus:

    '
    ’
    ʼ

They must NOT automatically be converted to one character.

Different apostrophe-like characters may originate from:

- Oromo orthography
- punctuation
- typography
- source formatting

Their linguistic role must be analyzed before any future normalization.

For the initial cleaning pipeline:

    preserve apostrophe-like characters

---

## 11. English-Language Content

English words must not be removed solely because they are English.

English may occur because of:

- proper names
- quotations
- titles
- technical terminology
- bilingual passages
- code-switching
- URLs or metadata

Language identification may be used for diagnostics, but it must not
automatically delete records from the Oromo corpus.

---

## 12. Record-Level Filtering

A record may be rejected only when there is strong evidence that it is
not useful training text.

Potential rejection conditions include:

- empty text after cleaning
- text consisting almost entirely of extraction artifacts
- obviously corrupted encoding
- extreme repeated-character corruption
- duplicated content after normalization
- records containing no meaningful linguistic content

Every rejection must have a machine-readable reason.

Example:

    rejected_reason = "empty_after_cleaning"

or:

    rejected_reason = "extraction_artifact_only"

---

## 13. Length Policy

Length thresholds must be conservative.

Do not remove short records merely because they are short.

Do not remove long records merely because they are long.

Initial filtering should focus on:

- empty records
- artifact-only records
- obvious corruption
- pathological repetition

Length statistics should be reported before deciding on hard limits.

---

## 14. Repetition Detection

The pipeline should identify pathological repetition such as:

    ha ha ha ha ha ha ha ha ha ha ha ha

or repeated blocks caused by extraction errors.

Normal repetition in legitimate language must be preserved.

Repetition detection should therefore be based on thresholds and diagnostics,
not simple duplicate-word rules.

---

## 15. Deduplication

Deduplication occurs AFTER cleaning and normalization.

The initial deduplication strategy is exact normalized-text hashing.

Normalization for hashing:

1. Unicode NFC
2. collapse whitespace
3. strip leading/trailing whitespace

Do not lowercase text for hashing.

Do not remove punctuation for hashing.

Near-duplicate detection may be added later, but it must be evaluated
separately.

---

## 16. Evaluation Set Protection

The evaluation corpus is held out.

It must NOT be:

- cleaned using rules developed from the evaluation set
- used to tune cleaning thresholds
- deduplicated against training data
- used for model training
- used to make training-data filtering decisions

The evaluation set may be inspected diagnostically, but its original
content must remain immutable.

---

## 17. Provenance

Every processed dataset must retain provenance information.

At minimum:

- source dataset
- source record ID
- source URL when available
- license
- processing version
- cleaning version
- transformation timestamp
- rejection reason when applicable

A processed record must remain traceable to its source.

---

## 18. Auditability

Every cleaning run must produce:

1. processed dataset
2. processing manifest
3. cleaning statistics
4. rejected-record statistics
5. duplicate statistics
6. pipeline version
7. configuration used

Example statistics:

    input_records
    output_records
    rejected_records
    duplicates_removed
    urls_removed
    html_markers_removed
    read_more_markers_removed
    embed_markers_removed

---

## 19. Determinism

Given:

- identical input
- identical cleaning configuration
- identical pipeline version

the cleaner must produce identical output.

Random transformations are prohibited.

If sampling is introduced for diagnostics, the random seed must be explicit.

---

## 20. Versioning

Cleaning rules are versioned independently from the dataset.

Example:

    cleaning_version = 0.1.0

A change to cleaning behavior requires a version change.

The pipeline must never silently reinterpret an older processed dataset
under newer cleaning rules.

---

## 21. Testing Requirements

Every cleaning rule must have tests covering:

### Positive cases

Text that SHOULD be cleaned.

### Negative cases

Text that MUST NOT be altered.

### Mixed cases

Text containing both removable artifacts and legitimate Oromo content.

Example:

    Legitimate Oromo sentence + URL

Expected:

    Legitimate Oromo sentence

The original raw text must remain unchanged.

---

## 22. Initial Cleaning Scope

Version 0.1.0 will implement only conservative transformations:

1. Unicode NFC normalization
2. whitespace normalization
3. removal of obvious Read More markers
4. removal of obvious embed markers
5. removal of HTML markup
6. removal of clearly identifiable CMS boilerplate
7. removal of URLs
8. empty-record detection
9. basic pathological-repetition diagnostics
10. exact normalized-text deduplication

No aggressive language filtering will be implemented.

No semantic rewriting will be implemented.

No AI-generated rewriting will be implemented.

No machine translation will be used to "improve" the corpus.

---

## 23. Future Cleaning

Future versions may add:

- language identification
- document-level quality scoring
- near-duplicate detection
- source-specific boilerplate detection
- sentence segmentation
- paragraph reconstruction
- OCR error detection
- dialect metadata
- contamination detection
- PII detection
- multilingual contamination analysis

Each future feature must be evaluated independently before becoming part
of the production pipeline.

---

## 24. Approval Status

Current status:

    POLICY DEFINED — IMPLEMENTATION NOT YET APPROVED

The raw AfriBERTa Afaan Oromoo corpus remains untouched.

No processed training corpus should be generated until the cleaning
implementation passes its unit and regression tests.

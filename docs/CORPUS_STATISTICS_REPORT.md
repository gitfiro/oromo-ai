<div align="center">

<h1>🧠 Afaan Oromoo AI</h1>

<h2>Corpus Statistics Report</h2>

<p>
<strong>Dataset:</strong> AfriBERTa Afaan Oromoo Training Corpus<br>
<strong>Processed Version:</strong> <code>afriberta_oromo_v0.1.1</code><br>
<strong>Language:</strong> Afaan Oromoo (<code>orm</code>)
</p>

<table>
<tr>
<td align="center"><strong>410,242</strong><br>Training Records</td>
<td align="center"><strong>52,122,995</strong><br>Characters</td>
<td align="center"><strong>0</strong><br>Malformed Records</td>
<td align="center"><strong>0</strong><br>Duplicate Hashes</td>
</tr>
</table>

<br>

<p>
<strong>Processing Status:</strong> 🟢 Production Cleaning Validated
</p>

<p>
<strong>Report Purpose:</strong> Quantify corpus composition before model-training decisions
</p>

</div>

---

## 1. Purpose

This document provides the quantitative statistics and structural characterization of the processed Afaan Oromoo corpus used by the **Oromo AI** project.

The analysis is intended to answer:

1. How large is the corpus?
2. How much usable text does it contain?
3. What are the record-length characteristics?
4. How diverse is the vocabulary?
5. How concentrated is the corpus?
6. How prevalent are English and code-switching signals?
7. What orthographic characteristics are present?
8. Are there remaining structural artifacts?
9. What limitations should be considered before continued pretraining?

> **Scope:** This report is descriptive. It does not automatically determine whether the corpus is sufficient for model training.

No transformation is performed by this report.

---

# 2. Source & Provenance

## 2.1 Upstream Dataset

<table>
<thead>
<tr>
<th>Property</th>
<th>Value</th>
</tr>
</thead>
<tbody>
<tr>
<td>Dataset</td>
<td><code>castorini/afriberta-corpus</code></td>
</tr>
<tr>
<td>Oromo subset</td>
<td><code>afaanoromoo</code></td>
</tr>
<tr>
<td>License</td>
<td>Apache-2.0</td>
</tr>
<tr>
<td>Original training records</td>
<td>410,841</td>
</tr>
<tr>
<td>Original evaluation records</td>
<td>30,000</td>
</tr>
</tbody>
</table>

The evaluation corpus is maintained separately and is **not included** in the processed training dataset.

---

## 2.2 Raw Training Source

```text
data/raw/afriberta_oromo/train/train.txt
```

<details>
<summary>🔐 Raw Source SHA-256</summary>

```text
269cde87d84ad34463b7bd654b16737aeef756adbe2463518353004660187d6a
```

<strong>Integrity:</strong> Immutable

</details>

---

## 2.3 Processed Dataset

```text
data/processed/afriberta_oromo_v0.1.1/train.jsonl
```

<details>
<summary>🔐 Processed Dataset SHA-256</summary>

```text
c6748db774fbd03af1fbfb3389f8fdb5ac43356918e292c994e82bfe984de039
```

</details>

### Supporting Files

```text
data/manifests/afriberta_oromo_v0.1.1/manifest.json

data/processed/afriberta_oromo_v0.1.1/rejected.jsonl
```

---

# 3. Processing Results

The production processor received:

<div align="center">

<h3>410,841 input records</h3>

↓

<h3>410,242 final records</h3>

</div>

## 3.1 Record Accounting

```text
410,242 output records
+   565 quality rejections
+    34 duplicates removed after cleaning
------------------------------------------
= 410,841 input records
```

## 3.2 Processing Summary

<table>
<thead>
<tr>
<th>Metric</th>
<th>Value</th>
</tr>
</thead>
<tbody>
<tr>
<td>Input records</td>
<td><strong>410,841</strong></td>
</tr>
<tr>
<td>Output records</td>
<td><strong>410,242</strong></td>
</tr>
<tr>
<td>Initial REJECT decisions</td>
<td>565</td>
</tr>
<tr>
<td>CLEAN decisions</td>
<td>360</td>
</tr>
<tr>
<td>Records actually changed</td>
<td>264</td>
</tr>
<tr>
<td>Empty after cleaning</td>
<td>0</td>
</tr>
<tr>
<td>Duplicates removed after cleaning</td>
<td>34</td>
</tr>
<tr>
<td>Rejected-ledger entries</td>
<td>599</td>
</tr>
<tr>
<td>Output characters</td>
<td><strong>52,122,995</strong></td>
</tr>
</tbody>
</table>

> The rejected ledger contains 599 entries because it records both quality rejections and duplicate-after-cleaning records.

```text
565 + 34 = 599
```

---

# 4. Integrity Validation

<div align="center">

<h3>🟢 Production Integrity Checks: PASSED</h3>

</div>

<table>
<thead>
<tr>
<th>Invariant</th>
<th>Result</th>
</tr>
</thead>
<tbody>
<tr>
<td>Raw source checksum unchanged</td>
<td>🟢 PASS</td>
</tr>
<tr>
<td>Processed JSONL valid</td>
<td>🟢 PASS</td>
</tr>
<tr>
<td>Malformed JSON records</td>
<td><strong>0</strong></td>
</tr>
<tr>
<td>Empty processed records</td>
<td><strong>0</strong></td>
</tr>
<tr>
<td>Duplicate cleaned hashes</td>
<td><strong>0</strong></td>
</tr>
<tr>
<td>Manifest record count matches</td>
<td>🟢 PASS</td>
</tr>
<tr>
<td>Manifest character count matches</td>
<td>🟢 PASS</td>
</tr>
<tr>
<td>Unique source lines match output</td>
<td>🟢 PASS</td>
</tr>
<tr>
<td>Residual HTML</td>
<td><strong>0</strong></td>
</tr>
<tr>
<td>Residual embed markers</td>
<td><strong>0</strong></td>
</tr>
</tbody>
</table>

### Raw Source Verification

```text
269cde87d84ad34463b7bd654b16737aeef756adbe2463518353004660187d6a
```

The raw source remains unchanged.

---

# 5. Cleaning Impact

The production cleaner is intentionally **conservative**.

## Applied Transformations

* Unicode NFC normalization
* Whitespace normalization
* Obvious `Read More` marker removal
* CMS embed-marker removal
* Obvious HTML removal
* URL removal
* CMS boilerplate removal

## Explicitly Not Applied

* Lowercasing
* ASCII folding
* Diacritic removal
* Apostrophe normalization
* Punctuation stripping
* Semantic rewriting
* Translation
* AI paraphrasing
* Dialect normalization

### Cleaning Impact

<div align="center">

<h2>264</h2>

<p>records were actually changed by cleaning</p>

</div>

This represents a very small fraction of the corpus and indicates that the source corpus is predominantly text rather than webpage markup or extraction noise.

---

# 6. Residual Structural Signals

<table>
<thead>
<tr>
<th>Signal</th>
<th>Count</th>
</tr>
</thead>
<tbody>
<tr>
<td>Residual URLs</td>
<td><strong>44</strong></td>
</tr>
<tr>
<td>Residual HTML</td>
<td><strong>0</strong></td>
</tr>
<tr>
<td>Residual embed markers</td>
<td><strong>0</strong></td>
</tr>
</tbody>
</table>

## 6.1 `Read More` Analysis

<table>
<thead>
<tr>
<th>Pattern</th>
<th>Records</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>[Read More]</code></td>
<td>561</td>
</tr>
<tr>
<td>Terminal <code>Read More</code></td>
<td>312</td>
</tr>
<tr>
<td>Legitimate <code>Read more about ...</code></td>
<td>66</td>
</tr>
<tr>
<td>Embedded / other</td>
<td>132</td>
</tr>
</tbody>
</table>

The remaining embedded/other cases were not automatically removed because they can represent legitimate linguistic or content-bearing text.

### Quality Principle

<div align="center">

<strong>Precision over artifact-count minimization.</strong>

</div>

---

# 7. Rejection Statistics

The production decision layer rejected **565 records**.

<table>
<thead>
<tr>
<th>Rejection Reason</th>
<th>Records</th>
</tr>
</thead>
<tbody>
<tr>
<td>Scientific / genomic payload</td>
<td>308</td>
</tr>
<tr>
<td>Social-media spam</td>
<td>144</td>
</tr>
<tr>
<td>Obvious extraction garbage</td>
<td>111</td>
</tr>
<tr>
<td>Technical / code payload</td>
<td>1</td>
</tr>
<tr>
<td>Base64 / data URI</td>
<td>1</td>
</tr>
<tr>
<td><strong>Total</strong></td>
<td><strong>565</strong></td>
</tr>
</tbody>
</table>

> These categories are structural quality signals, not judgments about the subject matter of the text.

Scientific, political, historical, religious, cultural, and technical Oromo content is **not rejected merely because of its topic**.

---

# 8. Deduplication

Deduplication occurs **after cleaning**.

## Normalization Pipeline

```text
Unicode NFC normalization
        ↓
Whitespace collapsing
        ↓
Leading / trailing whitespace removal
        ↓
SHA-256 hashing
```

The process does not lowercase text and does not remove punctuation.

This prevents potentially meaningful linguistic distinctions from being erased during duplicate detection.

## Production Results

<table>
<tr>
<td align="center">
<strong>410,841</strong><br>
Input Records
</td>
<td align="center">
<strong>34</strong><br>
Duplicates Removed
</td>
<td align="center">
<strong>410,242</strong><br>
Final Records
</td>
<td align="center">
<strong>0</strong><br>
Duplicate Hashes
</td>
</tr>
</table>

---

# 9. Corpus Size

<div align="center">

<table>
<tr>
<td align="center">

<h2>410,242</h2>

<strong>Records</strong>

</td>

<td align="center">

<h2>52,122,995</h2>

<strong>Characters</strong>

</td>
</tr>
</table>

</div>

> ⚠️ A model-token count has **not yet been established**.

The character count must **not** be presented as an equivalent token count.

Token counts must be calculated using the tokenizer selected for the foundation-model experiment.

---

# 10. Tokenization

The final foundation-model tokenizer has not yet been selected.

This distinction is important because tokenization efficiency for Afaan Oromoo may differ substantially between:

* Generic multilingual tokenizers
* African-language tokenizers
* Oromo-adapted tokenizers
* Newly trained Oromo-aware tokenizers

## Required Measurements

```text
Total tokens
Tokens / character
Tokens / record
Median tokens / record
P95 tokens / record
P99 tokens / record
Maximum tokens / record
Unknown-token rate, if applicable
```

> **Tokenizer comparison is a separate experiment.**

---

# 11. Record-Length Distribution

Record length must eventually be measured at both the **character** and **token** levels.

## Required Statistics

```text
Minimum characters
Maximum characters
Mean characters
Median characters
P50
P75
P90
P95
P99
```

## Short Records

Potential categories:

* Titles
* Headlines
* Metadata
* Fragments
* Legitimate short statements
* Dictionary-like content

## Long Records

Potential categories:

* Complete articles
* Concatenated articles
* Extraction errors
* Duplicated sections
* Unusually large documents

> **Length alone must not determine rejection.**

---

# 12. Vocabulary Analysis

The next vocabulary analysis should include:

```text
Unique whitespace tokens
Total whitespace-token occurrences
Type-token ratio
Hapax proportion
Top 100 tokens
Top 1,000 tokens
```

## Oromo-Specific Considerations

Vocabulary analysis must preserve relevant Oromo orthography, including:

* Apostrophes
* Long vowels
* Consonant length
* Qubee spelling
* `q`
* `x`
* `c`
* `ch`
* `dh`
* `ny`
* `ph`
* Capitalization
* Punctuation

> Vocabulary statistics must not normalize away linguistically meaningful properties.

---

# 13. Orthographic Analysis

Previously observed signals in the raw training corpus:

<table>
<thead>
<tr>
<th>Character</th>
<th>Count</th>
</tr>
</thead>
<tbody>
<tr><td><code>Q</code></td><td>41,695</td></tr>
<tr><td><code>q</code></td><td>340,997</td></tr>
<tr><td><code>X</code></td><td>9,027</td></tr>
<tr><td><code>x</code></td><td>67,411</td></tr>
<tr><td><code>C</code></td><td>35,367</td></tr>
<tr><td><code>c</code></td><td>330,451</td></tr>
<tr><td><code>G</code></td><td>86,002</td></tr>
<tr><td><code>g</code></td><td>782,016</td></tr>
<tr><td><code>ʼ</code></td><td>217</td></tr>
<tr><td><code>’</code></td><td>172,838</td></tr>
<tr><td><code>'</code></td><td>189,312</td></tr>
</tbody>
</table>

> These values are observations from the source corpus and should not be interpreted as linguistic frequency estimates for Afaan Oromoo as a whole.

Future analysis should also measure:

```text
dh
ch
ny
ph
Long-vowel representations
Apostrophe variants
Capitalization patterns
Unicode normalization variants
```

---

# 14. English & Code-Switching

A preliminary scan of the raw training corpus found:

<div align="center">

<h2>26,946</h2>

<p>matches against a set of common English words</p>

</div>

> ⚠️ This is **not an English contamination count**.

English words can legitimately occur through:

* Proper names
* Quotations
* Technical terminology
* Article titles
* Bilingual text
* Code-switching
* References
* URLs
* Web-derived content

## Future Language Identification

The corpus should eventually be classified into:

```text
Oromo-dominant
Oromo + English code-switching
English-dominant
Other-language
Uncertain
```

Classification should remain diagnostic before any records are removed.

---

# 15. Domain Diversity

The current corpus is known to contain substantial news-derived material, including **BBC News** and **Common Crawl** sources.

Future analysis should measure:

<table>
<tr>
<td>📰 News</td>
<td>🏛️ Politics</td>
<td>📜 History</td>
</tr>
<tr>
<td>🎭 Culture</td>
<td>🕌 Religion</td>
<td>🎓 Education</td>
</tr>
<tr>
<td>🔬 Science</td>
<td>💻 Technology</td>
<td>⚽ Sports</td>
</tr>
<tr>
<td>💰 Economics</td>
<td>🗺️ Geography</td>
<td>📚 Literature</td>
</tr>
<tr>
<td>💬 Conversation</td>
<td>📖 Reference</td>
<td>🌐 Web Content</td>
</tr>
</table>

> The current corpus should therefore be treated as a **seed corpus**, not automatically as a complete representation of Afaan Oromoo.

---

# 16. Source Concentration

A foundation model can become stylistically or factually concentrated when a large portion of training data originates from a small number of publishers or websites.

## Required Measurements

```text
Records per source
Characters per source
Percentage of corpus per source
Top 10 sources
Top 20 sources
Source entropy
```

The project should determine whether a small number of sources dominate the corpus.

If concentration is high, additional independent Oromo sources should be collected before large-scale continued pretraining.

---

# 17. Near-Duplicate Analysis

Exact duplicate removal is complete.

However, exact deduplication is not sufficient for a web-derived corpus.

Future analysis should investigate:

* Repeated article syndication
* Copied news stories
* Mirrored pages
* Paragraph-level duplication
* Boilerplate templates
* Headline duplication
* Near-identical article variants

## Recommended Methods

```text
MinHash
SimHash
n-gram fingerprints
Locality-sensitive hashing
```

> Near-duplicate removal must remain conservative and provenance-aware.

---

# 18. Evaluation Isolation

The original AfriBERTa evaluation set contains:

<div align="center">

<h2>30,000 records</h2>

</div>

It must remain completely separate from training.

The project must **not**:

* Clean it using training transformations
* Train on it
* Use it for SFT
* Use it for preference optimization
* Use it for tokenizer training without an explicit leakage analysis
* Use it for iterative model selection without recording evaluation exposure

<div align="center">

<h3>🔒 Evaluation Integrity</h3>

<strong>FIRST-CLASS REQUIREMENT</strong>

</div>

---

# 19. Current Assessment

<div align="center">

<h2>🟢 Structurally Healthy</h2>

<p>Ready for deeper corpus characterization</p>

</div>

Current evidence shows:

<table>
<thead>
<tr>
<th>Signal</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr><td>Approximately 410k usable training records</td><td>🟢</td></tr>
<tr><td>Approximately 52.1M characters</td><td>🟢</td></tr>
<tr><td>Very low cleaning impact</td><td>🟢</td></tr>
<tr><td>Malformed processed records</td><td>0</td></tr>
<tr><td>Empty records</td><td>0</td></tr>
<tr><td>Duplicate cleaned hashes</td><td>0</td></tr>
<tr><td>Complete source-line provenance</td><td>🟢</td></tr>
<tr><td>Raw source preserved</td><td>🟢</td></tr>
<tr><td>Explicit rejection ledger</td><td>🟢</td></tr>
<tr><td>Evaluation data separated</td><td>🟢</td></tr>
</tbody>
</table>

## Major Unanswered Questions

1. How many model tokens does the corpus contain?
2. How diverse is its vocabulary?
3. How concentrated are its sources?
4. How much near-duplicate material exists?
5. What proportion is genuinely Oromo-dominant?
6. What domains are represented?
7. How much English/code-switching exists?
8. How much dialectal variation exists?
9. How does a candidate tokenizer encode Oromo?
10. How much additional high-quality Oromo data should be added?

---

# 20. Training Readiness

<div align="center">

<h3>🟢 CORPUS CLEANING VALIDATED</h3>

<p>↓</p>

<h3>🟡 CORPUS CHARACTERIZATION IN PROGRESS</h3>

<p>↓</p>

<h3>⚪ TRAINING NOT YET APPROVED</h3>

</div>

### Current Status

```text
CORPUS CLEANING VALIDATED
CORPUS CHARACTERIZATION IN PROGRESS
```

The dataset is **not yet declared training-ready**.

The next decision should be based on measured corpus statistics rather than record count alone.

---

# 21. Required Next Statistics

## 📦 Size

* Records
* Characters
* Estimated tokens
* Exact tokens for candidate tokenizers

## 📏 Length

* Minimum
* Mean
* Median
* P75
* P90
* P95
* P99
* Maximum

## 🔤 Vocabulary

* Unique tokens
* Type-token ratio
* Frequency distribution
* Hapax rate

## 🌐 Source

* Source counts
* Source percentages
* Source concentration

## 🗣️ Language

* Oromo-dominant
* English-dominant
* Mixed / code-switched
* Uncertain

## 🖊️ Orthography

* Oromo-specific character frequencies
* Apostrophe variants
* Common Qubee sequences

## ♻️ Duplication

* Exact duplicates
* Near duplicates
* Repeated articles
* Repeated paragraphs

## 🌍 Domain

* News
* Politics
* Culture
* Religion
* Education
* Science
* Technology
* Literature
* Reference
* Other

---

# 22. Reproducibility Requirements

Every future corpus-statistics run must record:

```text
Dataset version
Source SHA-256
Processed dataset SHA-256
Statistics script version
Python version
Library versions
Tokenizer / model identifier
Timestamp
```

Statistics must **never silently overwrite previous reports**.

Each significant corpus revision receives a new version.

---

# 23. Project Principle

<div align="center">

<h2>Measure First.</h2>

<h2>Transform Second.</h2>

<h2>Train Third.</h2>

<br>

<strong>Measure → Transform → Train</strong>

</div>

The goal is not to maximize the apparent cleanliness of the dataset.

The goal is to preserve the largest possible amount of:

```text
HIGH-QUALITY
     +
DIVERSE
     +
TRACEABLE
     +
AFAAN OROMOO KNOWLEDGE
```

while removing demonstrable extraction and contamination artifacts.

---

# 24. Document Status

<table>
<tr>
<td><strong>Report Status</strong></td>
<td>🟡 Draft — Statistics Generation Pending</td>
</tr>
<tr>
<td><strong>Dataset Status</strong></td>
<td>🟢 Processed & Integrity Validated</td>
</tr>
<tr>
<td><strong>Training Status</strong></td>
<td>⚪ Not Yet Approved</td>
</tr>
<tr>
<td><strong>Dataset Version</strong></td>
<td><code>afriberta_oromo_v0.1.1</code></td>
</tr>
</table>

---

<div align="center">

<strong>Oromo AI</strong><br>

<sub>Corpus Engineering • Data Quality • Language Technology</sub>

</div>

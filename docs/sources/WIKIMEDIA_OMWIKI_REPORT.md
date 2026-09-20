# OromoCorpus — Wikimedia Afaan Oromoo Source Report

**Source ID:** `wikimedia-omwiki`
**Source:** Afaan Oromoo Wikipedia
**Corpus family:** OromoCorpus
**Status:** Metrics frozen; source licensing/provenance review complete
**Registry status:** `approved`

---

## 1. Purpose

This report records the acquisition, extraction, cleaning, quality
screening, deduplication, and tokenizer measurements for Afaan Oromoo
Wikipedia during OromoCorpus expansion.

The measured source contribution is frozen.

Any future change to extraction, cleaning, filtering, deduplication, or
tokenizer measurement requires a new source-manifest version.

---

## 2. Source Identity

- Wikimedia project: `omwiki`
- Language: Afaan Oromoo
- ISO 639-3: `orm`
- Website: `https://om.wikipedia.org/`
- Acquisition method: official Wikimedia XML dump
- Domain: encyclopedia / reference

During initial source verification, `orwiki` was identified as Odia
Wikipedia and discarded before ingestion.

The correct Afaan Oromoo Wikimedia project is `omwiki`.

---

## 3. Raw Artifact

Artifact:

`omwiki-latest-pages-articles-multistream.xml.bz2`

Verified SHA-256:

`6fa7678029d946e8c13fb00e088a2c21553bf955a5e6801d5313fc56173618aa`

Only namespace `0` article pages were considered.

Redirects were excluded.

---

## 4. Extraction

Namespace-0 articles extracted:

`2,420`

The extraction stage preserved:

- source ID
- page title
- page ID
- revision ID
- revision timestamp
- article URL
- revision URL
- source license metadata
- original MediaWiki wikitext

Contributor usernames and IP addresses were not retained as corpus fields.

---

## 5. MediaWiki Cleaning

Records before source-specific cleaning:

`2,420`

Records retained after MediaWiki cleaning:

`2,401`

Structural-only / empty records removed:

`19`

Raw characters:

`6,435,348`

Characters after MediaWiki cleaning:

`4,886,367`

Character retention:

`75.93%`

Cleaning removes demonstrable MediaWiki structure such as:

- templates
- tables
- references
- galleries
- categories
- file/image links
- wiki-link delimiters
- heading markup

The cleaner does not rewrite spelling, grammar, dialect, factual content,
or ordinary multilingual source text.

---

## 6. Quality Screening

Quality rejections:

- scientific/genomic payload: `6`
- social-media spam: `1`
- obvious extraction garbage: `1`

Total quality rejections:

`8`

---

## 7. Exact Deduplication

Within-source exact duplicates removed:

`33`

Exact duplicates against `afriberta_oromo_v0.1.2`:

`91`

Exact-net-new records:

`2,269`

Exact-net-new characters:

`4,768,570`

Exact duplicate normalization uses:

- Unicode NFC
- whitespace collapsing
- leading/trailing whitespace removal

It does not lowercase or remove punctuation.

---

## 8. Near-Duplicate Screening

Method:

`word 5-gram Jaccard`

Threshold:

`0.85`

Near duplicates removed:

`15`

Observed rejected-pair similarity:

- minimum: `0.861635`
- average: `0.953368`
- maximum: `1.0`

Final net-new records:

`2,254`

Final net-new characters:

`4,749,893`

---

## 9. Token Measurements

Whitespace tokens:

`612,144`

### Oromo Unigram 32K + byte fallback

- vocabulary: `32,000`
- tokenizer tokens: `1,112,880`
- chars/token: `4.2681`
- tokenizer tokens / whitespace token: `1.8180`

### Oromo Unigram 48K + byte fallback

- vocabulary: `48,000`
- tokenizer tokens: `1,070,896`
- chars/token: `4.4354`
- tokenizer tokens / whitespace token: `1.7494`

No final OromoLM tokenizer has been selected.

These counts are therefore reference measurements.

For corpus planning, the 48K-byte measurement is currently used as a
conservative reference:

`1,070,896 reference tokenizer tokens`

---

## 10. Licensing and Provenance

Declared Wikimedia text license:

`CC BY-SA 4.0`

Project source decision:

- registry status: `approved`
- training permission: `yes`
- redistribution permission: `yes`, subject to CC BY-SA 4.0 obligations
- attribution required: yes
- modification notice required: yes
- applicable ShareAlike obligations must be preserved for redistributed adapted text
- approved for OromoCorpus source use: yes
- downstream model-weight licensing: separate review required

Approval of this source for corpus use does not by itself determine the
license that must apply to trained model weights.

Article-level provenance and source URLs are preserved to support
attribution and reproducibility.

---

## 11. Frozen Contribution

Final measured contribution:

- records: `2,254`
- characters: `4,749,893`
- whitespace tokens: `612,144`
- 32K-byte tokenizer tokens: `1,112,880`
- 48K-byte tokenizer tokens: `1,070,896`

The measured result is frozen.

Any material processing-policy change requires a new source-manifest version.

---

## 12. OromoCorpus Status

`wikimedia-omwiki` is an approved OromoCorpus source.

It contributes approximately:

`1.07 million`

48K-byte reference tokenizer tokens toward the OromoCorpus expansion target.

The final tokenizer-dependent corpus total will be recalculated after the
OromoLM tokenizer strategy is frozen.

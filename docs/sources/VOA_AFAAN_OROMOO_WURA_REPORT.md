# VOA Afaan Oromoo via WURA — Source Qualification Report

**Source ID:** `voa-afaan-oromoo-via-wura`

**Publisher:** Voice of America

**Upstream dataset:** `castorini/wura`

**Language:** Afaan Oromoo (`orm`)

**Status:** Metrics frozen; provenance-cleared subset approved for OromoCorpus

## Purpose

This source qualification evaluates Afaan Oromoo documents attributed to
`voaafaanoromoo.com` in the WURA corpus.

WURA is used as the acquisition and provenance-discovery layer. Acceptance
into OromoCorpus is based on the underlying publisher provenance rather than
the WURA package license alone.

## Raw Source

WURA file:

`documents-v1.0/train/orm.jsonl`

WURA Oromo training file:

- Records: 20,169
- SHA-256:
  `854ad8d60226a6897294e613f8fc766c8e910634100141903d01f6576250fc12`

VOA subset:

- Records: 9,761
- Raw characters: 10,639,678
- SHA-256:
  `cded712bad9f2f7ee3778bc7ca8fcb9289d96f7e9c008a38b03744f4539a7afd`

## Provenance Screening

VOA material may contain externally supplied or copyrighted third-party
material. The source was therefore screened conservatively before entering
the normal Oromo AI corpus pipeline.

### Wire-service hold

Records containing markers for:

- Associated Press / AP
- Agence France-Presse / AFP
- Reuters

were held for exclusion from the approved subset.

Wire-service hold:

- 63 records

### Additional publisher hold

A second screening held records containing identified references to:

- BBC
- CNN
- Bloomberg
- The Guardian
- New York Times
- Washington Post
- Al Jazeera
- Deutsche Welle
- France 24

Publisher-marker hold:

- 59 records

### Provenance-cleared pool

9,761 raw VOA records
- 63 wire-service holds
- 59 publisher-marker holds
= 9,639 provenance-cleared candidates

Provenance-cleared SHA-256:

`1e4ec6b4405a6ebe37448df279a403b59085e2d3f732a7ae5748d06c77044d1c`

## Quality Processing

The provenance-cleared subset was processed through the existing conservative
Oromo AI quality pipeline.

Results:

- Input records: 9,639
- KEEP decisions: 9,612
- CLEAN decisions: 27
- Records changed during cleaning: 23
- REJECT decisions: 0
- Validation failures: 0
- Accepted records: 9,639
- Character retention: 99.98%

Quality-accepted SHA-256:

`1d85dc7595c0a401fad72a4e6ccc04b83fe4a071f60b6d321c80eee758eeb607`

## Exact Deduplication

Within-source exact duplicate removal:

- Input: 9,639
- Exact duplicates: 126
- Unique: 9,513

Cross-source comparison against:

- AfriBERTa Oromo v0.1.2: 410,193 records
- frozen omwiki v0.1: 2,254 records

Cross-source exact duplicates:

- AfriBERTa: 0
- omwiki: 0

Exact-net-new records:

9,513

Exact-net-new SHA-256:

`959e885ca5b8cb12c742ee238219aa816777f22ef0a4660fc88d14c355e46148`

## Near Deduplication

Near-duplicate policy:

- word shingle size: 5
- exact Jaccard threshold: >= 0.85
- bottom-k candidate signature size: 32

Within-source near duplicates:

- 2

Similarity range:

- 0.941176 to 1.000000

Cross-source near duplicates:

- AfriBERTa: 1
- omwiki: 0

Cross-source similarity:

- 0.891304

## Final Net-New Contribution

Final records:

9,510

Final characters:

10,433,883

Whitespace tokens:

1,334,704

Average characters per record:

1,097.15

Final artifact SHA-256:

`4abe7c6b938de5714707303a8f56a82bea48a624a5719a8e2beb1d46434b426d`

## Tokenizer Measurements

Tokenizer measurements are reference measurements only. The final OromoLM
tokenizer strategy has not yet been frozen.

### Oromo Unigram 32K + byte fallback

- vocabulary: 32,000
- tokenizer tokens: 1,976,931
- characters/token: 5.2778
- tokenizer tokens/whitespace token: 1.4812

### Oromo Unigram 48K + byte fallback

- vocabulary: 48,000
- tokenizer tokens: 1,899,811
- characters/token: 5.4921
- tokenizer tokens/whitespace token: 1.4234

The 48K tokenizer is currently used only as the corpus-planning reference.

## Licensing and Provenance Decision

The approved subset is based on VOA-origin material after conservative
third-party provenance filtering.

Training permission:

`yes`

Dataset-text redistribution permission:

`yes`

Third-party material:

held from the approved subset when identified by the provenance screens.

Downstream trained-model-weight licensing:

`separate_review_required`

This source decision applies only to the frozen provenance-cleared subset
described by this report and manifest.

## Release Status

Metrics frozen:

`true`

Approved for OromoCorpus release:

`true`

Any change to the provenance policy, quality pipeline, deduplication policy,
or source-selection rules requires a new manifest version.

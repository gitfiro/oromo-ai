# Michsethowusu Oromo Sentiments cleaned subset v0.1

## Decision

**Approved for OromoCorpus as a cleaned text subset.**

Approval applies only to the frozen project-produced artifact, not to all rows in the upstream dataset.

## Upstream source

- Dataset: `michsethowusu/oromo-sentiments-corpus`
- Upstream rows observed: **825,272**
- Dataset-level license: **MIT**
- Source URL: https://huggingface.co/datasets/michsethowusu/oromo-sentiments-corpus

The original dataset contained substantial multilingual/noisy material, so Oromo AI did not accept the upstream dataset wholesale.

## Qualification pipeline

```text
825,272 upstream rows
      ↓ first-pass Oromo/noise screening
282,604 likely-Oromo rows
      ↓ exact cross-source deduplication
77,384 exact duplicates removed
205,220 exact-net-new rows
      ↓ canonical 5-word-shingle near deduplication
11,539 near duplicates removed
      ↓
193,681 final accepted rows
```

Almost all measured cross-source duplication was against AfriBERTa:

```text
exact duplicates:
  AfriBERTa: 77,377
  Wikimedia:      7

near duplicates:
  AfriBERTa: 11,537
  Wikimedia:      2
```

Near-duplicate policy:

```text
normalization: project canonical similarity normalization
shingle size:  5 words
Jaccard gate:  0.85
```

## Frozen accepted artifact

```text
records:              193,681
whitespace words:   2,726,122
characters:        20,515,090
48K ref tokens:     3,877,136
tokens/word:           1.4222
```

Final artifact SHA-256:

```text
c816cd962170c50ed49f00c04951762b12391c772d52e7058ddb9a778f2afc01
```

Raw capture SHA-256:

```text
5e4285a51313103ef7f373d21a1d9202ab226daa52d542fd949772810393eac5
```

Acceptance report SHA-256:

```text
429ab43aa3fa3a32d1f7ad3f6a8411654898da82c21cd88b82f98b485ef5f14d
```

48K reference tokenizer SHA-256:

```text
79d64021d85877c1544e7e3a26bb21d2ad15f0aa7c6e76aeeeed3efddc5c3d2f
```

## Quality review

A deterministic retained-text sample showed overwhelmingly recognizable Afaan Oromoo across legal, political, religious, technical, public-information, health, and conversational material. A small amount of malformed or fragmentary text remains, so language risk is recorded as **medium** rather than low.

This is a pragmatic corpus-expansion decision: the cleaned subset is suitable for continued-pretraining use, while the original unfiltered dataset is not.

## OromoCorpus contribution

Before this source:

```text
511,510 records
52,137,803 reference tokens
```

After this source:

```text
705,191 records
56,014,939 reference tokens
56.01% of the 100M planning target
```

The sentiment labels are not required for OromoLM CPT; the accepted contribution is the text subset and its provenance metadata.

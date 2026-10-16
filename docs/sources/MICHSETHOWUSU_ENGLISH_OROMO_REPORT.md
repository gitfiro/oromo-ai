# Michsethowusu English–Oromo cleaned monolingual subset v0.1

## Decision

**Approved for OromoCorpus as an Oromo-side monolingual cleaned subset only.**

The English–Oromo alignment is **not trusted** and is excluded from translation or parallel-corpus use.

## Upstream source

- Dataset: `michsethowusu/english-oromo_sentence-pairs`
- Upstream family: NLLB-v1-derived
- Dataset card rows: approximately 3.23M
- Licensing basis: NLLB dataset release under ODC-BY, with original-source terms still applicable
- Source URL: https://huggingface.co/datasets/michsethowusu/english-oromo_sentence-pairs

The upstream dataset is highly multilingual/noisy on the Oromo side and highly redundant with previously accepted material. It was therefore not accepted wholesale.

## Qualification pipeline

```text
3.23M upstream sentence-pair rows
      ↓ conservative Oromo/noise filtering + within-source exact dedup
263,360 likely-Oromo rows
      ↓ exact cross-source deduplication
206,257 exact duplicates removed
57,103 exact-net-new rows
      ↓ canonical 5-word-shingle near deduplication, Jaccard 0.85
12,055 near duplicates removed
      ↓
45,048 final accepted rows
```

Exact overlap breakdown:

```text
sentiments_clean: 136,157
AfriBERTa:         70,096
Wikimedia:              4
```

Near-duplicate breakdown:

```text
AfriBERTa:         11,417
sentiments_clean:     637
Wikimedia:              1
```

## Frozen accepted artifact

```text
records:              45,048
whitespace words:    819,417
characters:        6,094,197
48K ref tokens:    1,185,406
tokens/word:          1.446646
```

Final artifact SHA-256:

```text
2c540ab00da91a78eaec021c859cc583e48a039c5a30c59d253a77827bdd7324
```

Reference-token report SHA-256:

```text
b9ca0e87cd94eb8258c85f8408fd259e5cb34818cc82ec6cf77a27f3ede6f8f7
```

Reference tokenizer SHA-256:

```text
79d64021d85877c1544e7e3a26bb21d2ad15f0aa7c6e76aeeeed3efddc5c3d2f
```

## Quality decision

The deterministic post-dedup sample was overwhelmingly usable Afaan Oromoo, with only a small number of obvious contamination/noise cases. Because the upstream data is noisy and sentence-pair alignment is unreliable, the accepted scope is intentionally narrow:

- accept Oromo-side monolingual text for CPT;
- reject English–Oromo pairing as a translation-quality assumption;
- keep language risk at medium;
- retain all upstream-license/original-source caveats.

## OromoCorpus contribution

Before this source:

```text
705,191 records
56,014,939 reference tokens
```

After this source:

```text
750,239 records
57,200,345 reference tokens
57.20% of the 100M planning target
```

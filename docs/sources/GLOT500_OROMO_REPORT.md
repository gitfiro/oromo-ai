# Glot500 Oromo source-partitioned subset v0.1

## Decision

**Approved for OromoCorpus with source-level partitioning.**

Accepted Glot500 Oromo source families:

- `CC100`
- `nllb_other_aau`
- `nllb_other_hornmt`
- `nllb_other_tico`

Held:

- `mtdata` — multiple upstream licenses require source-specific review.

Previously excluded from the priority pass:

- AfriBERTa-derived material already represented in OromoCorpus;
- Wikipedia-family material expected to overlap the accepted Wikimedia source;
- non-commercial source families such as Leipzig community and AfroMAFT.

## Cross-source qualification

Priority candidate before cross-deduplication:

```text
rows:   90,050
words: 4,360,269
```

Exact cross-source deduplication against the eight previously accepted OromoCorpus sources:

```text
exact duplicates:     680
exact-net-new rows: 89,370
net-new rate:       99.24%
```

Canonical near deduplication:

```text
method:      5-word shingles
threshold:   Jaccard >= 0.85
near duplicates removed: 6,220
post-near-dedup rows:   83,150
```

## Final source-level decision

| Glot500 source | Rows | Words | 48K reference tokens | Decision |
| --- | ---: | ---: | ---: | --- |
| CC100 | 73,083 | 3,983,252 | 5,694,643 | accepted |
| nllb_other_aau | 1,997 | 38,817 | 53,782 | accepted |
| nllb_other_hornmt | 2,020 | 41,896 | 63,855 | accepted |
| nllb_other_tico | 2,969 | 62,390 | 101,376 | accepted |
| mtdata | 3,081 | 39,116 | 102,603 | held |

Accepted total:

```text
records:              80,069
whitespace words:  4,126,355
characters:       30,954,346
48K ref tokens:    5,913,656
```

## Licensing scope

Glot500 is an aggregator, so approval is made per original source family rather
than by treating the combined Glot500 package as one homogeneous license.

- CC100 is accepted under the project's documented Common Crawl / underlying-content-rights caveat. Oromo AI does not claim independent copyright clearance for every underlying web page.
- AAU and HornMT are accepted under CC-BY-4.0 attribution obligations.
- TICO is accepted under CC0-1.0.
- MTData remains held because its component datasets have multiple licenses and need source-specific review.

## Frozen artifacts

Accepted artifact:

```text
data/processed/glot500-orm-v0.1/train.jsonl
SHA-256:
a896acf3a88f40e017dd802f821c4bf8bc9278cd8483760b21e0229ffd10914f
```

Held MTData artifact:

```text
SHA-256:
c4702998189e0630e06587eecdf44d5a55da121125f25911cd56a4eba7a6436d
```

Final acceptance report:

```text
SHA-256:
16a81c5ac03b454ef833f60aeea0f96ad72093b3e9bbaa6d2bff566d3daedab5
```

Final source measurement:

```text
SHA-256:
fd2bcf7575cbb15d88d9c10ec11b1df75b5456e63d42cde8206186a614bf59ea
```

Reference tokenizer:

```text
SHA-256:
79d64021d85877c1544e7e3a26bb21d2ad15f0aa7c6e76aeeeed3efddc5c3d2f
```

## OromoCorpus contribution

Before Glot500:

```text
records: 750,239
48K reference tokens: 57,200,345
```

After Glot500:

```text
records: 830,308
48K reference tokens: 63,114,001
progress toward 100M: 63.11%
remaining to 100M: 36,885,999
```

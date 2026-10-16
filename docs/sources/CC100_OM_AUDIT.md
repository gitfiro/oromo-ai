# Official CC100 Oromo Audit — v0.1

## Decision

**Not promoted into accepted OromoCorpus.**

The official CC100 Oromo release was audited as a primary upstream source after
Glot500 CC100 had already been accepted. The source remains useful provenance,
but the independently net-new residual was too small after cross-source
deduplication to justify another acceptance cycle at this stage.

The accepted OromoCorpus total therefore remains:

```text
830,308 records
63,114,001 48K-reference tokens
63.11% of the 100M planning target
```

## Quality filtering

The raw official CC100 Oromo text contained substantial valid Afaan Oromoo
alongside short web fragments, navigation text, malformed strings, and other
extraction noise.

A conservative first-pass Oromo/noise filter was applied before cross-source
deduplication.

Filtered candidate entering exact cross-deduplication:

```text
121,497 rows
```

## Exact cross-source deduplication

The filtered candidate was compared against all nine then-accepted OromoCorpus
sources, including the accepted Glot500 source-partitioned subset.

```text
candidate rows:       121,497
exact duplicates:     108,285
duplicate rate:        89.13%
exact net-new rows:    13,212
exact net-new rate:     10.87%
net-new words:        450,479
net-new characters: 3,416,310
```

Exact duplicate destinations:

```text
glot500_accepted       62,272
afriberta              45,286
sentiments_clean          394
english_oromo_clean       212
wikimedia                   60
hplt3                       47
madlad                      14
```

Frozen exact-net-new artifact SHA-256:

```text
a1dd150243f9f639e5cfff3df150e1452ea4b159a3bba674922209dfd84e67e1
```

Exact duplicate artifact SHA-256:

```text
479078bb01a3786176880774a1c9c50ef25d6c89e8beba0bac54429a8ea7b3b6
```

Exact report SHA-256:

```text
c012428e2606f8b9ea5ae42f99d90ab272e5c4d7bc65758bd89166d8879dc094
```

## Canonical near deduplication

The exact-net-new residual was then processed with the project-standard
5-word-shingle Jaccard near-duplicate gate at threshold 0.85.

```text
input after exact:      13,212
near duplicates:         7,609
near-duplicate rate:     57.59%
final residual rows:      5,603
final residual words:   194,669
final residual chars: 1,492,144
```

Near-duplicate destinations:

```text
afriberta              6,311
glot500_accepted         761
hplt3                    183
sentiments_clean         156
english_oromo_clean      107
madlad                    46
wikimedia                 35
voa                       10
```

Frozen near-dedup residual SHA-256:

```text
1464991d473f818969315dd09fb8bdbe1ddf4b7611c175eab2d0594b15abd27c
```

Near-duplicate artifact SHA-256:

```text
c6bfc59add79ac935a03127e705c50d4f94b0b5c1243a52874dade407cb65db5
```

Near-dedup report SHA-256:

```text
4dc127d923c282b9878e36cb0c2aab210e785d1b9724131a4bbc6e21bf66738e
```

## Final rationale

The source is not rejected for language quality. It is **not promoted because
of redundancy and diminishing marginal yield**.

After filtering and both deduplication stages, only 5,603 rows / 194,669 words
remained. The project preserves this residual and the audit trail, but does not
spend another acceptance/token-count cycle on it while higher-value independent
sources remain available.

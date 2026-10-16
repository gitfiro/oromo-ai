# OromoLM +4K model-level ablation — execution status

## Status

**Training and frozen evaluation complete; +4K is the strongest current candidate under the predeclared gate.**

The +4K vocabulary-size ablation has completed both predeclared training stages on an NVIDIA A100-SXM4-80GB. The experiment preserves the same underlying Oromo text exposure as the +8K trajectory while using the smaller 4,000-token lexical augmentation.

The Stage B exact Oromo BPB learning curve and frozen WikiText retention checks are complete. The +4K path beats both the native-tokenizer CPT and +8K v0.3 Oromo BPB references while passing the predeclared general-language retention ceiling.

## Frozen +4K tokenizer and initialization

```text
effective tokenizer length: 266,145
Oromo additions:            4,000
Oromo token IDs:            262,145–266,144
tokens/word:                2.369659446
fragmentation:              38.2084%
single-token words:         61.7916%
UNK:                        0
reduction vs native:        14.9298%
```

Tokenizer JSON SHA-256:

```text
cc2d83cbb65454deee2e274d8596ea0941ff3884e93b63df8fd7c0f84364b673
```

Initialized model SHA-256:

```text
194bd10595d1e6b7b91c4c671349956a80f96b8605010ae87e7b4c9d1c96a518
```

Initialization method:

```text
native_subtoken_centroid_scaled_to_native_mean_l2_norm
```

## Packed workload

### Stage A — pilot-equivalent

```text
training tokens:      4,964,141
packed sequences:     4,848
optimizer updates:    303
train SHA-256:        d9fc9db64d8258baa4de33fc05efc3f106f56b0d3eb5bd35c324d6358aad6a02
validation SHA-256:   e114d331ff673686f02bbf951cddbfe493a0e3e709866a3b356de7d384180314
```

### Stage B — fresh v0.3 continuation

```text
training tokens:      24,838,669
packed sequences:     24,257
optimizer updates:    1,517
train SHA-256:        f0112a2256bce93d23c4f34ecfa633302b126e1f3ccf04e2db882e0a4299c38a
validation SHA-256:   e114d331ff673686f02bbf951cddbfe493a0e3e709866a3b356de7d384180314
```

Two-stage total:

```text
training tokens:      29,802,810
optimizer updates:    1,820
```

The +4K path processes about 3.16% more training tokens than the +8K two-stage path because its tokenizer is less sequence-efficient, while still materially reducing token count relative to native Gemma.

## Stage A training result

Experiment:

```text
oromolm-4k-cpt-rerun-v0.2
```

Measured A100 result:

```text
train wall time:          1,162.36 s
eval wall time:              13.69 s
total wall time:          1,176.05 s
training throughput:      4,270.92 tokens/s
peak allocated VRAM:         10.68 GiB
peak reserved VRAM:          12.38 GiB
final Trainer eval loss:      3.970907
```

Run-summary SHA-256:

```text
e78a1a304c9045124f02d4a9922a7a7474f7006f12340921691871ea19030134
```

Raw Trainer loss is not used for cross-tokenizer ranking.

## Stage A exact Oromo BPB

The exact document-reset, byte-normalized evaluator was run on the frozen 1,503-record Oromo validation set.

```text
+4K Stage A BPB: 1.844463004
```

Reference comparison:

| Model state | Exact Oromo BPB |
| --- | ---: |
| Untouched Gemma | 2.670045532 |
| Native-tokenizer CPT | **1.733832395** |
| +8K Stage A / v0.2 | 1.863338883 |
| +4K Stage A / v0.2-equivalent | **1.844463004** |

At the pilot-equivalent stage, +4K is about **1.01% lower/better in BPB than +8K**, but remains about **6.38% higher/worse than native-tokenizer CPT**.

This is evidence that the smaller augmentation adapts faster than +8K at the same underlying pilot-text exposure. It is not yet evidence that +4K is the final winner after the full two-stage trajectory.

Stage A BPB result SHA-256:

```text
0f602c6e3398829f81a563feb00bd0f1e8b63ba49e48fd8291735395ee6007d9
```

## Stage B execution

Stage B completed the full predeclared one-epoch fresh-data continuation and produced checkpoints at:

```text
250
500
750
1000
1250
1500
1517
```

A separate final model was also preserved.

The Stage B exact Oromo BPB learning curve is complete:

| Checkpoint | Exact Oromo BPB |
| ---: | ---: |
| 250 | 1.781058836 |
| 500 | 1.744201370 |
| 750 | **1.727396376** |
| 1000 | **1.721889019** |
| 1250 | **1.720904266** |
| 1500 | **1.720890953** |
| 1517 | **1.720890950** |

Reference lines:

```text
native CPT: 1.733832395
+8K v0.3:   1.734823064
```

The +4K path crosses both references by checkpoint 750. Checkpoint 1517 is the lowest measured Oromo BPB, but the curve is effectively flat from 1250 onward.

Frozen WikiText retention:

| Checkpoint | WikiText BPB | Gate |
| ---: | ---: | --- |
| 1250 | **1.030453326** | PASS |
| 1517 | **1.030463994** | PASS |

```text
untouched Gemma WikiText: 1.013254631
predeclared +5% ceiling:  1.063917363
+8K v0.3 final:           1.033754855
```

Both +4K candidates pass comfortably, and both are slightly lower/better on WikiText than the +8K final checkpoint.

Under the predeclared rules, **+4K is the strongest current candidate** because it beats the native CPT and +8K Oromo quality references while passing the retention gate. This selection is specific to the declared evaluation protocol and does not substitute for downstream OromoBench, generation, safety, or human evaluation.

## Runtime environment note

The +4K RunPod host exposed an NVIDIA driver supporting CUDA 12.8. The locked environment initially installed PyTorch 2.14.0+cu130, which could not initialize CUDA on that driver. The runtime was corrected to:

```text
PyTorch:        2.14.0+cu126
PyTorch CUDA:   12.6
GPU:            NVIDIA A100-SXM4-80GB
BF16:           supported
compute cap.:   8.0
```

Because the +4K and historical +8K runs were not executed under an identical CUDA/PyTorch binary environment, small wall-time differences must not be interpreted as a clean tokenizer-runtime win. Exact BPB remains the primary quality endpoint, while token counts provide the cleaner tokenizer-efficiency comparison.

## Preservation

The complete +4K experiment was copied from RunPod to the local research environment before pod termination.

Preserved locally:

```text
preserved/4k-ablation-2026-10-14/
```

Integrity verification:

```text
files expected: 66
files failed:   0
preserved size: 18G
```

The preserved set includes:

- Stage A final model and run metadata;
- Stage B checkpoints at 250/500/750/1000/1250/1500/1517;
- Stage B final model;
- tokenizer/config/training-state artifacts;
- Stage A exact BPB report;
- RunPod-generated SHA-256 preservation manifest.

Large model artifacts remain intentionally outside normal Git tracking.

## Decision

The predeclared +4K ablation gate is closed.

Current ordering on frozen Oromo BPB:

```text
+4K step 1517: 1.720890950
+4K step 1250: 1.720904266
native CPT:     1.733832395
+8K v0.3:       1.734823064
untouched base: 2.670045532
```

Retention gate:

```text
+4K step 1250 WikiText: 1.030453326 PASS
+4K step 1517 WikiText: 1.030463994 PASS
ceiling:                  1.063917363
```

Because step 1250 and step 1517 are effectively tied on Oromo BPB, future release selection should consider checkpoint size, training cost, downstream evaluation, and reproducibility rather than assuming the numerically smallest BPB difference is practically meaningful.

Next work:

1. preserve the new Stage B Oromo and WikiText evaluation JSON outputs with hashes;
2. run source-level and paired per-record analysis;
3. expand OromoBench and generation/human evaluation;
4. use +4K as the leading tokenizer/model path for the next scaled CPT design unless later evidence overturns it;
5. avoid additional epochs over the same continuation text, because the learning curve has plateaued.


## Source-level and paired-record analysis

The preserved exact-BPB outputs were compared across the native CPT baseline,
+8K v0.3 final checkpoint, and +4K step 1517 on the same 1,503-record Oromo
validation set.

### Per-source Oromo BPB

| Source | Native CPT | +8K v0.3 | +4K step 1517 | +4K vs native | +4K vs +8K |
| --- | ---: | ---: | ---: | ---: | ---: |
| AfriBERTa Oromo v0.1.2 | 2.069977 | 2.086606 | **2.045153** | **-1.199%** | **-1.987%** |
| MADLAD-400 Oromo v0.2 | 1.647904 | 1.648041 | **1.640854** | **-0.428%** | **-0.436%** |
| WaxalNLP Oromo ASR v2 | 1.772030 | 1.772162 | **1.750583** | **-1.210%** | **-1.218%** |
| HPLT3 gaz_Latn v0.1 | 1.640245 | 1.634172 | **1.627110** | **-0.801%** | **-0.432%** |
| VOA Afaan Oromoo | 1.773451 | 1.770278 | **1.761404** | **-0.679%** | **-0.501%** |
| Wikimedia omwiki v0.1 | **1.671917** | 1.679502 | 1.677692 | +0.345% | **-0.108%** |

Interpretation:

- +4K beats +8K on **all six** source groups.
- +4K beats native CPT on **five of six** source groups.
- The only source-level regression relative to native CPT is Wikimedia, where
  +4K is **0.345% higher/worse**.
- The aggregate win is therefore not driven by a single dominant source; it is
  distributed across AfriBERTa, MADLAD, Waxal, HPLT3 and VOA, with a small
  Wikimedia tradeoff.

### Paired-record comparison

All three reports contain the same 1,503 validation records and all 1,503 were
matched by text SHA-256.

| Comparison | +4K better | +4K worse | Ties | +4K win rate | Median BPB delta | Mean BPB delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| +4K vs native CPT | 860 | 643 | 0 | **57.22%** | **-0.012094948** | **-0.013883567** |
| +4K vs +8K v0.3 | 1,086 | 417 | 0 | **72.26%** | **-0.033670352** | **-0.048155481** |

Negative deltas favor +4K.

These paired results strengthen the aggregate conclusion: +4K improves a
majority of individual validation records versus native CPT and a substantial
majority versus +8K. They also make clear that the improvement is not universal;
643 records remain worse than native CPT and Wikimedia remains the one
source-level regression. The next analysis should therefore quantify uncertainty
and inspect the tails rather than treating the aggregate BPB win as uniform.


## Paired bootstrap uncertainty

A paired bootstrap was run over the 1,503 matched validation records using
10,000 resamples and fixed seed `20261016`. Each bootstrap replicate sampled
paired record-level BPB deltas with replacement.

Results:

| Comparison | Mean paired BPB delta | 95% bootstrap CI | Direction |
| --- | ---: | ---: | --- |
| +4K vs native CPT | **-0.013883567** | **[-0.020199325, -0.007414796]** | favors +4K |
| +4K vs +8K v0.3 | **-0.048155481** | **[-0.053106421, -0.043233026]** | favors +4K |

Negative deltas favor +4K. In both comparisons, the full 95% bootstrap interval
remains below zero.

Interpretation:

- The observed +4K advantage is not supported only by the aggregate corpus BPB;
  it is also stable under paired resampling of the frozen validation records.
- This materially strengthens the evidence that +4K is better than both native
  CPT and +8K on this specific frozen holdout and evaluation protocol.
- This is not a universal statistical guarantee for all Afaan Oromoo domains,
  prompts, or downstream tasks. Wikimedia remains a small source-level
  regression versus native CPT, and 643/1,503 individual records are still
  worse than native CPT.
- The next useful analysis is the regression tail: identify the largest
  +4K-vs-native and +4K-vs-+8K degradations, inspect their sources/text
  properties, and convert recurring failure modes into OromoBench cases.

# OromoLM +4K model-level ablation — execution status

## Status

**Training complete; final normalized evaluation pending.**

The +4K vocabulary-size ablation has completed both predeclared training stages on an NVIDIA A100-SXM4-80GB. The experiment preserves the same underlying Oromo text exposure as the +8K trajectory while using the smaller 4,000-token lexical augmentation.

No final tokenizer/model winner is claimed yet. Stage B exact Oromo BPB and WikiText retention evaluation remain required.

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

The Stage B exact Oromo BPB learning curve has **not yet been run**, and the WikiText retention gate has **not yet been evaluated** for the +4K candidates. Therefore no Stage B quality ranking is reported here yet.

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

## Remaining decision work

Run the exact frozen evaluation protocol on all retained Stage B checkpoints, then apply the predeclared decision rules from `docs/CPT_4K_ABLATION_PROTOCOL.md`.

Required next measurements:

1. exact Oromo BPB at Stage B checkpoints 250/500/750/1000/1250/1500/1517;
2. WikiText BPB for the checkpoint(s) considered for final selection;
3. comparison against:
   - native CPT: 1.733832395 Oromo BPB;
   - +8K v0.3: 1.734823064 Oromo BPB;
   - WikiText retention ceiling: 1.063917363 BPB;
4. final Pareto analysis covering quality, vocabulary size, tokenizer efficiency, and compute.

Until those measurements are complete, +4K is a **promising but unelected candidate**.

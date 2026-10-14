# OromoLM +4K model-level ablation protocol

## Purpose

Test whether the smaller Gemma +4K Oromo lexical augmentation provides a better
quality/compute/parameter tradeoff than the frozen +8K path.

This is a controlled **vocabulary-size ablation**, not a new training recipe.

## Why two stages are required

The current +8K reference did not start from untouched Gemma at v0.3. Its
trajectory was:

1. initialized Gemma +8K;
2. original Oromo CPT pilot (~2.0M words) at learning rate `2e-5`;
3. fresh v0.3 continuation (10.039M words) at learning rate `1e-5`.

Therefore +4K must replay the same two underlying text exposures and learning
rate stages. Comparing a one-stage +4K model with the two-stage +8K model would
confound tokenizer size with training exposure.

## Frozen references

### Exact Oromo quality

```text
untouched Gemma:             2.670045532 BPB
native-tokenizer Oromo CPT:  1.733832395 BPB
+8K v0.2:                    1.863338883 BPB
+8K v0.3 final:              1.734823064 BPB
```

Lower is better.

### General-language retention

```text
untouched Gemma WikiText:    1.013254631 BPB
predeclared +5% ceiling:     1.063917363 BPB
+8K v0.3 final:              1.033754855 BPB
```

The existing WikiText ceiling is reused unchanged. It is not retuned after
seeing +4K results.

## +4K tokenizer

The +4K tokenizer is deterministically derived from the first 4,000 lexical
additions in the frozen cumulative +8K artifact. It does not rerank candidates
and does not inspect evaluation data.

Expected frozen tokenizer-holdout result:

```text
effective tokenizer length: 266,145
tokens/word:                 2.369659446
fragmentation:               38.2084%
single-token words:          61.7916%
UNK:                         0
tokens/word reduction:       14.9298% vs native
```

For comparison, +8K measured 2.290673210 tokens/word and a 17.7654% reduction.

## Initialization

The +4K model starts from untouched `google/gemma-3-1b-pt`.

The 4,000 appended Oromo rows use the same selected initialization method as the
+8K experiment:

```text
native_subtoken_centroid_scaled_to_native_mean_l2_norm
```

Native model rows must remain unchanged. The existing image soft-token boundary
at ID 262,144 is preserved; Oromo additions occupy IDs 262,145–266,144.

## Stage A — pilot-equivalent CPT

Underlying text:

```text
training/data/oromocorpus-cpt-pilot-v0.1/train.jsonl
SHA-256:
9c71050faca4be2700ccbfb94737a8e8f190f3d9a3325b70fec60745c48b1a0a
```

Training policy:

```text
sequence length: 1024
epochs: 1
learning rate: 2e-5
weight decay: 0.1
warmup ratio: 0.03
microbatch: 1
gradient accumulation: 16
BF16: true
TF32: true
seed/data_seed: 42
```

Stage A output becomes the starting model for Stage B.

## Stage B — fresh v0.3 continuation

Underlying text:

```text
records: 146,038
words: 10,039,123
train SHA-256:
814f52575f4e4e38ff64b98b01bbe3837d17129cc2628d43cd8e571d1d2b298d
pilot exact-text overlap: 0
```

Training policy:

```text
sequence length: 1024
epochs: 1
learning rate: 1e-5
weight decay: 0.1
warmup ratio: 0.02
microbatch: 1
gradient accumulation: 16
BF16: true
TF32: true
seed/data_seed: 42
checkpoints: every 250 optimizer updates
```

The exact number of +4K optimizer updates is determined from the packed +4K
workload during local preflight. It is intentionally not forced to the +8K step
count because the primary control is **same underlying text exposure**.

## Evaluation protocol

Use the existing `training/tools/evaluate_bpb.py` and frozen
`document-bos-sliding-v1` protocol:

- same 1,503-record Oromo validation JSONL;
- context 1024;
- stride 512;
- one BOS conditioning token;
- no scored EOS;
- exact tokenizer round-trip;
- float logits;
- total NLL normalized by original UTF-8 bytes.

Evaluate Stage A final and all retained Stage B checkpoints.

Evaluate WikiText on the Stage B checkpoints used for final model selection.

## Predeclared interpretation

Primary endpoint:

> Exact Oromo BPB after the same two-stage underlying-text exposure.

Retention requirement:

```text
WikiText BPB <= 1.063917363
```

Reference lines:

```text
native CPT quality line: 1.733832395
+8K v0.3 quality line:    1.734823064
```

Interpretation rules:

- +4K below 1.733832395 and retention PASS: +4K beats both current quality
  references and becomes the strongest tokenizer/model candidate.
- +4K between 1.733832395 and 1.734823064 with retention PASS: +4K beats +8K
  quality while remaining slightly behind native CPT; its smaller vocabulary
  makes it a strong efficiency/quality candidate.
- +4K above 1.734823064 with retention PASS: compare the BPB deficit against
  its smaller vocabulary and measured token/runtime savings; do not force a
  winner without a Pareto tradeoff.
- Any checkpoint above the WikiText ceiling fails the retention gate.
- Raw Trainer loss is never used for cross-tokenizer ranking.

No single scalar score will combine BPB, runtime, token count, and vocabulary
size. The final tokenizer decision must report the Pareto tradeoff explicitly.

## Local prerequisites before GPU rental

Run, in order:

```bash
uv run python tokenizer/augmentation/build_gemma_oromo_4k.py
uv run python models/initialization/initialize_oromolm_gemma_4k.py
uv run python training/tools/prepare_cpt_packed_4k.py --dataset all
uv run python training/tools/preflight_oromolm_4k_ablation.py
```

Do not launch a GPU unless the last command prints:

```text
PREFLIGHT SUCCESS
```

---

## Execution status — 2026-10-14

Both predeclared training stages are now complete.

Stage A packed workload:

```text
training tokens:   4,964,141
packed sequences:  4,848
optimizer updates: 303
```

Stage A exact Oromo BPB:

```text
1.844463004
```

This is lower/better than the +8K Stage A reference of 1.863338883 by about 1.01%, but remains about 6.38% higher/worse than native-tokenizer CPT at 1.733832395.

Stage B also completed the full fresh v0.3 continuation:

```text
training tokens:   24,838,669
packed sequences:  24,257
optimizer updates: 1,517
retained steps:    250, 500, 750, 1000, 1250, 1500, 1517
```

The Stage B exact Oromo BPB curve and WikiText retention checks remain pending. Therefore the predeclared model-selection rules have **not yet been resolved** and no final +4K-vs-+8K winner is claimed.

The completed run was preserved locally under `preserved/4k-ablation-2026-10-14/`. The RunPod-generated integrity manifest verified **66 files with 0 failures**; preserved size is approximately **18 GB**.

See `docs/CPT_4K_ABLATION_RESULTS.md` for the current execution record.

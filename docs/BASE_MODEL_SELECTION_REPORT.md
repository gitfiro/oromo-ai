# OromoLM Base-Model and Tokenizer Selection Report

**Project:** Oromo AI  
**Phase:** 4C/4D — base-model, tokenizer, initialization, and first model-level proof  
**Status:** Gemma +8K validated as a training candidate; final production selection remains open  
**Last updated:** 2026-10-03

## 1. Current decision

The configuration that has now completed the first controlled OromoLM model-level proof is:

```text
Base model:
google/gemma-3-1b-pt

Tokenizer strategy:
native Gemma tokenizer
+ 8,000 cleaned leakage-safe Afaan Oromoo whole-word tokens

Initialization:
native subtoken centroid
scaled to native mean L2 norm

Experiment role:
first controlled native-vs-augmented CPT proof
```

The comparator is the untouched native Gemma tokenizer/model.

This is a **validated training candidate**, not a final OromoLM production decision.

The previous Qwen3-0.6B +4K plan recorded in an earlier version of this report was a provisional proof-stage engineering path before the cleaned-vocabulary freeze and later Gemma +8K initialization/CPT work. It is retained as historical context but is superseded for the completed pilot by the measured Gemma native-vs-+8K experiment.

## 2. Why Gemma is the current controlled-proof base

Gemma remains useful for the current controlled experiment because:

- it had the strongest native Oromo tokenization efficiency among the causal model families benchmarked;
- whole-word augmentation preserved all native token IDs while delivering a strong sequence-efficiency reduction;
- the 1B-class model remained inexpensive enough for short A100 experiments;
- tied embeddings permit deterministic vocabulary expansion without separate untied output-head growth;
- the native and augmented arms can be compared within the same architecture, eliminating base-model architecture as a confounder.

Native frozen-holdout benchmark:

```text
google/gemma-3-1b-pt
tokens/word:   2.7855
fragmentation: 85.91%
single-token:  14.09%
UNK:           0
```

The cleaned +8K candidate:

```text
tokens/word:   2.2907
fragmentation: 32.38%
single-token:  67.62%
UNK:           0
reduction:     17.77%
```

## 3. Cleaned +8K vocabulary freeze

The historical whole-word candidate pool contained extraction-concatenation artifacts, including internally mixed-case forms. The v2 cleaning gate rejects those forms before model-level vocabulary freeze.

Frozen candidate pool:

```text
tokenizer/augmentation/candidates/oromo_word_candidates.v2.cleaned.jsonl
```

SHA-256:

```text
7747fd5f230bcec779324138ac3cc0854f620f92a2284e8757135de3dabfd17f
```

Selected +8K ledger SHA-256:

```text
68ac896b2db54dece77eb677953d03c174b4100368d6da0e351a8b3cb72ae952
```

Frozen tokenizer artifact:

```text
tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-8k
```

Artifact hashes:

```text
tokenizer.json:
44f015312316d19ba8337a1807ca26d1a76e868ada0d709f2fb81c2ffce53806

tokenizer_config.json:
dd3333ae52ab7e8d543ca05cfbd0a1e483999e8d39b0b7e05e9b1fe60f26d926

benchmark result:
116189d283efae678de1339f9031bab8f7c3a78e47f46b03993929a1737073fb
```

## 4. Vocabulary/model boundary

Gemma's tokenizer and model have an important native boundary:

```text
native tokenizer length: 262,145
native model vocab rows: 262,144
token ID 262,144: <image_soft_token>
```

The augmented model was resized to:

```text
270,145 rows
```

with Oromo additions occupying:

```text
262,145–270,144
```

The existing token 262,144 was preserved rather than overwritten.

Input/output embeddings remained tied after resizing.

## 5. Embedding initialization decision

The project did not leave the 8,000 new Oromo rows at the default resize initialization without testing alternatives.

Behavioral audit on the top 128 additions:

| Strategy | Logit cosine | KL divergence | Top-20 overlap |
| --- | ---: | ---: | ---: |
| HF mean resize | 0.729729 | 10.189774 | 4.10% |
| Raw native-subtoken centroid | 0.867015 | 8.425408 | 20.62% |
| **Scaled native-subtoken centroid** | **0.880990** | **7.667944** | **25.23%** |

Selected initialization:

```text
native_subtoken_centroid_scaled_to_native_mean_l2_norm
```

Across all 8,000 additions:

```text
mean native pieces/word: 3.416
median native pieces:    3
native mean embedding norm: 1.046725
installed Oromo mean norm:  1.046723
```

Initialization manifest SHA-256:

```text
5c24eb839da903cbc4c58da365120856f44c352cfe941a9bd0bed529b04f9ac4
```

The initialized model passed a forward smoke test with logits shape `(1, 16, 270145)`.

## 6. Why +8K rather than +4K for the completed pilot

The earlier proof plan favored +4K as a conservative vocabulary-cost point. Later cleaned-candidate benchmarking and model initialization work established +8K as the stronger provisional training candidate.

On the frozen tokenizer holdout:

| Budget | Tokens/word | Reduction vs native | Fragmentation |
| --- | ---: | ---: | ---: |
| Native | 2.7855 | — | 85.91% |
| +4K cleaned | 2.3697 | 14.93% | 38.21% |
| **+8K cleaned** | **2.2907** | **17.77%** | **32.38%** |

The +8K model vocabulary is 270,145 rows, only about 3.05% larger than the native 262,144-row model vocabulary.

The decision was therefore to test whether the additional sequence savings survive real model training and whether the larger vocabulary creates unacceptable compute/VRAM cost.

## 7. Model-level evidence

The six-source CPT pilot provides that evidence.

Same-text training workload:

```text
native:    5,708,421 tokens / 5,575 packed sequences
Oromo +8K: 4,811,939 tokens / 4,700 packed sequences

token reduction: 15.70%
1024-sequence reduction: 15.70%
```

Controlled A100 full-pilot result:

| Metric | Native Gemma | Oromo +8K | Change |
| --- | ---: | ---: | ---: |
| Optimizer steps | 349 | **294** | **-15.76%** |
| Train wall time | 1,437.05 s | **1,176.71 s** | **-18.12%** |
| Total wall time | 1,450.93 s | **1,189.96 s** | **-17.99%** |
| Throughput | 3,972.59 tok/s | **4,090.03 tok/s** | **+2.96%** |
| Peak allocated VRAM | 10.60 GiB | 10.77 GiB | +1.60% |
| Peak reserved VRAM | 12.21 GiB | 12.55 GiB | +2.78% |

The +8K vocabulary therefore passed its first model-level compute test: the larger vocabulary did not erase sequence-length savings.

## 8. Quality gate

Raw final eval losses were:

```text
native:    3.265455
Oromo +8K: 4.115734
```

These must not be compared directly because the tokenizations differ.

Using the exact validation text size and an approximate reconstruction from Trainer aggregate loss and causal-shift scored-token counts:

```text
validation records: 1,503
characters:         805,382
UTF-8 bytes:        814,153

reconstructed native BPB:    ~1.71377
reconstructed Oromo +8K BPB: ~1.82059
relative NLL/byte gap:       ~6.23% higher for +8K
```

This means the first short pilot demonstrates a compute advantage but does **not** establish model-quality parity.

The BPB figures are reconstructed rather than produced by a dedicated summed-NLL evaluator. Exact byte-normalized evaluation remains a required gate.

## 9. Current selection state

### Validated

```text
Gemma native tokenizer:
valid baseline

Gemma +8K whole-word tokenizer:
validated training candidate

generic internal AddedToken subword injection:
rejected

full tokenizer replacement:
deferred
```

### Still open

- final production tokenizer;
- final OromoLM base model;
- whether +8K quality catches native Gemma with additional CPT;
- whether +4K gives a better eventual quality/compute frontier;
- whether another base family should be reintroduced after this controlled proof;
- catastrophic-forgetting behavior;
- exact BPB and source-level model likelihood.

## 10. Next gate

The next sequence is:

```text
completed Gemma native-vs-+8K pilot
      ↓
exact summed-NLL / BPB evaluator
      ↓
longer +8K continued pretraining
      ↓
quality-gap trajectory + forgetting controls
      ↓
OromoBench / source-level evaluation
      ↓
decide whether to:
    retain Gemma +8K
    compare Gemma +4K
    revisit another base family
    or revise tokenizer strategy
```

No scaled production CPT or instruction tuning should be justified solely by the current efficiency result.

The complete experiment is documented in `docs/CPT_PILOT_REPORT.md`.

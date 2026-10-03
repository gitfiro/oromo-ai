# OromoLM Gemma +8K Continued-Pretraining Pilot Report

**Project:** Oromo AI  
**Component:** OromoLM / OromoTokenizer  
**Experiment family:** `oromocorpus-cpt-pilot-v0.1`  
**Base model:** `google/gemma-3-1b-pt`  
**Comparison:** native Gemma tokenizer vs frozen Gemma +8K Oromo whole-word augmentation  
**Run date:** 2026-10-03  
**Status:** completed controlled pilot; efficiency benefit verified; quality-equivalence not yet established

---

## 1. Purpose

This report freezes the first controlled model-level continued-pretraining (CPT) evidence for the Oromo AI project.

The experiment asks two separate questions:

1. Does the frozen Gemma +8K Oromo lexical augmentation materially reduce training workload and measured GPU time on the same underlying Afaan Oromoo text?
2. After a short one-epoch pilot, does the augmented model recover language-model quality comparable to native Gemma when evaluation is normalized by the same underlying text?

The experiment is deliberately a pilot. It does **not** establish a production OromoLM release, a final tokenizer, or a final scaling recipe.

---

## 2. Configuration under test

### Native arm

```text
model:      google/gemma-3-1b-pt
tokenizer:  google/gemma-3-1b-pt
model vocab rows: 262,144
tokenizer length: 262,145
```

Gemma exposes one tokenizer-side ID beyond the native model vocabulary:

```text
token ID 262,144 = <image_soft_token>
```

The trainer explicitly audited this off-by-one boundary and treated it as safe.

### Oromo +8K arm

Frozen tokenizer artifact:

```text
tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-8k
```

Configuration:

```text
augmentation type: whole-word lexical
AddedToken.single_word: true
AddedToken.normalized: true
added Oromo tokens: 8,000
native tokenizer length: 262,145
final tokenizer/model vocabulary: 270,145
Oromo token ID range: 262,145–270,144
model vocabulary growth: 3.0521%
```

The existing `<image_soft_token>` boundary row at ID 262,144 was preserved. Oromo additions start at ID 262,145.

Frozen tokenizer benchmark on the 10K tokenizer holdout:

| Metric | Native Gemma | Gemma +8K |
| --- | ---: | ---: |
| Tokens/word | 2.7855 | **2.2907** |
| Word fragmentation | 85.91% | **32.38%** |
| Single-token words | 14.09% | **67.62%** |
| Unknown tokens | 0 | 0 |
| Tok/word reduction | — | **17.77%** |

Important artifact hashes:

```text
clean candidate pool SHA-256:
7747fd5f230bcec779324138ac3cc0854f620f92a2284e8757135de3dabfd17f

selected-token ledger SHA-256:
68ac896b2db54dece77eb677953d03c174b4100368d6da0e351a8b3cb72ae952

benchmark result SHA-256:
116189d283efae678de1339f9031bab8f7c3a78e47f46b03993929a1737073fb

tokenizer.json SHA-256:
44f015312316d19ba8337a1807ca26d1a76e868ada0d709f2fb81c2ffce53806

tokenizer_config.json SHA-256:
dd3333ae52ab7e8d543ca05cfbd0a1e483999e8d39b0b7e05e9b1fe60f26d926
```

---

## 3. New-embedding initialization

The augmented model was resized from 262,144 native model rows to 270,145 rows with tied input/output embeddings preserved.

Three initialization strategies were behaviorally audited on the top 128 ranked additions:

| Initialization | Logit cosine | KL divergence | Top-20 overlap |
| --- | ---: | ---: | ---: |
| Hugging Face mean resize | 0.729729 | 10.189774 | 4.10% |
| Raw native-subtoken centroid | 0.867015 | 8.425408 | 20.62% |
| **Scaled native-subtoken centroid** | **0.880990** | **7.667944** | **25.23%** |

The selected strategy for `OromoLM v0.1` initialization is:

```text
native_subtoken_centroid_scaled_to_native_mean_l2_norm
```

Subtoken decomposition across all 8,000 additions averaged 3.416 native pieces per added word, with a median of 3.

Embedding norms:

```text
native mean embedding norm:       1.046725
HF mean-resize new-row norm:      ~0.256923
installed Oromo mean-row norm:    1.046723
```

The initialized model passed a forward smoke test with logits shape:

```text
(1, 16, 270145)
```

Initialization manifest SHA-256 recorded during the experiment:

```text
5c24eb839da903cbc4c58da365120856f44c352cfe941a9bd0bed529b04f9ac4
```

The initialized weights are training artifacts and are not required to be stored directly in Git.

---

## 4. CPT pilot corpus

The CPT pilot draws from all six accepted OromoCorpus source families and uses deterministic source-scoped SHA-256 record ordering.

Selection policy:

```text
target train:       2,000,000 whitespace words
target validation:    100,000 whitespace words
validation selected before train
tokenizer-independent source selection
zero train/validation record overlap
```

### Training split

| Source | Records | Words |
| --- | ---: | ---: |
| AfriBERTa Oromo v0.1.2 | 23,587 | 394,560 |
| Wikimedia omwiki v0.1 | 155 | 35,342 |
| VOA Afaan Oromoo via WURA v0.1 | 529 | 76,723 |
| WaxalNLP Oromo ASR | 2,529 | 79,545 |
| MADLAD-400 Oromo v0.2 | 1,076 | 635,730 |
| HPLT3 gaz_Latn v0.1 | 1,501 | 779,261 |
| **Total** | **29,377** | **2,001,161** |

Training characters:

```text
15,539,012
```

Training SHA-256:

```text
9c71050faca4be2700ccbfb94737a8e8f190f3d9a3325b70fec60745c48b1a0a
```

### Validation split

| Source | Records | Words |
| --- | ---: | ---: |
| AfriBERTa Oromo v0.1.2 | 1,179 | 19,728 |
| Wikimedia omwiki v0.1 | 13 | 3,438 |
| VOA Afaan Oromoo via WURA v0.1 | 27 | 3,968 |
| WaxalNLP Oromo ASR | 130 | 3,988 |
| MADLAD-400 Oromo v0.2 | 45 | 32,310 |
| HPLT3 gaz_Latn v0.1 | 109 | 39,386 |
| **Total** | **1,503** | **102,818** |

Exact validation text measurements used for later normalization:

```text
characters:       805,382
UTF-8 bytes:      814,153
whitespace words: 102,818
```

Validation SHA-256:

```text
cd1872643749992c7d4e22dad9b7dbe34907f0a5f96204c3040d428fc749a3d8
```

Pilot manifest SHA-256 recorded at freeze:

```text
7791a25fe9f0bca389b7db71709685e5dce8fbd4effc7ee7b16e8aa87d8ee399
```

---

## 5. Dual-tokenizer compute audit

Tokenization used `add_special_tokens=false` with exactly one EOS token counted per source record.

### Training workload

| Metric | Native | Oromo +8K | Change |
| --- | ---: | ---: | ---: |
| Tokens including EOS | 5,708,421 | **4,811,939** | **-15.70%** |
| Tokens/word | 2.8526 | **2.4046** | lower |
| Characters/token | 2.7221 | **3.2293** | +18.63% text capacity |
| 1024-token packed sequences | 5,575 | **4,700** | **-15.70%** |

Per-source train token reduction:

| Source | Reduction |
| --- | ---: |
| AfriBERTa | 17.46% |
| MADLAD | 14.01% |
| Waxal | 17.28% |
| HPLT3 | 16.08% |
| VOA | 16.58% |
| omwiki | 13.90% |

The efficiency gain is therefore broad across all six source families, not driven by a single corpus.

### Validation workload

| Metric | Native | Oromo +8K | Change |
| --- | ---: | ---: | ---: |
| Tokens including EOS | 296,460 | **249,875** | **-15.71%** |
| Tokens/word | 2.8833 | **2.4303** | lower |
| Characters/token | 2.7167 | **3.2231** | +18.64% text capacity |
| 1024-token packed sequences | 290 | **245** | -15.52% |

Compute-audit SHA-256:

```text
3ca992ece1cb56dcdaf436b5e1f4b8f8c720461df4d214d3bd54640081f3af98
```

---

## 6. Packed datasets

Packing policy:

```text
concatenate document tokenizations
+ exactly one EOS separator per source record
+ fixed blocks of 1024
+ retain final partial block
+ discard no text
```

### Native

```text
train sequences: 5,575
train tokens:    5,708,421
final partial:   645
train SHA-256:
8c85b2b35145c9a65439816d7b61382258eec3d184505b4739fb2cc2088961e1

validation sequences: 290
validation tokens:    296,460
final partial:        524
validation SHA-256:
82e7b46b9a7f97e8729e89b482d252b44a3272d52683ccf633eba84647983525

manifest SHA-256:
c726cadcc75ed28ad44a26d643e653fab3e63e961e508108bd961ef06fd009e8
```

### Oromo +8K

```text
train sequences: 4,700
train tokens:    4,811,939
final partial:   163
train SHA-256:
aa5183850ad2f93300ec7ca691349e26f47d428144cbf07de971b5439b11bb51

validation sequences: 245
validation tokens:    249,875
final partial:        19
validation SHA-256:
abb452f63a504884a875b7989fd31b34e4da5c6edfaa9cbf622ecc9cfb6c80dc

manifest SHA-256:
9d0c6a89268ae644fa6cf1e1615e65e6f6ebabab496742bf5bb8674fbb1a6977
```

---

## 7. Training configuration

Both full arms used the same training policy except for tokenizer/model artifact and the resulting number of packed sequences:

```text
sequence length:             1024
epochs:                      1
learning rate:               2e-5
weight decay:                0.1
warmup ratio:                0.03
microbatch:                  1
eval batch:                  1
gradient accumulation:       16
gradient checkpointing:      true
bf16:                        true
seed:                        42
data seed:                   42
optimizer:                   adamw_torch_fused
LR schedule:                 cosine
```

The primary comparison is **same underlying text exposure**, not matched optimizer-step count.

Consequently:

```text
native planned optimizer steps:    349
Oromo +8K planned optimizer steps: 294
```

This difference is intentional: fewer Oromo +8K steps are part of the measured end-to-end efficiency effect produced by representing the same text with fewer tokens.

---

## 8. GPU environment

The controlled full-pilot comparison was run on the same RunPod instance class:

```text
GPU:               NVIDIA A100-SXM4-80GB
VRAM:              81,920 MiB reported by nvidia-smi
Python:            3.12.3
PyTorch:           2.8.0+cu128
CUDA available:    true
BF16 supported:    true
compute capability: 8.0
```

During the final RunPod session, `nvidia-smi` reported driver 595.91.07 and CUDA compatibility 13.2. PyTorch itself was the CUDA 12.8 build.

The Hugging Face Gemma repository is gated, so the RunPod environment required authentication with an account that had accepted the Gemma access terms.

### Transformers 5.17 compatibility

The training script encountered two API compatibility changes in `TrainingArguments`:

- `overwrite_output_dir` was not accepted and was removed;
- `warmup_ratio` was translated at construction time to the v5.17 `warmup_steps` behavior while preserving the configured 0.03 ratio semantics.

These were infrastructure compatibility fixes, not changes to the intended experimental comparison.

---

## 9. Smoke-test results

Ten optimizer-step smoke tests were run before the full pilots.

| Metric | Native | Oromo +8K |
| --- | ---: | ---: |
| Optimizer steps | 10 | 10 |
| Input tokens | 163,840 | 163,840 |
| Train wall time | 39.88 s | **37.44 s** |
| Eval wall time | 12.57 s | **12.29 s** |
| Total wall time | 52.45 s | **49.73 s** |
| Throughput | 4,108.80 tok/s | **4,375.96 tok/s** |
| Peak allocated VRAM | 10.60 GiB | 10.76 GiB |
| Peak reserved VRAM | 12.21 GiB | 12.55 GiB |
| Raw eval loss | 4.516767 | 6.412447 |

Run-summary SHA-256:

```text
native:
88f99b776061d0ec6e3fae0161f4bc884b2c141ff934b97a41119d67cb90ce38

Oromo +8K:
ae211922fb9e1e879e0057c52a02302e3bf8c14e34f00736dfff088ca3c08cd1
```

The smoke tests established that both arms were stable and that the augmented vocabulary did not cause an OOM or substantial VRAM penalty.

---

## 10. Full-pilot results

### Native Gemma

```text
experiment:            gemma-native-cpt-pilot-v0.1
train wall time:       1,437.05 s
eval wall time:           13.88 s
total wall time:       1,450.93 s
peak allocated VRAM:      10.60 GiB
peak reserved VRAM:       12.21 GiB
training throughput:   3,972.59 tokens/s
final raw eval loss:       3.265455
```

Run-summary SHA-256:

```text
8a086e9af415879121c109e7d7e83dc141f49c993e6b1a88d7de0b213c99f124
```

### Oromo +8K

```text
experiment:            oromolm-8k-cpt-pilot-v0.1
train wall time:       1,176.71 s
eval wall time:           13.25 s
total wall time:       1,189.96 s
peak allocated VRAM:      10.77 GiB
peak reserved VRAM:       12.55 GiB
training throughput:   4,090.03 tokens/s
final raw eval loss:       4.115734
```

Run-summary SHA-256:

```text
a74579cdaf438c62931d98be3b9e0a4a528732275747eb6b47cd3108a8dbb690
```

### Controlled comparison

| Metric | Native Gemma | Oromo +8K | Difference |
| --- | ---: | ---: | ---: |
| Training tokens | 5,708,421 | **4,811,939** | **-15.70%** |
| Optimizer steps | 349 | **294** | **-15.76%** |
| Train wall time | 1,437.05 s | **1,176.71 s** | **-18.12%** |
| Total wall time | 1,450.93 s | **1,189.96 s** | **-17.99%** |
| Throughput | 3,972.59 tok/s | **4,090.03 tok/s** | **+2.96%** |
| Peak allocated VRAM | 10.60 GiB | 10.77 GiB | +1.60% |
| Peak reserved VRAM | 12.21 GiB | 12.55 GiB | +2.78% |

### Efficiency conclusion

The +8K vocabulary did **not** erase the sequence-length savings through a larger embedding/output vocabulary.

On the same A100 and same underlying pilot text:

- token workload fell by 15.70%;
- optimizer-step count fell by 15.76%;
- measured training wall time fell by 18.12%;
- total run wall time fell by 17.99%;
- token throughput increased by 2.96%;
- reserved VRAM increased by only 0.34 GiB.

This is positive model-level evidence for the engineering value of the frozen +8K tokenizer.

---

## 11. Interrupted Oromo run and storage incident

The first full Oromo +8K attempt reached step 200/294 successfully and completed the scheduled evaluation at that point:

```text
eval_loss: 4.114
num_input_tokens_seen: 3,276,800
```

It then failed while serializing the step-200 checkpoint:

```text
safetensors.SafetensorError:
I/O error: No space left on device (os error 28)
```

This was a storage failure, not a model-training failure.

The 30 GB RunPod overlay contained approximately 12 GB of native intermediate checkpoints in addition to model artifacts. Those intermediate checkpoints were removed after the completed native run.

For the clean Oromo rerun, intermediate checkpoint saving was disabled while all scientific training settings were kept unchanged. The failed partial Oromo run directory was removed, and the full 294-step Oromo pilot was rerun from step 0 uninterrupted. The measurements in Section 10 are from that clean rerun.

This incident should be retained in the experiment record because checkpoint storage requirements are part of operational reproducibility.

---

## 12. Cross-tokenizer quality interpretation

Raw token-level losses are **not directly comparable** across different tokenizers because the unit being averaged is different.

Therefore:

```text
native raw eval loss: 3.265455
Oromo raw eval loss:  4.115734
```

must not be interpreted as a direct quality ratio.

### Reconstructed normalized likelihood

The exact frozen validation text contains:

```text
1,503 records
805,382 characters
814,153 UTF-8 bytes
102,818 whitespace words
```

For an approximate reconstruction from Trainer aggregate loss, the causal shift removes the first prediction position of each packed sequence:

```text
native approximate scored tokens:
296,460 - 290 = 296,170

Oromo +8K approximate scored tokens:
249,875 - 245 = 249,630
```

Using:

```text
total NLL ≈ eval_loss × scored_tokens
```

produces:

| Metric | Native | Oromo +8K |
| --- | ---: | ---: |
| Reconstructed total NLL | ~967,129.81 | ~1,027,410.68 |
| NLL / character | ~1.20083 | ~1.27568 |
| NLL / UTF-8 byte | ~1.18790 | ~1.26194 |
| Reconstructed bits/byte | ~1.71377 | ~1.82059 |

On this reconstruction, Oromo +8K is approximately **6.23% higher/worse in NLL per byte** after one pilot epoch.

### Methodological limitation

These are **reconstructed normalized metrics**, not the output of a dedicated unreduced-NLL evaluator.

For publication-quality comparison, the project should run a dedicated evaluator that:

1. uses the exact same underlying validation records;
2. explicitly sums unreduced negative log-likelihood over valid predicted positions;
3. records exact scored-token counts;
4. normalizes by characters and UTF-8 bytes;
5. reports bits per byte;
6. reports per-source results;
7. preserves an evaluation manifest and hashes.

Until that evaluator exists, the ~6.23% figure is useful pilot evidence but must not be presented as an exact final BPB benchmark.

---

## 13. Current decision

The model-level pilot changes the project decision state.

### Established

- Gemma +8K whole-word augmentation is operationally compatible with the pretrained model.
- The 8,000 new embeddings can be initialized deterministically without breaking tied embeddings.
- The tokenizer reduces token workload broadly across all six accepted source families.
- The larger vocabulary produces only a small VRAM increase in this setup.
- The measured end-to-end training-time reduction is substantial: approximately 18% on this pilot.
- A single short CPT epoch is **not yet enough** to establish quality parity with native Gemma under reconstructed byte-normalized likelihood.

### Not established

- that +8K is the final production tokenizer;
- that the reconstructed ~6.23% normalized-likelihood gap persists after additional CPT;
- that +8K is superior to +4K under model-level quality/compute tradeoffs;
- that Gemma is the final OromoLM release base;
- that the pilot result generalizes to longer sequence lengths or different GPU classes;
- that raw token-level perplexity can be compared across the two tokenizers.

### Provisional research decision

Retain Gemma +8K as a **validated training candidate** because its compute benefit is now demonstrated at model level, but do not freeze it as the final OromoLM production tokenizer until additional CPT and exact normalized evaluation test whether the quality gap closes.

---

## 14. Next experiments

Before scaled CPT:

1. implement an exact summed-NLL / bits-per-byte evaluator;
2. reproduce native and +8K normalized validation metrics with that evaluator;
3. run a longer controlled Oromo +8K CPT experiment to measure adaptation of the newly added embeddings;
4. evaluate whether the normalized quality gap narrows with additional text exposure;
5. include a general-language control set to quantify catastrophic forgetting;
6. add source-level normalized likelihood for all six corpus families;
7. consider a +4K model-level ablation only if it materially informs the quality/compute frontier;
8. preserve all configs, manifests, hashes, runtime environment metadata, and run summaries.

The project should not scale training solely because the tokenizer is faster. The next gate is evidence that the augmented vocabulary can retain or recover model quality while preserving the measured compute advantage.

---

## 15. Reproducibility index

Primary repository artifacts:

```text
training/train_cpt.py

training/configs/gemma-native-cpt-smoke-v0.1.json
training/configs/oromolm-8k-cpt-smoke-v0.1.json
training/configs/gemma-native-cpt-pilot-v0.1.json
training/configs/oromolm-8k-cpt-pilot-v0.1.json

training/tools/dual_tokenizer_compute_audit.py
training/tools/prepare_cpt_packed.py

training/reports/oromocorpus-cpt-pilot-v0.1/
  dual_tokenizer_compute_audit.json

tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-8k/
tokenizer/augmentation/candidates/oromo_word_candidates.v2.cleaned.jsonl
tokenizer/augmentation/results_word_v3/
```

Large model weights, local RunPod checkpoints, raw/interim training data, and temporary archives are intentionally not required to be committed to Git. Their reproducibility should instead be anchored by configuration, provenance, deterministic generation procedures, and SHA-256 manifests.

---

## 16. Summary

The first controlled OromoLM CPT pilot produced a clear engineering result and a clear research caution.

```text
Efficiency:
+8K reduces training token workload by ~15.70%
+8K reduces measured training wall time by ~18.12%
+8K adds only a small VRAM penalty

Quality:
raw token losses are not cross-tokenizer comparable
reconstructed normalized NLL/byte currently favors native Gemma by ~6.23%
exact BPB evaluation is still required
```

The evidence therefore supports continued investigation of Gemma +8K, not premature finalization.

**Project principle remains: Data before model. Evidence before scale.**

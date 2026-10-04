# OromoLM CPT Reproduction v0.2 — Exact Oromo BPB Results

## Status

**Completed: 2026-10-04**

This report records the reproducibility rerun and exact byte-normalized evaluation of three Gemma/OromoLM model states on the same frozen Afaan Oromoo validation set.

The principal result is now model-quality evidence, not only tokenizer efficiency:

- continued pretraining (CPT) on OromoCorpus substantially improves the original Gemma base model on held-out Afaan Oromoo;
- the current Gemma +8K OromoLM candidate also substantially improves over the untouched base model;
- after one CPT epoch, the +8K candidate does **not yet** match the native-tokenizer CPT model under exact document-reset bits-per-byte (BPB).

Lower BPB is better.

## Frozen validation set

```text
records:          1,503
characters:       805,382
UTF-8 bytes:      814,153
whitespace words: 102,818
SHA-256:          cd1872643749992c7d4e22dad9b7dbe34907f0a5f96204c3040d428fc749a3d8
```

Evaluation protocol:

```text
protocol: document-bos-sliding-v1
context:  1024 tokens
stride:   512 tokens
EOS scored: false
document context reset: true
exact text round-trip required: true
normalization: exact summed causal NLL / original UTF-8 bytes
```

The evaluator is `training/tools/evaluate_bpb.py`. Its protocol tests are in `tests/training/test_bpb_protocol.py`.

## Three-way exact Oromo comparison

| Model state | Scored tokens | NLL / byte | BPB | Relative BPB vs base |
| --- | ---: | ---: | ---: | ---: |
| Original `google/gemma-3-1b-pt` | 294,957 | 1.850734532 | **2.670045532** | baseline |
| Native tokenizer + Oromo CPT | 294,957 | 1.201801036 | **1.733832395** | **-35.06%** |
| OromoLM +8K + Oromo CPT | 248,372 | 1.291568093 | **1.863338883** | **-30.21%** |

The +8K CPT model is approximately **7.47% higher/worse in BPB than native-tokenizer CPT** after this one-epoch experiment.

This replaces the earlier reconstructed normalized-likelihood estimate as the authoritative exact comparison for these rerun checkpoints.

## Per-source exact BPB

| Source | Base Gemma | Native CPT |
| --- | ---: | ---: |
| AfriBERTa Oromo v0.1.2 | 3.297737842 | **2.069977429** |
| MADLAD-400 Oromo v0.2 | 2.492631374 | **1.647904061** |
| WaxalNLP Oromo ASR v2 | 2.836827372 | **1.772029955** |
| HPLT3 gaz_Latn v0.1 | 2.531257643 | **1.640244503** |
| VOA Afaan Oromoo via WURA v0.1 | 2.586988131 | **1.773451274** |
| Wikimedia omwiki v0.1 | 2.393665083 | **1.671916637** |

Native-tokenizer Oromo CPT improved over untouched Gemma on every represented source family. The exact +8K per-source table should be preserved from the generated BPB JSON report when that result artifact is committed locally in the next session.

## Reproduction training environment

The v0.2 rerun used:

```text
GPU: NVIDIA RTX A6000
VRAM: 47.40 GiB
Python: 3.12.3
PyTorch: 2.14.0+cu130
CUDA available: true
BF16 supported: true
compute capability: 8.6
```

This differs from the earlier A100 pilot. Timing results from this rerun must therefore not be presented as a direct replacement for the controlled A100 18.12% wall-time result.

### Native CPT rerun

```text
experiment: gemma-native-cpt-rerun-v0.2
optimizer steps: 349
train wall time: 1518.6804 s
eval wall time: 16.3905 s
total wall time: 1535.0708 s
peak allocated VRAM: 10.6027 GiB
peak reserved VRAM: 12.2148 GiB
reported Trainer input tokens: 5,708,800
throughput: 3,759.05 tok/s
run-summary SHA-256:
b1e83673743b0e7af4d220fa05446d436316d3078a9d670a4471f743d694c23f
```

### OromoLM +8K CPT rerun

```text
experiment: oromolm-8k-cpt-rerun-v0.2
optimizer steps: 294
train wall time: 1391.55 s
eval wall time: 16.82 s
total wall time: 1408.37 s
peak allocated VRAM: 10.76 GiB
peak reserved VRAM: 11.96 GiB
throughput: 3,458.59 tok/s
final raw eval loss: 4.108630
run-summary SHA-256:
e2864d3c02c022d5a059b6496cffefce913e87374373daab2459d2ff2b272e28
```

On this A6000 rerun, +8K used approximately **8.37% less training wall time** than the native-tokenizer arm. Because hardware/runtime conditions differ from the original A100 pilot, this is supporting evidence only; the controlled A100 result remains the primary efficiency measurement.

## Preserved local artifact archive

The completed rerun was exported before RunPod termination.

```text
archive:
oromolm-cpt-results-v0.2.tar

local/export SHA-256:
4ee25bd22cdd895918307cae5c9a23a54d08322dc0116960132557730f2ea9c4

approximate archive size:
3.9 GB
```

The archive contains:

- native CPT final model;
- OromoLM +8K CPT final model;
- run summaries;
- preflight manifests;
- training logs;
- all three exact BPB reports;
- environment metadata;
- internal SHA-256 manifest.

Large model weights and the archive are intentionally not committed to normal Git.

## Current scientific conclusion

The project can now state reproducibly:

> Continued pretraining on the frozen OromoCorpus pilot substantially improves Gemma's modeling of held-out Afaan Oromoo text.

Exact BPB fell from **2.670046** for untouched Gemma to **1.733832** after native-tokenizer Oromo CPT, a **35.06% reduction**.

The +8K OromoLM candidate reached **1.863339 BPB**, a **30.21% reduction** relative to untouched Gemma, while retaining the previously demonstrated sequence-efficiency advantage. However, after one epoch it remains approximately **7.47% behind the native-tokenizer CPT model in BPB**.

Therefore:

- OromoCorpus + CPT is validated as an effective adaptation path;
- +8K remains a valid efficiency-oriented training candidate;
- +8K is not yet the leading quality checkpoint;
- tokenizer selection remains open.

## Next gate

The next experiment should measure a controlled OromoLM +8K learning curve rather than immediately redesigning the tokenizer.

Planned gate:

1. freeze a separate general-language control set;
2. define an acceptable forgetting threshold before inspecting results;
3. continue training from the preserved +8K CPT checkpoint in bounded increments;
4. run exact Oromo BPB at each checkpoint;
5. run the general-language control at each checkpoint;
6. determine whether +8K crosses below the current native-CPT benchmark of **1.733832 BPB**;
7. consider the +4K ablation if +8K plateaus above the native-CPT frontier.

The quality milestone worth celebrating next is:

> **OromoLM +8K beats native-tokenizer Oromo CPT on the same frozen Oromo validation text while retaining acceptable general-language behavior.**

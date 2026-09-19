# Oromo AI Evaluation Framework

## Purpose

Evaluation in Oromo AI is designed to prevent progress from being judged by fluent-looking examples alone.

This framework evaluates the named project layers: **OromoCorpus** integrity, **OromoTokenizer** efficiency and adaptation, **OromoLM** capability, and the future **OromoBench** suite.

Every major research layer should have a fixed, reproducible evaluation protocol before optimization begins.

Current evaluation layers:

```text
OromoCorpus integrity
      ↓
OromoTokenizer efficiency
      ↓
Base-model language ability
      ↓
Continued-pretraining gains
      ↓
Instruction following
      ↓
OromoBench
```

---

## 1. Corpus validation

The current production corpus is:

```text
afriberta_oromo_v0.1.2
```

Processed SHA-256:

```text
6f990088c8fb319b46c9a25a1c463e7a700cc8d292da781cfcc44ac4391ee0f6
```

Current validation invariants include:

- manifest record count matches output;
- character totals match;
- no malformed JSON;
- no empty processed records;
- no duplicate cleaned hashes;
- unique source-line accounting;
- rejection/deduplication accounting is exact.

Corpus quality and statistics are documented separately in:

- `docs/CORPUS_QUALITY_REPORT.md`
- `docs/CORPUS_STATISTICS_REPORT.md`

---

## 2. Tokenizer evaluation

### Canonical holdout

Tokenizer evaluation uses the frozen sample:

```text
tokenizer/evaluation/samples/afriberta_oromo_v0.1.2_n10000.jsonl
```

Records:

```text
10,000
```

Sampling seed:

```text
20260919
```

SHA-256:

```text
369c4438beab0d619336448eab7e27aae29d0722fd089088dbf0b2addc3d81f5
```

The sample contains 10,000 unique record IDs and 10,000 unique texts.

It is excluded from custom tokenizer training by stable `record_id`.

### Training/evaluation split

```text
Production records:        410,193
Tokenizer training:        400,193
Tokenizer evaluation:       10,000
Evaluation leakage:              0
```

Tokenizer training corpus SHA-256:

```text
a733419e61ed4751e7f4da950e8c05c893ecbbc63be12c1551a1493507162dff
```

### Metrics

Tokenizer comparisons record:

- vocabulary size;
- total tokens;
- tokens per whitespace-delimited word;
- characters per token;
- UTF-8 bytes per token;
- fragmented-word rate;
- single-token-word rate;
- unaligned words;
- unknown-token count/rate;
- sample tokenizations;
- software versions;
- model and corpus provenance where applicable.

The word accounting invariant is:

```text
fragmented + single-token + unaligned = total words
```

### Current benchmark

#### Custom and multilingual references

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oromo-unigram-48k-byte | 48,000 | **1.4000** | **38.75%** | **61.25%** | 0 | 5.4562 |
| oromo-unigram-32k-byte | 32,000 | 1.4495 | 40.83% | 59.17% | 0 | 5.2699 |
| castorini/afriberta_base | 70,006 | 1.6765 | 39.83% | 60.16% | 0 | 4.5563 |
| xlm-roberta-base | 250,002 | 2.6091 | 81.03% | 18.97% | 3 | 2.9278 |
| bert-base-multilingual-cased | 119,547 | 2.8696 | 87.36% | 12.63% | 5,423 | 2.6620 |

#### Native causal-LM tokenizers

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| google/gemma-3-1b-pt | 262,144 | **2.7855** | **85.91%** | **14.09%** | 0 | **2.7423** |
| Qwen/Qwen3.5-0.8B-Base | 248,044 | 2.9191 | 86.94% | 13.06% | 0 | 2.6169 |
| meta-llama/Llama-3.2-1B | 128,000 | 3.0311 | 88.32% | 11.68% | 0 | 2.5202 |
| Qwen/Qwen3-0.6B-Base | 151,643 | 3.0713 | 88.89% | 11.11% | 0 | 2.4872 |
| mistralai/Mistral-7B-v0.3 | 32,768 | 3.3241 | 93.09% | 6.91% | 0 | 2.2980 |

The native causal tokenizers all provide Unicode coverage on this holdout, but sequence inflation and word fragmentation are consistently high for Afaan Oromoo.

#### Whole-word augmentation feasibility

Vocabulary augmentation preserves the original tokenizer IDs and appends selected Oromo lexical tokens. Candidate ranking uses only the leakage-safe tokenizer-training split and optimizes:

```text
frequency × (native_pieces - 1)
```

Frozen-holdout results:

| Base tokenizer | Native | +2K | +4K | +8K | +16K |
| --- | ---: | ---: | ---: | ---: | ---: |
| Llama 3.2 1B | 3.0311 | 2.5705 | 2.4715 | 2.3716 | **2.2821** |
| Qwen3 0.6B | 3.0713 | 2.6063 | 2.5058 | 2.4049 | **2.3140** |
| Gemma 3 1B | 2.7855 | 2.4475 | 2.3692 | 2.2903 | **2.2172** |

At +4K, fragmentation falls to 38.19% for Llama, 38.70% for Qwen3, and 38.21% for Gemma—close to the 38.75% custom 48K reference. Token-per-word efficiency remains materially worse than the custom tokenizer, so fragmentation and sequence efficiency must be evaluated separately.

Full tokenizer methodology and all candidate results are documented in:

`docs/TOKENIZER_RESEARCH_REPORT.md`

---

## 3. Tokenizer decision criteria

The final tokenizer decision must not be based on tokens/word alone.

The decision should consider:

1. Oromo sequence efficiency;
2. word fragmentation;
3. unknown-token behavior;
4. vocabulary size;
5. embedding/output-layer parameter cost;
6. compatibility with the selected causal base model;
7. cost of vocabulary augmentation or tokenizer replacement;
8. continued-pretraining stability.

The current 32K-byte and 48K-byte tokenizers are OromoTokenizer research references, not yet final production choices.

---

## 4. Causal-LM tokenizer and augmentation evaluation

Native causal-tokenizer benchmarking is complete for the current candidate set, and Phase 4B1 has established that whole-word vocabulary augmentation can recover a large amount of Oromo word-level efficiency without replacing the original tokenizer.

Current evidence supports three conclusions:

1. native causal tokenizers are lossless on the frozen holdout but inefficient for Oromo;
2. 2K–4K high-value lexical additions produce the largest early gains;
3. whole-word augmentation alone does not recover the strongest OromoTokenizer candidate's token-per-word efficiency.

The next tokenizer decision should compare:

```text
native tokenizer
      vs
whole-word augmentation
      vs
Oromo subword augmentation
      vs
full tokenizer replacement
```

Before any model weights are modified, the project should quantify diminishing returns, vocabulary/embedding parameter cost, and whether subword augmentation closes the remaining sequence-efficiency gap.

---

## 5. Tiny CPT proof evaluation

Before scaling model size, the first continued-pretraining proof should evaluate:

- held-out Oromo loss/perplexity;
- catastrophic forgetting on a small general-language control set;
- Oromo completion quality;
- Oromo spelling/orthographic behavior;
- morphology-sensitive examples;
- context utilization;
- training stability;
- checkpoint reproducibility.

The first OromoLM proof exists to validate the pipeline, not to maximize benchmark headlines.

---

## 6. OromoBench direction

OromoBench will eventually separate several abilities rather than collapsing them into one score.

### Language

- spelling;
- vocabulary;
- morphology;
- grammar;
- sentence completion;
- reading comprehension;
- paraphrasing;
- summarization.

### Translation

- Oromo → English;
- English → Oromo;
- Oromo ↔ additional languages where reliable data exists.

### Reasoning

- basic reasoning;
- arithmetic;
- multi-step instructions;
- structured extraction.

### Knowledge

- general Oromo-language knowledge;
- history and culture;
- geography;
- terminology;
- regional/dialectal variation.

### Instruction following and safety

- instruction adherence;
- refusal behavior;
- privacy;
- harmful-request handling;
- hallucination and misinformation checks.

Evaluation sets should be versioned, documented, and kept separate from training data.

---

## 7. Evaluation principles

Oromo AI evaluation should remain:

- reproducible;
- versioned;
- leakage-aware;
- language-specific where necessary;
- comparable across experiments;
- resistant to cherry-picked examples.

A new model or tokenizer should not replace a previous reference simply because a handful of outputs look better. Changes should be supported by frozen-set measurements and documented tradeoffs.

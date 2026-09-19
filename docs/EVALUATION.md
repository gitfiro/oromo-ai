# Oromo AI Evaluation Framework

## Purpose

Evaluation in Oromo AI is designed to prevent progress from being judged by fluent-looking examples alone.

Every major research layer should have a fixed, reproducible evaluation protocol before optimization begins.

Current evaluation layers:

```text
Corpus integrity
      ↓
Tokenizer efficiency
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

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oromo-unigram-48k-byte | 48,000 | 1.4000 | 38.75% | 61.25% | 0 | 5.4562 |
| oromo-unigram-32k-byte | 32,000 | 1.4495 | 40.83% | 59.17% | 0 | 5.2699 |
| castorini/afriberta_base | 70,006 | 1.6765 | 39.83% | 60.16% | 0 | 4.5563 |
| xlm-roberta-base | 250,002 | 2.6091 | 81.03% | 18.97% | 3 | 2.9278 |
| bert-base-multilingual-cased | 119,547 | 2.8696 | 87.36% | 12.63% | 5,423 | 2.6620 |

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

The current 32K-byte and 48K-byte tokenizers are research references, not yet final production choices.

---

## 4. Next evaluation: causal-LM tokenizers

The next benchmark must use the same frozen 10K Oromo sample against realistic continued-pretraining model families.

Planned families:

- Qwen;
- Llama;
- Gemma;
- Mistral.

The objective is to measure native-tokenizer Oromo inflation before changing any pretrained model vocabulary.

This experiment will inform whether Oromo AI should use:

```text
native tokenizer
      |
      +-- sufficient → keep it
      |
      +-- usable but inefficient → investigate vocabulary augmentation
      |
      +-- substantially inefficient → investigate tokenizer surgery/custom path
```

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

The proof model exists to validate the pipeline, not to maximize benchmark headlines.

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

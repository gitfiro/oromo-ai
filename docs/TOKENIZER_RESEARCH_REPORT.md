# Afaan Oromoo Tokenizer Research Report

**Project:** Oromo AI  
**Research phase:** Tokenizer baseline and custom-candidate evaluation  
**Corpus version:** `afriberta_oromo_v0.1.2`  
**Status:** Baseline complete; custom candidates benchmarked; causal-LM tokenizer benchmarking next

---

## 1. Purpose

This report records the reproducible tokenizer research completed before Oromo AI begins continued-pretraining experiments.

The project does **not** assume that a custom tokenizer is automatically preferable. The objective is to measure how efficiently established and Oromo-specialized tokenizers represent Afaan Oromoo, identify failure modes, and preserve enough evidence to make the later base-model/tokenizer decision deliberately.

The current decision sequence remains:

```text
Validated corpus
      ↓
Frozen tokenizer evaluation set
      ↓
Established tokenizer baselines
      ↓
Custom tokenizer candidates
      ↓
Causal-LM tokenizer benchmarks
      ↓
Tokenizer/base-model decision
      ↓
Tiny CPT proof
```

No tokenizer has been declared the final production tokenizer yet.

---

## 2. Production corpus

Tokenizer research is based on the validated production corpus:

```text
data/processed/afriberta_oromo_v0.1.2/train.jsonl
```

Corpus statistics:

| Metric | Value |
| --- | ---: |
| Processed records | 410,193 |
| Processed characters | 52,122,367 |
| Primary quality rejections | 614 |
| Duplicate-after-cleaning records | 34 |
| Rejection-ledger entries | 648 |

Processed corpus SHA-256:

```text
6f990088c8fb319b46c9a25a1c463e7a700cc8d292da781cfcc44ac4391ee0f6
```

The tokenizer experiments do not modify the production corpus.

---

## 3. Frozen tokenizer evaluation set

The initial exploratory benchmark used the first 1,000 records. That run was intentionally superseded by a fixed corpus-wide evaluation sample.

The canonical tokenizer evaluation set is:

```text
tokenizer/evaluation/samples/afriberta_oromo_v0.1.2_n10000.jsonl
```

It contains:

```text
10,000 unique records
10,000 unique record IDs
10,000 unique texts
0 duplicate record IDs
0 duplicate texts
```

Sampling seed:

```text
20260919
```

Evaluation sample SHA-256:

```text
369c4438beab0d619336448eab7e27aae29d0722fd089088dbf0b2addc3d81f5
```

This sample is frozen. Tokenizer candidates must be evaluated against the same file to remain directly comparable.

---

## 4. Leakage-safe tokenizer training corpus

The 10,000 evaluation records were excluded by stable `record_id` before training custom tokenizer candidates.

Training corpus:

```text
tokenizer/training/afriberta_oromo_v0.1.2_tokenizer_train.txt
```

Split accounting:

| Split | Records |
| --- | ---: |
| Production corpus | 410,193 |
| Frozen tokenizer evaluation holdout | 10,000 |
| Tokenizer training corpus | 400,193 |
| Evaluation leakage | 0 |
| Empty records skipped | 0 |
| Unresolved record IDs | 0 |

Training corpus SHA-256:

```text
a733419e61ed4751e7f4da950e8c05c893ecbbc63be12c1551a1493507162dff
```

The split invariant is exact:

```text
400,193 training + 10,000 evaluation = 410,193 production records
```

---

## 5. Benchmark metrics

Tokenizer evaluation records:

- vocabulary size
- total token count
- tokens per whitespace-delimited word
- characters per token
- UTF-8 bytes per token
- fragmented words
- single-token words
- unaligned words
- unknown-token count
- unknown-token rate
- sample tokenizations
- tokenizer/library versions

Word-offset alignment was audited separately. The benchmark explicitly classifies words as:

```text
fragmented
single-token
unaligned
```

with the invariant:

```text
fragmented + single-token + unaligned = total whitespace words
```

The small alignment anomalies observed in pretrained tokenizers were traced primarily to Unicode formatting/control artifacts rather than ordinary Oromo words.

---

## 6. Established tokenizer baseline

The frozen 10K benchmark produced:

| Tokenizer | Vocabulary | Tokens/word | Fragmentation | Single-token | UNK | Bytes/token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| castorini/afriberta_base | 70,006 | 1.6765 | 39.83% | 60.16% | 0 | 4.5563 |
| xlm-roberta-base | 250,002 | 2.6091 | 81.03% | 18.97% | 3 | 2.9278 |
| bert-base-multilingual-cased | 119,547 | 2.8696 | 87.36% | 12.63% | 5,423 | 2.6620 |

AfriBERTa represents this Afaan Oromoo benchmark much more compactly than XLM-R or mBERT.

The result is evidence about tokenizer behavior, not a final model-selection decision.

---

## 7. Custom Oromo tokenizer Candidate V1

Custom candidates were trained with SentencePiece Unigram using identical training data and settings while varying vocabulary size.

Candidate vocabulary sizes:

```text
16K
24K
32K
48K
```

Core configuration:

```text
model_type=unigram
character_coverage=1.0
normalization_rule_name=nmt_nfkc
shuffle_input_sentence=False
input_sentence_size=0
max_sentence_length=16384
max_sentencepiece_length=32
split_digits=False
byte_fallback=False
```

Candidate V1 benchmark results:

| Tokenizer | Vocabulary | Tokens/word | Fragmentation | Single-token | UNK | Bytes/token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oromo-unigram-48k | 48,000 | 1.3993 | 38.74% | 61.26% | 28 | 5.4592 |
| oromo-unigram-32k | 32,000 | 1.4483 | 40.82% | 59.18% | 28 | 5.2744 |
| oromo-unigram-24k | 24,000 | 1.4912 | 42.55% | 57.45% | 28 | 5.1225 |
| oromo-unigram-16k | 16,000 | 1.5677 | 45.54% | 54.46% | 28 | 4.8726 |

The vocabulary-size curve shows continued gains through 48K. The gains are not flat enough to dismiss the larger candidate without considering model-parameter cost.

---

## 8. Unknown-token audit

All four Candidate V1 vocabularies produced exactly 28 unknown tokens, indicating that vocabulary size was not the cause.

The 28 unknown tokens occurred in 13 affected evaluation records. The audited characters were out-of-domain or unusual Unicode material such as:

- CJK characters
- Korean Hangul
- Lao script
- emoji
- mathematical symbols such as `≤`
- decorative symbols such as `◤` and `◥`
- `ɓ` / `Ɓ` from non-standard/non-Qubee material

No normal modern Afaan Oromoo Qubee coverage failure was identified in this audit.

The first version of the audit also exposed an implementation detail: SentencePiece proto offsets around multibyte Unicode must not be naively sliced as Python character indices. The corrected audit uses SentencePiece's own `piece.surface`.

---

## 9. Candidate V2: byte fallback

The serious 32K and 48K candidates were retrained with:

```text
byte_fallback=True
```

Results:

| Tokenizer | Vocabulary | Tokens/word | Fragmentation | Single-token | UNK | Bytes/token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oromo-unigram-48k-byte | 48,000 | 1.4000 | 38.75% | 61.25% | 0 | 5.4562 |
| oromo-unigram-32k-byte | 32,000 | 1.4495 | 40.83% | 59.17% | 0 | 5.2699 |

Byte fallback eliminated unknown tokens while producing only a negligible efficiency change.

For custom-tokenizer research, the two serious reference candidates are therefore:

```text
oromo-unigram-32k-byte
oromo-unigram-48k-byte
```

The 48K-byte candidate currently has the strongest measured sequence efficiency. The 32K-byte candidate remains important because a smaller vocabulary reduces embedding/output-layer parameter cost.

---

## 10. Unified tokenizer comparison

The frozen 10K benchmark now includes custom Oromo tokenizers, multilingual baselines, and realistic causal-LM tokenizers.

### Custom and multilingual references

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oromo-unigram-48k | 48,000 | 1.3993 | 38.74% | 61.26% | 28 | 5.4592 |
| oromo-unigram-48k-byte | 48,000 | **1.4000** | **38.75%** | **61.25%** | **0** | **5.4562** |
| oromo-unigram-32k | 32,000 | 1.4483 | 40.82% | 59.18% | 28 | 5.2744 |
| oromo-unigram-32k-byte | 32,000 | 1.4495 | 40.83% | 59.17% | 0 | 5.2699 |
| oromo-unigram-24k | 24,000 | 1.4912 | 42.55% | 57.45% | 28 | 5.1225 |
| oromo-unigram-16k | 16,000 | 1.5677 | 45.54% | 54.46% | 28 | 4.8726 |
| castorini/afriberta_base | 70,006 | 1.6765 | 39.83% | 60.16% | 0 | 4.5563 |
| xlm-roberta-base | 250,002 | 2.6091 | 81.03% | 18.97% | 3 | 2.9278 |
| bert-base-multilingual-cased | 119,547 | 2.8696 | 87.36% | 12.63% | 5,423 | 2.6620 |

### Native causal-LM tokenizers

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| google/gemma-3-1b-pt | 262,144 | **2.7855** | **85.91%** | **14.09%** | 0 | **2.7423** |
| Qwen/Qwen3.5-0.8B-Base | 248,044 | 2.9191 | 86.94% | 13.06% | 0 | 2.6169 |
| meta-llama/Llama-3.2-1B | 128,000 | 3.0311 | 88.32% | 11.68% | 0 | 2.5202 |
| Qwen/Qwen3-0.6B-Base | 151,643 | 3.0713 | 88.89% | 11.11% | 0 | 2.4872 |
| mistralai/Mistral-7B-v0.3 | 32,768 | 3.3241 | 93.09% | 6.91% | 0 | 2.2980 |

All tested causal tokenizers achieve zero unknown tokens on the current holdout, so the central problem is not Unicode coverage. The problem is **representation efficiency**.

Relative to the custom Oromo 48K-byte reference at 1.4000 tokens/word:

- Gemma 3 uses roughly 99% more tokens per word;
- Qwen3.5 uses roughly 109% more;
- Llama 3.2 uses roughly 117% more;
- Qwen3 uses roughly 119% more;
- Mistral 7B v0.3 uses roughly 137% more.

This cross-family result makes Oromo token inflation a real engineering constraint for continued pretraining rather than an artifact of one model family.

---

## 11. Phase 4A conclusion — native causal tokenizers

Phase 4A established the following:

1. modern causal tokenizers can represent the evaluated Oromo text without unknown tokens;
2. every tested causal tokenizer fragments Oromo heavily;
3. Gemma 3 is the strongest native causal tokenizer among the tested families;
4. no tested native tokenizer approaches the custom Oromo tokenizer's sequence efficiency;
5. tokenizer efficiency must therefore be considered explicitly when selecting a CPT base model.

The native benchmark does **not** by itself determine the best base model. Base-model quality, architecture, license, training ecosystem, compute cost, and CPT behavior remain separate decision variables.

---

## 12. Why augmentation was tested before replacement

Replacing a pretrained model's tokenizer is not a neutral operation.

A pretrained model has learned a correspondence between:

```text
token ID ↔ embedding vector ↔ learned internal behavior
```

Replacing the full tokenizer can invalidate much of that correspondence.

The first lower-risk experiment was therefore vocabulary augmentation:

```text
existing tokenizer
      +
selected Oromo tokens
      ↓
preserve all existing token IDs
append new token IDs
initialize only new embeddings later
```

Phase 4B1 is tokenizer-only. No model weights were changed.

---

## 13. Phase 4B1 candidate construction

The augmentation candidate pool is derived exclusively from:

```text
tokenizer/training/afriberta_oromo_v0.1.2_tokenizer_train.txt
```

Training corpus properties:

```text
400,193 records
SHA-256:
a733419e61ed4751e7f4da950e8c05c893ecbbc63be12c1551a1493507162dff
```

The frozen 10K evaluation holdout is never consulted for candidate frequency generation.

Candidate-pool statistics:

```text
6,716,499 whitespace tokens observed
6,414,817 accepted lexical occurrences
405,216 unique lexical forms
168,207 candidates with frequency >= 2
```

Candidates are conservative Latin/Qubee-like lexical forms. URLs, numbers, punctuation-only material, CJK, Hangul, Lao, emoji, and arbitrary symbol sequences are excluded from the lexical pool.

For each base tokenizer, candidates already represented as one native token are discarded.

The remaining candidates are ranked by:

```text
estimated_training_savings
    =
frequency × (native_pieces - 1)
```

This favors words that are both frequent in the leakage-safe training data and expensive for the native tokenizer.

Examples of high-value additions include:

- Oromoo
- Itoophiyaa
- keessatti
- Oromiyaa
- irraa
- yeroo
- mootummaa
- Bilisummaa
- qabsoo
- namoota

---

## 14. Phase 4B1 whole-word augmentation results

Exact effective vocabulary-growth budgets were tested at:

```text
+2,000
+4,000
+8,000
+16,000
```

The budget is defined by the actual increase in `len(tokenizer)`, not by the return value of the tokenizer API. This avoids counting lexical candidates that collide with pre-existing or normalized vocabulary entries.

### Llama 3.2 1B

| Budget | Effective vocab | Tok/Word | Reduction vs native | Frag % | Single % | UNK |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Native | 128,256 | 3.0311 | — | 88.32% | 11.68% | 0 |
| +2K | 130,256 | 2.5705 | 15.20% | 45.05% | 54.95% | 0 |
| +4K | 132,256 | 2.4715 | 18.46% | 38.19% | 61.81% | 0 |
| +8K | 136,256 | 2.3716 | 21.76% | 32.23% | 67.77% | 0 |
| +16K | 144,256 | 2.2821 | 24.71% | 27.11% | 72.89% | 0 |

### Qwen3 0.6B

| Budget | Effective vocab | Tok/Word | Reduction vs native | Frag % | Single % | UNK |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Native | 151,669 | 3.0713 | — | 88.89% | 11.11% | 0 |
| +2K | 153,669 | 2.6063 | 15.14% | 45.57% | 54.43% | 0 |
| +4K | 155,669 | 2.5058 | 18.41% | 38.70% | 61.30% | 0 |
| +8K | 159,669 | 2.4049 | 21.70% | 32.71% | 67.29% | 0 |
| +16K | 167,669 | 2.3140 | 24.66% | 27.59% | 72.41% | 0 |

### Gemma 3 1B

| Budget | Effective vocab | Tok/Word | Reduction vs native | Frag % | Single % | UNK |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Native | 262,145 | 2.7855 | — | 85.91% | 14.09% | 0 |
| +2K | 264,145 | 2.4475 | 12.13% | 44.79% | 55.21% | 0 |
| +4K | 266,145 | 2.3692 | 14.95% | 38.21% | 61.79% | 0 |
| +8K | 270,145 | 2.2903 | 17.78% | 32.38% | 67.62% | 0 |
| +16K | 278,145 | **2.2172** | **20.40%** | 27.38% | 72.62% | 0 |

Gemma remains the most efficient absolute tokenizer after whole-word augmentation because it starts from the strongest native baseline.

---

## 15. Interpretation of the augmentation curve

Whole-word augmentation works.

The first 2K–4K additions deliver the largest early improvements, especially in word fragmentation.

At +4K:

```text
Llama 3.2: 38.19% fragmentation
Qwen3:     38.70%
Gemma 3:   38.21%
Oromo 48K: 38.75%
```

This is an important result: a relatively small appended lexical vocabulary can bring frequent-word fragmentation close to the custom Oromo reference without replacing the pretrained tokenizer.

However, fragmentation and sequence efficiency are not the same metric.

At +16K:

```text
Gemma +16K:   2.2172 tokens/word
Llama +16K:   2.2821
Qwen3 +16K:   2.3140
Oromo 48K:    1.4000
```

Whole-word additions make many frequent words atomic, but uncovered words can still be decomposed inefficiently by the underlying native subword system.

This is the key Phase 4B1 finding.

---

## 16. Current decision state

**Established facts:**

- the production corpus and frozen tokenizer holdout remain unchanged;
- custom Oromo 32K-byte and 48K-byte tokenizers are strong sequence-efficiency references;
- the custom 48K-byte tokenizer remains the best measured sequence-efficiency reference at 1.4000 tokens/word;
- all tested causal tokenizers have zero unknowns on the current holdout;
- all tested causal tokenizers impose substantial Oromo token inflation;
- Gemma 3 has the strongest native causal tokenizer tested so far;
- whole-word augmentation substantially improves Llama, Qwen3, and Gemma;
- +2K to +4K captures much of the early word-fragmentation gain;
- whole-word augmentation does not recover the custom tokenizer's full subword efficiency.

**Not yet decided:**

- final causal base model;
- final tokenizer strategy;
- final augmentation budget;
- whether Phase 4B2 should introduce Oromo-specific subword augmentation;
- whether full tokenizer replacement is justified;
- embedding initialization strategy for any appended vocabulary;
- exact CPT configuration.

---

## 17. Next milestone

The next decision should remain tokenizer-only until the architecture is justified:

```text
Phase 4A native causal benchmark      ✅ complete
Phase 4B1 whole-word augmentation    ✅ complete
              ↓
analyze diminishing returns
              ↓
estimate embedding/vocabulary cost
              ↓
decide on Phase 4B2 subword augmentation
              ↓
select base-model + tokenizer strategy
              ↓
tiny continued-pretraining proof
```

The project should still avoid SFT, LoRA/QLoRA instruction tuning, and large-scale training until the base-model/tokenizer strategy is resolved with evidence.

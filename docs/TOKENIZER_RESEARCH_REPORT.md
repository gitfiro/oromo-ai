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

## 10. Current comparison

The current frozen benchmark is:

| Tokenizer | Vocab | Tok/Word | Frag % | Single % | UNK | Bytes/Tok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oromo-unigram-48k | 48,000 | 1.3993 | 38.74% | 61.26% | 28 | 5.4592 |
| oromo-unigram-48k-byte | 48,000 | 1.4000 | 38.75% | 61.25% | 0 | 5.4562 |
| oromo-unigram-32k | 32,000 | 1.4483 | 40.82% | 59.18% | 28 | 5.2744 |
| oromo-unigram-32k-byte | 32,000 | 1.4495 | 40.83% | 59.17% | 0 | 5.2699 |
| oromo-unigram-24k | 24,000 | 1.4912 | 42.55% | 57.45% | 28 | 5.1225 |
| oromo-unigram-16k | 16,000 | 1.5677 | 45.54% | 54.46% | 28 | 4.8726 |
| castorini/afriberta_base | 70,006 | 1.6765 | 39.83% | 60.16% | 0 | 4.5563 |
| xlm-roberta-base | 250,002 | 2.6091 | 81.03% | 18.97% | 3 | 2.9278 |
| bert-base-multilingual-cased | 119,547 | 2.8696 | 87.36% | 12.63% | 5,423 | 2.6620 |

The 48K-byte candidate uses approximately 16.5% fewer tokens per whitespace word than AfriBERTa on the same frozen evaluation set while retaining zero unknown tokens.

---

## 11. Why the custom tokenizer is not frozen yet

Oromo AI's main model strategy is continued pretraining of a capable open-weight causal language model rather than immediately training a large model from scratch.

A pretrained causal LM is coupled to its tokenizer and embedding vocabulary. Replacing that tokenizer can require vocabulary surgery, embedding initialization, and additional adaptation.

Therefore the next experiment is not another custom vocabulary sweep.

The next experiment is to benchmark the native tokenizers of realistic CPT base-model families against the same frozen Oromo evaluation set.

Target families include:

- Qwen
- Llama
- Gemma
- Mistral

Those measurements will determine whether:

1. a native causal-LM tokenizer is already adequate;
2. vocabulary augmentation is justified;
3. tokenizer replacement is justified;
4. a custom tokenizer is more appropriate for a model trained substantially from scratch.

---

## 12. Current decision state

**Established facts:**

- the tokenizer benchmark is reproducible;
- the 10K evaluation set is frozen and leakage-safe;
- AfriBERTa is substantially more efficient on Oromo than XLM-R or mBERT;
- Oromo-specific SentencePiece training materially improves sequence efficiency;
- byte fallback removes arbitrary-Unicode unknowns with negligible cost;
- 32K-byte and 48K-byte are the serious custom-tokenizer references.

**Not yet decided:**

- final tokenizer;
- final base model;
- whether tokenizer augmentation or replacement will be used for CPT;
- whether 32K or 48K is preferable after embedding-parameter cost is considered.

---

## 13. Next milestone

```text
Benchmark realistic causal-LM tokenizers
              ↓
Quantify Oromo token inflation
              ↓
Compare native tokenizer vs 32K-byte vs 48K-byte
              ↓
Select CPT/base-model strategy
              ↓
Tiny continued-pretraining proof
```

The project should not begin SFT, LoRA/QLoRA instruction work, or large-scale training before this decision is supported by evidence.

# OromoTokenizer Research

This directory contains the reproducible **OromoTokenizer** research and evaluation layer for the Oromo AI initiative.

## Objective

Determine how efficiently existing tokenizers represent Afaan Oromoo before deciding which tokenizer or tokenizer-adaptation strategy should accompany OromoLM.

The project will not assume that a custom tokenizer is necessary. The decision must be evidence-driven.

## Evaluation Principles

Tokenizer evaluation must measure:

- Token count
- Tokens per whitespace-delimited word
- Characters per token
- Bytes per token
- Word fragmentation
- Subword fragmentation
- Unknown-token behavior, when applicable
- Behavior on Oromo orthography and Qubee
- Preservation of punctuation, apostrophes, and diacritics
- Efficiency on short, medium, and long Oromo text

## Evaluation Corpus

The primary benchmark source is:

`data/processed/afriberta_oromo_v0.1.2/train.jsonl`

The benchmark must not modify the production corpus.

A deterministic evaluation sample should be generated from the validated corpus and recorded so future tokenizer comparisons use the same text.

## Benchmark Categories

The evaluation set should contain representative examples covering:

1. Normal Afaan Oromoo prose
2. Long Oromo words
3. Morphologically complex words
4. Words containing apostrophes
5. Oromo-specific orthography
6. Diacritics
7. Punctuation
8. Numbers
9. Oromo/English mixed text
10. Short sentences
11. Long sentences
12. Rare vocabulary

## Candidate Tokenizers

The first benchmark should evaluate established pretrained tokenizers.

A tokenizer should not be selected merely because it produces fewer tokens. Oromo linguistic behavior and fragmentation must also be considered.

## Reproducibility

Every benchmark run must record:

- tokenizer identifier
- tokenizer implementation/version
- Transformers version
- Tokenizers version
- evaluation corpus/version
- number of examples
- total characters
- total words
- total tokens
- benchmark timestamp
- configuration

## Decision Rule

Tokenizer research has three possible outcomes:

### Existing tokenizer is sufficient

Continue using an established tokenizer and document the evidence.

### Existing tokenizer is usable but inefficient

Investigate vocabulary augmentation or continued tokenizer research.

### Existing tokenizers are substantially inefficient

Train and evaluate OromoTokenizer candidates.

No custom tokenizer should be trained until the baseline measurements justify it.

# Oromo AI Naming Convention

## Purpose

This document defines the canonical names used by the Oromo AI project. The convention separates the overall initiative from its corpora, tokenizers, models, and evaluation artifacts.

## Canonical names

| Scope | Canonical name | Definition |
| --- | --- | --- |
| Initiative | **Oromo AI** | The overall open research and engineering initiative for Afaan Oromoo AI |
| Repository | **`oromo-ai`** | The GitHub repository and Python project containing the research infrastructure |
| Corpus family | **OromoCorpus** | Versioned training, validation, and evaluation corpora |
| Tokenizer family | **OromoTokenizer** | Custom tokenizer candidates and tokenizer-adaptation research |
| Model family | **OromoLM** | Afaan Oromoo causal language models developed through continued pretraining and later tuning |
| Evaluation suite | **OromoBench** | Versioned evaluation datasets, tasks, metrics, and reports |

## Model release identifiers

Model releases use:

```text
OromoLM-<size>
```

Examples:

```text
OromoLM-600M
OromoLM-1B
OromoLM-3B
```

Instruction-tuned or specialized releases add a descriptive suffix:

```text
OromoLM-1B-Instruct
OromoLM-1B-Translate
```

The size is the model's documented parameter class. A release must not use an OromoLM identifier until its underlying checkpoint, tokenizer strategy, model card, license, evaluation, and artifact checksums are ready to publish.

## Corpus identifiers

**OromoCorpus** is the family name. Concrete datasets keep immutable, reproducible identifiers, for example:

```text
afriberta_oromo_v0.1.2
```

Future public corpus releases may use names such as `OromoCorpus-v1`, but existing paths, manifests, hashes, and historical IDs must not be retroactively renamed.

## Tokenizer identifiers

**OromoTokenizer** is the tokenizer research family. Existing experimental identifiers remain unchanged, including:

```text
oromo-unigram-32k-byte
oromo-unigram-48k-byte
```

These are research candidates. The OromoTokenizer family name does not imply that full tokenizer replacement has been chosen for OromoLM.

## Stability rules

1. Use **Oromo AI** only for the initiative or ecosystem.
2. Use **OromoLM** for models developed by the initiative.
3. Use **OromoCorpus** for the corpus family, not as a replacement for immutable dataset version IDs.
4. Use **OromoTokenizer** for custom tokenizer and tokenizer-adaptation research.
5. Use **OromoBench** for the evaluation suite.
6. Preserve third-party model names exactly, including Qwen, Gemma, Llama, Mistral, and AfriBERTa identifiers.
7. Preserve historical filenames, hashes, manifests, benchmark result names, and experiment IDs for reproducibility.
8. Do not describe a planned artifact as released or final before its selection and release criteria are satisfied.

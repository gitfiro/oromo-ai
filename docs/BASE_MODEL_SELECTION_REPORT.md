# OromoLM Base-Model and Tokenizer Selection Report

**Project:** Oromo AI  
**Phase:** 4C — base-model and tokenizer strategy  
**Status:** provisional selection pending cleaned whole-word candidate v2 verification  
**Decision date:** 2026-10-03

## 1. Decision

The current leading configuration for the first controlled OromoLM continued-pretraining proof is:

```text
Primary base model:
Qwen/Qwen3-0.6B-Base

Tokenizer strategy:
native Qwen3 tokenizer
+ 4,000 leakage-safe Afaan Oromoo whole-word tokens

Experiment role:
primary tiny-CPT proof
```

The principal comparator remains:

```text
google/gemma-3-1b-pt
+ 4,000 leakage-safe Afaan Oromoo whole-word tokens
```

This is a **proof-stage engineering decision**, not a declaration that Qwen3
is the final OromoLM release base. Before the vocabulary is frozen, the +4K
result must be revalidated against the cleaned whole-word candidate v2 pool,
which rejects internal mixed-case extraction concatenations found in the
original Phase 4B1 candidates. Tiny CPT and OromoBench must then validate the
choice before scaled continued pretraining.

## 2. Why the project is ready for this decision

OromoCorpus has crossed the project's minimum data gate:

```text
accepted 48K-reference tokens: 52,137,803
50M minimum progress:          104.28%
accepted sources:              6
```

Tokenizer research has also completed the decision-critical experiments:

- custom OromoTokenizer vocabulary sweep;
- byte-fallback candidates;
- frozen 10,000-record tokenizer evaluation set;
- native causal-tokenizer benchmark;
- whole-word augmentation at +2K/+4K/+8K/+16K;
- Phase 4B2 internal-subword augmentation feasibility test.

## 3. Candidate models

### Qwen3-0.6B-Base

Current upstream metadata/configuration records:

- model: `Qwen/Qwen3-0.6B-Base`
- architecture: `Qwen3ForCausalLM`
- parameters: approximately 596M
- hidden size: 1,024
- layers: 28
- context configuration: 32,768 positions
- tied input/output word embeddings: yes
- license: Apache-2.0

Engineering advantages:

- smallest serious text-only base in the current shortlist;
- permissive Apache-2.0 model license;
- standard causal-LM architecture and mature Transformers integration;
- tied embeddings reduce vocabulary-expansion parameter cost;
- lower memory/compute requirement makes it appropriate for the first proof.

### Gemma 3 1B pre-trained

Current upstream metadata/configuration records:

- model: `google/gemma-3-1b-pt`
- architecture: `Gemma3ForCausalLM`
- parameters: approximately 1.0B
- hidden size: 1,152
- layers: 26
- tied embeddings: yes
- model license: Gemma Terms of Use

Engineering advantages:

- strongest native Oromo tokenizer efficiency among the causal families tested;
- strongest absolute whole-word-augmentation tokenizer result in Phase 4B1;
- useful comparator for whether the larger base and better tokenizer translate into better Oromo CPT outcomes.

Tradeoff:

- roughly 1B parameters versus Qwen3's 596M;
- custom Gemma license and redistribution/use obligations rather than Apache-2.0.

### Llama 3.2 1B

Current upstream metadata records:

- model: `meta-llama/Llama-3.2-1B`
- parameters: approximately 1.236B
- hidden size: 2,048
- context: 131,072 positions in the released base configuration
- license: Llama 3.2 Community License

Llama remains technically viable but is not selected for the first proof because
it combines a larger training footprint with a custom redistribution license,
while its measured Oromo tokenizer efficiency is weaker than Gemma's and its
+4K whole-word result is not better than Qwen3's by enough to offset those
costs.

### Qwen3.5-0.8B-Base

Qwen3.5-0.8B-Base is Apache-2.0 and has an efficient 1,024-dimensional text
backbone, but the current release is a multimodal `Qwen3_5ForConditionalGeneration`
architecture containing a vision stack and hybrid text attention design.

It is not selected for the first text-only Oromo CPT proof because that
additional architectural complexity is unnecessary for the experiment.
It may be revisited after the first causal-text proof is stable.

## 4. Frozen tokenizer evidence

Native tokenizer results on the same frozen 10K Oromo holdout:

| Model tokenizer | Native tok/word | Native fragmentation |
| --- | ---: | ---: |
| Gemma 3 1B | 2.7855 | 85.91% |
| Qwen3.5 0.8B | 2.9191 | 86.94% |
| Llama 3.2 1B | 3.0311 | 88.32% |
| Qwen3 0.6B | 3.0713 | 88.89% |
| Oromo Unigram 48K byte reference | 1.4000 | 38.75% |

### Whole-word augmentation

| Model | Native | +2K | +4K | +8K | +16K |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gemma 3 1B | 2.7855 | 2.4475 | **2.3692** | 2.2903 | 2.2172 |
| Llama 3.2 1B | 3.0311 | 2.5705 | **2.4715** | 2.3716 | 2.2821 |
| Qwen3 0.6B | 3.0713 | 2.6063 | **2.5058** | 2.4049 | 2.3140 |

At +4K all three families reach approximately 38% word fragmentation, near the
custom Oromo 48K reference's fragmentation, while preserving every native token
ID and adding only a small vocabulary extension.

## 5. Why +4K is the proof-stage budget

+4K is selected for the first model-level experiment because it captures most
of the early whole-word fragmentation gain without paying the full +16K
embedding cost before training evidence exists.

Approximate **tied-embedding** parameter growth:

| Model | Hidden size | +4K | +8K | +16K |
| --- | ---: | ---: | ---: | ---: |
| Qwen3 0.6B | 1,024 | 4.096M | 8.192M | 16.384M |
| Gemma 3 1B | 1,152 | 4.608M | 9.216M | 18.432M |
| Llama 3.2 1B | 2,048 | 8.192M | 16.384M | 32.768M |

For Qwen3-0.6B, +4K is about 0.7% of the base parameter count. That is small
enough for a proof while still producing a large tokenizer improvement.

The +8K and +16K budgets remain candidates for later experiments if the tiny
CPT confirms that vocabulary augmentation is beneficial at model level.

## 6. Phase 4B2 negative result

Phase 4B2 tested internal Oromo subword injection through Hugging Face
`AddedToken(single_word=False)` using leakage-safe internal pieces derived
from the Oromo 48K SentencePiece reference.

Gemma 3 results:

| Strategy | Added tokens | Tokens/word | Change vs native | Fragmentation |
| --- | ---: | ---: | ---: | ---: |
| Native | 0 | 2.7855 | — | 85.91% |
| internal subword | +1K | 3.1846 | 14.33% worse | 75.58% |
| internal subword | +2K | 3.0121 | 8.13% worse | 67.15% |
| internal subword | +3K | 2.9184 | 4.77% worse | 62.18% |

The result is rejected for model use.

Although the offset-based word fragmentation metric improved, total sequence
length worsened. Generic AddedToken substring matching interfered with the
native tokenizer's own segmentation rather than integrating Oromo subwords
into its learned subword model.

Therefore:

```text
native tokenizer                         viable
native + whole-word augmentation         viable / selected for proof
generic internal AddedToken subwords      rejected
full tokenizer replacement                deferred
```

The project will not repeat this implementation on Llama or Qwen because the
experiment already falsified the mechanism being tested.

## 7. Why Qwen3 is primary despite Gemma's better tokenizer

Tokenizer efficiency is only one part of the base-model decision.

Qwen3-0.6B has three proof-stage advantages:

1. **Compute:** approximately 596M parameters is materially easier to train and
   debug than ~1B–1.24B alternatives.
2. **License:** Apache-2.0 is simpler for research artifacts and potential
   derivative-weight distribution than the current Gemma or Llama custom
   licenses.
3. **Vocabulary cost:** tied 1,024-dimensional embeddings make +4K growth only
   ~4.1M parameters.

Gemma's tokenizer remains materially better:

```text
Gemma +4K: 2.3692 tokens/word
Qwen3 +4K: 2.5058 tokens/word
```

That difference is why Gemma remains the principal comparator rather than being
discarded.

## 8. Proof-stage decision matrix

| Criterion | Qwen3 0.6B | Gemma 3 1B | Llama 3.2 1B | Qwen3.5 0.8B |
| --- | --- | --- | --- | --- |
| Text-only causal proof simplicity | strong | strong | strong | weaker |
| Parameter footprint | **lowest** | medium | highest | medium |
| License simplicity | **Apache-2.0** | Gemma terms | Llama 3.2 terms | Apache-2.0 |
| Native Oromo tokenizer | weaker | **best** | weaker | second-best |
| +4K measured Oromo tokenizer | 2.5058 | **2.3692** | 2.4715 | not run |
| Embedding expansion cost | **low** | low | higher | low |
| First tiny-CPT role | **primary** | comparator | deferred | deferred |

This table is not a claim that Qwen3 is universally the best model. It records
the engineering rationale for the next controlled experiment.

## 9. Next gate

The next sequence is:

```text
Qwen3-0.6B-Base
      +
frozen +4K whole-word Oromo vocabulary
      ↓
deterministic embedding initialization
      ↓
untouched-base evaluation snapshot
      ↓
tiny continued-pretraining proof
      ↓
loss / stability / tokenizer-use audit
      ↓
OromoBench comparison
      ↓
decide whether to:
    keep Qwen3 +4K
    test Gemma +4K
    increase to +8K
    or revise the model strategy
```

No scaled CPT, SFT, LoRA/QLoRA instruction tuning, or production model release
should occur before this proof is evaluated.


---

## 10. Whole-word candidate v2 quality gate

Before freezing the Qwen +4K proof vocabulary, a manual inspection of the
historical Phase 4B1 selected-token list found extraction-concatenation
artifacts such as:

```text
jiruSa'aatii
ibseSa'aatii
ajjeefaman'Sa'aatii
```

These forms passed the original conservative Latin lexical regex but should not
be embedded as dedicated model vocabulary.

A new builder is therefore introduced:

```text
tokenizer/augmentation/build_word_candidates_v2.py
```

The v2 policy keeps lowercase, uppercase-acronym, and ordinary title-case
lexical forms while rejecting internal mixed-case/CamelCase patterns. It still
uses only the leakage-safe 400,193-record tokenizer-training split.

The primary Qwen +4K and Gemma +4K tokenizer results must be rerun against this
v2 pool before the proof vocabulary is frozen. The original Phase 4B1 results
remain historical evidence and are not deleted.

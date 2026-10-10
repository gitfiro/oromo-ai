# General-language forgetting control v0.1

## Purpose

This control is frozen before additional OromoLM +8K training so that progress on Afaan Oromoo cannot be accepted by silently sacrificing general-language modeling ability.

The control is evaluation-only and must never be mixed into OromoLM training data.

## Source

```text
dataset:  Salesforce/wikitext
config:   wikitext-103-raw-v1
split:    validation
revision: 844b6323027b47fc4c54b8c88faf7e188b540d76
```

WikiText contains verified Good and Featured English Wikipedia articles. The project uses the raw validation split as a general English language-modeling control. Licensing/attribution details follow the upstream dataset card and source repository; this control is evaluation-only.

The freeze builder is:

```text
training/tools/prepare_general_control.py
```

Policy:

- preserve source text exactly;
- exclude only empty rows;
- remove exact duplicate texts;
- preserve source order;
- use all remaining validation rows;
- no sampling;
- no normalization;
- record source-row indices and text SHA-256 hashes;
- write a frozen JSONL plus manifest;
- require an immutable Hugging Face dataset revision;
- hash the exact Parquet source artifact used to build the frozen control.

## Evaluation

Use the same `document-bos-sliding-v1` evaluator used for exact Oromo BPB:

```text
training/tools/evaluate_bpb.py
```

All compared model states must use:

```text
context: 1024
stride:  512
dtype:   float32
device:  same GPU class within the comparison
EOS scored: false
document reset: true
```

Measure at least:

1. untouched `google/gemma-3-1b-pt`;
2. native-tokenizer Oromo CPT;
3. current OromoLM +8K CPT;
4. every additional +8K learning-curve checkpoint.

## Predeclared forgetting gate

The next OromoLM +8K candidate advances only if both conditions hold:

```text
Oromo quality:
exact Oromo BPB < 1.733832395

General-language retention:
WikiText control BPB <= 1.05 × untouched-Gemma WikiText BPB
```

The **+5% relative BPB ceiling** is a project guardrail selected before inspecting the control results. It is not claimed as a universal catastrophic-forgetting standard.

If the candidate beats the Oromo target but exceeds the +5% general-control ceiling, it does not advance without a documented mitigation experiment.

## Freeze status

The source, revision, transformation policy, and acceptance rule are frozen. The generated JSONL counts and SHA-256 will be added after the builder is run in the local development environment.

## References

- Salesforce WikiText dataset card and repository.
- Oromo exact BPB protocol: `docs/OROMO_IMPROVEMENT_GATE.md`
- v0.2 exact result: `docs/CPT_RERUN_V0_2_RESULTS.md`

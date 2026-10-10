# OromoLM +8K CPT learning curve v0.3

## Purpose

Measure whether the validated +8K tokenizer/model path closes or crosses the
native-tokenizer Oromo CPT quality benchmark when given substantially more
fresh Oromo exposure, while retaining acceptable general-language behavior.

## Starting model

The run starts from the preserved v0.2 +8K CPT model weights:

```text
training/runs/oromolm-8k-cpt-rerun-v0.2/final_model/model.safetensors
SHA-256:
cc39d8100a640590f80a233e0c1720e52d74830118d43c79d941b00e51434fa2
```

The v0.2 final model does not preserve optimizer/scheduler state. Therefore
v0.3 starts a **new optimizer trajectory from the v0.2 model weights**. Within
v0.3, all learning-curve snapshots come from one uninterrupted trajectory.

## Fresh continuation corpus

```text
dataset: oromocorpus-cpt-continuation-v0.3
records: 146,038
whitespace words: 10,039,123
characters: 77,705,868
UTF-8 bytes: 78,680,181
exact overlap with v0.1 pilot train/validation: 0
JSONL SHA-256:
814f52575f4e4e38ff64b98b01bbe3837d17129cc2628d43cd8e571d1d2b298d
```

The source mixture remains proportional to the remaining accepted source words
after excluding all exact pilot train and validation texts.

## Packed +8K workload

```text
tokenizer length: 270,145
sequence length: 1,024
content tokens: 23,932,744
tokens including one EOS/document: 24,078,782
packed sequences: 23,515
packed train SHA-256:
14141a61f11755f8477ec2515e124fa46b071094547b6c46f35e294c4074c162
```

Frozen v0.1 validation remains unchanged:

```text
records: 1,503
tokens including EOS: 249,875
packed sequences: 245
packed validation SHA-256:
abb452f63a504884a875b7989fd31b34e4da5c6edfaa9cbf622ecc9cfb6c80dc
```

## Training schedule

At microbatch 1 and gradient accumulation 16:

```text
23,515 / 16 = 1,469.6875
planned optimizer updates = 1,470
```

The v0.3 run uses:

```text
learning rate: 1e-5
weight decay: 0.1
warmup ratio: 0.02
scheduler: cosine
BF16: true
gradient checkpointing: true
seed/data_seed: 42
```

The learning rate is intentionally lower than v0.2's 2e-5 because this is
continued adaptation from an already Oromo-adapted checkpoint rather than
initial CPT from Gemma.

Model-only snapshots are saved every 250 optimizer steps:

```text
250
500
750
1000
1250
final 1470
```

The final 1,470-step state is saved through the normal final-model export.

## Evaluation gates

For every retained snapshot, run exact Oromo BPB with the frozen
`document-bos-sliding-v1` protocol.

Primary Oromo target:

```text
BPB < 1.733832395
```

General-language forgetting gate:

```text
WikiText control BPB <= 1.05 × untouched Gemma WikiText control BPB
```

The untouched-Gemma WikiText baseline must be measured on the frozen
general-control-v0.1 set before declaring any v0.3 snapshot acceptable.

## Stop/selection rule

The preferred checkpoint is the earliest snapshot that:

1. beats 1.733832395 exact Oromo BPB;
2. remains within the predeclared general-language retention ceiling; and
3. shows no material instability in the training/evaluation trace.

If no checkpoint crosses the Oromo target, retain the learning curve and use it
to decide whether +8K deserves more exposure or whether the +4K ablation should
become the next controlled experiment.

# OromoLM +8K CPT learning curve v0.3 results

## Summary

The v0.3 continuation experiment tested whether the frozen Gemma +8K OromoLM
path could close the exact Oromo BPB gap to the native-tokenizer CPT reference
while retaining acceptable general-language behavior.

The answer is: **nearly, but not yet fully**.

The best v0.3 checkpoint reached **1.734823064 BPB** on the frozen Oromo
validation set, only about **0.057% higher/worse** than the native-tokenizer CPT
reference at **1.733832395 BPB**. At the same time, all tested late checkpoints
passed the predeclared WikiText retention gate.

## Frozen starting point

```text
v0.2 OromoLM +8K exact Oromo BPB: 1.863338883
native-tokenizer CPT benchmark:   1.733832395
```

The v0.3 run started from the preserved v0.2 +8K model weights:

```text
model.safetensors SHA-256:
cc39d8100a640590f80a233e0c1720e52d74830118d43c79d941b00e51434fa2
```

## Fresh continuation corpus

The continuation corpus was selected from the same six accepted Oromo source
families while excluding every exact text appearing in the original pilot
training and validation splits.

```text
records:          146,038
whitespace words: 10,039,123
characters:       77,705,868
UTF-8 bytes:      78,680,181
pilot exact-text overlap: 0
JSONL SHA-256:
814f52575f4e4e38ff64b98b01bbe3837d17129cc2628d43cd8e571d1d2b298d
```

With the frozen +8K tokenizer:

```text
content tokens:          23,932,744
tokens including EOS:    24,078,782
packed sequences:        23,515
optimizer updates:       1,470
packed train SHA-256:
14141a61f11755f8477ec2515e124fa46b071094547b6c46f35e294c4074c162
```

## A100 training result

Hardware:

```text
NVIDIA A100-SXM4-80GB
```

Run measurements:

```text
train wall time:       5,497.63 s
eval wall time:           12.93 s
total wall time:       5,510.56 s
training throughput:   4,379.95 tokens/s
peak allocated VRAM:      10.76 GiB
peak reserved VRAM:       11.97 GiB
final Trainer eval loss:   3.824897
run-summary SHA-256:
9ad83b6bce5a6155f859a09a468fc7c8675c73842bc7cd78c7367747a7cdec04
```

## Exact Oromo learning curve

All checkpoints were evaluated with the same frozen 1,503-record Oromo holdout
and the exact `document-bos-sliding-v1` byte-normalized evaluator.

| Step | Exact Oromo BPB | NLL / byte | Scored tokens |
| ---: | ---: | ---: | ---: |
| 250 | 1.799051259 | 1.247007308 | 248,372 |
| 500 | 1.758329918 | 1.218781425 | 248,372 |
| 750 | 1.741555246 | 1.207154108 | 248,372 |
| 1,000 | 1.735902233 | 1.203235739 | 248,372 |
| 1,250 | 1.734835917 | 1.202496625 | 248,372 |
| 1,470 | **1.734823064** | **1.202487715** | 248,372 |

The predeclared Oromo target was:

```text
BPB < 1.733832395
```

The final v0.3 checkpoint therefore missed the native-tokenizer CPT reference by:

```text
absolute BPB gap: 0.000990669
relative gap:     ~0.057%
```

The curve flattened strongly near the end: the improvement from step 1,250 to
1,470 was only about 0.000012853 BPB. This argues against blindly repeating the
same continuation set for another epoch.

Relative to the v0.2 +8K result at 1.863338883 BPB, v0.3 reduced BPB by about
6.90%.

## General-language retention

The general-language control was frozen before v0.3 training.

Untouched Gemma on the frozen WikiText control:

```text
records:        2,361
UTF-8 bytes:    1,142,152
scored tokens:  256,541
NLL / byte:     0.702334591
BPB:            1.013254631
```

The predeclared +5% retention ceiling was therefore:

```text
1.063917363 BPB
```

Late v0.3 checkpoints:

| Step | WikiText BPB | Gate |
| ---: | ---: | --- |
| 1,000 | 1.033682489 | PASS |
| 1,250 | 1.033754204 | PASS |
| 1,470 | 1.033754855 | PASS |

All measured late checkpoints remained comfortably inside the predeclared
general-language retention ceiling.

## Interpretation

v0.3 materially changes the tokenizer/model decision picture.

The +8K path is no longer ~7.47% behind the native-tokenizer CPT reference. With
fresh continued pretraining it reached near-parity, ending only ~0.057% higher
in exact Oromo BPB while still passing the general-language retention gate.

This does **not** justify claiming that +8K has beaten the native-tokenizer
reference. The benchmark line remains 1.733832395 BPB and v0.3 remained just
above it.

The result does show that the earlier +8K quality gap was largely an adaptation
gap rather than a permanent consequence of the augmented vocabulary.

## Preservation

The RunPod experiment was copied back to the local research environment under:

```text
preserved/v0.3-2026-10-10/
```

The local preservation check verified **53 hashed files with zero failures**
against the SHA-256 manifest generated on the A100:

```text
Checked: 53
Failed:  0
ALL PRESERVED HASHES MATCH
```

Large model checkpoints remain outside normal Git.

## Next research decision

The next controlled decision should compare:

1. one additional **fresh-data** +8K continuation tranche, versus
2. a **+4K vocabulary ablation** to map the quality/efficiency frontier.

Repeating the exact same v0.3 training text for another epoch is not the
preferred next experiment because the late learning curve is already nearly
flat.

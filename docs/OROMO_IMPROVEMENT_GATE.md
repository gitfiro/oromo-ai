# OromoLM language-improvement gate

The immediate goal is reproducible improvement in Oromo language modeling.
That goal is now established: exact v0.2 evaluation proved Oromo CPT improves
held-out Afaan Oromoo modeling, and the v0.3 +8K continuation reached near-parity
with the native-tokenizer CPT benchmark while passing the frozen WikiText
retention gate. A controlled +4K two-stage ablation has now completed training and frozen evaluation. Its Stage B learning curve crosses both the native-tokenizer CPT and +8K quality references, while checkpoints 1,250 and 1,517 both pass the predeclared WikiText retention ceiling. Under the frozen decision rules, +4K is now the strongest current tokenizer/model candidate.

## Three-way comparison

1. Original `google/gemma-3-1b-pt`, pinned to the pilot's original revision.
2. Native-tokenizer Gemma after the completed CPT pilot.
3. Gemma +8K after the completed CPT pilot, with its matching saved tokenizer.

Run `training/tools/evaluate_bpb.py` separately for each checkpoint against the
same frozen original-text validation JSONL. Do not pass packed `input_ids` files.
Use the same context, stride, numerical precision and hardware for every arm.

Example (replace checkpoint and output paths for each arm):

```bash
uv run python training/tools/evaluate_bpb.py \
  --model PATH_TO_FULL_CHECKPOINT \
  --data training/data/oromocorpus-cpt-pilot-v0.1/validation.jsonl \
  --expected-sha256 cd1872643749992c7d4e22dad9b7dbe34907f0a5f96204c3040d428fc749a3d8 \
  --context 1024 --stride 512 --dtype float32 --device cuda \
  --output training/reports/bpb/ARM-oromo.json
```

For a Hub model, provide `--revision` with the exact model commit. For a full
local checkpoint, model and tokenizer files are hashed in the result. If the
checkpoint does not contain its tokenizer, explicitly pass the matching frozen
`--tokenizer`. PEFT-only adapters are not supported by this entry point.

## Evaluation protocol

- Independent documents; one conditioning BOS; no scored EOS or padding.
- Every original text token is scored once, including the first text token.
- Overlapping token windows; context-only positions excluded from the sum.
- Unreduced float32 cross entropy summed in float64, then normalized by the
  exact original UTF-8 byte count. This is an exact accounting of computed NLL
  under the declared finite-context protocol, not infinite-context likelihood.
- Each tokenizer must round-trip the exact text; normalization or unknown-token
  failures stop evaluation instead of producing a misleading comparison.
- Same token context length does not mean identical character context across
  tokenizers. Report that protocol limitation alongside the comparison.
- Overall and per-source results, per-record hashes/metrics, input hash,
  evaluator hash, package versions and model identity are preserved.
- New output paths are required; earlier measurements are never overwritten.

These scores use a document-reset/BOS protocol and are not directly comparable
to the earlier packed-stream reconstruction. Re-score all three arms together.
Check that the frozen validation set was excluded from all training and
vocabulary selection; exact-file hashing does not establish absence of leakage
or near-duplicate overlap by itself.

## General-language control and decision

A separate general-language control was frozen before the v0.3 continuation.
The approved retention rule was fixed before inspecting results:

```text
WikiText BPB <= 1.05 × untouched-Gemma WikiText BPB
```

Untouched Gemma measured 1.013254631 BPB on the frozen control, producing a
predeclared ceiling of 1.063917363 BPB.

- Lower Oromo BPB than original Gemma supports improvement through adaptation.
- Lower Oromo BPB than native-tokenizer CPT supports the +8K strategy specifically.
- Check per-source outcomes and paired per-record uncertainty before claiming
  robust gains; aggregate improvement alone may hide source regressions.
- General-language behavior also needs prompt-based checks and human review;
  a BPB control is only one signal.
- If native CPT is stronger, use it as the leading candidate for further work.
- Schedule a bounded additional training run only after this comparison; keep
  the same holdouts and record its compute limit before launching.

## v0.2 gate result — 2026-10-04

The exact three-way Oromo evaluation has now been completed on the frozen 1,503-record validation set.

| Model state | Exact BPB | Result |
| --- | ---: | --- |
| Original `google/gemma-3-1b-pt` | 2.670046 | baseline |
| Native tokenizer + Oromo CPT | **1.733832** | best current quality checkpoint |
| OromoLM +8K + Oromo CPT | 1.863339 | strong improvement over base; not yet parity with native CPT |

Lower is better.

The native-tokenizer CPT model reduces BPB by **35.06%** relative to untouched Gemma. OromoLM +8K reduces BPB by **30.21%** relative to untouched Gemma, but remains approximately **7.47% higher/worse than native-tokenizer CPT** after one epoch.

This closed the first part of the improvement gate: **Oromo continued pretraining is demonstrably effective.**

## v0.3 gate result — 2026-10-10

The bounded fresh-data +8K continuation experiment has now been completed.

| Checkpoint | Exact Oromo BPB | WikiText BPB | Retention |
| ---: | ---: | ---: | --- |
| 1,000 | 1.735902233 | 1.033682489 | PASS |
| 1,250 | 1.734835917 | 1.033754204 | PASS |
| 1,470 | **1.734823064** | **1.033754855** | **PASS** |

The native-tokenizer CPT benchmark remains **1.733832395 BPB**. The best +8K
checkpoint is therefore only about **0.057% higher/worse**, but it did not cross
the predeclared Oromo quality threshold. The tokenizer-selection gate remains
open.

See `docs/CPT_RERUN_V0_2_RESULTS.md` and
`docs/CPT_LEARNING_CURVE_V0_3_RESULTS.md`.

## Implementation status

The evaluator and protocol tests are committed and have been used for the
completed v0.2 and v0.3 GPU evaluations. The v0.3 A100 experiment was copied
back to the local research environment and verified against the RunPod-generated
SHA-256 manifest: **53 files checked, 0 failures**. Large checkpoints remain
outside normal Git.


## +4K ablation status — 2026-10-14

The predeclared Gemma +4K model-level ablation has completed both training stages.

Stage A exact Oromo result:

| Model state | Exact Oromo BPB |
| --- | ---: |
| Native-tokenizer CPT | **1.733832395** |
| +8K Stage A / v0.2 | 1.863338883 |
| +4K Stage A / v0.2-equivalent | **1.844463004** |

At the pilot-equivalent exposure, +4K is about **1.01% lower/better than +8K**, while remaining about **6.38% higher/worse than native CPT**. This supports the hypothesis that the smaller lexical augmentation adapts faster than +8K, but it is not the final decision endpoint.

Stage B completed the same fresh 10.039M-word continuation text used by the +8K v0.3 path and produced retained checkpoints at 250, 500, 750, 1000, 1250, 1500, and 1517 updates.

Final exact Oromo learning curve:

| Checkpoint | Oromo BPB |
| ---: | ---: |
| 250 | 1.781058836 |
| 500 | 1.744201370 |
| 750 | **1.727396376** |
| 1000 | **1.721889019** |
| 1250 | **1.720904266** |
| 1500 | **1.720890953** |
| 1517 | **1.720890950** |

The +4K path crosses both the native CPT line (**1.733832395**) and the +8K v0.3 line (**1.734823064**) by step 750.

Frozen WikiText retention:

| Checkpoint | WikiText BPB | Result |
| ---: | ---: | --- |
| 1250 | **1.030453326** | PASS |
| 1517 | **1.030463994** | PASS |

Both remain below the fixed ceiling of **1.063917363** and slightly outperform the +8K final WikiText result of **1.033754855**.

**Gate decision:** +4K is the strongest current candidate under the predeclared protocol. The numerical difference between steps 1250 and 1517 is negligible, so downstream selection should consider compute and broader evaluation rather than treating 1517's tiny edge as practically decisive.

The complete +4K run was preserved locally and verified against the RunPod SHA-256 manifest: **66 files checked, 0 failures**. See `docs/CPT_4K_ABLATION_RESULTS.md` and `docs/CPT_4K_ABLATION_PROTOCOL.md`.


### Source robustness check

The +4K step-1517 result was compared source-by-source and record-by-record
against the native CPT and +8K v0.3 references.

- +4K beats +8K on **6/6** source groups.
- +4K beats native CPT on **5/6** source groups.
- Wikimedia is the only source-level regression versus native CPT:
  **1.677692 vs 1.671917 BPB (+0.345%)**.
- Across all 1,503 matched records, +4K beats native CPT on **860 records
  (57.22%)** and beats +8K on **1,086 records (72.26%)**.
- Mean/median paired BPB deltas favor +4K in both comparisons.

This supports the gate decision while preserving an important caveat: the gain
is broad but not universal. Wikimedia and the record-level regression tail
should be explicitly represented in downstream OromoBench and error analysis.


### Paired uncertainty check

A 10,000-resample paired bootstrap over all 1,503 matched validation records
produced:

```text
+4K vs native CPT
mean delta: -0.013883567 BPB
95% CI:     [-0.020199325, -0.007414796]

+4K vs +8K v0.3
mean delta: -0.048155481 BPB
95% CI:     [-0.053106421, -0.043233026]
```

Both intervals remain entirely below zero, which strengthens the conclusion
that +4K is the leading candidate on the frozen Oromo evaluation set rather
than an aggregate-only fluctuation. This remains a holdout-specific result;
Wikimedia and record-level regressions still require explicit downstream
analysis.

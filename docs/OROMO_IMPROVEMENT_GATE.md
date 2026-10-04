# OromoLM language-improvement gate

The immediate goal is reproducible improvement in Oromo language modeling.
Current pilot results establish efficiency, while model-quality improvement
remains unproven. Evaluate existing checkpoints before scheduling more training.

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

Freeze a separate general-language control JSONL and its hash, excluded from
training. Evaluate all three arms using the same protocol. Agree on a maximum
acceptable relative BPB regression before inspecting these results. No numeric
acceptance threshold has been approved yet; this gate remains open.

- Lower Oromo BPB than original Gemma supports improvement through adaptation.
- Lower Oromo BPB than native-tokenizer CPT supports the +8K strategy specifically.
- Check per-source outcomes and paired per-record uncertainty before claiming
  robust gains; aggregate improvement alone may hide source regressions.
- General-language behavior also needs prompt-based checks and human review;
  a BPB control is only one signal.
- If native CPT is stronger, use it as the leading candidate for further work.
- Schedule a bounded additional training run only after this comparison; keep
  the same holdouts and record its compute limit before launching.

## Implementation status

The evaluator and three protocol unit tests are committed. Window coverage,
normalization and CLI checks pass in the development environment. An actual
model inference run remains required: this workspace has neither the pilot
checkpoints nor frozen validation text, and no installed PyTorch/Transformers
runtime. No new model-quality result or training run is claimed here.

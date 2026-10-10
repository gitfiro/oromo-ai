# OromoLM v0.3 GPU execution protocol

## Preflight result

The local CPU preflight for `oromolm-8k-cpt-learning-curve-v0.3` passed with:

```text
train sequences: 23,515
train tokens: 24,078,782
validation sequences: 245
validation tokens: 249,875
tokenizer length: 270,145
maximum token ID: 270,144
effective sequences/update: 16
planned optimizer steps: 1,470
```

Packed hashes:

```text
train:
14141a61f11755f8477ec2515e124fa46b071094547b6c46f35e294c4074c162

validation:
abb452f63a504884a875b7989fd31b34e4da5c6edfaa9cbf622ecc9cfb6c80dc
```

## GPU payload

Build locally with:

```bash
bash training/tools/build_v03_gpu_payload.sh
```

The payload intentionally includes only:

- preserved v0.2 +8K model;
- frozen +8K tokenizer;
- v0.3 packed train/validation;
- original Oromo validation text;
- frozen WikiText general control;
- v0.3 config;
- trainer/evaluator;
- Python environment lock files.

The resulting archive is ignored by Git.

## Order of operations on GPU

The forgetting baseline must be measured **before inspecting v0.3 checkpoint quality**.

### 1. Verify payload SHA

Compare the uploaded archive SHA-256 against the locally generated
`oromolm-v0.3-gpu-payload.tar.gz.sha256`.

### 2. Install environment

```bash
uv sync
```

### 3. Untouched-Gemma WikiText baseline

```bash
uv run python training/tools/evaluate_bpb.py \
  --model google/gemma-3-1b-pt \
  --data training/data/general-control-v0.1/validation.jsonl \
  --context 1024 \
  --stride 512 \
  --dtype float32 \
  --device cuda \
  --output training/reports/bpb/gemma-base-v0.3-wikitext-control.json
```

Record:

- NLL sum;
- scored tokens;
- UTF-8 bytes;
- NLL/byte;
- BPB;
- output report SHA-256.

The fixed general-language ceiling is then:

```text
general ceiling = 1.05 × untouched-Gemma WikiText BPB
```

### 4. Run v0.3 training

```bash
uv run python training/train_cpt.py \
  --config training/configs/oromolm-8k-cpt-learning-curve-v0.3.json \
  2>&1 | tee training/runs/oromolm-8k-cpt-learning-curve-v0.3/train.log
```

Expected model-only checkpoints:

```text
checkpoint-250
checkpoint-500
checkpoint-750
checkpoint-1000
checkpoint-1250
final_model   # step 1470
```

### 5. Exact evaluation

For each retained checkpoint, run the exact Oromo BPB evaluator on the frozen
1,503-record Oromo validation text and WikiText evaluator on the frozen
general-language control.

Selection rule remains:

```text
Oromo BPB < 1.733832395
AND
WikiText BPB <= 1.05 × untouched-Gemma WikiText BPB
```

Do not select based on Trainer eval loss across tokenizers.

#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$PWD}"
cd "$ROOT"

ARCHIVE="oromolm-v0.3-gpu-payload.tar.gz"

required=(
  "preserved/v0.2/training/runs/oromolm-8k-cpt-rerun-v0.2/final_model"
  "tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-8k"
  "training/packed/oromocorpus-cpt-continuation-v0.3/oromo8k/seq1024/train.jsonl"
  "training/packed/oromocorpus-cpt-continuation-v0.3/oromo8k/seq1024/validation.jsonl"
  "training/data/oromocorpus-cpt-pilot-v0.1/validation.jsonl"
  "training/data/general-control-v0.1/validation.jsonl"
  "training/configs/oromolm-8k-cpt-learning-curve-v0.3.json"
  "training/train_cpt.py"
  "training/tools/evaluate_bpb.py"
  "pyproject.toml"
  "uv.lock"
)

for path in "${required[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "Missing required payload path: $path" >&2
    exit 1
  fi
done

rm -f "$ARCHIVE" "$ARCHIVE.sha256"

tar -czf "$ARCHIVE" "${required[@]}"
sha256sum "$ARCHIVE" | tee "$ARCHIVE.sha256"

echo
du -h "$ARCHIVE"
echo "Payload ready: $ARCHIVE"

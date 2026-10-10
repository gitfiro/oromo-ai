"""Freeze a reproducible general-language control set for OromoLM.

The default source is Salesforce/wikitext, config wikitext-103-raw-v1,
validation split. Text is preserved exactly; only empty rows are excluded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCE_ID = "salesforce-wikitext-103-raw-v1"
LICENSE = "CC BY-SA 4.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def freeze_rows(rows):
    """Return deterministic JSON-ready records, preserving non-empty text exactly."""
    out = []
    seen = set()
    for index, row in enumerate(rows):
        text = row.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Non-string text at source row {index}")
        if not text.strip():
            continue
        digest = sha256_bytes(text.encode("utf-8"))
        if digest in seen:
            continue
        seen.add(digest)
        out.append({
            "record_id": f"wikitext103raw-valid-{index:06d}",
            "source": SOURCE_ID,
            "source_row": index,
            "split": "validation",
            "text": text,
            "text_sha256": digest,
        })
    if not out:
        raise ValueError("No non-empty control records")
    return out


def write_jsonl(path: Path, records) -> str:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite frozen control: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        for row in records:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return sha256_bytes(path.read_bytes())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default="Salesforce/wikitext")
    p.add_argument("--config", default="wikitext-103-raw-v1")
    p.add_argument("--split", default="validation")
    p.add_argument(
        "--revision",
        required=True,
        help="Immutable Hugging Face dataset commit SHA; never use a floating branch for a frozen control.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("training/data/general-control-v0.1/validation.jsonl"),
    )
    p.add_argument(
        "--manifest",
        type=Path,
        default=Path("training/data/general-control-v0.1/manifest.json"),
    )
    args = p.parse_args()

    if args.manifest.exists():
        p.error(f"Manifest exists; refusing to overwrite: {args.manifest}")

    from datasets import load_dataset
    from huggingface_hub import HfApi

    info = HfApi().dataset_info(args.dataset, revision=args.revision)
    resolved_revision = info.sha
    if resolved_revision != args.revision:
        p.error(
            "Revision did not resolve byte-for-byte to the requested immutable SHA: "
            f"requested={args.revision} resolved={resolved_revision}"
        )

    ds = load_dataset(
        args.dataset,
        args.config,
        split=args.split,
        revision=args.revision,
    )
    records = freeze_rows(ds)
    output_sha = write_jsonl(args.output, records)

    chars = sum(len(r["text"]) for r in records)
    utf8_bytes = sum(len(r["text"].encode("utf-8")) for r in records)
    whitespace_words = sum(len(r["text"].split()) for r in records)

    manifest = {
        "format_version": 1,
        "control_id": "general-control-wikitext103raw-v0.1",
        "purpose": "General-language catastrophic-forgetting control; never training data.",
        "dataset": args.dataset,
        "config": args.config,
        "split": args.split,
        "requested_revision": args.revision,
        "resolved_revision": resolved_revision,
        "source_id": SOURCE_ID,
        "license": LICENSE,
        "selection_policy": {
            "source_order_preserved": True,
            "text_normalization": "none",
            "empty_rows_excluded": True,
            "exact_text_deduplication": True,
            "sampling": "none; all unique non-empty validation rows",
        },
        "records": len(records),
        "characters": chars,
        "utf8_bytes": utf8_bytes,
        "whitespace_words": whitespace_words,
        "output": str(args.output),
        "output_sha256": output_sha,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Build fresh Oromo continuation data for OromoLM v0.3.

The v0.3 continuation set is selected only from the six accepted source artifacts
recorded in the frozen CPT pilot manifest. Every exact text appearing in the
v0.1 pilot train or validation split is excluded before selection.

Selection is tokenizer-independent:
- target size: whitespace words
- source allocation: proportional to remaining accepted source words
- within-source order: SHA-256(source_id + NUL + exact text)
- no normalization
- exact source-file hashes must match the frozen pilot manifest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


DEFAULT_PILOT_MANIFEST = Path(
    "training/data/oromocorpus-cpt-pilot-v0.1/manifest.json"
)
DEFAULT_PILOT_TRAIN = Path(
    "training/data/oromocorpus-cpt-pilot-v0.1/train.jsonl"
)
DEFAULT_PILOT_VALIDATION = Path(
    "training/data/oromocorpus-cpt-pilot-v0.1/validation.jsonl"
)
DEFAULT_OUTPUT = Path(
    "training/data/oromocorpus-cpt-continuation-v0.3/train.jsonl"
)
DEFAULT_MANIFEST = Path(
    "training/data/oromocorpus-cpt-continuation-v0.3/manifest.json"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rank_key(source_id: str, text: str) -> str:
    return hashlib.sha256(
        source_id.encode("utf-8") + b"\0" + text.encode("utf-8")
    ).hexdigest()


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON at {path}:{line_no}") from exc
            yield line_no, row


def pilot_text_hashes(paths: list[Path]) -> set[str]:
    hashes: set[str] = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        for line_no, row in read_jsonl(path):
            text = row.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Invalid pilot text at {path}:{line_no}")
            hashes.add(text_sha(text))
    return hashes


def proportional_targets(
    remaining_words: dict[str, int],
    target_words: int,
) -> dict[str, int]:
    total = sum(remaining_words.values())
    if total <= 0:
        raise ValueError("No remaining source words")
    if target_words <= 0:
        raise ValueError("target_words must be positive")
    if target_words > total:
        raise ValueError(
            f"Requested {target_words:,} words but only {total:,} remain"
        )

    raw = {
        source: target_words * words / total
        for source, words in remaining_words.items()
    }
    base = {source: math.floor(value) for source, value in raw.items()}
    remainder = target_words - sum(base.values())

    order = sorted(
        raw,
        key=lambda source: (-(raw[source] - base[source]), source),
    )
    for source in order[:remainder]:
        base[source] += 1

    return base


def select_to_word_target(candidates, target_words: int):
    selected = []
    words = 0
    for candidate in sorted(candidates, key=lambda x: (x["rank"], x["text_sha256"])):
        selected.append(candidate)
        words += candidate["words"]
        if words >= target_words:
            break
    if words < target_words:
        raise RuntimeError(
            f"Source exhausted at {words:,} words below target {target_words:,}"
        )
    return selected, words


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target-words", type=int, default=10_000_000)
    p.add_argument("--pilot-manifest", type=Path, default=DEFAULT_PILOT_MANIFEST)
    p.add_argument("--pilot-train", type=Path, default=DEFAULT_PILOT_TRAIN)
    p.add_argument("--pilot-validation", type=Path, default=DEFAULT_PILOT_VALIDATION)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = p.parse_args()

    if args.output.exists() or args.manifest.exists():
        p.error("Output or manifest already exists; frozen artifacts are never overwritten")

    pilot_manifest = json.loads(args.pilot_manifest.read_text(encoding="utf-8"))
    if pilot_manifest.get("status") != "frozen_pilot_dataset":
        p.error("Pilot manifest is not marked frozen_pilot_dataset")

    excluded_hashes = pilot_text_hashes(
        [args.pilot_train, args.pilot_validation]
    )

    source_candidates = {}
    source_stats = {}
    all_remaining_text_hashes = set()

    for source in pilot_manifest["sources"]:
        source_id = source["source_id"]
        path = Path(source["path"])
        expected_sha = source["sha256"]
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            raise RuntimeError(
                f"Source SHA mismatch for {source_id}: "
                f"expected={expected_sha} actual={actual_sha}"
            )

        candidates = []
        records = 0
        words_total = 0
        words_excluded = 0
        records_excluded = 0

        for line_no, row in read_jsonl(path):
            text = row.get(source.get("text_field", "text"))
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Invalid source text at {path}:{line_no}")

            records += 1
            words = len(text.split())
            words_total += words
            digest = text_sha(text)

            if digest in excluded_hashes:
                records_excluded += 1
                words_excluded += words
                continue

            if digest in all_remaining_text_hashes:
                raise RuntimeError(
                    "Unexpected exact duplicate across accepted sources after "
                    f"pilot exclusion: {source_id} line {line_no}"
                )
            all_remaining_text_hashes.add(digest)

            candidates.append(
                {
                    "source": source_id,
                    "source_line": line_no,
                    "text": text,
                    "text_sha256": digest,
                    "rank": rank_key(source_id, text),
                    "words": words,
                    "characters": len(text),
                    "utf8_bytes": len(text.encode("utf-8")),
                }
            )

        remaining_words = sum(x["words"] for x in candidates)
        source_candidates[source_id] = candidates
        source_stats[source_id] = {
            "source_path": str(path),
            "source_sha256": actual_sha,
            "available_records": records,
            "available_words_recounted": words_total,
            "pilot_overlap_records_excluded": records_excluded,
            "pilot_overlap_words_excluded": words_excluded,
            "remaining_records": len(candidates),
            "remaining_words": remaining_words,
        }

    remaining_words = {
        source: stats["remaining_words"]
        for source, stats in source_stats.items()
    }
    targets = proportional_targets(remaining_words, args.target_words)

    selected_all = []
    selected_stats = {}
    for source_id in sorted(source_candidates):
        selected, selected_words = select_to_word_target(
            source_candidates[source_id],
            targets[source_id],
        )
        selected_all.extend(selected)
        selected_stats[source_id] = {
            "target_words": targets[source_id],
            "selected_records": len(selected),
            "selected_words": selected_words,
            "selected_characters": sum(x["characters"] for x in selected),
            "selected_utf8_bytes": sum(x["utf8_bytes"] for x in selected),
        }

    # Stable final order independent of source iteration.
    selected_all.sort(key=lambda x: (x["rank"], x["source"], x["text_sha256"]))

    selected_hashes = {x["text_sha256"] for x in selected_all}
    overlap = selected_hashes & excluded_hashes
    if overlap:
        raise AssertionError(f"Pilot overlap is non-zero: {len(overlap)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        for item in selected_all:
            row = {
                "source": item["source"],
                "source_line": item["source_line"],
                "text": item["text"],
                "text_sha256": item["text_sha256"],
            }
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    output_sha = sha256_file(args.output)
    total_words = sum(x["words"] for x in selected_all)
    total_chars = sum(x["characters"] for x in selected_all)
    total_bytes = sum(x["utf8_bytes"] for x in selected_all)

    manifest = {
        "format_version": 1,
        "dataset": "oromocorpus-cpt-continuation-v0.3",
        "purpose": (
            "Fresh OromoLM +8K continuation data; excludes all exact text from "
            "the frozen v0.1 pilot train and validation splits."
        ),
        "selection": {
            "method": "deterministic SHA-256 source-scoped text ordering",
            "source_weighting": "proportional_to_remaining_accepted_source_words",
            "tokenizer_independent": True,
            "target_words": args.target_words,
            "unit": "whitespace_words",
            "text_normalization": "none",
            "pilot_exclusion": "global exact-text SHA-256",
        },
        "pilot": {
            "manifest_path": str(args.pilot_manifest),
            "manifest_sha256": sha256_file(args.pilot_manifest),
            "train_path": str(args.pilot_train),
            "train_sha256": sha256_file(args.pilot_train),
            "validation_path": str(args.pilot_validation),
            "validation_sha256": sha256_file(args.pilot_validation),
            "unique_exact_text_hashes_excluded": len(excluded_hashes),
        },
        "source_inventory": source_stats,
        "selected_per_source": selected_stats,
        "output": {
            "path": str(args.output),
            "sha256": output_sha,
            "records": len(selected_all),
            "words": total_words,
            "characters": total_chars,
            "utf8_bytes": total_bytes,
            "pilot_exact_text_overlap": len(overlap),
        },
        "status": "frozen_fresh_continuation",
    }

    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest["output"], indent=2, sort_keys=True))
    print()
    print("Per-source selection:")
    for source_id in sorted(selected_stats):
        x = selected_stats[source_id]
        print(
            f"  {source_id}: "
            f"{x['selected_records']:,} records / "
            f"{x['selected_words']:,} words"
        )


if __name__ == "__main__":
    main()

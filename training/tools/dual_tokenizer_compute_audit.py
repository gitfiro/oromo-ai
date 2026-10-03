from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from transformers import AutoTokenizer


NATIVE_TOKENIZER = "google/gemma-3-1b-pt"

OROMO_TOKENIZER = Path(
    "tokenizer/augmentation/artifacts/"
    "gemma-3-1b-pt-oromo-8k"
)

PILOT_DIR = Path(
    "training/data/oromocorpus-cpt-pilot-v0.1"
)

TRAIN = PILOT_DIR / "train.jsonl"
VALIDATION = PILOT_DIR / "validation.jsonl"

REPORT_DIR = Path(
    "training/reports/oromocorpus-cpt-pilot-v0.1"
)

REPORT_PATH = (
    REPORT_DIR / "dual_tokenizer_compute_audit.json"
)

SEQUENCE_LENGTHS = [512, 1024, 2048, 4096]
BATCH_SIZE = 256

EXPECTED = {
    "train": (
        "9c71050faca4be2700ccbfb94737a8e8"
        "f190f3d9a3325b70fec60745c48b1a0a"
    ),
    "validation": (
        "cd1872643749992c7d4e22dad9b7dbe3"
        "4907f0a5f96204c3040d428fc749a3d8"
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)

    return h.hexdigest()


def pct_reduction(old, new):
    if old == 0:
        return 0.0

    return (old - new) / old * 100.0


def pct_increase(old, new):
    if old == 0:
        return 0.0

    return (new - old) / old * 100.0


def empty_stats():
    return {
        "records": 0,
        "words": 0,
        "characters": 0,
        "native_content_tokens": 0,
        "oromo_content_tokens": 0,
        "native_total_tokens": 0,
        "oromo_total_tokens": 0,
    }


print("=== OromoLM Dual-Tokenizer Compute Audit ===")
print()


# -------------------------------------------------------
# 1. Verify frozen pilot data
# -------------------------------------------------------

print("1. Verifying frozen CPT pilot")
print("=" * 72)

for name, path in (
    ("train", TRAIN),
    ("validation", VALIDATION),
):
    digest = sha256_file(path)

    print(
        f"{name:<12} {digest}"
    )

    if digest != EXPECTED[name]:
        raise RuntimeError(
            f"{name} SHA-256 mismatch.\n"
            f"Expected: {EXPECTED[name]}\n"
            f"Actual:   {digest}"
        )

print("Input integrity: PASS")


# -------------------------------------------------------
# 2. Load tokenizers
# -------------------------------------------------------

print()
print("2. Loading tokenizers")
print("=" * 72)

native = AutoTokenizer.from_pretrained(
    NATIVE_TOKENIZER,
    use_fast=True,
)

oromo = AutoTokenizer.from_pretrained(
    OROMO_TOKENIZER,
    use_fast=True,
)

print(
    f"Native tokenizer length: {len(native):,}"
)

print(
    f"Oromo tokenizer length:  {len(oromo):,}"
)

if len(native) != 262_145:
    raise RuntimeError(
        "Unexpected native tokenizer length."
    )

if len(oromo) != 270_145:
    raise RuntimeError(
        "Unexpected Oromo tokenizer length."
    )

if native.eos_token_id is None:
    raise RuntimeError(
        "Native tokenizer has no EOS token."
    )

if oromo.eos_token_id is None:
    raise RuntimeError(
        "Oromo tokenizer has no EOS token."
    )

print(
    f"Native EOS ID: {native.eos_token_id:,}"
)

print(
    f"Oromo EOS ID:  {oromo.eos_token_id:,}"
)


# -------------------------------------------------------
# 3. Tokenization helpers
# -------------------------------------------------------

def process_batch(
    rows,
    overall,
    per_source,
):
    texts = [
        row["text"]
        for row in rows
    ]

    native_ids = native(
        texts,
        add_special_tokens=False,
        padding=False,
        truncation=False,
    )["input_ids"]

    oromo_ids = oromo(
        texts,
        add_special_tokens=False,
        padding=False,
        truncation=False,
    )["input_ids"]

    for row, n_ids, o_ids in zip(
        rows,
        native_ids,
        oromo_ids,
    ):
        text = row["text"]
        source = row["source"]

        words = len(text.split())
        chars = len(text)

        native_content = len(n_ids)
        oromo_content = len(o_ids)

        # One EOS token is counted after every source record.
        native_total = native_content + 1
        oromo_total = oromo_content + 1

        for stats in (
            overall,
            per_source[source],
        ):
            stats["records"] += 1
            stats["words"] += words
            stats["characters"] += chars

            stats[
                "native_content_tokens"
            ] += native_content

            stats[
                "oromo_content_tokens"
            ] += oromo_content

            stats[
                "native_total_tokens"
            ] += native_total

            stats[
                "oromo_total_tokens"
            ] += oromo_total


def audit_split(path: Path):
    overall = empty_stats()

    per_source = defaultdict(
        empty_stats
    )

    batch = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            if not line.strip():
                continue

            batch.append(
                json.loads(line)
            )

            if len(batch) >= BATCH_SIZE:
                process_batch(
                    batch,
                    overall,
                    per_source,
                )

                batch.clear()

        if batch:
            process_batch(
                batch,
                overall,
                per_source,
            )

    return overall, dict(per_source)


# -------------------------------------------------------
# 4. Tokenize both frozen splits
# -------------------------------------------------------

print()
print("3. Tokenizing frozen splits")
print("=" * 72)

results = {}

for split_name, path in (
    ("train", TRAIN),
    ("validation", VALIDATION),
):
    print()
    print(
        f"Auditing {split_name}..."
    )

    overall, per_source = audit_split(
        path
    )

    results[split_name] = {
        "overall": overall,
        "per_source": per_source,
    }

    print(
        f"  records: {overall['records']:,}"
    )

    print(
        f"  words:   {overall['words']:,}"
    )

    print(
        "  native tokens + EOS: "
        f"{overall['native_total_tokens']:,}"
    )

    print(
        "  Oromo tokens + EOS:  "
        f"{overall['oromo_total_tokens']:,}"
    )


# -------------------------------------------------------
# 5. Derived workload metrics
# -------------------------------------------------------

def derived(stats):
    words = stats["words"]

    native_tokens = stats[
        "native_total_tokens"
    ]

    oromo_tokens = stats[
        "oromo_total_tokens"
    ]

    native_chars_per_token = (
        stats["characters"]
        / native_tokens
    )

    oromo_chars_per_token = (
        stats["characters"]
        / oromo_tokens
    )

    result = {
        "native_tokens_per_word": (
            native_tokens / words
        ),
        "oromo_tokens_per_word": (
            oromo_tokens / words
        ),
        "token_reduction_percent": (
            pct_reduction(
                native_tokens,
                oromo_tokens,
            )
        ),
        "native_characters_per_token": (
            native_chars_per_token
        ),
        "oromo_characters_per_token": (
            oromo_chars_per_token
        ),
        "character_capacity_gain_percent": (
            pct_increase(
                native_chars_per_token,
                oromo_chars_per_token,
            )
        ),
        "packing": {},
    }

    for seq_len in SEQUENCE_LENGTHS:
        native_sequences = math.ceil(
            native_tokens / seq_len
        )

        oromo_sequences = math.ceil(
            oromo_tokens / seq_len
        )

        result["packing"][
            str(seq_len)
        ] = {
            "native_sequences": (
                native_sequences
            ),
            "oromo_sequences": (
                oromo_sequences
            ),
            "sequence_reduction_percent": (
                pct_reduction(
                    native_sequences,
                    oromo_sequences,
                )
            ),
        }

    return result


print()
print("4. Compute/workload comparison")
print("=" * 72)

derived_results = {}

for split_name in (
    "train",
    "validation",
):
    metrics = derived(
        results[split_name]["overall"]
    )

    derived_results[
        split_name
    ] = metrics

    print()
    print(split_name.upper())

    print(
        "  Native tokens/word: "
        f"{metrics['native_tokens_per_word']:.4f}"
    )

    print(
        "  Oromo tokens/word:  "
        f"{metrics['oromo_tokens_per_word']:.4f}"
    )

    print(
        "  Token reduction:    "
        f"{metrics['token_reduction_percent']:.2f}%"
    )

    print(
        "  Native chars/token: "
        f"{metrics['native_characters_per_token']:.4f}"
    )

    print(
        "  Oromo chars/token:  "
        f"{metrics['oromo_characters_per_token']:.4f}"
    )

    print(
        "  Context text gain:  "
        f"{metrics['character_capacity_gain_percent']:.2f}%"
    )

    print()
    print(
        "  Packed sequence counts:"
    )

    for seq_len in SEQUENCE_LENGTHS:
        p = metrics["packing"][
            str(seq_len)
        ]

        print(
            f"    {seq_len:>4}: "
            f"native={p['native_sequences']:>7,}  "
            f"oromo={p['oromo_sequences']:>7,}  "
            "reduction="
            f"{p['sequence_reduction_percent']:>6.2f}%"
        )


# -------------------------------------------------------
# 6. Per-source comparison
# -------------------------------------------------------

print()
print("5. Training split by source")
print("=" * 72)

source_derived = {}

for source, stats in sorted(
    results["train"][
        "per_source"
    ].items()
):
    metrics = derived(stats)

    source_derived[
        source
    ] = metrics

    print()
    print(source)

    print(
        f"  words: {stats['words']:,}"
    )

    print(
        "  native tok/word: "
        f"{metrics['native_tokens_per_word']:.4f}"
    )

    print(
        "  Oromo tok/word:  "
        f"{metrics['oromo_tokens_per_word']:.4f}"
    )

    print(
        "  reduction:       "
        f"{metrics['token_reduction_percent']:.2f}%"
    )


# -------------------------------------------------------
# 7. Vocabulary accounting
# -------------------------------------------------------

native_model_vocab = 262_144
oromo_model_vocab = 270_145

vocab_growth = pct_increase(
    native_model_vocab,
    oromo_model_vocab,
)

print()
print("6. Model vocabulary accounting")
print("=" * 72)

print(
    f"Native model vocab: {native_model_vocab:,}"
)

print(
    f"Oromo model vocab:  {oromo_model_vocab:,}"
)

print(
    f"Vocabulary growth:  {vocab_growth:.2f}%"
)

print()

print(
    "NOTE: token/sequence reduction is "
    "a workload reduction, not a direct "
    "GPU wall-clock speedup estimate."
)

print(
    "The Oromo model also has a larger "
    "embedding and LM-head vocabulary."
)


# -------------------------------------------------------
# 8. Write frozen report
# -------------------------------------------------------

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

report = {
    "format_version": 1,
    "audit": (
        "oromolm_dual_tokenizer_compute_audit"
    ),
    "pilot": {
        "train_path": str(TRAIN),
        "train_sha256": (
            EXPECTED["train"]
        ),
        "validation_path": (
            str(VALIDATION)
        ),
        "validation_sha256": (
            EXPECTED["validation"]
        ),
    },
    "tokenizers": {
        "native": {
            "identifier": (
                NATIVE_TOKENIZER
            ),
            "tokenizer_length": (
                len(native)
            ),
            "model_vocab_size": (
                native_model_vocab
            ),
        },
        "oromo_8k": {
            "identifier": (
                str(OROMO_TOKENIZER)
            ),
            "tokenizer_length": (
                len(oromo)
            ),
            "model_vocab_size": (
                oromo_model_vocab
            ),
        },
        "model_vocab_growth_percent": (
            vocab_growth
        ),
    },
    "boundary_policy": (
        "add_special_tokens=false; "
        "exactly one EOS token counted "
        "per source record"
    ),
    "splits": {},
    "train_per_source_derived": (
        source_derived
    ),
}

for split in (
    "train",
    "validation",
):
    report["splits"][split] = {
        "raw": (
            results[split]["overall"]
        ),
        "derived": (
            derived_results[split]
        ),
        "per_source": (
            results[split][
                "per_source"
            ]
        ),
    }

REPORT_PATH.write_text(
    json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

report_sha = sha256_file(
    REPORT_PATH
)

print()
print("7. Frozen audit report")
print("=" * 72)

print(REPORT_PATH)

print(
    f"SHA-256: {report_sha}"
)

print()
print("=" * 72)
print("SUCCESS")
print("=" * 72)

print(
    "Dual-tokenizer workload audit complete."
)
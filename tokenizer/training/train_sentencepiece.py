from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import sentencepiece as spm


DEFAULT_INPUT = Path(
    "tokenizer/training/"
    "afriberta_oromo_v0.1.2_tokenizer_train.txt"
)

DEFAULT_OUTPUT_ROOT = Path(
    "tokenizer/training/candidates"
)

DEFAULT_VOCAB_SIZES = (
    16000,
    24000,
    32000,
    48000,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train reproducible Afaan Oromoo "
            "SentencePiece tokenizer candidates."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Tokenizer training text corpus.",
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory containing tokenizer candidates.",
    )

    parser.add_argument(
        "--vocab-sizes",
        type=int,
        nargs="+",
        default=list(DEFAULT_VOCAB_SIZES),
        help="Vocabulary sizes to train.",
    )

    parser.add_argument(
        "--byte-fallback",
        action="store_true",
        help=(
            "Enable SentencePiece byte fallback so unseen "
            "Unicode can be represented without <unk>."
        ),
    )

    return parser.parse_args()


def train_candidate(
    *,
    input_path: Path,
    output_root: Path,
    vocab_size: int,
    byte_fallback: bool,
) -> None:
    suffix = "_byte" if byte_fallback else ""

    candidate_name = (
        f"oromo_unigram_"
        f"{vocab_size // 1000}k"
        f"{suffix}"
    )

    candidate_dir = (
        output_root / candidate_name
    )

    candidate_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_prefix = (
        candidate_dir / "tokenizer"
    )

    model_path = (
        model_prefix.with_suffix(".model")
    )

    vocab_path = (
        model_prefix.with_suffix(".vocab")
    )

    manifest_path = (
        candidate_dir / "manifest.json"
    )

    print()
    print("=" * 72)
    print(f"Training: {candidate_name}")
    print(
        f"Vocabulary size: {vocab_size:,}"
    )
    print(
        f"Byte fallback: {byte_fallback}"
    )
    print("=" * 72)

    spm.SentencePieceTrainer.train(
        input=str(input_path),
        model_prefix=str(model_prefix),

        # Candidate V1/V2 algorithm.
        model_type="unigram",

        vocab_size=vocab_size,

        # Preserve all characters observed in the tokenizer
        # training corpus.
        character_coverage=1.0,

        # Keep training deterministic with respect to corpus order.
        shuffle_input_sentence=False,

        # Use the entire prepared training corpus.
        input_sentence_size=0,

        # Preserve whitespace as much as SentencePiece allows.
        remove_extra_whitespaces=False,

        # Special-token IDs.
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,

        pad_piece="<pad>",
        unk_piece="<unk>",
        bos_piece="<s>",
        eos_piece="</s>",

        # Require the requested vocabulary size.
        hard_vocab_limit=True,

        # Unicode normalization used for all candidates so results
        # remain directly comparable.
        normalization_rule_name="nmt_nfkc",

        # Our processed corpus can contain relatively long records.
        max_sentence_length=16384,

        # Prevent extremely long learned pieces.
        max_sentencepiece_length=32,

        # Keep number handling unchanged between candidates.
        split_digits=False,

        # Candidate V2 enables this. It reserves byte pieces that can
        # represent characters not observed in the training corpus.
        byte_fallback=byte_fallback,
    )

    if not model_path.exists():
        raise RuntimeError(
            f"SentencePiece model was not created: {model_path}"
        )

    if not vocab_path.exists():
        raise RuntimeError(
            f"SentencePiece vocabulary was not created: {vocab_path}"
        )

    processor = (
        spm.SentencePieceProcessor(
            model_file=str(model_path)
        )
    )

    actual_vocab_size = (
        processor.get_piece_size()
    )

    if actual_vocab_size != vocab_size:
        raise RuntimeError(
            "Vocabulary-size mismatch: "
            f"requested {vocab_size:,}, "
            f"created {actual_vocab_size:,}"
        )

    # Verify the standard special-token IDs.
    expected_special_ids = {
        "pad_id": 0,
        "unk_id": 1,
        "bos_id": 2,
        "eos_id": 3,
    }

    actual_special_ids = {
        "pad_id": processor.pad_id(),
        "unk_id": processor.unk_id(),
        "bos_id": processor.bos_id(),
        "eos_id": processor.eos_id(),
    }

    if actual_special_ids != expected_special_ids:
        raise RuntimeError(
            "Unexpected special-token IDs: "
            f"{actual_special_ids}"
        )

    input_sha256 = sha256_file(
        input_path
    )

    model_sha256 = sha256_file(
        model_path
    )

    vocab_sha256 = sha256_file(
        vocab_path
    )

    manifest = {
        "format_version": 2,
        "candidate": candidate_name,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "sentencepiece_version": (
            spm.__version__
        ),
        "training": {
            "input": str(input_path),
            "input_sha256": input_sha256,
            "model_type": "unigram",
            "requested_vocab_size": (
                vocab_size
            ),
            "actual_vocab_size": (
                actual_vocab_size
            ),
            "character_coverage": 1.0,
            "normalization_rule_name": (
                "nmt_nfkc"
            ),
            "shuffle_input_sentence": (
                False
            ),
            "input_sentence_size": 0,
            "remove_extra_whitespaces": (
                False
            ),
            "max_sentence_length": (
                16384
            ),
            "max_sentencepiece_length": (
                32
            ),
            "split_digits": False,
            "byte_fallback": (
                byte_fallback
            ),
            "hard_vocab_limit": True,
        },
        "special_tokens": {
            "pad": {
                "piece": "<pad>",
                "id": processor.pad_id(),
            },
            "unk": {
                "piece": "<unk>",
                "id": processor.unk_id(),
            },
            "bos": {
                "piece": "<s>",
                "id": processor.bos_id(),
            },
            "eos": {
                "piece": "</s>",
                "id": processor.eos_id(),
            },
        },
        "artifacts": {
            "model": {
                "path": str(model_path),
                "sha256": model_sha256,
            },
            "vocab": {
                "path": str(vocab_path),
                "sha256": vocab_sha256,
            },
        },
    }

    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        f"Candidate: {candidate_name}"
    )
    print(
        f"Actual vocabulary: "
        f"{actual_vocab_size:,}"
    )
    print(
        f"Byte fallback: "
        f"{byte_fallback}"
    )
    print(
        f"Training SHA-256: "
        f"{input_sha256}"
    )
    print(
        f"Model: {model_path}"
    )
    print(
        f"Model SHA-256: "
        f"{model_sha256}"
    )
    print(
        f"Vocabulary: {vocab_path}"
    )
    print(
        f"Vocabulary SHA-256: "
        f"{vocab_sha256}"
    )
    print(
        f"Manifest: {manifest_path}"
    )
    print("PASS")


def main() -> None:
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            args.input
        )

    if not args.input.is_file():
        raise ValueError(
            f"Training input is not a file: "
            f"{args.input}"
        )

    if not args.vocab_sizes:
        raise ValueError(
            "At least one vocabulary size "
            "must be supplied."
        )

    if (
        len(set(args.vocab_sizes))
        != len(args.vocab_sizes)
    ):
        raise ValueError(
            "Vocabulary sizes must be unique."
        )

    for vocab_size in args.vocab_sizes:
        if vocab_size < 1000:
            raise ValueError(
                "Vocabulary size is "
                "suspiciously small: "
                f"{vocab_size}"
            )

    args.output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    training_sha256 = (
        sha256_file(args.input)
    )

    print(
        "=== Afaan Oromoo "
        "SentencePiece Candidate Training ==="
    )
    print(
        f"Training corpus: {args.input}"
    )
    print(
        f"Training SHA-256: "
        f"{training_sha256}"
    )
    print(
        "Vocabulary sizes: "
        + ", ".join(
            f"{size:,}"
            for size in args.vocab_sizes
        )
    )
    print(
        f"Byte fallback: "
        f"{args.byte_fallback}"
    )

    for vocab_size in args.vocab_sizes:
        train_candidate(
            input_path=args.input,
            output_root=args.output_root,
            vocab_size=vocab_size,
            byte_fallback=(
                args.byte_fallback
            ),
        )

    print()
    print("=" * 72)
    print(
        "All tokenizer candidates "
        "trained successfully."
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
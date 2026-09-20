from __future__ import annotations

import argparse
import json
from pathlib import Path

from oromo_ai.data.source_registry import (
    SourceRegistryEntry,
    find_source,
    load_registry,
)


DEFAULT_REGISTRY = Path(
    "data/sources/registry.jsonl"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect and validate the OromoCorpus "
            "source registry."
        )
    )

    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help=(
            "Path to source registry JSONL. "
            "Default: data/sources/registry.jsonl"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "list",
        help="List registered corpus sources.",
    )

    subparsers.add_parser(
        "validate",
        help=(
            "Validate every source registry entry."
        ),
    )

    show_parser = subparsers.add_parser(
        "show",
        help=(
            "Show one source by stable source_id."
        ),
    )

    show_parser.add_argument(
        "source_id",
        help=(
            "Stable source identifier to inspect."
        ),
    )

    return parser.parse_args()


def command_list(
    entries: list[SourceRegistryEntry],
) -> int:
    if not entries:
        print("Registry contains no sources.")
        return 0

    print(
        f"{'SOURCE ID':<40} "
        f"{'STATUS':<10} "
        f"{'TRAIN':<8} "
        f"{'REDIST':<8} "
        f"LICENSE"
    )

    print("-" * 100)

    for entry in entries:
        print(
            f"{entry.source_id:<40} "
            f"{entry.review_status:<10} "
            f"{entry.training_permission:<8} "
            f"{entry.redistribution_permission:<8} "
            f"{entry.license or '-'}"
        )

    print()
    print(
        f"Registered sources: {len(entries)}"
    )

    return 0


def command_validate(
    registry_path: Path,
    entries: list[SourceRegistryEntry],
) -> int:
    # load_registry() already validates individual entries
    # and duplicate source IDs. We explicitly validate again
    # here so this command remains an obvious integrity gate.
    for entry in entries:
        entry.validate()

    approved = sum(
        entry.review_status == "approved"
        for entry in entries
    )

    reviewing = sum(
        entry.review_status == "reviewing"
        for entry in entries
    )

    candidate = sum(
        entry.review_status == "candidate"
        for entry in entries
    )

    hold = sum(
        entry.review_status == "hold"
        for entry in entries
    )

    rejected = sum(
        entry.review_status == "rejected"
        for entry in entries
    )

    print(
        "=== OromoCorpus Source Registry Validation ==="
    )

    print(
        f"Registry: {registry_path}"
    )

    print(
        f"Entries: {len(entries)}"
    )

    print(
        f"Approved: {approved}"
    )

    print(
        f"Reviewing: {reviewing}"
    )

    print(
        f"Candidate: {candidate}"
    )

    print(
        f"Hold: {hold}"
    )

    print(
        f"Rejected: {rejected}"
    )

    print()
    print("Validation: PASS")

    return 0


def command_show(
    entries: list[SourceRegistryEntry],
    source_id: str,
) -> int:
    entry = find_source(
        entries,
        source_id,
    )

    if entry is None:
        print(
            f"Source not found: {source_id}"
        )
        return 1

    print(
        json.dumps(
            entry.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )

    return 0


def main() -> int:
    args = parse_args()

    registry_path: Path = args.registry

    if not registry_path.exists():
        print(
            f"Registry not found: "
            f"{registry_path}"
        )
        return 1

    try:
        entries = load_registry(
            registry_path
        )
    except ValueError as exc:
        print(
            f"Registry validation failed: "
            f"{exc}"
        )
        return 1

    if args.command == "list":
        return command_list(
            entries
        )

    if args.command == "validate":
        return command_validate(
            registry_path,
            entries,
        )

    if args.command == "show":
        return command_show(
            entries,
            args.source_id,
        )

    raise RuntimeError(
        f"Unhandled command: {args.command}"
    )


if __name__ == "__main__":
    raise SystemExit(main())

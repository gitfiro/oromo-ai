from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_RESULTS_DIR = Path("tokenizer/evaluation/results")


def load_results(results_dir: Path) -> list[dict[str, Any]]:
    """Load tokenizer benchmark JSON results from a directory."""
    results: list[dict[str, Any]] = []

    for path in sorted(results_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            result = json.load(handle)

        if "benchmark" not in result or "metrics" not in result:
            continue

        result["_result_path"] = str(path)
        results.append(result)

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare Afaan Oromoo tokenizer benchmark results."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory containing tokenizer benchmark JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    results = load_results(args.results_dir)

    if not results:
        raise RuntimeError(
            f"No benchmark JSON results found in {args.results_dir}"
        )

    sample_sizes = {
        result["benchmark"]["sample_size"]
        for result in results
    }

    corpora = {
        result["benchmark"]["corpus"]
        for result in results
    }

    if len(sample_sizes) != 1:
        raise RuntimeError(
            "Benchmark results use different sample sizes: "
            f"{sorted(sample_sizes)}"
        )

    if len(corpora) != 1:
        raise RuntimeError(
            "Benchmark results use different corpora: "
            f"{sorted(corpora)}"
        )

    results.sort(
        key=lambda result: result["metrics"]["tokens_per_word"]
    )

    print("=== Afaan Oromoo Tokenizer Comparison ===")
    print(f"Corpus: {next(iter(corpora))}")
    print(f"Sample size: {next(iter(sample_sizes)):,}")
    print()

    header = (
        f"{'Tokenizer':<35}"
        f"{'Vocab':>10}"
        f"{'Tok/Word':>12}"
        f"{'Frag %':>10}"
        f"{'Single %':>11}"
        f"{'UNK':>8}"
        f"{'Bytes/Tok':>12}"
    )

    print(header)
    print("-" * len(header))

    for result in results:
        benchmark = result["benchmark"]
        metrics = result["metrics"]

        tokenizer = benchmark["tokenizer"]

        print(
            f"{tokenizer:<35}"
            f"{metrics['vocabulary_size']:>10,}"
            f"{metrics['tokens_per_word']:>12.4f}"
            f"{metrics['word_fragmentation_rate'] * 100:>9.2f}%"
            f"{metrics['single_token_word_rate'] * 100:>10.2f}%"
            f"{metrics['unknown_tokens']:>8,}"
            f"{metrics['bytes_per_token']:>12.4f}"
        )


if __name__ == "__main__":
    main()
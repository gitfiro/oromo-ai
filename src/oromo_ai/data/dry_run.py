"""Non-destructive dry-run analysis for line-oriented Oromo corpora."""
from __future__ import annotations

import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .audit import _looks_like_repetition_artifact, classify_record
from .clean import clean_text
from .decide import decide_record


DRY_RUN_VERSION = "0.1.0"


def iter_text_lines(path: str | Path) -> Iterable[tuple[int, str]]:
    """Yield (1-based line number, text) from a UTF-8 line-oriented corpus."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            yield line_number, raw_line.rstrip("\r\n")


def _char_count(text: str) -> int:
    return len(text)


def _example(
    *,
    line_number: int,
    before: str,
    after: str | None,
    decision: str,
    reason: str,
) -> dict[str, object]:
    return {
        "line_number": line_number,
        "decision": decision,
        "reason": reason,
        "before": before,
        "after": after,
    }


def dry_run_text_corpus(
    path: str | Path,
    *,
    max_examples_per_category: int = 5,
) -> dict[str, object]:
    """
    Analyze a line-oriented text corpus without modifying or writing it.

    No input files are modified.
    No cleaned corpus is written.
    """
    if max_examples_per_category < 1:
        raise ValueError("max_examples_per_category must be >= 1")

    path = Path(path)

    decision_counts = Counter()
    reason_counts = Counter()
    audit_counts = Counter()
    clean_reason_counts = Counter()
    reject_reason_counts = Counter()

    total_records = 0
    total_input_chars = 0
    total_cleaned_chars = 0
    changed_records = 0
    empty_after_cleaning = 0
    pathological_repetition = 0

    examples: dict[str, list[dict[str, object]]] = {
        "KEEP": [],
        "CLEAN": [],
        "REJECT": [],
        "EMPTY_AFTER_CLEANING": [],
        "PATHOLOGICAL_REPETITION": [],
    }

    for line_number, original in iter_text_lines(path):
        total_records += 1
        total_input_chars += _char_count(original)

        audit_categories = classify_record(original)

        for audit_category in audit_categories:
            audit_counts[audit_category] += 1

        decision_name, reasons = decide_record(original)

        if isinstance(reasons, str):
            reasons = [reasons]
        else:
            reasons = list(reasons)

        decision_counts[decision_name] += 1

        for reason in reasons:
            reason_counts[reason] += 1

        primary_reason = reasons[0] if reasons else "no_reason"

        cleaned = original

        if decision_name == "CLEAN":
            cleaned = clean_text(original)

            clean_reason_counts[primary_reason] += 1

            if cleaned != original:
                changed_records += 1

            if not cleaned.strip():
                empty_after_cleaning += 1

                if len(examples["EMPTY_AFTER_CLEANING"]) < max_examples_per_category:
                    examples["EMPTY_AFTER_CLEANING"].append(
                        _example(
                            line_number=line_number,
                            before=original,
                            after=cleaned,
                            decision=decision_name,
                            reason="empty_after_cleaning",
                        )
                    )

            if len(examples["CLEAN"]) < max_examples_per_category:
                examples["CLEAN"].append(
                    _example(
                        line_number=line_number,
                        before=original,
                        after=cleaned,
                        decision=decision_name,
                        reason=primary_reason,
                    )
                )

        elif decision_name == "REJECT":
            reject_reason_counts[primary_reason] += 1

            if len(examples["REJECT"]) < max_examples_per_category:
                examples["REJECT"].append(
                    _example(
                        line_number=line_number,
                        before=original,
                        after=None,
                        decision=decision_name,
                        reason=primary_reason,
                    )
                )

        else:
            if len(examples["KEEP"]) < max_examples_per_category:
                examples["KEEP"].append(
                    _example(
                        line_number=line_number,
                        before=original,
                        after=original,
                        decision=decision_name,
                        reason=primary_reason,
                    )
                )

        total_cleaned_chars += _char_count(cleaned)

        if _looks_like_repetition_artifact(original):
            pathological_repetition += 1

            if len(examples["PATHOLOGICAL_REPETITION"]) < max_examples_per_category:
                examples["PATHOLOGICAL_REPETITION"].append(
                    _example(
                        line_number=line_number,
                        before=original,
                        after=cleaned,
                        decision=decision_name,
                        reason="repetition_signal",
                    )
                )

    total_chars_removed = total_input_chars - total_cleaned_chars

    return {
        "dry_run_version": DRY_RUN_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": str(path),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
        },
        "input_records": total_records,
        "decision_counts": dict(decision_counts),
        "reason_counts": dict(reason_counts),
        "audit_category_counts": dict(audit_counts),
        "clean_reason_counts": dict(clean_reason_counts),
        "reject_reason_counts": dict(reject_reason_counts),
        "input_characters": total_input_chars,
        "post_clean_characters": total_cleaned_chars,
        "characters_removed": total_chars_removed,
        "changed_records": changed_records,
        "unchanged_clean_decisions": (
            decision_counts.get("CLEAN", 0) - changed_records
        ),
        "empty_after_cleaning": empty_after_cleaning,
        "pathological_repetition": pathological_repetition,
        "change_rate": (
            changed_records / total_records if total_records else 0.0
        ),
        "character_reduction_rate": (
            total_chars_removed / total_input_chars
            if total_input_chars
            else 0.0
        ),
        "examples": examples,
        "non_destructive": True,
        "source_modified": False,
        "output_corpus_written": False,
    }


def write_dry_run_report(
    report: dict[str, object],
    output_path: str | Path,
) -> None:
    """Write the dry-run audit report as JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            report,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")


def format_dry_run_report(report: dict[str, object]) -> str:
    """Format a compact human-readable dry-run report."""
    decisions = report["decision_counts"]
    reasons = report["reason_counts"]

    lines = [
        "OROMO CORPUS DRY-RUN REPORT",
        "=" * 80,
        "",
        "NON-DESTRUCTIVE: NO SOURCE DATA WAS MODIFIED",
        "",
        f"Input records:          {report['input_records']:,}",
        "",
        "DECISIONS",
        "-" * 80,
        f"KEEP:                   {decisions.get('KEEP', 0):,}",
        f"CLEAN:                  {decisions.get('CLEAN', 0):,}",
        f"REJECT:                 {decisions.get('REJECT', 0):,}",
        "",
        "DECISION REASONS",
        "-" * 80,
    ]

    for reason, count in sorted(
        reasons.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        lines.append(f"{reason}: {count:,}")

    lines.extend(
        [
            "",
            "TEXT IMPACT",
            "-" * 80,
            f"Input characters:       {report['input_characters']:,}",
            f"Post-clean characters:  {report['post_clean_characters']:,}",
            f"Characters removed:     {report['characters_removed']:,}",
            f"Changed records:        {report['changed_records']:,}",
            f"Unchanged CLEAN:        {report['unchanged_clean_decisions']:,}",
            f"Empty after cleaning:   {report['empty_after_cleaning']:,}",
            f"Repetition signals:     {report['pathological_repetition']:,}",
            f"Change rate:            {report['change_rate']:.4%}",
            f"Character reduction:    {report['character_reduction_rate']:.4%}",
            "",
            "AUDIT CATEGORY COUNTS",
            "-" * 80,
        ]
    )

    for category, count in sorted(
        report["audit_category_counts"].items(),
        key=lambda item: (-item[1], item[0]),
    ):
        lines.append(f"{category}: {count:,}")

    lines.extend(
        [
            "",
            "The source corpus was read only.",
            "No cleaned corpus was written.",
            "No records were deleted.",
        ]
    )

    return "\n".join(lines)

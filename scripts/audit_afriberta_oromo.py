from pathlib import Path

from oromo_ai.data.audit import audit_jsonl_like_text


INPUT = Path("data/raw/afriberta_oromo/train/train.txt")
OUTPUT = Path("data/manifests/afriberta_oromo_cleaning_audit.json")


def main() -> None:
    stats = audit_jsonl_like_text(
        INPUT,
        OUTPUT,
        sample_limit=100,
    )

    print("\n=== AfriBERTa Afaan Oromoo Cleaning Audit ===")
    print(f"Input records:              {stats['input_records']:,}")
    print(f"Changed records:            {stats['changed_records']:,}")
    print(f"Unchanged records:          {stats['unchanged_records']:,}")
    print(f"Empty after cleaning:       {stats['empty_after_cleaning']:,}")
    print(f"Pathological repetition:    {stats['pathological_repetition']:,}")
    print(f"Input characters:           {stats['input_characters']:,}")
    print(f"Cleaned characters:         {stats['cleaned_characters']:,}")
    print(f"Characters removed:         {stats['characters_removed']:,}")
    print(f"Record change rate:         {stats['change_rate']:.4%}")
    print(f"Character reduction rate:   {stats['character_reduction_rate']:.4%}")
    print(f"\nReport: {OUTPUT}")


if __name__ == "__main__":
    main()

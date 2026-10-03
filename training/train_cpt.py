from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import time
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)


# ============================================================
# Utilities
# ============================================================


def sha256_file(path: Path) -> str:
    """Return SHA-256 digest for a file."""
    h = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def load_config(path: Path) -> dict:
    """Load experiment configuration JSON."""
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# Causal-LM collator
# ============================================================


class CausalLMCollator:
    """
    Collator for already-packed causal-LM sequences.

    Full sequences pass through unchanged.

    The final partial sequence is padded to the configured
    sequence length.

    Padding labels are set to -100 so padding positions
    do not contribute to the causal-LM loss.
    """

    def __init__(
        self,
        tokenizer,
        sequence_length: int,
    ):
        self.tokenizer = tokenizer
        self.sequence_length = sequence_length

        if tokenizer.pad_token_id is None:
            if tokenizer.eos_token_id is None:
                raise RuntimeError(
                    "Tokenizer has neither PAD nor EOS token."
                )

            tokenizer.pad_token = (
                tokenizer.eos_token
            )

    def __call__(
        self,
        features,
    ):
        batch_size = len(features)

        input_ids = torch.full(
            (
                batch_size,
                self.sequence_length,
            ),
            fill_value=(
                self.tokenizer.pad_token_id
            ),
            dtype=torch.long,
        )

        attention_mask = torch.zeros(
            (
                batch_size,
                self.sequence_length,
            ),
            dtype=torch.long,
        )

        labels = torch.full(
            (
                batch_size,
                self.sequence_length,
            ),
            fill_value=-100,
            dtype=torch.long,
        )

        for index, feature in enumerate(
            features
        ):
            ids = feature["input_ids"]

            if len(ids) > self.sequence_length:
                raise RuntimeError(
                    "Packed sequence exceeds "
                    "configured sequence length: "
                    f"{len(ids)} > "
                    f"{self.sequence_length}"
                )

            length = len(ids)

            ids_tensor = torch.tensor(
                ids,
                dtype=torch.long,
            )

            input_ids[
                index,
                :length,
            ] = ids_tensor

            attention_mask[
                index,
                :length,
            ] = 1

            labels[
                index,
                :length,
            ] = ids_tensor

        return {
            "input_ids": input_ids,
            "attention_mask": (
                attention_mask
            ),
            "labels": labels,
        }


# ============================================================
# Runtime callback
# ============================================================


class PilotMetricsCallback(
    TrainerCallback
):
    """Measure trainer wall-clock time."""

    def __init__(self):
        self.started = None

    def on_train_begin(
        self,
        args,
        state,
        control,
        **kwargs,
    ):
        self.started = (
            time.perf_counter()
        )

    def on_train_end(
        self,
        args,
        state,
        control,
        **kwargs,
    ):
        if self.started is None:
            return

        elapsed = (
            time.perf_counter()
            - self.started
        )

        print()
        print(
            "Measured Trainer wall time: "
            f"{elapsed:.2f} seconds"
        )


# ============================================================
# Dataset verification
# ============================================================


def validate_dataset(
    dataset,
    sequence_length: int,
    tokenizer_length: int,
    name: str,
) -> dict:
    """
    Validate an already-packed dataset.

    Checks:
    - non-empty dataset
    - sequence lengths
    - maximum token ID
    - total token count
    """

    if len(dataset) == 0:
        raise RuntimeError(
            f"{name} dataset is empty."
        )

    shortest = None
    longest = 0
    maximum_id = -1
    total_tokens = 0

    for row in dataset:
        ids = row["input_ids"]

        length = len(ids)

        if shortest is None:
            shortest = length
        else:
            shortest = min(
                shortest,
                length,
            )

        longest = max(
            longest,
            length,
        )

        total_tokens += length

        if ids:
            maximum_id = max(
                maximum_id,
                max(ids),
            )

    if longest > sequence_length:
        raise RuntimeError(
            f"{name}: sequence exceeds "
            f"configured sequence length "
            f"{sequence_length:,}. "
            f"Maximum observed: "
            f"{longest:,}"
        )

    if maximum_id >= tokenizer_length:
        raise RuntimeError(
            f"{name}: token ID "
            f"{maximum_id:,} is outside "
            f"tokenizer length "
            f"{tokenizer_length:,}."
        )

    return {
        "records": len(dataset),
        "tokens": total_tokens,
        "minimum_length": shortest,
        "maximum_length": longest,
        "maximum_token_id": maximum_id,
    }


# ============================================================
# GPU/runtime information
# ============================================================


def print_runtime_info():
    print()
    print("Runtime:")
    print(
        f"  Python: "
        f"{platform.python_version()}"
    )
    print(
        f"  PyTorch: "
        f"{torch.__version__}"
    )
    print(
        f"  CUDA available: "
        f"{torch.cuda.is_available()}"
    )

    if not torch.cuda.is_available():
        return

    device = torch.cuda.current_device()

    print(
        f"  GPU: "
        f"{torch.cuda.get_device_name(device)}"
    )

    properties = (
        torch.cuda.get_device_properties(
            device
        )
    )

    print(
        f"  VRAM: "
        f"{properties.total_memory / 1024**3:.2f} GiB"
    )

    print(
        f"  BF16 supported: "
        f"{torch.cuda.is_bf16_supported()}"
    )

    capability = (
        torch.cuda.get_device_capability(
            device
        )
    )

    print(
        f"  Compute capability: "
        f"{capability[0]}."
        f"{capability[1]}"
    )


# ============================================================
# Main
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Controlled OromoLM continued-"
            "pretraining pilot."
        )
    )

    parser.add_argument(
        "--config",
        required=True,
        help=(
            "Path to CPT experiment "
            "configuration JSON."
        ),
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Validate datasets/configuration "
            "without loading a model or "
            "performing training."
        ),
    )

    args = parser.parse_args()

    config_path = Path(
        args.config
    )

    cfg = load_config(
        config_path
    )

    experiment = cfg["experiment"]
    variant = cfg["variant"]

    output_dir = (
        Path("training/runs")
        / experiment
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "=== OromoLM CPT Pilot ==="
    )
    print()

    print(
        f"Experiment: {experiment}"
    )
    print(
        f"Variant:    {variant}"
    )
    print(
        f"Model:      {cfg['model']}"
    )
    print(
        f"Tokenizer:  "
        f"{cfg['tokenizer']}"
    )

    print_runtime_info()

    # --------------------------------------------------------
    # Dataset files
    # --------------------------------------------------------

    train_file = Path(
        cfg["train_file"]
    )

    validation_file = Path(
        cfg["validation_file"]
    )

    for path in (
        train_file,
        validation_file,
    ):
        if not path.exists():
            raise FileNotFoundError(
                path
            )

    train_sha = sha256_file(
        train_file
    )

    validation_sha = (
        sha256_file(
            validation_file
        )
    )

    print()
    print(
        "Packed dataset hashes:"
    )
    print(
        f"  train: "
        f"{train_sha}"
    )
    print(
        f"  validation: "
        f"{validation_sha}"
    )

    # --------------------------------------------------------
    # Tokenizer
    # --------------------------------------------------------

    print()
    print(
        "Loading tokenizer..."
    )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            cfg["tokenizer"],
            use_fast=True,
        )
    )

    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise RuntimeError(
                "Tokenizer has neither PAD "
                "nor EOS token."
            )

        tokenizer.pad_token = (
            tokenizer.eos_token
        )

    tokenizer_length = len(
        tokenizer
    )

    print(
        f"Tokenizer length: "
        f"{tokenizer_length:,}"
    )

    print(
        f"EOS token ID: "
        f"{tokenizer.eos_token_id:,}"
    )

    print(
        f"PAD token ID: "
        f"{tokenizer.pad_token_id:,}"
    )

    # --------------------------------------------------------
    # Load packed JSON datasets
    # --------------------------------------------------------

    print()
    print(
        "Loading packed datasets..."
    )

    dataset = load_dataset(
        "json",
        data_files={
            "train": str(
                train_file
            ),
            "validation": str(
                validation_file
            ),
        },
    )

    train_stats = (
        validate_dataset(
            dataset["train"],
            cfg["sequence_length"],
            tokenizer_length,
            "train",
        )
    )

    validation_stats = (
        validate_dataset(
            dataset[
                "validation"
            ],
            cfg[
                "sequence_length"
            ],
            tokenizer_length,
            "validation",
        )
    )

    print()
    print(
        "Dataset validation:"
    )

    for name, stats in (
        (
            "train",
            train_stats,
        ),
        (
            "validation",
            validation_stats,
        ),
    ):
        print(
            f"  {name}:"
        )
        print(
            f"    sequences: "
            f"{stats['records']:,}"
        )
        print(
            f"    tokens: "
            f"{stats['tokens']:,}"
        )
        print(
            f"    length range: "
            f"{stats['minimum_length']:,}"
            f"–"
            f"{stats['maximum_length']:,}"
        )
        print(
            f"    max token ID: "
            f"{stats['maximum_token_id']:,}"
        )

    # --------------------------------------------------------
    # Training plan
    # --------------------------------------------------------

    microbatch = cfg[
        "per_device_train_batch_size"
    ]

    accumulation = cfg[
        "gradient_accumulation_steps"
    ]

    effective_batch = (
        microbatch
        * accumulation
    )

    batches_per_epoch = math.ceil(
        train_stats["records"]
        / microbatch
    )

    planned_epoch_steps = math.ceil(
        batches_per_epoch
        / accumulation
    )

    max_steps = cfg.get(
        "max_steps",
        -1,
    )

    if max_steps > 0:
        planned_optimizer_steps = (
            max_steps
        )
    else:
        planned_optimizer_steps = (
            math.ceil(
                planned_epoch_steps
                * cfg[
                    "num_train_epochs"
                ]
            )
        )

    estimated_tokens_per_update = (
        effective_batch
        * cfg["sequence_length"]
    )

    print()
    print(
        "Planned training:"
    )

    print(
        f"  epochs: "
        f"{cfg['num_train_epochs']}"
    )

    print(
        f"  max steps override: "
        f"{max_steps}"
    )

    print(
        f"  sequence length: "
        f"{cfg['sequence_length']:,}"
    )

    print(
        f"  microbatch: "
        f"{microbatch}"
    )

    print(
        f"  accumulation: "
        f"{accumulation}"
    )

    print(
        "  effective sequences/update: "
        f"{effective_batch}"
    )

    print(
        f"  approx tokens/update: "
        f"{estimated_tokens_per_update:,}"
    )

    print(
        f"  optimizer steps/epoch: "
        f"{planned_epoch_steps:,}"
    )

    print(
        f"  planned optimizer steps: "
        f"{planned_optimizer_steps:,}"
    )

    # --------------------------------------------------------
    # Preflight manifest
    # --------------------------------------------------------

    validation_manifest = {
        "format_version": 1,
        "experiment": experiment,
        "variant": variant,
        "config_path": str(
            config_path
        ),
        "config_sha256": (
            sha256_file(
                config_path
            )
        ),
        "model": cfg[
            "model"
        ],
        "tokenizer": cfg[
            "tokenizer"
        ],
        "tokenizer_length": (
            tokenizer_length
        ),
        "train_file": str(
            train_file
        ),
        "train_sha256": (
            train_sha
        ),
        "validation_file": str(
            validation_file
        ),
        "validation_sha256": (
            validation_sha
        ),
        "sequence_length": cfg[
            "sequence_length"
        ],
        "num_train_epochs": cfg[
            "num_train_epochs"
        ],
        "max_steps": max_steps,
        "train": train_stats,
        "validation": (
            validation_stats
        ),
        "effective_sequences_per_update": (
            effective_batch
        ),
        "estimated_tokens_per_update": (
            estimated_tokens_per_update
        ),
        "planned_optimizer_steps_per_epoch": (
            planned_epoch_steps
        ),
        "planned_optimizer_steps": (
            planned_optimizer_steps
        ),
    }

    preflight_path = (
        output_dir
        / "preflight.json"
    )

    preflight_path.write_text(
        json.dumps(
            validation_manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "Preflight manifest:"
    )
    print(
        preflight_path
    )

    if args.validate_only:
        print()
        print(
            "=" * 72
        )
        print(
            "PREFLIGHT SUCCESS"
        )
        print(
            "=" * 72
        )
        print(
            "No model was loaded and "
            "no training was performed."
        )
        return

    # --------------------------------------------------------
    # GPU requirements
    # --------------------------------------------------------

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU required for CPT "
            "training. Use --validate-only "
            "on CPU systems."
        )

    if (
        cfg.get(
            "bf16",
            False,
        )
        and not torch.cuda.is_bf16_supported()
    ):
        raise RuntimeError(
            "Configuration requests BF16 "
            "but this GPU does not report "
            "BF16 support."
        )

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print()
    print(
        "Loading model..."
    )

    requested_dtype = (
        torch.bfloat16
        if cfg.get(
            "bf16",
            False,
        )
        else torch.float32
    )

    model = (
        AutoModelForCausalLM
        .from_pretrained(
            cfg["model"],
            dtype=requested_dtype,
            low_cpu_mem_usage=True,
        )
    )

    input_embedding_rows = (
        model
        .get_input_embeddings()
        .weight
        .shape[0]
    )

    output_embeddings = (
        model
        .get_output_embeddings()
    )

    if output_embeddings is None:
        raise RuntimeError(
            "Model has no output "
            "embedding / LM head."
        )

    output_embedding_rows = (
        output_embeddings
        .weight
        .shape[0]
    )

    print()
    print(
        "Model vocabulary:"
    )
    print(
        f"  tokenizer length: "
        f"{tokenizer_length:,}"
    )
    print(
        f"  input rows:       "
        f"{input_embedding_rows:,}"
    )
    print(
        f"  output rows:      "
        f"{output_embedding_rows:,}"
    )
    print(
        f"  config vocab:     "
        f"{model.config.vocab_size:,}"
    )

    # --------------------------------------------------------
    # Gemma native tokenizer special case
    #
    # The stock Gemma tokenizer has 262,145 entries because
    # ID 262,144 is <image_soft_token>, while the text-only
    # 1B model has 262,144 model-backed rows.
    #
    # Native packed training data never uses that ID.
    # --------------------------------------------------------

    if variant == "native":
        if tokenizer_length != 262_145:
            raise RuntimeError(
                "Unexpected native Gemma "
                "tokenizer length."
            )

        if input_embedding_rows != 262_144:
            raise RuntimeError(
                "Unexpected native Gemma "
                "embedding row count."
            )

        if (
            train_stats[
                "maximum_token_id"
            ]
            >= input_embedding_rows
        ):
            raise RuntimeError(
                "Native dataset contains "
                "a token ID with no model "
                "embedding row."
            )

        if (
            validation_stats[
                "maximum_token_id"
            ]
            >= input_embedding_rows
        ):
            raise RuntimeError(
                "Native validation dataset "
                "contains a token ID with "
                "no model embedding row."
            )

        print(
            "  native tokenizer/model "
            "off-by-one boundary: SAFE"
        )

    else:
        # OromoLM must have a fully aligned
        # tokenizer and model vocabulary.
        if (
            input_embedding_rows
            != tokenizer_length
        ):
            raise RuntimeError(
                "OromoLM input embedding "
                "rows do not match tokenizer "
                "length."
            )

        if (
            output_embedding_rows
            != tokenizer_length
        ):
            raise RuntimeError(
                "OromoLM output embedding "
                "rows do not match tokenizer "
                "length."
            )

        if (
            model.config.vocab_size
            != tokenizer_length
        ):
            raise RuntimeError(
                "OromoLM config vocab_size "
                "does not match tokenizer."
            )

    # Verify tied embeddings where expected.
    embeddings_tied = (
        model
        .get_input_embeddings()
        .weight
        .data_ptr()
        ==
        model
        .get_output_embeddings()
        .weight
        .data_ptr()
    )

    print(
        f"  embeddings tied: "
        f"{embeddings_tied}"
    )

    if (
        model.config.tie_word_embeddings
        and not embeddings_tied
    ):
        raise RuntimeError(
            "Model expects tied embeddings "
            "but input/output weights are "
            "not tied."
        )

    # --------------------------------------------------------
    # Gradient checkpointing
    # --------------------------------------------------------

    if cfg.get(
        "gradient_checkpointing",
        False,
    ):
        model.config.use_cache = False

    # --------------------------------------------------------
    # Data collator
    # --------------------------------------------------------

    collator = CausalLMCollator(
        tokenizer=tokenizer,
        sequence_length=cfg[
            "sequence_length"
        ],
    )

    # --------------------------------------------------------
    # Trainer configuration
    # --------------------------------------------------------

    print()
    print(
        "Creating TrainingArguments..."
    )

    training_args = TrainingArguments(
        output_dir=str(
            output_dir
            / "checkpoints"
        ),

        overwrite_output_dir=False,

        num_train_epochs=cfg[
            "num_train_epochs"
        ],

        max_steps=max_steps,

        per_device_train_batch_size=(
            cfg[
                "per_device_train_batch_size"
            ]
        ),

        per_device_eval_batch_size=(
            cfg[
                "per_device_eval_batch_size"
            ]
        ),

        gradient_accumulation_steps=(
            cfg[
                "gradient_accumulation_steps"
            ]
        ),

        learning_rate=cfg[
            "learning_rate"
        ],

        weight_decay=cfg[
            "weight_decay"
        ],

        warmup_ratio=cfg[
            "warmup_ratio"
        ],

        lr_scheduler_type=(
            cfg.get(
                "lr_scheduler_type",
                "cosine",
            )
        ),

        optim=cfg.get(
            "optim",
            "adamw_torch_fused",
        ),

        max_grad_norm=cfg.get(
            "max_grad_norm",
            1.0,
        ),

        bf16=cfg.get(
            "bf16",
            False,
        ),

        tf32=cfg.get(
            "tf32",
            True,
        ),

        gradient_checkpointing=(
            cfg.get(
                "gradient_checkpointing",
                False,
            )
        ),

        eval_strategy=cfg.get(
            "eval_strategy",
            "steps",
        ),

        eval_steps=cfg.get(
            "eval_steps",
            50,
        ),

        save_strategy=cfg.get(
            "save_strategy",
            "steps",
        ),

        save_steps=cfg.get(
            "save_steps",
            100,
        ),

        save_total_limit=cfg.get(
            "save_total_limit",
            2,
        ),

        logging_strategy="steps",

        logging_steps=cfg.get(
            "logging_steps",
            10,
        ),

        logging_first_step=True,

        include_num_input_tokens_seen=True,

        prediction_loss_only=True,

        report_to="none",

        seed=cfg.get(
            "seed",
            42,
        ),

        data_seed=cfg.get(
            "data_seed",
            42,
        ),

        dataloader_num_workers=(
            cfg.get(
                "dataloader_num_workers",
                2,
            )
        ),

        dataloader_pin_memory=True,

        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=(
            dataset["train"]
        ),
        eval_dataset=(
            dataset[
                "validation"
            ]
        ),
        processing_class=tokenizer,
        data_collator=collator,
        callbacks=[
            PilotMetricsCallback()
        ],
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print()
    print(
        "=" * 72
    )
    print(
        "STARTING TRAINING"
    )
    print(
        "=" * 72
    )

    total_start = (
        time.perf_counter()
    )

    train_result = (
        trainer.train()
    )

    train_elapsed = (
        time.perf_counter()
        - total_start
    )

    # --------------------------------------------------------
    # Final evaluation
    # --------------------------------------------------------

    print()
    print(
        "Running final evaluation..."
    )

    eval_start = (
        time.perf_counter()
    )

    eval_result = (
        trainer.evaluate()
    )

    eval_elapsed = (
        time.perf_counter()
        - eval_start
    )

    total_elapsed = (
        time.perf_counter()
        - total_start
    )

    # --------------------------------------------------------
    # Derived throughput
    # --------------------------------------------------------

    actual_train_tokens = (
        train_result.metrics.get(
            "num_input_tokens_seen",
            None,
        )
    )

    if actual_train_tokens is not None:
        tokens_per_second = (
            actual_train_tokens
            / train_elapsed
        )
    else:
        tokens_per_second = None

    peak_allocated = (
        torch.cuda.max_memory_allocated()
    )

    peak_reserved = (
        torch.cuda.max_memory_reserved()
    )

    # --------------------------------------------------------
    # Save final model
    # --------------------------------------------------------

    final_model_dir = (
        output_dir
        / "final_model"
    )

    print()
    print(
        "Saving final model..."
    )

    trainer.save_model(
        str(
            final_model_dir
        )
    )

    tokenizer.save_pretrained(
        final_model_dir
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {
        "format_version": 1,
        "experiment": experiment,
        "variant": variant,

        "config": {
            "path": str(
                config_path
            ),
            "sha256": (
                sha256_file(
                    config_path
                )
            ),
        },

        "datasets": {
            "train": {
                "path": str(
                    train_file
                ),
                "sha256": (
                    train_sha
                ),
                **train_stats,
            },
            "validation": {
                "path": str(
                    validation_file
                ),
                "sha256": (
                    validation_sha
                ),
                **validation_stats,
            },
        },

        "model": cfg[
            "model"
        ],

        "tokenizer": cfg[
            "tokenizer"
        ],

        "tokenizer_length": (
            tokenizer_length
        ),

        "model_vocab_size": (
            model.config.vocab_size
        ),

        "max_steps": (
            max_steps
        ),

        "planned_optimizer_steps": (
            planned_optimizer_steps
        ),

        "runtime": {
            "gpu": (
                torch.cuda
                .get_device_name(0)
            ),
            "pytorch": (
                torch.__version__
            ),
            "train_wall_time_seconds": (
                train_elapsed
            ),
            "eval_wall_time_seconds": (
                eval_elapsed
            ),
            "total_wall_time_seconds": (
                total_elapsed
            ),
        },

        "memory": {
            "peak_allocated_bytes": (
                peak_allocated
            ),
            "peak_allocated_gib": (
                peak_allocated
                / 1024**3
            ),
            "peak_reserved_bytes": (
                peak_reserved
            ),
            "peak_reserved_gib": (
                peak_reserved
                / 1024**3
            ),
        },

        "throughput": {
            "num_input_tokens_seen": (
                actual_train_tokens
            ),
            "tokens_per_second": (
                tokens_per_second
            ),
        },

        "train_metrics": (
            train_result.metrics
        ),

        "eval_metrics": (
            eval_result
        ),
    }

    summary_path = (
        output_dir
        / "run_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    summary_sha = (
        sha256_file(
            summary_path
        )
    )

    # --------------------------------------------------------
    # Final console report
    # --------------------------------------------------------

    print()
    print(
        "=" * 72
    )
    print(
        "TRAINING COMPLETE"
    )
    print(
        "=" * 72
    )

    print(
        f"Experiment: "
        f"{experiment}"
    )

    print(
        f"Train wall time: "
        f"{train_elapsed:.2f} seconds"
    )

    print(
        f"Eval wall time:  "
        f"{eval_elapsed:.2f} seconds"
    )

    print(
        f"Total wall time: "
        f"{total_elapsed:.2f} seconds"
    )

    print(
        f"Peak allocated VRAM: "
        f"{peak_allocated / 1024**3:.2f} GiB"
    )

    print(
        f"Peak reserved VRAM:  "
        f"{peak_reserved / 1024**3:.2f} GiB"
    )

    if tokens_per_second is not None:
        print(
            f"Training throughput: "
            f"{tokens_per_second:,.2f} "
            f"tokens/sec"
        )

    if "eval_loss" in eval_result:
        print(
            f"Final eval loss: "
            f"{eval_result['eval_loss']:.6f}"
        )

    print()
    print(
        f"Final model:"
    )
    print(
        final_model_dir
    )

    print()
    print(
        f"Run summary:"
    )
    print(
        summary_path
    )

    print(
        f"Summary SHA-256:"
    )
    print(
        summary_sha
    )


if __name__ == "__main__":
    main()
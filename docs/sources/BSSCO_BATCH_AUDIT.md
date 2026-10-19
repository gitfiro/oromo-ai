# BSSCO batch yield audit

This tool replaces manual page-by-page experiments with a resumable candidate audit. It does not promote data or change accepted corpus accounting.

## Run the existing 30-PDF sample

From the project root, with Poppler, Tesseract `eng` and `amh`, and Pillow available:

```bash
uv run --with pillow python scripts/audit_bssco.py \
  --pdf-dir data/candidates/oromia-legal-government-v0.1/sample/stratified-30/raw \
  --out-dir data/candidates/oromia-legal-government-v0.1/sample/batch-audit-v0.1 \
  --workers 2
```

The command checks that exactly 30 PDFs exist. It uses that existing sample without resampling. PDF discovery is recursive and case-insensitive. It downloads nothing and modifies no source PDFs. Two document workers each use one Tesseract thread. OCR can still take substantial CPU time on scan-heavy documents; page progress prints as work completes.

If the process is interrupted, rerun the identical command. Completed page checkpoints are reused only when the source PDF, script, DPI, tool versions, and OCR model hashes match. Failed pages are retried; a document failure makes the command exit nonzero and marks the summary incomplete. A final summary is produced after the workers finish.

For actual reference-token measurement of the candidates, append both arguments below using the locally frozen tokenizer. The hash is from the tracked 48K byte-fallback tokenizer manifest used for current corpus accounting:

```bash
  --tokenizer tokenizer/training/candidates/oromo_unigram_48k_byte/tokenizer.model \
  --tokenizer-sha256 79d64021d85877c1544e7e3a26bb21d2ad15f0aa7c6e76aeeeed3efddc5c3d2f
```

No token estimate is fabricated if the tokenizer is omitted. Measured candidate tokens are before cross-source deduplication and remain outside the accepted total.

## Outputs

- `summary.json`: completed/failed PDFs, candidate page/word yield, optional measured reference tokens, file hashes, input inventory, tool/model versions, and limitations.
- `oromo-candidates.jsonl`: at most one passing region per page, with PDF hash/path, page, extraction method, crop, rotation, language evidence, and candidate-only status. Exact duplicate text within the sample is removed from this output.
- `checkpoints/`: every attempted region's text, evidence, warnings, and decision, including rejected attempts for manual review.

Outputs under `data/candidates/` are already ignored by Git. Original URLs are not inferred from filenames: join the PDF hashes/paths to the existing source inventory before creating an acceptance manifest.

## Extraction behavior and limits

1. Inspect embedded words with Poppler bounding boxes, trying full page, left 38%, middle third, and right third.
2. If no region passes, render at 300 DPI and OCR the full page in four counterclockwise rotations.
3. If a full-page candidate passes, retain it. Otherwise try the crop hypotheses at the strongest coherent orientation, falling back to all four orientations when evidence is weak.
4. Compare Amharic OCR diagnostically when no Oromo candidate is found. Count actual OCR words across scripts; Latin token counts are a separate metric.
5. Require multiple distinct Oromo markers, sufficient text, low English/Ethiopic contamination, and OCR confidence before candidate retention. Unknown text stays in review.

Thresholds and region hypotheses are uncalibrated heuristics. Confidence is not a calibrated language probability and is not directly comparable across OCR models. This tool does not claim production-level precision from four demonstration pages. Fixed crops can miss or split valid content, and false candidates remain possible. Only one region per page is retained to avoid overlapping-region duplication; embedded pages that pass bypass OCR. Yield is consequently a partial candidate measure, not a full archive yield estimate.

Review passing regions and rejected regions across different PDFs and layouts before trusting the routing. Text receives only NFC normalization and edge whitespace trimming. No guessed spelling corrections or automatic hyphen joining are applied.

After review: rights/provenance decision, cleanup and quality validation, exact and canonical near deduplication against every accepted source, frozen 48K measurement, artifact hashes, then promotion. The accepted baseline remains **94,230,190**, and this tool always reports **0 accepted-token delta**.

## Validation

```bash
python -m unittest discover -s tests/data -p test_bssco_audit.py -v
```

Routing tests cover clean Oromo, English/mixed rejection, low-confidence rejection, repeated-marker rejection, Ethiopic word counting, bounding-box region isolation, and conservative normalization. Real BSSCO yield and classification quality must still be verified on the user's local PDFs.

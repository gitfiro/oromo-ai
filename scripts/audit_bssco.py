#!/usr/bin/env python3
"""Resumable BSSCO PDF yield audit. Outputs are candidates, never accepted data."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter

VERSION = "bssco-audit-0.1"
OROMO = set("akka akkaataa akkasumas aangoo bara bahe dambii fi hojii irratti irraa jira kana keessatti keewwata kutaa labsii mata mootummaa naannoo oromiyaa oromiya oromiyaa qaba qaban taee ta'e ta'u tumaalee uummata waan yeroo jechuun fuula bulchiinsa nageenya misooma mirga mirgoota hojii seera seeraa namni nama irratti keessatti".split())
ENGLISH = set("the and of to in shall government article region regional proclamation chapter policy state this that with for from rights economic development any or be have as by a an is are on under not which".split())
# Hypotheses, not universal layouts. Keep at most one region per page.
REGIONS = {"full": (0, 1), "left38": (0, .38),
           "middle": (1 / 3, 2 / 3), "right": (2 / 3, 1)}


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command):
    env = dict(os.environ, OMP_THREAD_LIMIT="1", LC_ALL="C.UTF-8")
    p = subprocess.run(command, capture_output=True, text=True,
                       timeout=180, env=env)
    if p.returncode:
        raise RuntimeError(f"{command[0]} failed: {p.stderr[-1500:]}")
    return p.stdout, p.stderr


def normalize(text):
    # Do not guess spelling, rejoin hyphens, or remove unfamiliar words.
    return unicodedata.normalize("NFC", text).strip()


def evidence(text, confidence=None):
    normalized = normalize(text).replace("’", "'").lower()
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)*", normalized)
    oro = [t for t in tokens if t in OROMO]
    eng = [t for t in tokens if t in ENGLISH]
    letters = [c for c in normalized if c.isalpha()]
    eth = sum('\u1200' <= c <= '\u137f' or '\u1380' <= c <= '\u139f'
              or '\u2d80' <= c <= '\u2ddf' for c in letters)
    return dict(latin_tokens=len(tokens), oromo_hits=len(oro),
                oromo_distinct=len(set(oro)), english_hits=len(eng),
                oromo_rate=len(oro) / max(1, len(tokens)),
                english_rate=len(eng) / max(1, len(tokens)),
                ethiopic_rate=eth / max(1, len(letters)),
                confidence=confidence)


def route(m):
    n = m["latin_tokens"]
    quality = m["confidence"] is None or m["confidence"] >= 65
    if (quality and n >= 20 and m["oromo_hits"] >= 5
            and m["oromo_distinct"] >= 3 and m["oromo_rate"] >= .06
            and m["english_rate"] <= .005 and m["ethiopic_rate"] <= .01):
        return "oromo_candidate"
    if (quality and n >= 20 and m["english_hits"] >= 5
            and m["english_rate"] >= .08 and m["oromo_hits"] <= 1):
        return "english"
    return "unknown"


def tsv_result(tsv):
    lines = {}
    weighted_conf = weight = 0
    for row in csv.DictReader(io.StringIO(tsv), delimiter="\t"):
        text = (row.get("text") or "").strip()
        try:
            conf = float(row.get("conf", -1))
        except (ValueError, TypeError):
            continue
        if not text or conf < 0:
            continue
        key = tuple(row.get(k) for k in ("page_num", "block_num", "par_num", "line_num"))
        lines.setdefault(key, []).append(text)
        weighted_conf += conf * len(text)
        weight += len(text)
    text = "\n".join(" ".join(words) for words in lines.values())
    return text, weighted_conf / weight if weight else 0, sum(map(len, lines.values()))


def attempt(text, method, region, rotation=0, confidence=None, **extra):
    m = evidence(text, confidence)
    return dict(text=normalize(text), method=method, region=region,
                rotation_ccw=rotation, evidence=m, decision=route(m), **extra)


def choose(attempts):
    candidates = [a for a in attempts if a["decision"] == "oromo_candidate"]
    # Favor the largest passing region, not the largest number of OCR words.
    return max(candidates, key=lambda a: (a["evidence"]["latin_tokens"],
               a["evidence"]["oromo_hits"]), default=None)


def direct_attempts(page):
    width = float(page.attrib["width"])
    output = []
    for name, (lo, hi) in REGIONS.items():
        lines = []
        for line in page.iter():
            if line.tag.rsplit("}", 1)[-1] != "line":
                continue
            words = []
            for word in line:
                if word.tag.rsplit("}", 1)[-1] != "word":
                    continue
                # Require the entire word inside the hypothesis region.
                if float(word.attrib["xMin"]) >= lo * width and float(word.attrib["xMax"]) <= hi * width:
                    words.append(word.text or "")
            if words:
                lines.append(" ".join(words))
        output.append(attempt("\n".join(lines), "embedded", name))
    return output


def ocr_attempts(pdf, page_number, dpi):
    from PIL import Image
    output = []
    with tempfile.TemporaryDirectory(prefix="bssco-") as td:
        prefix = str(Path(td) / "page")
        run(["pdftoppm", "-f", str(page_number), "-l", str(page_number),
             "-r", str(dpi), "-singlefile", "-png", str(pdf), prefix])
        with Image.open(prefix + ".png") as original:
            def recognize(angle, region, language="eng"):
                lo, hi = REGIONS[region]
                image = Path(td) / "region.png"
                with original.rotate(angle, expand=True) as rotated:
                    with rotated.crop((int(lo * rotated.width), 0,
                                       int(hi * rotated.width), rotated.height)) as crop:
                        crop.save(image)
                tsv, warnings = run(["tesseract", str(image), "stdout",
                                     "-l", language, "--psm", "4", "tsv"])
                text, conf, count = tsv_result(tsv)
                a = attempt(text, "ocr-" + language, region, angle, conf,
                            ocr_words=count, warnings=warnings[-1500:])
                if language == "amh":
                    a["decision"] = "review_ethiopic" if count >= 20 and conf >= 65 and a["evidence"]["ethiopic_rate"] >= .8 else "unknown"
                output.append(a)
                return a

            full = [recognize(angle, "full") for angle in (0, 90, 180, 270)]
            if choose(full):
                return output
            best = max(full, key=lambda a: (a["evidence"]["oromo_hits"] +
                       a["evidence"]["english_hits"], a["evidence"]["confidence"]))
            strong = (best["evidence"]["confidence"] >= 65 and
                      best["evidence"]["oromo_hits"] + best["evidence"]["english_hits"] >= 5)
            # A coherent full-page orientation avoids 12 unnecessary crop probes.
            angles = [best["rotation_ccw"]] if strong else [0, 90, 180, 270]
            for angle in angles:
                for region in ("left38", "middle", "right"):
                    recognize(angle, region)
            if not choose(output):
                # Diagnostic only: script emitted by an OCR model is not language proof.
                for angle in angles:
                    recognize(angle, "full", "amh")
    return output


def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def process_pdf(job):
    pdf, out, config = job
    source_hash = sha_file(pdf)
    key = hashlib.sha256(json.dumps(dict(source_sha256=source_hash, **config),
                                   sort_keys=True).encode()).hexdigest()
    work = out / "checkpoints" / key
    work.mkdir(parents=True, exist_ok=True)
    xml, _ = run(["pdftotext", "-bbox-layout", str(pdf), "-"])
    root = ET.fromstring(xml)
    pages = [p for p in root.iter() if p.tag.rsplit("}", 1)[-1] == "page"]
    if not pages:
        raise ValueError(f"No pages found in {pdf}")
    records = []
    for index, page in enumerate(pages, 1):
        saved = work / f"page-{index:05d}.json"
        if saved.exists():
            records.append(json.loads(saved.read_text(encoding="utf-8")))
            continue
        attempts = direct_attempts(page)
        selected = choose(attempts)
        if selected is None:
            attempts.extend(ocr_attempts(pdf, index, config["dpi"]))
            selected = choose(attempts)
        record = dict(page=index, decision="oromo_candidate" if selected else "review",
                      selected=selected, attempts=attempts)
        atomic_json(saved, record)
        records.append(record)
        print(f"{pdf.name}: page {index}/{len(pages)} -> {record['decision']}", flush=True)
    return dict(path=str(pdf), source_sha256=source_hash, pages=records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--expected-pdfs", type=int, default=30)
    p.add_argument("--tokenizer", type=Path)
    p.add_argument("--tokenizer-sha256", help="Required with --tokenizer; frozen reference hash")
    args = p.parse_args()
    if args.workers < 1 or not 150 <= args.dpi <= 400:
        p.error("workers must be positive and dpi must be 150..400")
    files = sorted(f.resolve() for f in args.pdf_dir.rglob("*") if f.suffix.lower() == ".pdf")
    if len(files) != args.expected_pdfs:
        p.error(f"Expected {args.expected_pdfs} PDFs, found {len(files)}. Point at the existing stratified sample; no automatic resampling.")
    for tool in ("pdftotext", "pdftoppm", "tesseract"):
        if not shutil.which(tool):
            p.error(f"Missing executable: {tool}")
    from PIL import Image
    import PIL
    languages, _ = run(["tesseract", "--list-langs"])
    if not {"eng", "amh"}.issubset(set(languages.split())):
        p.error("Tesseract eng and amh language models are required")
    sp = None
    if args.tokenizer:
        if not args.tokenizer_sha256 or sha_file(args.tokenizer) != args.tokenizer_sha256:
            p.error("Reference-tokenizer SHA-256 is absent or mismatched")
        import sentencepiece as sentencepiece
        sp = sentencepiece.SentencePieceProcessor(model_file=str(args.tokenizer))
        if sp.vocab_size() != 48000:
            p.error("Reference tokenizer must have vocabulary size 48000")
    elif args.tokenizer_sha256:
        p.error("--tokenizer-sha256 requires --tokenizer")
    versions = {}
    for tool in ("pdftotext", "pdftoppm", "tesseract"):
        stdout, stderr = run([tool, "--version" if tool == "tesseract" else "-v"])
        versions[tool] = (stdout + stderr).splitlines()[0]
    versions["pillow"] = PIL.__version__
    # Fingerprint OCR model bytes, not just the Tesseract engine version.
    header = languages.splitlines()[0]
    match = re.search(r'"([^"]+)"', header)
    if not match:
        p.error("Cannot locate Tesseract language models for reproducibility")
    model_dir = Path(match.group(1))
    models = {lang: sha_file(model_dir / (lang + ".traineddata")) for lang in ("eng", "amh")}
    config = dict(version=VERSION, script_sha256=sha_file(Path(__file__)),
                  dpi=args.dpi, tools=versions, ocr_model_sha256=models)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    results, failures = [], []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [(pdf, pool.submit(process_pdf, (pdf, args.out_dir, config))) for pdf in files]
        for pdf, future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                failures.append(dict(path=str(pdf), error=str(e)))
                print(f"ERROR {pdf.name}: {e}", flush=True)
    counts = Counter()
    hashes = set()
    words = tokens = 0
    candidate_path = args.out_dir / "oromo-candidates.jsonl"
    temporary = candidate_path.with_suffix(".jsonl.tmp")
    with temporary.open("w", encoding="utf-8") as dest:
        for result in results:
            for page in result["pages"]:
                counts[page["decision"]] += 1
                chosen = page["selected"]
                if chosen is None:
                    continue
                text_hash = hashlib.sha256(chosen["text"].encode()).hexdigest()
                if text_hash in hashes:
                    counts["within_sample_exact_duplicates"] += 1
                    continue
                hashes.add(text_hash)
                words += len(chosen["text"].split())
                if sp:
                    tokens += len(sp.encode(chosen["text"], out_type=int))
                entry = dict(source_id="bssco-oromia-legal-candidate-v0.1",
                             status="candidate_not_accepted", rights_status="unreviewed",
                             cross_source_dedup="not_run", path=result["path"],
                             source_sha256=result["source_sha256"], page=page["page"],
                             text_sha256=text_hash, **chosen)
                dest.write(json.dumps(entry, ensure_ascii=False) + "\n")
    temporary.replace(candidate_path)
    report = dict(status="incomplete" if failures else "candidate_audit_complete",
                  config=config, pdfs_requested=len(files), pdfs_completed=len(results),
                  inputs=[dict(path=str(f), sha256=sha_file(f)) for f in files],
                  counts=dict(counts), unique_candidate_pages=len(hashes),
                  candidate_whitespace_words=words,
                  candidate_reference_tokens_before_cross_source_dedup=tokens if sp else None,
                  tokenizer_sha256=args.tokenizer_sha256,
                  accepted_token_delta=0, failures=failures,
                  candidate_file_sha256=sha_file(candidate_path),
                  limitations=["Heuristic thresholds are uncalibrated; manually review candidates and rejected regions.",
                               "Fixed region hypotheses are incomplete; at most one candidate region per page.",
                               "Embedded-text pages that pass bypass OCR; other regions may be missed.",
                               "Counts are sample candidate yield, not net-new or accepted tokens.",
                               "Source URLs must be joined from the original inventory before promotion."])
    atomic_json(args.out_dir / "summary.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

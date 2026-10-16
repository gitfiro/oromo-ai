# Mozilla Common Voice Afaan Oromo — Candidate Status

## Status

**Paused at acquisition/inspection stage on 2026-10-16.**

This is the next independent source family selected after the Glot500 and
official CC100 audits.

## Why this source

Mozilla Common Voice is attractive because it is community-contributed speech
and transcript data rather than another Common Crawl/NLLB aggregation. It can
add a different register to OromoCorpus: short read/spoken Afaan Oromoo
sentences with explicit dataset provenance.

Target release:

```text
Mozilla Common Voice
Scripted Speech 27.0
Language: Afaan Oromo / Oromo
License: CC0-1.0
```

## Local acquisition state

The release archive was downloaded locally to the user's Windows Downloads
directory:

```text
1789492439552-cv-corpus-27.0-2026-09-11-om.tar.gz
size: ~529 MB
```

A corresponding extracted download directory was also present locally:

```text
1789492439552-cv-corpus-27.0-2026-09-11-om/
```

Project directories were created:

```text
data/candidates/commonvoice-om-v27/raw/
data/candidates/commonvoice-om-v27/extracted/
data/candidates/commonvoice-om-v27/reports/
```

The Common Voice data has **not yet been copied/extracted into the project,
profiled, transcript-deduplicated, token-counted, or accepted**.

No Common Voice records or tokens currently count toward OromoCorpus.

## Resume point

Next session:

1. copy the already-downloaded extracted Common Voice directory into the
   project candidate workspace;
2. inspect the actual TSV metadata schema;
3. extract unique Oromo transcript sentences only;
4. freeze raw transcript hashes and basic statistics;
5. exact-deduplicate against the current 830,308-record OromoCorpus;
6. run canonical 5-word-shingle near deduplication;
7. perform deterministic quality sampling;
8. measure 48K-reference-token yield;
9. make an evidence-backed accept/hold decision.

Do not redownload the archive unless the existing local copy is unavailable.

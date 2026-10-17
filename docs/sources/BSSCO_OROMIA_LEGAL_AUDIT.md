# BSSCO Oromia Legal Corpus Audit

**Status:** candidate / extraction validated / not yet accepted into OromoCorpus  
**Audit date:** 2026-10-17  
**Source family:** Oromia government legal publications (BSSCO)  
**Accepted-token impact:** **0** — this source remains outside the accepted corpus until rights review, full extraction, quality filtering, cross-source deduplication, and 48K reference-token measurement are complete.

## 1. Why this source matters

The BSSCO legal repository is a large collection of Oromia proclamations, regulations, and related government legal publications. It is especially valuable because it contains sustained formal Afaan Oromoo legal and administrative prose rather than only short web fragments.

The source may improve domain coverage in:

- law and regulation;
- public administration;
- government institutions;
- rights and responsibilities;
- economics and development;
- land, investment, public services, and institutional terminology.

## 2. Inventory

The validated BSSCO inventory currently contains:

| Metric | Value |
| --- | ---: |
| Live PDF files | 291 |
| HTTP-valid files | 291 |
| Total known bytes | 2,281,769,274 |
| Total size | 2,176.06 MiB |
| Minimum file size | 72.8 KiB |
| Median file size | 2.61 MiB |
| P75 | 7.27 MiB |
| P90 | 20.37 MiB |
| P95 | 31.01 MiB |
| Maximum file size | 112.46 MiB |

All 291 probed BSSCO file URLs returned live PDF candidates.

## 3. Stratified extraction audit

A deterministic 30-PDF stratified sample was selected across the full file-size distribution.

Direct text extraction with Poppler produced:

| Result | Files | Share |
| --- | ---: | ---: |
| Text-rich | 12 | 40% |
| Very-low text / likely OCR | 15 | 50% |
| No direct text | 3 | 10% |
| **Total** | **30** | **100%** |

The 30-file sample contained:

- **1,018 pages**
- **212,457 directly extracted whitespace words**
- **130,371 Latin-script words**
- **179,375 Ethiopic characters**

The distribution is highly uneven. For example, one 235-page born-digital proclamation yielded 116,344 words, while several large scan-heavy PDFs yielded essentially no embedded text.

This means file size is not a reliable proxy for recoverable text volume.

## 4. Trilingual legal structure

Manual inspection showed that many born-digital legal documents are parallel publications containing:

1. Afaan Oromoo in Latin/Qubee script;
2. Amharic in Ethiopic script;
3. English translation.

A prior whole-page language heuristic incorrectly labeled some pages as English because all three languages coexist on the page. The audit therefore rejects whole-page marker counts as a sufficient extraction strategy.

The correct extraction unit is the **page or page region**, not the whole PDF.

## 5. OCR feasibility

A scan-only legal page was rendered at 300 DPI and tested with Tesseract.

Full-page OCR recovered recognizable Afaan Oromoo but mixed the Oromo, Amharic, and English columns.

Cropping the left Oromo column before OCR materially improved quality and recovered coherent legal text such as:

- `Mata Duree Gabaabaa`
- `Tumaatota Fooyyeeffaman`
- `Yeroo Labsiin Kun Itti Ragga'u`
- substantive Oromo legal clauses and institutional terminology.

For one tested layout, the working OCR configuration was:

```text
300 DPI
→ Oromo-region crop
→ Tesseract
→ PSM 4
```

The 38% left-column crop worked well on multiple sampled pages of `Labsii 121/1999`, including beginning, middle, and final pages.

## 6. Page-level orientation and language routing

A larger scan (`Labsii 174/2004`) demonstrated that a fixed crop/orientation cannot safely be applied to an entire PDF.

Sampled pages showed multiple states:

| Page | Best interpretation |
| ---: | --- |
| 1 | Afaan Oromoo, upright |
| 50 | Afaan Oromoo, rotated 90° |
| 100 | English, rotated 90° |
| 150 | Amharic/Ethiopic, rotated 90° |
| 215 | Afaan Oromoo, rotated 90° |

A four-orientation OCR probe correctly recovered Oromo from rotated pages 50 and 215.

Quantitative OCR routing checks on pages 50, 100, 150, and 215 produced:

| Page | OCR model | Tokens | Mean confidence | Oromo hits | English hits | Interpretation |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 50 | eng | 186 | 86.74 | 26 | 0 | Oromo |
| 50 | amh | 7 | 30.27 | 0 | 0 | poor fit |
| 100 | eng | 228 | 90.13 | 0 | 96 | English |
| 100 | amh | 2 | 42.78 | 0 | 0 | poor fit |
| 150 | eng | 176 | 28.22 | 0 | 0 | poor fit |
| 150 | amh | 1 | 88.38 | 0 | 0 | Amharic/Ethiopic page; direct output inspection confirms coherent Amharic |
| 215 | eng | 211 | 79.38 | 28 | 1 | Oromo |
| 215 | amh | 16 | 41.14 | 0 | 0 | poor fit |

The Amharic model was also tested against a known English page and forced it into nonsensical Ethiopic-looking output. Therefore model choice alone is not a language detector.

The production router must combine:

- orientation;
- OCR confidence;
- Oromo lexical evidence;
- English lexical evidence;
- Ethiopic/Amharic evidence;
- conservative UNKNOWN handling.

## 7. Proposed extraction architecture

```text
PDF
 ↓
page-by-page inspection
 ↓
embedded text usable?
 ├── yes → direct extraction
 └── no  → render scan at 300 DPI
              ↓
        orientation search
              ↓
        candidate region detection
              ↓
        OCR model comparison
              ↓
   Oromo / English / Amharic / Unknown
              ↓
        keep Oromo only
              ↓
     conservative normalization
              ↓
       quality validation
              ↓
 exact + cross-source near deduplication
              ↓
 48K reference-token measurement
```

The goal is **high-precision recovery of trustworthy Afaan Oromoo**, not maximum page recovery.

Unknown or ambiguous pages should be held or dropped rather than allowed to contaminate OromoCorpus.

## 8. What has been established

The source has passed the following research gates:

- live-source inventory established;
- 291 BSSCO PDFs validated;
- file-size distribution measured;
- born-digital text extraction validated;
- trilingual publication structure identified;
- scan OCR feasibility validated;
- Oromo-region isolation validated on multiple pages;
- rotated Oromo pages recovered;
- English pages distinguished;
- Amharic/Ethiopic page routing demonstrated.

## 9. What is not yet complete

The source is **not yet accepted**.

Remaining work:

1. implement a reusable page-level BSSCO router;
2. run the full 30-file yield audit through the hybrid direct/OCR pipeline;
3. estimate recoverable Oromo word/token volume;
4. perform source/provenance and rights/licensing review;
5. acquire/process the full 291-PDF collection only if justified by yield and rights evidence;
6. perform conservative cleanup;
7. exact-deduplicate against all accepted OromoCorpus sources;
8. canonical near-deduplicate against the accepted corpus;
9. measure with the frozen Oromo Unigram 48K reference tokenizer;
10. freeze final artifacts and hashes before any promotion.

## 10. Corpus accounting

The authoritative accepted OromoCorpus baseline remains:

```text
Accepted records:          1,986,575
48K reference tokens:     94,230,190
Progress to 100M:              94.23%
Remaining to 100M:          5,769,810
```

**No BSSCO words or tokens are included in those totals.**

## 11. Current decision

**KEEP / CONTINUE AUDIT.**

BSSCO has enough scale, linguistic value, and demonstrated recoverability to justify a production-quality page router and 30-file yield audit. It should not be promoted on raw PDF size, OCR output, or pre-dedup word counts alone.

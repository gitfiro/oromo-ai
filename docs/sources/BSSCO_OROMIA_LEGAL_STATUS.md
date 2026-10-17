# BSSCO Oromia Legal Corpus — Extraction Status

**Source family:** Oromia government legal publications / BSSCO  
**Primary host:** `bssco.gov.et`  
**Research status:** extraction validated; corpus qualification in progress  
**OromoCorpus status:** **NOT PROMOTED / 0 accepted tokens counted**  
**Checkpoint date:** 2026-10-17

---

## 1. Purpose

This report records the current technical qualification state of the BSSCO legal-document candidate for OromoCorpus.

The source is potentially valuable because it contains long-form formal Afaan Oromoo in legal, administrative, economic, institutional, and public-policy domains. Many publications are parallel-language gazette documents containing Afaan Oromoo, Amharic, and English.

No BSSCO text is counted in the accepted OromoCorpus total at this stage.

Promotion still requires:

1. source-rights/licensing review;
2. reproducible page/region extraction;
3. conservative Oromo-only filtering;
4. quality review;
5. exact and near cross-source deduplication;
6. 48K reference-token measurement;
7. frozen artifact hashes and source manifest.

---

## 2. Repository inventory

The BSSCO inventory currently contains:

| Metric | Value |
| --- | ---: |
| Live PDF records | 291 |
| Successful HTTP metadata probes | 291 |
| Failed metadata probes | 0 |
| Total known size | 2,176.06 MiB |
| Minimum PDF size | 72.8 KiB |
| Median PDF size | 2.61 MiB |
| P75 | 7.27 MiB |
| P90 | 20.37 MiB |
| P95 | 31.01 MiB |
| Maximum PDF size | 112.46 MiB |

All 291 probed files returned live PDF metadata.

File size is not treated as a proxy for usable text. The audit found both very large scan-only PDFs and large text-rich PDFs.

---

## 3. Stratified 30-PDF audit

A deterministic 30-file sample was selected across the complete file-size distribution, from approximately 0.07 MiB to 112.46 MiB.

Direct text extraction with Poppler produced:

| Metric | Value |
| --- | ---: |
| PDFs sampled | 30 |
| Total pages | 1,018 |
| Directly extracted words | 212,457 |
| Latin-script words | 130,371 |
| Ethiopic characters | 179,375 |
| Text-rich PDFs | 12 / 30 |
| Very-low-text / OCR candidates | 15 / 30 |
| No-text PDFs | 3 / 30 |

Interpretation:

- about 40% of the stratified sample was directly text-rich;
- about 60% required OCR or other image-based recovery;
- the source is therefore a **hybrid born-digital + scanned archive**.

The sample is not used to extrapolate accepted token yield. The distribution is highly uneven: one text-rich 235-page document alone yielded 116,344 directly extracted words.

---

## 4. Parallel-language structure

Manual inspection confirmed that several BSSCO gazette documents contain parallel legal text in:

1. Afaan Oromoo;
2. Amharic;
3. English.

Whole-page language labels are therefore unsafe. A page can contain all three languages at once.

Examples inspected during the audit included:

- `Labsii lakk. 235-2013`
- `Dambii Lakk. 195 2010`
- `Labsii Lak 222 bara 2012`

The Afaan Oromoo portions contain substantive legal prose, including definitions, operative provisions, institutional powers, economic terminology, and administrative language.

The extraction unit for this source must therefore be the **page or page-region**, not the whole PDF.

---

## 5. Scan OCR feasibility

A scan-only page from `Labsii Lak 40 Bara 1993` was rendered at 300 DPI and OCR-tested with Tesseract.

Full-page OCR was readable but mixed Oromo, Amharic, and English because of the parallel-column layout.

Cropping the left 38% of the page before OCR materially improved the output and recovered coherent Afaan Oromoo text such as:

- `Mata Duree Gabaabaa`
- `Tumaatota Fooyyeeffaman`
- `Yeroo Labsiin Kun Itti Ragga'u`
- `Preezidaantii Mootummaa Naannoo Oromiyaa`

The remaining errors were typical OCR artifacts: line-break hyphenation, occasional character substitutions, punctuation noise, and isolated damaged lines.

This established that scan-only BSSCO material is technically recoverable.

---

## 6. Layout/orientation validation

The fixed left-column crop was tested on additional documents.

### Labsii 121/1999

Pages 1, 8, and 16 all produced strong Afaan Oromoo OCR after the left-column crop. This validated the layout strategy for that document.

### Labsii 174/2004

This 215-page scan demonstrated that a single PDF can change orientation and language/layout across pages.

Observed sample pages:

| Page | Best observed state |
| ---: | --- |
| 1 | Afaan Oromoo, upright |
| 50 | Afaan Oromoo, 90-degree rotation |
| 100 | English, 90-degree rotation |
| 150 | Amharic / Ethiopic text, 90-degree rotation |
| 215 | Afaan Oromoo, 90-degree rotation |

Therefore no single crop/orientation can safely be applied to an entire PDF.

---

## 7. Page-routing evidence

A small page-level OCR comparison used:

- English Tesseract OCR;
- Amharic Tesseract OCR;
- Oromo lexical hits;
- English lexical hits;
- mean OCR confidence.

Results:

| Page | English OCR tokens | English mean confidence | Oromo hits | English hits | Amharic OCR signal | Interpretation |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 50 | 186 | 86.74 | 26 | 0 | weak | Oromo |
| 100 | 228 | 90.13 | 0 | 96 | weak | English |
| 150 | 176 | 28.22 | 0 | 0 | coherent Amharic OCR observed separately | Amharic |
| 215 | 211 | 79.38 | 28 | 1 | weak | Oromo |

Page 150 was independently OCR-tested with the Amharic model and produced coherent Ethiopic-script prose, confirming that the poor English OCR on that page was not useful Oromo text.

This demonstrates why the pipeline must compare OCR evidence rather than infer language from the script produced by one OCR model.

---

## 8. Required extraction architecture

The current evidence supports this source-specific pipeline:

```text
PDF
  ↓
page-level inspection
  ↓
embedded text usable?
  ├── yes → extract page text / region
  └── no  → render scan at controlled resolution
               ↓
         orientation selection
               ↓
         candidate Oromo region
               ↓
         OCR-model comparison
               ↓
         language routing
          ├── Oromo   → candidate KEEP
          ├── English → DROP
          ├── Amharic → DROP
          └── unknown → REVIEW / conservative DROP
```

Accepted Oromo candidates must then pass the normal OromoCorpus pipeline:

```text
conservative normalization
        ↓
quality validation
        ↓
exact cross-source deduplication
        ↓
canonical near deduplication
        ↓
48K reference-token measurement
        ↓
freeze + SHA-256 + manifest
```

The project should optimize for **high-precision Oromo recovery**, not maximum page recovery.

---

## 9. Current limitations

The following remain unresolved:

- no full 291-PDF text/OCR processing has been run;
- no source-wide Oromo word/token yield is available;
- the 38% crop is not universal;
- page orientation varies;
- some PDFs contain different languages on different pages;
- OCR quality varies by scan condition;
- no final OCR-normalization policy has been frozen for this source;
- no exact or near cross-source deduplication has been run on the recovered Oromo text;
- no 48K-reference token total has been measured;
- licensing/rights status has not yet been approved for OromoCorpus use.

Government hosting alone is **not** treated as proof of unrestricted training or redistribution rights.

---

## 10. Decision

**Decision: KEEP AS ACTIVE CANDIDATE — extraction technically validated; not promoted.**

The source has passed the technical feasibility gates needed to justify further engineering:

- live-document inventory established;
- born-digital extraction validated;
- trilingual structure identified;
- scan OCR validated;
- Oromo-region isolation validated on multiple documents;
- rotated Oromo pages recovered;
- English pages distinguished;
- Amharic page behavior confirmed.

The next high-value step is to replace manual page experiments with a reusable **BSSCO page router** and run it over the full 30-file stratified sample to estimate trustworthy Oromo yield.

Only after source-wide quality, rights, deduplication, and reference-token gates pass should BSSCO contribute to the accepted OromoCorpus total.

---

## 11. Corpus accounting

Authoritative accepted OromoCorpus remains:

```text
Accepted 48K reference tokens: 94,230,190
Progress to 100M:             94.23%
Remaining to 100M:             5,769,810
BSSCO contribution today:              0
```

This report records a **qualification milestone**, not a corpus-size increase.

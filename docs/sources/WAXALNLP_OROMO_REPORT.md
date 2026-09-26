# WaxalNLP Oromo ASR v2 — Source Qualification Report

**Source ID:** `google-waxalnlp-orm-asr-v2`

**Provider:** Digital Umuganda / AfriVoice

**Distribution:** Google WaxalNLP

**Dataset config:** `orm_asr_v2`

**Language:** Afaan Oromoo (`orm`)

**Status:** Metrics frozen; approved for OromoCorpus

## Purpose

This qualification evaluates the Afaan Oromoo transcription text distributed
through the Google WaxalNLP ASR dataset.

Only transcription text is admitted to OromoCorpus. Audio files are not part
of the OromoCorpus text release evaluated here.

Waxal adds a speech-transcription domain that complements the existing
web, encyclopedia, and news-oriented source families.

## Source and Licensing

WaxalNLP identifies Digital Umuganda / AfriVoice as the provider for the
Afaan Oromoo ASR data.

Declared license:

`CC-BY-SA-4.0`

Training permission:

`yes`

Dataset-text redistribution permission:

`yes`, subject to applicable CC BY-SA 4.0 attribution and ShareAlike
requirements.

Downstream trained-model-weight licensing:

`separate_review_required`

This qualification does not assume that the source-text license automatically
determines the licensing status of downstream model weights.

## Dataset Configuration

Configuration:

`orm_asr_v2`

The Oromo data was already speaker-disjoint in the original Waxal release;
the v2 configuration points to those existing Oromo splits.

Transcribed rows measured:

- train: 38,185
- validation: 3,078
- test: 3,782
- unlabeled with transcription: 0
- total rows with text: 45,045

## Exact Deduplication

Transcriptions were normalized conservatively by collapsing whitespace.

Results:

- rows with text: 45,045
- within-source exact duplicates: 788
- exact-unique transcripts: 44,257

Exact-unique artifact SHA-256:

`dafa39e928ba8bf8531cf4f3dde3db4833865f6fcc1dc561188f11c157c8c255`

Cross-source exact comparison used the complete accepted OromoCorpus baseline:

- AfriBERTa Oromo v0.1.2: 410,193 records
- Wikimedia omwiki v0.1: 2,254 records
- VOA Afaan Oromoo via WURA v0.1: 9,510 records
- baseline total: 421,957 records

Cross-source exact duplicates:

`0`

All 44,257 exact-unique Waxal transcripts were exact-net-new against the
accepted baseline.

## Near Deduplication

Canonical OromoCorpus near-duplicate policy:

- word shingle size: 5
- exact Jaccard threshold: >= 0.85
- bottom-k candidate signature size: 32
- deterministic within-source policy: first record in source order wins

Within-source near duplicates:

`63`

Within-source similarity range:

`0.862069 - 1.000000`

Records after within-source near deduplication:

`44,194`

Cross-source comparison against:

- AfriBERTa Oromo v0.1.2
- Wikimedia omwiki v0.1
- VOA Afaan Oromoo via WURA v0.1

Cross-source near duplicates:

`0`

## Final Net-New Contribution

Final records:

`44,194`

Final characters:

`10,637,213`

Whitespace tokens:

`1,387,505`

Average characters per record:

`240.69`

Final artifact SHA-256:

`15c713b20186787d31ad7e9144b7ff96e16ac7a58776c2f1b009d9b724357e3b`

## Tokenizer Measurements

Tokenizer measurements are planning/reference measurements only. The final
OromoLM tokenizer strategy has not yet been frozen.

### Oromo Unigram 32K + byte fallback

- vocabulary: 32,000
- tokenizer tokens: 1,991,271
- characters/token: 5.3419
- tokenizer tokens/whitespace token: 1.4351

### Oromo Unigram 48K + byte fallback

- vocabulary: 48,000
- tokenizer tokens: 1,934,045
- characters/token: 5.5000
- tokenizer tokens/whitespace token: 1.3939

The 48K byte-fallback tokenizer remains the corpus-planning reference.

## Updated OromoCorpus Planning Total

| Accepted source | Net-new records | 48K reference tokens |
| --- | ---: | ---: |
| AfriBERTa Afaan Oromoo v0.1.2 | 410,193 | 9,587,934 |
| Wikimedia omwiki v0.1 | 2,254 | 1,070,896 |
| VOA Afaan Oromoo via WURA v0.1 | 9,510 | 1,899,811 |
| WaxalNLP Oromo ASR v0.1 | 44,194 | 1,934,045 |
| **Total** | **466,151** | **14,492,686** |

Progress toward the 50M OromoCorpus v0.2 minimum:

`28.99%`

Remaining:

`35,507,314`

Progress toward the preferred 100M target:

`14.49%`

## Release Status

Metrics frozen:

`true`

Approved for OromoCorpus release:

`true`

Any change to the source selection, normalization, deduplication threshold,
candidate-generation policy, or tokenizer reference measurements requires a
new manifest version.

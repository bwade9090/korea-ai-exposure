# ADR 0007 — What derived data the public repository may contain

- Status: accepted, 2026-10-30 (Checkpoint A: the owner approved the proposal as written,
  including decision 3, committing resident registration aggregates with citation). Proposed
  2026-10-29.
- Decider: Hyungbae Cho
- Evidence: `docs/discovery/01_source_verification.md`, licence notes; `docs/DATA_SOURCES.md`

## Context

The repository is public (ADR 0002 amendment), so every committed table is redistributed. The
sources' terms differ:

| Source | Terms found | Implication |
| --- | --- | --- |
| AEI (Anthropic) | Dataset card text: data CC-BY, code MIT (no CC-BY version); card metadata says MIT | Derived tables with attribution and the release BibTeX |
| KOSIS (국가데이터처 and other producers) | KOSIS use guide: free use, reuse and redistribution, with citation | Processed tables with citation |
| Resident registration (행정안전부) | KOSIS statistical description adds a note restricting processing and for-profit use | Owner judgement; see decision 3 |
| KSSC classification files | KOGL Type 3: attribution, no derivatives | Do not commit modified crosswalks |
| data.go.kr combined KSIC/KSCO linkage CSV | KOGL Type 4: adds non-commercial | Do not use; KSSC originals suffice |
| BLS, O*NET, World Bank, ABS, ILO WP140 | Public domain; CC BY 4.0 (ILO adds an adaptation notice) | Derived tables with attribution |
| Bank of Korea issue notes | All rights reserved; linking is free, other reuse needs prior consultation and approval | Cite; commit rank orders only |

## Decision

1. Raw downloads are never committed (unchanged).
2. `data/processed/` may hold derived tables from AEI, KOSIS, BLS, O*NET, World Bank, ABS and
   ILO data, each with source, period, access date and licence in a sidecar note.
3. Resident registration aggregates (regional 15–64 totals) are committed with citation, and
   the methodology note records the MOIS note.
4. KSSC crosswalks are rebuilt at build time from the pinned originals; only project measures
   computed with them (for example, exposure by KSCO-8 sub-major group) are committed.
5. From the Bank of Korea note, only the published regional rank orders are used, with full
   citation; no values digitized from its figures are committed unless the Bank permits it.

## Consequences

- A clean clone needs a free KOSIS key to rebuild the KOSIS-based tables; the committed
  processed tables let readers check results without one.
- The owner may wish to confirm items 3 and 5 with the producers.

## Amendment — 2026-10-30: committed inputs

The owner decided that the pinned inputs other than the AEI files (KOSIS, BLS, ILO and KSSC; 15
files, 14.7 MB) are committed unchanged under `data/raw/`, with attribution in `data/README.md`,
so that the repository rebuilds without a KOSIS key and survives revised or moved sources. The
AEI files stay out, because two of them exceed GitHub's 100 MB limit; they are fetched from their
pinned Hugging Face commit. Item 1 is amended accordingly. Under item 4, the KSSC table is now
redistributed unchanged, which KOGL Type 3 allows with attribution; no derivative of it is
committed beyond the project's measures.

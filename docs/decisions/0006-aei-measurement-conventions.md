# ADR 0006 — AEI measurement conventions

- Status: proposed, 2026-10-29. Owner decision at Checkpoint A, before Phase 2 replication.
- Decider: Hyungbae Cho
- Evidence: `docs/discovery/01_source_verification.md` §1.1

## Context

Phase 1 reproduced every value in PLAN §3 and found conventions that differ between releases:

- Files change after release. The February 2026 raw file was replaced in place on 2026-05-21 by
  a version with added rows (country- and region-level numeric task-trait summaries).
- The raw files apply only a 15-conversation cell floor. The 200-per-country and
  100-per-region floors are documented for releases 2025-09-15 and 2026-01-15; the current
  2026-03-24 documentation no longer states them, and release 2026-06-26 states floors without
  numbers.
- The country lists contain pseudo-geographies: `not_classified` (unlocated conversations, 16–18%
  of each sample), `NONE` (February 2026), Seychelles (described by Anthropic as VPN or abusive
  traffic), and Reunion (no population).
- Published AUI levels are not on one basis. August and November 2025 put every row with at
  least 200 conversations into the usage total, unlocated conversations and Seychelles included,
  which shrinks every AUI (by 0.843 in August, to about 0.82 of the renormalized value in
  November). The February 2026 statements fit bases that exclude unlocated usage, without
  pinning one. April–May 2026 renormalize usage over the published countries. Within a snapshot
  every basis is a uniform rescaling, so ranks agree; levels do not. Only Anthropic's 2024
  working-age population file reproduces the published ranks and values.
- Release 2026-06-26 has no counts. The June 2026 report says chat sampling began on 10 April,
  so the April aggregate may cover only part of the month; Korea ties Norway in April (AUI 3.92,
  rank 9–10 of 114) and ranks 14 of 121 in May (3.78).
- Methods change between releases: O*NET 20.1 tasks with SOC 2010 codes in the raw releases,
  O*NET 30.2 and a SOC 2018 classifier in 2026-06-26; new sampling, request taxonomy and artifact
  classifier; task-trait levels and units shift (global AI autonomy 3.38 in November 2025 and
  2.72 in April 2026).
- Regional facets are complete for all 17 regions only for some breakdowns (use case,
  collaboration, task traits and other categorical facets; artifacts in 2026-06-26). In February
  2026 the coursework cluster is suppressed in Ulsan and Jeju.

## Decision (proposed)

1. **Pinning.** Every AEI download is pinned to Hugging Face commit
   `4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6`, which includes the 2026-05-21 February file.
2. **Floors.** For the raw releases the pipeline applies 200 conversations per country and 100
   per region; for 2026-06-26, a published row counts as clearing the floor.
3. **Pseudo-geographies** (`not_classified`, `NONE`, Seychelles, and countries without
   population such as Reunion) are excluded from every ranking and from renormalized shares, and
   kept in published-basis shares. Territories that Anthropic lists as countries (for example
   Puerto Rico) are kept as published.
4. **AUI, two series.** (a) Published values, each labelled with its basis. (b) The headline
   series on one basis for all five snapshots: usage share renormalized over the ranked countries
   divided by their working-age population share. The published April–May 2026 values are
   already on this basis; August 2025, November 2025 and February 2026 are recomputed. Population
   comes from Anthropic's 2024 working-age file (AEI-WAP2024); World Bank 2025 data are a
   sensitivity. Ranks are reported from both series; level differences are documented, not
   tuned away.
5. **Share of global usage.** Headline: the published `usage_pct` (all sampled conversations).
   Sensitivity: the share of geolocated conversations.
6. **Snapshots.** National: August 2025, November 2025, February 2026, April 2026, May 2026.
   Regional: the last four. May 2026 is the headline month of release 2026-06-26; April is a
   stability check. Every cross-release comparison is flagged with the method changes.
7. **Within-release comparisons.** Task traits, task concentration and SOC mixes are compared as
   Korea-versus-global or Korea-versus-peer gaps within one release, with each release's units.
   The SOC major-group mix is reported for August 2025 and April–May 2026, where it is published;
   for November 2025 and February 2026 only if the owner asks for an in-house task-to-SOC map.
8. **Regions.** The 17 ISO 3166-2:KR codes (KR-11 … KR-50) for every snapshot through May 2026.
   The Gwangju–Jeonnam merger of 2026-07-01 matters only for later releases; the region table
   gets validity dates.
9. **Regional facets.** Phase 4.5 uses the facets published for all 17 regions; O*NET task and
   request breakdowns appear only for the capital-region aggregate or with coverage flags. For
   M4, the work share is taken over the classified use cases, and the unclassified share is
   reported.
10. **Parsing.** Raw files are read with `keep_default_na=False` (Namibia's code is `NA`), and
    joins use codes, never names.

## Consequences

- Replication targets in PLAN Phase 2.4 are checked against the matching basis: Korea 3.73
  (August 2025) and 3.12 (November 2025) under the published rule; February 2026 statements on
  rank and range. Values published to one decimal (Australia's AUI 4.1) are checked on rank
  exactly, and a level gap is documented with its likely cause (truncation).
- On the headline basis, Korea's AUI is about 4.42, 3.82, 3.69, 3.92 and 3.78 across the five
  snapshots; the published series' rise from 3.12 to 3.92 is mostly a method change.

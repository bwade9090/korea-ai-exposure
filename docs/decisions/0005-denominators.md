# ADR 0005 — Denominators for the within-Korea usage index

- Status: proposed, 2026-10-29. Owner decision at Checkpoint A; the headline choice among the
  confirmed denominators is made at Checkpoint B (PLAN Phase 4).
- Decider: Hyungbae Cho
- Evidence: `docs/discovery/01_source_verification.md` §1.3

## Context

M3 divides each region's share of Korean usage by its share of a denominator. Phase 1 found:

- Resident registration population (`DT_1B04005N`, 5-year age groups; `DT_1B04006`, single
  years) is monthly, at month end, and the 17 regions sum exactly to the national total in
  every snapshot month. It excludes foreign residents.
- No 시도-level workplace-based employment table exists. The 지역별고용조사 workplace table
  (`DT_1ES3C01S`) is at 시군구 level, has no Sejong, covers metropolitan-city districts only from
  2021 1/2, and is not benchmarked to the official 시도 totals.
- The establishment survey of the Ministry of Employment and Labor (`DT_118N_MOND66`) gives
  workers by workplace region, monthly, for all 17 regions, but only employees of industries
  B–S: no agriculture, forestry or fishing, and no self-employed or unpaid family workers.
- Residence-based employment for all 17 regions is in `DT_1ES3B01J` (half-yearly, benchmarked).

## Decision (proposed)

1. **Population:** residents aged 15–64 at the end of each snapshot month (November 2025,
   February 2026, April 2026, May 2026), from resident registration. Foreign residents are
   excluded; the methodology note says so.
2. **Workplace-based alternative:** workers from the establishment survey for the same months
   (17 regions; employees in industries B–S). It understates agricultural provinces, which is
   stated wherever it is used.
3. **Residence-based employment:** employed persons from `DT_1ES3B01J`, paired with snapshots as
   in ADR 0004.
4. **Commuting check on 16 regions:** the ratio of workplace-based to residence-based employment
   within the 지역별고용조사 시군구 tables (both on the same, unbenchmarked basis). Sejong is not
   covered, and the ratio is a check, not a denominator.

## Consequences

- Seoul's index under a workplace-based denominator is expected to fall: within the 시군구
  tables its workplace to residence employment ratio is about 1.18 (2026 1/2).
- All denominators keep 17 regions for snapshots through May 2026 (ADR 0006 on the
  Gwangju–Jeonnam merger).

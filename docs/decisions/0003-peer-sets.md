# ADR 0003 — Peer sets

- Status: proposed, 2026-10-29. Owner decision at Checkpoint A.
- Decider: Hyungbae Cho
- Evidence: `docs/discovery/01_source_verification.md` §1.1

## Context

PLAN §3.1 proposed three peer sets: P1, Asia-Pacific advanced economies (Japan, Singapore,
Taiwan, Australia, New Zealand); P2, AUI > 1 with at least 200 conversations; P3, all countries
with at least 200 conversations. Phase 1 found:

- Coverage. Claude.ai is not offered in mainland China or Hong Kong, and neither appears in any
  release. Every other Asia-Pacific economy below has a country row in the November 2025,
  February 2026, April 2026 and May 2026 snapshots and clears 200 conversations in both raw
  releases (smallest: New Zealand, 2,899 in November 2025 and 2,739 in February 2026).
- Count floors cannot be applied to release 2026-06-26, which publishes no counts. It publishes
  114 countries for April 2026 and 121 for May 2026.
- Facet comparisons depend on sample size. In August 2025, 45–59% of task-level usage is
  unclassified for Singapore and New Zealand, against 19% for Korea, because small samples
  clear fewer privacy thresholds.
- Taiwan has no World Bank population series. AEI release 2025-09-15 ships its own 2024
  working-age population file, which includes Taiwan.

## Options

- **P1a — advanced Asia-Pacific (as proposed):** Japan, Singapore, Taiwan, Australia, New Zealand.
- **P1b — BIS Asian Consultative Council economies with data:** Australia, India, Indonesia,
  Japan, Malaysia, New Zealand, the Philippines, Singapore, Thailand. A fixed institutional
  definition of "Asia-Pacific" rather than one chosen by the project; it adds emerging economies.
- **P2, P3 — as proposed,** with one change: for release 2026-06-26, "published by Anthropic in
  that month" replaces the 200-conversation floor.
- **P4 — size-matched:** the ten countries closest to Korea in share of global usage in each
  snapshot (within a snapshot, share is proportional to conversation count, so this also works
  for release 2026-06-26). For task concentration and other facet metrics whose coverage grows
  with sample size (PLAN §6).

## Decision (proposed)

Use P1a and P1b for the national profile, P2 and P3 for rankings, and P4 for facet comparisons.
Population for recomputed AUIs comes from Anthropic's 2024 working-age file (AEI-WAP2024), which
covers Taiwan and reproduces the published ranks (ADR 0006). Report N with every comparison.

## Consequences

- RQ1 compares Korea with both advanced and emerging Asia-Pacific economies, on a definition the
  project did not choose.
- Facet comparisons against small peers carry coverage notes, or use P4 instead.

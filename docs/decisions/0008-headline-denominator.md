# ADR 0008 — Headline denominator of the within-Korea usage index

- Status: proposed, 2026-10-30, for Checkpoint B.
- Decider: Hyungbae Cho
- Evidence: `outputs/tables/T2.csv` and `outputs/facts.json` (`rq2.*`), from
  `korea_ai_exposure.regional`; the denominators are in `data/processed/denominators.csv`.

## Context

M3 divides a region's share of Korean usage by its share of a denominator. ADR 0005 accepted
three, and left the headline choice to Checkpoint B. Phase 4 computed all three for the four
regional snapshots (November 2025, February 2026, April 2026, May 2026; N = 17):

- **Residents aged 15-64** at month end (resident registration). Monthly, exact: the 17 regions
  sum to the national total in every month. Excludes foreign residents. The same population
  concept as the AUI and as the Australia brief's within-country index.
- **Workers by workplace region** (establishment survey). Monthly, and the only 17-region
  workplace measure, so it addresses commuting; but it covers employees of industries B-S only,
  which understates agricultural provinces.
- **Employed persons by residence** (지역별고용조사). Half-yearly, benchmarked.

Findings:

- The ranking hardly depends on the denominator: Spearman's rho between the population-based
  index and the other two is 0.97-0.99 in every snapshot.
- Levels do depend on it for Seoul: in May 2026 its index is 3.38 on residents, 2.63 on workers
  by workplace, and 3.55 on residence-based employment. Within the 지역별고용조사 시군구 tables,
  Seoul's workplace-based employment is 1.18 times its residence-based employment.
- Seoul and Incheon are the only regions above parity in April and May 2026. Incheon's usage
  share moved from 4.8% (November 2025) to 10.6% (February 2026) and 6.9% (April 2026), the only
  move of more than a third between snapshots.

## Options

1. **Residents aged 15-64 (recommended).** Exact, monthly, complete, comparable with the AUI and
   the Australia brief. Report the workplace-based index beside it as the commuting check.
2. **Workers by workplace region.** Closest to where work happens, but biased against
   agricultural provinces and provisional for 2025 onward.
3. **Employed persons by residence.** Half-yearly, so it does not match the snapshot month.

## Proposed decision

Option 1 for the headline index (F5, the brief), with the workplace-based index reported for
Seoul and in T2, and the residence-based index in T2. Phase 5 uses employment by occupation
(ADR 0004), not this denominator, so the choice changes M3 levels, not the decomposition.

## Consequences

- Seoul's headline index (3.38 in May 2026) is stated together with its workplace-based value
  (2.63) wherever it is quoted.
- Rankings are reported as robust across the three denominators (rho 0.97-0.99, N = 17).

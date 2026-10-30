# Replication log

Published values that the pipeline reproduces before relying on the AEI data (PLAN §3 and 2.4).
`make replicate` regenerates the table.

## Phase 2 — 2026-10-30

`make replicate` (`korea_ai_exposure.replication`) at commit `f8d9d0c`, on the files pinned in
`data/manifest.json` (Hugging Face commit `4e5f69fa…`); the data-marked test
`test_every_replication_check_passes_or_is_a_declared_optional_target` runs the same checks.
Tolerances follow PLAN 2.4. Basis: `published` compares the release's own AUI values;
`anthropic_2025` and `renormalized` are the bases of ADR 0006; `published usage_pct` is the
release's share of global usage.

| Target | Published | Reproduced | Basis | Result | Note |
| --- | --- | --- | --- | --- | --- |
| Korean conversations, Nov 2025 | 30,618 | 30,618 |  | pass |  |
| Korean regional counts sum to the national count, Nov 2025 | exact | 30,618 of 30,618 (17 regions) |  | pass |  |
| Smallest regional count, Nov 2025 | 175 (Ulsan) | 175 (Ulsan) |  | pass |  |
| Korean conversations, Feb 2026 | 29,075 | 29,075 |  | pass |  |
| Korean regional counts sum to the national count, Feb 2026 | exact | 29,075 of 29,075 (17 regions) |  | pass |  |
| Smallest regional count, Feb 2026 | 174 (Jeju) | 174 (Jeju) |  | pass |  |
| Korean regions with published usage, Nov 2025 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, Nov 2025 | 3.06% | 3.0622% |  | pass |  |
| Seoul's share of Korean usage, Nov 2025 | 58.23% | 58.2305% |  | pass |  |
| Seoul + Gyeonggi + Incheon, Nov 2025 | 79.09% | 79.0940% |  | pass |  |
| Incheon's share of Korean usage, Nov 2025 | 4.82% | 4.8207% |  | pass |  |
| Korean regions with published usage, Feb 2026 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, Feb 2026 | 2.91% | 2.9075% |  | pass |  |
| Seoul's share of Korean usage, Feb 2026 | 56.09% | 56.0929% |  | pass |  |
| Seoul + Gyeonggi + Incheon, Feb 2026 | 81.91% | 81.9089% |  | pass |  |
| Incheon's share of Korean usage, Feb 2026 | 10.56% | 10.5589% |  | pass |  |
| Korean regions with published usage, Apr 2026 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, Apr 2026 | 3.19% | 3.1900% |  | pass |  |
| Seoul's share of Korean usage, Apr 2026 | 63.53% | 63.5300% |  | pass |  |
| Seoul + Gyeonggi + Incheon, Apr 2026 | 83.34% | 83.3400% |  | pass |  |
| Incheon's share of Korean usage, Apr 2026 | 6.94% | 6.9400% |  | pass |  |
| Korean regions with published usage, May 2026 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, May 2026 | 3.24% | 3.2400% |  | pass |  |
| Seoul's share of Korean usage, May 2026 | 63.65% | 63.6500% |  | pass |  |
| Seoul + Gyeonggi + Incheon, May 2026 | 82.78% | 82.7800% |  | pass |  |
| Incheon's share of Korean usage, May 2026 | 6.75% | 6.7500% |  | pass |  |
| Korea's published AUI and rank, Apr 2026 | 3.92, rank 9–10 of 114 | 3.92, rank 9–10 of 114 | published | pass |  |
| Renormalized basis reproduces Korea's published AUI, Apr 2026 | 3.92 | 3.921 | renormalized | pass |  |
| Korea's published AUI and rank, May 2026 | 3.78, rank 14 of 121 | 3.78, rank 14 of 121 | published | pass |  |
| Renormalized basis reproduces Korea's published AUI, May 2026 | 3.78 | 3.774 | renormalized | pass |  |
| Korea's AUI and rank, Aug 2025 (September 2025 report) | 3.73, rank 5 | 3.725, rank 5 of 115 | published | pass |  |
| Rule anthropic_2025 reproduces every published AUI, Aug 2025 | 115 values | largest absolute difference 0.0e+00 over 115 countries | anthropic_2025 | pass |  |
| Korea's AUI and rank, Nov 2025 (January 2026 appendix, Fig. 3) | 3.12, rank 7 of 116 | 3.123, rank 7 of 116 | anthropic_2025 | pass |  |
| India's share of global usage and rank, Nov 2025 (India brief) | 5.8%, rank 2 | 5.81%, rank 2 of 116 | published usage_pct | pass |  |
| Korea's AUI, Feb 2026 (Anthropic, 2026-05-26: 'more than 3.5 times') | above 3.5 | 3.692, rank 12 of 116 | renormalized | pass |  |
| Australia's share of global usage and rank, Feb 2026 (Australia brief) | 1.6%, rank 11 | 1.59%, rank 11 of 116 | published usage_pct | pass |  |
| Australia's AUI rank, Feb 2026 (Australia brief: 4.1, rank 7) | rank 7 | rank 7 of 116 | renormalized | pass | Published to one decimal; the basis is not pinned. Level 4.183 renormalized (truncates to 4.1, rounds to 4.2); 4.094 with usage over all geolocated conversations (rounds to 4.1). |
| Australia's state indices, Feb 2026 (optional; NSW 1.20, VIC 1.19, WA 0.68) | NSW 1.20, VIC 1.19, WA 0.68 | not run |  | not run | Optional target: needs ABS state population (ABS-ERP), not pinned yet. |
| Anthropic observed_exposure: occupations, zeros, maximum | 756; 411; 0.745 | 756; 411; 0.7451 |  | pass |  |

38 pass, 0 fail, 1 not run.

- Australia's AUI level: the brief gives 4.1, to one decimal, without its basis. The renormalized
  value, 4.183, gives 4.1 only if truncated; usage over all geolocated conversations gives 4.094,
  which rounds to 4.1. Neither basis is confirmed, so the check is on rank (PLAN 2.4). The rank
  is the same on both bases, which differ by a constant factor.
- Australia's state indices are an optional target: they need ABS population by state and age
  (ABS-ERP), which is not pinned yet.
- Phase 1 had reproduced these values with scratch scripts
  (`docs/discovery/01_source_verification.md` §1.1); committed code now checks them.

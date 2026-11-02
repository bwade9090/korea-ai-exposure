# ADR 0010 — Compare regions per worker in RQ3 and RQ4

- Status: accepted, 2026-11-02. An external review questioned the RQ3 statistic; the owner asked
  in session that the feedback be applied where it is warranted, and this ADR records how.
- Decider: Hyungbae Cho
- Evidence: `outputs/facts.json` (`rq3.fit.*`, `rq3.robustness.*`, `rq4.bok.*`),
  `outputs/tables/rq3_fit.csv`, `T3.csv` and `rq4_bok.csv`, from `korea_ai_exposure.decomposition`.
  The values stay in `outputs/` until Checkpoint C (ADR 0002).

## Context

PLAN §6 (M7) reports the share of the cross-regional variance in log w_r, a region's share of
Korean work usage, accounted for by log ŵ_r, its predicted share (R² and Spearman's rho, N = 17).
Both shares are proportional to the region's employment, which varies 36-fold across the 17
regions (지역별고용조사, first half of 2026). The common size term enters both sides, so the fit
mostly measures size, and so do three other comparisons built on shares:

- T3 compares rankings of predicted and of observed work-usage shares across variants; every
  variant carries the same size term, so the rho >= 0.9 rule of PLAN §7 is passed through size;
- the Bank of Korea's exposure rank orders, which do not scale with size, are compared with the
  ranking of observed work-usage shares, which does;
- F8 and F9 plot the shares.

RQ3 asks how much of the regional variation occupational composition accounts for. Composition is
what remains of ŵ_r once size is removed. The prior art fits per capita: Anthropic's January 2026
report relates US state usage per capita to workforce composition.

## Options

1. **Per worker (recommended).** Divide both shares by the region's share of the employment behind
   the prediction: the published cells with an intensity. Predicted usage per worker is then the
   employment-weighted mean usage per worker of the region's occupations over the national mean,
   that is composition alone; the residual R_r is unchanged, and y = p + log R_r, with y and p the
   logs of observed and predicted usage per worker. Report the composition share cov(y, p) /
   var(y), the part of the variance of y that composition accounts for at face value (the residual
   accounts for the rest), with the R² and slope of y on p (R² = slope × share) and Spearman's rho.
2. **Per resident aged 15–64** (the M3 denominator, ADR 0008). The predicted side then also carries
   the employment rate, which is not composition.
3. **Shares, with log employment share as a control.** A second regressor on N = 17, and a
   statistic that is harder to read.

## Decision

Option 1, for Korea and for the US states. The fit is reported for the 17 regions, for the 14
outside the capital region (the check used for location effects since Checkpoint B), and for the 50
states and DC. T3 compares per-worker rankings, with each earlier snapshot's observed usage on the
paired half-year's employment (ADR 0004, item 2). The Bank of Korea comparison uses observed work
usage per worker. F8 and F9 plot usage per worker. Predicted shares and residuals stay as defined
in PLAN §6.

## Consequences

- The composition share answers RQ3; R² and slope describe the association. A slope above 1 means
  that regions differ more than their composition predicts.
- The rho >= 0.9 rule now tests the composition ranking itself; T3 reports the variants that fail.
- A fit on shares is not comparable with these statistics. Anthropic's state fit is on the same
  basis (per capita) but not the same specification (one occupation share there, predicted usage
  from all occupations here).
- Facts `rq3.r2.*` and `rq3.rho.*` are replaced by `rq3.fit.*`, and `rq4.bok.*.observed_work` by
  `rq4.bok.*.observed_per_worker`; T3's usage rows are renamed "per worker".

# korea-ai-exposure

Where AI is used, and where AI-exposed work sits, across Korea's 17 metropolitan cities and
provinces. Measured from public data: the Anthropic Economic Index, Anthropic's occupation-level
exposure data, and Korean official statistics.

**Status:** work in progress; no results yet.

## Questions

1. How does Korea's Claude.ai usage compare with peer economies?
2. How is usage distributed across Korea's regions, relative to population and employment?
3. How much of the regional pattern does occupational composition account for, and how does usage
   compare with exposure?

## Reproducibility

`make all` will regenerate every figure and number from pinned public sources. Raw data are
downloaded by scripts and are not stored in this repository.

- Sources, versions, and licenses: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md)
- Plan: [`docs/PLAN.md`](docs/PLAN.md)

## Attribution and disclaimer

This project uses data from the Anthropic Economic Index (Anthropic; CC-BY). It is an independent
project, not affiliated with or endorsed by Anthropic. Further disclaimers will be finalized before
publication; see [ADR 0002](docs/decisions/0002-employer-and-publication-review.md).

# ADR 0002 — Employer and publication review

- Status: accepted, 2026-11-02: the owner confirmed in session that the review in items 1–5 is
  complete and approved publication (Checkpoint C; outcome below). Proposed 2026-10-29; amended
  2026-10-29 (repository visibility, below).
- Decider: Hyungbae Cho

## Context

The owner works at the Bank of Korea. Its Research Department published on AI and regional labor
markets on 15 September 2026. A public repository or brief on the same subject could be read as
institutional communication, and the employer may have rules on external publications and outside
activities.

## Decision

The repository stays private (superseded for the repository itself by the amendment below), and
nothing from it is shared externally, until the owner has:

1. checked the employer's rules on external publications and outside activities, and obtained any
   required clearance;
2. confirmed that the full git history contains no non-public data;
3. added disclaimers: the views are the author's own, and the project is independent, not
   affiliated with or endorsed by Anthropic or the Bank of Korea;
4. confirmed licenses and attribution for every source in `docs/DATA_SOURCES.md`;
5. decided whether the README names the employer.

Record the outcome here with a date, then change the status to accepted.

## Amendment — 2026-10-29: repository visibility

The GitHub repository was already public when Phase 0 started. The owner decided to keep it
public. Consequences:

- Every push publishes its commits. The hard stops in `CLAUDE.md` (no restricted or confidential
  data, no secrets) therefore apply to every commit, not only to releases.
- Items 1–5 still apply before the brief, its findings, or its figures are released, presented,
  or promoted (Checkpoint C).

## Outcome — 2026-11-02: Checkpoint C

The owner approved the draft of the brief and confirmed that items 1–5 are complete. The brief is
published in `report/` (`brief.docx`, built from `outputs/facts.json`, and `brief.pdf`, exported
from Word), with the disclaimers of item 3 on its cover and in the README; the README does not
name the employer. From this date the results in `outputs/` are tracked.

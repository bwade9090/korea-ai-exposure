# 8. Methodology and limitations

Draft for the brief (PLAN §9, section 8), written from the code. It states methods only. Values
in braces are fact IDs in `outputs/facts.json`; replace each with the fact's `display` value. The
final check compares every number in the brief with its source.

## 8.1 Data

**Claude.ai usage.** The Anthropic Economic Index (AEI) publishes aggregates from a
privacy-preserving sample of Claude.ai conversations, classified into O*NET tasks, request
topics, collaboration patterns, use cases and task traits, by country and, from November 2025,
by subnational region. The analysis uses five snapshots from four releases, all pinned to one
commit of the Hugging Face dataset:

| Snapshot | Release | Sample window | Regional data |
| --- | --- | --- | --- |
| August 2025 | 2025-09-15 | 4–11 August 2025 | No |
| November 2025 | 2026-01-15 | 13–20 November 2025 | 17 regions |
| February 2026 | 2026-03-24 | 5–12 February 2026 | 17 regions |
| April 2026 | 2026-06-26 | April 2026 (sampling from 10 April) | 17 regions |
| May 2026 | 2026-06-26 | May 2026 | 17 regions |

May 2026 is the headline month. Usage is located by the IP address of the conversation, and
regions are identified by ISO 3166-2:KR codes. A missing row means that the release did not
publish the cell (privacy thresholds and sample floors), never zero.

**Korean official statistics** (KOSIS, retrieved through its OpenAPI): residents aged 15–64 at
month end from resident registration (Ministry of the Interior and Safety; foreign residents
excluded); workers by workplace region from the establishment labour survey (Ministry of
Employment and Labor; employees of establishments in industries B–S); employed persons by region
of residence, and by region and KSCO-8 sub-major group, from the Local Area Labour Force Survey
(지역별고용조사, half-yearly); national employment by KSCO-8 minor group; and GRDP per capita for
2024 (preliminary, current prices).

**United States.** OEWS May 2025 national and state employment by detailed occupation
(wage-and-salary jobs only).

**Classifications and exposure.** BLS crosswalks from SOC 2018 to SOC 2010 and from SOC 2010 to
ISCO-08; the official KSCO-8 to ISCO-08 correspondence table of Statistics Korea (November 2025,
re-posted 27 January 2026); the 2018 SOC structure; the generative-AI exposure scores of
Gmyrek et al. (2025, ILO Working Paper 140) for ISCO-08 unit groups; and Anthropic's observed
exposure by SOC 2018 occupation (Massenkoff and McCrory 2026).

Every download is pinned with its URL, SHA-256 checksum, size and retrieval date
(`data/manifest.json`); `docs/DATA_SOURCES.md` gives versions, licences and attribution.

## 8.2 National measures (RQ1)

**Share and AUI.** A country's share of usage is Anthropic's published share of all sampled
conversations. The AI Usage Index (AUI) is that share divided by the country's share of
working-age (15–64) population, from Anthropic's 2024 population file. Published AUIs are on
different bases across releases: August and November 2025 count every row above the floor in
the usage total, unlocated conversations included, and no level was published for February 2026.
The headline series therefore puts all five snapshots on one basis, with both shares taken over
the ranked countries: at least 200 conversations in the weekly releases, or published in release
2026-06-26, excluding unlocated conversations and other pseudo-geographies, Seychelles (described
by Anthropic as VPN or abusive traffic) and countries without population data. The April and May 2026 values are
published on this basis and are used as published. Published values are reported beside the
headline series with their basis. Before these data were used, the pipeline reproduced the
published values it could check (`docs/replication.md`).

**Peers.** Korea is compared with the advanced Asia-Pacific economies (Japan, Singapore, Taiwan,
Australia, New Zealand), the members of the BIS Asian Consultative Council with data (Australia,
India, Indonesia, Japan, Malaysia, New Zealand, the Philippines, Singapore, Thailand), countries
with a headline AUI above 1, all ranked countries, and, for metrics whose coverage grows with
sample size, the ten countries closest to Korea in share of usage. Peer statistics are medians,
reported with N.

**Profile.** Use cases are shares of conversations classified as work, personal or coursework.
Collaboration patterns are shares of the five patterns (directive, feedback loop, task iteration,
learning, validation); automation is directive plus feedback loop and augmentation the other
three, which reproduces Anthropic's published buckets. Task traits are the published means and
shares, in each release's units. Task concentration is the share of all conversations in the 100
largest published O*NET tasks. Occupation (SOC major group), request-topic and artifact mixes
are shares of published, classified rows, compared with the global sample in percentage points.
These comparisons are made within one snapshot; every comparison across snapshots is flagged,
because releases differ in sampling, classifiers, taxonomies and trait scales.

## 8.3 Regional measures (RQ2)

**Shares and index.** A region's usage share is its published share of Korean conversations.
Where a release publishes counts (November 2025 and February 2026), Wilson 95% intervals are
given; they understate uncertainty, because conversations cluster by user. The within-Korea
usage index divides the usage share by the region's share of residents aged 15–64 at the end of
the snapshot month (ADR 0008); 1 means parity. The same index on workers by workplace region
addresses commuting, though it covers employees in industries B–S only; an index on employed
persons by residence uses the half-year paired with the snapshot (second half of 2025 for
November 2025 and February 2026, first half of 2026 for April and May).

**Work usage.** A region's share of Korean work-related usage is its usage share times its work
share of classified use cases, normalized over regions. In February 2026, where the coursework
share is not published for Ulsan and Jeju, every region uses its work share of all
conversations.

**Checks.** Commuting is gauged by the ratio of workplace-based to residence-based employment
summed over the districts of the Local Area Labour Force Survey (16 regions; Sejong is not
covered; the district figures are not benchmarked to regional totals). Stability is Spearman's
rank correlation of the index between snapshots, with regions whose usage share moves by more
than a third between consecutive snapshots flagged. The capital region (Seoul, Gyeonggi,
Incheon) is compared with the other 14 regions, and regions are also ranked outside the capital
region. Regional profiles use only the metrics published for all 17 regions. The association
with GRDP per capita is Spearman's rho.

## 8.4 Composition and exposure (RQ3–RQ4)

**From US occupations to Korean occupation groups.** US measures are mapped to the 56 KSCO-8
sub-major groups, the level at which regional employment by occupation is published: SOC 2018
to SOC 2010 to ISCO-08 (BLS) to KSCO-8 unit groups (official table) to sub-major groups. A SOC
code divides its US employment equally over its matches at each step, and an ISCO group's value
is the employment-weighted mean of the US values allocated to it. A KSCO unit group takes the
equal-weight mean of its ISCO matches; unit groups are averaged equally within minor groups, and
minor groups are weighted by Korean national employment (first half of 2026). The 12 OEWS codes
that combine several SOC occupations are treated as single units. Values missing at any step
are left out and the weights renormalized; the chain maps {rq3.coverage.usage.us_mapped_to_isco}
of US employment to ISCO groups, and occupation groups with an exposure value hold
{rq3.coverage.ilo.korea_with_value} of Korean employment.

**Occupation measures.** Usage per worker for a US occupation is its share of US Claude.ai usage
in May 2026 (detailed occupations, O*NET-SOC codes truncated to SOC 2018) divided by its share of
US employment. This assumes that workers generate conversations about their own occupation's
tasks. AEI classifies the content of conversations and does not observe users' occupations, so
the measure is large for occupations whose tasks are common conversation topics but that employ
few wage-and-salary workers. Exposure is measured primarily by the ILO WP140 scores (ADR 0009),
which are independent of Claude usage; Anthropic's observed exposure, which is built from Claude
usage, is reported beside them.

**Decomposition.** A region's exposure is the employment-weighted mean exposure of its workers
across occupation groups (first half of 2026). Predicted work usage is a region's share of
Korean employment weighted by usage per worker; the residual is observed over predicted work
usage. The share of the cross-regional variance in log observed work usage accounted for by log
predicted usage (R²) and Spearman's rho are reported with N = 17. The same decomposition for the
50 US states and the District of Columbia uses OEWS state employment by occupation, with no
crosswalk, against each state's share of US work usage in May 2026; suppressed state cells are
left out, and covered employment ranges from {rq3.us_coverage.min.2026-05} to
{rq3.us_coverage.max.2026-05} by state.

**Comparison with the Bank of Korea.** The Bank of Korea's issue note of 15 September 2026 ranks
the regions by generative, agentic and physical AI exposure. Only its published rank orders are
used. The project's exposure ranking draws on the same ILO source as the note's generative
ranking but without the note's complementarity adjustment, whose details are not published, so
the rank correlations compare measures; they do not replicate the note.

**Robustness.** Each headline regional ranking is recomputed with the other occupation measures,
with the minimum, maximum or first listed ISCO match in place of the mean (the first match is a
mechanical stand-in for the one-to-one rules of the official table, which need judgment), with
global usage shares, with the other denominators and with the other snapshots. Fixed in advance:
a ranking whose Spearman's rho with the headline falls below 0.9 under any variant is reported
as not robust (Table T3).

## 8.5 Limitations

- **Location.** Usage is located by IP address. Commuting, mobile and corporate network
  gateways and VPNs can shift measured usage toward Seoul; the effect cannot be measured with
  public data. The workplace-based index and the rankings outside the capital region are
  reported for this reason.
- **Small N.** Seventeen regions is a small sample. Every cross-regional statistic is reported
  with N and describes an association, not an effect.
- **Method changes.** Releases differ in sampling windows, classifiers, taxonomies and trait
  scales, so changes across snapshots mix real change with method change. Comparisons are made
  within a snapshot wherever possible.
- **Instability.** February 2026 shows the one large swing in regional shares (Incheon) and is
  not used for levels. Weekly snapshots may also reflect the season, such as school breaks.
- **Coverage of the inputs.** The resident population excludes foreign residents; the
  establishment survey excludes agriculture, the self-employed and unpaid family workers; OEWS
  counts wage-and-salary jobs only.
- **Occupation measures.** Usage per worker rests on the assumption stated in 8.4. Exposure
  scores rate the potential exposure of tasks, not realized adoption.
- **Not published means missing.** Suppressed cells are left out and coverage is reported; they
  are never treated as zero.
- **Independence.** The project is independent. It is not affiliated with, or endorsed by,
  Anthropic, the Bank of Korea or any other institution, and the views are the author's own.

## 8.6 Reproducibility

The analysis runs from public sources with committed code: `make fetch` downloads and verifies
the pinned files, `make build` writes the canonical tables, `make figures` and `make facts` write
the figures, tables and `outputs/facts.json`, and `make replicate` repeats the replication
checks. KOSIS downloads need a free OpenAPI key, which the fetcher adds at request time and never
stores. Data licences: AEI data CC BY according to the dataset card; ILO WP140 scores CC BY 4.0; BLS publications public
domain; KOSIS data reusable with citation; the official KSCO–ISCO table (KOGL Type 3) is used at
build time and not redistributed.

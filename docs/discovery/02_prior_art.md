# Phase 1.7 — Prior art

- Date: 2026-10-29. Sources were read in full where public, and the claims below were
  re-checked by an independent pass. Quotations are kept to a minimum.
- Bibliographic details are in `docs/DATA_SOURCES.md` (prior-art table).

## Bank of Korea issue note of 15 September 2026

**Citation.** 김보성·정민수·정유정·장수빈 (2026). 「AI와 지역 노동시장 - 지역간 격차 확대 위험과 새로운
기회」. BOK 이슈노트 제2026-25호, 한국은행 조사국 지역경제조사팀, 2026년 9월 15일 (43 pp.). No official
English version exists; the project's translation of the title is *AI and Regional Labor
Markets: Risks of Widening Regional Gaps and New Opportunities*. The note asks that citations name
its authors and number, and states that the views are the authors' own.

**Method.** Three occupation-level exposure measures, each min-max scaled to 0–1:

- generative AI: the task-level exposure of Gmyrek et al. (2025, ILO Working Paper 140), adjusted
  for complementarity following Pizzinelli et al. (2023);
- agentic AI: Gupta and Kumar (2026), an arXiv preprint;
- physical AI: Frey and Osborne (2017), with the note's own adjustments.

Regional exposure is the employment-weighted mean of occupational exposure over each region's
workers, using 지역별고용조사 employment for the 17 regions; this is the form of the project's M6.
The note states neither the KSCO revision, nor the crosswalk to its exposure sources, nor the
occupation level or reference period of the regional aggregation, so its regional values cannot
be rebuilt exactly. Internal evidence points to KSCO-8 (56 sub-major groups; 데이터 전문가 as a
minor group) and to second-half 2025 employment weights.

**Regional results (Figure 7, p. 9; descending).**

| Rank | Generative | Agentic | Physical |
| --- | --- | --- | --- |
| 1 | Seoul | Seoul | Gyeongbuk |
| 2 | Sejong | Sejong | Jeonnam |
| 3 | Gyeonggi | Gyeonggi | Chungbuk |
| 4 | Incheon | Daejeon | Ulsan |
| 5 | Busan | Busan | Chungnam |
| 6 | Daejeon | Daegu | Gyeongnam |
| 7 | Daegu | Incheon | Gangwon |
| 8 | Gwangju | Gwangju | Jeonbuk |
| 9 | Jeju | Jeju | Jeju |
| 10 | Chungbuk | Jeonbuk | Daegu |
| 11 | Ulsan | Gyeongnam | Gwangju |
| 12 | Gyeongnam | Chungbuk | Incheon |
| 13 | Jeonbuk | Ulsan | Busan |
| 14 | Chungnam | Gangwon | Daejeon |
| 15 | Gangwon | Chungnam | Gyeonggi |
| 16 | Gyeongbuk | Jeonnam | Seoul |
| 17 | Jeonnam | Gyeongbuk | Sejong |

The note publishes no table of regional values, and several adjacent ranks are near-ties in the
figure (generative: Chungbuk–Ulsan, Jeonbuk–Chungnam; agentic: Gyeonggi–Daejeon, Busan–Daegu,
Chungbuk–Ulsan; physical: Jeonnam–Chungbuk, Daegu–Gwangju, Daejeon–Gyeonggi). Rank comparisons
in Phase 5.5 must be ties-aware.

**Other results.** The capital region's higher generative and agentic exposure reflects its
occupation mix (more professional and clerical work, fewer machine operators). Most of the
recent growth in highly exposed jobs is in the capital region. For workers in their twenties,
highly exposed employment fell in both the capital and the other regions, by similar amounts.
The note also shows an observed measure of AI use by region, the share of firms using AI
(기업활동조사 2024; Seoul about 15%), and an AI-readiness index by region.

**Relation to this project.**

- The note does not use or cite the Anthropic Economic Index. It states that its regional
  exposure reflects potential exposure from employment structure and is not a direct measure of
  regional AI use. This supports the usage-first framing (ADR 0001).
- Youth employment, which the note covers, is out of scope (PLAN §4).
- The note analyses National Pension Service records for one result. The project may cite that
  published result but never obtains or uses such data.
- Copyright: "All Rights Reserved". The Bank's copyright policy allows linking; other use of
  content not designated as public data needs prior consultation and approval, with credit and
  disclosure of changes. The project uses the published rank orders with citation and commits no
  values digitized from figures (ADR 0007).

## Other Bank of Korea work

오삼일·이수민·이하민·장수정·Zexi Sun·Xin Cindy Xu (2025). 「AI와 한국경제」. BOK 이슈노트 제2025-2호,
2025년 2월 10일. The Korean version of the IMF Selected Issues Paper *Transforming the Future: The
Impact of Artificial Intelligence in Korea*; national results only, with AIOE-based exposure
(Felten et al.) and complementarity.

## Anthropic publications

| Item | Date | Relevance |
| --- | --- | --- |
| Appel, McCrory, Tamkin, Stern, McCain and Neylon, *Anthropic Economic Index report: Uneven geographic and enterprise AI adoption* | 2025-09-15 | Introduces the AUI; Korea fifth (3.73) |
| *Anthropic Economic Index report: Economic primitives* and its online appendix | 2026-01-15 | Appendix Fig. 3: Korea AUI 3.12, rank 7 of 116 (November 2025). Within the US, a higher share of computer and mathematical workers goes with higher usage per capita (elasticity 0.36), accounting for nearly two-thirds of cross-state variation; workforce composition also instruments a convergence estimate. Direct prior art for RQ3 and M8 |
| *Anthropic Economic Index report: Learning curves* | 2026-03-24 | February 2026 data; no Korea-specific statement |
| *Anthropic Economic Index report: Cadences* | 2026-06-26 | April–May 2026 data; no Korea or subnational results |
| Appel, *India Country Brief: The Anthropic Economic Index* | 2026-02-16 | Format model; state shares |
| McCrory, *How Australia Uses Claude: Findings from the Anthropic Economic Index* | 2026-03-31 | Format model; state indices relative to working-age population; income does not predict state usage (canonical URL `/research/how-australia-uses-claude`; the URL in its own BibTeX returns 404) |
| McCrory, *How Canada Uses Claude* | 2026-07-14 | Provincial shares and indices against working-age population; provincial usage related to industry composition rather than income |
| Massenkoff and McCrory, *Labor market impacts of AI: A new measure and early evidence* | 2026-03-05 | Defines observed exposure |
| Anthropic news on Korea: Seoul office announcement (2025-10-23), representative director (2026-05-26), Seoul office opening (2026-06-17) | — | National statements only: top five in total and per-capita usage (August 2025 data); "more than 3.5 times" the population-expected rate; among the top dozen countries |

All three country briefs analyse regions within the country, and the January 2026 report fits US
state usage to workforce composition. Anthropic also offers an Economic Index connector (July
2026) with subregion profiles, and on 2026-10-22 posted a Seoul-based "Regional Research
Economist" role (also Tokyo and Sydney) whose duties include country- and region-specific
analysis. No Anthropic Korea brief existed on 2026-10-29, but one is plausible.

## Other analyses

| Item | Scope | Overlap |
| --- | --- | --- |
| 송하윤·이병준, 「주요국의 AI 사용 실태와 한국의 현황」, KIEP 세계경제 포커스 9(4), 2026-01-29 | Korea's national AEI profile against Japan, Taiwan and Singapore (November 2025 data) | RQ1 and peer set P1a; must be cited. KOGL Type 4 |
| Arce, *Claude Adoption Atlas* (GitHub Pages), since 2026-09-13 | Interactive map of AEI data: all 17 Korean regions' usage shares in the four snapshots, plus regional use-case mix and automation share for April–May 2026 | Shows Korean regional patterns publicly; no per-capita index and no written analysis; national figures use its own denominators |
| Navarro, *More service jobs, less technical AI use: a subnational look*, August 2026 | 279 OECD TL2 regions in 35 countries (release 2026-06-26): the computer-and-mathematical usage share falls with the service employment share | Method relevant to RQ3; Korea and Japan are not in the sample |
| Murugan, Aguirre, Nagaraj and Bommasani, arXiv:2607.05404, June 2026 | Validates national exposure measures against country adoption statistics from Anthropic, Microsoft and OpenAI | Usage versus exposure at national level (RQ4) |
| paullabkorea (이호준), Anthropic Economic Index 분석 리포트, March 2026 | Korean-language national deep dive (November 2025 data) | National only |
| 이으뜸·문아람, 지역별 AI 준비도, KISDI Premium Report 25-12, December 2025 | AI readiness of 229 시군구 | Index based; seen through citations and press only |
| 과학기술정보통신부·한국지능정보사회진흥원, 2025 인터넷이용실태조사, 2026-03-31 | Generative-AI experience by 시도 (survey) | A possible check on IP-based regional usage (Checkpoint B); primary tables not yet verified |

No published analysis of the Korean regional AEI usage data was found (searches in Korean and
English, arXiv, GitHub and the Anthropic site, 2026-10-29). Absence cannot be proven; it
supports a "to our knowledge" statement only.

## Framing implications

- Not new: showing Korean regional usage shares and mixes (the Claude Adoption Atlas does), the
  national comparison with Asian peers (KIEP), within-country regional analysis of Claude usage
  (the three Anthropic briefs), fitting regional usage to workforce composition (Anthropic's US
  analysis), and regional AI-use measures for Korea (the Bank of Korea note shows firm AI use).
- What remains, to our knowledge as of 2026-10-29: a 시도-level analysis of observed Claude.ai
  conversation data with population and employment denominators; the decomposition of Korean
  regional usage into occupational composition and a residual, benchmarked on US states; and the
  comparison of observed regional usage with the Bank of Korea's exposure rankings.
- Cite KIEP (2026), the three Anthropic briefs, Anthropic's January 2026 report, Navarro (2026)
  and Murugan et al. (2026) where relevant. Cite the Bank of Korea note by its four authors and
  number. Any "first" claim is dated and qualified.

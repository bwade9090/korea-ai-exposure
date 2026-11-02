# ruff: noqa: RUF001
"""Text of the brief (report/brief.docx), written for policy readers; ``brief`` builds the file.

Every reported number is a placeholder resolved from outputs/facts.json: {id} is the fact's
display; {id:.1f} its value formatted; {id!abs:.1f} the absolute value; {id!ordw} an integer rank
as an ordinal word; {id!total} the N of an "x of N" display; {id!num} the display without
"(N = ..)". [^key] marks a footnote, whose text is in FOOTNOTES. Numbers typed directly are
structural only (dates, ages, counts of regions or groups, note numbers)."""

TITLE = "Regional Patterns of Generative AI Use in Korea"
SUBTITLE = "Evidence from Claude Conversation Data"
SERIES = "RESEARCH BRIEF"
DATE = "November 2026"
AUTHOR = "Hyungbae Cho"
DISCLAIMER = (
    "This brief is independent research based on public data. It is not affiliated with, or "
    "endorsed by, Anthropic, the Bank of Korea or any other institution. The views expressed "
    "are the author's own."
)

SUMMARY = [
    (
        "Korea is one of the most intensive users of Claude.",
        "In May 2026 Korea accounted for {rq1.share.2026-05} of Claude.ai conversations "
        "worldwide, the {rq1.share_rank.2026-05!ordw}-largest share among "
        "{rq1.share_rank.2026-05!total} countries. Relative to its working-age population, its "
        "use was {rq1.aui.2026-05} times the cross-country average.",
    ),
    (
        "Korean users rely on Claude more for work, and work with it more collaboratively.",
        "Work accounts for {rq1.use_case_work.korea.2026-05} of conversations with a classified "
        "purpose, against {rq1.use_case_work.global.2026-05} worldwide. Conversations in which "
        "users iterate with Claude rather than delegate to it make up "
        "{rq1.augmentation.korea.2026-05} of those with a classified pattern, the "
        "{rq1.augmentation.korea_rank.2026-05!ordw}-highest share among "
        "{rq1.augmentation.korea_rank.2026-05!total} countries.",
    ),
    (
        "Within Korea, use is heavily concentrated in the capital region.",
        "Seoul, Gyeonggi and Incheon account for {rq2.capital.usage.2026-05} of Korean "
        "conversations but {rq2.capital.population.2026-05} of residents aged 15–64; Seoul "
        "alone accounts for {rq2.share.seoul.2026-05}. Part of this concentration probably "
        "reflects how conversations are located: a national household survey finds much smaller "
        "regional differences in the use of generative AI.",
    ),
    (
        "Occupational composition explains only a small part of the regional differences.",
        "Regions with more occupations that use AI intensively do use Claude more for work, but "
        "composition accounts for only {rq3.fit.composition_share.korea.2026-05!num} of the "
        "regional variation in work use per worker, against "
        "{rq3.fit.composition_share.us.2026-05!num} across US states. Actual differences in use "
        "are several times larger than the occupational mix predicts.",
    ),
    (
        "Use follows exposure to AI in rank, but is far more unequal.",
        "Regions whose workforce is more exposed to generative AI tend to use Claude more (rank "
        "correlation {rq4.rho.ilo.index_population!num}), yet exposure varies little across "
        "regions while use varies widely. Assessments based on exposure alone may therefore "
        "understate how unevenly the use of AI is spreading across the country.",
    ),
]

# Body: ("h1", text) | ("p", lead, body). Exhibits are placed by PLACEMENT.
BODY = [
    ("h1", "I. Background"),
    (
        "p",
        "Most evidence on AI and regional labor markets measures potential exposure rather "
        "than actual use.",
        "Exposure indicators rate how much of each occupation's work generative AI could "
        "perform, and average these ratings over each region's workers. A recent Bank of Korea "
        "issue note ranks Korea's 17 regions in this way (Kim et al., 2026). Such measures show "
        "where AI could matter; as the note itself points out, they do not show where AI is "
        "actually used.",
    ),
    (
        "p",
        "Data on actual use are now available for regions within countries.",
        "Anthropic, the developer of the Claude AI models, publishes the Anthropic Economic "
        "Index: aggregate statistics from privacy-preserving samples of conversations on "
        "Claude.ai, classified by task, purpose and way of working. From the November 2025 sample "
        "onward the data cover regions within many countries, including all 17 Korean regions, "
        "and Anthropic has used regional data to describe use within the United States, India, "
        "Australia and Canada (Anthropic, 2026a; Appel, 2026; McCrory, 2026a; 2026b). The data "
        "cover one AI service, do not record users' occupations, and locate each conversation by "
        "the user's IP address.",
    ),
    (
        "p",
        "This brief compares observed use with occupational exposure across Korea's regions.",
        "It first places Korea among other countries, then describes how use is distributed "
        "across regions, asks how much of this distribution occupational composition explains, "
        "and compares use with exposure. The analysis centers on May 2026, the latest month "
        "available; snapshots from August 2025 to April 2026 serve as checks. With only 17 "
        "regions, the results describe associations, not causes.",
    ),
    ("h1", "II. Korea's Use of Claude in International Comparison"),
    (
        "p",
        "Korea is among the most intensive users of Claude worldwide.",
        "In May 2026 Korea accounted for {rq1.share.2026-05} of all Claude.ai conversations, the "
        "{rq1.share_rank.2026-05!ordw}-largest share among {rq1.share_rank.2026-05!total} "
        "countries [Figure 1]. Relative to the size of its working-age population, Korea's use "
        "was {rq1.aui.2026-05} times the cross-country average, {rq1.aui_rank.2026-05!ordw} in "
        "the ranking.[^aui] Korea has ranked between {rq1.aui_rank.2025-08!ordw} and "
        "{rq1.aui_rank.2026-05!ordw} in every snapshot since August 2025, although part of the "
        "movement between snapshots reflects changes in Anthropic's sampling methods.[^song]",
    ),
    (
        "p",
        "Korean users rely on Claude relatively more for work.",
        "Work accounts for {rq1.use_case_work.korea.2026-05} of Korean conversations with a "
        "classified purpose, against {rq1.use_case_work.global.2026-05} worldwide, and coursework "
        "for less ({rq1.use_case_coursework.korea.2026-05} against "
        "{rq1.use_case_coursework.global.2026-05}) [Figure 2]. The work share is close to the "
        "median of the advanced Asia-Pacific economies (Japan, Singapore, Taiwan, Australia and "
        "New Zealand; {rq1.use_case_work.P1a_median.2026-05}) and has exceeded the global share in "
        "every snapshot that reports it, by "
        "{rq1.use_case_work.gap_global.2026-05!abs:.1f} to "
        "{rq1.use_case_work.gap_global.2025-11!abs:.1f} percentage points.",
    ),
    (
        "p",
        "Korean users also work with Claude more collaboratively.",
        "Anthropic classifies each conversation by how the user works with the model: handing "
        "over a task to be completed (automation) or iterating, learning and checking results "
        "together with it (augmentation). In Korea augmentation accounts for "
        "{rq1.augmentation.korea.2026-05} of conversations with a classified pattern, against "
        "{rq1.augmentation.global.2026-05} worldwide, the "
        "{rq1.augmentation.korea_rank.2026-05!ordw}-highest share among "
        "{rq1.augmentation.korea_rank.2026-05!total} countries. Korean requests are also more "
        "advanced: Anthropic rates the level of education they reflect at "
        "{rq1.human_education_years_mean.korea.2026-05:.1f} years on average, against "
        "{rq1.human_education_years_mean.global.2026-05:.1f} years worldwide.",
    ),
    (
        "p",
        "The tasks lean toward content, analysis and business work.",
        "Compared with the global sample, Korean conversations more often involve the tasks of "
        "arts, design and media occupations "
        "({rq1.soc_gap.arts_design_entertainment_sports_and_media.2026-05!abs:.1f} percentage "
        "points more) and of business and financial occupations "
        "({rq1.soc_gap.business_and_financial_operations.2026-05!abs:.1f} points more), and less "
        "often those of sales ({rq1.soc_gap.sales_and_related.2026-05!abs:.1f} points less) and "
        "computer and mathematical occupations "
        "({rq1.soc_gap.computer_and_mathematical.2026-05!abs:.1f} points less). Requests for "
        "content creation and copywriting "
        "(+{rq1.request_gap.content_creation_copywriting.2026-05!abs:.1f} points) and for "
        "research (+{rq1.request_gap.research_intelligence.2026-05!abs:.1f}) are "
        "over-represented, while requests about hobbies "
        "(−{rq1.request_gap.hobbies_lifestyle.2026-05!abs:.1f}) and education "
        "(−{rq1.request_gap.education_learning.2026-05!abs:.1f}) are under-represented. Korean "
        "users also more often ask for analyses, summaries, documents and presentations, and "
        "less often for advice.",
    ),
    ("h1", "III. Regional Distribution of Use"),
    (
        "p",
        "Within Korea, use of Claude is concentrated in the capital region, and above all in "
        "Seoul.",
        "In May 2026 Seoul, Gyeonggi and Incheon together accounted for "
        "{rq2.capital.usage.2026-05} of Korean conversations but only "
        "{rq2.capital.population.2026-05} of residents aged 15–64 [Figure 3]. Seoul alone "
        "accounted for {rq2.share.seoul.2026-05}, giving it a usage index of "
        "{rq2.index_population.seoul.2026-05}: its share of use was more than three times its "
        "share of the population.[^index] Only Seoul and Incheon "
        "({rq2.index_population.incheon.2026-05}) used Claude more than their population share, "
        "and the index was lowest in Jeonnam ({rq2.index_population.jeonnam.2026-05}) "
        "[Figure 4].",
    ),
    (
        "p",
        "The pattern is stable over time and does not depend on the population measure.",
        "The capital region's share of conversations stayed between "
        "{rq2.capital.usage.2025-11} and {rq2.capital.usage.2026-04} across the four regional "
        "snapshots, and the ranking of regions barely changed (rank correlations of "
        "{rq2.rho.nov_2025.feb_2026:.2f} to {rq2.rho.apr_2026.may_2026:.2f} between snapshots). "
        "Rankings based on employment by place of work or by place of residence instead of "
        "population are almost the same (rank correlation of "
        "{rq3.robustness.usage_index_residents_15_64.denominator_workers:.2f} with either). "
        "Measured against employment by place of work, which allows for commuting into Seoul, "
        "Seoul's index falls to {rq2.index_workers.seoul.2026-05} but remains by far the "
        "highest. The one large swing is in Incheon's share, which rose from "
        "{rq2.share.incheon.2025-11} to {rq2.share.incheon.2026-02} between November 2025 and "
        "February 2026 and fell back to {rq2.share.incheon.2026-04} in April 2026.",
    ),
    (
        "p",
        "A stable pattern is not necessarily an accurate one, because of how conversations are "
        "located.",
        "The data assign each conversation to a region by the user's IP address. Commuting, "
        "mobile and corporate networks and virtual private networks can all shift recorded use "
        "toward Seoul, and a location bias that is itself stable would also produce a stable "
        "pattern. A national household survey offers an external check [Table 1]. In the 2025 "
        "Internet Usage Survey, the share of people who had used generative AI was highest in "
        "Sejong ({rq2.survey.experience.sejong.2025}), Daejeon "
        "({rq2.survey.experience.daejeon.2025}) and Seoul ({rq2.survey.experience.seoul.2025}), "
        "only about {rq2.survey_relative.experience.seoul.2025:.1f} times the national rate of "
        "{rq2.survey.experience.national.2025}. Paid subscriptions, a closer indicator of "
        "intensive use, were {rq2.survey_relative.paid.seoul.2025} times the national rate in "
        "Seoul, with Gyeonggi second. In the Claude data, by contrast, Seoul's index is "
        "{rq2.index_population.seoul.2026-05}, while Sejong "
        "({rq2.index_population.sejong.2026-05}), Daejeon "
        "({rq2.index_population.daejeon.2026-05}) and Gyeonggi "
        "({rq2.index_population.gyeonggi.2026-05}) are well below parity.",
    ),
    (
        "p",
        "The two sources measure different things, but the comparison calls for caution in "
        "reading regional levels.",
        "The survey counts any use of any generative-AI service, mostly ChatGPT, whereas the "
        "Claude data measure the volume of conversations with one service, whose users may be "
        "concentrated in particular occupations and industries. Even so, the low recorded use in "
        "Gyeonggi, home to some of Korea's largest technology clusters, and the swings in "
        "Incheon are consistent with part of the capital region's use being recorded in Seoul. "
        "Regional levels in this brief should therefore be read as levels of IP-located use. "
        "Rankings outside the capital region are less exposed to this problem: there, Daejeon, "
        "Sejong and Busan lead, while Gyeongbuk, Gyeongnam and Jeonnam trail.",
    ),
    (
        "p",
        "Use is not closely related to regional income.",
        "The rank correlation between the usage index and GRDP per capita is "
        "{rq2.grdp_rho.2026-05:.2f} (N = 17). Ulsan and Chungnam, which have among the highest "
        "output per person, have usage indices of only {rq2.index_population.ulsan.2026-05} and "
        "{rq2.index_population.chungnam.2026-05}. Anthropic's analysis of Australian states "
        "similarly finds that income does not predict use (McCrory, 2026a).",
    ),
    ("h1", "IV. Occupational Composition and Regional Differences"),
    (
        "p",
        "Regions differ in their mix of occupations, and occupations differ widely in how much "
        "they use AI.",
        "To gauge how much this matters, this brief predicts each region's work-related use of "
        "Claude from its occupational mix alone. It applies the US rate of Claude use per worker "
        "in each occupation to the region's employment in that occupation, and compares actual "
        "with predicted use per worker.[^pred] This assumes that people use Claude for the tasks "
        "of their own occupation, which the data cannot confirm.",
    ),
    (
        "p",
        "Occupational composition explains only a small part of the regional differences.",
        "Regions with more AI-intensive occupations do use Claude more for work, but actual "
        "differences are much larger than predicted ones [Figure 5]. Composition accounts for "
        "{rq3.fit.composition_share.korea.2026-05!num} of the regional variation in work-related "
        "use per worker.[^share] The share is similar outside the capital region "
        "({rq3.fit.composition_share.korea_outside_capital.2026-05!num}), so the result does not "
        "rest on Seoul alone. Across US states, measured in the same way, composition accounts "
        "for {rq3.fit.composition_share.us.2026-05!num}.",
    ),
    (
        "p",
        "Seoul uses far more, and most other regions far less, than their occupational mix "
        "predicts.",
        "Seoul's occupational mix predicts work use per worker "
        "{rq3.predicted_per_worker.seoul.2026-05} times the national average; its actual use is "
        "{rq3.observed_per_worker.seoul.2026-05} times the average, or "
        "{rq3.residual.seoul.2026-05} times the prediction. Incheon "
        "({rq3.residual.incheon.2026-05}) and Sejong ({rq3.residual.sejong.2026-05}) are also "
        "above their predictions. Elsewhere actual use falls well short: to less than half of the "
        "prediction in Busan ({rq3.residual.busan.2026-05}) and Gyeonggi "
        "({rq3.residual.gyeonggi.2026-05}), and to under a quarter in Gyeongbuk "
        "({rq3.residual.gyeongbuk.2026-05}), Gyeongnam ({rq3.residual.gyeongnam.2026-05}) and "
        "Jeonnam ({rq3.residual.jeonnam.2026-05}). These "
        "gaps may reflect differences in adoption beyond occupation, for example in industry, "
        "firm size or age structure, as well as the location effects discussed above. Public "
        "data cannot separate the two.",
    ),
    (
        "p",
        "The predicted pattern is sensitive to how occupational use is measured.",
        "If AI exposure scores replace usage rates in the prediction, the predicted ranking of "
        "regions changes considerably (rank correlations of "
        "{rq3.robustness.predicted_work_usage_per_worker_v.intensity_ilo:.2f} and "
        "{rq3.robustness.predicted_work_usage_per_worker_v.intensity_observed:.2f} with the main "
        "prediction). Predictions for individual regions should therefore be treated as "
        "indicative, and the composition share as an approximate magnitude.",
    ),
    ("h1", "V. Use and Exposure"),
    (
        "p",
        "Regions whose workforce is more exposed to generative AI tend to use Claude more.",
        "Exposure is measured with the International Labour Organization's occupational scores "
        "for generative AI (Gmyrek et al., 2025), averaged over each region's workers. The rank "
        "correlation between exposure and the usage index is "
        "{rq4.rho.ilo.index_population!num} (N = 17) [Figure 6]. This exposure ranking closely "
        "matches the Bank of Korea's generative-AI ranking, which builds on the same scores "
        "(rank correlation {rq4.bok.generative.ilo!num}), and the Bank's ranking is similarly "
        "related to use ({rq4.bok.generative.index_population!num}).",
    ),
    (
        "p",
        "Use, however, is far more unequal than exposure.",
        "Average exposure scores, on a scale from 0 to 1, lie in a narrow band from "
        "{rq4.exposure_ilo.jeonnam.2026-h1} in Jeonnam to {rq4.exposure_ilo.seoul.2026-h1} in "
        "Seoul, while the usage index ranges from {rq2.index_population.jeonnam.2026-05} to "
        "{rq2.index_population.seoul.2026-05}. The largest departures from the exposure ranking "
        "are Gyeongnam ({rq4.rank.exposure.gyeongnam!ordw} in exposure but "
        "{rq4.rank.usage_index.gyeongnam!ordw} in use) and Gyeonggi "
        "({rq4.rank.exposure.gyeonggi!ordw} and {rq4.rank.usage_index.gyeonggi!ordw}), which "
        "use less than their exposure suggests, and Gangwon ({rq4.rank.exposure.gangwon!ordw} "
        "and {rq4.rank.usage_index.gangwon!ordw}), which uses more. Exposure thus indicates where "
        "AI could matter, but it is a weak guide to how much AI is used.",
    ),
    ("h1", "VI. Implications"),
    (
        "p",
        "Assessments of AI's regional impact should look at actual use as well as exposure.",
        "Exposure measures show where generative AI could change work. Observed use shows that "
        "adoption so far is far more concentrated than exposure implies, and that occupational "
        "structure explains only a small part of the difference. If early use brings "
        "productivity gains, regional differences in use, and not only in exposure, may shape "
        "how AI affects regional disparities.",
    ),
    (
        "p",
        "Broadening AI use outside the capital region may deserve policy attention.",
        "Most regions outside the capital region use Claude well below their population share, "
        "even after allowing for their occupational mix. Policies that build AI skills among "
        "workers and support adoption by small firms and local public bodies could help ensure "
        "that the "
        "benefits of AI are not confined to a few areas. The evidence here does not show which "
        "measures would work; it shows where the gaps are.",
    ),
    (
        "p",
        "Better regional data on AI use are needed.",
        "Data from AI platforms located by IP address may overstate concentration in the capital "
        "region, and official surveys publish few regional details. Regular regional statistics "
        "on AI use by firms and workers, and checks of platform data against them, would give a "
        "firmer basis for policy.",
    ),
]

FOOTNOTES = {
    "aui": "The AI Usage Index divides a country's share of conversations by its share of the "
    "working-age (15–64) population, both taken over the countries with enough conversations to "
    "be ranked. A value of 1 means use in line with population.",
    "song": "For an earlier comparison of Korea with Japan, Taiwan and Singapore, see Song and Lee "
    "(2026).",
    "index": "The regional usage index divides a region's share of Korean conversations by its "
    "share of Korean residents aged 15–64. A value of 1 means use in line with population.",
    "pred": "Use per worker in each US occupation is the occupation's share of US Claude.ai "
    "conversations in May 2026 divided by its share of US employment (Occupational Employment "
    "and Wage Statistics, May 2025). The values are mapped to Korea's 56 occupation groups "
    "through the international classification of occupations (ISCO-08) and weighted by each "
    "region's employment in the first half of 2026 (Local Area Labour Force Survey).",
    "share": "The composition share is the covariance between the logarithms of actual and "
    "predicted use per worker, divided by the variance of the logarithm of actual use; the "
    "remainder is the part that composition does not account for. A regression of the logarithm "
    "of actual on that of predicted use gives an R² of {rq3.fit.r2.korea.2026-05!num} and a slope "
    "of {rq3.fit.slope.korea.2026-05!num} (N = 17): in proportional terms, regions differ in "
    "actual use more than three times as much as composition predicts.",
}

FIGURES = {
    "F1": {
        "headline": "Korea has consistently ranked among the leading users of Claude",
        "title": "[Figure 1] Korea's share of global Claude.ai conversations and AI Usage Index",
        "width_cm": 14.0,
        "notes": [
            "Notes: 1) Labels in the right panel show Korea's rank among countries with enough "
            "conversations to be ranked.",
            "2) Snapshots: 4–11 August 2025, 13–20 November 2025, 5–12 February 2026, April 2026 "
            "and May 2026. The dashed line separates weekly samples from the monthly samples of "
            "the June 2026 release, which use different methods.",
            "3) For August and November 2025, Anthropic's published index "
            "({rq1.aui_published.2025-08} and {rq1.aui_published.2025-11}) uses a broader base "
            "that includes conversations not attributed to any country.",
        ],
        "source": "Sources: Anthropic Economic Index; author's calculations.",
    },
    "F2": {
        "headline": "Korean users use Claude more for work and more collaboratively",
        "title": "[Figure 2] Purpose of use and mode of collaboration: Korea and peer economies",
        "width_cm": 14.5,
        "notes": [
            "Notes: 1) Left: shares of conversations classified as work, personal or coursework. "
            "Right: automation (directive and feedback-loop patterns) against augmentation (task "
            "iteration, learning and validation).",
            "2) Peer economies: the advanced Asia-Pacific economies and other members of the BIS "
            "Asian Consultative Council with data. May 2026.",
        ],
        "source": "Sources: Anthropic Economic Index; author's calculations.",
    },
    "F6": {
        "headline": "The capital region accounts for over four-fifths of use but about half of "
        "the population",
        "title": "[Figure 3] Capital region's shares of Claude use, population and employment",
        "width_cm": 11.5,
        "notes": [
            "Notes: 1) Capital region: Seoul, Gyeonggi and Incheon.",
            "2) Residents aged 15–64 and workers by place of work: May 2026; employed persons by "
            "place of residence: first half of 2026. Workers by place of work are employees in "
            "industries other than agriculture, forestry and fishing.",
        ],
        "source": "Sources: Anthropic Economic Index; Ministry of the Interior and Safety; "
        "Ministry of Employment and Labor; Ministry of Data and Statistics; author's "
        "calculations.",
    },
    "F5": {
        "headline": "In May 2026 only Seoul and Incheon used Claude more than their population "
        "share",
        "title": "[Figure 4] Regional usage index",
        "width_cm": 11.0,
        "notes": [
            "Notes: 1) A region's share of Korean Claude.ai conversations divided by its share of "
            "residents aged 15–64; 1 = use in line with population.",
            "2) Bars: May 2026; markers: earlier snapshots.",
        ],
        "source": "Sources: Anthropic Economic Index; Ministry of the Interior and Safety; "
        "author's calculations.",
    },
    "F9": {
        "headline": "Regions differ far more in use than their occupational mix predicts",
        "title": "[Figure 5] Actual and predicted work-related use of Claude per worker, by region",
        "width_cm": 14.5,
        "notes": [
            "Notes: 1) Actual: a region's share of Korean work-related conversations divided by "
            "its share of employment. Predicted: the same implied by the region's occupational "
            "mix and US use per worker in each occupation. Both relative to the national average "
            "(= 1), log scales; dashed line: actual equal to predicted.",
            "2) Right: actual divided by predicted use. May 2026; employment in the first half of "
            "2026.",
        ],
        "source": "Sources: Anthropic Economic Index; Ministry of Data and Statistics; US Bureau "
        "of Labor Statistics; author's calculations.",
    },
    "F10": {
        "headline": "Use follows exposure in rank, with notable exceptions",
        "title": "[Figure 6] Regional ranks of exposure to generative AI and of Claude use",
        "width_cm": 9.0,
        "notes": [
            "Notes: 1) Exposure: ILO generative-AI exposure scores by occupation, averaged over "
            "each region's employment in the first half of 2026. Use: regional usage index, May "
            "2026.",
            "2) Dashed line: equal ranks.",
        ],
        "source": "Sources: Gmyrek et al. (2025); Anthropic Economic Index; Ministry of Data and "
        "Statistics; Ministry of the Interior and Safety; author's calculations.",
    },
}

TABLE_1 = {
    "headline": "A household survey shows much smaller regional differences",
    "title": "[Table 1] Generative-AI use in a household survey and in the Claude data",
    "header": [
        "Region",
        "Used generative AI¹ (%)",
        "Relative to national",
        "Paid subscription¹ (%)",
        "Relative to national",
        "Claude usage index² (May 2026)",
    ],
    "rows": [
        [
            "National",
            "{rq2.survey.experience.national.2025:.1f}",
            "1.00",
            "{rq2.survey.paid.national.2025:.1f}",
            "1.00",
            "1.00",
        ],
        [
            "Seoul",
            "{rq2.survey.experience.seoul.2025:.1f}",
            "{rq2.survey_relative.experience.seoul.2025}",
            "{rq2.survey.paid.seoul.2025:.1f}",
            "{rq2.survey_relative.paid.seoul.2025}",
            "{rq2.index_population.seoul.2026-05}",
        ],
        [
            "Sejong",
            "{rq2.survey.experience.sejong.2025:.1f}",
            "{rq2.survey_relative.experience.sejong.2025}",
            "–",
            "–",
            "{rq2.index_population.sejong.2026-05}",
        ],
        [
            "Daejeon",
            "{rq2.survey.experience.daejeon.2025:.1f}",
            "{rq2.survey_relative.experience.daejeon.2025}",
            "–",
            "–",
            "{rq2.index_population.daejeon.2026-05}",
        ],
        [
            "Gyeonggi",
            "–",
            "–",
            "{rq2.survey.paid.gyeonggi.2025:.1f}",
            "{rq2.survey_relative.paid.gyeonggi.2025}",
            "{rq2.index_population.gyeonggi.2026-05}",
        ],
        [
            "Gangwon",
            "–",
            "–",
            "{rq2.survey.paid.gangwon.2025:.1f}",
            "{rq2.survey_relative.paid.gangwon.2025}",
            "{rq2.index_population.gangwon.2026-05}",
        ],
    ],
    "notes": [
        "Notes: 1) Percent of internet users aged 12 and over, the survey's base for the national "
        "rates, 2025. The survey release names only the three regions with the highest rate of "
        "each measure; '–' means not published.",
        "2) A region's share of Korean Claude.ai conversations divided by its share of residents "
        "aged 15–64.",
    ],
    "source": "Sources: Ministry of Science and ICT and National Information Society Agency "
    "(2026); Anthropic Economic Index; author's calculations.",
}

ANNEX = [
    (
        "Usage data.",
        "The Anthropic Economic Index publishes aggregate statistics from privacy-preserving "
        "samples of Claude.ai conversations, classified by task, purpose, pattern of "
        "collaboration and type of request. This brief uses five snapshots from four releases "
        "(Appel et al., 2025; Anthropic, 2026a; 2026b; 2026c): 4–11 August 2025, 13–20 November "
        "2025, 5–12 February 2026, April 2026 and May 2026. "
        "Regional data start in November 2025. Conversations are located by the user's IP "
        "address. Values that Anthropic does not publish, for privacy reasons or because of small "
        "samples, are treated as missing, never as zero.",
    ),
    (
        "Korean statistics.",
        "Residents aged 15–64 at the end of each month (resident registration, Ministry of the "
        "Interior and Safety); employment by region and occupation, using 56 groups of the Korean "
        "Standard Classification of Occupations, and employed persons by place of residence "
        "(Local Area Labour Force Survey, Ministry of Data and Statistics); workers by place of "
        "work (Labour Force Survey at Establishments, Ministry of Employment and Labor); and GRDP "
        "per capita for 2024 (preliminary).",
    ),
    (
        "Occupational measures.",
        "Use per worker by occupation combines Claude.ai conversations by US occupation (May "
        "2026) with US employment by occupation (Occupational Employment and Wage Statistics, "
        "May 2025). Exposure uses the generative-AI exposure scores of Gmyrek et al. (2025); "
        "Anthropic's observed exposure (Massenkoff and McCrory, 2026) serves as a check. All are "
        "mapped to Korean occupations through the international classification (ISCO-08), "
        "using official crosswalks from the US Bureau of Labor Statistics and the Korean "
        "Standard Statistical Classification.",
    ),
    (
        "Limitations.",
        "The data cover one AI service, whose users do not represent all users of AI, and samples "
        "of one week or one month. Location by IP address can shift recorded use toward Seoul. "
        "Users' occupations are not observed, so use per worker assumes that people ask about "
        "their own occupation's tasks. Seventeen regions allow only descriptive associations. "
        "Anthropic's methods differ across releases, so changes over time partly reflect method "
        "changes; comparisons are made within each snapshot wherever possible.",
    ),
]

REFERENCES = [
    "Anthropic (2026a). Anthropic Economic Index report: Economic primitives. 15 January.",
    "Anthropic (2026b). Anthropic Economic Index report: Learning curves. 24 March.",
    "Anthropic (2026c). Anthropic Economic Index report: Cadences. 26 June.",
    "Appel, R. (2026). India Country Brief: The Anthropic Economic Index. Anthropic, 16 February.",
    "Appel, R., P. McCrory, A. Tamkin, M. Stern, M. McCain and T. Neylon (2025). Anthropic "
    "Economic Index report: Uneven geographic and enterprise AI adoption. Anthropic, 15 "
    "September.",
    "Gmyrek, P., et al. (2025). Generative AI and Jobs: A Refined Global Index of Occupational "
    "Exposure. ILO Working Paper 140. International Labour Organization.",
    "Kim, B., et al. (2026). 김보성·정민수·정유정·장수빈, 「AI와 지역 노동시장 - 지역간 격차 확대 "
    "위험과 새로운 기회」 [AI and Regional Labor Markets: Risks of Widening Regional Gaps and New "
    "Opportunities]. BOK Issue Note No. 2026-25, Bank of Korea, 15 September (in Korean).",
    "Massenkoff, M. and P. McCrory (2026). Labor market impacts of AI: A new measure and early "
    "evidence. Anthropic, 5 March.",
    "McCrory, P. (2026a). How Australia Uses Claude: Findings from the Anthropic Economic Index. "
    "Anthropic, 31 March.",
    "McCrory, P. (2026b). How Canada Uses Claude. Anthropic, 14 July.",
    "Ministry of Science and ICT and National Information Society Agency (2026). 2025 Internet "
    "Usage Survey. Press release, 31 March (in Korean).",
    "Song, H. and B. Lee (2026). 송하윤·이병준, 「주요국의 AI 사용 실태와 한국의 현황」 [AI Use in "
    "Major Economies and the Case of Korea]. KIEP 세계경제 포커스 9(4), Korea Institute for "
    "International Economic Policy, 29 January (in Korean).",
]

# Each exhibit follows the numbered paragraph given, after the text that refers to it, so that the
# text fills the page before an exhibit moves to the top of the next one.
PLACEMENT = [("F1", 6), ("F2", 6), ("F6", 9), ("F5", 10), ("T1", 10), ("F9", 16), ("F10", 18)]

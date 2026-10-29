# Phase 1 — Checksums of downloaded files

SHA-256 and size of the data files and source documents recorded during the Phase 1
verification (2026-10-29), compiled from the verification records. Downloaded files were
hashed locally; rows under AEI-REPO come from the Hugging Face tree listing (LFS SHA-256) at
commit `4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6`, to which all AEI files are pinned. File
names are those the verification passes used; Phase 2 fetchers will store files under their
own paths but must reproduce these checksums. KOSIS responses are API extracts, and KOSIS
revises tables in place, so their checksums are expected to drift; drift is reviewed, not
assumed to be an error.

| ID | File | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| ABS-ERP | `ERP_Q_persons_15-64_bystate_2024Q1-latest.csv` | 46,509 | `236640a82a9218216d63e5398e365ab1202b6f03d108b1a94c53cdeef96b235c` |
| AEI-2025-09 | `aei_analysis_functions_claude_ai.py` | 92,526 | `e3899e54efda712dcf81ad6db7c799a4f0389253cd5c4c09efdb196ef718901b` |
| AEI-2025-09 | `aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv` | 26,840,881 | `48a2c39f8a98ce7c2ba72767cbe3760fd55ba4a64a193abfecefc76d19852c09` |
| AEI-2025-09 | `aei_raw_1p_api_2025-08-04_to_2025-08-11.csv` | 7,027,019 | `c0fc061ea7d4feb71a7bd88c528d54e2d3a11e2045574f1e1fb2d594eebffd0f` |
| AEI-2025-09 | `aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv` | 18,894,517 | `c8ef9c5eee0c42febc73e358ecc7d2358e0a0ce3b50122c0c15ae8ec569aceff` |
| AEI-2025-09 | `aei_report_v3_preprocessing_claude_ai.ipynb` | 85,914 | `ae091150222670abefc49d9b59f1794457002a1115a090dfe35f4a706a11fb88` |
| AEI-2025-09 | `iso_country_codes.csv` | 4,564 | `eee318d4ab2c2c30f5a7da11f2bc7e0e36c246f6be5bb9b323fdb12b8e4809e0` |
| AEI-2025-09 | `Population by single age _20250903072924.csv (saved with underscores)` | 2,176 | `89c1e953dbab481760a966c40bdb121ed4e301b4cd0cbaea8a44990caa91ce8e` |
| AEI-2025-09 | `preprocess_population.py` | 13,542 | `fcb0f7eaad56c12963dc5c471cb837040cdd4d4dac796bd0e048d0824d6aa13d` |
| AEI-2025-09 | `README.md (dataset card, repository root)` | 5,262 | `7f3a9c7c8fb2c04c55794810671926466698f171294cd2641075eb7bc403a9f0` |
| AEI-2025-09 | `release_2025_09_15/data_documentation.md` | 20,133 | `d7e23aa0888628fdeb27f49a14e151c41ea99d47bd5dd65e84383b203c23464a` |
| AEI-2025-09 | `release_2025_09_15/README.md` | 2,640 | `cfb576732eb4768d9ee071d13b71c578db9ee47708d85a78181ac6cba47b97ff` |
| AEI-2026-01 | `aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv` | 94,086,309 | `70dc16780061b84d3f34ddf7fe5c978d65c99a5ef58afd78f9315f886a6a5873` |
| AEI-2026-01 | `data_documentation.md (release_2026_01_15)` | 18,721 | `50f117f8f995606004680749fc43012d2bd83c5fc9dab6044a935f601643ef6f` |
| AEI-2026-03 | `aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv (current version)` | 103,287,181 | `69ebf6f9afc1e3be45caab172a84ae09e78bf41b97e1c310100d81c8a35a7433` |
| AEI-2026-03 | `aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv (original 2026-03-24 version, commit 7fc50b03)` | 96,018,130 | `9c53320b8732ac2e88fc2c95fbdefa02222f04333a41d4f4e947861409798cf1` |
| AEI-2026-03 | `data_documentation.md (release_2026_03_24)` | 17,739 | `0a194ff1e317567e8b5d68d581fa2e5f8a1d3112f71aa209d2caa408ee12a779` |
| AEI-2026-06 | `aei_1p_api_2026-06-26.csv` | 77,282,477 | `62197f003e001945ad130c2f26f5e07f3fda45ff41644df91444b04fd524a19f` |
| AEI-2026-06 | `aei_claude_ai_2026-06-26.csv` | 219,174,671 | `f974b358bce0e5a8417510c61da4342234cd0de9d9d0b62acf4c6dbcf8ec7b68` |
| AEI-2026-06 | `data_documentation.md` | 7,397 | `1a01eeb7d34250b192aa9c906098bea1db971644e6bdb04497d87b7a4ed141a5` |
| AEI-APX | `aei_v4_appendix.pdf` | 6,036,245 | `2c23a233ea334600881c614c7dd76db05a45f46d4ecff61a050680736ba9a9ed` |
| AEI-LMI | `labor_market_impacts/job_exposure.csv` | 37,176 | `4f0a3adf5feeb2ec5f5d02ab18cc5e851a2a4b8470bde84c0c9335017be12d68` |
| AEI-LMI | `labor_market_impacts/task_penetration.csv` | 1,889,822 | `85bee872db1d55d3e9a7f4e89da5ae4a5d59aa8ec875d728fbf4b7d820984616` |
| AEI-ONET20 | `onet_task_statements.csv` | 3,650,862 | `88427f8d2a9f37a7c08b5420c6c66a01cdae6467b716bbbd31989128504b8ebb` |
| AEI-ONET20 | `release_2025_09_15/data/input/onet_task_statements_raw.xlsx` | 1,204,658 | `373cdc961891d04bcd29db66c43c7cf412d61fe3ef1f49e634dd979f4d5a3a95` |
| AEI-ONET20 | `release_2025_09_15/data/input/soc_structure_raw.csv` | 77,176 | `05eb5e689fb471b7a66962b57bba6666dee2c3e6a6854f0f84faf423af68dd17` |
| AEI-ONET20 | `release_2025_09_15/data/intermediate/soc_structure.csv` | 78,834 | `97dee70470182ac642872839f71a4a938c03677829aadca9bfbf250cb4021863` |
| AEI-REPO | `.gitattributes` | 3,375 | `ba0cae3e640fe1174c85a8073a9e619a521aaac4d750a980d18e9c8d67fb6f64` |
| AEI-REPO | `release_2025_09_15/data/input/automation_vs_augmentation_v1.csv` | 197 | `d1e264882b17618db4f4a00b6f87f48134222bc5c15eefb3d46aae9519e89d11` |
| AEI-REPO | `release_2025_09_15/data/input/automation_vs_augmentation_v2.csv` | 198 | `0d7d8b1666f3d942d728f9b2177681ca6756edfe01fb8fc130e29264d41a391e` |
| AEI-REPO | `release_2025_09_15/data/input/bea_us_state_gdp_2024.csv` | 1,663 | `913bc0d017570e711c71bc838016b3b52cbf49e717d0cabc4cc2d70306acfa5a` |
| AEI-REPO | `release_2025_09_15/data/input/BTOS_National.xlsx` | 63,052 | `c55e2fc6892941a1a536e87445de0bee8ea327526081389b93b85c54a8d69761` |
| AEI-REPO | `release_2025_09_15/data/input/census_state_codes.txt` | 1,485 | `bea4e03f71a1fa0045ae732aabad11fa541e5932b071c2369bb0d325e8cba5a0` |
| AEI-REPO | `release_2025_09_15/data/input/geonames_countryInfo.txt` | 31,667 | `0be4994498c57cd6ef79a5c7a480a4a98f5b1579aa4b5d30ef33be9699c1fc26` |
| AEI-REPO | `release_2025_09_15/data/input/imf_gdp_raw_2024.json` | 265,358 | `d8583c093381da17225f57ee69ab39285f4c9557d53fa1ce5a8ce1160950c509` |
| AEI-REPO | `release_2025_09_15/data/input/sc-est2024-agesex-civ.csv` | 818,707 | `334210a5080a6e470db22e42346ba7e6d0d43490887e08c5ed3ece62a7adfa9c` |
| AEI-REPO | `release_2025_09_15/data/input/task_pct_v1.csv` | 461,306 | `8de89c99f762146c9e46b2202c3501e2a14f11c5b44c61c8007021127b6c676e` |
| AEI-REPO | `release_2025_09_15/data/input/task_pct_v2.csv` | 435,372 | `0c20f184cd4a1e3d8ef3d77f500b32b62431ce61a3c2f133c3af7fa8429f97db` |
| AEI-REPO | `release_2025_09_15/data/intermediate/gdp_2024_country.csv` | 4,115 | `e0618d6ba634a612b97b1c82f521ab38a387216069818a86f50c9aaf8e2bda6c` |
| AEI-REPO | `release_2025_09_15/data/intermediate/gdp_2024_us_state.csv` | 2,179 | `cb1573e8143bd407c2ea7c43f5a6822852568c596dbde843fc5d8692c9e967ec` |
| AEI-REPO | `release_2026_01_15/data/intermediate/aei_raw_1p_api_2025-11-13_to_2025-11-20.csv` | 41,518,256 | `432f8d14348ba384dd9c659fa7fdc85754cbae3b5a480c14a344ac4823d0e861` |
| AEI-REPO | `release_2026_03_24/data/aei_raw_1p_api_2026-02-05_to_2026-02-12.csv` | 43,957,174 | `b3bcd68e7f6d820ffbb50a3c53d71ec2a122556fc2a38226cd86951a054bd4c8` |
| AEI-ROBOT | `robot_exposure/README.md` | 7,769 | `34cce581f932237800f92494338aaa73f737a1af1e18f46ae6f4fb85e8eba408` |
| AEI-ROBOT | `robot_exposure/robot_exposure_tasks.csv` | 99,520,982 | `28b17551a913fd0d0bad1deb0d1c83584d9a936270e6e545eefb3a8aee081586` |
| AEI-WAP2024 | `release_2025_09_15/data/input/working_age_pop_2024_country_raw.csv` | 22,974 | `7c86dcb133a3f9f54f5f22e74683f5d6c5cc97faa9ddc2cdd466a4422cd4124c` |
| AEI-WAP2024 | `release_2025_09_15/data/intermediate/working_age_pop_2024_country.csv` | 6,321 | `3a9e0edc0453702e8efb63d7cab57e5b1a689bc09e070626bbf513e37edd5dd3` |
| AEI-WAP2024 | `release_2025_09_15/data/intermediate/working_age_pop_2024_us_state.csv` | 1,079 | `e2d0fb7239934f4f6d0ae3444ab12ad8ff1dd323b71ccfc4295d074b537f17ec` |
| ANT-AEI-2025-09-RPT | `Economic-Index.pdf` | 13,850,183 | `42c34a517e9184ff06d5e3ab084e8a70c013c6fda60db4c97407bfbd582fde42` |
| ANT-AEI-2026-06 | `aei_june2026_report_appendix.pdf` | 2,707,986 | `771ad63f5867478dddf31a44b95e80c59b3059cda3543ecba229da3fe72618fc` |
| ANT-LMI | `2b5bbaf2c1eb81dbf6e6fb813c1a24e35a64d376.pdf` | 2,419,969 | `48c941dbdc1053456ec72f893c6a27630559507d3882895bb036d034b6972450` |
| ANT-LMI | `e5f77fc0e77c0185110b5e4b909602791ae76eae.pdf` | 993,038 | `25f3333efae2766a67f3ffaea0431a5e417b89bb680ac1f2587f11ab67a3643e` |
| ATLAS-KR | `KR.json` | 3,937 | `cbb9a656ac754fae59faebf1f1c50644a66ef0594c21d7ad53b937068874c284` |
| BOK-2025-02 | `BOK_IssueNote_2025-2.pdf` | 2,345,594 | `ea79c741fea4d9b0134856298241b1cd953d00194e74cd910a83977ccde0ee8f` |
| BOK-2026-09 | `BOK_IssueNote_2026-25.pdf` | 4,285,750 | `a001417f37b5562141a67b3382161e762a584cdff336e1f0df7b04573f8e50e1` |
| CL-KSCO7 | `KSCO_201707_20260128012209.pdf` | 4,716,749 | `0f26b7446066b1ae8a142aa4eb97dc418cbaefe8766d22fcd5b7f13cc387f38e` |
| CL-KSCO8 | `1. (해설서) 제8차 한국표준직업분류(2차 정오표 반영)_최종_20250722023539.pdf` | 4,881,063 | `2aa8e296112e4ba98481f4a783ecec21ec470c9646ed95845ac65273f492580d` |
| ILO-WP140 | `4digits_with_tasks.xlsx` | 245,645 | `6ae251a73addcc7c397a4d6e777662c698f879fa748a677f04a7242a8527e2a5` |
| ILO-WP140 | `Final_Scores_ISCO08_Gmyrek_et_al_2025.xlsx` | 2,598,951 | `c1940b87e7293b1eb95b530b6d3da7cd806b61d217c4bff1e69372b2cff5c90a` |
| ILO-WP140 | `output_data.json` | 876,668 | `c73052a0fb47d2df5d40c5c886c264cc20984e3fbad0631a0f1f9bde1cd3d98b` |
| ILO-WP140 | `WP140_web.pdf` | 4,211,233 | `9077761c72aabaa3c7ee70999ec5aa46a6afcf943b5fb01baa971f601d363ee9` |
| KIEP-2026-01 | `KIEP_WEF_26-04.pdf` | 1,390,169 | `d829ea052c696ad3c55fab93b1ec9d7d3e9cb7978a92682320cd1b264c171e5d` |
| KR-CENSUS2020-OCC | `DT_1PC2012_2020.json` | 10,478,121 | `b2a777f898cf5d6810d7da4304f008c4421f9dfae82bb0b238bbf89b23c1e22c` |
| KR-CENSUS2020-OCC | `DT_1PD2002_2020.json` | 5,970,082 | `2e01710dcb047b10f8d1b03479a7f17867d7aee412d02580a141b857f1397adb` |
| KR-GRDP | `DT_1BPB001_T10_medium_sido_total_2023_2024.json` | 27,519 | `9aa3ee2d8a8ae55fdb7bcb9712fcec639923df93dc249350f30ed80044d31eae` |
| KR-GRDP | `DT_1C91_T1_Z10_sido_2023_2024.json` | 20,104 | `fc3fdbe360f2d303ea6b6b607c9ebd41dc452ab7327fff978cbf01157f55ca48` |
| KR-GRDP | `DT_1C96_all_sido_2015_2024.json` | 418,941 | `40ea2a09db4113a7616c89fb804e73f1a3e3251c657661869a9d175820a51159` |
| KR-GRDP | `expl_1989005.json (KOSIS 통계설명, 지역소득)` | 18,913 | `491a365545382e9e1caf70995a28b32cc60118324b16c6383168774df9fa6d63` |
| KR-MDIS | `mdis_items_A_2025H2_get.json` | 35,936 | `4c2110fbb4c6bd88ddfa03bd9b80384b72f5c98e83432837abf174040e9bcd30` |
| KR-MDIS | `mdis_items_B_2025H2_get.json` | 32,716 | `dd4c84e412384924007ef17c2b6551996fedd01632a0879fbfa303c1fc422683` |
| KR-MDIS | `mdis_items_C_2025H2_get.json` | 40,207 | `008164c2f653eff8ee7e7d4608316eacced333df49d19662469412ecae6265f9` |
| KR-MDIS | `mdis_rspn_C_2025H2_11360429.json` | 140,397 | `1059b04368785ac0996706d197384df8a094077119746d52f1aea577dd086442` |
| KR-OCC | `DT_1ES3B06J_2013H1-2019H2.json` | 10,467,553 | `18f24fa9cdfc66414cd81b539157a6c1c21430cafb2ad24e4161ae31cae840bc` |
| KR-OCC | `DT_1ES3B06J_2020H1-2026H1.json` | 10,022,373 | `3503c373641d1fe88a23ca24403a8e868806d3bf70b2f8ad537abc858764a34d` |
| KR-OCC | `DT_1ES3B06J_2026H1.json` | 773,756 | `03fe8163171d8bc1c3e0f3098c77af44faac7aad1489b291890879aacdd0aae3` |
| KR-OCC | `DT_1ES3B06S_2022H1-2024H1.json` | 3,806,646 | `3e79e6c35c624d04c12fe80c0759361f842fe86b5bdeb15a11c60fc4674d55e3` |
| KR-OCC | `DT_1ES3B32J_2025H2-2026H1.json` | 671,542 | `3c03c4946acddd613bbe3015fc811df9725269c885c41f1dd4732bfd4ac1a262` |
| KR-OCC | `statExpl_2006081.json` | 13,955 | `a1df5ef5f32658a0792c795d05bae679b973e921a044704821e902a620b168c8` |
| KR-OCC-EAPS | `DT_1DA7E34S_NEW_M_202501-202609.json` | 2,847,115 | `f5c3b29f121f1e1a56329f9421154394e9a6b7140101b3f1756dcc1acd1db173` |
| KR-OCC-WORK | `DT_1ES3C07S_2025H2.json` | 901,491 | `bb568fc8a05ed8db0b64ae9b930b5d71c24c2755ff540c7cb5d56c286f3ea53b` |
| KR-OCC-WORK | `DT_1ES3C07S_2026H1.json` | 901,435 | `1a199f8594cc9dd037eb91f505b9b2606052d8dbd8c99dd7ab2dbff91b50006b` |
| KR-POP | `DT_1B04005N_T2_merger_check_202604_202609.json` | 92,542 | `864cf9c37ae3d26cc98db07e4c5118a7999a8a395cd00586b9edafd7a1d4d70f` |
| KR-POP | `DT_1B04005N_T2_sido_age5_202508_202605.json` | 2,216,576 | `e2d1b063c34b7a03a08ae4d0f3c05930c7e9ed2a62b700d02b347dc4063a7fb7` |
| KR-POP | `DT_1B04006_T2_sido_age1_202508_202605.json` | 9,142,344 | `7d68e299909a4d654583834040ca3c4701a9322df4e2593c96478c5909be3143` |
| KR-POP | `expl_2008001.json (KOSIS 통계설명, 주민등록인구현황)` | 5,697 | `f255eb771c77f79de4b470bdba939ab0dc56f4948d34cf8cf53e667a91c1f0bf` |
| KR-WORK | `DT_1ES3A01S_all_sigungu_202502_202601.json` | 1,792,555 | `a2cba495ff52a947be885501c30bf106242f9b1999050a4dc58f611db5f9654f` |
| KR-WORK | `DT_1ES3B01J_all_sido_202502_202601.json` | 426,621 | `1558b6e3ae07ed3dbe6d8a969a2f8e156ad517db01544ad6f4539f574e53dbc9` |
| KR-WORK | `DT_1ES3C01S_all_sigungu_202502_202601.json` | 1,241,445 | `3fde503bde7c14628a1c2aa5bb8a84ca7d689b336fdba8af50a9af10f7790e46` |
| KR-WORK-EST | `DT_118N_MOND66_emp001_sido_total_202508_202605.json` | 100,481 | `6a33f513af6e8614e0c520346a1722b7a78c3648cab0d6d85238b60f2337b375` |
| US-OEWS-NAT | `oesm25nat.zip` | 279,525 | `b5855a37f3e03e779f6fbf173d3bbc94aeeff33426aef32fa95ce6d025bab1af` |
| US-OEWS-NAT | `oesm25nat/national_M2025_dl.xlsx (zip member)` | 289,615 | `852250997ceff9b721ff68f63e877d818f9c1ec8b1b69dd367958faedd5282b2` |
| US-OEWS-NAT-M2024 | `oesm24nat.zip` | 282,052 | `5fa368aa034ca784f0a4f67f0f1bac67072c5a07992ac3e3de92db10a2821043` |
| US-OEWS-OCCDEF-M2021 | `occupation_definitions_m2021.xlsx` | 253,633 | `6a1f0e54a292b3aca178f3b27a5d899afcb2f773282bfcf89a05121f9e1efc45` |
| US-OEWS-ST | `oesm25st.zip` | 7,563,829 | `74d5be0e1df865517d22dc3bd1fc3a8af5f6f9e3052a2163143021505d8e04c6` |
| US-OEWS-ST | `oesm25st/state_M2025_dl.xlsx (zip member)` | 7,675,521 | `e9590ec791fd2941341631f84ee6445d3df931c1ad5776b80ea07c9f89fba95d` |
| US-SOC2018 | `soc_structure_2018.xlsx` | 51,367 | `ade08af40923266f3a854842e888ca3e93c15b26a147c20a2b12a61f4c4f4077` |
| WB-POP | `countries.json` | 113,954 | `c9acf3932785191a649cbc04c3056af4cf64a236e5c3b49d49be25ddb0440bce` |
| WB-POP | `indicator_SP.POP.1564.TO.json` | 557 | `a705d3d61c94e0242753babb205e491204e6f02f426cce189b64b0dcd3815214` |
| WB-POP | `SP.POP.1564.TO_2023-2025.json` | 171,632 | `114dfccd9f217e91545caab532f8042fc22de471bccabe8ed7e08fa1ac915a4f` |
| XW-ISCO-SOC | `ISCO_SOC_Crosswalk.xls` | 311,296 | `0936c78c4ab2cb0b61d7cfe3dcf0f94d943a4e30b11dade1f11676307e2c0aae` |
| XW-ISCO-SOC | `ISCO_SOC_Crosswalk_process.pdf` | 59,708 | `8ca9ac78b4afd27743f7d165ff016001ec7eaef35f3b04c6f46972fc087d6fec` |
| XW-KSCO-ISCO | `한국표준직업분류(KSCO 8차)-국제표준직업분류(ISCO-08) 연계표_20251103085955.xlsx` | 328,025 | `d401d12d503abf353ed1ef026c1d44fef8be38c88dfdbf168548b341e0a11633` |
| XW-KSCO87 | `(붙임) 제8차 한국표준직업분류 연계표 (8차→7차 7차→8차)_250604_20250604045126.xlsx` | 203,517 | `4a55293c39d802d5df2c740138a294fc26b0ff95f27dfc3109bef9c4dfabf285` |
| XW-KSCO87 | `4. 구신 신구 연계표_20250115013713.xlsx` | 179,489 | `508d7e6fbaf7dfe2ab30b9f2551acbdd7febef16b3e1e725c9be9804670e08fe` |
| XW-KSCO87 | `한국표준직업분류 연계표(8-5차_종합)_260921_20250604045215.xlsx` | 376,107 | `8f472263e1c1f9194f1ef1c05b1cd8de095a3c7c9e2c11d89ffcb3db4fe10134` |
| XW-KSCO87 | `한국표준직업분류 연계표(8-7 7-6 6-5 5-4 4-3)_250604_20250604045215.xls` | 1,432,576 | `f54a7c61fa8c173bfebf41e866a3580e2cf77c54ca6f6352b335689f251ab9d5` |
| XW-KSCO87-DGK | `산업직업분류 연계표_2025년 2분기.csv` | 608,239 | `5915b9678fdc5f2aab753ac703da4c7ea3eba1a0a094c48adae36d6be1e794c4` |
| XW-ONET | `2019_to_SOC_Crosswalk.csv` | 91,732 | `506fff0a3ca0d26137b9389322413022a4348bead559c4dd24edeb2cea86aa89` |
| XW-ONET | `2019_to_SOC_Crosswalk.xlsx` | 44,847 | `bfc6722a92c2d607e5a99dee88b7826cf5aa91f7c0453182e0c8268e32a20a19` |
| XW-SOC1018 | `soc_2010_to_2018_crosswalk.xlsx` | 46,630 | `f3a847561562d3e5a30eb848f2902a5f7b02e9c48b3d7f2cc8879899fbc242a7` |
| XW-SOC1018 | `soc_note_2010_to_2018_crosswalk.pdf` | 147,117 | `18e05874b6976ef06b637c6d975d4f602643d4f4d5e38ee1db2f08c683426a04` |

# DESTA v2.3 match report (2026-11-23)

A snapshot of how the trade agreements registry covers the DESTA list of treaties, written by the DESTA walk (`scripts/oneoff/match_desta.py`, `scripts/oneoff/import_desta.py`). It describes the registry on 2026-11-23: `main`, the pull requests open on that day (datenoio/internacia-db#207 to #231, several of which have since merged), and the records this walk adds. Do not treat its gap lists as current.

Every DESTA base treaty, with its group, record and action, is in [desta-match-2026-11-23.csv](desta-match-2026-11-23.csv).

## Source

[DESTA](https://www.designoftradeagreements.org/downloads/) (Design of Trade Agreements) v2.3: `desta_list_of_treaties_02_03.csv` (1410 rows: 903 base treaties, 208 accessions, 72 withdrawals, 77 protocols or amendments, 72 consolidated versions, 78 negotiations), `desta_list_of_treaties_02_03_dyads.csv` (country pairs, ISO 3166 numeric codes) and `desta_dyadic_withdrawal_02_03.csv`. DESTA gives a year of signature and of entry into force and a WTO flag, not a status. The WTO RTA-IS export (`ExportAllRTAList.aspx`, 2026-11-23) supplied the RTA IDs for WTO-listed treaties.

## Method

1. A WTO-listed treaty is matched by its `wto_name` to an RTA ID in the export, and the RTA ID to a record's `wto_rta_id`. DESTA uses older WTO names, so 119 of the 495 WTO-listed treaties fall through to step 2.
2. A bilateral treaty (`typememb` 1) needs a two-party record with the same two countries. A plurilateral treaty needs a record whose roster (parties, or members of a linked or party intblock) matches the DESTA members; a bloc-and-country record (`EU` and Mexico) must have the same third countries. The year of signature, or of entry into force, may differ by one.
3. An acronym in the DESTA name that is a record id (`SPARTECA`), and five hand matches.
4. A record claimed by two treaties keeps the one with the closer year; the other becomes ambiguous.

The CSV gives each treaty a `confidence`: `high` for a hand match, a single WTO RTA ID, or the same parties and the same year; `medium` for the same parties a year apart, a roster or bloc match, or an acronym; `low` for ambiguous and `none` for missing treaties. A later `desta_id` backfill can take `high` and `medium` rows as they are (`desta_number`, `record_id`) and review the `low` ones. Confidence: high 614, none 141, low 87, medium 61.

## Results

| Group | Treaties | Bilateral | Plurilateral | Plurilateral and third country | Region-region |
|---|---|---|---|---|---|
| matched | 675 | 450 | 55 | 153 | 16 |
| ambiguous | 87 | 45 | 28 | 9 | 5 |
| missing | 141 | 120 | 16 | 1 | 4 |

Matched treaties by where the record is: main 569, this PR 54, #209 26, #226 21, #231 3, #210 2. One treaty has no `typememb`.

Bilateral country pairs: DESTA has 532. 166 had no two-party record on `main` (the planning review counted 238 with an earlier registry and code mapping). After the open pull requests and this walk, 105 have none. A pair with a record can still miss an older instrument: those treaties are in the ambiguous group.

**Ambiguous** treaties have records with the same parties but another year (usually an earlier or later instrument between the same countries, such as the 1980s ALADI agreements that later ACEs replaced) or share one record with another DESTA treaty (DESTA lists the early harvest, the main agreement or the Dickenson Bay and Chaguaramas texts separately).

**Missing** treaties have no record with their parties. Of the 120 bilateral ones, 118 are not WTO-listed. By region: Asia 33, Intercontinental 29, Africa 25, Europe 19, Americas 11, Oceania 3. The largest groups: Arab bilaterals of the 1950s to 2000s (many with Iraq in 2001 and 2002), most of them between countries that are now all members of the Greater Arab Free Trade Area; 1990s bilaterals between CIS states; Nordic agreements with the Faroe Islands and Greenland; and trade agreements of Canada and Australia from the 1950s and 1960s. The 21 missing plurilateral treaties are mostly organisation treaties (the EEC Treaty and its revisions, the ECSC, Benelux, CEAO, UDEAO, CEPGL, the Lomé and Cotonou conventions); some have an intblock but no registry record.

## Added in this walk

54 records. Each cites a depositary, a party government or the WTO for its status and dates and DESTA (provenance field `desta_id`) only for listing it.

12 ALADI records were superseded by an agreement whose record is only in an open pull request (datenoio/internacia-db#209 or #226), so they are `terminated` for now; their notes name the successor. Once those pull requests merge they become `superseded` with `superseded_by`: `ARBO-1992` (`MERCOSURBO`), `ARCU-1999` (`MERCOSURCU`), `BOPY-1994` (`MERCOSURBO`), `BOUY-1991` (`MERCOSURBO`), `BRCU-1999` (`MERCOSURCU`), `BRPE-1993` (`BRCAN-ACE39`), `BRVE-1994` (`BRCAN-ACE39`), `CLPE-1983` (`CLPE-1998`), `CLUY-1985` (`MERCOSURCL`), `COCU-1994` (`COCU`), `CUPY-2000` (`MERCOSURCU`), `CUUY-1999` (`MERCOSURCU`).

| Record | DESTA | Name | Status | Signed | In force | Ended | Source of status |
|---|---|---|---|---|---|---|---|
| `ARBO-1992` | 31 | Economic Complementation Agreement No. 19 between Argentina and Bolivia | terminated | 1992-04-28 | 1992-04-28 | 1997-02-28 | ALADI, historical agreements database |
| `ARBR-1986` | 32 | Economic Complementation Agreement No. 7 between Argentina and Brazil | superseded | 1986-12-10 | 1987-01-01 | 1990-12-20 | ALADI, historical agreements database |
| `ARBR-1988` | 33 | Economic Complementation Agreement No. 12 between Argentina and Brazil | superseded | 1988-09-09 | 1988-09-01 | 1990-12-20 | ALADI, historical agreements database |
| `ARCAN-ACE48` | 24 | Economic Complementation Agreement No. 48 between Argentina, Colombia, Ecuador, Peru and Venezuela | superseded | 2000-06-29 | 2000-08-01 | 2006-01-02 | ALADI, historical agreements database |
| `ARCO-1988` | 36 | Economic Complementation Agreement No. 11 between Argentina and Colombia | superseded | 1988-04-28 | 1988-08-01 | 2000-08-01 | ALADI, historical agreements database |
| `ARCR-1983` | 37 | Partial Scope Agreement No. 2 between Argentina and Costa Rica (Article 25 of the 1980 Montevideo Treaty) | terminated | 1983-08-31 | 1983-08-31 | 1994-12-31 | ALADI, historical agreements database |
| `ARCU-1984` | 38 | Partial Scope Agreement No. 4 between Argentina and Cuba (Article 25 of the 1980 Montevideo Treaty) | superseded | 1984-03-16 | 1984-05-16 | 2000-01-01 | ALADI, historical agreements database |
| `ARCU-1999` | 39 | Economic Complementation Agreement No. 45 between Argentina and Cuba | terminated | 1999-12-30 | 2000-01-01 | 2007-07-02 | ALADI, historical agreements database |
| `ARPE-1988` | 46 | Economic Complementation Agreement No. 9 between Argentina and Peru | superseded | 1988-03-11 | 1988-04-01 | 2000-08-01 | ALADI, historical agreements database |
| `ARSV-1983` | 42 | Partial Scope Agreement No. 3 between Argentina and El Salvador (Article 25 of the 1980 Montevideo Treaty) | terminated | 1983-08-27 | 1983-10-27 | 1994-12-31 | ALADI, historical agreements database |
| `ARUY-1982` | 699 | Economic Complementation Agreement No. 1 between Argentina and Uruguay | terminated | 1982-12-20 | 1985-11-27 | 2003-05-01 | ALADI, historical agreements database |
| `ARVE-1986` | 48 | Economic Complementation Agreement No. 10 between Argentina and Venezuela | superseded | 1986-04-11 | 1986-04-11 | 1995-08-06 | ALADI, historical agreements database |
| `ARVE-1992` | 49 | Economic Complementation Agreement No. 20 between Argentina and Venezuela | superseded | 1992-10-06 | 1995-08-06 | 2000-08-01 | ALADI, historical agreements database |
| `BOBR-1994` | 118 | Economic Complementation Agreement No. 26 between Bolivia and Brazil | terminated | 1994-01-27 | 1994-01-27 | 1995-12-31 | ALADI, historical agreements database |
| `BOMX-1994` | 124 | Economic Complementation Agreement No. 31 between Bolivia and Mexico | superseded | 1994-09-10 | 1995-01-01 | 2010-06-07 | ALADI, historical agreements database |
| `BOPY-1994` | 125 | Economic Complementation Agreement No. 29 between Bolivia and Paraguay | terminated | 1994-03-15 | 1994-03-15 | 1997-02-28 | ALADI, historical agreements database |
| `BOUY-1991` | 126 | Economic Complementation Agreement No. 15 between Bolivia and Uruguay | terminated | 1991-04-12 | 1991-04-12 | 1997-02-28 | ALADI, historical agreements database |
| `BRCU-1999` | 139 | Economic Complementation Agreement No. 43 between Brazil and Cuba | terminated | 1999-12-22 | 2000-01-01 | 2007-07-02 | ALADI, historical agreements database |
| `BRMX-1983` | 712 | Partial Scope Renegotiation Agreement No. 9 between Brazil and Mexico | superseded | 1983-04-30 | 1984-01-01 | 2003-05-02 | ALADI, historical agreements database |
| `BRPE-1993` | 142 | Economic Complementation Agreement No. 25 between Brazil and Peru | terminated | 1993-12-31 | 1994-09-28 | 1999-08-16 | ALADI, historical agreements database |
| `BRVE-1994` | 145 | Economic Complementation Agreement No. 27 between Brazil and Venezuela | terminated | 1994-07-15 | 1995-01-31 | 1999-08-16 | ALADI, historical agreements database |
| `CLEC-1994` | 203 | Economic Complementation Agreement No. 32 between Chile and Ecuador | superseded | 1994-12-20 | 1994-12-20 | 2010-01-25 | ALADI, historical agreements database |
| `CLEC-2008` | 204 | Economic Complementation Agreement No. 65 between Chile and Ecuador | superseded | 2008-03-10 | 2010-01-25 | 2022-05-16 | ALADI, historical agreements database |
| `CLMX-1991` | 211 | Economic Complementation Agreement No. 17 between Chile and Mexico | superseded | 1991-09-22 | 1991-09-22 | 1999-08-01 | ALADI, historical agreements database |
| `CLPE-1983` | 214 | Partial Scope Renegotiation Agreement No. 28 between Chile and Peru | terminated | 1983-04-30 | 1983-05-01 | 1998-07-01 | ALADI, historical agreements database |
| `CLUY-1985` | 217 | Economic Complementation Agreement No. 4 between Chile and Uruguay | terminated | 1985-02-01 | 1985-02-01 | 1996-10-01 | ALADI, historical agreements database |
| `COCU-1988` | 231 | Partial Scope Agreement No. 19 between Colombia and Cuba (Article 25 of the 1980 Montevideo Treaty) | superseded | 1988-12-12 | 1989-11-21 | 1995-01-01 | ALADI, historical agreements database |
| `COCU-1994` | 232 | Partial Scope Agreement No. 33 between Colombia and Cuba (Article 25 of the 1980 Montevideo Treaty) | terminated | 1994-07-08 | 1995-01-01 | 2001-07-14 | ALADI, historical agreements database |
| `COGT-1984` | 236 | Partial Scope Agreement No. 5 between Colombia and Guatemala (Article 25 of the 1980 Montevideo Treaty) | superseded | 1984-03-01 | 1985-09-02 | 2009-11-12 | ALADI, historical agreements database |
| `CRMX-1982` | 247 | Partial Scope Agreement No. 1 between Costa Rica and Mexico (Article 25 of the 1980 Montevideo Treaty) | superseded | 1982-07-22 | 1984-06-15 | 1995-01-01 | ALADI, historical agreements database |
| `CUMX-1985` | 268 | Partial Scope Agreement No. 12 between Cuba and Mexico (Article 25 of the 1980 Montevideo Treaty) | superseded | 1985-03-11 | 1986-05-28 | 2001-02-28 | ALADI, historical agreements database |
| `CUPY-2000` | 270 | Economic Complementation Agreement No. 52 between Cuba and Paraguay | terminated | 2000-11-20 | 2001-04-25 | 2009-02-24 | ALADI, historical agreements database |
| `CUUY-1999` | 275 | Economic Complementation Agreement No. 44 between Cuba and Uruguay | terminated | 1999-12-23 | 2000-01-01 | 2008-09-03 | ALADI, historical agreements database |
| `GTMX-1984` | 467 | Partial Scope Agreement No. 10 between Guatemala and Mexico (Article 25 of the 1980 Montevideo Treaty) | superseded | 1984-09-04 | 1985-06-07 | 2001-03-15 | ALADI, historical agreements database |
| `MXNI-1985` | 610 | Partial Scope Agreement No. 13 between Mexico and Nicaragua (Article 25 of the 1980 Montevideo Treaty) | terminated | 1985-04-08 | 1986-08-12 | 1998-06-30 | ALADI, historical agreements database |
| `MXSV-1986` | 417 | Partial Scope Agreement No. 15 between Mexico and El Salvador (Article 25 of the 1980 Montevideo Treaty) | superseded | 1986-02-06 | 1987-06-11 | 2001-03-15 | ALADI, historical agreements database |
| `MXUY-1986` | 615 | Economic Complementation Agreement No. 5 between Mexico and Uruguay | superseded | 1986-05-07 | 1986-06-01 | 2004-07-15 | ALADI, historical agreements database |
| `AECF` | 1122 | UAE-Central African Republic Comprehensive Economic Partnership Agreement | signed | 2025-03-06 |  |  | Emirates News Agency (WAM) |
| `AEIL` | 1096 | UAE-Israel Comprehensive Economic Partnership Agreement | in_force | 2022-05-31 | 2023-04-01 |  | Israeli Ministry of Foreign Affairs, Consulate General in Dubai, bilateral relations |
| `AEKE` | 1124 | UAE-Kenya Comprehensive Economic Partnership Agreement | signed | 2025-01-14 |  |  | Kenya National Assembly, Hansard, 18 November 2025 |
| `AEMU` | 1132 | UAE-Mauritius Comprehensive Economic Partnership Agreement | in_force | 2024-07-22 | 2025-04-01 |  | UAE Ministry of Economy and Tourism |
| `AERS` | 1129 | UAE-Serbia Comprehensive Economic Partnership Agreement | in_force | 2024-10-05 | 2025-06-01 |  | UAE Ministry of Economy and Tourism |
| `BWZW` | 137 | Trade Agreement between Botswana and Zimbabwe | in_force | 1988 | 1988 |  | WTO, Trade Policy Review of SACU, WT/TPR/S/324 (2015), Annex 1 (Botswana) |
| `CHFO` | 443 | Agreement between the Government of Switzerland and the Government of Denmark and the Home Government of the Faroe Islands on Free Trade between Switzerland and the Faroe Islands | in_force | 1994-01-12 | 1995-03-01 |  | Swiss State Secretariat for Economic Affairs (SECO), SR 0.632.313.141 |
| `DZJO` | 18 | Jordan - Algeria Agreement | in_force | 1997 | 1999 |  | Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights |
| `EGRS` | 1130 | Free Trade Agreement between the Government of the Republic of Serbia and the Government of the Arab Republic of Egypt | in_force | 2024-07-13 | 2025-09-01 |  | Serbian Ministry of Foreign Affairs, Embassy in Cairo |
| `FRMC` | 452 | Customs Convention between the Government of the Principality of Monaco and the Government of the French Republic | in_force | 1963-05-18 | 1963-09-01 |  | Legimonaco, Convention douanière du 18 mai 1963 |
| `JOKW` | 524 | Jordan - Kuwait Agreement | in_force |  | 2005 |  | Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights |
| `JOSD` | 535 | Jordan - Sudan Agreement | in_force |  | 2003 |  | Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights |
| `LBTR` | 1101 | Agreement Establishing an Association Establishing a Free Trade Area between the Republic of Türkiye and the Lebanese Republic | signed | 2010-11-24 |  |  | Turkish Ministry of Trade, FTAs in ratification |
| `LVUA` | 571 | Free Trade Agreement between the Republic of Latvia and Ukraine | terminated | 1995-11-22 | 1997-01-15 | 2004-05-01 | Latvian official legal portal (likumi.lv) |
| `MWMZ` | 595 | Preferential Trade Agreement between the Government of the Republic of Malawi and the Government of the Republic of Mozambique | in_force | 2005-12-28 | 2006-09-20 |  | WTO, Trade Policy Review of Malawi, report by the Government, WT/TPR/G/460 (2024) |
| `MWZA` | 762 | Trade Agreement between Malawi and South Africa | in_force |  | 1990 |  | WTO, Trade Policy Review of Malawi, report by the Government, WT/TPR/G/460 (2024) |
| `MZZW` | 629 | Trade Agreement between the Government of the Republic of Mozambique and the Government of the Republic of Zimbabwe | in_force | 2004-01-09 | 2004-03-01 |  | Zimbabwe Revenue Authority (ZIMRA), origin and preference |

## Held

Treaties checked against an official source and not added, because the status rules need a date the source does not give:

| DESTA | Name | Year | Reason |
|---|---|---|---|
| 40 | Argentina Ecuador | 1984 | ALADI: replaced by ACE 21 when its First Additional Protocol took effect, and ALADI gives no date for that |
| 41 | Argentina Ecuador | 1993 | ALADI gives no date of entry into force (ACE 21) |
| 50 | Armenia Belarus | 2000 | Belarus MFA lists a bilateral FTA in force with Armenia but gives no dates |
| 105 | Belarus Kyrgyzstan | 1999 | Belarus MFA lists a bilateral FTA in force with Kyrgyzstan but gives no dates |
| 106 | Belarus Moldova | 1993 | Belarus MFA lists a bilateral FTA in force with Moldova but gives no dates |
| 112 | Belarus Serbia | 2009 | Belarus MFA lists a bilateral FTA with Serbia (replaced by the EAEU - Serbia FTA, in force 10 July 2021) but gives no dates |
| 120 | Bolivia Cuba | 1995 | ALADI gives no date of entry into force (AAP.A25TM 34) |
| 138 | Brazil Cuba | 1989 | ALADI gives no date of entry into force (AAP.A25TM 21) |
| 235 | Colombia El Salvador | 1984 | ALADI: historical, with no end date; the 2007 Colombia - Northern Triangle FTA ended AAP.A25TM 5 with Guatemala, and ALADI gives no date for El Salvador (AAP.A25TM 8) |
| 237 | Colombia Honduras | 1984 | ALADI: as for El Salvador (AAP.A25TM 9) |
| 264 | Cuba Ecuador | 1995 | ALADI gives no date of entry into force (AAP.A25TM 32) |
| 271 | Cuba Peru | 1987 | ALADI: replaced by AAP.A25TM 30, whose entry into force ALADI does not give, so no end date |
| 272 | Cuba Peru | 1994 | ALADI gives no date of entry into force (AAP.A25TM 30) |
| 274 | Cuba Uruguay | 1987 | ALADI gives no date of entry into force (AAP.A25TM 17) |
| 276 | Cuba Venezuela | 1995 | ALADI gives no date of entry into force (AAP.A25TM 35) |
| 290 | Czechoslovakia Finland | 1974 | a party (Czechoslovakia) has no country record; DESTA codes it as the Czech Republic |
| 373 | Ecuador Paraguay | 1994 | ALADI gives no date of entry into force (ACE 30) |
| 374 | Ecuador Uruguay | 1994 | ALADI gives no date of entry into force (ACE 28) |
| 446 | Finland German Democratic Republic | 1975 | a party (the German Democratic Republic) has no country record; DESTA codes it as Germany |
| 451 | Finland USSR | 1960 | a party (the USSR) has no country record |
| 477 | Honduras Mexico | 1985 | ALADI gives no date of entry into force (AAP.A25TM 11) |
| 583 | Lithuania Ukraine | 1995 | Ukraine's legal database (zakon.rada.gov.ua) dates the agreement 4 August 1993, not 1995; the site refused the browser, so no entry into force was read |
| 596 | Malawi South Africa | 1967 | the 1967 Malawi - South Africa agreement, which the 1990 revision (MWZA) replaced (Malawi Trade Portal); no date of entry into force or end |
| 613 | Mexico Panama | 1985 | ALADI: historical, with no end date or successor (AAP.A25TM 14) |
| 702 | Azerbaijan Belarus | 2004 | Belarus MFA lists a bilateral FTA in force with Azerbaijan but gives no dates |
| 705 | Belarus Kazakhstan | 1997 | Belarus MFA lists a bilateral FTA in force with Kazakhstan but gives no dates |
| 763 | Malawi Zimbabwe | 1995 | WTO and Malawi date the Malawi - Zimbabwe agreement differently (adopted 1986 and modified 1995, WT/TPR/S/96; signed 1995, Malawi Trade Portal), and Zimbabwe implements it by Statutory Instrument 103 of 2005; in force, but no date of entry into force |
| 764 | Malawi Zimbabwe | 2006 | the 2006 revision DESTA lists: Malawi's 2002 review says the agreement was being renegotiated, and Zimbabwe's instrument is of 2005; no official date of signature or entry into force |
| 767 | Mexico Peru | 1987 | ALADI: historical, with no end date or successor (ACE 8) |
| 791 | Estonia Poland | 1998 | Riigi Teataja: signed 5 November 1998, applied provisionally from 1 January 1999, ended 1 May 2004; no date of definitive entry into force found |

The other missing treaties were not looked up in this walk. Sources found for some of them: the Belarus MFA list of free trade partners, Jordan's export portal (Jordan's other Arab bilaterals are not on it), the Turkish Ministry of Trade, and Riigi Teataja and likumi.lv for the Baltic agreements. The southern African bilaterals were looked up in WTO trade policy reviews (Malawi 2002, 2010, 2016 and 2024; Mozambique 2009 and 2017; Zimbabwe 2011; SACU 2009 and 2015), the Zimbabwe Revenue Authority and the Malawi Trade Portal: four were added and three held.

## Party-history gaps

DESTA accession and withdrawal rows were compared with the party rosters of the matched records (parties, or the `includes` of a linked or party intblock). No party date was written from DESTA. Gaps:

| DESTA | Row | Year | Record | Country | Gap |
|---|---|---|---|---|---|
| 3+1 | African Economic Community South Africa accession | 1997 | `AEC` | ZA | not a party |
| 22_1 | Andean Community Brazil withdrawal Venezuela | 2006 | `BRCAN-ACE39` | VE | not a party |
| 29+1 | Arab Common Market Libya accession | 1975 | `ARABCOMMONMARKET` | LY | party without a date |
| 123+1 | Bolivia MERCOSUR Venezuela accession | 2006 | `MERCOSURBO` | VE | not a party |
| 192_1 | Central European Free Trade Agreement (CEFTA) withdrawal Czech Republic Hungary Poland Slovakia Slovenia | 2004 | `CEFTA-1992` | CZ | party without left date |
| 192_1 | Central European Free Trade Agreement (CEFTA) withdrawal Czech Republic Hungary Poland Slovakia Slovenia | 2004 | `CEFTA-1992` | HU | party without left date |
| 192_1 | Central European Free Trade Agreement (CEFTA) withdrawal Czech Republic Hungary Poland Slovakia Slovenia | 2004 | `CEFTA-1992` | PL | party without left date |
| 192_1 | Central European Free Trade Agreement (CEFTA) withdrawal Czech Republic Hungary Poland Slovakia Slovenia | 2004 | `CEFTA-1992` | SK | party without left date |
| 192+5 | Central European Free Trade Agreement (CEFTA) Macedonia accession | 2006 | `CEFTA-1992` | MK | not a party |
| 209+1 | Chile MERCOSUR Venezuela accession | 2006 | `MERCOSURCL` | VE | not a party |
| 243_1 | Common Market for Eastern and Southern Africa (COMESA) withdrawal Lesotho Mozambique | 1997 | `COMESA` | LS | not a party |
| 243_1 | Common Market for Eastern and Southern Africa (COMESA) withdrawal Lesotho Mozambique | 1997 | `COMESA` | MZ | not a party |
| 243_2 | Common Market for Eastern and Southern Africa (COMESA) withdrawal Namibia | 2000 | `COMESA` | NA | not a party |
| 243_3 | Common Market for Eastern and Southern Africa (COMESA) withdrawal Tanzania | 2004 | `COMESA` | TZ | not a party |
| 243_4 | Common Market for Eastern and Southern Africa (COMESA) withdrawal Angola | 2007 | `COMESA` | AO | not a party |
| 244_1 | Commonwealth of Independent States (CIS) withdrawal Georgia | 2009 | `CISFTA-1994` | GE | party without left date |
| 267+1 | Cuba MERCOSUR Venezuela accession | 2006 | `MERCOSURCU` | VE | not a party |
| 360+1 | Economic and Monetary Community of Central Africa (CEMAC) Sao Tome and Principe accession | 2004 | `CEMAC` | ST | not a party |
| 360+2 | Economic and Monetary Community of Central Africa (CEMAC) DR Congo accession | 2005 | `CEMAC` | CD | not a party |
| 363+1 | Economic Community of Central African States (ECCAS-CEEAC) Angola accession | 1999 | `ECCAS` | AO | not a party |
| 375+1 | EFTA Iceland accession | 1969 | `EFTA` | IS | party without a date |
| 375_1 | EFTA withdrawal Denmark UK | 1973 | `EFTA` | DK | not a party |
| 375_1 | EFTA withdrawal Denmark UK | 1973 | `EFTA` | GB | not a party |
| 375+2 | EFTA Finland accession | 1985 | `EFTA` | FI | not a party |
| 375_2 | EFTA withdrawal Portugal | 1986 | `EFTA` | PT | not a party |
| 375+3 | EFTA Liechtenstein accession | 1991 | `EFTA` | LI | party without a date |
| 375_3 | EFTA withdrawal Austria Finland Sweden | 1995 | `EFTA` | AT | not a party |
| 375_3 | EFTA withdrawal Austria Finland Sweden | 1995 | `EFTA` | FI | not a party |
| 375_3 | EFTA withdrawal Austria Finland Sweden | 1995 | `EFTA` | SE | not a party |
| 422+1 | Equatorial Customs Union Cameroon accession | 1961 | `UDECAMEROON` | CM | party without a date |
| 435+1 | Eurasian Economic Community (Union of the Five) Kyrgyzstan accession | 1996 | `EURASEC` | KG | party without a date |
| 435+2 | Eurasian Economic Community (Union of the Five) Tajikistan accession | 1998 | `EURASEC` | TJ | party without a date |
| 464_1 | Group of Three withdrawal Venezuela | 2006 | `COMX` | VE | not a party |
| 490+1 | India MERCOSUR Venezuela accession | 2006 | `INDIAMERCOSURPTA` | VE | not a party |
| 561+1 | Latin American Free Trade Area (LAFTA) Colombia Ecuador accession | 1961 | `LAFTA` | CO | not a party |
| 561+1 | Latin American Free Trade Area (LAFTA) Colombia Ecuador accession | 1961 | `LAFTA` | EC | not a party |
| 561+2 | Latin American Free Trade Area (LAFTA) Venezuela accession | 1966 | `LAFTA` | VE | not a party |
| 561+3 | Latin American Free Trade Area (LAFTA) Bolivia accession | 1967 | `LAFTA` | BO | not a party |
| 562+1 | Latin American Integration Association (ALADI LAIA) Cuba accession | 1998 | `ALADI` | CU | party without a date |
| 562+2 | Latin American Integration Association (ALADI LAIA) Panama accession | 2009 | `ALADI` | PA | party without a date |
| 604_1 | MERCOSUR withdrawal Venezuela | 2017 | `MERCOSUR` | VE | party without left date |
| 606+1 | MERCOSUR Peru Venezuela accession | 2006 | `MERCOSURPE` | VE | not a party |
| 931+1 | Central America Korea Guatemala accession | 2024 | `KRCENTRALAMERICA` | GT | not a party |
| 988+1 | African Continental Free Trade Area (AfCFTA) Burundi Lesotho Namibia Sierra Leone South Africa accession | 2018 | `AfCFTA` | BI | party without a date |
| 988+1 | African Continental Free Trade Area (AfCFTA) Burundi Lesotho Namibia Sierra Leone South Africa accession | 2018 | `AfCFTA` | LS | party without a date |
| 988+1 | African Continental Free Trade Area (AfCFTA) Burundi Lesotho Namibia Sierra Leone South Africa accession | 2018 | `AfCFTA` | NA | party without a date |
| 988+1 | African Continental Free Trade Area (AfCFTA) Burundi Lesotho Namibia Sierra Leone South Africa accession | 2018 | `AfCFTA` | SL | party without a date |
| 988+1 | African Continental Free Trade Area (AfCFTA) Burundi Lesotho Namibia Sierra Leone South Africa accession | 2018 | `AfCFTA` | ZA | party without a date |
| 988+2 | African Continental Free Trade Area (AfCFTA) Botswana Guinea-Bissau Zambia accession | 2019 | `AfCFTA` | BW | party without a date |
| 988+2 | African Continental Free Trade Area (AfCFTA) Botswana Guinea-Bissau Zambia accession | 2019 | `AfCFTA` | GW | party without a date |
| 988+2 | African Continental Free Trade Area (AfCFTA) Botswana Guinea-Bissau Zambia accession | 2019 | `AfCFTA` | ZM | party without a date |
| 988+3 | African Continental Free Trade Area (AfCFTA) Benin Nigeria accession | 2019 | `AfCFTA` | BJ | party without a date |
| 988+3 | African Continental Free Trade Area (AfCFTA) Benin Nigeria accession | 2019 | `AfCFTA` | NG | party without a date |

Not listed row by row: 34 withdrawals of the United Kingdom from EU agreements in 2020. The EU party's roster (the `EU` intblock) has no former members, so the UK appears in no EU agreement; the UK continuity agreements are their own records. 63 accession or withdrawal rows belong to base treaties without a match.

Readings that need care: DESTA codes Venezuela's 2006 accession to MERCOSUR as accession to MERCOSUR's agreements with Bolivia, Chile, Cuba, India and Peru, which no official source checked here confirms; Venezuela was suspended from MERCOSUR in 2016 and 2017, not withdrawn; Georgia left the CIS in 2009 but still applies the 1994 CIS free trade agreement with Belarus by an exchange of notes (Belarus MFA); and DESTA lists São Tomé and Príncipe and the DR Congo as CEMAC members, which they are not.

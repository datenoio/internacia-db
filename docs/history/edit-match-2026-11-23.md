# EDIT match report (2026-11-23)

A snapshot of how the trade agreements registry covers EDIT, the Electronic Database of Investment Treaties, written by the EDIT walk (`scripts/oneoff/fetch_edit.py`, `scripts/oneoff/import_edit.py`, `scripts/oneoff/write_edit_report.py`). It describes the registry on `main` on 2026-11-23 (after datenoio/internacia-db#241) and the records this walk adds. Do not treat its gap lists as current.

Every EDIT document, with its group, record, method and confidence, is in [edit-match-2026-11-23.csv](edit-match-2026-11-23.csv). Its `edit_uuid` column is the input for the `edit_uuid` backfill proposed in OpenSpec `add-edit-catalogue-links`. Each date where EDIT and the record differ is in [edit-date-conflicts-2026-11-23.csv](edit-date-conflicts-2026-11-23.csv).

## Source

[EDIT](https://edit.wti.org/) is run by the World Trade Institute (University of Bern) with the University of Ottawa. It holds the full texts of investment treaties, with their parties, dates of signature, entry into force and termination, and the languages of the text. On 2026-11-23 it had 4,271 documents: 3,462 bilateral investment treaties (`BIT`), 664 other international investment agreements (`OIIA`: free trade and partnership agreements with investment provisions, framework agreements, treaties of friendship, commerce and navigation, plurilateral investment treaties) and 145 model treaties. EDIT gives no status and no UNCTAD id.

The search page loads its results from a public JSON API. The walk called the same endpoints, 2 s apart (10 requests):

- `POST /web-public-api/document/investment-treaty/full_search` (500 documents a page): uuid, name, type, ISO party codes, dates, and the start of the text, which is empty for the 195 documents that EDIT has no text for;
- `POST /web-public-api/document/report/csv`: the same list with the languages of the text and EDIT's document reference.

It saved metadata only and downloaded no texts. Each document page, `https://edit.wti.org/document/show/<uuid>`, shows the text, with PDF and plain-text downloads.

## Method

1. EDIT's party codes are ISO alpha-3 codes, bloc codes (`EU`, `EFTA`, `MERCOSUR`, `ASEAN`, `BLEU`, `GCC` and 30 others, mapped to intblock ids) and a few of EDIT's own (`RKS` for Kosovo, `SCG` and `YUG`). `YUG` before 27 April 1992 is the Socialist Federal Republic, whose treaties each successor state may apply; after that date it is the Federal Republic, read as Serbia. Four EDIT rows have party codes that contradict the treaty name and were corrected (BLEU–Thailand 1986, Saudi Arabia–Uruguay 2025, Saudi Arabia–United States TIFA, Chile–China 2012).
2. A treaty matches a record with the same parties. Parties compare as ids, as the member countries of each bloc on the date of signature (EDIT writes `EFTA` where the registry lists the EFTA states, and a record linked to an intblock stands for the intblock's members), and, on the same date of signature, as member sets that differ only by bloc members. A BIT matches only `investment` records; another agreement prefers records of other types.
3. Levels, best first: the same date of signature (or the founding date of a linked record's intblock); the same year (for an OIIA, at most 45 days apart or with the same entry into force); for a BIT, the only record of the pair when the dates differ by one part (a typing slip). Ties go to the record with the same entry into force, then the closer name (`interim`, `framework`, `investment`). A date that matches an `instruments` entry makes the treaty that instrument.
4. EDIT lists a treaty of Czechoslovakia, the USSR or Yugoslavia once, with its successor states; the registry, following UNCTAD, has one record per successor. Such a BIT matches each successor's record with the same date of signature.
5. 150 documents were decided by hand (`MANUAL` in `import_edit.py`): plurilateral agreements, agreements of a bloc with one record per member, status-lagging records without a date of signature, and candidates rejected as other agreements.

Confidence in the CSV: `high` (same parties and date, a successor-state record, or a hand match) 3,648 rows; `medium` (bloc members, overlapping rosters or the same year) 169; `low` (typing slip) 10.

## Results

| Group | Documents | BIT | OIIA | Model |
|---|---|---|---|---|
| matched | 3,797 | 3,396 | 401 | |
| added (new record) | 25 | 23 | 2 | |
| component (part of a recorded agreement) | 33 | 4 | 29 | |
| instrument | 4 | | 4 | |
| duplicate in EDIT | 2 | 1 | 1 | |
| held | 45 | 38 | 7 | |
| missing (out of scope or follow-up) | 193 | | 193 | |
| plurilateral, no record | 27 | | 27 | |
| model treaty | 145 | | | 145 |

The 3,797 matched documents map to 3,827 records: 21 treaties of Czechoslovakia, the USSR, Yugoslavia or Serbia and Montenegro map to 45 successor-state records, and the Chile–Central America and Mexico–Northern Triangle FTAs to 8 bilateral records.

### Links added

3,636 matched records gained a `treaty_text` link to the EDIT document page, after their existing links, like the GPTAD links of datenoio/internacia-db#209. Documents without a text in EDIT get no link. Four matched records are edited by sessions running at the same time (CIS/EAEU and AfCFTA walks) and were left for later: `AfCFTA`, `CISFTASERVICES`, `EAEU`, `EAEUVN`. To avoid conflicts, the UAE CEPA walk (branch `claude/uae-cepa-walk-460aec`) carries the EDIT links and notes of the 18 UAE CEPA records it rewrites (`AECL`, `AECO`, `AECR`, `AEEC`, `AEGE`, `AEID`, `AEIL`, `AEKE`, `AEKH`, `AEMU`, `AEMY`, `AENZ`, `AERS`, `AETR-CEPA`, `AEUA`, `AEVN`, `AUUAE`, `INUAE`): 17 links and 4 notes. The CSV marks these 21 links `deferred`. The registry stores the URL, not the text.

### Date conflicts

609 dates differ between EDIT and the record (CSV). A record keeps its dates and status. 458 records gained a note in the form "EDIT gives 2016-06-15 as the date of entry into force.", with an EDIT provenance entry for `notes`. Two of them (`CLID`, `USBH`) were written by hand because their YAML layout does not round-trip.

| Record's source | Signature | Entry into force | Termination | Status |
|---|---|---|---|---|
| UNCTAD IIA Navigator (`catalogue` with `unctad_iia_id`) | 97 | 142 + 20 empty | 84 + 46 empty | 22 |
| other catalogues (WTO RTA-IS, ARIC) | 13 + 8 empty | 31 + 2 empty | 6 + 1 empty | 6 |
| `official` | 12 + 46 empty | 33 + 35 empty | 1 + 2 empty | 2 |

"Empty" means the record has no such date. On a catalogue record a missing date usually means another status (UNCTAD's capture predates the entry into force), so it is noted. On an `official` record or a record linked to an intblock it is a gap, not a conflict, and is not noted.

Status differences, noted through the date (EDIT has the newer event in most of them):

- signed in the registry, in force in EDIT: `JPRS-BIT`, `JPTJ-BIT`, `JPPY-BIT`, `JPZM-BIT`, `AEVN`, `HKTR-BIT`, `AEKM-BIT`, `MKQA-BIT`, `BHSD-BIT-2006`, `FIRS-BIT`, `CDUA-BIT`, `CZDZ-BIT`, `SDTR-BIT`, `MYSD-BIT`, `TNYE-BIT`, `RSZW-BIT`, `QATN-BIT`, `MYTM-BIT`, `MYZW-BIT`;
- in force in the registry, terminated in EDIT: `PATW` (2017-06-12), `ILSI-BIT` (2007), `IDLK-BIT` (2017), `KRRO-BIT` (2008); signed in the registry, terminated in EDIT: `ITRS-BIT` (2019);
- under negotiation or proposed in the registry, signed in EDIT: `EFTAVN` (2026-10-18), `GCCGB` (2026-05-20), `AEEC`, `BDJP`, `CRIL`; in force in EDIT: `INOM` (2026-06-01).

These are worth checking against official sources; the walk changed no status.

## Added in this walk

25 records. The 22 BITs that only EDIT lists are `verification: catalogue` and cite EDIT for every field, the rule of the UNCTAD walk (the `catalogue` description now names EDIT). A BIT was added only when EDIT gives its entry into force: EDIT has no status, and a missing date does not show that a treaty is not in force. The three EU agreements cite the European Commission or EUR-Lex.

| Record | Name | Status | Signed | In force | Ended | Source |
|---|---|---|---|---|---|---|
| `EUSG-BIT` | EU-Singapore Investment Protection Agreement | signed | 2018-10-19 | | | European Commission, DG Trade |
| `EUVN-BIT` | EU-Viet Nam Investment Protection Agreement | signed | 2019-06-30 | | | European Commission, DG Trade |
| `EUAO-BIT` | EU-Angola Sustainable Investment Facilitation Agreement | in_force | 2023-11-17 | 2024-09-01 | | EUR-Lex, CELEX 22024A00830 |
| `AEJE-BIT` | Jersey - United Arab Emirates BIT (2021) | in_force | 2021-11-09 | 2023-03-13 | | EDIT |
| `ALXK-BIT` | Albania - Kosovo BIT (2004) | in_force | 2004-02-19 | 2005-02-07 | | EDIT |
| `ARTW-BIT` | Argentina - Taiwan Province of China BIT (1993) | in_force | 1993-11-30 | 1993-11-30 | | EDIT |
| `ATRO-BIT-1976` | Austria - Romania BIT (1976) | terminated | 1976-09-30 | 1977-11-08 | 1997-07-01 | EDIT |
| `ATXK-BIT` | Austria - Kosovo BIT (2010) | in_force | 2010-01-22 | 2012-02-01 | | EDIT |
| `AUHK-BIT-2019` | Australia - Hong Kong, China SAR BIT (2019) | in_force | 2019-03-26 | 2020-01-17 | | EDIT |
| `CATW-BIT` | Canada - Taiwan BIT (2023) | in_force | 2023-12-29 | 2023-12-29 | | EDIT |
| `CGQA-BIT` | Congo - Qatar BIT (2010) | in_force | 2010-03-28 | 2013-07-04 | | EDIT |
| `CHXK-BIT` | Kosovo - Switzerland BIT (2011) | in_force | 2011-10-27 | 2012-06-13 | | EDIT |
| `CIMA-BIT` | Côte d'Ivoire - Morocco BIT (2013) | in_force | 2013-03-19 | 2021-03-23 | | EDIT |
| `CNRO-BIT-1983` | China - Romania BIT (1983) | terminated | 1983-02-10 | 1983-12-27 | 1995-09-01 | EDIT |
| `EGIT-BIT-1975` | Egypt - Italy BIT (1975) | terminated | 1975-04-29 | 1981-07-30 | 1994-05-01 | EDIT |
| `IDTW-BIT` | Indonesia - Taiwan BIT (1990) | in_force | 1990-12-19 | 1990-12-19 | | EDIT |
| `INTW-BIT-2018` | India - Taiwan Province of China BIT (2018) | in_force | 2018-12-18 | 2019-02-14 | | EDIT |
| `MYTW-BIT` | Malaysia - Taiwan Province of China BIT (1993) | in_force | 1993-02-18 | 1993-03-18 | | EDIT |
| `PHTW-BIT` | Philippines - Taiwan Province of China BIT (1992) | in_force | 1992-02-28 | 1992-02-28 | | EDIT |
| `PYZA-BIT` | Paraguay - South Africa BIT (1974) | in_force | 1974-04-03 | 1974-08-16 | | EDIT |
| `QATJ-BIT-2011` | Qatar - Tajikistan BIT (2011) | in_force | 2011-08-25 | 2013-08-28 | | EDIT |
| `SATW-BIT` | Saudi Arabia - Taiwan Province of China BIT (2000) | in_force | 2000-10-31 | 2001-07-25 | | EDIT |
| `SGTW-BIT` | Singapore - Taiwan Province of China BIT (1990) | in_force | 1990-04-09 | 1990-04-09 | | EDIT |
| `THTW-BIT` | Taiwan Province of China - Thailand BIT (1996) | in_force | 1996-04-30 | 1996-04-30 | | EDIT |
| `TRXK-BIT` | Kosovo - Turkey BIT (2012) | in_force | 2012-05-30 | 2015-10-15 | | EDIT |

The terminated 1975, 1976 and 1983 treaties ended on the day their pair's later BIT (`EGIT-BIT`, `ATRO-BIT`, `CNRO-BIT`) entered into force; `AUHK-BIT-2019` replaced `AUHK-BIT`, which ended on its entry into force. Most of the rest are treaties of Taiwan and Kosovo, which the UNCTAD economy pages read by datenoio/internacia-db#227 do not list.

## Not added

**Components (33).** Separate instruments of an agreement that one record covers. An FTA with an investment chapter or an investment agreement stays one record, as `docs/intblock-inclusion-policy.md` says for the ASEAN+1 investment agreements:

- investment agreements under a framework or FTA: ASEAN with China, Korea, India and Hong Kong (`ACFTA`, `AKFTA`, `AIFTA`, `AHKFTA`), the CEPA investment agreements of Hong Kong and Macao (`CNHK`, `CNMO`), the cross-strait agreement (`CNTW`), Korea–Türkiye (`KRTR`), Chile–China (`CLCN`), the EFTA–Korea investment agreement (`EFTAKR`), the APTA framework on investment, the 2011 ANZCERTA investment protocol;
- upgrades and modernisations that are not yet `instruments`: AANZFTA 2023, NZ–Singapore 2019, Canada–Chile 2017, the EU–Mercosur interim agreement;
- community acts and protocols of a recorded bloc: ECOWAS (the 1975 treaty, five protocols and acts), MERCOSUR (Colonia, Buenos Aires and Montevideo protocols, the 2017 facilitation protocol), CACM (2002 treaty and 2007 protocol), the 1981 GCC Unified Economic Agreement, the 2001 Vaduz Convention of EFTA, the Revised Treaty of Chaguaramas, the 2001 EU–OCT decision, the AfCFTA Investment Protocol (not in force).

**Instruments (4).** Already `instruments` of a record: the China–Singapore upgrades of 2018 and 2023, and the 2015 services agreements of the Hong Kong and Macao CEPAs.

**Duplicates (2).** EDIT lists North Macedonia–Taiwan 1999 and the 1963 Ankara Agreement twice; the second uuid of each is in the CSV.

**Held (45).**

- 28 documents typed BIT without a date of entry into force in EDIT, among them the 1960s German treaties with the Philippines, Chile, Kenya, Colombia and Ghana, Kosovo's treaties of 2015 and 2016, Japan–Taiwan 2011, and four of 2025 and 2026 that UNCTAD's captures predate: Central African Republic–UAE, Bahrain–Switzerland, Bangladesh–Hong Kong and Korea–Turkmenistan. Two of them are the EU–Indonesia investment protection agreement and the EU–China Comprehensive Agreement on Investment.
- 3 BITs that may be the registry's treaty of the pair with other dates (Kuwait–Tunisia, Armenia–Viet Nam, Gambia–Taiwan), and 4 older treaties of a pair whose later treaty is recorded, where EDIT gives no termination (Denmark–Romania 1980, Romania–Tunisia 1987, Libya–Malta 1973, Belgium–Congo 1976).
- The 1974 France–Senegal establishment convention (not an investment treaty), the 1977 Italy–Romania BIT (EDIT dates its signature after its entry into force), the 1976 Netherlands–Yugoslavia BIT (no record for the former Yugoslavia).
- `UAIA`: the 1980 Unified Agreement for the Investment of Arab Capital. Task 3.3 of `add-investment-agreements` waits for a party government or the League of Arab States; EDIT gives 1981-09-07 as its entry into force.
- The Energy Charter Treaty (an intblock, `ECT`; no registry record planned), the 1987 ASEAN Investment Agreement (predecessor of `ACIA`), Lomé IV, the Cotonou Agreement and the Samoa Agreement (they need the ACP rosters from EUR-Lex), and the GCC–New Zealand FTA, which EDIT dates 31 October 2011 and the registry has under negotiation.

**Missing (193)**, all OIIAs, by kind:

- 37 treaties of friendship, commerce and navigation or of establishment: out of scope (`add-trade-relations-walk`);
- 57 trade and investment framework agreements and councils, mostly U.S. TIFAs: the registry type is `framework`, but they belong in a walk of the USTR list, not in this one;
- 73 cooperation, partnership and framework agreements (EU cooperation agreements and PCAs, economic and technical cooperation agreements, investment guarantee agreements): not trade agreements;
- 26 others: the UAE CEPAs with Korea, Jordan, Azerbaijan, the Philippines, Angola, Nigeria, the DR Congo (listed twice), Sierra Leone and Gabon; Korea–Serbia 2026; the services and investment agreements of Armenia and Kazakhstan with Singapore, of Belarus and Russia with the UAE, and of the Common Economic Space (2010); EU–SADC interim 2009, EU–Turkmenistan interim 1999, EC–Macao 1992; Argentina–Bolivia 2004, Brazil–Peru 2016, Costa Rica–Panama 1973, Brazil–Paraguay 1956, Rwanda–Switzerland 1963, DR Congo–UK 1970, Czech Republic–Pakistan 2023. They need an official source; the African UAE CEPAs and the EAEU-member agreements are left to the walks running in parallel.

27 of the missing documents had an automatic candidate that is another agreement (a U.S. TIFA against a proposed FTA, an EU cooperation agreement against a negotiated FTA, a 1950s FCN treaty against a later preferential agreement); the CSV marks them.

**Plurilateral, no record (27).** Constitutive treaties (TFEU, the SADC Treaty, the 1957 Arab Economic Unity agreement, the CEN-SAD revised treaty), the OECD Code of Liberalisation of Capital Movements, regional investment agreements not in force or without an intblock (COMESA CCIA 2007 and 2017, ECO, Arab Maghreb Union, CIS 1997, Eurasian 2008, SADC FIP, CEMAC and ECGLC codes, the 1970 Arab capital agreement), framework instruments (IPEF's three agreements, the Central Asia TIFA, AIFF, the WTO Investment Facilitation for Development, ACCTS) and EEC cooperation agreements.

**Model treaties (145)** map to nothing.

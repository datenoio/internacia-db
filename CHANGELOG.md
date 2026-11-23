# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.1.0] - 2026-11-23

### Added

- 51 trade agreements registered with ALADI, the depositary of the LAIA partial-scope agreements,
  that the registry lacked, as `verification: official` records with signatories, date of signature
  and entry into force (per party where it differs by pair) from the ALADI records: the Cuba
  agreements, MERCOSUR with Colombia (ACE 72), Panama (ACE 76), Cuba and Mexico, Chile–Uruguay (ACE 73),
  Chile–Ecuador (ACE 75), the Venezuela agreements of its MERCOSUR accession, ECOALBA-TCP, the agreements
  inside MERCOSUR, 19 Article 25 agreements with Central American and Caribbean countries,
  MERCOSUR–Central American Common Market, two agricultural agreements, the regional tariff
  preference and the market-opening lists for Bolivia, Ecuador and Paraguay. Added by
  `scripts/oneoff/import_aladi.py` from pages saved by `scripts/oneoff/fetch_aladi.py` on 2026-11-23.
  35 are new records; the other 16 were added from OAS SICE the same day and now merge both sources
  under the SICE ids (`ARCL-1991`, `ARUY-AUTO`, `BRGYKN`, `MERCOSURMX-AUTO` and 12 with the same id),
  with ALADI dates, status and parties and a note where SICE differs.
- 71 terminated ALADI partial-scope agreements whose successor the ALADI Secretariat names, as
  `verification: official` records with signatories, date of signature, entry into force and end
  date from the ALADI historical records: 62 `superseded` (`superseded_by` the agreement that
  replaced them: the 1983 renegotiation agreements, the bilateral economic complementation
  agreements that MERCOSUR's agreements with Chile, Bolivia, Peru, the Andean Community and Cuba
  replaced, and the Article 25 agreements that Mexico's and Colombia's FTAs replaced) and 9
  `terminated` (eight 1982 sectoral commercial agreements that ended pair by pair, and ACE 26).
  15 successors already in the registry get `supersedes` (among them `CLEC` and `COCU`, current ALADI
  agreements). `ARCAN-ACE48` gives each party the date its pair was replaced (`left`). Added by
  `scripts/oneoff/import_aladi.py`.
- 19 more terminated ALADI partial-scope agreements, from a second pass over the 47 that the
  historical ALADI import left out, with the missing date taken from the validity clause of the
  text, the ALADI Secretariat's note, the protocols or the successor's text:
  3 `superseded` (`MXPE-ACE8` and `MXPE-AAPR32`, replaced by the Mexico–Peru agreement;
  `MXPA-A25TM14`, ended by Article 20.7 of the Mexico–Panama FTA), 15 `terminated` (eleven
  sectoral commercial agreements of 1981–1984, `BOUY-AAPR22`, `BRPY-AAPR34`, `BRUY-AAPR35` and
  `COMXVE-ACE61`) and 1 `abandoned` (`ALADI-PREC5`, never in force). `MXPE` and `MXPA` get
  `supersedes`. Added by `scripts/oneoff/import_aladi.py`, which now lists the 28 agreements
  still left out with the reason.
- Eleven `trade_agreements` records from the Global Affairs Canada agreements table, checked on 2026-11-23 (`verification: official`):
  - `CAEC` (Canada-Ecuador FTA, signed 2026-07-24) and `AECA` (Canada-UAE CEPA, signed 2026-10-27).
  - `CADO` (Dominican Republic), `CATR` (Türkiye) and `MERCOSURCA` (Mercosur), all `negotiating`.
  - `PACALLCA` (Pacific Alliance), `CARICOMCA` (CARICOM), `CAGTNISV` (Guatemala, Nicaragua and El Salvador), `CAMA` (Morocco) and `CAGB-FTA` (the comprehensive Canada-UK FTA), all `abandoned`, which Global Affairs Canada lists as "8. Inactive".
  - `TISA` (Trade in Services Agreement, 23 parties with the EU as one), `services`, `abandoned`.
- 29 `trade_agreements` records (`agreement_type: framework`, `status: signed`,
  `verification: official`) for China's framework agreements on economic partnership for
  shared development with African countries, checked on 2026-11-23 against official sources:
  - 19 of the 22 agreed and signed at the FOCAC Beijing Summit in September 2024: Burundi,
    the Central African Republic, Chad, Comoros, Côte d'Ivoire, the Democratic Republic of
    the Congo, Djibouti, Equatorial Guinea, Ethiopia, Guinea-Bissau, Liberia, Libya,
    Madagascar, Mauritania, Sao Tome and Principe, Sierra Leone, South Sudan, Uganda and
    Zimbabwe;
  - the seven reported on 1 July 2025: Angola, Benin, the Gambia, Ghana, Senegal, Somalia and
    Zambia (June 2025);
  - three with no MOFCOM release: Cameroon (`CMCN`, 10 December 2025, from the state daily
    Cameroon Tribune), Botswana (`BWCN`, April 2026) and Togo (`CNTG`, 23 April 2026), both
    from the bilateral relations pages of the Chinese Ministry of Foreign Affairs.
- `scripts/oneoff/import_china_africa_frameworks.py`, the import that wrote them.
- Two `preference_scheme` registry records for China's unilateral zero-tariff measures,
  checked on 2026-11-23 against announcements of the Customs Tariff Commission of the State
  Council (`verification: official`). China is the grantor of both.
  - `CN-LDC`: the duty-free treatment for LDCs (WTO PTA Database id 79), in force from
    2010-07-01 and covering 100% of tariff lines from 2024-12-01. Its 43 beneficiaries are the
    UN LDCs with which China has diplomatic relations. The PTA Database lists none for this
    scheme, so it was left out of the PTA Database import.
  - `CN-AFRICA`: zero tariffs from 2026-05-01 to 2028-04-30 for the 20 African countries with
    diplomatic relations that are not LDCs, taken from the country list annexed to
    announcement No. 5 of 2026.
- 30 trade agreement records for agreements that the DESTA (Design of Trade Agreements) v2.3
  list of treaties has and the registry lacked, checked on 2026-11-23
  (`scripts/oneoff/match_desta.py`, `scripts/oneoff/import_desta.py`). Status and dates come
  from ALADI, a party government or the WTO, never from DESTA: four historical ALADI
  agreements of 1982 to 1985 that ended on a fixed date, the UAE CEPAs with Israel, Serbia,
  Mauritius, Kenya and the Central African Republic, Egypt - Serbia, Lebanon - Türkiye,
  Jordan's agreements with Kuwait, Sudan and Algeria, Switzerland - Faroe Islands, the
  France - Monaco customs convention, Latvia - Ukraine, four southern African bilaterals from
  WTO trade policy reviews (Malawi - Mozambique, Mozambique - Zimbabwe, Botswana - Zimbabwe,
  Malawi - South Africa) and nine Arab bilaterals from the WTO reviews of Egypt, Morocco and
  Tunisia (`EGSY`, `EGLY`, `EGLB`, `EGIQ`, `EGMA`, `EGTN`, `SYTN`, `LYTN`, `MATN`).
- A DESTA match report: `docs/history/desta-match-2026-11-23.md` and a per-treaty CSV with the
  matched, ambiguous and missing groups, the held agreements and the party-history gaps that
  DESTA's accession and withdrawal rows suggest.
- `trade_agreements.dta_id`: the agreement id (`WB ID`) in the World Bank Deep Trade Agreements
  (DTA) database, the key of the DTA content files. Set on the registry records that DTA lists,
  mapped by `scripts/oneoff/import_dta.py` from the version 2 files of 2024-01-23 (OpenSpec
  change `add-dta-catalogue-links`). The registry does not ship the DTA content data.
- `CNTW`, the Cross-Straits Economic Cooperation Framework Agreement (ECFA), as a `pta`
  registry record (`verification: official`, checked on 2026-11-23). It was signed on
  2010-06-29 by ARATS and SEF and is in force from 2010-09-12, according to the text in
  Taiwan's Laws & Regulations Database and the MOFCOM ECFA page. Its notes record:
  - the early harvest from 2011-01-01;
  - the Investment Protection and Promotion Agreement, in force from 2013-02-01;
  - the Agreement on Trade in Services of 2013, not in force;
  - the Customs Tariff Commission's suspension of ECFA rates for 12 tariff lines from
    2024-01-01 and for 134 more from 2024-06-15.

  WTO RTA-IS lists it as an early announcement (RTA ID 713), which the WTO walk had skipped.
- `treaty_text` links to EDIT, the Electronic Database of Investment Treaties of the World Trade
  Institute, on 3,636 trade agreement records: 3,276 investment treaties and 360 FTAs, PTAs,
  customs unions and other agreements with investment provisions. The registry stores the
  document URL, not the text (OpenSpec `add-edit-catalogue-links`; report
  `docs/history/edit-match-2026-11-23.md`).
- 25 investment treaties that EDIT lists and the registry lacked: the EU investment protection
  agreements with Singapore and Viet Nam and the EU–Angola Sustainable Investment Facilitation
  Agreement (`official`), and 22 BITs that only EDIT lists, mostly of Taiwan and Kosovo
  (`catalogue`).
- Seven EFTA Joint Declarations on Cooperation with partners that have no other EFTA
  agreement, as `framework` records: `EFTADZ-JDC` (Algeria, 2002), `EFTAMN-JDC` (Mongolia,
  2007), `EFTAMU-JDC` (Mauritius, 2009), `EFTAPK-JDC` (Pakistan, 2012), `EFTAMM-JDC`
  (Myanmar, 2013), `EFTANG-JDC` (Nigeria, 2017) and `EFTAASEAN-JDC` (2024, signed by the ten
  ASEAN Member States and the four EFTA States). Name, date and parties come from each text.
- 21 EFTA joint declarations that preceded a free trade agreement, also as `framework` records
  with name, date, place and parties from each text: `EFTAAL-JDC` (1992, signed by the seven
  EFTA States of the time), `EFTAEG-JDC`, `EFTAMA-JDC` and `EFTATN-JDC` (1995), `EFTAMK-JDC`
  and `EFTAPS-JDC` (1996), `EFTAJO-JDC` and `EFTALB-JDC` (1997), `EFTAGCC-JDC`, `EFTAUA-JDC`,
  `EFTAMERCOSUR-JDC` and `EFTAYU-JDC` (2000; Yugoslavia's declaration lists Serbia and
  Montenegro), `EFTAPE-JDC` and `EFTACO-JDC` (2006), `EFTAMY-JDC` and `EFTAPA-JDC` (2010),
  `EFTAGE-JDC` (2012), `EFTAPH-JDC` (2014; `signed`, because it takes effect on a notification
  whose date is not published), `EFTAEC-JDC` (2015), `EFTAMD-JDC` (2017) and `EFTAXK-JDC`
  (2018).
- `EFTAUA-2025`, the modernised EFTA-Ukraine Free Trade Agreement (signed 2025-04-08). On
  entry into force it replaces `EFTAUA` for each EFTA State.
- `EFTACL-2024`, the Protocol Amending the EFTA-Chile Free Trade Agreement (signed
  2024-06-24).
- `EFTADZ`, the EFTA-Algeria free trade negotiations (four rounds in 2007–2008, on hold).
- Three EU negotiations that the European Commission lists as on hold, as `suspended` records
  checked on 2026-11-23: `EUCENTRALAFRICAEPA-REGIONAL` (regional EPA talks with Central Africa,
  started in 2003 and paused in 2011, for the seven countries that have not signed an EPA),
  `EUESAEPA-REGIONAL` (regional EPA talks with Eastern and Southern Africa, started in 2004 and
  paused in 2011, for Djibouti, Ethiopia, Malawi, Somalia, Sudan and Zambia) and `EUMM-BIT`
  (EU-Myanmar Investment Protection Agreement, launched in 2014 and on hold since 2017).
- Records for the Interim Agreements that applied the trade provisions of the Stabilisation
  and Association Agreements and of the EU-Lebanon Association Agreement until those entered
  into force: `EUAL-2006`, `EUMK-2001`, `EUME-2007`, `EUBA-2008`, `EURS-2008` and `EULB-2002`
  (`superseded`). Also the Europe Agreements with Estonia, Latvia and Lithuania
  (`EUEE-1995`, `EULV-1995`, `EULT-1995`, in force 1998-02-01 to 2004-05-01). Checked against
  Official Journal notices and EUR-Lex metadata on 2026-11-23.
- Ten EU trade agreements from the European Commission's negotiations and agreements
  overview (DG Trade, checked on 2026-11-23), all `verification: official`:
  - `EUXK`: EU-Kosovo Stabilisation and Association Agreement, in force since 2016-04-01.
  - `EUSG-DTA`: EU-Singapore Digital Trade Agreement, in force since 2026-02-01.
  - `EUCA-DTA`: EU-Canada Digital Trade Agreement, concluded on 2026-10-30 and not yet
    signed (`negotiating`).
  - `EUMX-MGA` and `EUMX-ITA`: the EU-Mexico Modernised Global Agreement and Interim
    Trade Agreement, both signed on 2026-05-22.
  - `EUCL-AFA`: EU-Chile Advanced Framework Agreement, signed on 2023-12-13.
  - `EUAE`: EU-United Arab Emirates FTA, under negotiation since 2025-05-28.
  - `EUGCC`: EU-GCC FTA, launched in 1990 and suspended since 2008. It keeps the
    `negotiating` status, and a note records the suspension.
  - `EUEACEPA`: the regional EU-EAC Economic Partnership Agreement. Kenya and Rwanda
    signed it in September 2016, and it has never been applied.
  - `EUADSM`: the EU-Andorra-San Marino Association Agreement, signed on 2026-10-19.
- Intblocks `EUEACEPA` (`pta`) and `EUADSM` (`fta`), the rosters of those two 3-party
  agreements. The registry records now link to them.
  - `EUEACEPA`: the EU, Kenya and Rwanda are `member`; Burundi, Tanzania and Uganda,
    which have not signed, are `partner`.
  - `EUADSM`: the EU, Andorra and San Marino are `founding_member`, joined 2026-10-19.
  - Neither agreement has a Wikidata item, so both are listed in
    `data/schemas/wikidata_exclusions.yaml`.
- `trade_agreements.gptad_id`: the agreement id in the World Bank Global Preferential Trade
  Agreements Database (GPTAD), on the registry records that GPTAD lists, mapped by
  `scripts/oneoff/import_gptad.py` from pages saved by `scripts/oneoff/fetch_gptad.py` on
  2026-11-23 (OpenSpec change `add-gptad-catalogue-links`).
- 31 trade agreements that GPTAD lists and the registry lacked: Arab bilaterals not notified to the WTO
  (Jordan with Bahrain, Egypt, Israel, Morocco, Syria, Tunisia and the UAE; Egypt–Palestine), the
  Iran–Pakistan PTA, ALADI complementation agreements (MERCOSUR–Bolivia, MERCOSUR–Chile, Bolivia–Chile,
  Chile–Venezuela, Andean Community–Brazil), CARICOM agreements with Colombia, Costa Rica, Cuba, the
  Dominican Republic and Venezuela, the ASEAN–China, ASEAN–India, ASEAN–Korea and BIMST-EC framework
  agreements, predecessors of `AUPG`, `CLCO`, `CLPE` and `PASV` (which get `supersedes`), Croatia–Lithuania,
  and the founding treaties of `AEC`, `ECCAS` and `MRU` as linked records. Status and dates come from ALADI,
  SICE, the ASEAN Secretariat and party governments, not from GPTAD alone.
- The successors that GPTAD does not list: the 1998 Jordan–Morocco FTA (`JOMA`), and ALADI complementation
  agreements No. 58 MERCOSUR–Peru (`MERCOSURPE`) and No. 59 MERCOSUR–Colombia, Ecuador, Venezuela
  (`MERCOSURCOECVE`), with pair-by-pair entry into force from ALADI.
- `treaty_text` link type in `trade_agreements.links`: a URL of the full text of the
  agreement. Mapped records link the GPTAD PDF. The registry stores the URL, not the text.
- 14 intelligence, counter-terrorism-information and intelligence-fusion bodies, each with the
  roster from its own site or parent organization, checked on 2026-11-23: the Committee of
  Intelligence and Security Services of Africa (`CISSA`, 53 member services), the CIS
  Anti-Terrorism Center (`CISATC`), the SCO Regional Anti-Terrorist Structure (`SCORATS`), the
  Intelligence College in Europe (`ICE`), the European Centre of Excellence for Countering Hybrid
  Threats (`HYBRIDCOE`, with the United States as a former member since February 2026), the Five
  Eyes Intelligence Oversight and Review Council (`FIORC`), the Five Country Ministerial (`FCM`),
  the Maritime Analysis and Operations Centre – Narcotics (`MAOCN`), the Terrorist Financing
  Targeting Center (`TFTC`), the AU Nouakchott Process (`NOUAKCHOTTPROCESS`), the UNODC Paris
  Pact Initiative (`PARISPACT`) and Triangular Initiative (`TRIANGULARINITIATIVE`), and the two
  MASE regional centres in the Western Indian Ocean (`RMIFC`, `RCOC`).
- `trade_agreements` accepts `agreement_type: investment` for standalone investment treaties, such as bilateral investment treaties and Canada's FIPAs. Investment records have ids ending in `-BIT`, or `-BIT-YYYY` for a further treaty between the same parties. The new validator rule `TRADE_AGREEMENT_ID_SUFFIX` checks the suffix (OpenSpec `add-investment-agreements`).
- 65 Canadian investment treaty records (`AMCA-BIT`, `CACN-BIT`, `CAUA-BIT` and others), all `verification: official`:
  - 59 rows of the Global Affairs Canada agreements table, with signature, entry into force and suspension dates from the Canada Treaty Series;
  - six Canada Treaty Series treaties that the table omits (El Salvador, South Africa, Uruguay 1991, Czechoslovakia 1990, Latvia 1995, Romania 1996).

  Imported with `scripts/oneoff/import_canada_fipas.py`, checked on 2026-11-23.
- `BLEU` intblock for the Belgium–Luxembourg Economic Union (convention of 25 July 1921, renewed by the Protocol of 18 December 2002, in force from 1 February 2005). Belgium and Luxembourg sign investment treaties as one party, so a Belgium–Luxembourg treaty lists `BLEU` as one party.
- Registry records linked to the plurilateral investment intblocks `OICIA`, `ACIA`, `CJKIA` and `PCFI` (`agreement_type: investment`) and `INTRAEUBIT` (`agreement_type: other`, because it terminates investment treaties), all `in_force` and `verification: official`. `UAIA` has no record yet: no party government or depositary source for its status could be read.
- Four HCCH conventions to which Japan is a Contracting Party and which had no record:
  `CIVILPROCEDURE1954` (Convention on Civil Procedure), `CHILDMAINTENANCE1956` (law applicable to
  maintenance obligations towards children), `TESTAMENTARY1961` (form of testamentary dispositions)
  and `MAINTENANCE1973` (law applicable to maintenance obligations), with Contracting Parties and
  ratification, accession or succession dates from the HCCH status tables, checked on 2026-11-23.
- The UN regional commissions `ESCAP` (Economic and Social Commission for Asia and the Pacific,
  Wikidata Q1142901) and `ECLAC` (Economic Commission for Latin America and the Caribbean, Wikidata
  Q32874), with members, associate members and admission dates from the commissions' member pages.
  The United States is a `former_member` of both from 7 January 2026, the date of the presidential
  memorandum directing its withdrawal.
- 19 `trade_agreements` records from the China FTA Network of China's Ministry of Commerce
  (MOFCOM), checked on 2026-11-23, all `verification: official`:
  - `CNHN` (China-Honduras FTA early harvest arrangement, in force from 1 September 2024),
    `CNSV` (China-El Salvador FTA, negotiating), `CNPS` (China-Palestine FTA, negotiating) and
    `CNUY` (China-Uruguay FTA, joint feasibility study completed in 2022);
  - eight China-Pacific Island country framework agreements on enhanced economic partnership
    signed in 2025-2026: `CNFM`, `CNKI`, `CNNR`, `CNVU`, `CNFJ-EEPA`, `CNTO`, `CNPG-EEPA`,
    `CNSB`;
  - China-Africa economic partnership for shared development: early harvest arrangements with
    Kenya (`CNKE`) and Seychelles (`CNSC`, both signed), the concluded Gabon negotiations
    (`CNGA`), and framework agreements with South Africa (`CNZA`), Nigeria (`CNNG`), Namibia
    (`CNNA`) and Cabo Verde (`CNCV`).
- `scripts/oneoff/import_mofcom_fta.py`, the curated import that wrote these changes.
- Beneficiary history for the preference schemes imported from the WTO Preferential Trade
  Arrangements Database, read from every database version (walked 2026-11-23; OpenSpec
  `add-preference-scheme-beneficiary-history`).
  - A beneficiary that a later version first lists has `in_force`. A beneficiary that a
    version drops has `left`, and countries that graduated or were removed are now listed as
    former beneficiaries (`trade_agreement_parties.status = 'former_party'`): 439 rows in 30
    schemes, such as the beneficiaries that left `EU-GSP` in the 2014 reform.
  - These are no-later-than dates. Beneficiaries already in the earliest list (about 2011)
    have no `in_force`, and earlier spells are in the party `note`.
  - Older sub-scheme lists are dated only when their size matches the count in the
    database's dropdown label. Current lists are unchanged.
- Validation rule `TRADE_AGREEMENT_PARTY_DATE`: a party's `in_force` is not before the
  agreement's, its `left` is not after the agreement's `ended`, and `left` is after its own
  `in_force`.
- 45 preference schemes from the WTO Preferential Trade Arrangements Database (walked
  2026-11-23) in `trade_agreements`, all `verification: catalogue`:
  - 29 schemes: the national GSP schemes (`EU-GSP`, `JP-GSP`, `US-GSP`, `GB-DCTS`, `EAEU-GSP`
    and others), the LDC-only schemes (`IN-DFTP`, `KR-LDC`, `CL-LDC` and others), and 6 other
    programmes (`EU-ATM-WB`, `US-ATPA`, `US-NTPP` and others);
  - 16 sub-schemes, such as `EU-GSP-EBA`, `NO-GSP-ZERO`, `CA-GSP-LDCT` and `AGOA-APPAREL`.

  Each record lists its grantor and the beneficiaries of the scheme's latest version. Its
  provenance gives that version's date: some lists are old, the EU GSP list is from 2017-06-29.
  China's LDC scheme is not added, because the database lists no beneficiaries for it.
  (OpenSpec `add-preference-scheme-rosters`.)
- Party roles:
  - `parties[].role` (`grantor`, `beneficiary`) on preference schemes;
  - a `role` column in `trade_agreement_parties` and `country_trade_agreements`, which is
    `party` on every reciprocal agreement.
- `parent` in `trade_agreements`: it links a sub-scheme to its scheme, and a national scheme
  to the `GSP` framework (`GSP` → `EU-GSP` → `EU-GSP-EBA`, `GSPPLUS`).
- `wto_pta_ids` in `trade_agreements`: the PTA Database ids, a list. `AGOA`, `CBERA`,
  `CARIBCAN` and `SPARTECA` have theirs now.
- Validation:
  - `TRADE_AGREEMENT_PARTY_ROLE`: a preference scheme needs a grantor and a beneficiary, and
    a linked preference-scheme intblock may use only `contributor` and `recipient`;
  - `TRADE_AGREEMENT_PARENT`: a sub-scheme has the parent's grantors and a subset of its
    beneficiaries;
  - `DUPLICATE_WTO_PTA_ID`.
- 46 trade agreement records from the OAS Foreign Trade Information System (SICE), checked
  on 2026-11-23 (`scripts/oneoff/import_sice.py`): ALADI complementation and partial scope
  agreements (ACE 14, 16, 57, 58, 59, 72; AAP.A25TM 22, 23, 29, 38, 41, 42; ACE 54 and 55
  with Mexico), free trade agreements never notified to the WTO (`ARCL`, `BRCL`, `CLUY`,
  `CLPY`, `CLEC`, `CREC`, `AECR`, `AECL`, `GTIL`, `GTPE`, `PYTW`), signed agreements
  (`AECO`, `COPA-2013`, `ILPA`, `PATT`, `MERCOSURPA`) and current negotiations (`BZSV`,
  `CLTT`, `CRIL`, `DOEC`, `AEEC`, `AEPE`, `PESV`, `MERCOSURAE`, `INUS`, `GCCCL`). Entry into
  force per pair of parties is kept as party `in_force` dates; ALADI codes are `acronyms`.
- Four Swiss trade agreements from Fedlex, checked on 2026-11-23:
  - `CHLI`, the Switzerland-Liechtenstein Customs Treaty (`customs_union`, in force since
    1924-01-01);
  - `EUCH-AGRI`, the EU-Switzerland Agreement on Trade in Agricultural Products (Bilaterals I,
    in force since 2002-06-01; Liechtenstein included from 2007-09-27);
  - `CHGB-FSA`, the Berne Financial Services Agreement with the United Kingdom (`services`, in
    force since 2026-01-01);
  - `CHGB-MOBILITY`, the UK-Switzerland Services Mobility Agreement (`services`, in force since
    2021-01-01).
- New `trade_agreement_instruments` table (Parquet, JSONL, DuckDB; listed in
  `contract.json` and `datapackage.json`). It has one row per agreement and per instrument
  that amends or adds to the agreement: upgrade and amending protocols, CEPA Supplements,
  supplementary agreements, early harvest arrangements and Joint Committee decisions. Each
  row has a `kind`, a `status`, dates, `coverage` and provenance. The primary key is
  (`agreement_id`, `instrument_id`). This is an additive (MINOR) contract change; OpenSpec
  `add-trade-agreement-instruments`.
- Optional `instruments` list on `data/trade_agreements/*.yaml` records, validated by the
  JSON Schema and by the rules `DUPLICATE_TRADE_AGREEMENT_INSTRUMENT` and
  `TRADE_AGREEMENT_INSTRUMENT_DATE`. The quality report lists instruments signed before
  their agreement as `TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`.
- 136 instruments on 48 records:
  - 122 come from the WTO RTA-IS `RTA Changes` sheet, checked on 2026-11-23. They are
    Joint Committee decisions of EFTA and other agreements, the Mainland–Hong Kong and
    Mainland–Macao CEPA Supplements and agreements, and amending protocols.
  - 14 come from China FTA Network (MOFCOM) releases. They are the `ACFTA` 2.0 and 3.0
    protocols, the upgrade protocols of `CHCN`, `CLCN`, `CNGE`, `CNNZ`, `CNPE` and `CNSG`,
    the `CNPK` second-phase protocol, the `CNNI` early harvest arrangement, and the
    negotiations on `CNKR` (second phase), `CNNZ` (services) and `SACUCN` (early harvest).
- `scripts/oneoff/import_trade_agreement_instruments.py`, the import that wrote them.
- Query recipes for an agreement's instruments and for agreements upgraded since a date.
- `suspended` value for trade agreement `status` (and `country_trade_agreements.agreement_status`):
  negotiations that were launched and then suspended, paused or put on hold without being
  formally ended. A `suspended` record has no `in_force` or `provisional_application` date and
  is not an intblock candidate. An agreement in force whose application is suspended keeps
  `in_force`. Both enums are open, so this is a MINOR contract change with no `schema_hash`
  change; consumers that filter `status = 'negotiating'` for live talks no longer get frozen
  ones. OpenSpec change `add-suspended-trade-agreement-status`.
- `agreement_type` value `trade_relations` in the trade agreements registry (OpenSpec
  `add-investment-and-trade-relations-types`) for agreements that grant most-favoured-nation
  or normal trade relations treatment without preferences. It covers the United States only so far.
- 41 U.S. bilateral investment treaties from trade.gov (`ALUS-BIT` … `USUY-BIT`), checked on
  2026-11-23, including the terminated treaties with Bolivia and Ecuador.
- 27 U.S. trade relations records from the ITA's former TARA database and the State
  Department's Treaties in Force 2026: 21 agreements on trade relations (`-TRA` ids, among
  them `RUUS-TRA`, `USVN-TRA`, `CNUS-TRA`) and the 1881 treaty of commerce with Serbia as
  applied to the six successor states of Yugoslavia (`-1881` ids).
- `ITA` (Information Technology Agreement, 56 participants) and `TCA` (Agreement on Trade in
  Civil Aircraft, 33 Signatories), WTO plurilaterals with rosters from the WTO.
- `unts_registration` in `trade_agreements`: the UN Treaty Series registration number
  (OpenSpec `add-trade-relations-walk`), with a validator check that no two records share it.
- 342 bilateral trade relations agreements (`agreement_type: trade_relations`): 301 with the
  status from the treaty databases of Australia, Canada, the Netherlands and Switzerland, and
  41 found only in the UN Treaty Series, concluded since 2000 between countries outside the EU
  (`verification: catalogue`). Agreements that the Netherlands concluded with Belgium and
  Luxembourg have the `BENELUX` intblock as one party.
- `provisional_application` on trade agreement records and parties, and as a column of
  `trade_agreements`, `trade_agreement_parties` and `country_trade_agreements`: the date an
  agreement began to apply provisionally. `in_force` is now the definitive entry into force;
  an agreement applied only provisionally keeps `status = 'in_force'` with an empty `in_force`.
  Use `coalesce(provisional_application, in_force)` for "applies since". OpenSpec change
  `add-trade-agreement-provisional-application`.
- Five UK trade agreements from gov.uk, checked on 2026-11-23: `GBUA-DTA` (UK-Ukraine Digital
  Trade Agreement, in force since 1 September 2024) and four under negotiation, three of them
  concluded: `GCCGB` (UK-Gulf Cooperation Council FTA, concluded 20 May 2026), `GBKR-2025`
  (upgraded UK-Korea FTA, concluded 15 December 2025), `CHGB-2026` (enhanced UK-Switzerland
  FTA, concluded 13 July 2026) and `GBTR-2024` (enhanced UK-Turkey FTA).
- `unctad_iia_id` in `trade_agreements`: the UNCTAD IIA Navigator treaty identifier that
  `add-investment-agreements` specifies, with a validator check that no two records share it.
- 3,367 bilateral investment treaties from the UNCTAD IIA Navigator (OpenSpec
  `add-unctad-bit-walk`), read from Wayback Machine captures of 2025–2026, as
  `agreement_type: investment` records at `verification: catalogue`. The U.S. BITs from
  trade.gov and the Canadian treaties gain their UNCTAD ids.
- U.S. Agreements on Reciprocal Trade in the trade agreements registry, checked against USTR, the White House, the
  Federal Register and partner governments on 2026-11-23: `MYUS-ART`, `KHUS-ART`, `SVUS-ART`, `GTUS-ART`,
  `ARUS-ART` (with its Protocol of Amendment of 14 October 2026), `BDUS-ART`, `TWUS-ART`, `IDUS-ART`, `ECUS-ART`
  and `JOUS-ART`. They are `pta` records with status `signed`: none had entered into force.
- The 2025–26 reciprocal trade frameworks that have not led to a signed agreement, as `framework` records with
  status `signed` and the date the framework was agreed: `GBUS-EPD` (UK Economic Prosperity Deal general terms),
  `EUUS-FRAMEWORK`, `JPUS-FRAMEWORK`, `KRUS-FRAMEWORK`, `CHLIUS-FRAMEWORK`, `USVN-FRAMEWORK`, `THUS-FRAMEWORK`,
  `MKUS-FRAMEWORK` and `INUS-FRAMEWORK`. Frameworks that led to a signed agreement are noted on that agreement.
- U.S. trade and investment framework agreements (TIFAs, TICFAs, trade and investment councils and forums) in the
  trade agreements registry: 62 `framework` records with ids `<pair>-TIFA` (`AFUS-TIFA` … `USZA-TIFA`, bloc
  agreements such as `ASEANUS-TIFA`, `COMESAUS-TIFA`, `EACUS-TIFA`, `SACUUS-TIFA`, `UEMOAUS-TIFA`,
  `CARICOMUS-TIFA` and `CARICOMUS-TIFA-1991`), all `in_force` at `verification: official`. Dates come from the
  State Department's Treaties in Force 2026 and from the texts USTR posts (scans read with OCR), with USTR press
  releases for WAEMU (2002) and the 2012 amendment of the South Africa TIFA, which is recorded as an instrument. The
  two 2008 protocols to the Uruguay TIFA are instruments of `USUY-TIFA`. Each record links USTR's text and, where
  EDIT holds the text, its EDIT document page; notes give EDIT's date where it differs (Afghanistan, Sri Lanka,
  Saudi Arabia, Central Asia).
- Councils on trade and investment that Treaties in Force 2026 still lists although USTR's current TIFA page does
  not: Bolivia, Chile, Guatemala, Honduras, Panama, Suriname, Venezuela, CARICOM (1991), the Central
  American-U.S. regional council (1998) and the Andean Community council (1998), and the framework agreements with
  Estonia, Jordan, Lithuania, Mexico (1987), Morocco and Singapore.

### Changed

- The names of `ALADI-AG2`, `BRGYKN` and `GTMXSV` list three or more parties as "A, B and C".
- `CAJP` and `CASG` are now `abandoned`. Global Affairs Canada lists both negotiations as inactive: Japan's last round was in November 2014, and Singapore's talks have been on hold since November 2009.
- `CAPH` and `CATH` are now `negotiating`, not `proposed`. The Canada-Philippines negotiations were launched on 2025-10-26 and concluded on 2026-11-14.
- `CAIN` is renamed "Canada-India Comprehensive Economic Partnership Agreement", after the November 2025 relaunch.
- `ASEANCA` notes the substantial conclusion of negotiations on 2026-11-15.
- `ASEANCA`, `CAID`, `CAIN`, `CAJP`, `CAPH`, `CASG` and `CATH` move from `catalogue` to `official`.
- The early harvest records `CGCN`, `CNGA` and `CNSC` (frameworks signed in September 2024)
  and `CNKE` (framework signed on 24 April 2025) note their framework agreements.
- The validator also reports a `dta_id` set on two records as `DUPLICATE_IDENTIFIER`.
- `CNTW` (ECFA) lists its two follow-up agreements as `instruments` instead of in `notes`:
  the Cross-Strait Investment Protection and Promotion Agreement (`investment-2012`, signed
  2012-08-09, in force 2013-02-01) and the Cross-Strait Agreement on Trade in Services
  (`services-2013`, signed 2013-06-21, not in force), checked against the Taiwan Laws &
  Regulations Database and the Straits Exchange Foundation on 2026-11-23.
- 458 records note the date of signature, entry into force or termination that EDIT gives where
  it differs from the record; no date or status was changed. `verification: catalogue` also
  covers records taken only from EDIT.
- `EFTAMY` and `EFTATH`, already `signed` from the EFTA free trade network review, also cite
  SECO (Swiss State Secretariat for Economic Affairs) for the date of signature and status.
  They take their parties from the EFTA partner pages instead of ADB ARIC. `EFTATH` is now
  named `EFTA-Thailand Free Trade Agreement` and keeps the ADB ARIC name in `other_names`.
  `EFTAMY` lists the official title, `Economic Partnership Agreement between the EFTA States
  and Malaysia`.
- 29 EFTA trade agreement records checked on 2026-11-23 against the EFTA free trade
  network partner pages (Wayback Machine copies, because efta.int sits behind a bot
  check), with the WTO RTA-IS ID cards and Fedlex as tie-breakers. Each one now links its
  EFTA page and cites it in `provenance`. 26 records move from `catalogue` to `official`
  verification; `EFTAMD`, `EFTAXK` and `EFTATSOUZ` stay `catalogue`.
- Per-state entry-into-force dates (`parties[].in_force`) for agreements that entered into
  force on different dates for different EFTA States: `EFTAAL`, `EFTACO`, `EFTACRPA`,
  `EFTAMD`, `EFTAME`, `EFTAMERCOSUR`, `EFTAPE`, `EFTARS`, `EFTATN`, `EFTAXK` and
  `EFTASG-DEA`. `EFTAPE` also records Peru's later signature (2010-07-14).
- `EFTAMY` is renamed to EFTA-Malaysia Economic Partnership Agreement (MEEPA). `EFTAEC` is
  renamed to EFTA-Ecuador Comprehensive Economic Partnership Agreement, and `EFTAPS` to
  EFTA-Palestine Interim Agreement (concluded with the PLO for the benefit of the Palestinian
  Authority). Official titles from Fedlex go in `other_names`, and so do the former WTO-style
  names.
- Notes on later instruments: the amending protocols for `EFTAAL` (2015, in force 2017),
  `EFTARS` (2015, in force 2017), `EFTAME` (2021, in force 2022) and `EFTABA` (2022, in force
  2023); the rules-of-origin decisions for `EFTAJO` (2025, in force 2026-02-01) and `EFTATN`
  (2024, in force 2026-03-01); the revised `EFTAIL` agricultural agreements (signed 2018, in
  force 2021-08-01); and the review talks for `EFTAMX` and `EFTASACU`.
- `EUGCC` (EU-Gulf Cooperation Council FTA, suspended since 2008) moves from `negotiating` to
  `suspended`. Its UAE party notes that the UAE is not on the Commission's on-hold list and has
  negotiated a bilateral FTA (`EUAE`) since 2025.
- EU trade agreements now separate provisional application from entry into force, using Official
  Journal notices:
  - Applied provisionally only, so `in_force` is now empty: `CETA`, `EUCI`, `EUGH`,
    `EUCENTRALAFRICAEPA`, `EUESAEPA`, `EUSADCEPA`, `EUCARIFORUMEPA`, `EUPACIFICEPA` and the
    `EUMERCOSUR` interim agreement.
  - `in_force` is now the definitive date and `provisional_application` the earlier one:
    `EUKR` (2015-12-13), `EUUA` (2017-09-01), `EUGE` and `EUMD` (2016-07-01), `EUAM`
    (2021-03-01), `EUANDEAN` (2024-11-01), `EUCENTRALAMERICA` (2024-05-01) and `EUCL-2002`
    (2005-03-01).
- `EUAL`, `EUMK`, `EUME`, `EUBA`, `EURS` and `EULB` now carry the entry into force of the
  Stabilisation and Association Agreement or Association Agreement itself. The earlier trade
  date belongs to the new Interim Agreement record.
- `EUEE`, `EULV` and `EULT` (the 1994 free trade agreements) are `superseded` by the Europe
  Agreements and ended on 1998-02-01.
- `EUCENTRALAMERICA` and `EUANDEAN` intblocks note when trade provisions began to apply for each
  partner.
- `EUID` (EU-Indonesia CEPA) is `signed` (2026-11-21), and `EUKR-DIGITAL` (EU-Korea
  Digital Trade Agreement) is `signed` (2026-06-10).
- `EUAU`, `EUIN`, `EUMY` and `EUTH` now have notes with the dates when negotiations were
  concluded, paused or resumed, as the European Commission gives them. These records,
  `EUID`, `EUKR-DIGITAL` and `EUCL` are now `verification: official`.
- `EUCL` is named `EU-Chile Interim Trade Agreement`.
- 19 EU agreements have notes that tell provisional application apart from full entry
  into force. The dates are not changed: `in_force` keeps the date from which trade
  provisions first applied.
  - The Western Balkans SAAs (`EUAL`, `EUBA`, `EUME`, `EURS`, `EUMK`) get their entry
    into force dates from EUR-Lex. The Commission gives the dates for `EULB`, `EUGE`,
    `EUMD` and `EUAM`.
  - `EUUA` gets the 2025 DCFTA upgrade.
  - `EUCENTRALAMERICA` gets its staggered 2013 provisional application by country and
    full application from 2024-05-01.
  - `EUANDEAN`, `EUCARIFORUMEPA`, `EUPACIFICEPA`, `EUESAEPA`, `EUSADCEPA`, `EUCI`,
    `EUGH` and `EUMERCOSUR` are marked as still provisionally applied.
  - Where the Commission's overview disagrees with the record (Papua New Guinea,
    Namibia, Côte d'Ivoire), the note gives both dates.

- 62 EU trade agreements move from `verification: catalogue` to `official`. Their
  signature and entry-into-force dates are checked against EUR-Lex metadata from the
  Publications Office Cellar SPARQL endpoint, and each record cites the CELEX document
  in `provenance` and `links`.
  - `EUGE`, `EUMD`, `EUAM` and `EUCL-2002` keep the provisional-application date in
    `in_force`; their notes give the EUR-Lex date of full entry into force.
  - `EUPH` is confirmed by the Commission's negotiations overview.
- 14 EU records stay `catalogue`: EUR-Lex gives different dates, and their notes quote
  the EUR-Lex values for review. They are `EUAT`, `EUCI`, `EUCZSK`, `EUSI`,
  `EUSI-1996-2`, `EUEE`, `EULT`, `EULV`, `EUEG-1972`, `EULB-1972`, `EULB-1977`, `EUAD`,
  `EUMX` and `EUTR`.
- A trade agreement record linked to an intblock may list its own `links`; the export puts
  them after the intblock's links instead of dropping them.
- The validator reports a `wto_rta_id`, `aric_id` or `gptad_id` set on two records as
  `DUPLICATE_IDENTIFIER`.
- `ACIA` entered into force on 29 March 2012, per the Malaysian trade ministry (MITI), not on 24 February 2012 as UNCTAD gives it.
- The `services` agreement type now means services-only agreements. Investment treaties use `investment`.
- `country_trade_agreements` and `trade_agreement_parties` now include investment treaties. Filter on `agreement_type` to count trade agreements only.
- `SIAP` (Statistical Institute for Asia and the Pacific) now declares `partof: ESCAP`.
- `CGCN` and `BYCN` take their official names (the China-Republic of the Congo early harvest
  arrangement and the China-Belarus Agreement on Trade in Services and Investment), keep the WTO
  RTA-IS names as other names, and are now `verification: official`.
- Notes on upgrade protocols and early harvest arrangements from MOFCOM releases: `ACFTA`
  (versions 2.0 and 3.0), `CHCN`, `CLCN`, `CNGE`, `CNKR` (second phase), `CNNI`, `CNNZ`,
  `CNPE`, `CNPK`, `CNSG`, and `SACUCN`; joint feasibility study dates on `CACN`, `CNCO`, `CNFJ`,
  `CNMN` and `CNNP`.
- MOFCOM topic pages added as links to 31 China records.
- `HNSVTW`: El Salvador's party row records its exit on 7 November 2022.
- `country_trade_agreements` has about 2,800 more beneficiary rows and grantor rows (EU
  schemes expand to the 27 member states). Queries that count reciprocal trade links between
  countries should filter on `role = 'party'` or `agreement_type <> 'preference_scheme'`.
- `GSP` and `SPARTECA` intblocks:
  - the 16 GSP grantors are `contributor` instead of `participant`;
  - in SPARTECA, Australia and New Zealand are `contributor` and the 13 Forum Island Countries
    `recipient`, instead of `founding_member` and `member`.

  `memberships` shows the new statuses.
- The Lomé Conventions (`LOME-1975`, `LOME-1979`, `LOME-1984`) give the EU the role `grantor`
  and the ACP States the role `beneficiary`.
- Preference schemes are no longer reported as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`.
- Four trade agreements whose `in_force` held the start of provisional application now
  record it in `provisional_application`, checked against official sources on 2026-11-23:
  - `EUUK` (EU-UK Trade and Cooperation Agreement): `provisional_application` 2021-01-01,
    `in_force` 2021-05-01, from the Official Journal notices (CELEX 22021X0101(01) and
    22021X0430(02)).
  - `EUZA` (EC-South Africa Trade, Development and Cooperation Agreement, `superseded`):
    `provisional_application` 2000-01-01 under the Exchange of Letters (CELEX
    21999A1204(01)), `in_force` 2004-05-01 (CELEX 21999A1204(02)).
  - `GBVN` (UK-Vietnam Free Trade Agreement): `provisional_application` 2021-01-01, from the
    Viet Nam Ministry of Industry and Trade; `in_force` stays 2021-05-01 (UK Treaty Series).
  - `GBGH` (UK-Ghana Interim Trade Partnership Agreement): `provisional_application`
    2021-03-05, from the CS Ghana No.1/2021 page. `in_force` is now empty: the UK still lists
    the agreement as applied provisionally, and no Treaty Series publication or official date
    of entry into force has been found.
- `CHCN`, `CHJP` and `CHFOLI` are `official`, with Fedlex links and provenance (dates
  unchanged).
- `EFTAEE`, `EFTALV` and `EFTALT` give Switzerland's own entry into force (1997-10-01 and
  1997-08-01). `EFTAEE` now lists Switzerland as a party.
- The upgrade and early harvest sentences that the MOFCOM import put in `notes` on 11 records
  now live in `instruments`. When MOFCOM and the WTO give different dates for the same
  instrument, the item's `notes` record the WTO dates.
- `EFTATSOUZ` (EFTA-Russia/Belarus/Kazakhstan, suspended after 11 rounds since 2011) and
  `EFTADZ` (EFTA-Algeria, on hold since 2008) move from `negotiating` to `suspended`.
  `EFTATSOUZ` now cites the EFTA page for its status and parties and moves from `catalogue` to
  `official` verification.
- `CAFTADR` notes give the entry-into-force date for each signatory and the 2006 amendment
  to Article 22.5; `USBH` notes the 2009 First Protocol of Amendment; `USAU`, `USCO`,
  `USKR`, `USPA`, `USSG` and `CAFTADR` cite trade.gov for `in_force`; `USMCA` links trade.gov.
- `verification: catalogue` also covers records taken only from the UN Treaty Series.
- `ALUS-TRA` and `CNUS-TRA` give their UN Treaty Series registration numbers.
- 34 UK trade agreement records are checked against gov.uk and the UK Treaty Series and are
  now `verification: official`, with the gov.uk name (the catalogue name stays in
  `other_names`), the agreement collection link and the treaty series numbers in `notes`.
  Entry into force dates follow the Treaty Series: 31 December 2020 instead of 1 January 2021
  for 12 continuity agreements, and later dates for `CAGB`, `CMGB`, `EGGB`, `GBISLINO`, `GBKE`,
  `GBMK`, `GBRS` and `GBTR`, several of which applied provisionally from 1 January 2021.
  `GBMA`, `UKCARIFORUM` and `UKPACIFICEPA` are applied provisionally only and have no
  `in_force` date.
- `CPTPP`: the United Kingdom's entry gives the date its accession entered into force with each
  partner.
- `verification: catalogue` also covers records taken only from the UNCTAD IIA Navigator.

### Fixed

- `CAID` (Canada-Indonesia CEPA) `signed` is 2025-09-24, not 2024-12-02. ADB ARIC gave the date negotiations were concluded. Global Affairs Canada gives entry into force on 2026-12-01; this is recorded in the notes.
- `EFTATH` and `EFTAMY` were still `negotiating`; they are `signed` (2025-01-23 and
  2025-06-23).
- `EFTASG-DEA` was still `negotiating`; it was signed on 2025-09-25 and has been in force
  for Norway and Singapore since 2026-03-01.
- Notes on `EFTATSOUZ` (negotiations suspended), `EFTAVN` (negotiations concluded
  2026-07-02, not signed) and `EFTALB` (the EFTA page's 1 July 2007 date conflicts with
  Fedlex and WTO, which give 1 January 2007 for all parties).
- Dates corrected to EUR-Lex:
  - `EUIS` signed 1972-07-22 (was 1972-12-19);
  - `EUTN` signed 1995-07-17 (was 1995-07-07);
  - `EUFI` ended 1995-01-01 (was 1994-01-01);
  - `EUPT` ended 1986-01-01 (was 1976-01-01).
- `EUDZ-1976` and `EUSY` now describe the 1976 and 1977 Cooperation Agreements.
  - Their `in_force` is 1978-11-01; they had the date of the matching Interim
    Agreements (`EUDZ-1976-2`, `EUSY-1977`).
  - They are renamed to `EC - Algeria Cooperation Agreement` and
    `EC - Syria Cooperation Agreement`.
- `EUTR-1963` (Ankara Agreement) and `EUTR-1970` (Additional Protocol) are `in_force`,
  not `terminated`, and no longer have an `ended` date. EUR-Lex records both as valid
  with no end of validity. WTO RTA-IS had ended them on 1973-01-01 and 1974-01-01, the
  dates of the following instruments. Both are now `verification: official`.
- `EUTR-1973` is the 1973 EC-Turkey Interim Agreement consequent on enlargement, now
  named `EC - Türkiye Interim Agreement of 1973`, and is `verification: official`. It
  ended on 1986-03-01, not 1996-01-01: EUR-Lex gives end of validity on 1986-02-28,
  when the Supplementary Protocol signed the same day entered into force.
- `EUZA` is the EC-South Africa Trade, Development and Cooperation Agreement. It is now
  `superseded` by `EUSADCEPA`, ended 2016-10-10. The SADC EPA repealed its trade
  component when it entered into provisional application in October 2016.

- `EUWESTAFRICAEPA`: the regional EU-West Africa EPA is `signed`, not `in_force`.
  - The intblock no longer has the `active_period` start of 2016-12-15. That date
    belongs to the Côte d'Ivoire and Ghana stepping-stone EPAs (`EUCI`, `EUGH`).
  - The 13 West African signatories listed by the European Commission are now `member`,
    not `partner`. Nigeria, which has not signed, stays `partner`.
- Dates of 14 trade agreement records linked to an intblock. Their exported dates (taken from
  the intblock, or from ADB ARIC or Wikipedia) differed from WTO RTA-IS. Each was checked on
  2026-11-23 against the treaty text, the depositary, the secretariat or a party government,
  and each record now sets its own dates:
  - in force: `ACFTA` 2005-01-01, `AfCFTA` 2019-05-30, `CACM` 1961-06-04, `CAN` 1969-10-16,
    `MERCOSUR` 1991-11-29, `SADCFTA` 2000-01-25, `UEMOA` 1994-08-01;
  - signed and in force: `AFTA` 2009-02-26 and 2010-05-17 (ATIGA), `CEFTA` 2006-12-19 and
    2007-07-26, `COMESA` 1993-11-05 and 1994-12-08, `EAC` 1999-11-30 and 2000-07-07, `EFTA`
    1960-01-04 and 1960-05-03, `EUCU` 1957-03-25 and 1958-01-01 (EEC Treaty), `SACU`
    2002-10-21 and 2004-07-15.
- `AKFTA`, `CEMAC`, `ECOTA` and `MSGTA` keep their dates; their notes record the different
  date or instrument that WTO RTA-IS gives.
- `wto_rta_id: 128` moves from `ECOTA` to a new catalogue record, `ECOPTA-1992`. WTO RTA 128
  is the ECO Additional Protocol on Preferential Tariffs, signed at Tehran on 17 February 1992
  by Iran, Pakistan and Turkey (GATT document L/7047), not the 2003 ECO Trade Agreement, which
  WTO RTA-IS lists no notification of.
- `akfta.asean.org` now serves an unrelated gambling page. The `AKFTA` intblock and record
  link a 2021 Wayback Machine copy of the ASEAN–Korea FTA page instead.
- Dead MOFCOM links on `CNKR` (`/korea/korea_special.shtml`) and in the `CNRS` provenance
  (`/english/fta_qianshu.shtml`).
- `EFTAES`: Austria and Sweden no longer have a `left` date of 1995-01-01. That is when they
  left EFTA, after this agreement had already ended in 1986.
- `CEFTA-1992`: `ended` is 2007-01-01, when Romania, Bulgaria and Croatia stopped being
  parties, not 2004-05-01.
- The release data-change summary and the `data` section of `migration.vX.Y.Z.json` now count
  trade agreement records: ids added, removed and changed since the previous release. Before, the
  release train did not read `data/trade_agreements/`. The release level rules are unchanged.
- Trade agreement dates that differed from OAS SICE, checked on 2026-11-23 against party
  governments and now `verification: official`: `CAKR` signed 2014-09-22 (Canada Treaty
  Series 2015/3), `CLVN` in force 2014-01-01 (Chile Decreto 139), `CLID` in force 2019-08-10
  (Chile Decreto 100), `CNPE` in force 2010-03-01 (MOFCOM), `CLIN` in force 2007-08-17 with
  India from 2007-09-11 (India Department of Commerce) and `USIL` in force 1985-08-19 (U.S.
  State Department, Treaties in Force). `CLHK` keeps 2014-10-09 (Hong Kong SAR Government);
  its notes explain the 29 November 2014 date that Chile and SICE give. The replaced dates
  came from ADB ARIC, except `USIL`, where 1 September 1985 is when the tariff cuts started.
- The 1992 Swiss free trade agreements with Estonia, Latvia and Lithuania (`CHEE`, `CHLV`,
  `CHLT`) entered into force in March 1994, not on 1993-04-01, and ended in 1997, when the EFTA
  agreements took effect for Switzerland. They are now `superseded` by `EFTAEE`, `EFTALV` and
  `EFTALT`.
- `GBGE` signature date (21 October 2019, not 1 January 2014), `GBLB` signature date
  (19 September 2019), `CAGB` (9 December 2020) and `CMGB` (9 March 2021), from the treaty texts.
- `UKESA` lists Madagascar as a party; `UKCARIFORUM` no longer lists Haiti, which has not signed.

### Data changes since the previous release

- Countries: 256 → 256 records
- Intblocks: 1581 → 1606 records; added `BLEU`, `CHILDMAINTENANCE1956`, `CISATC`, `CISSA`, `CIVILPROCEDURE1954`, `ECLAC`, `ESCAP`, `EUADSM`, `EUEACEPA`, `FCM`, `FIORC`, `HYBRIDCOE`, `ICE`, `ITA`, `MAINTENANCE1973`, `MAOCN`, `NOUAKCHOTTPROCESS`, `PARISPACT`, `RCOC`, `RMIFC` and 5 more; 10 changed
- Blocktypes: 83 → 83 records
- Trade agreements: 839 → 5195 records; added `ACFTA-FA`, `ACIA`, `ADAE-BIT`, `AEAG-BIT`, `AEAL-BIT`, `AEAM-BIT`, `AEAO-BIT`, `AEAR-BIT`, `AEAT-BIT`, `AEAU-BIT`, `AEAU-TRA`, `AEAZ-BIT`, `AEBB-BIT`, `AEBD-BIT`, `AEBH-BIT`, `AEBI-BIT`, `AEBJ-BIT`, `AEBR-BIT`, `AEBY-BIT`, `AEBZ-BIT` and 4336 more; 589 changed
- Membership edges: 72461 → 73052; 591 added, 0 removed, 43 changed
- Schema (minor): table trade_agreement_instruments added
- Schema (minor): column country_trade_agreements.provisional_application added
- Schema (minor): column country_trade_agreements.role added
- Schema (minor): column trade_agreement_parties.provisional_application added
- Schema (minor): column trade_agreement_parties.role added
- Schema (minor): column trade_agreements.dta_id added
- Schema (minor): column trade_agreements.gptad_id added
- Schema (minor): column trade_agreements.parent added
- Schema (minor): column trade_agreements.provisional_application added
- Schema (minor): column trade_agreements.unctad_iia_id added
- Schema (minor): column trade_agreements.unts_registration added
- Schema (minor): column trade_agreements.wto_pta_ids added

## [5.0.0] - 2026-11-22

### Added

- `IATI` (International Aid Transparency Initiative, Wikidata Q14901678), a `governance`/`development`
  `policy_forum` record. It lists the 38 countries among the IATI Members' Assembly members: the 22
  partner countries and the 16 providers that are national governments or their agencies, with the
  year each joined. Multilateral, civil society and private sector members are named in the notes.
  Checked on 2026-11-22.
- `COSTINFRA` (CoST – Infrastructure Transparency Initiative, Wikidata Q132472491), a `governance`
  `policy_forum` record with the 9 national members and 9 former national members from the CoST
  "Where we work" page and country pages. Sub-national members and partners are named in the notes.
  Checked on 2026-11-22.
- `REDGEALC` (Red GEALC, Inter-American Network of Digital Government), a `digital`/`governance`
  `policy_forum` record with the 29 countries in its directory of members by country and the 3
  associate members named in its statutes. It has no Wikidata item, so it gets a Wikidata exclusion.
  Checked on 2026-11-22.
- Five multilateral trade agreements found in a walk of the ADB ARIC FTA database, each with a roster from its depositary or secretariat, checked on 2026-11-22:
  - `TPSOIC`, the Trade Preferential System among OIC member states: 14 participating states, from the COMCEC status tables.
  - `D8PTA`, the Preferential Trade Agreement among D-8 Member States: eight parties, with ratification dates from the D-8 Secretariat.
  - `ECOTA`, the ECO Trade Agreement (Wikidata Q24089710): five parties. It has been in force since 2008 but has never been applied.
  - `MSGTA`, the Melanesian Spearhead Group Trade Agreement: four parties, from the MSG Secretariat and WIPO Lex.
  - `KRCENTRALAMERICA`, the Republic of Korea–Central America FTA: six parties, with entry-into-force dates for each party. Guatemala's accession is not yet in force.
- An OpenSpec proposal, `add-trade-agreements-registry`, for a separate registry of all trade agreements, bilateral ones included.
- 35 further records found by the DFAT Australian Treaties Database walk, each with its roster from
  the depositary, secretariat or official site, checked on 2026-11-22. Signatories that have not
  ratified are left out.
  - ICRC IHL Treaties Database: `APIII2005` (Additional Protocol III, 80 parties) and `HAGUEIV1907`
    (Hague Convention IV and its Regulations, 38 parties; the ICRC does not list the British
    Dominions bound through the United Kingdom's 1909 ratification).
  - WIPO Lex: `NICEAGREEMENT` (96), `STRASBOURGIPC` (68), `TLT1994` (55), `PLT2000` (45, with the
    Eurasian Patent Organization) and `SINGAPORETREATY` (58, with OAPI and BOIP).
  - `ATACONVENTION` (A.T.A. Carnet Convention, 65), from the WCO position, and `WARSAW1929`
    (Warsaw Convention, 152), from the ICAO list of parties.
  - IMO Status Book Vol. II of 30 October 2026: `OPRCHNS2000` (43), `BUNKERS2001` (111),
    `SALVAGE1989` (80), `CSC1972` (86) and `INTERVENTION1969` (92).
  - `TRUSTS1985` (HCCH Trusts Convention, 14), from the HCCH status table.
  - Council of Europe, from the Netherlands Treaty Database party tables: `COELAUNDERING1990`
    (ETS No. 141, 49) and `COEANTIDOPING` (ETS No. 135, 52).
  - UNESCO States Parties exports: `UCC1952` (Universal Copyright Convention, 100; the 1971 Paris
    revision is described in the record), `CDE1960` (Convention against Discrimination in
    Education, 112), `TOKYOCONVENTION2011` (Asia-Pacific recognition of qualifications, 13) and
    `GLOBALCONVENTION2019` (Global Convention on higher-education qualifications, 43).
  - Antarctic and Pacific: `MADRIDPROTOCOL1991` (Environmental Protocol to the Antarctic Treaty,
    42), `CCAS` (Antarctic Seals, 17), `ACAP` (albatrosses and petrels, 13, `partof` `CMS`), `PRF`
    (Pacific Resilience Facility, an IGO in Nuku'alofa, 9 members), `SPTT` (South Pacific Tuna
    Treaty with the United States, 17) and `DRIFTNETCONVENTION` (Wellington driftnet convention,
    13).
  - Organizations and groups: `RECAAP` (ReCAAP Agreement, 22), `NACA` (Network of Aquaculture
    Centres in Asia-Pacific, 20), `ACWL` (Advisory Centre on WTO Law, 59) and `WWTG` (World Wine
    Trade Group, an informal `policy_forum` of 9 governments). The International Sugar
    Organization is already recorded as `OIS`.
  - Historical and peace treaties, from the UN Treaty Series and the Tractatenblad: `ELDO`
    (European Launcher Development Organisation, 1964–1975, `successor` `ESA`), `SPEC` (South
    Pacific Bureau for Economic Co-operation, 1973–1993), `SANFRANCISCOTREATY` (Treaty of Peace
    with Japan, 45 parties) and `PARISPEACECAMBODIA1991` (Paris Peace Agreements on Cambodia).
- `GLOBALCONVENTION2019`, `HAGUEIV1907`, `PRF`, `SPEC` and `WWTG` have `wikidata_exclusions.yaml`
  entries: Wikidata has no item for them.
- CAB International, the Waigani Convention and the FAO regional commissions (APPPC, APHCA, the
  International Rice Commission) are not added: their sites refuse automated reads.
- 9 multilateral treaties to which Australia is a party, found missing by walking the DFAT
  Australian Treaties Database and added as `treaty_body` records. Each has its parties roster
  from the depositary or treaty secretariat, checked on 2026-11-22. Signatories that have not
  ratified are left out.
  - `GCI` (Q19136672), `GCII` (Q583921) and `GCIII` (Q3984882): Geneva Conventions I–III of
    1949, each with 196 States parties from the ICRC IHL Treaties Database. `GCIV` was already
    recorded.
  - `SUAFIXEDPLATFORMS1988` (Protocol for the Suppression of Unlawful Acts against the Safety of
    Fixed Platforms Located on the Continental Shelf, 157 parties, Q15991246), from the IMO
    Status Book Vol. II of 30 October 2026.
  - `PLASTICEXPLOSIVES1991` (Convention on the Marking of Plastic Explosives for the Purpose of
    Detection, 157 parties, Q15991245), from the ICAO list of parties.
  - `OECDANTIBRIBERY` (OECD Anti-Bribery Convention, 46 parties, Q626826), from the OECD
    ratification status of August 2024, the latest the OECD publishes.
  - `BEPSMLI` (BEPS Multilateral Instrument, 89 parties, Q39058243), from the OECD signatories
    and parties list of 12 November 2026. Guernsey, Jersey and the Isle of Man are parties in
    their own right; Curaçao and Hong Kong are covered by the Netherlands and China and are not
    listed.
  - `GPA` (WTO Agreement on Government Procurement, 22 parties, Q331553), from the WTO parties
    page. The European Union is one party and its member States are not listed separately.
  - `TAC` (Treaty of Amity and Cooperation in Southeast Asia, 62 High Contracting Parties
    including the European Union, Q1054948), from the ASEAN Legal Instruments database.
- The International Treaty on Plant Genetic Resources for Food and Agriculture and the FAO Port
  State Measures Agreement are not added: the FAO site refuses automated reads.
- `GIFT` (Global Initiative for Fiscal Transparency), a `governance` `policy_forum` record listing the
  23 national governments among its stewards. The roster comes from a Wayback Machine copy of the GIFT
  About page of 4 May 2026, because the live site returned server errors on 2026-11-22. That page was
  last edited on 1 March 2024, so the roster may be out of date.
- `DPGA` (Digital Public Goods Alliance, Wikidata Q102440976), a `digital` `policy_forum` record listing
  the 24 national governments among its members on the DPGA Roadmap, with joining dates from the
  alliance's announcement posts. Checked on 2026-11-22.
- `BOLG` (Beneficial Ownership Leadership Group), a historical `governance` `policy_forum` record. Its
  eight members are recorded as former members, because the group concluded in December 2023. Checked
  on 2026-11-22.
- `IIC` (Inter-American Investment Corporation, IDB Invest, 48 member countries) and four commodity
  organizations, with members from their own membership pages (checked on 2026-11-22): `ICO`
  (International Coffee Organization), `ICCO` (International Cocoa Organization), `OIS`
  (International Sugar Organization) and `IOOC` (International Olive Council).
- `ODC` (International Open Data Charter, Wikidata Q22905856), a `governance`/`digital` record for the
  six non-binding open data principles launched in 2015. Its 29 national government adopters come from
  the Open Data Charter government adopters page, checked on 2026-11-22. The 146 sub-national adopters
  and the endorsing organisations are not country members and are not listed.
- Trade agreements registry (OpenSpec `add-trade-agreements-registry`). Source files are in
  `data/trade_agreements/<ID>.yaml` and follow `data/schemas/trade_agreements.schema.json`.
  The build exports them as new `trade_agreements` and `trade_agreement_parties` tables
  (Parquet, JSONL, DuckDB) and a new `country_trade_agreements` view. In the view, a bloc
  party such as the EU expands to its current member countries, with `via` set to the bloc id.
  The registry records parties, status, dates, `wto_rta_id`, `aric_id` and provenance only.
  It has no trade values, tariff lines or depth scores.
- Every multilateral `fta`, `pta` and `customs` intblock, plus `TFTA`, `PACER` and `EAEU`, has a
  registry record linked to the intblock with `intblock:`. The record reads its parties from the
  intblock's `includes`.
- The ADB ARIC FTA database (snapshot of 2026-11-22) is imported. Rows that matched existing
  records got `aric_id`; the other rows are new `verification: catalogue` records. ARIC's
  proposed and negotiating agreements are imported as well, with their status.
- Twelve multilateral agreements from the ARIC walk that are in force now have intblocks in
  `data/intblocks/fta/`, with party-by-party dates from official sources. Each is linked from its
  registry record:
  - EFTA agreements, dated from the Swiss Fedlex scope tables and EFTA partner pages: `EFTASG`,
    `EFTAKR`, `EFTAHK`, `EFTAPH`, `EFTAID`, `EFTAGE` and `EFTATR` (the modernised 2018
    agreement).
  - EAEU agreements, from Eurasian Economic Commission texts: `EAEUVN`, `EAEURS` and `EAEUIR`
    (the 2023 agreement). The Union itself is a party alongside its member states.
  - `GCCSG`, the GCC–Singapore FTA. The six GCC states are parties individually.
  - `UKPACIFICEPA`, the UK–Pacific States interim EPA. It is applied provisionally from 1 January
    2021; Samoa and Solomon Islands acceded on 31 March 2022.
- The eight ARIC candidates marked as signed but not in force were checked against official
  sources, because ARIC's statuses were out of date:
  - `MERCOSURSG`, `PACALLSG` (Pacific Alliance–Singapore), `EAEUCN` (EAEU–China, a
    non-preferential agreement) and `AZTMTR` (Azerbaijan–Türkiye–Turkmenistan cooperation) are
    in force. Each now has an intblock, with per-party dates.
  - `EAEUSG` (EAEU–Singapore) is signed but not yet in force. It now has an intblock with no
    `active_period`.
  - `GCCKR`, `GCCNZ` and `GCCPK` were only concluded, never signed. Their registry status is now
    `negotiating`, and they have no intblock.
  - ARIC lists Australia, New Zealand and Canada as parties to the Pacific Alliance agreement.
    None of them signed it.
- Two earlier agreements are registry records with status `superseded`: `EFTATR-1991`, the
  EFTA–Turkey agreement of 1991, and `EAEUIR-2018`, the EAEU–Iran interim agreement of 2018.
- New validator rules for the registry: schema, ids shared with intblocks, party and intblock
  resolution, status and date consistency, and freshness. The quality report now lists
  multilateral catalogue records that have no intblock yet.
- Topic key `industry` (Industry), first used by `UNIDO`.
- The WTO RTA Information System export of 2026-11-22 is imported into the trade agreements
  registry by `scripts/oneoff/import_wto_rtais.py`. Every in-force and inactive RTA that was not
  recorded yet is a new record: 346 `verification: catalogue` records with the parties that WTO
  lists, and five records linked to existing intblocks (`CCASG`, `ECOWAS`, `EEA`, `ALADI` and
  `CARICOM`). An inactive agreement has status `terminated`, or `superseded` with
  `superseded_by` when its successor is known, and the WTO inactive date as `ended`.
- 260 existing registry records now have `wto_rta_id`. Accession rows (EC enlargements, COMESA,
  EAEU, CPTPP and others) map to the agreement that they join.

### Changed

- `OIC`, `D8`, `ECO`, `MSG` and `GUAM` now have notes that point to their trade agreements. The GUAM free trade agreement is a note only, because its parties are the GUAM members.
- `docs/intblock-sources.md` logs the ARIC walk.
- `ESA` has `predecessor: ELDO`.
- `COEAICONVENTION` (Council of Europe Framework Convention on AI, CETS No. 225): the roster is
  now sourced from the Council of Europe Treaty Office chart of signatures and ratifications
  (status as of 21 November 2026), which agrees with the Netherlands treaty database. The parties
  are unchanged: the EU and Bosnia and Herzegovina.
- `ILO` reviewed on 2026-11-22. The 187 members are unchanged: 186 UN members and the Cook
  Islands.
  - Set `joined` on every member to its date of latest admission. Readmitted states (for
    example the United States in 1980, South Africa in 1994 and Germany in 1951) note their
    earlier membership periods.
  - Add the State of Palestine as an observer: the 113th International Labour Conference made it
    a non-member observer State in June 2025.
  - Add 40 `founding_members`: the Treaty of Versailles signatories and the States invited to
    join in 1919, mapped to present members.
  - Add `recognition_status` (UN specialized agency since 1946), `secretariat`, and notes on
    membership rules, tripartite organs and Directors-General.
  - Move the headquarters coordinates to the ILO building.
  - Fix the French acronym, rewrite the description, replace the generic tags, expand topics
    and `other_names`, and add source-backed provenance.
- `OPENGOV` (Open Government Partnership): the record moves from `agreement/` to `governance/`
  (`blocktype: [governance]`, `scope_category: policy_forum`, `geographic_scope: global`), because
  OGP is a voluntary partnership whose members endorse a declaration, not a treaty.
- `OPENGOV` roster rebuilt from the OGP National Members and Procedural Review pages (22 November
  2026): 72 active members with the year they joined, Kosovo as a non-voting member (`participant`),
  and 15 withdrawn countries as `former_member`, each with the year it joined (from OGP or the
  letter of intent OGP publishes) and the date it left OGP.
  Benin, Albania, Burkina Faso, Cabo Verde, Côte d'Ivoire, Maldives, Papua New Guinea, Senegal,
  Seychelles, Thailand and Timor-Leste are added as members. Azerbaijan, Denmark, El Salvador,
  Georgia, Hungary, Israel, the Kyrgyz Republic, Sri Lanka, Tanzania and the United States change
  from `member` to `former_member`, and Afghanistan, Luxembourg, Pakistan, Trinidad and Tobago and
  Turkey are added as `former_member`. Austria and Japan, which are not on any OGP member list, are
  removed. `membership_count` changes from 73 to 72. `left` is the date a withdrawal took effect
  where the withdrawal letter, OGP letter or Steering Committee resolution states one (for example
  Denmark 31 December 2024, Luxembourg 1 January 2023, the Kyrgyz Republic and Sri Lanka 10 May
  2025), otherwise the date of the document that ended membership (Israel 1 February 2026,
  El Salvador 28 March 2023, and the resolutions that permanently suspended Azerbaijan on 21 July
  2023 and Georgia on 13 April 2026).
- `OPENGOV` gains a full description, founding date (20 September 2011) and founding members,
  the Open Government Declaration, the Support Unit secretariat, social media links, governance
  topics, more names in other languages, and corrected acronyms.
- `OSPAR` is named "OSPAR Convention" to match its `treaty_body` scope and its roster of
  Contracting Parties; "OSPAR Commission" stays in `other_names`. `legal_status` is `treaty`.
- `OSPAR` includes gain `joined` dates: the date each of the 16 Contracting Parties deposited
  its instrument of ratification or approval, from the Netherlands treaty database.
- `OSPAR` gets a fuller description and notes, the `biodiversity` topic, more names in other
  languages, and field-level provenance with named sources.
- `intblocks_aliases` has a new `target_dataset` column and a new reason, `moved`.
  `countries_aliases` keeps its old columns.
- `docs/intblock-inclusion-policy.md`: bilateral trade agreements belong in the registry.
  The bar for an intblock still applies to agreements with three or more parties.
- Ten ADB ARIC catalogue records take the WTO RTA-IS status: `AMRU`, `KGRU`, `KZRU`, `RUTJ` and
  `NITW` are terminated; `GTTW`, `CNMV`, `ILVN`, `HKPE` and `INNZ` are in force. `GBGE` and
  `GBUA` have type `fta` instead of `other`.
- ARIC catalogue records that give only a year, or no date, take the full WTO date of
  signature or entry into force.

### Removed

- **Breaking, needs a MAJOR release (5.0.0).** 34 two-party trade agreements left `intblocks`
  and `memberships` and moved to `trade_agreements` under the same ids:
  `ANZCERTA`, `AUINDIA`, `AUUAE`, `AUUK`, `CETA`, `CHAFTA`, `CNEC`, `CNKR`, `CNNI`, `CNRS`,
  `EUCENTRALAFRICAEPA`, `EUJP`, `EUKR`, `EUNZ`, `EUSG`, `EUUA`, `EUUK`, `EUVN`, `INUAE`,
  `UKIN`, `UKJP`, `UKNZ`, `USAU`, `USBH`, `USCL`, `USCO`, `USIL`, `USJO`, `USKR`, `USMA`,
  `USOM`, `USPA`, `USPE` and `USSG`. Each has an alias with `reason: moved` and
  `target_dataset: trade_agreements`. `USCR` was the US–Costa Rica part of CAFTA-DR, so it is
  merged into `CAFTADR`. To find the agreements a country is party to, query the view:

  ```sql
  SELECT agreement_id, via FROM country_trade_agreements WHERE country_code = 'KR';
  ```

### Fixed

- `intblocks.partof` holds parent ids when the source YAML uses the object form
  `partof: {id: BIS, name: ...}`. Before, the build exported the object's keys, so 53
  intblocks (for example `FSB`, `AFRICACDC`, `ITLOS`, `OPCW`, `LVFO`) had
  `partof = ['id', 'name']`; `FSB` now has `['BIS']`. A list of `{id, name}` objects
  exports each `id` instead of the object's string form. No source YAML changes.
- `OSPAR`: `wikidata_id` pointed to Q7076363 (a post office building in Florida). It is now
  Q1928254, the Convention for the Protection of the Marine Environment of the North-East
  Atlantic, and the Wikipedia link points to the OSPAR Convention article.
- Trade agreement Wikidata id audit (22 November 2026): the 26 `wikidata_id` values set on
  `data/trade_agreements/` records, and the 54 that linked records read from their
  intblocks, were fetched from Wikidata and checked against each record's name, parties and
  type. Every id points to the right agreement item except `AUUK`: Q107271797 does not
  exist, and its correction to Q97356844 is listed under the intblock Wikidata id audit. No
  record had names or descriptions copied from a wrong item.
- `EUJP` (EU-Japan Economic Partnership Agreement) now links to the English Wikipedia
  article on the agreement, the enwiki sitelink of Q30749427, instead of the article on
  Japan–European Union relations.
- `UNIDO` checked on 2026-11-22 against the UN Treaty Collection status of the UNIDO
  Constitution (chapter X-9). The roster had 189 members, all listed as `member`. It now has 174
  members, the parties the depositary records, and 11 former members with the dates their
  withdrawal took effect: Canada, the United States, Australia, Lithuania, New Zealand, France,
  Portugal, Belgium, Denmark, Greece and Slovakia.
  - Remove Brunei, Estonia, Iceland, Latvia, Nauru, San Marino and Singapore, which never became
    parties.
  - Add Albania, the Marshall Islands and the State of Palestine.
  - The United Kingdom stays a member: it re-acceded on 9 November 2026 after leaving at the end
    of 2012.
  - Set `joined` on every entry to the date the Constitution entered into force for that State
    under Article 25(2).
- `UNIDO`: add the founding date (17 November 1966, General Assembly resolution 2152 (XXI)),
  `development` blocktype, recognition_status, secretariat, named official_documents and notes
  on the organs and Directors General. Move the headquarters coordinates to the Vienna
  International Centre, fix the Russian name and acronyms, replace the generic tags and topics,
  and add source-backed provenance.
- Wikidata id audit (22 November 2026): every intblock `wikidata_id` was fetched from
  Wikidata and checked against the record's name and type. 54 records pointed to the wrong
  item, a missing item or a redirect. Each corrected record also gets the matching
  `type: wikidata` link and a `wikidata_id` provenance entry for the new item.
  Old id, new id, and what the old id was:
  - `ARTEMISACCORDS` (Artemis Accords): Q96341450 to Q94568413; Q96341450 is a 2020 article
    on diesel engine emissions.
  - `BANGKOK` (Treaty of Bangkok): Q7707000 to Q1395235; Q7707000 is a Ukrainian tennis
    player.
  - `BARCELONA` (Barcelona Convention): Q808430 to Q2118997; Q808430 is a crater on Mars.
  - `CTBT` (Comprehensive Nuclear-Test-Ban Treaty): Q192088 to Q521306; Q192088 is Eton
    College.
  - `EIB` (European Investment Bank): Q152096 to Q192247; Q152096 is Sainsbury's.
  - `ESM` (European Stability Mechanism): Q2040462 to Q1130098; Q2040462 is the Meath West
    Dáil constituency.
  - `FOCONLINE` (Freedom Online Coalition): Q5504594 to Q17024071; Q5504594 is fringe
    benefits tax.
  - `GGGI` (Global Green Growth Institute): Q5533568 to Q12586353; Q5533568 is a ward in
    Hastings.
  - `LIC` (Low income): Q28035133 to Q25450947 (World Bank low income countries);
    Q28035133 is a Romanian politician.
  - `MSF` (Médecins Sans Frontières): Q37685 to Q49330; Q37685 is Jurong Falls.
  - `NAIROBI` (Nairobi Convention): Q6960080 to Q2996268; Q6960080 is a Wikimedia category.
  - `OFID` (OPEC Fund for International Development): Q7074800 to Q392787; Q7074800 is a
    Canadian publisher.
  - `PEPFAR`: Q1191982 to Q3402412; Q1191982 is mariculture.
  - `RAROTONGA` (Treaty of Rarotonga): Q7835003 to Q1760687; Q7835003 is transport in
    Jersey.
  - `TPNW` (Treaty on the Prohibition of Nuclear Weapons): Q27961877 to Q28130514;
    Q27961877 is a football club.
  - `UNAIDS`: Q781014 to Q588982; Q781014 is Aubusson tapestry.
  - `UNCLOS`: Q19989 to Q216996; Q19989 is a Linkin Park single.
  - `UNHCR`: Q15768 to Q132551; Q15768 is sodium bromide.
  - `ASEANPLUS3` (ASEAN Plus Three): Q483654 to Q1323760; Q483654 is Sunni Islam.
  - `BUDCONV` (Budapest Convention on Cybercrime): Q223800 to Q1093069; Q223800 is the
    Houston disambiguation page.
  - `CILSS`: Q1419931 to Q1114955; Q1419931 is Niemann-Pick disease.
  - `CISG`: Q202027 to Q1196344; Q202027 is the cornet.
  - `COVAX`: Q101437219 to Q99360983; Q101437219 is a street in Eberswalde.
  - `EASTASIASUMMIT` (East Asia Summit): Q618666 to Q542549; Q618666 is a Swiss glacier.
  - `G24` (Group of 24): Q18048978 to Q1589222; Q18048978 is the human gene LACTB.
  - `GATT`: Q192713 to Q194284; Q192713 is a commune in Lozère.
  - `GHSA` (Global Health Security Agenda): Q22022249 to Q104846388; Q22022249 is a 1928
    college football season.
  - `IPBES`: Q3156270 to Q1666088; Q3156270 is a place in Madagascar.
  - `ITC` (International Trade Centre): Q315306 to Q1184878; Q315306 is the German
    Schutzpolizei.
  - `NDPHS` (Northern Dimension Partnership in Public Health and Social Well-being):
    Q17021727 to Q7058307; Q17021727 is a fictional TV character.
  - `REFUGEECONVENTION` (1951 Refugee Convention): Q193430 to Q60433; Q193430 is
    heterocyclic compound.
  - `REFUGEEPROTOCOL` (1967 Refugee Protocol): Q392278 to Q60468; Q392278 is a lake in
    France.
  - `UNCTAD`: Q192710 to Q182000; Q192710 is the Malayan tapir.
  - `UNICEF`: Q142489 to Q740308; Q142489 is the gigabit interface converter.
  - `UNIDROIT`: Q376658 to Q1192641; Q376658 is a Chicago skyscraper.
  - `UNODC`: Q188307 to Q636107; Q188307 is The Salvation Army.
  - `VISTA`: Q924241 to Q1136157; Q924241 is Vista, California.
  - `ICPE` (International Center for Promotion of Enterprises): Q85787929 to Q6049045;
    Q85787929 is an Indian institute for small enterprises.
  - `BBNJ` (High Seas Treaty): Q120432689 to Q48780688; Q120432689 redirects to an
    American economist.
  - `STATELESS1954` (1954 Statelessness Convention): Q1783482 to Q5166243; Q1783482 is a
    mathematical theorem.
  - `STATELESS1961` (1961 Statelessness Convention): Q1783494 to Q5166303; Q1783494 is a
    disambiguation page.
  - `V20` (Vulnerable Twenty Group): Q30943971 to Q141737207; Q30943971 is a Chinese
    person.
  - `WESTERNBLOC` (Western Bloc): Q153045 to Q1507074; Q153045 is an asteroid.
  - `GPAI` (Global Partnership on Artificial Intelligence): Q97185282 to Q105730365;
    Q97185282 is a 1988 animated film.
  - `IAPH` (International Association of Ports and Harbors): Q6048000 to Q17081446;
    Q6048000 is a legal concept.
  - `DEPA` (Digital Economy Partnership Agreement): Q104830867 to Q104880620; Q104830867
    does not exist.
  - `PELINDABA` (Treaty of Pelindaba): Q4691025 to Q1468283; Q4691025 does not exist.
  - `GFCE` (Global Forum on Cyber Expertise): Q30337375 to Q142168082; Q30337375 does not
    exist.
  - `AUUK` (Australia–United Kingdom Free Trade Agreement, now in the trade agreements
    registry): Q107271797 to Q97356844; Q107271797 does not exist.
  - `CCAMLR`: Q97382426 to Q16184543; Q97382426 redirects to Q16184543.
- No Wikidata item exists for 4 records, so their wrong ids are removed and the records are
  listed in `data/schemas/wikidata_exclusions.yaml`: `TIMBI` (Q22702079, a river in the
  Central African Republic), `ECTEL` (Q5329555, a railway workshop in New Zealand), `ALLPI`
  (Q106518178, a Polish rapper) and `ABIDJAN` (Q4666000, which does not exist).
- 105 names copied from the wrong items are removed from `other_names` and `acronyms` in 23
  records, for example "The Salvation Army" from `UNODC`, "Sunni Islam" from `ASEANPLUS3`
  and "Houston" from `BUDCONV`.
- Descriptions copied from the wrong items are rewritten for `UNAIDS`, `UNHCR`, `G24`,
  `ITC`, `UNCTAD`, `UNICEF` and `UNODC` (for example, `UNHCR` was described as a chemical
  compound).
- Wikipedia links: `BBNJ` now links to High Seas Treaty and `CILSS` to the existing article
  title. Links to articles that do not exist are removed from `V20`, `GFCE`, `ECTEL` and
  `ALLPI`.

### Data changes since the previous release

- Countries: 256 → 256 records
- Intblocks: 1538 → 1581 records; added `ACAP`, `ACWL`, `APIII2005`, `ATACONVENTION`, `AZTMTR`, `BEPSMLI`, `BOLG`, `BUNKERS2001`, `CCAS`, `CDE1960`, `COEANTIDOPING`, `COELAUNDERING1990`, `COSTINFRA`, `CSC1972`, `D8PTA`, `DPGA`, `DRIFTNETCONVENTION`, `EAEUCN`, `EAEUIR`, `EAEURS` and 58 more; removed `ANZCERTA`, `AUINDIA`, `AUUAE`, `AUUK`, `CETA`, `CHAFTA`, `CNEC`, `CNKR`, `CNNI`, `CNRS`, `EUCENTRALAFRICAEPA`, `EUJP`, `EUKR`, `EUNZ`, `EUSG`, `EUUA`, `EUUK`, `EUVN`, `INUAE`, `UKIN` and 15 more; 65 changed
- Blocktypes: 83 → 83 records
- Membership edges: 69142 → 72461; 3396 added, 77 removed, 455 changed
- New intblocks aliases: `ANZCERTA`, `AUINDIA`, `AUUAE`, `AUUK`, `CETA`, `CHAFTA`, `CNEC`, `CNKR`, `CNNI`, `CNRS`, `EUCENTRALAFRICAEPA`, `EUJP`, `EUKR`, `EUNZ`, `EUSG`, `EUUA`, `EUUK`, `EUVN`, `INUAE`, `UKIN` and 15 more
- Schema (minor): table country_trade_agreements added
- Schema (minor): table trade_agreement_parties added
- Schema (minor): table trade_agreements added
- Schema (minor): column intblocks_aliases.target_dataset added

## [4.4.0] - 2026-11-22

### Added

- Two more artificial intelligence records with `artificial_intelligence`, checked on
  2026-11-22:
  - `SANTODOMINGOAIDECLARATION` (Santo Domingo Declaration, third ministerial summit on the
    ethics of AI in Latin America and the Caribbean, 26 June 2026), a `regional` record. The
    published text has a placeholder instead of the list of countries, so only the Dominican
    Republic (host and new chair of the regional working group) and Uruguay (outgoing chair)
    are listed. Sources: AGESIC and the text on UNESCO's site.
  - `IRAISE` (International Research-driven Alliance for AI Serving Every Child, formerly the
    Beneficial AI for Children Coalition, February 2025), a `policy_forum` with `human_rights`:
    nine governments. Source: the Paris Peace Forum.
- Two more artificial intelligence records with `artificial_intelligence`, checked on
  2026-11-22:
  - `AIPFD` (AI Partnership for Defense, the forum of defence institutions convened by the US
    Department of Defense since September 2020), a `policy_forum` in `military`: 13 founding
    nations and Germany, the Netherlands and Singapore from May 2021. Source: DoD Joint AI
    Center and CDAO releases, cited from Internet Archive copies.
  - `AIHUBSD` (AI Hub for Sustainable Development, co-led by Italy and UNDP and opened in Rome
    on 20 June 2025), a `regional` `policy_forum`: the two co-leads and 18 African partner
    countries. Sources: the AI Hub website and MIMIT.
- Twenty artificial intelligence declarations, coalitions and partnerships with
  `artificial_intelligence` and the signatory lists of their hosts, checked on 2026-11-22:
  - `BLETCHLEYDECLARATION` (Bletchley Declaration, AI Safety Summit 2023, Wikidata
    Q130201327): 29 countries and the EU, with New Zealand from October 2024. Source:
    the UK government.
  - `SEOULAIDECLARATION` (Seoul Declaration for Safe, Innovative and Inclusive AI, 2024):
    10 countries and the EU. Sources: the UK government and the Korean Ministry of
    Foreign Affairs.
  - `SEOULAIMINISTERIAL` (Seoul Ministerial Statement, 2024): 27 countries and the EU.
    Source: the UK government.
  - `PARISAISTATEMENT` (Statement on Inclusive and Sustainable AI for People and the
    Planet, AI Action Summit 2025, Wikidata Q133259297): 63 countries, the African Union
    Commission and the EU. Source: the French Presidency; later signatories are dated
    from archived copies of its page.
  - `PARISAIWEAPONSDECLARATION` (Paris Declaration on Maintaining Human Control in AI
    Enabled Weapon Systems, 2025), in `armscontrol`: 27 states. Source: the French
    Presidency.
  - `NEWDELHIAIDECLARATION` (AI Impact Summit Declaration, New Delhi, 2026): 90 countries,
    the EU and IFAD. Sources: the Press Information Bureau and the Ministry of External
    Affairs of India.
  - `REAIMCALLTOACTION` (REAIM Call to Action, The Hague, 2023), in `armscontrol`: 57
    states and Palestine. Source: the Netherlands government.
  - `REAIMPATHWAYS` (REAIM 2026 Pathways to Action, A Coruña), in `armscontrol`: 45
    states. Source: the Spanish Ministry of Foreign Affairs.
  - `PARISAISAFETYCALL` (Paris Call for AI Safety and Security, 9 November 2026): 19 states;
    the 11 companies and 11 civil society signatories are named in `notes`. Source: the
    French Presidency.
  - `CHILDRENAICOALITION` (Coalition for Children's Rights and Protection in the Age of AI,
    July 2026), a `policy_forum` with `human_rights`: the 18 founding states and Australia.
    Source: the French Ministry for Europe and Foreign Affairs. The coalition has since
    reported 23 states without naming them, so the roster is incomplete.
  - `AFRICAAIDECLARATION` (Africa Declaration on Artificial Intelligence, Kigali, April
    2025), a `regional` record: 52 African countries and the African Union. Source: the
    official text published by C4IR Rwanda.
  - `CURRENTAI` (Current AI, Wikidata Q132753289), a `non_state_organization` headquartered
    in Paris: its ten partner countries, with status `partner`. Source: currentai.org.
  - `SANTIAGOAIDECLARATION` (Santiago Declaration to Promote Ethical AI in Latin America and
    the Caribbean, October 2023), a `regional` record: 20 countries. Source: InvestChile; the
    declaration text has no signatory block.
  - `NORDICBALTICAIDECLARATION` (AI in the Nordic-Baltic Region, Stockholm, 14 May 2018), a
    `regional` record: eight states, the Faroe Islands and the Åland Islands. Source: the
    signed copy published by the Government of Iceland.
  - `CARTAGENAAIDECLARATION` (Cartagena de Indias Declaration on AI governance, ecosystems
    and education, August 2024), a `regional` record: 17 countries. Source: MinTIC Colombia.
  - `MONTEVIDEOAIDECLARATION` (Montevideo Declaration on a regional approach to AI
    governance, 4 October 2024, Wikidata Q133894914), a `regional` record: 15 approving
    countries and three later adherents (Bolivia, Costa Rica, Dominica). Source: the text
    published by AGESIC.
  - `REAIMBLUEPRINT` (REAIM Blueprint for Action, Seoul, 10 September 2024), in
    `armscontrol`: 41 of the 61 endorsing states. The official list was only on the closed
    summit website, so each state is sourced separately from the Korea Herald (citing the
    Korean Foreign Ministry), RSIS, Canada's First Committee statement and national replies
    to UN General Assembly resolution 79/239. 18 EU member states rest on the EU's
    collective statement only and carry a `note`.
  - `SUSTAINABLEAICOALITION` (Coalition for Sustainable AI, February 2025), a `policy_forum`
    with `environment`: 15 supporting governments and five intergovernmental organisations
    (UNEP, ITU, UNDP, IEA, GGGI), with status `participant`. Sources: the coalition's site
    and the French Ministry of Ecological Transition.
  - `HAMBURGAIDECLARATION` (Hamburg Declaration on Responsible AI for the SDGs, 2 June 2025):
    eight states, each through a ministry, and the EAC, UNDP and UNICEF. Source: BMZ
    Digital.Global and the declaration's list of endorsements.
  - `AICAPACITYFRIENDS` (Group of Friends for International Cooperation on AI
    Capacity-building, UN New York, December 2024), a `policy_forum`: only its co-chairs, China
    and Zambia, because the group publishes no member list. Source: the Permanent Mission of
    China to the UN.
- `EUROAREA` (euro area, Wikidata Q8268), a `currency` record for the 21 EU member states
  that use the euro, with adoption dates from the ECB roster and `partof: EU`, checked on
  2026-11-22. It shares Q8268 with its World Bank mirror `EMU`.
- Six Hague Conference on Private International Law conventions as `legal` treaty records,
  with Contracting Parties from the HCCH status tables (checked on 2026-11-22):
  `APOSTILLE` (Apostille Convention, 1961), `SERVICE1965` (Service Convention),
  `EVIDENCE1970` (Evidence Convention), `CHILDABDUCTION1980` (Child Abduction Convention),
  `ADOPTION1993` (Intercountry Adoption Convention) and `CHILDPROTECTION1996` (Child
  Protection Convention).
- Eleven Council of Europe treaties, with parties from the Netherlands Treaty Database
  (checked on 2026-11-22): `MAAC` (Convention on Mutual Administrative Assistance in Tax
  Matters), `TRANSFERSENTENCED` (ETS 112), `LISBONRECOGNITION` (Lisbon Recognition
  Convention), `CONVENTION108` (data protection), `LANZAROTE`, `COETRAFFICKING` (CETS 197),
  `ECPT` (prevention of torture), `ISTANBULCONVENTION`, `FCNM`, `ESC` (European Social
  Charter, 1961) and `ESCREVISED` (European Social Charter, revised 1996).
- Four UNESCO conventions, with parties from the Netherlands Treaty Database (checked on
  2026-11-22): `ANTIDOPING2005` (International Convention against Doping in Sport),
  `INTANGIBLEHERITAGE` (2003 Convention), `CULTURALEXPRESSIONS` (2005 Convention) and
  `UNESCO1970` (illicit traffic in cultural property).
- Six IMO instruments, with Contracting States from the IMO Status Book of 30 October 2026:
  `TONNAGE1969`, `SUA1988`, `OPRC1990`, `AFS2001`, `LC1972` (London Convention) and `LP1996`
  (London Protocol).
- Five IAEA conventions, the 1977 Additional Protocols to the Geneva Conventions and the 1925
  Geneva Protocol, with parties from the Netherlands Treaty Database (checked on 2026-11-22):
  `CPPNM`, `CNS` (Convention on Nuclear Safety), `JOINTCONVENTION` (spent fuel and radioactive
  waste), `EARLYNOTIFICATION`, `ASSISTANCECONVENTION`, `API1977`, `APII1977` and
  `GENEVAPROTOCOL1925`. Organizations that are parties (EURATOM, FAO, WHO, WMO) are listed as
  `organization` entries.
- Three CMS daughter agreements and three river basin commissions, with parties from the Netherlands
  Treaty Database (checked on 2026-11-22): `AEWA` (African-Eurasian Migratory Waterbirds),
  `EUROBATS` (European bats), `WADDENSEALS` (Wadden Sea seals), `ICPR` (International Commission
  for the Protection of the Rhine), `IMC` (International Meuse Commission) and `SCHELDTCOM`
  (International Scheldt Commission).
- `BIE` (Bureau International des Expositions, 184 Member States, with accession dates from the BIE),
  `UPC` (Unified Patent Court, 18 Contracting Member States) and `TSCG` (Treaty on Stability,
  Coordination and Governance, the Fiscal Compact, 27 parties).
- `PHEUR` (Convention on the Elaboration of a European Pharmacopoeia, 39 states and the EU), `EMBC`
  (European Molecular Biology Conference, 32 Member States and 3 associate members) and `IARC`
  (International Agency for Research on Cancer, 28 Participating States).
- Seven historical `currency` records with dated former members, checked on 2026-11-22
  against treaty texts, central bank histories and UK archive records: `LMU` (Latin
  Monetary Union, Wikidata Q613420), `SMU` (Scandinavian Monetary Union, Q60812), `EACB`
  (East African Currency Board, Q5327653), `WACB` (West African Currency Board,
  Q134599375), `MALAYABORNEOCURRENCYBOARD` (Board of Commissioners of Currency, Malaya and
  British Borneo; currency item Q2407759), `BCCB` (British Caribbean Currency Board;
  currency item Q942092) and `ECCA` (Eastern Caribbean Currency Authority, no Wikidata
  item).
- Lineage `BCCB` → `ECCA` → `ECCU`: `ECCU` gains `predecessor: ECCA`.
- `TLATELOLCO` (Treaty of Tlatelolco, Wikidata Q1567567), the treaty record for the Latin
  American and Caribbean nuclear-weapon-free zone: 33 States Parties with deposit dates from
  the UNODA Treaties Database, checked on 2026-11-22. `OPANAL` is now `partof` it.
- `PTBT` (Partial Nuclear Test Ban Treaty, Wikidata Q278960): 125 States Parties, each with the
  earliest deposit date at any of the three depositaries, from the UNODA Treaties Database,
  checked on 2026-11-22.
- `CANWFZ` (Central Asian Nuclear-Weapon-Free Zone Treaty, Wikidata Q501371): 5 States Parties
  with deposit dates from the UNODA Treaties Database, checked on 2026-11-22.
- `AFCONE` (African Commission on Nuclear Energy, Wikidata Q2986403), an `intergovernmental_body`
  `partof` `PELINDABA` that lists the 12 States Parties currently elected to the Commission.
- `UNSCEAR` (Wikidata Q2297408), an `intergovernmental_body` `partof` `UN`, established by General
  Assembly resolution 913 (X) of 3 December 1955: 31 member states with the year each was designated.
- `CONFDISARMAMENT` (Conference on Disarmament, Wikidata Q1931500): 65 member states by regional
  group, from UNODA. The id avoids `CD`, the ISO code of the Democratic Republic of the Congo.
- `PARISNUCLEAR` (Paris Convention on Third Party Liability in the Field of Nuclear Energy,
  Wikidata Q7137274): 16 Contracting Parties with ratification dates. The roster comes from the
  Wikipedia table of the OECD NEA ratification status, because oecd-nea.org blocks automated access.
- Nuclear forums and initiatives, each with its official roster checked on 2026-11-22:
  - `GIF` (Generation IV International Forum, Q1123284): the seven states and Euratom that have
    signed the 2025 Framework Agreement.
  - `IFNEC` (International Framework for Nuclear Energy Cooperation, Q3366107): 33 Participant
    countries, 32 observer countries and 5 observer organizations.
  - `PSI` (Proliferation Security Initiative, Q1141011): 116 endorsing states.
  - `GPWMD` (Global Partnership Against the Spread of Weapons and Materials of Mass Destruction,
    Q5570539): 30 countries and the EU.
  - `IPNDV` (International Partnership for Nuclear Disarmament Verification): 32 partner states
    and the EU. It has no Wikidata item and is listed in `wikidata_exclusions.yaml`.
  - `NPDI` (Non-Proliferation and Disarmament Initiative, Q7048793): 12 members.
  - `NEWAGENDA` (New Agenda Coalition, Q3875176): 6 members. The id avoids `NAC`, which is the
    World Bank North America aggregate.
- IAEA regional agreements and the Arab Atomic Energy Agency, each with its official roster checked on
  2026-11-22:
  - `RCA` (Asia-Pacific, 22 Government Parties).
  - `ARCAL` (Latin America and the Caribbean, 21 members).
  - `ARASIA` (Arab states in Asia, 10 States Party).
  - `AAEA` (Arab Atomic Energy Agency, Q56376750): an `igo` `partof` `LAS` with 14 member states.

  `RCA`, `ARCAL` and `ARASIA` have no Wikidata item and are listed in
  `wikidata_exclusions.yaml`.
- `HCOC` (Hague Code of Conduct against Ballistic Missile Proliferation, Q1566329): 145 subscribing
  states with subscription dates.
- `TRIPLENUCLEAR` (Declaration to Triple Nuclear Energy, Q139072661): the 39 endorsing countries
  listed by the World Nuclear Association (updated 2 October 2026), including Kosovo (`XK`).
- `NUCLEARARMED`, a `reference_enumeration` of the nine nuclear-armed states counted by the SIPRI
  Yearbook 2026. It complements `NWS`, the five NPT nuclear-weapon States.
- 66 technical organizations found missing in the `technical` blocktype audit, each with an
  official roster or `membership_applicability: not_applicable`, checked on 2026-11-22:
  - Metrology and standards: `BIPM`, `EURAMET`, `COOMET`, `APMP`, `SIM`, `AFRIMETS`,
    `GULFMET`, `GSO`, `AIDSMO`, `SARSO`, `ISSNIC`.
  - Accreditation: `GLOBALACI` (Global Accreditation Cooperation, formed on 1 January 2026
    from IAF and ILAC), the historical `ILAC`, `EA`, `APAC`, `IAAC`, `AFRAC`, `ARAC`. `IAF`
    now names `GLOBALACI` as its successor.
  - Aviation and maritime: `ASECNA`, `SRVSOP`, `RFIR`, `IOPCFUNDS`, `MOSELLECOM`, and the port
    State control regimes `PARISMOU`, `TOKYOMOU`, `CARIBMOU`, `MEDMOU`, `BSMOU`, `ABUJAMOU`,
    `RIYADHMOU`.
  - Telecom, broadcasting and digital: `RCCCOMM`, `CITEL`, `ABU`, `ASBU`, `DCO`, and the
    regulator networks `CRASA`, `WATRA`, `AREGNET`, `BEREC`, `REGULATEL`, `FRATEL`,
    `EAPEREG`, `ASMG`.
  - Nuclear and power grids: `EURATOM`, `ENSREG`, `WENRA`, `FNCA`, `ABACC`, `GCCIA`, `CRIE`.
  - Meteorology, Earth observation and geospatial: `GEO`, `AGRHYMET`, `ICPAC`,
    `TYPHOONCOMMITTEE`, `WMOESCAPPTC`, `UNGGIM`, `RCMRD`, `AFRIGIST`, `PAIGH`.
  - Scientific and technical cooperation: `ICGEB`, `COMSTECH`, `GOIC`, `CYTED`, `IIR`,
    `CIEC`, `PIARC`.
- Seven more technical bodies whose own sites could not be read, compiled from Wayback Machine
  copies of their official pages, founding texts and IGO documents: `SMARTAFRICA`, `COMELEC`,
  `ACMAD`, `EMERG`, `IOMOU`, `VINADELMAR`, and the historical `ECOMET` (dissolved 2023), which
  `EUMETNET` now names as its predecessor.
- `CCASG` lists `GOIC` and `GSO` among its suborganizations.
- 27 technical multilateral treaties as `treaty_body` records, each with its states-parties
  roster from the depositary, checked on 2026-11-22:
  - WIPO-administered (`patent`, roster from WIPO Lex): `PARIS1883` (Paris Convention),
    `BERNE1886` (Berne Convention; `BERNECONVENTION` stays the wildlife convention), `PCT`,
    `MADRIDPROTOCOL`, `HAGUEAGREEMENT`, `BUDAPESTTREATY`, `LISBONAGREEMENT` (1958 Agreement),
    `MARRAKESHVIP`, `WCT` and `WPPT`.
  - IMO (`maritime`, roster from the IMO Status Book of 30 October 2026): `STCW`, `COLREG`,
    `LL1966`, `SAR1979`, `FAL1965`, `BWM`, `HKC` (in force since 2025-06-26) and `CLC1992`
    (the 1992 Protocol to the Civil Liability Convention).
  - ICAO (`aviation`, roster from the ICAO lists of parties): `MONTREAL1999`, `CAPETOWN2001`
    (count checked against the UNIDROIT status page), `IASTA`, `TOKYO1963`, `HAGUE1970` and
    `MONTREAL1971`.
  - WCO (`trade`, roster from the WCO positions as regards ratifications): `HSCONVENTION`,
    `RKC` (Revised Kyoto Convention) and `ISTANBUL1990` (Convention on Temporary Admission).
- The European Union, OAPI and the Eurasian Patent Organization are listed as
  `type: organization` parties where the depositary lists them. Signatories that have not
  ratified are left out.
- `CLC1992` and `RKC` have `wikidata_exclusions.yaml` entries, because their Wikidata items
  describe the unamended 1969 and 1973 conventions.
- The Maritime Labour Convention, 2006 is not added: the ILO NORMLEX ratification page could
  not be read.

### Changed

- A push to `main` runs the `validate` workflow on Python 3.13 only, the leg with the data
  checks and the uploaded reports. Its pull request already passed all three legs.
- A pull request that changes only `openspec/`, `dev/` or `website/` skips the build, the
  tests and the data checks in `validate`. It still runs the Markdown link check, and its
  `validate (3.11/3.12/3.13)` legs still report as required checks.
- The `validate` workflow installs dependencies with `uv pip install` instead of `pip`,
  which saves 15–25 seconds per leg.
- `OECS` moved from `eccurr/` to `economic/` with `blocktype` `[economic, political,
  currency, eccurr]`. `CEMAC` and `UEMOA` now carry `[customs, currency, cuscurr]`.
  `list_contains(blocktype, 'currency')` now also returns these three records.
- `SCHENGENAREA` moved from `customs/` to `travel/` (`blocktype: [travel]`): Schengen is a
  passport-free travel area, not a customs union. `UNASUR` no longer carries `customs`.
  Record IDs do not change.
- `EMU` (World Bank Euro area aggregate) adds Bulgaria, which joined on 1 January 2026, as
  the World Bank API lists it.
- The `currency` and `customs` scope notes state when an organization adds `currency` as a
  secondary blocktype.
- YAML is read with libyaml's C parser (`CSafeLoader`) through
  `internacia_builder.yaml_io.safe_load`, about eight times faster than `yaml.safe_load`.
  Writing stays on PyYAML's Python emitter, so every export is byte-for-byte the same.
  `ruff` now rejects `yaml.safe_load` (`TID251`).
- `INTERNACIA_ZSTD_LEVEL` (1–22) sets the zstd level of the `*.zst` and Parquet exports. The
  default stays 22, which releases always use. The `validate` workflow builds at 3, which
  nearly halves each build.
- In the `validate` workflow, the checks that do not depend on the Python version (dependency
  audit, oldest-DuckDB read, data, documentation, staged-artifact and quality checks) run on
  Python 3.13 only, and are no longer repeated on every leg. The 3.12 leg keeps coverage and
  the SDK contract suite, and 3.11 keeps the reproducibility check. Each Python version still
  builds its own artifacts and runs the whole test suite. The CI artifacts are now named
  `validation-reports` and `quality-report`, without a `-py3.x` suffix.
- `CMA` gains `previous_names` (Rand Monetary Area, 1974–1986) and `joined` dates: Lesotho,
  Eswatini and South Africa on 5 December 1974, Namibia on 6 February 1992. Its `founded`
  date and `active_period.start` become 5 December 1974, the Rand Monetary Area Agreement
  (was July 1986), as Wikidata Q1116201 treats the two areas as one entity.
- Nuclear arms-control treaties `NPT`, `CTBT`, `TPNW`, `PELINDABA`, `RAROTONGA`, `BANGKOK`
  and `SEABEDTREATY` move from `agreement` to `armscontrol` as primary blocktype, as the
  `agreement` description requires. They keep `agreement` and add `nuclear`.
- `OPANAL` (from `energy`) and `AG`, the Australia Group (from `political`), move to
  `armscontrol`.
- The `nuclear` blocktype now covers nuclear security and non-proliferation, not only energy
  and safety. It is added as a secondary tag to `IAEA`, `CTBT`, `CTBTO`, `KEDO`, `OPANAL`,
  `GICNT`, `NSS`, `JCPOA`, `NWS`, `NWFZ` and the nuclear-weapon-free zone treaties. `NSS`,
  `ISTC` and `STCU` also gain `armscontrol`.
- `scope_category`: `OPANAL` is an `igo` established by Article 7 of the treaty, no longer a
  `treaty_body`. `NWS` and `NWFZ` are `reference_enumeration`, applying the reviewed decisions
  in `scope_category_nonformal_30.yaml`.
- `technical` blocktype now also tags the six bodies whose `institutional_design.mandate`
  is `technical` (`ICAO`, `IMO`, `ITU`, `UPU`, `WIPO`, `WMO`), `IEC` (as `ISO` already
  was), and the technical-cooperation bodies `CFTC`, `CP` (Colombo Plan) and `SPC`, which
  also gains `scientific`.
- Primary blocktype moved to the domain the taxonomy notes prescribe: `SOLAS` to
  `maritime` (was `transport`), `NSG` and `ZANGGERCOM` to `armscontrol` (were `energy` and
  `forum`), `IPCC` to `climate` (was `research`), and `CP` to `development` (was
  `economic`). `MARPOL` adds `maritime`, `CEPT` adds `telecom`, `NEA`, `NSG` and
  `ZANGGERCOM` add `nuclear`, and `IPCC` adds `scientific`.

### Deprecated

- Blocktypes `eccurr` (replacements `economic`, `currency`) and `cuscurr` (replacements
  `customs`, `currency`) are deprecated and listed in `contract.json` `deprecated`. A
  blocktype never combines two other blocktypes. Queries on them return the same records
  (`OECS`; `CEMAC`, `UEMOA`) until they are removed in the next MAJOR release. Replacement
  queries: `list_has_all(blocktype, ['economic', 'currency'])` and
  `list_has_all(blocktype, ['customs', 'currency'])`.

### Fixed

- `ASEAN` gains its English acronym `ASEAN`, so consumers that label blocks by English
  acronym (as they do for `EU` and `EAEU`) no longer fall back to the full name.
- English acronyms for other formal IGOs that had none: `UNESCO`, `EUTELSAT`, `APA`,
  `IMCTC`, `CGIAR`, `International IDEA`, `EURONEST PA`, `NATO PA`, `AFRISTAT`, `OHADA`,
  `IFC-IOR`, `IMSC`, `ALBA`, `CONMEBOL` and `AMN`.
- `ASEAN` name casing: "Association of Southeast Asian Nations" (was "SouthEast"), also in
  the `BIMPEAGA` `partof` reference.
- `IAEA` listed 8 of its members. It now lists all 182 member states with membership dates
  (IAEA INFCIRC/2/Rev.94), North Korea as a former member (withdrew 1994) and Palestine as an
  observer.
- `CTBT` listed every signatory as a member. It now lists the 179 States Parties with deposit
  dates. The Russian Federation is a `former_member` since it withdrew its ratification on
  3 November 2023, and the 8 signature-only states are omitted, as for other treaties.
- `CTBTO` listed 195 states, including non-signatories (India, Pakistan, North Korea, Saudi
  Arabia, Syria and others). It now lists the 188 CTBT signatories that make up the
  Preparatory Commission, with signature dates.
- `CTBT` headquarters pointed to coordinates near Windsor, England, taken from Wikidata. It is
  now Vienna, the seat of the Organization under Article II of the treaty.
- `WANO` and `WNA`, now `non_state_organization`, no longer present countries with nuclear
  plants or member companies as member states. Their members are operators and companies, so
  the records have no country roster (`membership_applicability: not_applicable`).
- `ITER` listed its European Member as `EU` ("European Union (through Euratom)"), and `KEDO`
  listed it under the unresolved id `EAEC`. Both now reference the `EURATOM` record.
- `scope_category` was `igo` on records whose own `legal_status` says they are not
  intergovernmental organizations. Industry associations, NGOs and operator bodies are now
  `non_state_organization`: `WNA`, `WANO`, `WEC`, `IGA`, `IHA`, `WBA`, `WWEA`, `GEIDCO`,
  `FUTURECOAL`, `ENTSOE`, `NORDEL`, `NAERC` (NERC), `AICEP`, `IPC` and `POSTEUROP`.
  Forums and agency coordination groups without IGO personality are now `policy_forum`:
  `CEM`, `MI`, `IPEEC`, `EEHUB`, `NSG`, `CCSDS`, `CEOS` and `CGMS`. `IPCC`, a body of
  WMO and UNEP, is now `intergovernmental_body`.
- `IGAD`: Eritrea is a `former_member` (joined 1993, left 2025-12-12). IGAD acknowledged its
  withdrawal on 12 December 2025, so `membership_count` is now 7.
- `IGAD`: Sudan's entry notes its suspension on 20 January 2024 and its return on
  9 February 2026; it stays a `member`.
- `ISA` (International Solar Alliance): the roster grows from 9 to 114 current members, compiled
  from the Netherlands treaty database's parties tables for the Framework Agreement and its
  amendment, with ratification dates where shown. Brazil, which has signed but not ratified,
  is no longer listed as a member; the United States stays a `former_member`.
- `SOLAS` and `MARPOL` rosters follow the IMO Status Book, Vol. I, dated 30 October 2026.
  Both add Kyrgyzstan (`SOLAS` 169, `MARPOL` 163).
- `MARPOL` `joined` dates for Liberia, Mexico, the Netherlands, Poland, Spain, Sweden, the
  United Kingdom, the United States and Uruguay were all `2007-01-09`, which is Albania's date.
  They now carry each State's own date of signature or deposit.
- `SOLAS` `joined` for Monaco and Ukraine is now 1974-11-01, the date of their definitive
  signature, not the date the convention entered into force.

### Data changes since the previous release

- Countries: 256 → 256 records
- Intblocks: 1338 → 1538 records; added `AAEA`, `ABACC`, `ABU`, `ABUJAMOU`, `ACMAD`, `ADOPTION1993`, `AEWA`, `AFCONE`, `AFRAC`, `AFRICAAIDECLARATION`, `AFRIGIST`, `AFRIMETS`, `AFS2001`, `AGRHYMET`, `AICAPACITYFRIENDS`, `AIDSMO`, `AIHUBSD`, `AIPFD`, `ANTIDOPING2005`, `APAC` and 180 more; 89 changed
- Blocktypes: 83 → 83 records; 5 changed
- Membership edges: 58096 → 69142; 11126 added, 80 removed, 398 changed

## [4.3.0] - 2026-11-21

### Added

- Seven more `statistics` records, checked on 2026-11-21 (1318 intblocks):
  - `AITRS` (Arab Institute for Training and Research in Statistics, Amman, an `igo`): 22
    countries, whose national statistical offices are its members. Its own sources do not
    call it an organ of the League of Arab States, so `partof` is not set.
  - `UNSTATCOM` (United Nations Statistical Commission, `partof: ECOSOC`): the 34 members
    of 2026, from the UN Statistics Division list. `UNSC` is already the Security Council.
  - Five `intergovernmental_body` records with `membership_applicability: not_applicable`,
    as for `GCCPO`, so the parent's members are not copied: `GCCSTAT` (GCC-Stat, `CCASG`),
    `SESRIC` (`OIC`), `STATAFRIC` (AU Institute for Statistics, `AFUNION`), `ISSEA`
    (`CEMAC`) and `SIAP` (UN Statistical Institute for Asia and the Pacific; ESCAP has no
    record, so `partof` is not set).
- Seven `statistics` records, checked on 2026-11-21 (1311 intblocks). Before this, the
  blocktype held only `CISSTAT`.
  - `AFRISTAT` (Economic and Statistical Observatory of Sub-Saharan Africa, an `igo`): 22
    member states, with the 14 founders of 1993. Source: AFRISTAT's member-states page.
  - `AFRICANSTATISTICSCHARTER` (African Charter on Statistics, a `treaty_body`, in force since
    8 February 2015): 26 parties. Source: the AU status list of 19 September 2023. The AU uses
    no acronym for the Charter, so the id is descriptive.
  - `SDDSPLUS` (32 adherents), `SDDS` (48 subscribers) and `EGDDS` (110 participants): the
    three tiers of the IMF Data Standards Initiatives, as `reference_enumeration` records
    with `partof: IMF`. Source: the IMF DSBB. An economy appears in only one tier, as on
    DSBB, so the 32 SDDS Plus adherents are not repeated in `SDDS`.
  - `CES` (Conference of European Statisticians, an `intergovernmental_body` of UNECE): the
    56 UNECE member States and the 8 OECD members outside the region; Argentina, Brazil,
    Mongolia and the Philippines are `participant`. Source: UNECE's 2022 report to the UN
    Statistical Commission.
  - `ESS` (European Statistical System, a `policy_forum`): the EU-27 and the four EFTA
    States. Sources: Eurostat, EFTA and Regulation (EC) No 223/2009.
- `wikidata_exclusions.yaml` entries for `AFRICANSTATISTICSCHARTER`, `SDDSPLUS`, `EGDDS` and
  `CES`, which have no Wikidata item.
- `AH` (Asian Highway Network, Wikidata Q728802), a `project`/`transport` record for the ESCAP
  road network itself, checked on 2026-11-21 (1304 intblocks). It mirrors `TAR`: no country
  roster (`membership_applicability: not_applicable`), because the 32 countries the network
  crosses are not treaty parties. The 30 states parties stay on `ASIANHIGHWAY`.
- 12 international road, rail and transit-corridor records, checked on 2026-11-21 against
  depositary and official sources (1297 intblocks):
  - Treaties (`transport`, `agreement`; `treaty_body`): `ARABMASHREQRAILWAYS` (UNTC XI-C-4,
    12 parties), the ESCWA rail network agreement and sibling of `ARABMASHREQROADS` below,
    renamed "between Arab Countries" in 2016; `PANAMERICANHIGHWAY` (1936 convention, OAS B-19,
    12 ratifying states); `SCOROADTRANSPORT` (2014 SCO road transport agreement: the six
    founding parties plus IN, PK and BY); `GMSCBTA` (GMS Cross-Border Transport Facilitation
    Agreement, 6 parties); `QTTA` (1995 China–Kazakhstan–Kyrgyzstan–Pakistan transit
    agreement); `CHABAHAR` (2016 Afghanistan–India–Iran transit corridor agreement).
  - Corridor bodies (`transport`): `CCTTFA` (Central Corridor, 7 members with MW in 2023 and
    ZM in 2024), `LCTTFA` (Lobito Corridor, 3 members) and `ALCOMA` (Abidjan–Lagos Corridor,
    5 members), all `igo`, alongside `NCTTCA` below; `TKCS`
    (Trans-Kalahari Corridor, MoU of 3 members) and `CLRT` (Trans-Saharan Road Liaison
    Committee, 6 members), both `policy_forum`.
  - `GMS` (Greater Mekong Subregion Economic Cooperation Program, ADB-supported, 6 members;
    `project`, `policy_forum`).
  - Ten of them have no Wikidata item and are listed in `wikidata_exclusions.yaml`.
  The roads agreement (UNTC XI-B-33) is not added again: it is `ARABMASHREQROADS` below.
  `GMS` is the programme behind the `EWEC` corridor below.
  The Ashgabat Agreement is deferred: Qatar's status conflicts between sources, Pakistan's
  and Armenia's accessions are unconfirmed, and its 10-year term from 23 April 2016 ended
  in April 2026 with no extension found. The older Abidjan–Lagos Corridor Organization
  (ALCO) is a different body and is not added. None of the new records carries corridor
  route roles.
- `ARABMASHREQROADS` (Agreement on International Roads in the Arab Mashreq, ESCWA, Beirut
  2001; in force 19 October 2003), the treaty behind the Arab Mashreq International Road
  Network: 13 States parties from the UN Treaty Collection table XI-B-33, checked on
  2026-11-21 (1284 intblocks). Oman is served by the network but is not a party.
- `NCTTCA` (Northern Corridor Transit and Transport Coordination Authority; `transport`, `igo`),
  checked on 2026-11-21 (1283 intblocks): BI, CD, KE, RW, SS (since December 2012) and UG, with
  its Permanent Secretariat in Mombasa. Source: the authority's official site. It has no route
  roles because the corridor branches from Mombasa to several landlocked countries instead of
  running between two ends.
- `EWEC` (East–West Economic Corridor of the Greater Mekong Subregion programme), a transport
  corridor record with route roles, checked on 2026-11-21 (1285 intblocks): MM and VN
  `terminal`, TH and LA `transit`. Sources: JICA and IDE-JETRO for the route from Mawlamyine
  to Da Nang and the 1998 Eighth GMS Ministerial Conference. Cambodia is a GMS member but is not
  on the route, so it is not listed. ADB and GMS Secretariat pages could not be read (access
  blocked), so no ADB page is cited.
- `CICPEC` (China-Indochina Peninsula Economic Corridor, formerly the Nanning-Singapore
  Economic Corridor), a Belt and Road economic corridor with `partof: BRI` (1298 intblocks).
  Its eight `participant` countries are CN, VN, LA, KH, TH, MM, MY and SG. Sources: Xinhua
  Silk Road and Beijing Review. `BRI` lists it in `suborganizations`.
- `scripts/check_min_duckdb.py` reads every table and view of `internacia.duckdb` on the
  running DuckDB. CI runs it with `min_duckdb` from `contract.json` (Python 3.12 job).
- Blocktype `artificial_intelligence` (83 blocktypes), a secondary tag for artificial
  intelligence governance, safety and cooperation, including partnerships on AI compute and
  semiconductor supply chains. Four records take it as an additional blocktype, with no
  directory move: `WAICO`, `PAXSILICA`, `CHIP4` and `GPAI`. The `digital` scope note now
  points AI bodies to the new key.
- Five artificial intelligence records with `artificial_intelligence`, checked on 2026-11-21
  (1303 intblocks):
  - `NAAIMES` (International Network for Advanced AI Measurement, Evaluation and Science, formerly
    the International Network of AI Safety Institutes): 9 countries and the EU, all founding members
    from November 2024. Sources: NIST and the UK government.
  - `HAIPFRIENDS` (Hiroshima AI Process Friends Group): 69 countries and the EU, with join dates from
    the Japanese Ministry of Internal Affairs and Communications.
  - `OECDAIPRINCIPLES` (OECD Recommendation of the Council on AI, OECD/LEGAL/0449): 51 adherents
    (38 OECD members, 12 non-members and the EU). Source: the OECD Legal Instruments database.
  - `MILITARYAIDECLARATION` (Political Declaration on Responsible Military Use of AI and Autonomy):
    58 endorsing states on the U.S. Department of State list dated 27 November 2024.
  - `COEAICONVENTION` (Council of Europe Framework Convention on AI, CETS No. 225): not in force; the
    parties are the EU and Bosnia and Herzegovina, and the 19 other signatories are named in `notes`.
    Source: the Netherlands treaty database, because the Council of Europe Treaty Office chart could
    not be read automatically.
  The UN Group of Friends for International Cooperation on AI Capacity-building is deferred: it
  publishes no member list.
- `includes[].joined` dates for 21 tier-1 organizations (`data/watch/rosters.yaml`) that had
  none: 891 entries, checked on 2026-11-21. Affected organizations: UN, EU, NATO, AFUNION,
  ECOWAS, OECD, WTO, COMMONWEALTH, OIC, G-20, G7, SCO, CIS, LAS, CELAC, SAARC, APEC, OAS,
  CARICOM, SADC and COE. Each date comes from the organization's official member list and
  keeps the precision of that list. Where the official list could not be read, the date comes
  from an archived copy of the organization's own page (OAS, LAS) or from government treaty
  registers (OECD). Four entries stay undated because their official sources conflict: AFUNION
  KE and AO, and CIS AZ and MD. The reviewed values are in `data/schemas/includes_joined_tier1.yaml`.
  `scripts/backfill_includes_joined.py` applies them. It runs as a dry run by default and
  stops on any conflict. It adds provenance and sets `last_verified`.
- 20 linear transport corridors with route roles (`transport`, `corridor`), checked on 2026-11-21
  against government, intergovernmental, operator and project-finance sources. Each is in the
  reviewed manifest `data/schemas/include_roles_pilot.yaml`:
  - Asia: `CPEC` (CN, PK `terminal`; `project`, `partof: BRI`), `TRILATERALHIGHWAY`
    (India–Myanmar–Thailand), `BTKRAILWAY` (Baku–Tbilisi–Kars), `ITIRAILWAY`
    (Islamabad–Tehran–Istanbul), `TRANSAFGHANRAILWAY` (planned, UZ–AF–PK), `DEVELOPMENTROAD`
    (IQ, TR; Qatar and the UAE are memorandum parties only) and `GMSSECCENTRAL` (GMS Southern
    Economic Corridor, central subcorridor: TH, KH, VN).
  - Europe: `RAILBALTICA` (EE, LV, LT, PL) and `VIABALTICA` (PL, LT, LV, EE). Finland is not
    on either route.
  - Africa: `MAPUTOCORRIDOR`, `LAPSSET` (KE, SS and ET all `terminal`), `TAZARARAILWAY`,
    `ADDISDJIBOUTIRAILWAY`, `WBNLDC` (Walvis Bay–Ndola–Lubumbashi), `TRANSCUNENE`,
    `DOUALANDJAMENA` and `DOUALABANGUI`.
  - Americas: `BIOCEANICCORRIDOR` (BR, PY, AR, CL), `INTEROCEANICHIGHWAY` (BR, PE) and
    `PACIFICCORRIDOR` (Mesoamerican Pacific Corridor, Mexico to Panama).
  The manifest also defers 14 corridors, with reasons, because they branch, have no defined
  ends or have only one terminal country:
  - the China–Mongolia–Russia, New Eurasian Land Bridge and China–Central Asia–West Asia
    corridors;
  - BCIM;
  - Kaladan, whose two ends are both in India;
  - IMEC;
  - the nine TEN-T European Transport Corridors;
  - Nacala, Beira and the wider Dar es Salaam corridor;
  - the GMS North–South and Southern corridors as wholes;
  - CAREC corridors 1 to 6.
  `BRI` lists `CPEC` among its suborganizations.

### Changed

- Cookbook results that the new records change: the UN-majority blocks without China or the US
  return 59 rows (16 without both, now including `EGDDS`), UN grandchildren return 44 (the
  three IMF standards and `UNSTATCOM` under `ECOSOC`), and `membership_count` mismatches total 186 (`CES` counts 64 members
  and 4 participants; with the `SICA` and `CEI` changes below).
- `SICA` (Central American Integration System) is enriched and reclassified, checked on
  2026-11-21 against archived sica.int pages, the UN Treaty Series and OAS SICE copies of
  the instruments (live sica.int refused automated requests):
  - The record moves from `fta/` to `political/`. Its `blocktype` is now `[political,
    economic]`, as for `ASEAN`, because the Protocol of Tegucigalpa sets a general mandate.
    `scope_category` changes from `treaty_body` to `igo`, because Arts 29-31 of the Protocol
    give SICA legal personality.
  - `founded` is now `1991-12-13`, the date of signature. New `active_period.start`:
    `1993-02-01`. New `founding_members`: the six isthmus signatories.
  - Members get `joined` dates: BZ in 2000, DO on 2013-06-27.
  - 38 observers are added from SICA's observer table (June 2024): 34 countries and the EU,
    OEI, OIJ and ACS. The observer agreements still pending are given in an include `note`.
  - New fields: `suborganizations` (the 8 records whose `partof` is SICA), `secretariat`,
    `headquarters.country` with the Wikidata P159 coordinates, `official_documents`,
    `social_media`, `recognition_status`, `legal_status`, `geographic_scope`, `regions` and
    `notes`. The notes cover the ODECA lineage, the Pro Tempore Presidency, the Secretary
    General and Nicaragua.
  - `languages` is now `[es]`, since Spanish is the Protocol's only authentic text.
  - The documented recipes change. Countries with five or more observer seats: 34 rows
    become 40. Membership-count mismatches: SICA adds one, so with `CEI` below the count
    is 185.
- `CEI` (Central European Initiative) enriched and checked on 2026-11-21 against cei.int and
  the CEI Guidelines and Rules of Procedure (2023):
  - `includes`: accession years for the 17 members from the official roster; a note on the
    suspension of Belarus's rights of representation (25 March 2022), which keeps it on the
    roster as `member`; and founding member Austria as `former_member` (1989–2018). SFR
    Yugoslavia and Czechoslovakia have no country code, so they are only in `notes`.
  - `headquarters` gains `country: IT`. The website link moves from ceinet.org to cei.int.
    `languages` is English, the working language under Article 32.
  - New fields: `founded` (1989-11-11, Budapest), `founding_members` (AT, HU, IT),
    `previous_names` (Quadragonale, Pentagonale, Hexagonale), `secretariat`,
    `geographic_scope`, `regions`, `legal_status`, `recognition_status` (UN General Assembly
    observer since 2011), `official_documents`, `social_media`, a full `description` and
    `notes`, and 17 more `provenance` entries (23 in all).
  - `institutional_design` from the Guidelines: `general` mandate, `consensus`, no
    independent organs, suspension and expulsion by consensus minus one. `CEI` is the first
    record outside the reviewed cohort of 108 that carries it. `decision_force` is omitted
    because the Guidelines do not say whether decisions bind.
  - `other_names` gains ten languages from Wikidata (be, bg, cs, hr, it, pl, ro, sl, sr, uk).
    `acronyms` adds `InCE` (it), `ЦЕИ` (bg), `ЦЕІ` (be) and `ЦЄІ` (uk). The two Chinese
    "acronyms" are removed: 中歐倡議組織 is a name and moves to `other_names`; 歐洲創新中心
    ("European Innovation Centre") was a wrong Wikidata alias.
  - Documented query counts move with the record: 184 `membership_count` mismatches (the
    roster now lists 17 members plus Austria), 201 `former_member` rows with `joined`, and
    109 records with `institutional_design`.
- The review of associate statuses is complete, and no record uses the deprecated `associate`
  status any more. CEOS (12 agencies' home states) and AMN (Bolivia, Chile) move from
  `associate` to `associate_member`. FAO (Faroe Islands, Tokelau), CIAT (Angola, India,
  Morocco, Nigeria) and IOTA (Republic of Korea) move from `associated` to `associate_member`,
  because each organization names the tier associate membership. IICA keeps Spain as
  `associated` ("Associated country").
- `CIS` (Commonwealth of Independent States) checked on 2026-11-21 against the CIS Charter, the
  CIS portal, Wikidata and news on Moldova's withdrawal. The roster keeps nine members, `TM` as
  `associate_member` and `GE` and `UA` as `former_member`. Join dates follow the reviewed
  tier-1 backfill; `AZ` and `MD` stay undated there, and their notes give the 1993 and 1994
  ratifications.
  - `MD` stays `member` with a note: it deposited its withdrawal notifications on 8 April 2026,
    so under Charter Article 9 it leaves on 8 April 2027.
  - `UA` now has `left: 2018-05-19`, the decree that ended its participation in the statutory
    bodies (was `2018`).
  - `GE` is removed from `founding_members`: it joined in 1993, after the Alma-Ata Protocol.
    The eleven Alma-Ata signatories remain.
  - The headquarters is now the Executive Committee at 17 Kirova Street, Minsk, with
    coordinates. The website moves to `https://cis.minsk.by/`, and the CIS portal, the Russian
    Wikipedia article and Wikidata are linked.
  - Acronyms gain their language tags from Wikidata P1813, and the `ru` entry `CIS` is
    dropped. Two traditional Chinese duplicates are dropped too. The French name is capitalized.
  - New fields: `geographic_scope`, `regions`, `headquarters`, `secretariat` (with the Moscow
    branch), `suborganizations` (IACIS, ECCIS, CISSTAT, IAC, EASC, IFESCCO), `legal_status`,
    `recognition_status` (UN General Assembly observer, resolution 48/237), `official_documents`,
    a full `description` and `notes`, 21 `other_names` languages, and the `security` and
    `trade` topics. Field-level `provenance` is added for each.
- Build manifests (`*.manifest.json`) and `datapackage.json` are no longer committed under
  `data/datasets/`. The build still writes them, and every GitHub Release still ships them:
  read them from the latest release or run `python scripts/builder.py build`. They carried
  per-build checksums, sizes, row counts and build identity, so every pair of open data pull
  requests conflicted on them. `contract.json`, the alias files, `border_status.json` and
  `attribute_intblock_migrations.json` stay committed.
- Documentation states the intblock count rounded down to the hundred (`1300+`);
  `scripts/check_doc_counts.py` reads the built manifests and checks that figure.
- Changelog entries go in `changelog.d/<slug>.md` fragments, which the release train merges
  into the release section (see `changelog.d/README.md`).
- `scripts/diff_countries_baseline.py` compares the built manifests with the baseline ref's
  source record counts and committed `contract.json` schema hashes.
- `CSTO` (Collective Security Treaty Organization), checked on 2026-11-21 against the CSTO
  website, Wikidata Q318693 and Wikipedia:
  - `name` uses the official English spelling "Collective Security Treaty Organization"; the
    "Organisation" spelling moves to `other_names`.
  - `includes` gains `joined` dates for the six members and three `former_member` entries:
    UZ (2006-08-16 to 2012-12-19), AZ and GE (1993 to 1999, parties to the 1992 treaty that did
    not sign the 1999 extension). AM stays `member` with a note: participation frozen since
    February 2024, voting rights suspended at the 11 November 2026 Moscow summit, no withdrawal
    filed. `membership_count` stays 6.
  - `founded` is `1992-05-15` (Tashkent treaty) instead of `1992`; new `founding_members`,
    `previous_names`, `suborganizations` (CRRF, PAODKB), `secretariat`, `official_documents`
    (Treaty and Charter), `social_media`, `recognition_status` (UN General Assembly observer
    since 2004), `geographic_scope`, `legal_status` and `regions`.
  - `headquarters.city` is `Moscow` instead of the street name; `languages` is `ru` only, the
    working language; the templated `description` is replaced, and `notes` cover the history
    and statutory bodies.
  - `acronyms` carry the right language tags (for example `KGAÖ` is `tr`, `ҰҚШҰ` is `kk`), and
    `other_names` add the member-state languages (az, be, hy, kk, ky, tg, tr, uk, uz, ms).
  - Documented query counts move with the roster: one more `membership_count` mismatch and
    three more `former_member` rows with `joined`.
- The `validate` workflow runs the test suite in parallel with `pytest-xdist` (`-n auto`;
  `pytest-xdist` is pinned in `requirements-dev.txt`). Python 3.11, 3.12 and 3.13 still
  each build and test their own artifacts. Only 3.11 runs the second build for the
  reproducibility check, and only 3.12 measures coverage against the `fail_under` gate.
- `IAC` (Interstate Aviation Committee) roster checked on 2026-11-21 against the IAC website
  (nine participating states as of January 2026) and the 1991 Minsk Agreement on Civil Aviation
  and on the Use of Airspace. `membership_count` drops from 12 to 9: `UA` becomes
  `former_member` with `left: 2021-02-23` (Presidential Decree No. 70/2021), and `GE` and `MD`
  become `former_member` without a `left` date, since no formal withdrawal date was found. All
  twelve signatories get `joined: 1991-12-25` and are listed in `founding_members`. `RU` keeps
  `member` with a note on the December 2015 transfer of certification to Russian federal bodies.
  - The headquarters now has its country (`RU`) and the coordinates of 22/2 Bolshaya Ordynka
    Street, Moscow, instead of the city centre. The website moves from the retired `mak.ru` to
    `mak-iac.org`.
  - Acronyms get their Wikidata language tags (`SAK` lv, `DAK` tk, `CIEA` es, `ՄԱԿ` hy). Two
    Chinese aliases tagged as acronyms are dropped. The French `other_names` entry, which was
    the English name, is also dropped.
  - New fields: `founded` as a full date, `founding_members`, `secretariat`,
    `geographic_scope`, `regions`, `legal_status`, `recognition_status`, `official_documents`,
    `notes`, `last_verified`, a full `description`, 20 `other_names` languages, and the
    `aviation`, `accident_investigation`, `certification` and `safety` topics. Field-level
    `provenance` cites the IAC website, the Agreement text, Interfax, Wikidata, Wikipedia and
    OpenStreetMap.
  - The documented query counts move with the roster: one more `membership_count` mismatch
    and three more `former_member` rows with `joined`.
- The `last_verified` rule for changed rosters now accepts a record that keeps the base's
  `last_verified` when that date is today. A pull request that re-verified a roster on the same day
  another merge stamped it (for example after the tier-1 `joined` backfill) had no later true date
  to set, so validation failed. A roster change on any later day must still update the date.
- `SCO` (Shanghai Cooperation Organisation), checked on 2026-11-21 against the SCO Secretariat
  website, the 2002 Charter and Wikidata Q485207:
  - The record moves from `data/intblocks/military/` to `data/intblocks/political/`. `blocktype`
    is now `political`, `security`, `military`, `economic` (was `military`, `forum`, `political`):
    the SCO is a multipurpose regional organization and its Charter has no mutual-defence clause.
  - `scope_category` is `igo` (was `policy_forum`). Charter Article 15 makes the SCO a subject of
    international law.
  - `includes` gains `joined` dates for the ten members (founders 2001-06-15, IN and PK
    2017-06-09, IR 2023-07-04, BY 2024-07-04) and the 15 dialogue partners as `partner`, each with
    its Council of Heads of State decision and memorandum. Afghanistan and Mongolia stay
    `observer`. `membership_count` stays 10.
  - `languages` is `ru`, `zh` (Charter Article 20); `headquarters` gains `country: CN`; `founded`
    is `2001-06-15` instead of `2001`. New `founding_members`, `previous_names` (Shanghai Five),
    `secretariat`, `geographic_scope`, `regions`, website links and `social_media`.
    `official_documents` lists the Charter and the 2026 Bishkek Declaration instead of the site root.
  - The templated `description` is replaced, and `notes` cover the Shanghai Five, the 2025
    decision to replace observer and dialogue partner with one SCO Partner status, and the 2026
    Charter protocol.
  - `acronyms` carry the Wikidata language tags (for example `ŞİÖ` is `tr`, `SOZ` is `de`, `ШКУ`
    is `ky`) instead of `en`, and `other_names` add the member and partner languages.
- `ITU` checked on 2026-11-21 against the ITU Member States directory. The 194 Member States
  are unchanged.
  - Every member has `joined` set to its ITU "Member Since" date. Estonia, Latvia and Lithuania
    use the date their membership resumed in 1991-1992, with the interwar year in a `note`.
  - Palestine (`PS`) is an `observer` under Plenipotentiary Resolution 99 (Rev. Dubai, 2018).
  - The record also gets the founding date 1865-05-17 (International Telegraph Convention),
    `active_period` from 1866-01-01 and `previous_names` (International Telegraph Union). The 20
    signatories of 1865 are listed as 16 present-day `founding_members`, mapped as ITU's
    history portal does. It also gets `secretariat`, `recognition_status` (UN agreement of 1947,
    in force 1949), the six official languages, the Constitution, Convention, Radio Regulations
    and International Telecommunication Regulations as `official_documents`, `social_media`,
    `notes` and source-backed `provenance`.
  - `telecommunications`, `standardization` and `connectivity` are added to `topics`.
- Documented recipe expectations in `docs/query-examples.md` now reflect these changes:
  `PS` reaches five observer seats in "Countries with many observer seats", and the UPU and
  ITU rosters now differ from their `membership_count` in "Declared vs actual roster size".
- CI fails on validator warnings: both validation steps run with `--fail-on-warning`. The
  date-based staleness warnings (`last_verified` age, provenance age, border status age) are
  still reported but do not fail it, because they appear as time passes without any change
  to the data.

### Fixed

- The `country_borders` view failed on DuckDB before 2.0, `min_duckdb` 1.5.4 included, with
  "Non-inner join on correlated columns not supported": a build on such a DuckDB stopped at
  view creation, and the v4.1.0 and v4.2.0 release databases could not query the view there.
  The view now unnests `countries.borders` in a subquery before the `LEFT JOIN`. Its rows are
  unchanged (648 on v4.2.0 data, 36 with a status).

- `ASIANHIGHWAY` `regions` listed all six continents, including Africa, the Americas and
  Oceania. They now follow its states parties: Asia, Europe, Caucasus, Central Asia, East Asia,
  Middle East, South Asia and Southeast Asia.
- `regions` on 174 intblocks no longer carries the six-continent placeholder (Africa, Asia,
  Europe, North America, Oceania, South America) left by the 2026-09-09 UNTC import. Each fixed
  record gains a `provenance` entry for `regions`.
  - 147 `geographic_scope: global` records (for example IPPC, ITLOS, SOLAS, CPD, TIR1975) now use
    `worldwide`, as 92 other global records already do. A global record is open to any state, so
    the party footprint at one date is not its region; that footprint is in `includes`.
  - 27 `geographic_scope: regional` records (for example AGR, ATP, ADR, AETR, CMR, DRYPORTS,
    EURO1968TRAFFIC, UN1997AGREEMENT, CLRTAP, AARHUS) now list the continents of their parties,
    most parties first, then the subregion labels of the parties outside Europe in alphabetical
    order. Subregions follow each country's UN M49 `subregion`: Western Asia is `Middle East`
    (except AM, AZ and GE, which are `Caucasus`), and Iran is in `South Asia`. ASIANHIGHWAY gets
    the same fix in a separate change.
- `AGR` (European Agreement on Main International Traffic Arteries, which defines the
  International E-road network) now links the English Wikipedia article on the network. Its
  Wikidata exclusion now records that Q106123 describes the network, not the agreement, as for
  `ASIANHIGHWAY`; the old reason said no English article existed.
- `UNECEWATER` (Water Convention) and `UN1958AGREEMENT` (1958 Agreement on vehicle regulations)
  now have `geographic_scope: global`, not `regional`, because their parties are no longer
  limited to the UNECE region. 19 of the Water Convention's 59 parties are outside it; the
  amendments to articles 25 and 26 that opened it entered into force on 6 February 2013. 16 of
  the 1958 Agreement's 61 Contracting Parties are outside it, for example AU, JP, KR and ZA;
  Revision 2, which opened it, entered into force on 16 October 1995. As for other global
  records, `regions` is now `worldwide`.
- `PARLACEN` (Central American Parliament) roster checked on 2026-11-21 against PARLACEN's
  official observer list and press reports; `last_verified` was 2026-07-29.
  - The record listed no observers. It now has the five on the official list as `observer`:
    `MX`, `PR`, `MA`, `VE` and `CN` (admitted on 21 August 2023). `TW` is a former observer
    (`joined` 1999, `left` 2023-08-21): the same plenary decision revoked the Legislative Yuan's
    status. Russia, approved in September 2024 subject to ratification, is not on the official
    list and is not added.
  - Nicaragua denounced the Constitutive Treaty on 3 October 2026 "with immediate effect". The
    treaty has no denunciation or withdrawal clause, and PARLACEN has not accepted the exit, so
    `NI` stays a founding member and `notes` records the pending exit.
  - The documented recipe "Countries with many observer seats" still returns 40 rows: `MX`
    and `TW` move from 5 to 6 observer entries, and `CN` from 6 to 7. "Declared vs actual
    roster size" counts 187 mismatches, one more than with `SICA`, `CEI` and `CES`:
    `membership_count` stays 6, the member states, while `includes` now has 12 entries.
- Three global records checked against official sources on 2026-11-21. Each gains
  `last_verified`, and its `regions` label `Global` becomes `worldwide`.
  - `BUDCONV` (Budapest Convention on Cybercrime): parties now follow the Council of Europe
    Treaty Office chart, which counts 84 ratifications and accessions; the record had 69. 20
    parties are added, with the date each ratified or acceded as `joined`; among them are AM, AZ,
    IL, MC, SM, eight African states and five Pacific states. Kazakhstan and Seychelles are in
    the count, but the Convention enters into force for them only in 2027. IE and ZA (signed
    only), MX and UY (invited to accede only) and SV (not on the chart) are removed.
  - `COVAX`: Gavi says COVAX closed on 31 December 2023, so the record is now `historical`
    with `dissolved: 2023-12-31`. Participants now follow Gavi's list of participating economies
    of 12 May 2021, the latest list that names them, and their status changes from `member` to
    `participant`. That list has 177 economies: 56 self-financing, 29 "Team Europe" and 92
    eligible for the COVAX AMC. Kosovo and West Bank and Gaza are added. 19 economies not on the
    list are removed, among them US, RU, TR, ZA, MY and TH. The notes record that Gavi counts
    195 participants and donors at closure but names none beyond the list.
  - `JCPOA`: no roster change. The 8 participants, the US withdrawal on 8 May 2018 and the end
    on 18 October 2025 are now cited from the EEAS, the White House and Iran's foreign
    ministry, not only Wikipedia.
- The `regions` label `Global` is now `worldwide`, the label other global records use, on 40
  intblocks. 39 of them had `regions: [Global]`, for example ATT, CWC, WCO, WEF, BIMCO and IRF.
  SIDS keeps its other labels (Caribbean, Pacific, Africa). 34 records gain a `provenance` entry
  for `regions`. CTBTO, MSC, BIMCO, GSP, GSTP and IRF keep the entry they already had, because
  only the spelling of the label changed. BUDCONV, COVAX and JCPOA, the other three records
  with `Global`, are covered by the roster check entry above.
- `GRECO`: Belarus is a `former_member` (it ceased to be a member on 1 May 2024), not an
  associate. `membership_count` is now 48, and the `joined` dates of Poland and the Russian
  Federation follow GRECO's members page.
- `IOTA`: Uzbekistan is added as an associate member (2026).
- `EROPA` checked on 2026-11-21 against the EROPA website (history, constitution, secretariat,
  centers): `headquarters.city` is now Quezon City (it held the college name), and admission
  dates come from the official history, so Nepal joined in December 1980, not 1983. Founding
  members carry `joined: 1960-12-05`, which adds one row (`AU`) to the documented
  former-members-with-dates recipe. `legal_status` now describes the hybrid
  State/Group/Individual membership. The record gains `social_media`, the constitution in
  `official_documents`, `secretariat.organization`, notes on PRC and SRV seat successions, and
  three topics. `scope_category` stays `igo` pending review.
- `CAPAM` is now `non_state_organization` and no longer lists 55 country members. It was a
  Canadian federal not-for-profit corporation whose members were individuals and organisations,
  including government ministries and departments, not states (Corporations Canada; Jamaica
  Information Service, 2008). The old roster copied the Commonwealth's, without the UK and with
  Gabon and Togo, which joined the Commonwealth in 2022. The record drops `partof: COMMONWEALTH`
  and sets `membership_applicability: not_applicable`, as `ACU` does, and leaves
  `scope_category.igo_legal_status_allowlist`. `memberships` loses CAPAM's 55 rows, and the
  documented dissolved-with-roster recipe loses one row. The record also gains the last
  registered office, the 2019 dissolution vote and reasons, the 1998 start of the Innovations
  Awards (not 1997), conference examples and three topics.
- `CREDAF` checked on 2026-11-21 against credaf.org. `headquarters` is now Paris (86, allée de
  Bercy), where the secretariat sits, not Yaoundé, where the statutes were drawn up in 1982.
  The 15 founding administrations, Gabon among them, are in `founding_members` and marked
  `founding_member` (`joined: 1982`) in `includes`. The English name in `other_names` is the one
  the site uses, and the pre-2018 name is in `previous_names`. `legal_status` now records the
  self-described non-governmental form and the membership of national tax administrations.
  The record also gains `secretariat`, the Executive Bureau, conferences from 2012 to 2026,
  cooperation agreements and two topics. `scope_category` stays `igo`, as for its NTO peers.
- `GFDRR` (Global Facility for Disaster Reduction and Recovery) roster and metadata, checked on
  2026-11-21 against the GFDRR Annual Reports 2024 and 2025 on World Bank Documents & Reports.
  `includes` now has 11 `member` entries: AU, AT, CA, DE, IT, JP, NO, SE, CH, US and the EU.
  IN, LU and RS are not in either report's partner list, so they are now `former_member`
  (exit dates unknown), and `membership_count` drops from 14 to 11. The record gains the
  `fund` blocktype and `partof: WB`. It also gains `geographic_scope`, `regions`,
  `active_period`, `legal_status`, `recognition_status`, `secretariat`, `social_media`,
  `official_documents` and `notes` (governance, Umbrella Program trust funds, FY2025 figures).
  The description is rewritten and `provenance` is extended. GFDRR adds one row to the
  `membership_count` mismatch recipe in `docs/query-examples.md`.
- `CDRI` (Coalition for Disaster Resilient Infrastructure) roster and metadata, checked on
  2026-11-21 against cdri.world (About page, Charter and Leadership team). The Philippines
  (`PH`, joined 2026-09) is added, so `membership_count` goes from 58 to 59 member countries.
  ECOWAS gets `joined: '2026-02'`. The site now reports 13 partner organizations but shows
  logos for only 12, so the 13th is not mapped. The record gains French and Spanish
  `languages` and links. It also gains `other_names` (fr, es, ar, zh), `social_media`
  (X, LinkedIn, YouTube, Facebook), `official_documents` (the amended Charter in three
  languages and the 2024–25 Annual Report) and the `sustainable_development` topic. `notes`
  now covers governance under the Charter, the co-chairs and IRAF. The description is
  rewritten and `provenance` is extended.
- `ECOWAS` was missing Mauritania (`MR`), one of the 15 signatories of the 1975 Treaty of Lagos.
  It is now listed as `former_member`, joined 1975-05-28 and left 2000-12, per the ECOWAS
  Creation (History) page. The page also says Mauritania signed an associate-membership
  agreement in August 2017. That agreement is kept in the entry's note, because it is not
  membership.
- `ITER` checked on 2026-11-21 against the ITER Agreement and iter.org. `name` is now the
  Article 1 name, "ITER International Fusion Energy Organization". `founded` moves from
  2006 (the signing year) to 2007-10-24, the date the Organization was established, and
  `active_period` starts on the same day. `headquarters` gains `country: FR` and the
  Saint-Paul-lez-Durance site coordinates, replacing the CEA Cadarache point. `languages`
  is now `en` only, because English is the working language. The seven Members gain
  `joined` 2007-10-24 and become `founding_members`: CN, IN, JP, KR, RU and US, since
  Euratom has no country code. New `includes` entries: CH (`participant` through Fusion for
  Energy, from 2026-01-01) and the non-Member cooperation partners AU, KZ and CA
  (`cooperating`). `membership_count` stays 7. The record also gains `institutional_design`,
  `legal_status`, `recognition_status`, `official_documents`, `social_media`, `secretariat`,
  `notes`, a rewritten `description`, the topics energy, nuclear and physics, and 19
  provenance entries. A second Wikidata link points to the organization item Q101069148;
  `wikidata_id` stays Q191788. ITER joins the reviewed `institutional_design` cohort, and
  it now appears in the declared vs actual roster recipe, because it lists 11 entries
  against its 7 Members.
- `CERN` checked on 2026-11-21 against home.cern and the CERN Convention (English text on
  the Dutch government treaty database). `founded` moves from 1954 to 1954-09-29, the date
  the Convention entered into force, and `active_period` starts on the same day. All 25
  Member States and 11 Associate Member States gain `joined` years from CERN's timeline,
  and the 11 founders still members become `founding_members`. Yugoslavia, the twelfth
  founder, left in 1961 and has no country record. The observers JP, US, EU and UNESCO are
  added as `observer`. `membership_count` stays 36 (Member States plus Associate Member
  States). `previous_names` records the provisional Conseil Européen pour la Recherche
  Nucléaire (1952-1954). Also changed: the website becomes https://home.cern/, the
  headquarters coordinates come from Wikidata, and `description` is rewritten.
  The record also gains `institutional_design`, `legal_status`, `recognition_status`,
  `official_documents`, `social_media`, `secretariat`, `notes`, `geographic_scope`
  (regional, Europe), the topic physics and 19 provenance entries. CERN joins the reviewed
  `institutional_design` cohort, and it now appears in the declared vs actual roster
  recipe, because it lists 40 entries, observers included, against a count of 36.
- `ESO` checked on 2026-11-21 against eso.org and the ESO Convention (Dutch authentic text on
  the Dutch government treaty database). `founded` moves from 1962 to 1962-10-05, the date of
  signature, and `active_period` starts on 1964-01-17, when the Convention took effect. The
  16 Member States gain `joined` dates from ESO's Member States table and timeline. The five
  signatories (BE, DE, FR, NL, SE) become `founding_members`. Chile, the host and partner
  country, and Australia, a Strategic Partner since 2017, are added as `partner`.
  `membership_count` stays 16. `languages` gains `fr` and `de`. The website moves to
  https://www.eso.org/, the headquarters coordinates come from Wikidata, and `description` is
  rewritten. The record also gains `institutional_design`, `legal_status`,
  `recognition_status`, `official_documents`, `social_media`, `secretariat`, `notes`,
  `geographic_scope` (regional, Europe), the topic astronomy and 18 provenance entries. ESO
  joins the reviewed `institutional_design` cohort, and it now appears in the declared vs
  actual roster recipe, because it lists 18 entries against 16 Member States.
- With ITER, CERN and ESO, the reviewed `institutional_design` cohort in
  `data/schemas/institutional_design_pilot.yaml` becomes `reviewed_111`. The documented
  authority-level and declared vs actual roster recipes, and their tests, are updated.
- The roster watch no longer reports Denmark as missing from Wikidata for the UN and the OECD.
  Wikidata records those memberships on the Kingdom of Denmark (Q756617), which has no
  ISO 3166-1 code. The Denmark mapping pointed at Q35, which already has the code.
- The roster watch no longer opens a new `roster-drift` issue for differences that a person
  closed as not planned (internacia-db is right). It reports them again only when the
  differences change. Before, closing such an issue brought it back as a new issue the next
  Monday.
- `UPU` checked on 2026-11-21 against the UPU member countries list and its 192 member pages.
  - Cook Islands (`CK`) and Niue (`NU`) were listed as members. The UPU covers them under New
    Zealand's membership, so they are now `represented`. `AW` is added as the coded `member` for
    the joint member "Aruba, Curaçao and Sint Maarten". The roster still has 190 sovereign-state
    members.
  - 42 territories that UPU member pages list under another member (Constitution art. 23) are
    `represented`. They include the UK Overseas Territories, which form one UPU member without a
    single ISO code. `membership_count` stays 192, with `membership_count_type: mixed`.
  - Palestine (`PS`) is an `observer` (since 1999).
  - Every member has `joined` set to its UPU date of entry.
  - The record also gets the founding date 1874-10-09 (Treaty of Bern), `active_period`,
    `previous_names` (General Postal Union), the 22 Treaty of Bern signatories as
    `founding_members`, `secretariat`, `recognition_status`, named `official_documents`, `notes`
    and source-backed `provenance`. Mislabelled acronym languages are fixed.
  - Off-topic tags and topics (`regional_cooperation`, `telecommunications`) are replaced with
    `standardization` and `trade_facilitation`.

### Data changes since the previous release

- Countries: 256 → 256 records
- Intblocks: 1282 → 1338 records; added `ADDISDJIBOUTIRAILWAY`, `AFRICANSTATISTICSCHARTER`, `AFRISTAT`, `AH`, `AITRS`, `ALCOMA`, `ARABMASHREQRAILWAYS`, `ARABMASHREQROADS`, `BIOCEANICCORRIDOR`, `BTKRAILWAY`, `CCTTFA`, `CES`, `CHABAHAR`, `CICPEC`, `CLRT`, `COEAICONVENTION`, `CPEC`, `DEVELOPMENTROAD`, `DOUALABANGUI`, `DOUALANDJAMENA` and 36 more; 262 changed
- Blocktypes: 82 → 83 records; added `artificial_intelligence`; 1 changed
- Membership edges: 57295 → 58096; 880 added, 79 removed, 1670 changed

## [4.2.0] - 2026-11-21

### Added

- Three transport corridor records with route roles (`transport`, `corridor`), checked on
  2026-11-20 (1282 intblocks):
  - `INSTC` (International North–South Transport Corridor): IN and RU `terminal`, IR and AZ
    `transit`. Sources: ADB (ARIC) and the Azerbaijani government.
  - `TITR` (Trans-Caspian International Transport Route, the Middle Corridor): CN and TR
    `terminal`; KZ, AZ and GE `transit`. Sources: the TITR association and the Azerbaijani
    government.
  - `LAPISLAZULI` (Lapis Lazuli route, a 2017 agreement and `treaty_body`): AF and TR
    `terminal`; TM, AZ and GE `transit`. Source: Afghanistan's foreign ministry (RECCA).
  `INSTC` and `TITR` describe the route, not the organization: the 2000 INSTC agreement has
  parties that are not crossed, and the TITR association's members are companies. A separate
  INSTC agreement record is deferred.
- `institutional_design` for 21 more organizations, from founding instruments or official
  pages checked on 2026-11-20 (55 in all): BENELUX, BSEC, CAN, CELAC, CEMAC, COMESA,
  COMMONWEALTH, CPLP, EAC, ECCAS, ECO, FAO, GUAM, ILO, IMO, OIF, OSCE, PIF, SICA, UEMOA and
  UNESCO. IGAD (its 2023 treaty's entry into force is unconfirmed) and SAARC (no readable
  source) are deferred, with BRICS and OECD.
- `institutional_design` for 18 more organizations, checked on 2026-11-21 (73 in all): ADB,
  AFDB, AIIB, BIS, CBSS, EBRD, IADB, IEA, IFAD, INTERPOL, IOM, IRENA, ISA_SEABED, OPCW,
  PACIFICALLIANCE, UMA, UNIDO and WCO. Arbitration that covers only disputes with former members
  is not an independent organ, as for WB. ALBA (no readable source) and CTBTO (the record is the
  Preparatory Commission, while the sources describe the organs of the CTBT, which is not in
  force) are deferred. `UNIDO` gains `last_verified`.
- Nine more `border_status` entries from Canadian and UK travel advice, checked on 2026-11-21
  (15 in all): `closed` for ERI–ETH, FIN–RUS, GUY–VEN (no official crossing), IND–PAK and
  KHM–THA; `restricted` for AFG–PAK, BLR–LTU, BLR–POL and EST–RUS. No source gives a start
  date, so `since` is omitted. LVA–RUS, NOR–RUS and ISR–SYR are deferred.
- `institutional_design` for 16 more organizations, checked on 2026-11-21 (89 in all): ACD,
  ACS, ALADI, ARCTICC, BEACST, BIMSTEC, CEFTA, CENSAD, CICA, COI, NCM, NORDEN, OECS, SACU, SELA
  and UNWTO. NAM, SPC, TURKKON and V4 are deferred for lack of a qualifying source.
- Three more `border_status` entries, checked on 2026-11-21 (18 in all): `closed` for BLR–UKR;
  `restricted` for LTU–RUS and POL–RUS (Kaliningrad crossings). KAZ–TKM and AFG–TJK are deferred
  because the travel advice read concerns travellers and does not settle whether goods cross;
  nine more pairs are deferred for lack of a qualifying source.
- The evidence limit of `border_status` is documented in `docs/ai-consumers.md`,
  `docs/query-examples.md` and the source file header. Most entries rest on travel advice, which
  describes crossings for travellers, so a `closed` border can still carry some freight. A
  re-check against customs, border and transport sources on 2026-11-21 could not read them (403
  or bot checks), so no status changed. FIN–RUS, IND–PAK and KHM–THA are the first to verify.
- `institutional_design` for 19 treaty bodies and courts, checked on 2026-11-21 (108 in all):
  ATS, BASEL, CBD, CITES, ECSEE, ECT, HCCN, ICW, IGC, ITLOS, ITTO, IWC, MONTREALPROTOCOL, NPT,
  PARISAGREEMENT, PCA, POPS, UNCLOS and UNFCCC. For treaties the principal organ is the
  Conference or Meeting of the Parties. Where the text names consensus only for rules of
  procedure and amendments (UNFCCC, the Paris Agreement, CBD, Basel, Stockholm),
  `decision_rule` is omitted. RAMSAR is deferred because only the 1971 text could be read.

### Data changes since the previous release

- Countries: 256 → 256 records
- Intblocks: 1279 → 1282 records; added `INSTC`, `LAPISLAZULI`, `TITR`; 74 changed
- Blocktypes: 82 → 82 records
- Membership edges: 57281 → 57295; 14 added, 0 removed, 0 changed

## [4.1.0] - 2026-11-20

### Migration

- `intorg` is deprecated (see Deprecated). To select intergovernmental organizations, filter
  on `scope_category` (712 → 638 records after this release's corrections), not on a blocktype:

  ```sql
  -- before
  SELECT id, name FROM intblocks WHERE list_contains(blocktype, 'intorg');
  -- after
  SELECT id, name FROM intblocks WHERE scope_category = 'igo';
  ```

  The `intorg` query still returns the same 358 records in 4.x.
- `scope_category = 'igo'` returns 638 records instead of 712: 75 records leave `igo` and
  `ISA_SEABED` joins it (see Changed). Filters that treated every
  `igo` as state-constituted now exclude NGOs, scientific unions, industry associations,
  partnerships and hosted funds.
- 170 intblock files moved to new directories. Record ids are unchanged, so no alias is needed.
  Code that reads source YAML by path should look a record up by `id`.
- 24 non-state organizations no longer list countries in `includes` (1,800 membership edges,
  59,102 → 57,302). Their members are companies, unions, universities or other organizations,
  so the countries where those members are based were never member states. Queries that
  counted, for example, IATA, ITF or WFTU membership by country return no rows for them now.
- One optional column, `institutional_design`, is appended as the last intblocks column, with
  open enums for its subfields (see Added). No existing column, type, key or identifier
  changes. Consumers that read intblocks into a fixed-width row see one new trailing column.
- `memberships` and `current_memberships` gain a trailing `role` column (route role on
  pipelines and corridors; NULL elsewhere). The intblocks `includes[].role` field, exported but
  always NULL before, is now declared and populated for a reviewed cohort. A new `border_status`
  table (one row per border, keyed on the sorted `iso3code` pair) and `country_borders` view are
  added, and four oil pipeline records are new. All new enums are open; no existing column,
  type, key or identifier changes.

### Added

- Blocktypes `governance` (public administration, federalism, elections, anti-corruption,
  transparency) and `commodity` (intergovernmental commodity bodies and study groups), and
  directories for six existing keys: `fisheries`, `financial`, `development`, `tourism`,
  `labor`, `disaster`. 80 blocktypes.
- Every blocktype has a `description` (scope note) that states the boundary with overlapping
  keys. The blocktypes export gains nullable `description` and `deprecated` columns.
- Validation rules (blocking): `PRIMARY_BLOCKTYPE_MISMATCH` (the directory must be the first
  blocktype), `MISSING_BLOCKTYPE_DESCRIPTION`, `DEPRECATED_PRIMARY_BLOCKTYPE`, and
  `DEPRECATED_BLOCKTYPE_RATCHET` (the records that carry a deprecated blocktype must equal the
  baseline in `data/schemas/deprecated_blocktypes_baseline.yaml` until the next MAJOR release).
- `SCOPE_CATEGORY_SEMANTIC_MISMATCH` now also reports `igo` with a non-state `legal_status`
  (NGO, non-profit, charity, private body, industry or trade association, union federation).
  39 reviewed ids are allowlisted in `intblocks_completeness.yaml`
  (`scope_category.igo_legal_status_allowlist`) pending review: 11 former `intorg` records and
  28 sports federations, energy and postal associations.
- `scripts/backfill_scope_category.py` can reclassify a record from the value listed under
  `expected_current` in a reviewed manifest, with evidence.
- Optional `institutional_design` object on intblocks (OpenSpec change `add-intblock-institutional-design`): what the founding instrument lets an organization decide and enforce. Subfields: `mandate`, `decision_rule`, `decision_force`, `independent_organs[]`, `enforcement[]`, `mutual_defence`, `veto_holders[]`. An absent object or subfield means unknown. Values are defined in `data/schemas/institutional_design.yaml`; all subfield enums are open in `contract.json`.
- Exported as a struct column, appended last, in Parquet, DuckDB and JSONL, and as `design_*` columns in the flattened intblocks CSV. The lite exports do not change.
- Reviewed pilot of 34 records from `data/schemas/institutional_design_pilot.yaml`, each with `provenance` (`field: institutional_design`) to the founding instrument or an official page, checked on 2026-11-20. Two candidates (BRICS, OECD) are deferred because no qualifying source could be read; the manifest lists why. `IAEA` and `UPU` gain `last_verified: 2026-11-20`; other records keep their existing date, because their rosters were not re-verified.
- `scripts/backfill_institutional_design.py`: dry run by default, whole-cohort validation, conflict blocking, idempotent apply, provenance insertion.
- Validation rules: `INSTITUTIONAL_DESIGN_SCOPE_CONFLICT`, `INSTITUTIONAL_DESIGN_NONE_CONFLICT`, `INVALID_VETO_HOLDER` and `MISSING_INSTITUTIONAL_DESIGN_PROVENANCE` (blocking); `VETO_HOLDERS_UNDER_CONSENSUS` (warning). `institutional_design` coverage is reported, never gated.
- Documented, tested DuckDB recipes in `docs/query-examples.md` (Authority and capacity): an authority level (`none`/`low`/`medium`/`high`) derived from `institutional_design`, and member population concentration (world share, largest member, HHI, effective members). `docs/ai-consumers.md` shows how to join external GDP or military indicators on `iso3code`; none ship.
- Transit dependence layer (OpenSpec change `add-transit-dependence-layer`):
  - `includes[].role` declared, with values in `data/schemas/include_roles.yaml`: `origin`,
    `transit` and `destination` on pipelines (`gaspipeline`, `oilpipeline`); `terminal` and
    `transit` on linear transport corridors (`corridor`). Blocking rules `INCLUDE_ROLE_NOT_ALLOWED`,
    `INVALID_INCLUDE_ROLE`, `INCOMPLETE_INCLUDE_ROLES`, `MISSING_ROUTE_ENDPOINT` and
    `MISSING_ROLE_PROVENANCE`. `scripts/backfill_include_roles.py` applies roles from the reviewed
    manifest `data/schemas/include_roles_pilot.yaml` (dry run by default).
  - Blocktypes `oilpipeline` and `corridor` (82 blocktypes).
  - Reviewed role pilot, checked on 2026-11-20 against operator, government, intergovernmental or
    project-finance sources: 15 gas pipelines, four new `oilpipeline` records (`BTC`, `KAZCHINA`,
    `CPC`, `KIRKUKCEYHAN`; 1279 intblocks) and the `CKURAILWAY` corridor (which gains the
    `corridor` blocktype). Changed records get `last_verified` 2026-11-20. Thirteen candidates are
    deferred with reasons in the manifest, among them TANAP, Baltic Pipe and the MEG pipeline,
    whose rosters list supplier countries that sit on a feeder pipeline rather than on the
    record's own route.
  - Land-border crossing status in `data/borders/border_status.yaml` (schema
    `data/schemas/border_status.schema.json`), exported as `border_status.json`,
    `border_status.parquet` and the DuckDB `border_status` table, plus the `country_borders`
    view. Six closures from official travel advice, checked on 2026-11-20: ARM–AZE, ARM–TUR,
    DZA–MAR (since 1994), ISR–LBN, KOR–PRK and RUS–UKR. ISR–SYR is deferred for lack of a
    qualifying source. Absence of a row means no closure is recorded, not that the border is
    verified open. Blocking rules `UNRESOLVED_BORDER_STATUS_PAIR`, `BORDER_STATUS_NOT_ADJACENT`
    and `BORDER_STATUS_PERIOD_CONFLICT`; warning `STALE_BORDER_STATUS`.
  - Recipes in `docs/query-examples.md` (Transit and borders): neighbours' border status,
    sea-access gateways of landlocked countries (a structural lower bound; `closed` and
    `restricted` borders are not crossable), and countries by route role.
    `docs/ai-consumers.md` documents trade dependence measures and the external join pattern;
    no trade data ships.

### Changed

- The 147 records in `data/intblocks/intorg/` and 23 records from other directories moved to
  domain directories (OpenSpec change `reorganize-intorg-blocktype`, mapping in
  `openspec/changes/reorganize-intorg-blocktype/intorg_mapping.yaml`). Examples: 34 regional
  fisheries bodies in `fisheries/` (17 from `intorg/`, 17 from `food/`); FATF, its regional
  bodies, FSB, IOSCO, IAIS and BCBS in `financial/`; BEACST, NCM, MSG and other multipurpose
  regional organizations in `political/`. Each record's directory is now its first blocktype;
  `intorg` moved to the end of the list. 26 `space/` records were reordered the same way.
- `scope_category` corrected for 76 records that carried `intorg`, each from an official
  source with field-level provenance (`data/schemas/scope_category_intorg_review.yaml`):
  54 become `non_state_organization` (for example ISO, IEC, CEN, IATA, BIMCO, UIC, IFRC and
  the scientific unions), 11 `intergovernmental_body` (for example BCBS, UNITAID, NEPAD,
  GFDRR, IOC-UNESCO), 10 `policy_forum` (for example GBEP, IGF, GMI, PLG), and `ISA_SEABED`
  becomes `igo` (it was `treaty_body`). The legacy labeller no longer maps `intorg` to `igo`,
  which caused these labels.
- Country rosters removed from 24 records that became `non_state_organization` and whose members
  are organizations, not states: `AAU`, `ACU`, `EBU`, `EMS`, `ETSI`, `EUA`, `EUCHEMS`,
  `EUROGEOGRAPHICS`, `IAF`, `IAF_ASTRO`, `IAPH`, `IATA`, `IAU_UNIV`, `IBRO`, `IFOAM`,
  `INTERPORTPOLICE`, `IRU`, `ISTO`, `ITFTRANSPORT`, `PATA`, `PBEC`, `POGO`, `UIC`, `WFTU`.
  Each now has `membership_applicability: not_applicable` with provenance, as `MSF` and
  `CANTO` already did, and `last_verified` 2026-11-20. `includes`, `founding_members` and
  country-unit `membership_count` values are removed; counts of organizations keep their
  `membership_count_type`. Records whose members are one national body per country (ISO, IEC,
  CEN, the scientific unions) keep their rosters. Documented recipes change accordingly: Russia
  has 13 former memberships (not 14), and 58 majority-UN blocks lack China or the US (not 59).
- The changed-record `last_verified` rule compares a moved file with its record at the old path
  and treats `blocktype` as a classification field, like `scope_category`.

### Deprecated

- Blocktype `intorg`, listed in `contract.json` `deprecated[]` (`intblocks.blocktype`). It
  described entity form, which `scope_category` holds. It stays as the last blocktype of its
  358 records in 4.x and will be removed no earlier than 5.0.0.

### Data changes since the previous release

- Countries: 256 → 256 records
- Intblocks: 1275 → 1279 records; added `BTC`, `CPC`, `KAZCHINA`, `KIRKUKCEYHAN`; 280 changed
- Blocktypes: 78 → 82 records; added `commodity`, `corridor`, `governance`, `oilpipeline`; 78 changed
- Membership edges: 59072 → 57281; 9 added, 1800 removed, 40 changed
- Schema (minor): table border_status added
- Schema (minor): table country_borders added
- Schema (minor): column blocktypes.deprecated added
- Schema (minor): column blocktypes.description added
- Schema (minor): column current_memberships.role added
- Schema (minor): column intblocks.institutional_design added
- Schema (minor): column memberships.role added
- Schema (minor): source field intblocks.institutional_design added

## [4.0.0] - 2026-11-19

### Migration from 3.x

This is a MAJOR release: `contract_version` is `4.0`. Tables, columns, types, keys and record
identifiers are unchanged.

- `countries.native_names` holds names in each entity's own languages only (see Changed). Read
  names in other languages from `other_names`, and English names from `name` and
  `official_name`. A lookup of `native_names['en']` or a UN-language key now finds nothing for
  most countries.
- internacia-python 0.4.x accepts contract 3 only: it keeps downloading v3.1.0 and refuses a 4.x
  database with `ContractError`. internacia-python 0.5.0 reads 3.x and 4.x databases.
- `associate` and `associated_observer` are deprecated (see Deprecated) but stay valid in 4.x.
  Filters on them should also accept `associate_member`. They are removed no earlier than 5.0.0.

### Security

- The release workflow is split into `build`, `sdk-contract` and `publish` jobs. Only `publish` has `contents: write` and secrets; it verifies every artifact against a digest recorded by `build` and runs no third-party code except pinned actions and `huggingface_hub`. Before, `internacia-python@main` was installed and tested in the job that held `HF_TOKEN`, with the write token stored in `.git/config`.
- Every GitHub Action is pinned to a commit SHA (Dependabot keeps them current). `pip-audit` and `huggingface_hub` (`requirements-publish.txt`) are pinned. The SDK contract suite runs against a pinned internacia-python commit (v0.4.1) in both `validate.yml` and `release.yml`.
- `validate.yml` and `link-validation.yml` run with a read-only token, and checkouts that run pull-request or third-party code no longer keep credentials.

### Added

- Validation rule `SCOPE_CATEGORY_STATUS_CONFLICT` (blocking): an `informal` or `de-facto` intblock cannot have `scope_category: igo`, because an IGO requires independent institutional identity.
- `python scripts/enrich_countries.py refresh-classifications` refreshes `region`, `adminregion`, `incomeLevel` and `lendingType` from the World Bank API (`/v2/country`) and rebuilds the `wbgroup` rosters derived from them; the monthly `enrich` run does the same. Shared logic lives in `internacia_builder/wb_classification.py`.
- Validation rule `World Bank group rosters` (warning, `WB_GROUP_ROSTER_MISMATCH`): each `wbgroup` region, administrative-region and income roster must list exactly the economies whose Bank-published country field puts them in the group.
- `data/vocabs/language_codes.yaml`: the 153 ISO 639-3 codes used in `languages[]`, each with its `native_names` key and the Wikidata label codes to try. It replaces two-letter truncation (`pol` became `po`, `swe` became `sw`) and resolves collisions (`ron` also matches the "Moldovan" item; Norwegian labels are under `nb`/`nn`).
- `python scripts/enrich_countries.py refresh-native-names [--code XX] [--dry-run]`.
- Validation warning `NATIVE_NAME_LANGUAGE`: a `native_names` key must be one of the record's languages. An empty `native_names` map is complete when `languages[]` is empty.

### Changed

- Dependencies: duckdb 2.0.0, pyarrow 26.0.0, pandas 3.1.0, typer 0.27.3, tqdm 4.70.1; dev pytest 9.2.0, pytest-cov 7.1.0, ruff 0.17.3, pre-commit 4.7.0, polars 2.1.0 (Dependabot #104, with `uv.lock`). The builder keeps DuckDB storage `v1.0.0`, so `internacia.duckdb` still opens with DuckDB 1.5. DuckDB 2.0 no longer lets a connection register a table while a `fetchone()` result is open, and it warns on Arrow output from DB-API results; the build and `check_generated_artifacts.py` are adjusted.
- `tests/test_dependency_pins.py` fails CI when the runtime pins in `pyproject.toml`, `requirements.txt` and `uv.lock` disagree (Dependabot's pip updates do not touch `uv.lock`). The coverage gate rises from 49% to 80% (measured 82.6%).
- Exported `includes[].name` of `type: country` entries is the country's `name`, filled by the build; `name` is optional for those entries in the source. The 3,501 source names that differed (95 id–name pairs, for example TR `Turkey`, MK `Macedonia, FYR`, CV `Cape Verde`) are rewritten to the country `name`. `INCLUDE_NAME_MISMATCH` compares exactly and is now a validator warning. Relabelling a country include does not need `last_verified`.
- Associate memberships use `associate_member`: 40 entries move from `associate` (UNESCO 12, SCAR 13, ACS 10, IMO 3, EMBL 1, OECD DAC 1) and 10 from `associated` (OECS 5, PASO 3, MSG 1, Dutch Language Union 1). OECS, PASO, MSG and the Dutch Language Union were checked against their sources and have `last_verified` 2026-11-19. OpenSpec change `normalize-include-labels-and-statuses`.
- Hugging Face is pushed after the GitHub Release, in one commit (`scripts/push_huggingface.py`) that also removes legacy files and is tagged with the release tag. Before, files were uploaded one by one before the GitHub Release, and failed legacy deletions were silently ignored.
- The changed-record `last_verified` rule now also exempts changes limited to `scope_category` and its provenance. Reclassifying a record does not attest its roster.
- `data/schemas/countries.schema.json` now rejects fields it does not declare (`additionalProperties: false` at the top level and in every nested object), so a misspelled field fails validation instead of passing silently. It declares the fields the data already used: `source_id` on `area` and `gini`, `note` on provenance entries, and the optional `official` flag on `languages` that its description already mentioned. No export changes.
- **BREAKING (content):** `countries.native_names` now holds names in each entity's own languages (`languages[]`), not English and the UN languages. `official` comes from Wikidata P1448 (official name) and `common` from the Wikidata label, falling back to P1705 (native label) when the label repeats `official`. Aliases are no longer used, which removes values such as CN `en.common: Red China`, BY `en.common: White Russia` and RU `fr.common: Rus.`. The variants were also swapped before (DE `en` had `official: Germany`, `common: Federal Republic of Germany`). Chinese follows the entity's script. Entries fall from 1504 to 388, and `en` remains for the 91 entities that list English. Read exonyms from `other_names` and English names from `name`/`official_name`. internacia-python 0.4.1 searches `other_names` and `common_names` too, so country search in other languages keeps working. The column type `map<string, struct<official, common>>` is unchanged; either field may now be null. OpenSpec change `fix-country-native-names`.

### Deprecated

- Include statuses `associate` and `associated_observer`, listed in `contract.json` `deprecated[]` (new `enum_value` entries) and reported as `DEPRECATED_INCLUDE_STATUS` warnings. They stay valid in 4.x and will be removed no earlier than 5.0.0. Fifteen entries still use `associate` (CEOS 12, AMN 2, GRECO 1) because their sources could not be reached; recoding a deprecated value to one of its replacements does not need `last_verified`.

### Fixed

- `PACIFICALLIANCE` now describes the Pacific Alliance's free trade agreement, the Additional Protocol to the Framework Agreement (signed 10 February 2014, in force 1 May 2016, parties Chile, Colombia, Mexico and Peru), instead of duplicating the alliance. The alliance with its associated state, candidates and observers stays `PACALL`. The Wikidata id Q7122288 stays on `PACALL` only; the Protocol has no Wikidata item and is listed in `wikidata_exclusions.yaml`. Costa Rica, Panama and Singapore are no longer listed on the trade agreement, which they are not parties to.
- The build no longer guesses: a YAML boolean in a text field (an unquoted `no` parses as False) fails with the record and field instead of becoming "yes"/"no", and a missing or invalid capital or headquarters coordinate no longer becomes 0 (missing stays null, invalid fails). No current record is affected.
- Club de Berne roster: Austria (re-admitted in 2022) and the United Kingdom are added, giving the 30 services of the 27 EU states, Norway, the United Kingdom and Switzerland that the cited source lists; `last_verified` is set.
- The World Bank groups `OEC` (High income: OECD) and `NOC` (High income: nonOECD) are `historical`, with `dissolved: '2016-07-05'`: the World Bank removed both in the July 2016 World Development Indicators update (Data Updates and Errata). Their last rosters are kept.
- ERRA roster refreshed from its members page: 37 full and 14 associate member regulators (`membership_count: 51`, `membership_count_type: organizations`). By country, 37 are `member` and 6 are `associate_member` (Algeria, Bahamas, Egypt, Fiji, France, United States); Austria, Latvia, Lithuania, Moldova, Nigeria, North Macedonia, Pakistan, Palestine, Russia and Ukraine are added, Kosovo is now a full member, and Ghana, Jordan and Peru are removed.
- `python scripts/<name>.py` and `pytest` now import the `internacia_builder` of the checkout they run in (`scripts/_checkout.py`, `pythonpath = ["."]`). Before, with an editable install from another checkout, a script in a git worktree silently ran the other checkout's code against its data; only `builder.py` had this guard.
- `scope_category` corrected for 21 informal intblocks that were classified as `igo`. Twenty become `policy_forum`: the five UN regional groups (AFRICANGROUP, ASIAPACIFICGROUP, EEG, GRULAC, WEOG), AG, ASPA, BASIC, CLUBDEBERNE, CTG, EUMED, GROUPOFFIVE, I2U2, LMDC, MIKTA, NB8, NINEEYES, PBP, QSD and UDCG. 3GC, a Citigroup classification, becomes `reference_enumeration`.
- Country provenance entries use `note`, like intblocks; 26 entries in 22 records used `notes`.
- World Bank classifications in `countries` were a pre-2016 snapshot that enrichment never refreshed, while provenance claimed a 2026-06-15 retrieval. The 217 economies the Bank classifies now carry its 2026-11-18 values with provenance pointing at the economy's API URL: 134 income levels change (the retired `OEC`/`NOC` codes become `HIC`; for example China and Indonesia `LMC` → `UMC`, Bangladesh `LIC` → `LMC`, Russia `UMC` → `HIC`), 93 lending types (`NC` → `LNX` and current IBRD/IDA/Blend status), Afghanistan and Pakistan move from `SAS` to `MEA`, region labels lose the `(all income levels)` suffix, and `adminregion` is dropped for high-income economies (absent now for 119 records). The 31 entities the Bank does not classify keep their inferred values, recoded to current ids; Mayotte and the Netherlands Antilles, no longer classified, have provenance `World Bank (historical classification)`.
- `wbgroup` rosters `HIC`, `UMC`, `LIC`, `EAS`, `SSF`, `ECA`, `MNA` and `SSA` now match the Bank's current classification (`memberships` grows from 59080 to 59094 edges). The nine regional groups take the Bank's current names (for example `MEA` is *Middle East, North Africa, Afghanistan & Pakistan*, `ECA` is *Europe & Central Asia (excluding high income)*); the old names are kept in `previous_names`.
- `languages[]` codes: ES Galician `glc` → `glg` (`glc` is Bon Gula), BZ Belize Kriol `bjz` → `bzj` (`bjz` is Baruga), NA Khoekhoe `hgm` → `naq` (`hgm` is Haiǁom), GG Guernésiais `nfr` → `nrf` (Norman; `nfr` is Nafaanra). CH gains German (`deu`, Federal Constitution Article 4) and XK gains Albanian and Serbian (`sqi`, `srp`, Constitution Article 5).
- Enrichment keeps a refreshed provenance entry at its position instead of moving it to the end of the list.
- `last_verified` set to 2026-10-25 for IPBES (151 coded members after the United States withdrew on 6 February 2026 and Slovenia joined on 9 February 2026; the Plenary 12 list prints both Eswatini and Swaziland, and the Council of the EU counts 152), the Global Fund (123 countries with an eligible or transition-funded component on the 2026 eligibility list), ICH (New Zealand and Pakistan added as observers; 25 members), the European Mathematical Society (52 full corporate members in 40 countries; Serbia added, and Belarus, Malta, and North Macedonia removed), EuChemS (42 societies in the same 35 countries), and FACS (the 31 coded societies match the member page; the Chemical Society of the South Pacific has no single country code).
- `last_verified` set to 2026-10-25 for the OFC (11 ordinary members in the March 2026 statutes; Kiribati and Tuvalu are associate members; Niue is not a member) and the Rio Group (24 members in the 29 September 2011 UN statement, including Suriname; CELAC succeeded the group on 3 December 2011).
- `last_verified` set to 2026-10-25 for the Global Health Security Agenda (71 countries on the membership page; international and non-government organizations on that page are not country rows).
- `last_verified` set to 2026-10-25 for the WMO (188 state parties in the US depositary list, including Grenada from 18 October 2026, plus French Polynesia, New Caledonia, Hong Kong, Macao and Curaçao; Curaçao and Sint Maarten are one member, and British Caribbean Territories is the uncoded sixth territory member) and the G5 Sahel (the five former members named in the 6 December 2023 Mauritania-Chad communique).
- `last_verified` set to 2026-10-25 for the BBNJ Agreement (104 parties in the UN Treaty Collection, including the European Union; signatories that have not ratified, accepted, approved or acceded are not parties, and the United States remains a signatory only).
- `last_verified` set to 2026-10-25 for the Global Partnership on Artificial Intelligence (46 member countries and the European Union, including Malta and Saudi Arabia; the fifteen founding members are unchanged).
- `last_verified` set to 2026-10-25 for ISO (177 national standards bodies: 135 member bodies, 38 correspondent members and 4 subscriber members; Congo, Liberia, Samoa, Sao Tome and Principe and Tonga are added, and Guinea and Mozambique are not on the members page), UNCTAD (195 members, adding the Holy See and the State of Palestine), UN Tourism (161 member states, including Saint Kitts and Nevis from 1 January 2026; associate members Aruba, Hong Kong, Macao and Puerto Rico; observers the Holy See and Palestine), the Security Council (the 2026 elected members replace the 2024 set), ECOSOC (the 54 members for 2026 match) and the Human Rights Council (the 47 members for 2026 match).
- `last_verified` set to 2026-10-25 for the Asia Cooperation Dialogue (35 member countries, including Palestine).
- `last_verified` set to 2026-10-25 for the OSJD (30 member countries as of 1 September 2026).
- `last_verified` set to 2026-10-25 for the IOC of UNESCO (153 member states as of 25 March 2026).
- `last_verified` set to 2026-10-25 for the IPU (184 member parliaments). Antigua and Barbuda, Barbados, Dominica, Eritrea, Grenada, Kiribati, Saint Kitts and Nevis, Solomon Islands, Sudan and the United States are not on the list.
- `last_verified` set to 2026-10-25 for the ITU (194 member states) and UNCITRAL (68 current members as of 7 July 2025).
- `last_verified` set to 2026-10-25 for UNESCO (194 member states and 12 associate members as of 1 January 2026; Israel withdrew effective 31 December 2018) and the IPCC (195 member countries).
- `last_verified` set to 2026-10-25 for FAO (193 member nations, the European Union, and associate members the Faroe Islands and Tokelau; the Cook Islands are a member nation; Nicaragua is a former member) and the IMO (176 member states and associate members the Faroe Islands, Hong Kong and Macao).
- `last_verified` set to 2026-10-25 for WOAH (183 members, including Curaçao, Liechtenstein, New Caledonia and Chinese Taipei), INTOSAI (194 country full members; the European Court of Auditors is the additional supranational full member) and IFAD (180 member states).
- `last_verified` set to 2026-10-25 for INTERPOL (196 member countries), the OACPS (79 members; Egypt, New Caledonia, French Polynesia and South Sudan are not on the annex, and the Cook Islands and Niue are), the Asian Parliamentary Assembly (44 member parliaments and 14 observer parliaments), IDLO (39 member states and the OPEC Fund, as of December 2025), UNIDROIT (65 member states) and the GEF (186 participants as of 13 April 2026; the Cook Islands, Niue, Palestine and Kosovo are added, and Cyprus, Iceland, Oman, Saudi Arabia, Singapore and the United Arab Emirates are not on the list).
- `last_verified` set to 2026-10-25 for SCOR (32 national committees; `membership_count` 32) and the ACS (25 members and 10 associates; Turks and Caicos is not a current associate).
- `last_verified` set to 2026-10-25 for the IMU (83 members and associate members Bangladesh, Mongolia and Paraguay; `membership_count` 85).
- `last_verified` set to 2026-10-25 for BSEC (13 members and 14 observers) and the UIC (84 countries in the January 2026 work programme; Indonesia, Pakistan and Qatar drop out, and Burkina Faso, Libya, Mexico and Niger are added).
- `last_verified` set to 2026-10-25 for WATAF (15 member administrations) and the Arms Trade Treaty (118 states parties as of 26 February 2026).
- `last_verified` set to 2026-10-25 for IICA (34 member states, plus the observers and associated Spain named on the country page), GICNT (77 partner nations and 4 observers), the Warsaw Pact (the eight UN-registered parties, all former), and PEPFAR (Barbados and Suriname replace Benin; the United States stays the funder).
- `last_verified` set to 2026-10-25 for CEN-SAD (25 members) and the United Nations Command (Korea added; Germany is a former medical contributor and has not returned; `membership_count` 18).
- `last_verified` set to 2026-10-25 for ECCAS (Rwanda added; 11 members), the Network of Tax Organizations (10 member organisations), and IFC-IOR (15 liaison-officer countries).
- `last_verified` set to 2026-10-25 for COPUOS (110 members in the 2025 UN list), EARAF (the eight EAC partner states), and IMSC (12 nations named by IMSC public affairs). AfCFTA signatories replace Eritrea with Western Sahara (54).
- `last_verified` set to 2026-10-25 for 14 rosters (and 2026-10-22 for ATAIC). Exact matches: SGATAR (19), the UN African Group (54), the UN Asia-Pacific Group (55), WEOG (29), the Cluster Munitions Convention (112 states parties; Lithuania withdrew 6 March 2025), the IHO (104, including Panama), PASC (27), IUBMB (76), AfricaRice (28), and the V20 (the same 74 members as the CVF). Corrections: Gavi adds Angola, Mozambique and Timor-Leste (56 eligible countries in 2026); COTA adds Curaçao, French Guiana and Martinique and records Sint Maarten as a member (24); Partnership for Peace records Finland and Sweden as former members on NATO accession (`membership_count` 18, with Belarus and Russia still signatories and cooperation suspended); the Group of 15 record is the 17-country forum, not the Logitech keyboard.
- `last_verified` set to 2026-10-22 for 24 rosters. Corrections: CEI replaces Austria with Belarus, suspended from participation since 25 March 2022; PAHO adds four associate members, three participating states and two observers (`membership_count` 39); AALCO adds Djibouti and Sierra Leone (49); MNNA is the 19 designated countries, with Taiwan treated as an ally without formal designation; MTCR adherents are cooperating states (`membership_count` 35); the AFC drops Israel; CONCACAF adds Grenada; SMIIC adds Syria and Togo (46 members and 3 observers); SCAR promotes Colombia, Czechia and Türkiye and adds four associate members (48); the NSG records the European Commission as an observer; the G-24 records China as a special-invitee observer; the EBU adds Canada (55); the GICHD council drops Norway.
- `last_verified` set to 2026-10-22 for 45 rosters checked against an official list. Corrections: IMF replaces Monaco with Andorra (191); CILSS adds Benin, Côte d'Ivoire, Guinea and Togo (13; Sudan and the Central African Republic have not formally joined); GUAM records Uzbekistan as a former member from 2005 (4); SKAO adds France from 4 June 2026 (14); ESA adds four associate members (Cyprus, Latvia, Lithuania, Slovakia) and four cooperating states (Canada, Bulgaria, Croatia, Malta), `membership_count` 27; SESAME observers are recorded and `membership_count` stays 8; IOM is 174 members and 8 observers; IOMed contracting states are 18; Combined Maritime Forces is 47 nations; the Australia Group includes the European Union (43); the Zangger Committee records the EU as a permanent observer (39 members); SELA's current members are 25 (Jamaica is a former member).
- `last_verified` set to 2026-10-22 for AFRIPOL. Membership is the police institutions of the 55 African Union member states; Western Sahara is added and `membership_count` is 55.
- `last_verified` set to 2026-10-22 for the China FTAs with Ecuador (in force 1 May 2024), Nicaragua (1 January 2024) and Serbia (1 July 2024).
- `last_verified` set to 2026-10-22 for the NPT nuclear-weapon states (China, France, Russia, the United Kingdom and the United States).
- `last_verified` set to 2026-10-22 for the Sava Commission (Bosnia and Herzegovina, Croatia, Serbia and Slovenia; Montenegro shares the basin and is not a party) and the SEECP (13 participants, including Kosovo).
- `last_verified` set to 2026-10-22 for the ICPDR (14 contracting parties plus the EU) and CICOS (Cameroon, the Central African Republic, Congo, the Democratic Republic of the Congo, Gabon and Angola).
- `last_verified` set to 2026-10-22 for the Niger Basin Authority (9), the Lake Chad Basin Commission (6 members and 3 observers), and the Australia FTAs with India, the United Kingdom and the United Arab Emirates.
- `last_verified` set to 2026-10-22 for OKACOM (3), OMVS (4), OMVG (4), the Volta Basin Authority (6), the Nile Basin Initiative (10 members; Eritrea added as an observer), ZAMCOM (8) and the Organization of Turkic States (5 members; Turkmenistan and the Economic Cooperation Organization added as observers).
- `last_verified` set to 2026-10-22 for CERN (25 member states and 11 associate member states), ITER (7), the CBSS (Russia withdrew on 17 May 2022; 11 members remain), ESO (16), the EFTA–India TEPA (5), CAFTA-DR (7) and CONMEBOL (10).
- `last_verified` set to 2026-10-22 for 24 rosters checked against an official list:
  APEC (21 economies), OIC (57, including Syria), BIMSTEC (7), ECO (10), CSTO (6),
  the European Defence Agency (the 27 EU member states), WHO (194; the United States
  remains listed while a withdrawal notification is pending before the governing bodies),
  ILO (187), WIPO (194), ICAO (193), the Paris Club (22 permanent members), OAPI (17),
  OHADA (17), ALADI (13), PICES (6 contracting parties), CEPGL (Burundi, the Democratic
  Republic of the Congo and Rwanda), USMCA and the historical NAFTA parties, the EU–New
  Zealand FTA, and the US FTAs with Australia, Chile, Korea and Singapore. D-8 adds
  Azerbaijan, a full member since 19 March 2025 (`membership_count` 9).
- Roster corrections checked against official lists on 2026-10-22: WTO `wikidata_id` is
  Q7825 (Q215524 is the village Riaville); Council of Europe records Russia as
  `former_member` from 1996-02-28 to 2022-03-16 (`CM/Res(2022)2`) and `membership_count`
  46; OPEC follows the member-countries page (12 current members, including the UAE, plus
  Qatar, Indonesia, Ecuador and Angola as former members with end dates). Tier-1 rosters
  re-checked from the roster-watch diff (OAS, BRICS, MERCOSUR, SCO, CIS, Commonwealth,
  African Union, CELAC, SAARC, PIF) were left in place where the official list supports
  them, with `last_verified` refreshed.
- Tier-1 `last_verified` stamps for rosters that match an official list on 2026-10-22:
  UN (193), EU (27), NATO (32), ASEAN (11, including Timor-Leste), OECD (38), G7 (7),
  SADC (16) and the EAEU (5). The G20 roster adds the African Union (21 members).
  CARICOM associate members are Anguilla, Bermuda, the British Virgin Islands, the
  Cayman Islands, Curaçao, French Guiana, Martinique and the Turks and Caicos Islands
  (`membership_count` 23). APEC and the OIC were left unchanged: their member pages
  could not be retrieved.

### Data changes since the previous release

- Countries: 256 → 256 records; 256 changed
- Intblocks: 1275 → 1275 records; 893 changed
- Blocktypes: 78 → 78 records
- Membership edges: 59466 → 59072; 342 added, 736 removed, 140 changed

## [3.1.0] - 2026-10-22

Snapshot: **256** countries, **1275** intblocks, **78** blocktypes. Planned as **3.1.0**:
`scope_category` and alias `reason` are open enums, so new values are a MINOR change;
consumers must accept unknown values.

### Removed

- Unused Docusaurus blog templates (`website/blog/`; the site has `blog: false`).
- `data/_legacy/` (pre-1.0 Airtable snapshots; history remains in git and Zenodo) and the unused
  `data/datasets/schema_baseline/`.
- `dataquality/` is no longer committed; the quality report is a CI artifact (`validate.yml`), and
  the enrichment workflow no longer commits it.
- `TELESUR` (La Nueva Televisión del Sur C.A.) and its seven country rows: a Venezuelan commercial company, not an intergovernmental organization. The ID is kept in `intblocks_aliases` with `reason: retired` and a null `target`; do not remap it. See [retired intblock IDs](docs/retired-intblock-ids.md).

### Added

- Monthly release train (`docs/release-train.md`): `release-train.yml` opens a release PR when the
  data changed since the last tag, choosing PATCH or MINOR from the versioning policy and stopping
  on MAJOR changes; merging it tags the release (`release-tag.yml`), and `release.yml` notifies
  internacia-python and internacia-api. `scripts/prepare_release.py` runs the same plan locally.
  Needs the internacia-bot GitHub App.
- `migration.vX.Y.Z.json` has a `data` section: record ids added, removed and changed, and
  membership edges added, removed and changed since the previous release.
- Weekly roster watch (`.github/workflows/roster-watch.yml`, `scripts/roster_watch.py`,
  `docs/roster-watch.md`): compares tier-1 rosters with Wikidata current memberships and keeps one
  `roster-drift` issue per organization (opened, updated on change, closed when resolved). It
  never edits data. The first run reports 19 of 29 organizations with differences, including a wrong
  WTO `wikidata_id` (Q215524 is a village; WTO is Q7825).
- `last_verified` KPI: never-verified and overdue intblocks overall (12-month window) and for the
  29 tier-1 organizations in the new `data/watch/rosters.yaml` (6-month window), written to
  `dataquality/last_verified_kpi.json`, printed by `scripts/last_verified_report.py` and added to
  the CI job summary. Currently 298 of 1275 never verified; tier 1: 21 of 29.
- Validation error for intblocks that are new or changed since the pull request base without
  `last_verified`, and for `includes` changes that do not update it.
- CI and the release workflow run the internacia SDK's portable `tests/contract` suite against
  the freshly built `internacia.duckdb` (`INTERNACIA_SDK_REF`), so a change that breaks the SDK
  fails here before it is released.
- `internacia.duckdb` contains the alias and migration tables (`intblocks_aliases`,
  `countries_aliases`, `attribute_intblock_migrations`) and canonical views:
  `current_memberships` (not former, no `left` date, organization neither historical nor
  dissolved), `country_currencies`, `country_languages`, `country_timezones`. They are listed in
  `contract.json` with their SQL, checked against an independent computation in
  `check_generated_artifacts.py`, and readable by DuckDB 1.1+. Cookbook section "Canonical views".
- Identifier stability gate: the validators fail when an intblock ID or country code from the
  latest release tag has neither a record nor an alias entry.
- `contract.json`: machine-readable consumer contract (tables, columns, logical types,
  nullability, primary/foreign keys, open enum values, `contract_version`, `min_duckdb`, DuckDB
  storage compatibility). Generated from the schemas, committed, and attached to releases. See
  `docs/data-contract.md`.
- `SHA256SUMS` covering every file of the bundle (rewritten after the release adds
  `migration.vX.Y.Z.json`). Manifests list `sha256`/`bytes` per file; `datapackage.json` resources
  carry `bytes`, `hash` and (Parquet) a Table Schema.
- `contract_version` in manifests, `.meta.json` sidecars and DuckDB `_meta` (additive column).
- `TARAGREEMENT`: the [Intergovernmental Agreement on the Trans-Asian Railway Network](https://treaties.un.org/pages/viewdetails.aspx?src=treaty&mtdsg_no=xi-c-5&chapter=11&clang=_en), with **22 treaty parties** as of 2026-09-30, separate from the `TAR` network and its 28-country reach. The `TAR` Wikidata ID stays on the network.
- **6 major multilateral treaty intblocks** (official rosters verified 2026-09-30): Fourth Geneva Convention `GCIV` (196 parties, ICRC), Biological Weapons Convention `BWC` (189, UNODA), World Heritage Convention `WORLDHERITAGE` (196, UNESCO), SOLAS 1974 `SOLAS` (168 contracting states, IMO), MARPOL 73/78 `MARPOL` (162, IMO), and the 1954 Hague Convention `HAGUE1954` (138, UNESCO). Territorial applications are excluded from IMO rosters.
- Alias `reason: retired` for IDs removed without a replacement. Retired aliases have no `target` in the source and a null `target` in `intblocks_aliases.json`.

### Changed

- The monthly enrichment opens one pull request per source (World Bank indicators and
  classifications, Wikidata country names, IANA time zones, intblock metadata) instead of one
  `chore/monthly-enrichment` PR. PRs whose changes only fill values, add items or stay within
  `data/schemas/enrichment_sources.yaml` thresholds merge automatically; others are labelled
  `needs-review`. The changed-record rule no longer requires `last_verified` for metadata-only
  intblock changes.
- Per-platform agent files (`CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/skills/`,
  `.lingma/rules/`, `.kimi/AGENTS.md`, `.agent/workflows/` except the OpenSpec-managed ones) and
  `llms-full.txt` are generated from `templates/` by `scripts/generate_agent_shims.py`; CI runs it
  with `--check`. Shared guardrails, data-access and validation text now live in one place and
  reflect that exports must be built first. Hand-maintained: `AGENTS*.md`, `llms.txt`,
  `llms.zh.txt`, `docs/agents/`.
- One-off migration scripts moved to `scripts/oneoff/` (with a README).

- LLM tool definitions now come from the internacia SDK (`internacia.tools`, SDK 0.4+).
  `data/schemas/{country,intblock}_lookup.openai.json` are deprecated and will be removed one
  MINOR release after that SDK release (OpenSpec change `deprecate-llm-tool-schema-files`).
- Superseded reviews and plans (`REPOSITORY_REVIEW*.md`, `dev/internacia-db-review.md`,
  `outputs/*.md`, `docs/improvement-plan.md`) moved to `docs/history/`, which the documentation
  site does not publish.
- All 29 completed OpenSpec changes are archived and their deltas applied to `openspec/specs/`;
  the four tasks left open were closed (done, moved to issue #21, or won't do with rationale).

- **Generated exports are no longer committed** (decision D3). `data/datasets/` keeps only the
  manifests, `contract.json`, `datapackage.json`, the dataset card and the alias JSON; Parquet,
  DuckDB, JSONL, YAML and CSV come from `python scripts/builder.py build` or the GitHub Release.
  Release assets are unchanged. Tests build `data/datasets/` on first run if it is missing.
- **Reproducible builds.** Source files are read in sorted order, `build_date` is the commit time
  (or `SOURCE_DATE_EPOCH`) and `git_commit` the built commit. CI builds twice and requires
  identical files (DuckDB: identical table contents) and committed descriptors that match the
  build (`scripts/check_committed_snapshot.py`, `scripts/check_reproducible_build.py`).
- `generate_schema_migration.py` reads the previous release's export schema from its committed
  `contract.json` when its Parquet files are not in git.
- `schema_hash` is now the SHA-256 (full 64-hex digest) of the canonical column list
  `[name, logical_type, nullable]`, independent of the pyarrow version. All hash values change
  once. Primary-key columns are declared non-nullable, so Parquet marks them `required`.
- `internacia.duckdb` is written with an explicit `storage_compatibility_version` (`v1.0.0`, the
  format already in use).
- Country crosswalks now use curated official-source snapshots with field-level provenance and machine-readable eligibility exceptions (`data/schemas/country_crosswalk_sources.yaml`, `data/schemas/country_crosswalk_exclusions.yaml`): GeoNames covers all 249 current ISO records, IOC covers 206 mapped NOCs, FIFA covers 207 mapped Member Associations, and FIPS remains explicitly legacy-only. Columnar schemas are unchanged; populated values grow from about 118 per field to 206–251.
- The validators and `analyze-quality` run one rule registry
  (`internacia_builder/validate/registry.py`, issue #21). `analyze-quality` now also reports
  invalid attribute fields, missing intblock `wikidata_id` and `partof` targets that are treaties,
  and files crosswalk and attribute-migration issues as IMPORTANT, so the quality gate fails on
  every validator error. `validate_intblocks.py` now warns about intblock provenance integrity and
  freshness. On the current data neither output changes.
- `validate_countries.py` and `validate_intblocks.py` run about 4–5 times faster (YAML is parsed
  with libyaml when available, and each file once).
- Intblock `scope_category` accepts `intergovernmental_body` and `non_state_organization` in addition to the four existing values. **Closed-enum consumers must update their parsers.** Reviewed subsidiary commissions, offices, funds and NGOs are classified by legal entity rather than parent/beneficiary geography; invalid country-member rosters are removed instead of being exported as memberships.
- Formal intblocks now **require** `scope_category`: the validator treats an omission or unknown value as an error and the quality analyzer as IMPORTANT, and the `max_missing_formal` ratchet is now 0 (`MSF` and `CANTO` are `non_state_organization`). The legacy directory heuristic in `scripts/oneoff/label_scope_category.py` is suggestion-only.
- 22 formal records change category after source review, replacing the 3.0.0 classification and its generic provenance with the cited source: eight FAO commissions (`APFIC`, `CECAF`, `CIFAA`, `CODEX`, `COPESCAALC`, `EIFAAC`, `SWIOFC`, `WECAFC`), the funds `ADF`, `AF` and `CIF`, the GCC patent office `GCCPO`, and `RDR` become `intergovernmental_body`; `ACIL` becomes `non_state_organization`; `CACM`, `PETROCARIBE` and `TRACECA` become `treaty_body`; `AMERIPOL`, `CELSE`, `CKURAILWAY`, `PACALL` and `TAR` become `policy_forum`. `PACALL` cites the Alianza del Pacífico glossary, which describes a regional integration process constituted by the Framework Agreement, not an organization with separate juridical personality.
- `CIF` now describes the standing CTF+SCF partnership, not its 15 dated contributors; `TAR` remains the ESCAP network platform, not a treaty-party roster. Neither exports country-membership edges, and CIF no longer claims `partof: WB`.
- Six reviewed non-formal intblocks gain sourced `scope_category` values: `ARABW`, `BALTICSTATES`, `HISPAM`, `MIDAMERICA` and `SLAVISPHERE` are `reference_enumeration`; the Common Monetary Area (`CMA`) is `policy_forum`. Their country links are unchanged. **72 non-formal records remain unlabeled.**
- The `wbgroup` display label is now "World Bank classification group" to distinguish statistical aggregates from World Bank institutions.

### Fixed

- Citation metadata now uses the Zenodo concept DOI `10.5281/zenodo.20706176`
  (`CITATION.cff`, README badge, `ATTRIBUTION.md`, docs, dataset card). The
  previously cited `10.5281/zenodo.21452328` is the v1.7.0 version DOI.
- The release workflow no longer has its own Zenodo deposit step; the Zenodo
  GitHub integration is the only depositor, so each release gets one version.
- The release version gate (`scripts/check_release_bundle.py --version`) also
  checks `CITATION.cff` `version` and `date-released` against `CHANGELOG.md`.
- `attribute_intblock_migrations` `since` is `2.0.0` (the release that retired
  these intblocks) instead of `Unreleased`.
- Removed the stale committed `data/datasets/migration.vUnreleased.json`; schema
  migrations ship as `migration.vX.Y.Z.json` Release assets.
- Corrected four crosswalk conflicts against official snapshots: Bahrain GeoNames id (`290291`), Latvia FIFA code (`LVA`), Singapore FIFA code (`SGP`), and Kosovo FIFA code (`KOS`).
- Country validation now requires field-level provenance for every populated crosswalk and rejects duplicate external identifiers or incomplete eligibility policy.
- `AFDF` is a legally independent `igo` with the **29 State Participants** in the African Development Fund voting statement dated 2025-09-30, instead of 82 mixed country links (53 removed). It no longer asserts `partof: AFDB`.
- All 25 World Bank regional, income, lending and analytical groups use `scope_category: reference_enumeration` instead of `igo`; a validator rule keeps `wbgroup` records out of organization categories.
- False country rosters were removed from dependent bodies and NGOs (for example `ACIL`, `MSF`, `CANTO`), which now set `membership_applicability: not_applicable`.

### Documentation

- SDK status: `internacia` 0.2.x (PyPI) predates data v3 — it cannot download
  current releases, `search.fuzzy` fails, `get_by_member` includes former
  memberships, and `get_by_id` ignores aliases. `docs/llm-scenarios.md`,
  `docs/when-to-use-internacia.md`, `docs/getting-started.md`, and `llms*.txt`
  now say so and give DuckDB SQL equivalents (tested in `tests/test_release_docs.py`).
- internacia-api is described as in development / experimental rather than a
  shipped REST API or "reference implementation".
- `docs/release-distribution.md` lists the exact Release assets and states that
  the GitHub Release assets are the bundle of record for each version.

### Data changes since the previous release

- Countries: 256 → 256 records; 251 changed
- Intblocks: 1269 → 1275 records; added `BWC`, `GCIV`, `HAGUE1954`, `MARPOL`, `SOLAS`, `TARAGREEMENT`, `WORLDHERITAGE`; removed `TELESUR`; 64 changed
- Blocktypes: 78 → 78 records; 1 changed
- Membership edges: 58649 → 59466; 1071 added, 254 removed, 4 changed
- New intblocks aliases: `TELESUR`
- Schema (minor): table country_currencies added
- Schema (minor): table country_languages added
- Schema (minor): table country_timezones added
- Schema (minor): table current_memberships added
- Schema (minor): enum intblocks.scope_category values added: intergovernmental_body, non_state_organization

## [3.0.0] - 2026-10-16

Data integrity and release validation: **256** countries, **1269** intblocks,
**78** blocktypes, and **58694** membership edges.

### Breaking

- Three duplicate intblock IDs are retired: `COMMLEARN` → `COL`, `ABCZNZ` →
  `ABCANZ`, and `USAN` → `UNASUR`. Normalize stored keys through
  `intblocks_aliases.json` or `intblocks_aliases.parquet` before joining the new
  exports. Alias mappings are retained indefinitely. Country identifiers and
  columnar schemas are unchanged.
- Frictionless resource names now identify both table and format (for example,
  `countries-parquet`); consumers selecting resources by name must update their
  selectors. Resource paths and table names are unchanged.

For a downstream table with an `intblock_id` column:

```sql
SELECT d.* EXCLUDE (intblock_id),
       coalesce(a.target, d.intblock_id) AS intblock_id
FROM downstream AS d
LEFT JOIN read_parquet('data/datasets/intblocks_aliases.parquet') AS a
  ON d.intblock_id = a.alias AND a.reason = 'merged' AND a.since = '3.0.0';
```

### Fixed

- Documentation query examples now use valid DuckDB struct aliases and quoted
  departure-date columns, country `code` keys, and Polars fields available in the
  selected export. Cookbook expectations match the current repository snapshot;
  UN full-member comparisons explicitly exclude observer seats.
- Contributor guides now require a full export rebuild with source changes before
  CI's committed-artifact check. README and release guides describe current
  staging, metadata, tag-version, and recursive schema-migration checks.
- Manual Hugging Face publishing uses the same validated Parquet bundle as CI,
  including rewritten descriptor paths and all four tables' metadata. Zenodo
  guidance now describes draft creation and upload before maintainer publication.
- Artifact validation now checks complete source projections, values, duplicate keys,
  membership edges, schema hashes, and required metadata before CI rebuilds exports.
- Enrichment refreshes usable provider-backed observations without renewing untouched
  provenance; unknown years and partial inception dates retain honest precision.
- ECOWAS retains Mali, Burkina Faso, and Niger as former members from 2025-01-29,
  with 12 current members. Duplicate IDs `COMMLEARN`, `ABCZNZ`, and `USAN` are merged
  into `COL`, `ABCANZ`, and `UNASUR`; use the alias map for existing consumer keys.
  The catalogue now contains 1269 canonical intblock records. Columnar schemas are unchanged.
- Release tests inspect final staging artifacts and enforce quality/version checks.
  Migration diffs compare recursive source/export contracts with the prior release.
- Frictionless resources now have unique table/format names (`countries-parquet`,
  `countries-csv`, etc.) and each distribution descriptor resolves within its bundle.
- Full-membership queries use member/founding_member explicitly; historical joins
  preserve known identifiers such as `SU`. Formal scope omissions fell from 114
  to two documented NGO taxonomy exceptions; validator/analyzer warnings agree.
- Documentation builds and typechecks run on PRs; repository-external docs links
  are resolved before rendering and broken links fail the site build.

## [2.2.0] - 2026-09-16

### Changed

- `WAICO` roster aligned to the [Wikipedia membership list](https://en.wikipedia.org/wiki/World_Artificial_Intelligence_Cooperation_Organization) (retrieved 2026-09-14): 37 members (adds Dominica on 30 July 2026 and Brunei, Georgia, Iran, Sudan, Tanzania, Togo, and Vietnam on 31 July 2026) plus Bangladesh as an observer from 1 August 2026.
- `BRICS` roster aligned to the [India 2026 chairship About page](https://www.brics2026.gov.in/about-us/): 11 full members (adds Saudi Arabia from January 2024) and 10 partner countries that joined in 2025 (Belarus, Bolivia, Cuba, Kazakhstan, Malaysia, Nigeria, Thailand, Uganda, Uzbekistan, Vietnam).
- Country display names updated to current official short forms, with the former names kept in `common_names`: `MK` North Macedonia (was "Macedonia, FYR"), `SZ` Eswatini (was "Swaziland"), `CV` Cabo Verde (was "Cape Verde"), `TR` Türkiye (was "Turkey").

## [2.1.0] - 2026-09-09

Intblock catalogue expansion: **256** countries, **1272** intblocks (**1037 → 1272**), **78** blocktypes. Adds 235 named treaties, FTAs, PTAs, IIAs, standing IGOs, and geographic groups.

### Changed

- Intblock inclusion policy now has explicit bars for WTO RTA-IS, WTO PTA Database, and UNCTAD IIA Navigator candidates ([docs/intblock-inclusion-policy.md](docs/intblock-inclusion-policy.md)): named durable join targets only; untitled bilaterals, constitutive IGO instruments, and not-in-force protocols stay out.
- Agent routing treats discovery as a first-class job: [docs/discovery.md](docs/discovery.md), [docs/agents/discover.md](docs/agents/discover.md), Cursor skill `internacia-discover`, and `.agent/workflows/discover-intblock.md`.
- `AANZFTA` moved from `intorg/` to `fta/`. `TPP` now records `TPSEP` as predecessor. `GSP` grantors include the Kyrgyz Republic.

### Fixed

- Medium-priority data-quality issues: aligned `membership_count` with `includes` on 48 intblocks; added missing `partof` on `ALLPI` (COMESA), `CAC`, `INCAP`, and `COMTELCA` (SICA); populated the UN-OHRLLS 39-sovereign `SIDS` roster (and removed WMO fields copied onto that record); compiled Wikipedia visa-not-required destinations for `VISAFBR`, `VISAFGE` (provenance only), `VISAFIR`, `VISAFJP`, `VISAFRU`, `VISAFSA`, `VISAFUK`, and `VISAFUS`.
- Low-priority data-quality issues: `partof: UN` on `IAEA`, `IFAD`, `IMO`, `UNWTO`, and `UPU`; `EARAF` nested under `EAC`; allowlisted real-world English acronym collisions (`COL`, `IAF`, `ABCANZ`, `ABCA`, `G5`); dropped shared catalogue/parent homepage `links` from non-canonical records (WTO RTA-IS/PTA indexes, ICAO/INTOSAI lists, World Bank grouping pages, and parent-org sites kept on the parent).
- DuckDB query cookbook no longer claims Parquet/DuckDB omit `includes[].left` (the field is exported on `includes` and on `memberships`).

### Added

- **31 Wikipedia `.int` standing IGO intblocks** (retrieved 2026-09-09): remaining named treaty IGOs from the [Wikipedia `.int` list](https://en.wikipedia.org/wiki/List_of_organizations_with_.int_domain_names) with official rosters, including `ALLPI`, `ALSF`, `BOIP`, `CAC`, `CAFRAD`, `CEDARE`, `COMTELCA`, `CTU`, `EACO`, `EASF`, `ECB` (21 euro-area members including Bulgaria from 2026-01-01), `ECSAHC`, `ECTEL`, `GCAP`, `GLFC`, `IAI`, `ICMP`, `ICPE`, `ICSTI`, `IICAS`, `IGC`, `INCAP`, `INL`, `ISTC`, `IVI`, `JINR`, `OSC`, `RECSA`, `RESPA`, `STCU`, and `VPI`. Dissolved or non-IGO `.int` holders, internet-infrastructure domains, and organs whose membership is identical to a parent already recorded (EFTA Court, Benelux Court, SIECA/SISCA) are not imported. `CEDARE` and `ICSTI` have no published states-parties roster (`membership_applicability: not_applicable`).
- **7 UNCTAD IIA Navigator plurilateral investment intblocks** (retrieved 2026-09-09): wave 1 `OICIA` (29 ratifiers), `ACIA` (11 parties), `UAIA` (20 parties), and `CISFTASERVICES` (7 parties); wave 2 `CJKIA` (China–Japan–Korea trilateral investment agreement) and `INTRAEUBIT` (intra-EU BIT Termination Agreement, 23 of 27 EU members); wave 3 `PCFI` (Intra-MERCOSUR investment protocol, 3 ratifiers in force). SADC FIP and the ECOWAS Supplementary Act on Investments are noted on `SADC` and `ECOWAS` rather than duplicated. Bilateral BITs, FTA investment chapters of records already present, and not-in-force protocols (AfCFTA Investment Protocol, COMESA CCIA, Protocol of Colonia) are not imported. Inclusion bar for IIAs documented in [docs/intblock-inclusion-policy.md](docs/intblock-inclusion-policy.md).
- **17 geographic reference-enumeration intblocks** (retrieved 2026-09-09): UN M49 subregions `SOUTHAMERICA`, `NORTHAMERICA` (Northern America; distinct from continent/`NAC`), `EASTASIA`, `SOUTHASIA`, `WESTASIA`, `NORTHAFRICA`, `WESTAFRICA`, `EASTAFRICA`, `SOUTHERNAFRICA`, `EASTERNEUROPE`, `WESTERNEUROPE`; named regions `SAHEL`, `LEVANT`, `ARABIANPENINSULA`, `SCANDINAVIA`, `IBERIA`, `GUIANAS`. Rosters from UNSD M49 or Wikipedia regional definitions; `NORDICC` remains the broader Nordic set.
- **4 WTO PTA Database intblocks** (retrieved 2026-09-09): named non-reciprocal waiver programmes `AGOA`, `CBERA` (CBI; CBTPA recorded as a sub-scheme), and `CARIBCAN`; EU GSP+ arrangement `GSPPLUS` (eight-country beneficiary roster). National GSP/DFQF ID cards, Everything But Arms, and untitled bilateral preferences are not imported. `GSP` grantors now include the Kyrgyz Republic. Inclusion bar for WTO PTAs documented in [docs/intblock-inclusion-policy.md](docs/intblock-inclusion-policy.md).
- **8 United States bilateral FTA intblocks (wave 3)** (retrieved 2026-09-09): `USIL`, `USJO`, `USMA`, `USBH`, `USOM`, `USPE`, `USCO`, `USPA`. Completes the remaining named U.S. FTAs alongside existing `USMCA`, `CAFTADR`, `USKR`, `USAU`, `USCL`, `USSG`, and `USCR`. CAFTA-DR country slices other than the existing Costa Rica record are not duplicated.
- **14 named WTO-notified FTA intblocks (wave 2)** (retrieved 2026-09-09): EU partnerships `CETA`, `EUJP`, `EUUK`, `EUKR`, `EUVN`, `EUSG`, `EUUA`, `EUANDEAN`; bilateral `CHAFTA`, `CNKR`, `UKJP`, `UKIN`, `UKNZ`, `INUAE`. UK–India uses id `UKIN` (the acronym CETA remains the EU–Canada agreement).
- **11 WTO-notified regional trade agreement intblocks** (rosters from official treaty texts and WTO RTA-IS, retrieved 2026-09-09): named plurilaterals `AGADIR`, `ANZCERTA`, `PICTA`, `TPSEP`; ASEAN+1 FTAs `ACFTA`, `AJCEP`, `AKFTA`, `AIFTA`, `AHKFTA`; bloc-to-bloc `EFTAGCC` and `EFTASACU`. `AANZFTA` moved from `intorg/` to `fta/`. `TPP` now records `TPSEP` as predecessor. Inclusion bar for RTAs documented in [docs/intblock-inclusion-policy.md](docs/intblock-inclusion-policy.md).
- **47 UN Treaty Collection treaty intblocks** (states-parties rosters from treaties.un.org, retrieved 2026-09-09): nine core human-rights treaties plus the Genocide Convention (`GENOCIDE`, `ICERD`, `ICESCR`, `ICCPR`, `CEDAW`, `CAT`, `CRC`, `ICMW`, `CRPD`, `CPED`); refugee and statelessness instruments (`REFUGEECONVENTION`, `REFUGEEPROTOCOL`, `STATELESS1954`, `STATELESS1961`); Vienna diplomatic/consular/treaty law (`VCDR`, `VCCR`, `VCLT`); crime, health, and commercial law (`UNTOC`, `UNCAC`, `FCTC`, `NYC`, `CISG`); optional protocols with distinct party lists (`ICCPROP1`, `ICCPROP2`, `OPCAT`, `OPCEDAW`, `OPCRCAC`, `OPCRCSC`, `OPCRPD`, `PALERMOTIP`, `PALERMOSOM`, `PALERMOFIREARMS`, `FCTCITP`, `KIGALI`); and environment, drugs, and disarmament instruments (`MINAMATA`, `AARHUS`, `ESCAZU`, `CLRTAP`, `ESPOO`, `UNECEWATER`, `UNWATERCOURSES`, `SINGLECONVENTION`, `PSYCHOTROPIC`, `UNDRUGS1988`, `CCW`, `ENMOD`, `UNFSA`). Constitutive acts of existing IGOs (UN Charter, WHO Constitution, Rome Statute) are not duplicated.
- **16 further UNTC treaty intblocks** (retrieved 2026-09-09): UN privileges (`CPIUN`); remaining human-rights protocols and instruments (`ICESCROP`, `OPCRCIC`, `POLITICALWOMEN`, `CONSENTMARRIAGE`, `SLAVERY1956`); counter-terrorism and related penal treaties (`HOSTAGES`, `PROTECTEDPERSONS`, `UNSAFETY`, `TERRORBOMB`, `ICSFT`, `ICSANT`); transport and commercial instruments (`TIR1975`, `ROADTRAFFIC1968`, `SINGAPOREMEDIATION`); and the Tampere disaster-telecom convention (`TAMPERE`). The UN Cybercrime Convention (`UNCYBERCRIME`) is omitted until it has a real states-parties roster.
- **20 further UNTC treaty intblocks** (retrieved 2026-09-09): specialized-agency privileges and diplomatic law (`CPISA`, `SPECIALMISSIONS`); apartheid, statutory-limitations, trafficking, and nationality instruments (`APARTHEID`, `APARTHEIDSPORTS`, `STATUTORYLIMITATIONS`, `TRAFFICPERSONS`, `NATIONALITYMARRIED`); mercenaries and UN-safety protocol (`MERCENARIES`, `UNSAFETYOP`); UNCLOS Part XI implementing agreement (`UNCLOSPARTXI`); investor-state transparency and succession (`MAURITIUS`, `SUCCESSION1978`); UNECE environment protocols (`INDUSTRIALACCIDENTS`, `WATERHEALTH`, `PRTR`); and transport/customs instruments (`CMR`, `ADR`, `ROADSIGNS1968`, `CONTAINERS1972`, `FRONTIERCONTROLS`). Agency P&I annexes, IMO/ICC constitutive texts, and not-in-force instruments (jurisdictional immunities, VCLT-IO) are not duplicated.
- **19 further UNTC treaty intblocks** (retrieved 2026-09-09): land-locked transit and UNCITRAL commercial law (`LANDLOCKEDTRANSIT`, `LIMITATIONCISG`, `IGSBLC`, `ELECTRONICCOMM`, `PAPERLESSTRADE`); UNESCO/WIPO cultural and neighboring-rights instruments (`FLORENCE`, `NAIROBIPROTOCOL`, `ROME1961`, `PHONOGRAMS`, `BRUSSELSSATELLITE`); slavery as amended (`SLAVERY1926`, with `SLAVERY1956` nested via `partof`); ICC privileges (`APIC`); maintenance recovery (`MAINTENANCE1956`); European commercial arbitration (`EUROARBITRATION`); UNECE road/food transport (`AETR`, `ATP`); Espoo SEA protocol (`KIEVSEA`); CMS small-cetacean agreement (`ASCOBANS`); and ship arrest (`ARRESTSHIPS`). The Beijing Convention on the Judicial Sale of Ships is omitted until it has at least five states parties. Constitutive acts of existing IGOs (WHO, AfDB, ADB, IFAD, UNIDO, APT, South Centre) are not duplicated.
- **17 further UNTC treaty intblocks** (retrieved 2026-09-09): Geneva 1949 road traffic (`ROADTRAFFIC1949`); WP.29 vehicle agreements (`UN1958AGREEMENT`, `UN1998AGREEMENT`, `UN1997AGREEMENT`); CMR protocols (`ECMR`, `CMRPROTOCOL`); Asian Highway and E-road networks (`ASIANHIGHWAY`, `AGR`); CPD temporary-importation carnet (`CPD`); Vienna diplomatic/consular disputes optional protocols (`VCDROP`, `VCCROP`); ITLOS and ISA privileges (`ITLOSPI`, `ISAPI`); Cartagena liability protocol (`NAGOYAKL`); Lusaka wildlife-enforcement agreement (`LUSAKA`); Food Assistance Convention (`FOODASSIST`); and UNESCO Beirut audiovisual agreement (`BEIRUT`). Individual UN Regulations, commodity-era coffee/cocoa/sugar pacts, and constitutive acts of existing IGOs are not duplicated.
- **14 further UNTC treaty intblocks** (retrieved 2026-09-09): UNECE inland/combined-transport network agreements (`ADN`, `AGN`, `AGC`, `AGTC`, `DRYPORTS`); maritime carriage and liens (`HAMBURGRULES`, `MARITIMELIENS`); customs/tourism instruments (`SAMPLES`, `TOURING`, `TEMPIMPORTCOMM`); 1958 Geneva law-of-the-sea conventions still in force for some non-UNCLOS parties (`HIGHSEAS1958`, `CONTINENTALSHELF`, `TERRITORIALSEA`); and the European supplement to the 1968 Road Traffic Convention (`EURO1968TRAFFIC`, `partof: ROADTRAFFIC1968`). The Rotterdam Rules are omitted until they enter into force. The 1958 Fishing and Conservation Convention and a second Trans-Asian Railway treaty (already covered by `TAR`) are not duplicated.
- Mermaid diagram rendering on the documentation website (`@docusaurus/theme-mermaid`), so existing `mermaid` code blocks in `docs/` display as diagrams instead of plain text.
- Documentation: discovery and improvement guide ([docs/discovery.md](docs/discovery.md), [docs/agents/discover.md](docs/agents/discover.md)) for searching catalogues and raising country / intblock quality — hunt patterns from UNTC, WTO RTA-IS / PTA, UNCTAD IIA, Wikipedia `.int`, and UN M49 sessions; official-roster repair loop; country enrichment without new socioeconomic fields.
- Documentation: intblock discovery catalogues and roster sources ([docs/intblock-sources.md](docs/intblock-sources.md)) for the UN Treaty Collection, WTO RTA-IS, WTO PTA Database, UNCTAD IIA Navigator, and Wikipedia `.int` organization searches used to compile recent treaty, FTA, PTA, IIA, and IGO records.
- Documentation: [ATTRIBUTION.md](ATTRIBUTION.md) now lists intblock catalogues and roster authorities (UNTC, WTO, UNCTAD, Wikipedia `.int`, official IGO/treaty sites, Wikidata for entity linking only).
- Documentation: dataset SemVer and self-host API posture ([docs/versioning-policy.md](docs/versioning-policy.md)); intblock id/category conventions; display-name and `parent_entity` policy; validator exit codes; docs-count CI guard; Chinese query/contribute coverage; website sidebar no longer presents historical planning docs as current.
- Intblock `JEF` (Joint Expeditionary Force) — UK-led Northern European military partnership (10 members).
- Intblock `NORTHSEASUMMIT` (North Sea Summit) — informal North Sea energy summit series (9 members + Iceland observer).
- Intblock `UPOV` (International Union for the Protection of New Varieties of Plants) — plant variety protection IGO (80 members).
- Intblock `ARC` (African Risk Capacity) — AU specialized agency for climate disaster risk financing (39 members).
- Intblock `COSPASSARSAT` (International Cospas-Sarsat Programme) — satellite-aided search-and-rescue IGO (45 participants).
- Intblock `EFI` (European Forest Institute) — European forest research IGO (30 member states).
- Intblock `CRFM` (Caribbean Regional Fisheries Mechanism) — CARICOM fisheries institution (17 members).
- Intblock `GMCO` (Gulf Monetary Council) — GCC monetary-union preparatory body (4 members: BH, KW, QA, SA).
- Intblock `OIML` (International Organization of Legal Metrology) — legal metrology treaty IGO (129 members).
- Intblock `RIMES` (Regional Integrated Multi-Hazard Early Warning System for Africa and Asia) — multi-hazard early warning IGO (22 members + 26 collaborating states).

## [2.0.0] - 2026-08-04

Dataset rebuild after attribute-partition retirement and Kosovo rename: **256** countries,
**1037** intblocks (**1078 → 1037**), **78** blocktypes (**86 → 78**).

### Changed

- **BREAKING:** Attribute-partition intblocks retired (`dvdregion`, `govform`, `lawsystem`, `railgauge`, `teleregion`, `traffichand`, `writingdirection`, `writingsystem`). Values now live on country records (except government form, which is vocab-only and out of countries scope). Remap retired ids via `attribute_intblock_migrations.json`.
  - Before: `SELECT … FROM intblocks, UNNEST(includes) … WHERE id = 'RHTRAFFIC'`
  - After: `SELECT code, name FROM countries WHERE car_side = 'right'`
- **BREAKING:** Kosovo country code renamed `KV` → `XK`, alpha-3 `KSV` → `XKX`; legacy codes in `countries_aliases.json`.
- New export formats: zstd-compressed `countries.csv.zst` / `intblocks.csv.zst` / `memberships.csv.zst`, lite CSV/Parquet variants, `countries.json.zst` / `intblocks.json.zst`, `datapackage.json`, `countries_aliases.json`.
- Documentation refreshed for new counts, exports, Kosovo `XK`, attribute-field migrations, citation/DOI, and Polars consumer recipes.

### Fixed

- Intblock factual corrections: African Union HQ (Addis Ababa), OAS HQ/roster (Nicaragua former member), EU `partof: EEA` removed, ASEAN description (eleven members), UN agency `partof` standardized to `UN` (ILO, FAO, ICAO).

### Added

- Country attribute fields: `writing_directions`, `writing_systems`, `dvd_region`, `broadcast_systems`, `legal_systems`, `rail_gauges` (plus existing `car_side`); vocab catalogs under `data/vocabs/`; optional `government_forms.yaml` without country assignment.
- `docs/entity-classification-policy.md` — TW, PS, XK, EH, VA, CK, NU edge-case guidance.
- Validation: `partof` hierarchy check (no treaty/agreement parents); Wikidata completeness gate with `data/schemas/wikidata_exclusions.yaml`.
- Contributor onboarding: `docs/getting-started.md`, `docs/architecture.md`, generated `docs/data-dictionary.md`, GitHub issue templates, `dev/research`/`dev/scripts`/`data/_legacy` READMEs.
- LLM ergonomics: OpenAI tool schemas, token-budget tables, RAG/policy-researcher recipes.
- Optional `scope_category` on intblocks (~872 labeled) + `docs/intblock-inclusion-policy.md`.
- Optional country crosswalks: `geonames_id`, `ioc_code`, `fifa_code`, `fips_code`, `bbox`.
- Citation: `CITATION.cff`, Zenodo concept DOI badge, ODbL note for mledoze/countries centroids in `ATTRIBUTION.md`.
- pytest-cov gate (fail-under 45%, measured baseline ~48%), schema migration emitter (`migration.vUnreleased.json`), monthly enrichment auto-PR, optional HF/Zenodo release steps (dataset card + draft deposit).
- Wikidata id backfill for TIMBI, VISTA, SAPP (110 remain on exclusion list).
- [docs/query-examples-polars.md](docs/query-examples-polars.md) — verified Polars / Parquet query cookbook (country filters, borders, memberships, overlap, former members); covered by `tests/test_documented_queries_polars.py`. `polars` added to `requirements-dev.txt`.
- [docs/query-examples-r.md](docs/query-examples-r.md) — verified R / dplyr / Parquet query cookbook (same scenarios via `arrow` + `dplyr` + `tidyr`).
- [docs/query-examples-observable.md](docs/query-examples-observable.md) — Observable Framework / Plot cookbook (DuckDB-Wasm + Plot: density bars, NATO/EU overlap, centroid maps, HQ cities, former-member timeline).

## [1.9.0] - 2026-08-01

Correct Guinea-Bissau UN membership and expand the verified DuckDB query cookbook.

### Fixed

- Country **GW** (Guinea-Bissau): set `un_member: true` (was incorrectly `false`). The country-level flag now matches the `UN` intblock roster at **193** members; independent non-UN states shrink to Vatican City (`VA`) alone.

### Changed

- Expanded [docs/query-examples.md](docs/query-examples.md) with verified DuckDB recipes for near-universal org coverage (CN/US absences), former memberships and departure dates (via `intblocks.jsonl.zst`), roster density, observer seats, border/income patterns, `partof` hierarchy, and related cross-joins; expected counts updated for the GW fix. Covered by `tests/test_documented_queries.py`.
- Rebuilt `data/datasets/` exports so consumers pick up the corrected `un_member` flag.

## [1.8.0] - 2026-07-30

Membership and provenance enrichment: ~500 intblock records refreshed with sourced rosters, metadata, and provenance; intblocks row count **1076 → 1078** (three added, one duplicate merged).

### Added

- Data-quality rule **INSUFFICIENT_PROVENANCE**: flags country and intblock records whose `provenance` list has fewer than four entries (threshold configurable via `min_count` in completeness schemas).
- Intblock **USCR** (United States-Costa Rica Free Trade Agreement): bilateral CAFTA-DR schedules for US and CR; signed 2004-05-28, entered into force for Costa Rica 2009-01-01, with full metadata, includes, and provenance.
- Intblock **FATFGREYLIST** (FATF grey list / Jurisdictions under Increased Monitoring): 22 jurisdictions as of the June 2026 FATF plenary, sourced from FATF black-and-grey-lists and increased-monitoring statements.
- Intblock **IPSOS** (International Patient Summary): global health-informatics standards initiative (successor to epSOS); G7 roadmap participants and documented national IPS deployments, HL7 FHIR IPS links, and full provenance.

### Changed

- **Bulk intblock enrichment**: ~500 records across agreements, forums, FTAs, fisheries, education, environment, gas pipelines, geographic groups, and trade blocs — membership rosters synced to official sources, with founded/HQ metadata, descriptions, notes, and full provenance where previously sparse.
- Intblock completeness: `provenance.min_count: 4` in `countries_completeness.yaml` and `intblocks_completeness.yaml`; Pacific Alliance Wikidata Q7122288 added to `wikidata_duplicate_allowlist` (PACALL vs PACIFICALLIANCE).
- Intblock **BTE** (Baku–Tbilisi–Erzurum / South Caucasus Pipeline): merged duplicate **SOUCAPIPE** record (same Wikidata Q572699); added SCP acronym, notes, and Arabic name; alias `SOUCAPIPE` → `BTE`.
- Intblock **SADCFTA** (Southern African Development Community Free Trade Area): corrected FTA roster to 13 implementing members (removed Angola; DRC and Comoros remain outside SADC FTA), added join dates and founding members, active period from August 2008, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **INTTRASPORTFORUM** (International Transport Forum): synced membership to 72 (added AR/BR/CR/GH/KH/KR/PA/PE), set founded `1953-10-17`, Paris HQ, ECMT previous names, sourced description/notes on May 2026 Ghana/Panama/Peru accession and RU/BY restrictions, and full provenance.
- Intblock **MSC** (Munich Security Conference): added Wikidata Q565507, foundation legal status, Munich HQ coordinates, previous names, and sourced description/notes; reframed `includes` as 57 frequent participant states plus EU/NATO (`participant` status; invitation-only, no treaty membership), with full provenance.
- Intblock **CAIRNSGROUP** (Cairns Group): confirmed 20 current members plus Fiji and Hungary as former founding members; set founded `1986-08`, join dates where known (incl. Ukraine 2024-02-25), trade blocktype, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **EAPC** (Euro-Atlantic Partnership Council): confirmed 50-member roster (32 NATO Allies + 18 PfP partners), set founded `1997-05-29`, Brussels NATO HQ, corrected English acronym to EAPC, sourced description/notes on RU/BY suspension and NACC succession, and full provenance.
- Intblock **FIPIC** (Forum for India-Pacific Islands Cooperation): confirmed 15 members (India plus 14 Pacific Island countries) with founding join dates `2014-11-19`, corrected Wikidata to Q20983306 (removed wrong mountain Q-id), fixed FM display name and bogus other_names, FICCI site link, sourced description/notes, and full provenance.
- Intblock **ARF** (ASEAN Regional Forum): confirmed 27 participants with join dates and 18 founding participants, set founded `1994-07-25`, Jakarta ASEAN Secretariat HQ, corrected Wikidata to Q7886981 (replaced polluted Q481014), sourced description/notes, and full provenance.
- Intblock **FOCAC** (Forum on China–Africa Cooperation): confirmed 54 country members (China + 53 African states recognizing the PRC; Eswatini excluded), set founded `2000-10-10`, Beijing HQ, geographic scope/regions, sourced description/notes, multilingual names/acronyms, and full provenance.
- Intblock **BFA** (Boao Forum for Asia): synced `includes` to the 29 BFA Initial Countries (26 charter founders plus Israel/New Zealand 2006 and Maldives 2016; removed incorrect KW/RU/SA/TR), set founded `2001-02-27`, Wikidata Q887521, Beijing secretariat metadata, sourced description/notes, and full provenance.
- Intblock **CVF** (Climate Vulnerable Forum): synced membership to 74 CVF-V20 members (added Cabo Verde, Gabon, Nauru, Solomon Islands, Somalia, and Suriname), set founded `2009-11-10`, Accra HQ, V20 as suborganization, sourced description/notes, and full provenance.
- Intblock **CCAMLR** (Commission for the Conservation of Antarctic Marine Living Resources): confirmed 27 Commission Members plus 10 Acceding States, set founded `1982-04-07`, founding members, Hobart HQ, Wikidata Q97382426, sourced description/notes, and full provenance.
- Intblock **GFCM** (General Fisheries Commission for the Mediterranean): confirmed 24 contracting parties with join dates plus 5 cooperating non-contracting parties; recorded United Kingdom and Japan as former members; set founded `1949-09-24` / entry into force `1952-02-20`, Rome HQ, founding members, sourced description/notes, and full provenance.
- Intblock **VIENNACONVENTION** (Vienna Convention for the Protection of the Ozone Layer): synced parties to universal ratification roster of 198 (added Guinea-Bissau), set founded `1985-03-22` / entry into force `1988-09-22`, founding members, Nairobi Ozone Secretariat HQ, Montreal Protocol as suborganization, sourced description/notes, and full provenance.
- Intblock **WCPFC** (Western and Central Pacific Fisheries Commission): confirmed 26 Members with Convention entry-into-force join dates and 14 founding members; added 7 Participating Territories and 8 Cooperating Non-Members from the official CCM roster; set founded `2004-06-19`, Pohnpei HQ coordinates, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **CECAF** (Fishery Committee for the Eastern Central Atlantic): confirmed 34 FAO members (coastal African states plus distant-water fishing/research members and the EU), set founded `1967-06` / statutes `1967-09-19`, Accra FAO RAF secretariat, COPACE/CPACO acronyms, sourced description/notes, and full provenance.
- Intblock **IOTC** (Indian Ocean Tuna Commission): confirmed 29 Contracting Parties plus Liberia/Panama as cooperating CNCPs and five former members (BZ/ER/GN/SL/VU), set founded `1993-11-25` / entry into force `1996-03-27`, Victoria HQ, founding members with join/left dates, sourced description/notes, and full provenance.
- Intblock **APFIC** (Asia-Pacific Fishery Commission): confirmed 21 current members plus Netherlands as former member (left 1974-06-01), set founded `1948-11-09`, Bangkok FAO RAP headquarters, founding members and acceptance dates, previous IPFC names, sourced description/notes on 2023–2028 activity suspension, and full provenance.
- Intblock **WECAFC** (Western Central Atlantic Fishery Commission): synced 34-member roster (added Costa Rica; removed incorrect Bolivia), set founded `1973`, Bridgetown FAO/SLC secretariat metadata, COPACO acronyms, Wikidata Q16189708, sourced description/notes, and full provenance.
- Intblock **CIFAA** (Committee for Inland Fisheries and Aquaculture of Africa): confirmed 37 African member states from FAO RFB sources, set founded `1971-06` (FAO Council Resolution 1/56), Accra RAF secretariat, rename history CIFA→CIFAA (2007), sourced description/notes, multilingual names/acronyms, and full provenance.
- Intblock **EIFAAC** (European Inland Fisheries and Aquaculture Advisory Commission): synced membership to 39 (added Cyprus, European Union, and Ukraine), set founded `1957`, Rome FAO secretariat metadata, official links/languages, sourced description/notes (EIFAC→EIFAAC rename; UA joined 2026-02-27), and full provenance.
- Intblock **UNFCCC** (United Nations Framework Convention on Climate Change): synced parties to 198 (added Iraq and Nauru), set founded `1992-05-09` / entry into force `1994-03-21`, Bonn secretariat/HQ metadata, official links/documents, sourced description/notes, and full provenance.
- Intblock **UNCCD** (United Nations Convention to Combat Desertification): added missing Guinea-Bissau to complete 197 parties; set founded `1994-06-17` / entry into force `1996-12-26`, Bonn HQ/secretariat, UNTC links, sourced description/notes, and full provenance.
- Intblock **CPSC** (Colombo Plan Staff College): confirmed 16 active members plus 12 inactive charter members, set founded `1973-12-05`, founding members, Pasig HQ, official site links, sourced description/notes, and full provenance.
- Intblock **UIL** (UNESCO Institute for Lifelong Learning): confirmed `includes` as the 193 UNESCO Member States served by this Category 1 institute, set founded `1952`, Wikidata Q2467481, Hamburg HQ coordinates, previous name UIE (1952–2006), geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **ACU** (Association of Commonwealth Universities): synced includes to the official home-regions roster (56 countries/territories; added Gibraltar, Hong Kong, and Zimbabwe; removed Gabon, Gambia, and Togo), set Wikidata Q593768, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **IIEP** (UNESCO International Institute for Educational Planning): confirmed `includes` as the 193 UNESCO Member States served by this Category 1 institute, set founded `1963-07`, Wikidata Q3152335, Paris HQ, sourced description/notes, multilingual names, and full provenance.
- Intblock **EHEA** (European Higher Education Area): confirmed 49 country members from the official roster (European Commission noted separately); removed incorrect `partof: EU`; set founded `2010-03`, geographic scope/regions, corrected acronyms (EHEA/EEES/EVP), sourced description/notes on RU/BY suspension, and full provenance.
- Intblock **IBE** (International Bureau of Education): confirmed `includes` as the 193 UNESCO Member States served by this Category 1 institute, added Wikidata Q1047672, official site, global scope, sourced description/notes, multilingual names, and full provenance.
- Intblock **COMMLEARN** (Commonwealth of Learning): completed includes for all 56 Commonwealth member states (added United Kingdom), replaced templated description, set Vancouver HQ/secretariat metadata, geographic scope/regions, sourced notes, and full provenance.
- Intblock **AAU** (Association of African Universities): synced `includes` to 50 countries with AAU member institutions from the official directory (added AE/DE/MY associates; removed seven African countries with no listed members), set founded `1967-11-12`, Wikidata Q743769, geographic scope/regions, recognition notes, and full provenance.
- Intblock **EEA** (European Economic Area): confirmed 30 current parties (27 EU + IS/LI/NO) with join dates; recorded United Kingdom as former member (left 2020-01-31); set founded `1992-05-02` / entry into force `1994-01-01`, Brussels EFTA secretariat metadata, founding members, sourced description/notes, and full provenance.
- Intblock **PETROCARIBE**: confirmed 18 current members plus Guatemala as former member (left 2013-11), set founded `2005-06-29`, founding members and join dates, energy blocktype, Caracas HQ, sourced description/notes, and full provenance.
- Intblock **PECC** (Pacific Economic Cooperation Council): confirmed 24 current member committees from the official roster (11 founding economies; France as associate; PIF/PBEC/PAFTAD as institutional members), recorded Ecuador and Mongolia as former members, set Singapore HQ/secretariat, sourced description, and full provenance.
- Intblock **CP** (Colombo Plan): synced membership to 27 current members (added Chile and Saudi Arabia; recorded United States, Canada, United Kingdom, and Cambodia as former members after the January 2026 U.S. withdrawal), set founded `1951-07-01`, founding members, Colombo HQ, sourced description, and full provenance.
- Intblock **AEC** (African Economic Community): synced parties to 50 Abuja Treaty ratifiers/acceding states (removed DJ, ER, MG, SO, SS pending ratification), set founded `1991-06-03` / entry into force `1994-05-12`, Addis Ababa AU headquarters, founding members, join dates, partof AFUNION, sourced description, and full provenance.
- Intblock **CAEU** (Council of Arab Economic Unity): confirmed 18-member roster with founding members (EG, IQ, JO, KW, SY), set founded `1957-06-03`, Arab League `partof`, Cairo HQ/official site, sourced description, multilingual names, and full provenance.
- Intblock **CCASG** (Gulf Cooperation Council): set founded `1981-05-25`, Riyadh headquarters, founding-member status and join dates for all six members, suborganizations PSF/GCCPO, sourced description/notes, and full provenance.
- Intblock **POPS** (Stockholm Convention on Persistent Organic Pollutants): synced parties to 186 (added Cook Islands, DPRK, and Niue; removed Andorra, Bhutan, Brunei Darussalam, Haiti, Israel, Malaysia, San Marino, South Sudan, Timor-Leste, and Turkmenistan), set founded `2001-05-22` / entry into force `2004-05-17`, Geneva BRS secretariat metadata, sourced description, and full provenance.
- Intblock **RAMSAR** (Ramsar Convention / Convention on Wetlands): synced Contracting Parties to 172 current members (added CI, KP, TR; removed 10 non-parties; recorded Russia as former member after denunciation effective 2025-12-21), set founded `1971-02-02` / entry into force `1975-12-21`, Gland secretariat (IUCN-hosted), sourced description, and full provenance.
- Intblock **RAROTONGA** (Treaty of Rarotonga / South Pacific Nuclear Free Zone Treaty): set founded `1985-08-06` and entry into force `1986-12-11`, confirmed 13 States Parties with ratification join dates and founding members, Suva PIF secretariat, official UNODA/UNTC links, and full provenance.
- Intblock **TPNW** (Treaty on the Prohibition of Nuclear Weapons): synced parties to 75 current States parties (added Mongolia, Niue, and Tonga; removed signatories that have not ratified), set founded `2017-09-20` / entry into force `2021-01-22`, official links/languages, and full provenance.
- Intblock **PIC** (Rotterdam Convention): synced parties to 168 current parties from the UN Treaty Collection (added EU, Israel, DPRK, Palestine; removed 28 non-parties), set founded `1998-09-10` / entry into force `2004-02-24`, BRS secretariat metadata, sourced description, and full provenance.
- Intblock **NPT** (Treaty on the Non-Proliferation of Nuclear Weapons): synced parties to 190 current States parties (added Denmark and Palestine, removed South Sudan, recorded North Korea as former member), set entry-into-force date `1970-03-05`, official name/description/links/languages, and full provenance.
- Intblock **OSPAR** (OSPAR Commission): added European Union to Contracting Parties (15 → 16), founded `1992-09-22` / entry into force `1998-03-25`, London secretariat, founding members, sourced description, and full provenance.
- Intblock **NOUMEA** (Noumea Convention): corrected membership to the 12 contracting parties (removed non-parties previously listed from the broader SPREP roster), added founded/EIF dates, founding members, join dates, UNEP Regional Seas metadata, Apia secretariat, multilingual names, and full provenance; removed incorrect Wikidata Q7446680.
- Intblock **PELINDABA** (Treaty of Pelindaba / African Nuclear-Weapon-Free Zone Treaty): added Western Sahara (EH) as the 44th party, set founded `1996-04-11` and entry into force `2009-07-15`, AFCONE Pretoria headquarters, official links, and full provenance.
- Intblock **CPTPP** (Comprehensive and Progressive Agreement for Trans-Pacific Partnership): added United Kingdom (12th member), founding-member status and join dates for original signatories, Wikidata Q48852287, predecessor TPP, sourced description, multilingual names, and full provenance.
- Intblock **TPP** (Trans-Pacific Partnership): corrected record from P4-only membership to all twelve 2016 signatories (US as former member after 2017 withdrawal), historical status, founded/dissolved dates, successor CPTPP, sourced description, official links, and full provenance.
- Intblock **CASPSREG** (Caspian Sea region): confirmed five littoral-state membership (AZ, IR, KZ, RU, TM), geographic scope/regions, sourced description, multilingual names, and full provenance.
- Intblock **MEGP** (Maghreb–Europe Gas Pipeline): added Portugal to membership (3 → 4), Wikidata Q734096, founded `1996-11-01`, geographic scope/regions, acronyms (MEG/GME), multilingual names, sourced description covering the 2021 supply halt and 2022 reverse flow, and full provenance.
- Intblock **GFTEITP** (Global Forum on Transparency and Exchange of Information for Tax Purposes): expanded includes from 103 to 173 participants (172 tax jurisdictions plus the European Union), corrected description/tags/topics, added headquarters, official links, and full provenance.

### Fixed

- All **FOUNDING_MEMBER_NOT_INCLUDED** and **HISTORICAL_ENTITY_ACTIVE_MEMBER** quality findings resolved across the enriched intblock set.
- Refreshed documentation counts across README, `llms.txt`, `docs/`, and `openspec/project.md` (256 countries, 1078 intblocks, 86 blocktypes).

## [1.7.0] - 2026-07-20

Coverage expansion: five new intblocks and refreshed ISA Seabed Authority / International Copper Study Group membership.

### Added

- Intblocks **ARABSAT**, **CDRI**, **WANO**, **PAXSILICA**, **WAICO**; intblocks row count **1071 → 1076**.
- Intblock **ARABSAT** (Arab Satellite Communications Organization): Arab League intergovernmental satellite operator founded 1976-04-14, Riyadh HQ; 21 shareholder member states.
- Intblock **CDRI** (Coalition for Disaster Resilient Infrastructure): India-launched global coalition for disaster- and climate-resilient infrastructure (2019-09-23); New Delhi HQ; 58 member countries and 12 partner organizations.
- Intblock **WANO** (World Association of Nuclear Operators): nonprofit nuclear-operator safety organisation founded 1989-05-15, London HQ; 31 countries with operating commercial NPPs.
- Intblock **PAXSILICA** (Pax Silica): US-led AI, semiconductor, and critical-minerals supply-chain initiative.
- Intblock **WAICO** (World Artificial Intelligence Cooperation Organization) — 29 founding members, Shanghai HQ, established 2026-07-16.

### Changed

- Intblock **ISA_SEABED** (International Seabed Authority): synced membership to UNCLOS parties (172 members + US observer); set founded `1994-11-16`, Kingston HQ coordinates, `partof: UNCLOS`, and Wikipedia/Wikidata links.
- Intblock **ICSG** (International Copper Study Group): refreshed membership to 26 current members (incl. EU) plus 7 former members; set founded date 1992-01-23, Wikidata Q17084551, and Lisbon HQ provenance.

## [1.6.0] - 2026-07-16

Data-quality expansion release: shared rule engine with 40+ new referential, temporal, and plausibility checks; intblocks schema tightened (**breaking**); space category consolidation; artifact-consistency and link-check CI guards; hundreds of data fixes.

### Added

- Consumer query cookbook [docs/query-examples.md](docs/query-examples.md) with verified DuckDB and Pandas examples (UN members, borders, intblock membership, cross-joins).
- Intblock **BLASMBL** (Baltic Assembly); intblocks row count **1070 → 1071**.
- `data/datasets/blocktypes.manifest.json` — blocktypes now emit a build manifest like countries/intblocks.
- `scripts/check_generated_artifacts.py` — cross-format primary-key parity, source/export parity, and single-build-identity guard (wired into CI and release).
- `scripts/check_markdown_links.py` — internal Markdown link checker (wired into CI).
- Intblock structural enrichment: `enrich_intblocks.py backfill-structural` fills `headquarters` (Wikidata P159/P625) and `founded` (P571), stamping `last_verified`; `last_verified` coverage now reported by `validate_intblocks.py`.
- Capital cities for 10 previously capital-less entities (GI, HK, IL, MO, PS, TW, VA, XA, XS, XT) with provenance; remaining capital-less entities documented as expected exclusions in `docs/country-code-policy.md`.
- `internacia-build` and `internacia-analyze-quality` console entry points; shared HTTP client `internacia_builder.http`; `internacia_builder.__version__` now reports the release version.
- **Expanded data-quality rules** (`expand-data-quality-rules`): new referential-integrity checks — `UNRESOLVED_BORDER_REFERENCE` (borders resolve to existing `iso3code`, no self-reference), `NONRECIPROCAL_BORDER` (advisory, with allowlist), `UNRESOLVED_ORG_REF` (`predecessor`/`successor`/`suborganizations`), `UNRESOLVED_HQ_COUNTRY`, and `DUPLICATE_WIKIDATA_ID` (with documented allowlist for concept-level Q-ids). New consistency/plausibility checks — `CHRONOLOGY_ERROR`, `DUPLICATE_INCLUDE_ENTRY`, `MEMBERSHIP_COUNT_MISMATCH`, `CONTRADICTORY_APPLICABILITY`, `INVALID_INDICATOR_VALUE`, `INCONSISTENT_ENTITY_FLAGS`, `PROVENANCE_INTEGRITY`, and the `INCLUDE_NAME_MISMATCH` advisory (replaces `scripts/report_country_include_names.py`). CI-only rules (`INVALID_CURRENCY_CODE`, `INVALID_COORDINATES`, `STALE_PROVENANCE`, `FILENAME_ID_MISMATCH`, `DIRECTORY_BLOCKTYPE_MISMATCH`, `DEPRECATED_TOPIC_KEY`) now also appear in `dataquality/` reports.
- `data/schemas/includes_status.yaml` — canonical catalog of `includes[].status` participation values (member, observer, founding_member, former_member, etc.); `validate_intblocks.py` and the quality analyzer now check every include status against it (`INVALID_INCLUDE_STATUS`) and flag entries with no status at all.
- Intblock `membership_applicability: not_applicable` marker for records where an empty `includes` list is intentional (conceptual entities, acronym groups, DVD regions); records with neither `includes` nor the marker are flagged by the new `MISSING_INCLUDES_APPLICABILITY` rule.
- **Extended data-quality rules** (`add-extended-quality-rules`): country field validity — `INVALID_TLD`, `INVALID_CALLING_CODE`, `INVALID_TIMEZONE` (IANA tz database), `FLAG_EMOJI_MISMATCH`, `LANDLOCKED_INCONSISTENCY`, `REGION_HIERARCHY_MISMATCH` (canonical continent→subregion table with allowlist), `UNRESOLVED_PARENT_ENTITY`. Geographic plausibility — `CAPITAL_FAR_FROM_CENTROID` and `HQ_COORDINATES_OUTSIDE_COUNTRY` (area-scaled great-circle budgets that catch swapped/mis-signed coordinates). Intblock temporal/membership — `INCLUDE_DATE_INCONSISTENCY` (precision-aware `joined`/`left` checks), `FOUNDING_MEMBER_NOT_INCLUDED`, `HISTORICAL_ENTITY_ACTIVE_MEMBER`, `STALE_LAST_VERIFIED`. Lineage and naming advisories — `SUCCESSOR_RECIPROCITY`, `PARTOF_SUBORG_RECIPROCITY`, `DUPLICATE_ACRONYM` (with allowlist for real-world collisions). Text integrity — `MOJIBAKE_TEXT`. `UNKNOWN_TOPIC_KEY` is backed by the new canonical topic catalog `data/schemas/topics.yaml` (153 keys seeded from current usage).

### Changed

- **INOGATE enriched**: filled `includes` (12 partner countries plus Russia as observer), marked `status: historical` with `founded`/`dissolved` (1996–2016), and added `energy` blocktype, secretariat, headquarters, and provenance.
- **BREAKING (intblocks schema)**: `intblocks.schema.json` now sets `additionalProperties: false`. Declared canonical fields `legal_status`, `recognition_status`, `predecessor`, `successor`, `previous_names`, `official_documents`, `social_media`, `secretariat`; removed unused `abbrRU`, `listed`, and `translations`.
- **BREAKING (intblocks export)**: the empty `translations` column was removed from the Parquet/DuckDB export (use `other_names`).
- Intblock validation now errors (previously warned/unchecked) when a filename stem does not match the record `id`, or a record's category directory is absent from its `blocktype` list. Renamed `UFM.yaml` → `UfM.yaml`; added `space` to 22 space records; normalized one-off keys (`succeeded_by`, plural `predecessors`/`successors`, `official_languages`, `purpose`).
- 25 space-related records (space treaties, agencies, and coordination bodies — e.g. OUTERTREATY, ARTEMISACCORDS, ESA, ISS, UNOOSA, COPUOS, EUMETSAT, COSPAR) consolidated into the `data/intblocks/space/` category directory from `agreement/`, `forum/`, `intorg/`, `meteorology/`, `project/`, `scientific/`, and `unagency/`.
- `data/schemas/intblocks_completeness.yaml` restructured into priority/requirement tiers (high: `includes`; medium: `wikidata_id`, non-templated `description`; low: `languages`, `headquarters`, `regions`, `other_names`, `provenance`, `links`) with measured 2026-07 baselines as warn thresholds, plus documented allowlists for org references, wikidata duplicates, and acronym collisions.
- Quality analyzer `DUPLICATE_LINK` rule de-noised (normalized URLs, excludes reference-catalog hosts and hierarchically related orgs, drops synthetic TLD pseudo-links): 77 → 22 flags. `analyze-quality` now runs in CI and fails on CRITICAL/IMPORTANT.
- Build now emits a single frozen build identity (`build_date`/`git_commit`) across all manifests, sidecars, and DuckDB `_meta` rows.
- `gini` completeness threshold documented and re-scoped (0.33 → 0.40, warn) reflecting World Bank coverage reality.
- Build/export logic moved into the installable `internacia_builder.build`; `scripts/builder.py` is now a thin shim.
- Refreshed stale documentation counts across README, `llms.txt`, `docs/`, and `openspec/project.md` (256 countries, 1071 intblocks, 86 blocktypes).
- Data-quality checkers consolidated into a single shared layer (`internacia_builder/validate/country_rules.py`, `intblock_rules.py`, `cross_rules.py`) used by both `analyze-quality` and the `validate_countries`/`validate_intblocks` CLIs, eliminating the duplicated rule logic in `build.py`.

### Fixed

- All 377 `INCLUDE_NAME_MISMATCH` advisories resolved: IFDC's Benin member used Belgium's code (`BE` → `BJ`); World Bank WLD placeholder display names `TW`/`VA` replaced with real names; legitimate alternate names (e.g. `Türkiye`, `Holy See`, `Chinese Taipei`, ISO 3166 long forms) added to 15 country records' `common_names` with provenance; scoped-membership qualifiers (e.g. "Denmark (in respect of the Faroe Islands and Greenland)", "Malaysia (Labuan)", Bonaire/Sint Eustatius under `BQ`) moved from `includes[].name` into `includes[].note`.
- Wrong `wikidata_id` on seven UN records (UNDP, WFP, UNFPA, UNRWA, UN Women shared the generic "nonprofit organization" item Q163740; UN-Habitat and SIDS carried UNEP's and WMO's Q-ids); Kosovo's empty `borders` populated (ALB, MKD, MNE, SRB); 27 intblock `founded`/`dissolved` placeholder dates (`YYYY-00-00`) normalized.
- Swapped/incorrect capital coordinates for Western Sahara (`EH`: El Aaiún was placed in Zambia) and the French Southern Territories (`TF`: Port-aux-Français was placed near Mont-Saint-Michel), surfaced by the new `CAPITAL_FAR_FROM_CENTROID` rule.
- Missing lineage back-references added: `WTO.predecessor: GATT`, `ICSU.successor: ISC`, `EEHUB.predecessor: IPEEC`, `ENTSOE.predecessor: NORDEL`, `G8 ↔ G7`, and `BRIC ↔ BRICS`; `IMF` now declares `partof: UN` (it was already listed in UN suborganizations); IATTC's Spanish acronym `CIAT` re-tagged from `lang: en` to `lang: es`.

## [1.5.0] - 2026-06-15

Coverage expansion, taxonomy governance, builder refactor, and enrichment tooling release.

### Added

- User-assigned country profiles for CIS2 entities (`XA`, `XS`, `XT`, `XN`) with `recognition_status` metadata; countries row count **252 → 256**.
- Country `centroid: {lat, lng}` on all 256 records.
- Intblocks **COCESNA**, **EPLO**, **FILAC** (P2 backlog); intblocks row count **1067 → 1070**.
- Nine intblock coverage gaps (UNSC, UNGA, UNHRC, CHIP4, DEPA, PEPFAR, MSF, UNCITRAL, UNCLOS) and topic taxonomy governance (`docs/topic-taxonomy.md`, `data/schemas/topic_aliases.yaml`).
- `scripts/apply_manus_roadmap.py` for batch topic/directory/centroid migrations.
- `enrich_countries.py check`: report stale provenance and missing fields (no network).
- `validate_countries.py`: ISO 4217 currency code warnings and provenance freshness checks.
- `.github/workflows/enrichment-check.yml`: monthly enrichment freshness report.
- G5 Sahel historical record (`G5SAHEL`) and `enrich_intblocks.py backfill-founded` for Wikidata inception dates.

### Changed

- `builder.py` imports validators directly (no subprocess); validation logic moved to `internacia_builder/`.
- `enrich_intblocks.py backfill-founded` also checks Wikidata P1619 (date of official opening).
- Blocktypes taxonomy source moved to `data/blocktypes/blocktypes.yaml`; `data/datasets/blocktypes.yaml` is now build output.
- Intblock directory taxonomy aligned with blocktype values (`tax/`, `transport/`, `unregionalblock/`, `audit` blocktype); 169 primary blocktype mismatches remediated.
- Topic keys consolidated (11 synonym groups, sports unification); `validate_intblocks.py` warns on deprecated keys and directory misalignment.
- `enrich_countries.py`: paginated World Bank fetch, M49-based classification for non-WB entities.
- `enrich_intblocks.py`: `--ids` filter for batch high-profile enrichment.
- **Dataset outputs rebuilt**: 256 countries, 1070 intblocks, 86 blocktypes.

## [1.4.0] - 2026-06-15

Intblocks taxonomy reorganization and enrichment release: domain-folder classification, Wikidata enrichment, data licensing, and self-describing dataset metadata.

### Added

- **Intblocks enrichment** (`scripts/enrich_intblocks.py`): backfills `wikidata_id` (high-confidence matches only), replaces templated boilerplate descriptions with Wikidata descriptions, and adds multilingual `other_names` and acronym aliases — all with field-level `provenance`. Intblock records now support a `provenance` list (validated and exported in all formats). Coverage: +55 `wikidata_id` (60%→66%), templated descriptions 43%→24%, provenance on 459 records.
- **Intblocks description-quality gate**: `validate_intblocks.py` measures the templated-description rate against a configurable threshold in `intblocks_completeness.yaml` (`quality.templated_description`).
- **Data license**: explicit `DATA_LICENSE` (CC BY 4.0) for datasets, separate from the MIT code license, plus `ATTRIBUTION.md` documenting World Bank (CC BY 4.0), Wikidata (CC0), and IANA tzdata sources and a recommended citation. Build manifests and metadata now carry a `data_license` SPDX field.
- **Self-describing datasets**: `internacia.duckdb` now includes a `_meta` table (one row per dataset with `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`, `data_license`); each Parquet export is accompanied by a `<dataset>.meta.json` sidecar.
- **Identifier stability**: `data/intblocks_aliases.yaml` source plus generated `intblocks_aliases.{json,parquet}` mapping retired/renamed intblock ids to current ids (`reason`: `renamed`/`merged`/`disambiguated`). `validate_intblocks.py` checks alias integrity (targets resolve; collisions allowed only when `disambiguated`). Seeded with the v1.3.0 `ASF`→`FSA` and `CAF`→`CAFBANK` disambiguations.
- **Domain category folders**: new intblock source directories — `agriculture`, `audit`, `aviation`, `climate`, `cultural`, `education`, `health`, `intelligence`, `maritime`, `space`, `statistics`, `taxation`, `tourism`, `transportation`, and `water` — with ~150 records relocated from the catch-all `intorg/` folder into their primary domain.
- **New intblock records**: OPCW, GICNT, BIS, ICCROM, WTO, AANZFTA, OIV, CARICC, and regional fisheries/aviation/audit bodies among others.
- **Blocktype taxonomy**: added `statistics` blocktype (86 total).

### Changed

- **Intblocks folder taxonomy**: records are filed under their primary domain category rather than `intorg/` when a dedicated folder exists; `intorg/` now holds general-purpose intergovernmental organizations only (~81 records, down from ~230).
- **Description quality**: acronym and geographic group records updated with substantive descriptions replacing generic "International entity." boilerplate.
- **Currency record**: `CMA` (Comorian franc) moved from `cuscurr/` to `currency/`.
- **Release assets**: the release workflow now publishes `*.meta.json` sidecars and the `intblocks_aliases.*` artifacts.
- **Dataset outputs rebuilt**: all artifacts regenerated (252 countries, 1057 intblocks, 86 blocktypes).

## [1.3.0] - 2026-06-12

Intblocks quality and engineering hardening release: intblocks validation pipeline, automated tests, dev tooling, CI/CD workflows, and data fixes.

### Added

- **Intblocks validation** (`scripts/validate_intblocks.py`): JSON Schema checks, duplicate id detection, blocktype taxonomy validation, `partof` reference resolution, lifecycle consistency (`dissolved` implies `historical`), and completeness gates; runs in CI and before every build.
- **Intblocks completeness config** (`data/schemas/intblocks_completeness.yaml`): per-field null-rate thresholds with warn/error modes.
- **Intblocks build manifest** (`data/datasets/intblocks.manifest.json`): `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`; baseline diff extended to cover it.
- **Test suite** (`tests/`, 49 tests): `clean_data` normalization, country/intblock validation logic, cross-dataset include resolution, Parquet/DuckDB export round-trips, and manifest generation.
- **Dev tooling**: `pyproject.toml` (ruff + pytest config), `.pre-commit-config.yaml`, `requirements-dev.txt`.
- **Contributor guide** (`CONTRIBUTING.md`): setup, YAML authoring conventions, validation workflow, PR checklist.
- **Workflows**: weekly scheduled link validation (`.github/workflows/link-validation.yml`), tag-triggered release with dataset assets (`.github/workflows/release.yml`), Dependabot for pip and GitHub Actions.

### Changed

- **Builder hardening** (`scripts/builder.py`): runs both countries and intblocks validation before export; YAML parse failures abort the build instead of silently skipping files; Parquet schema mismatches fail loudly (removed pandas fallback); fixed DuckDB export (PyArrow tables are now registered explicitly, restoring `internacia.duckdb` generation).
- **Intblocks schema reconciled** (`data/schemas/intblocks.schema.json`): status, include type/status, and geographic scope enums now match observed legitimate values; `founded` accepts decade notation; `partof` accepts strings or objects.
- **Indicator years**: missing `population`/`area`/`gini` years are exported as `null` instead of `0` (**semantic change**); validator rejects `year: 0`.
- **Pinned dependencies** (`requirements.txt`): exact versions for reproducible builds; CI uses pip caching.
- **One-off scripts relocated**: `enrich_gap_records.py` and `fill_includes_agreement_intorg.py` moved to `dev/scripts/`.

### Fixed

- **Intblocks deduplicated**: merged 8 duplicate records (OFID, GEF, ICRC, IFRC, NPI, IFAD, UNHCR, UNICEF) keeping the richer record with combined blocktypes; resolved 2 acronym collisions (African Solidarity Fund renamed to `FSA`, CAF Development Bank renamed to `CAFBANK`). Row count: 1065 → 1057 (**breaking** for consumers joining on removed ids).
- **Country data corrections**: `AN.yaml` (Netherlands Antilles) had Anguilla's wikidata id, names, and indicators; `JG.yaml` (Channel Islands) pointed to the wrong Wikidata entity (Urdoma); removed all `year: 0` placeholders across 36 country files.
- **YAML boolean traps**: quoted `NO` (Norway) and `no` (Norwegian) values that were parsed as `false` in intblock records (NORDEL, CEPI, and others).
- **Lifecycle consistency**: dissolved organizations (EASTERNBLOC, WESTERNBLOC, FRUGALFOUR, ICSU, NORDEL, GATT) now carry `status: historical`.
- **Reference fixes**: `partof` aliases corrected (`AU` → `AFUNION`, `GCC` → `CCASG`); missing `wikidata_id` filled for ISA, Kimberley Process, EAEU; UNFCCC duplicate member entry removed.
- **Validation report ordering**: `validate_countries.py --report` now includes cross-dataset results.

### Migration

- **Removed intblock ids**: `ASF` (African Solidarity Fund) is now `FSA`; `CAF` (development bank) is now `CAFBANK`; duplicate ids listed above resolve to a single record.
- **Indicator year**: treat `population.year == null` as "year unknown" (previously `0`).

## [1.2.0] - 2026-05-29

Countries reference data quality release: validation gates, profile enrichment, entity status modeling, and release governance. Based on gap analysis in `dev/research/countries_gaps_manus_20260528.md`.

### Added

- **Country validation** (`scripts/validate_countries.py`): JSON Schema checks, ISO identifier rules, completeness thresholds, entity status enforcement, and intblock cross-reference validation.
- **Completeness manifest** (`data/schemas/countries_completeness.yaml`): per-field null-rate gates with warn/error modes.
- **Country enrichment** (`scripts/enrich_countries.py`): World Bank + Wikidata + IANA tzdata for `population`, `area`, `gini`, `timezones`, and `native_names`; `backfill-provenance` subcommand.
- **IANA timezone reference**: bundled `scripts/data/zone1970.tab`.
- **Entity status fields**: `entity_type`, `code_status`, optional `recognition_status` on all 252 country records.
- **Entity annotation utility** (`scripts/annotate_entity_status.py`).
- **Country code policy** (`docs/country-code-policy.md`): ISO vs user-assigned codes, filter examples, deferred CIS2 entity notes.
- **Field provenance**: optional `provenance` list on country records (`field`, `source`, `retrieved_at`, `url`, `license`).
- **Build manifest** (`data/datasets/countries.manifest.json`): `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`.
- **Baseline diff utility** (`scripts/diff_countries_baseline.py`).
- **Include name audit** (`scripts/report_country_include_names.py`): intblock alias reporting (warn-only).
- **CI workflow** (`.github/workflows/validate.yml`): validate, completeness report artifact, parquet build, baseline diff.

### Changed

- **Countries profile fields**: `population`, `area`, and `gini` are structured indicators `{value, year, source, source_id}` in YAML and Parquet (**breaking** — was bare `int64` for population).
- **Countries data populated**: formerly empty fields (`population`, `area`, `timezones`, `native_names`) filled across all 252 records where sources exist.
- **Borders contract**: documented and validated as ISO 3166-1 **alpha-3** land-border codes.
- **Builder integration**: runs country validation before export; strips categorical whitespace; writes manifest on parquet/duckdb build.
- **Extended JSON Schema** (`data/schemas/countries.schema.json`): full builder field coverage including entity status and provenance.
- **Dataset outputs rebuilt**: all countries artifacts regenerated.

### Migration

- **Parquet population**: column is now a struct. Access count via `population.value` (pandas: `df['population'].struct.field('value')`).
- **Current ISO filter**: `code_status == 'official_iso3166_1'` returns 249 records; excludes `AN` (obsolete), `JG` and `KV` (user-assigned).
- **Borders joins**: use alpha-3 codes in `borders` or map via `iso3code`.
- **Upgrade check**: compare `countries.manifest.json` `schema_hash` before deploying downstream consumers.

## [1.1.2] - 2026-05-28

### Added
- **International blocks expansion**: Added and merged new `intblocks` records from gap-analysis research (Manus + Perplexity), including additional agreement, intorg, forum, political, military, bank, food, environment, geographic, economic, and armscontrol entries.
- **Merged research report**: Added consolidated gap report at `dev/research/gaps_merged_20260528.md`.
- **Metadata enrichment utility**: Added `scripts/enrich_gap_records.py` to normalize and enrich newly added records with `wikidata_id`, `headquarters`, `acronyms`, `legal_status`, `topics`, and aligned tags.
- **Includes backfill utility**: Added `scripts/fill_includes_agreement_intorg.py` to populate missing `includes` for `agreement` and `intorg` datasets.

### Changed
- **Blocktype taxonomy**: Extended `data/datasets/blocktypes.yaml` with previously used but undefined blocktypes (including `health`, `water`, `ocean`, `transport`, `digital`, `cybersecurity`, `climate`, and related domain tags).
- **International blocks coverage**: Updated `agreement` and `intorg` records to ensure `includes` sections are populated where previously missing.
- **Dataset outputs rebuilt**: Regenerated all dataset artifacts (`countries`, `intblocks`, `blocktypes`) in JSONL, YAML, Parquet, and DuckDB formats.

## [1.1.0] - 2025-12-07

### Added
- **Countries dataset**: Added `other_names` field containing name translations in multiple languages (Arabic, Chinese, English, French, Russian, Spanish)
- **Countries dataset**: Added `common_names` field containing common aliases and alternative names
- **International Blocks dataset**: Added `other_names` field for standardized multilingual name translations
- **New international blocks categories**: Added support for environment, humanitarian, intelligence, meteorology, patent, scientific, sports, and standards categories
- **Expanded UN agency data**: Significantly expanded membership data for UN agencies (UNDP, UNEP, UNFPA, UNHABITAT, UNODC, UNRWA, UNWOMEN, WFP)
- **New utility scripts**: 
  - `add_environment_members.py`: Script to add environment organization members
  - `add_un_members_to_agencies.py`: Script to add UN members to UN agencies
  - `generate_environment_members.py`: Generate environment organization memberships
  - `generate_un_regional_groups.py`: Generate UN regional groups
  - `insert_environment_members.py`: Insert environment members into intblocks
  - `remove_translations.py`: Utility to remove deprecated translations field
- **Dataset expansion**: Increased international blocks from 727 to 1021+ files across 53+ categories
- **New international block**: Added PACER Plus (Pacific Agreement on Closer Economic Relations Plus) free trade agreement

### Changed
- **International Blocks dataset**: Replaced `translations` field with `other_names` field for consistency. The new field uses `id` instead of `lang` to identify languages, maintaining the same `name` structure
- **Schema updates**: Updated JSON schemas to reflect new `other_names` and `common_names` fields
- **Builder improvements**: Enhanced builder script to handle new field structures and expanded data

## 1.0

### Added
- Initial release of the Internacia Dataset Builder, a component of the **Dateno** search engine.
- Provides comprehensive availability of countries, intergovernmental organizations, and country groups data.
- Support for generating datasets in multiple formats:
    - **JSONL** (Zstandard compressed)
    - **YAML** (Zstandard compressed)
    - **Parquet** (Zstandard compressed)
    - **DuckDB** database
- CLI tool (`scripts/builder.py`) using `typer` for easy dataset generation.
- Comprehensive dataset schemas for:
    - **Countries**: 252 countries and territories with detailed attributes (ISO codes, demographics, geography, etc.).
    - **International Blocks**: 727 organizations and alliances with rich metadata (members, history, links, etc.).
- Zstandard compression (level 22) for efficient storage.
- Progress bar integration (`tqdm`) for build process visualization.

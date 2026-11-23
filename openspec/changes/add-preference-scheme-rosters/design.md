# Design: non-reciprocal preference schemes

## Context

The WTO Preferential Trade Arrangements Database (PTA Database) is the WTO register of non-reciprocal preferences that members notify under the Transparency Mechanism for PTAs (WT/L/806). It was walked on 2026-11-23 with plain HTTP requests (ASP.NET postbacks). It has 38 list rows for 37 schemes, because SPARTECA has one row for Australia and one for New Zealand. Each scheme has a beneficiary list for its latest version. 20 sub-schemes have their own lists. The database also stores tariff and trade data, which is out of scope (see decision 9).

| PTA Database type | Rows | In the registry today | Not in the registry |
|---|---|---|---|
| GSP | 17 | `GSP` (framework: 16 grantors, no beneficiaries), `GSPPLUS` | National schemes: AM, AU, CA, EU, IS, JP, KZ, KG, NZ, NO, RU (2010–2016 and from 2016), CH, TR, GB (GSP 2021–2023, DCTS from 2023), US |
| LDC-specific | 10 | none | CL, CN, IN (DFTP), KR, KG (2006–2016), ME, MA (African LDCs), TW, TJ, TH (2015–2020) |
| Other PTAs | 11 | `AGOA`, `CBERA`, `CARIBCAN`, `SPARTECA` | EU: Western Balkans, Pakistan (2012–2013), Moldova (2008–2015); US: ATPA (1991–2013), Former Trust Territory of the Pacific Islands, Nepal (2016–2025) |

The beneficiary lists of the 4 existing waiver programmes match the PTA Database, with three exceptions: Panama and Curaçao in CBERA, and Gabon in AGOA (see decision 8).

Many rosters in the PTA Database are old. The table shows the date of the latest version of each scheme:

| Latest version | Schemes |
|---|---|
| 2025-12 to 2026-06 | JP, EAEU members, GB DCTS |
| 2024 to 2025 | CA, CN, EU Western Balkans, US waiver programmes |
| 2022 to 2023 | IN, NO, TH, US GSP |
| 2018 to 2020 | NZ, MA, KG, TR, TJ, KR, TW, ME |
| 2017 or earlier | EU GSP (2017-06-29), CH (2017-01-01), IS, AU |

For example, the EU GSP+ list in the PTA Database still has Armenia, which left on 2022-01-01, and does not have Uzbekistan, which joined in 2021. The registry's `GSPPLUS` is correct on both.

## Goals and non-goals

Goals:

- Every notified scheme and sub-scheme has a registry record.
- Every grantor–beneficiary link can be joined from `country_trade_agreements`.
- A consumer can tell a grantor from a beneficiary, and a preference from a reciprocal agreement.
- Each roster stays in one place.

Non-goals:

- Tariff lines, preference margins, product coverage, rules-of-origin content, utilization rates and trade values.
- New intblocks.
- Historical beneficiary dates (a follow-up, see decision 10).

## Decisions

### 1. Preference schemes are registry records only

A national scheme is a unilateral instrument of one grantor, and its beneficiary list changes by the grantor's decision almost every year. It is a set of links from one grantor, not a group of countries that acts together. Under the inclusion policy it is not an intblock, and `docs/intblock-sources.md` already rules out national GSP and LDC-only schemes as intblocks.

New preference schemes therefore list their `parties` in the record. The quality report does not list them as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`.

The 6 existing intblocks keep their records linked, and their rosters stay in `includes`: `GSP`, `GSPPLUS`, `AGOA`, `CBERA`, `CARIBCAN` and `SPARTECA`. They are named programmes that people look up as groups.

### 2. Party role

`parties[].role` has two values, `grantor` and `beneficiary`.

On a `preference_scheme` record that lists its parties, every party sets a role. There is at least one grantor. There is at least one beneficiary, unless the record is the parent of another preference scheme and so acts as a framework (decision 3). Records of other agreement types do not set `role`: on a reciprocal agreement every party grants and receives.

The export column `role` is always filled:

- `grantor` or `beneficiary` on a preference scheme;
- `party` on every other agreement.

On a linked intblock, `contributor` maps to `grantor` and `recipient` to `beneficiary`. These are already the statuses that `AGOA`, `CBERA`, `CARIBCAN` and `GSPPLUS` use. A linked preference-scheme intblock may use no other party status, so the mapping never has to guess. Two rosters have to be fixed:

- `GSP`: all 16 grantors are `participant` and become `contributor`.
- `SPARTECA`: Australia and New Zealand become `contributor`. The Forum Island Countries become `recipient`, with their accession dates kept as `joined`.

`country_trade_agreements` keeps the role of the party row it expands. EU member states under `EU-GSP` get `role = 'grantor'` and `via = 'EU'`.

The name `role` is also used for `includes[].role` on infrastructure routes. The two do not clash: they are different tables, and each has its own enum and validator.

### 3. Sub-schemes with `parent`

`parent` names another `preference_scheme` record. Three levels are expected:

1. `GSP`: the Enabling Clause framework, with grantors and no beneficiaries.
2. A national scheme, such as `EU-GSP` or `JP-GSP`, with `parent: GSP`.
3. A named sub-scheme, such as `GSPPLUS` or `EU-GSP-EBA`, with `parent: EU-GSP`.

LDC-only schemes and waiver programmes (`CN-LDC`, `AGOA`) have no parent.

Rules:

- The parent resolves to a preference scheme, and the chain of parents has no cycle.
- A sub-scheme has the same current grantors as its parent. This is not checked when the parent has no beneficiaries, because the `GSP` framework lists EAEU states one by one while `EAEU-GSP` is granted by the bloc.
- A sub-scheme's current beneficiaries are a subset of its parent's current beneficiaries, when the parent lists any.

The legal texts work the same way. For example, Regulation (EU) No 978/2012 lists every GSP beneficiary in Annex II, and the GSP+ and EBA beneficiaries in Annexes III and IV. A sub-scheme roster is a separate legal list, not a copy of its parent's roster.

All 20 PTA Database sub-schemes are imported as records. The only exception is EU GSP+, which already exists as `GSPPLUS` and gets `parent: EU-GSP`.

### 4. Identifiers

The id is the grantor id, a hyphen and the scheme, so the scheme can be read from the id:

- national schemes: `EU-GSP`, `JP-GSP`, `CH-GSP`, `GB-DCTS`;
- LDC-only schemes: `CN-LDC`, `IN-DFTP`, `KR-LDC`, `MA-LDC`;
- other programmes: `US-ATPA`, `US-NTPP`, `US-FTTPI`, `EU-ATM-WB`;
- sub-schemes add a suffix: `EU-GSP-EBA`, `NO-GSP-ZERO`, `CA-GSP-LDCT`.

A scheme that a grantor replaced keeps its own id and uses `superseded_by`. For example, `GB-GSP` (2021–2023) has `superseded_by: GB-DCTS`.

Existing ids stay as they are (`GSPPLUS`, `AGOA`). The ids follow the registry rules: uppercase, unique, and one namespace with intblock ids.

### 5. `wto_pta_ids`

The PTA id is the hidden first id column of the PTA Database list, for example 36 for the EU GSP and 37 for AGOA. The field is a list for two reasons:

- The EAEU unified system of tariff preferences is one legal instrument, but 4 WTO members notify it: Armenia (96), Kazakhstan (87), the Kyrgyz Republic (100) and Russia (98). It becomes one record, `EAEU-GSP`, with the `EAEU` intblock as grantor. Belarus is an EAEU member that grants these preferences but is not a WTO member, so it has no PTA Database row.
- SPARTECA has one id, 80, on two rows.

No PTA id appears in more than one record.

### 6. Verification and staleness

Imported records set `verification: catalogue`. Their provenance cites `https://ptadb.wto.org/ptaList.aspx`, with the version date of the roster in `source`, for example `WTO Preferential Trade Arrangements Database, version as of 2017-06-29`. `retrieved_at` is the walk date.

`last_verified` is the walk date, as for the RTA-IS walk. Because of that, the freshness warning does not show that a roster is old. The version date in provenance and in `notes` shows it.

A record moves to `official` when its beneficiary list is checked against the grantor's own legal list. The old EU, CH, AU, IS and TR rosters go first.

A scheme whose authority has lapsed gets `status: terminated` and the lapse date as `ended`, with a note. For example, the US GSP lapsed on 2020-12-31. If the scheme is reauthorized, the record is updated in a normal data PR.

### 7. Country code crosswalk

PTA Database country links use WTO numeric codes. Most of them map to alpha-2 through the `numeric_code` and `m49_code` fields of `data/countries`. Fixed overrides cover the rest:

- `899` → the `EU` intblock;
- `893` → `ME`;
- `892` → `RS`;
- `888` → `XK`;
- `736` → `SD` (the code Sudan used before 2011);
- `158` → `TW`.

Dependent territories (AI, IO, FK, CX and others) are countries in `data/countries` and use `type: country`. Two entries are parts of a member state and get no party row: Canary Islands (`128`) and Ceuta and Melilla (`146`). The record notes name them.

### 8. Existing records

The import adds `wto_pta_ids` to `AGOA` (37), `CBERA` (78), `CARIBCAN` (70) and `SPARTECA` (80), and `parent: EU-GSP` to `GSPPLUS`. It does not overwrite their rosters, which come from official sources. Three differences are checked against USTR:

- the PTA Database has Panama in CBERA, and the registry does not;
- the registry has Curaçao in CBERA, and the PTA Database does not (it lists Aruba under the Kingdom of the Netherlands);
- the registry has Gabon in AGOA, and the PTA Database version of 2025-03-21 does not.

### 9. Scope guardrail

The PTA Database "Tariffs & Trade" pages (tariff lines, preferential margins, imports) are not read. The schema gets no numeric trade fields: `wto_pta_ids` is a catalogue key. This follows the `trade-agreements` scope requirement.

### 10. Follow-up: historical beneficiary dates

Each PTA Database version (for example 15 versions of AGOA since 2000) has its own beneficiary list. Comparing the versions gives each beneficiary an `in_force` date (the first version that lists it) and a `left` date (the first version that drops it). These dates show graduations and suspensions.

The scraper must post the version id explicitly. The "As of" dropdown is cached on the server across sessions and often shows another scheme's versions, so a version id is mapped to a date only when the scheme name on the page matches. A separate change handles this.

## Risks

- **Old rosters presented as current.** Mitigation: `verification: catalogue`, the version date in provenance and notes, and decision 6.
- **Consumers counting trade links.** `country_trade_agreements` grows by about 2,500 rows. Mitigation: the `role` column, the changelog note, and a query example that filters on `role = 'party'`.
- **Fragile scraping.** The PTA Database has no API, and the version dropdown is unreliable. Mitigation: a one-off script that only uses the list export, the scheme cards and the beneficiary pages; a committed crosswalk; hand review of every new id.

## Open questions

1. The Customs Union scheme of 2010–2016 (Russia's row 83; Belarus and Kazakhstan applied the same system) and the EAEU scheme from 2016: one record or two? The default is two, `RU-GSP-2010` with `superseded_by: EAEU-GSP`, because the PTA Database splits them and the grantor changed from the Customs Union to the EAEU.
2. Should the PTA Database type (GSP, LDC-specific, other) get its own field? The default is no. GSP schemes can be found through `parent`. LDC-only schemes are recognized by name, and this can be revisited when a consumer needs it.

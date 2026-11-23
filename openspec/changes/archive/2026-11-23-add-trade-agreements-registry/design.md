# Design: trade agreements registry

## Context

Trade agreements are now intblocks under `data/intblocks/{fta,pta,customs}/`. The inclusion policy keeps named plurilaterals and skips untitled bilateral pairs, but 34 bilateral records were added anyway because they have well-known names (`USKR`, `CETA`, `CHAFTA`). The maintainer wants a complete world registry, bilateral agreements included, that can be compared across countries. Precedent for a separate edge-like dataset: `border_status` (`data/borders/border_status.yaml`, its own schema, table and view).

Sources: WTO RTA-IS (about 370 agreements in force, notified only), ADB ARIC (433 rows, Asia-Pacific parties only, includes non-notified, proposed and negotiating agreements), and official treaty texts and depositaries.

## Goals and non-goals

Goals: one record per legal instrument; every country pair with an agreement can be joined; no roster is kept in two places; existing join keys keep working through aliases.

Non-goals: trade values, tariff schedules, preference margins, depth or coverage indices, rankings, agreement text, and negotiation round histories.

## Decisions

### 1. Layout

`data/trade_agreements/<ID>.yaml`, one file per agreement. A flat directory with one file per record keeps data PRs free of conflicts. Validated by `data/schemas/trade_agreements.schema.json` and by rules registered in `internacia_builder/validate/registry.py` (`internacia_builder/validate/trade_agreement_rules.py`). They run in `scripts/validate_intblocks.py`, because they resolve intblocks.

Record fields:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | See decision 4 |
| `name` | yes | English name as used by the parties or the depositary |
| `acronyms`, `other_names` | no | Same shape as intblocks |
| `agreement_type` | yes | `fta`, `customs_union`, `pta` (reciprocal partial-scope or preferential), `preference_scheme` (non-reciprocal, such as GSP and AGOA), `services` (services or investment only), `digital`, `framework`, `other` |
| `status` | yes | `proposed`, `negotiating`, `signed`, `in_force`, `terminated`, `abandoned` (signed or negotiated, never in force), `superseded` |
| `signed`, `in_force`, `ended` | by status | ISO date or partial date; on a linked record they override the intblock's dates |
| `parties` | unless `intblock` is set | List of `{id, type: country or intblock, signed, in_force, left, note}` |
| `intblock` | for 3+ parties, once signed | The linked intblock id; parties come from its `includes` |
| `supersedes`, `superseded_by` | no | Registry ids |
| `wto_rta_id`, `aric_id` | no | Integers from the catalogues |
| `wikidata_id`, `links`, `notes` | no | Same shape as intblocks |
| `verification` | yes | `official` (dates and parties checked against the treaty text or a party government) or `catalogue` (taken from WTO RTA-IS or ARIC only) |
| `last_verified`, `provenance` | yes | At least one provenance entry; `official` records need one for `parties` from a government or depositary |

### 2. Two parties or more

An agreement is **bilateral** when exactly two parties have ever been party to it. A party is a country or a bloc that signs as one party (the EU, or a customs union that negotiates as one). EFTA states, ASEAN members and EAEU states that sign individually count one by one, so `EFTAGCC`, `INDIAEFTA` and the ASEAN+1 FTAs are multilateral. Former parties count, so `G-3` (Colombia, Mexico, former Venezuela) stays multilateral.

Bilateral agreements live only in the registry. Multilateral agreements that are signed or in force are also intblocks: they are country groups that people query. A proposed or negotiating multilateral agreement has registry parties and no intblock until it is signed. A catalogue-level record may list the parties a catalogue gives, including a bloc that stands for its member states; the quality report lists signed or in-force records with three or more parties and no intblock as intblock candidates, so a missing intblock does not block an import.

### 3. One roster per agreement

A registry record with `intblock` set SHALL NOT have `parties`, `name` or `wikidata_id`. The build reads parties from the intblock's party-like `includes` (id, type, `joined`, `left`; observers and partners are not parties). Dates come from the intblock (`founded` as `signed`, `active_period.start` as `in_force`) unless the record sets them, because an organization's `founded` is not always the signature of its trade agreement (`EAEU`, `AfCFTA`). Contributors keep editing the roster in one place, and the registry and the intblock cannot disagree.

### 4. Identifiers

- Records moved from intblocks keep their ids (`USKR`, `CETA`).
- Records linked to an intblock use the intblock id (`RCEP`).
- New bilateral records between two countries use the two alpha-2 codes in alphabetical order (`AMGE`, `JPUS`). New bloc–country records put the bloc id first (`EAEUVN`, `EFTASG`), as in `EFTAGCC` and `EUJP`.
- A second agreement between the same parties adds a suffix for the instrument (`JPUS-DTA`, `TNTR-CEPA`).
- Registry ids and intblock ids are one namespace. A registry id equal to an intblock id is allowed only when `intblock` names that id.

### 5. Migration and version (decided: option A)

Option A, recommended: **5.0.0 MAJOR**. Move the 34 YAML files in one step, add `moved` aliases with `target_dataset: trade_agreements`, and document the replacement queries (`trade_agreement_parties`, `country_trade_agreements`). `memberships` no longer returns bilateral FTAs, which changes what a consumer gets for "groups of country X". A MAJOR bump states that clearly.

Option B: **4.4.0 MINOR, then 5.0.0**. Add the registry in 4.4.0 and keep the 34 intblocks for one release as deprecated. The build generates their intblock rows from the registry records, so there is one source. Remove the rows in 5.0.0. This keeps consumers working longer but needs a compatibility path in the build.

The `TELESUR` retirement shipped in a MINOR release, but it removed one wrong record, not a class of 34.

### 6. Verification levels

ARIC and WTO rows can be imported as `verification: catalogue` with parties and status from the catalogue. They are counted separately in the quality report, and `last_verified` follows the catalogue retrieval date. A registry record linked to an intblock, and every moved record, is `official`. Moving a record from `catalogue` to `official` is a normal data PR.

### 7. ARIC import

A one-off script `scripts/oneoff/import_aric_ftas.py` reads the `arrayFTA`, `arrayType` and `arrayCountry` objects embedded in `https://aric.adb.org/database/fta-all` and writes one YAML per row that does not map to an existing record:

- ADB economy codes (`PRC`, `INO`, `SIN`, `TAP`) are mapped to alpha-2 through a checked crosswalk.
- ARIC lists only ADB-member parties, so the other party is taken from the title (bloc names map to intblock ids: EU, EFTA, EAEU, CCASG, MERCOSUR, SACU, Pacific Alliance) and checked by hand.
- Status: `Signed and In Effect` → `in_force`, `Signed but not yet In Effect` → `signed`, `Negotiations launched` → `negotiating`, `Proposed/Under consultation and study` → `proposed`, `(FA) signed` → `framework`/`signed`, `Discontinued` → `terminated` or `abandoned` by hand.
- ARIC rows that are not trade agreements in the narrow sense (Compacts of Free Association, TIFAs, digital and green economy agreements, strategic partnership agreements) are kept with `agreement_type` `other`, `framework` or `digital`, because the registry mirrors the catalogue.
- Upgrades and second protocols listed separately in ARIC are one record with a note, not two (one record per legal instrument).
- ARIC statuses lag; rows where a later official source differs are corrected and marked `official`.

### 8. Country expansion view

`country_trade_agreements` has one row per (country, agreement). Country parties map directly. A bloc party is expanded to its **current** members from `current_memberships`, with `via` set to the bloc id. This gives current coverage (Croatia under `EUKR` from 2013, the United Kingdom not under `EUKR` after 2020) but not historical coverage, and the documentation says so.

### 9. Scope guardrail

The schema has no numeric trade fields. Free text in `notes` is for legal facts (accessions, suspensions, supersession), not for trade volumes. A record never judges whether an agreement is good, deep or important.

## Risks

- **Volume.** About 600 to 800 records once WTO RTA-IS is also walked. Mitigation: one file per record, catalogue-level records allowed, ids are mechanical.
- **Party resolution errors in ARIC.** Mitigation: hand review of every title where the second party comes from the title, and validator checks that parties resolve to countries or intblocks.
- **Breaking change.** Mitigation: aliases with `target_dataset`, migration SQL in the changelog, decision 5.

## Open questions

1. Decision 5: resolved on 2026-11-22, option A (5.0.0).
2. Should proposed and negotiating agreements stay in the main `trade_agreements` table, or go to a separate `trade_agreement_candidates` file? The default is the main table, filtered by `status`.
3. After ARIC, walk WTO RTA-IS in full (about 370 in force) as the next catalogue? The default is yes.

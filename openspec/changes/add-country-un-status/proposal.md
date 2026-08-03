# Change: Add UN participation status and explicit flags on non-standard codes

## Why
Verified on 2026-08-02: the countries schema cannot represent the UN's "193 members + 2 observers" structure — `VA` and `PS` carry only `un_member: false`, indistinguishable from ordinary non-members. All 7 non-standard code records (`AN`, `JG`, `KV`, `XA`, `XS`, `XT`, `XN`) omit `un_member`, `independent`, and `landlocked` entirely rather than stating explicit values, which is ambiguous for consumers (absence vs false). Wikidata-sourced `population` entries for `KV`, `XA`, `XS`, `XT`, `XN` lack `year`. Finally, the documented country-code policy does not state the disputed-territory inclusion threshold (Abkhazia/South Ossetia/Transnistria are included while Somaliland and Northern Cyprus are not), does not warn about the `JG` aggregate double-count trap (JG population is not GG+JE), and does not mention the exceptionally reserved codes (`EU`, `EZ`, `UN`).

## What Changes
- Add an optional `un_status` field to `data/schemas/countries.schema.json` (enum: `member`, `observer`, `non_member`); set `observer` on `PS` and `VA`, `member` on the 193 members, `non_member` elsewhere; keep `un_member` for compatibility.
- Set explicit `un_member`, `independent`, and `landlocked` values on the 7 non-standard code records.
- Backfill `year` on the Wikidata-sourced population entries for `KV`, `XA`, `XS`, `XT`, `XN` (retrieval year when the reference year is unknown, consistent with existing policy).
- Extend `docs/country-code-policy.md` with: the disputed-territory inclusion rule (why XA/XS/XT are in and Somaliland/Northern Cyprus are out, or a decision to add `XL`/`XC` records), the `JG` aggregation double-count note, and a one-line note on exceptionally reserved ISO codes (`EU`, `EZ`, `UN` — `EU` exists as an intblock, not a country).

## Impact
- Affected specs: countries-entity-model
- Affected code: `data/schemas/countries.schema.json`, `data/countries/{AN,JG,KV,XA,XS,XT,XN,PS,VA,...}.yaml`, `internacia_builder/validate/country_rules.py`, `docs/country-code-policy.md`, regenerated `data/datasets/`

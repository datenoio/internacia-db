# Design: include labels and associate statuses

## Context
`includes[]` entries carry `{id, name, type, status, joined, left, role, note}`. The `id` is the
join key. `name` was declared a free display label, and `status` is a closed enum
(`intblocks.schema.json`) described in `includes_status.yaml`. Measured on 2026-11-19:

| | Count |
|---|---|
| `type: country` entries | 59,050 |
| … whose `name` equals the country `name` | 55,549 |
| … whose `name` differs (95 id–name pairs) | 3,501 |
| associate-tier entries (`associate` 55, `associated` 57, `associate_member` 210) | 322 in 55 records |

## Decisions

### Labels come from the country record
The build writes the referenced country's `name` into exported `includes[].name` for
`type: country`. The source YAML is normalized to the same value once, so a reader of the YAML
sees what the export shows. New and rewritten entries may omit `name`; the build fills it in.
Organization, territory and historical-country entries keep their source names, because there is
no canonical record to copy from.

A membership that ended before a rename (an SZ entry with `left` before the 2018 rename to
Eswatini, say) also shows the current name. The label identifies the country by `id`; history belongs in
`joined`/`left` and the country's own naming fields.

Alternatives considered:
- **Keep free labels and improve the advisory.** This costs nothing now, but consumers keep seeing
  "Macedonia, FYR" and "Turkey".
- **Drop `name` from every country entry in the source.** That removes 59,050 lines and all drift,
  but the YAML becomes hard to read during review. It remains possible later, because the build
  already fills missing names.
- **Copy a display name instead of `name`.** There is no display field yet. CLDR English names are
  concise, but the short forms are "US" and "UK" and the full forms include "Congo - Brazzaville"
  and "Hong Kong SAR China". UN M49 names are formal ("Iran (Islamic Republic of)"). Wikidata
  labels lag official renames (TR "Turkey"). Picking one is a separate change.

### One value per associate arrangement
- `associate_member`: the organization's instrument names the status "associate member(s)" or
  "associate membership" (CERN, UNESCO, IMO, FAO, CARICOM, OECS, ICC, …).
- `associated`: an association that the instrument does not call membership, such as "associated
  countries" or "associated nations". EUREKA, EUROCORPS and NORDEN use `associated` today; the
  review confirms or recodes each of them.
- `associate` is retired, and its records are recoded to one of the two values above.
  `associated_observer` is retired as well; it is unused.

Each of the 27 records with `associate` or `associated` is checked against the source in its
`provenance`. Recoding a status is a roster change, so it refreshes `last_verified`.

### Deprecating enum values
`contract.json` `deprecated[]` lists columns and resources today. It gains entries of the form
`{kind: "enum_value", table: "memberships", column: "status", value: "associate", removal: "next
MAJOR", replacement: "associate_member"}` (and the same for `intblocks.includes[].status`). The
values stay valid until the MAJOR release, and `DEPRECATED_INCLUDE_STATUS` warns on any new use.

## Result (2026-11-19)
- Labels: 3,501 source names in 804 files rewritten; validation reports no `INCLUDE_NAME_MISMATCH`.
- Deprecated `associate` → `associate_member`, checked against each organization's wording
  (term only, a vocabulary migration that the `last_verified` rule exempts): UNESCO (12; "194
  member states and 12 associate members"), SCAR (13; "35 full and 13 associate members"), ACS
  (10; "10 Associate Members"), IMO (3; "three Associate Members"), EMBL (Australia; "Associate
  Member"), OECD DAC (Romania; listed under "Associate" between Members and Participants).
- `associated` → `associate_member` with the roster checked in both directions against the
  source and `last_verified` 2026-11-19: OECS (5), PASO (3), MSG (Indonesia; Wikipedia, the
  record's source), Dutch Language Union (Suriname; its Caribbean territories stay `associated`).
- Completed 2026-11-21 (validation reports no `DEPRECATED_INCLUDE_STATUS`). GRECO, CEOS and FAO
  were read from Wayback Machine copies of their official pages because the live pages served
  bot checks; AMN's site did not respond, so its archived page was used:
  - CEOS: 12 `associate` → `associate_member` (the agencies page heads the tier "32 Associate
    Members"); roster checked against the 2026-10-03 copy, `last_verified` 2026-11-21.
  - AMN: Bolivia and Chile `associate` → `associate_member` ("Associated members are the NSBs
    of the countries registered as Associated States in MERCOSUR"). Term only: the only
    readable copy (2025-05-29) predates the record's last check, so `last_verified` stays.
  - GRECO: Belarus `associate` → `former_member`, not an associate tier. GRECO's members page
    says Belarus "ceased to be a member of GRECO with effect from 1 May 2024".
    `membership_count` 49 → 48 ("48 member States"); the Poland and Russian Federation
    `joined` dates were corrected from the same page.
  - FAO: Faroe Islands and Tokelau `associated` → `associate_member` ("two Associate
    Members"); roster of 193 Member Nations, the EU and the two checked in both directions.
  - CIAT: Angola, India, Morocco and Nigeria `associated` → `associate_member` ("two membership
    categories in CIAT – member countries and associate member countries"); 42-country roster
    checked against the NTO factsheet.
  - IOTA: Korea `associated` → `associate_member` ("ASSOCIATE MEMBERS"); Uzbekistan added as
    the second associate member (2026); first `last_verified`.
  - IICA: Spain stays `associated` (listed as "Associated country").
- Not recoded:
  - ERRA's roster was refreshed in its own change, which recoded its associate members.
  - COPANT's page does not name the tier.
  - Cospas-Sarsat's categories (Ground Segment Providers, User States) are not association.
  - EUROCONTROL (Comprehensive Agreement States), EUCU, the Pacific Alliance (Singapore,
    "Associated State"), EUROCORPS (associated nations), NORDEN and EUREKA (associated
    countries) stay `associated` as recorded.
- Seen in passing: the IMO page lists 176 Member States without Nauru, while the record has NR.

## Risks / Trade-offs
- About 3,500 changed lines in one data PR. Mitigation: it is mechanical, generated by a
  script, and checked by the rule itself.
- Status recoding needs judgement per organization. Mitigation: each record cites its instrument,
  and the PR lists every recoded record with its source.
- Consumers that match `associated` lose rows at the MAJOR release. Mitigation: deprecation in a
  MINOR release first, and both values are documented as one tier in the meantime.

## Migration
1. PATCH: build fill, source normalization, `INCLUDE_NAME_MISMATCH` as a warning.
2. MINOR: recode the 27 records, deprecate `associate` and `associated_observer`, add
   `DEPRECATED_INCLUDE_STATUS`.
3. MAJOR: remove both values from the schema enum, `includes_status.yaml` and `contract.json` enums.

## Open Questions
- Should `INCLUDE_NAME_MISMATCH` become an error once the source is normalized? This proposal keeps
  it a warning, so the monthly roster tooling cannot block CI on a rename.
- Does any record use `associated` for something that is neither membership nor association (for
  example a dependent territory listed under its sovereign)? The per-record review answers this;
  such entries would move to `represented`.

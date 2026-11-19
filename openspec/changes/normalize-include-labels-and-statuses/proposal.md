# Change: One label per country in includes, and one status for associate members

## Why
Two parts of `includes[]` look controlled but are not, so consumers get inconsistent answers.

- **Labels.** Of 59,050 `type: country` entries, 3,501 have a `name` that differs from the
  country's `name`, in 95 distinct id–name pairs. Many are stale: TR `Turkey` (278 entries), MK
  `Macedonia, FYR` (166), CV `Cape Verde` (138), SZ `Swaziland`. Others are alternatives such as EG
  `Egypt` vs `Egypt, Arab Rep.`. The spec allows this ("`name` MAY differ"), and the analyzer only
  logs a LOW advisory. The exported `intblocks.includes[].name` therefore shows several names for
  the same country, and the stale ones are wrong.
- **Associate statuses.** The schema enum has `associate`, `associated` and `associate_member`, and
  they are applied inconsistently to the same concept. UNESCO and IMO record their associate members
  as `associate`, FAO and OECS as `associated`, CERN, CARICOM and ICC as `associate_member` (322
  entries in 55 records in total). `associated_observer` is in the enum but unused. A consumer who
  filters `status = 'associate_member'` misses UNESCO's associate members.

## What Changes
- **Labels (PATCH):**
  - The build exports `includes[].name` for `type: country` from the referenced country's `name`.
  - Source `name` becomes optional for `type: country` entries.
  - The 3,501 differing source names are rewritten to the country `name` in one mechanical change.
  - `INCLUDE_NAME_MISMATCH` becomes a validator warning for country entries whose source `name`
    is present and differs from the country `name`.
  - Organizations, territories and historical countries keep their source names.
- **Associate statuses (MINOR, then MAJOR):**
  - `associate_member` is the value for every arrangement that the organization's own instrument
    calls associate membership.
  - `associated` is kept only for association arrangements that are not memberships ("associated
    states", "associated countries").
  - The 27 records using `associate` or `associated` are reviewed against their sources and
    recoded.
  - `associate` and `associated_observer` are listed in `contract.json` `deprecated[]` in a MINOR
    release (a new `enum_value` kind) and are removed from the enum in the next MAJOR.
  - A new `DEPRECATED_INCLUDE_STATUS` warning flags any remaining use.
- `includes_status.yaml`, `docs/ai-consumers.md` and the status table are rewritten with definitions
  that say when to use each value.

## Not in scope
- `membership_count`. It is already checked by `MEMBERSHIP_COUNT_MISMATCH` (tolerance 0, matching
  either the full roster or the member-class entries), and `membership_count_type` exempts
  non-country headcounts (WNA 3000, IGA 10000). Validation reports no mismatch today.
- A display-oriented country name (`display_name`). Country `name` follows World Bank style
  ("Egypt, Arab Rep.", "Korea, Rep."). Choosing a display source (CLDR, UN M49 or Wikidata) is a
  separate decision, see design.md. Once it exists, this change's build step can read it instead of
  `name`.

## Impact
- Affected specs: cross-dataset-integrity (Include name is display label only; Include display-name
  advisory rule), intblocks-data-quality (Intblock includes contract enforcement; new Associate-tier
  include statuses)
- Affected code: `internacia_builder/export.py` (include labels),
  `internacia_builder/validate/cross_rules.py` (`check_include_name_mismatch`),
  `internacia_builder/validate/intblock_rules.py` (status check), `internacia_builder/contract.py`
  (`deprecated[]` enum values), `data/schemas/intblocks.schema.json`, `data/schemas/includes_status.yaml`
- Affected data: about 3,500 `includes[].name` values across the intblocks; associate statuses in 27
  records
- Consumers: exported country labels change to the country `name` (PATCH, values only). Filters on
  `associate` or `associated` must add `associate_member` from the MINOR release on. The removed
  values are a MAJOR change, batched with the next MAJOR.

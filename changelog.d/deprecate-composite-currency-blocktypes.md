### Added

- `EUROAREA` (euro area, Wikidata Q8268), a `currency` record for the 21 EU member states
  that use the euro, with adoption dates from the ECB roster and `partof: EU`, checked on
  2026-11-22. It shares Q8268 with its World Bank mirror `EMU`.

### Changed

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

### Deprecated

- Blocktypes `eccurr` (replacements `economic`, `currency`) and `cuscurr` (replacements
  `customs`, `currency`) are deprecated and listed in `contract.json` `deprecated`. A
  blocktype never combines two other blocktypes. Queries on them return the same records
  (`OECS`; `CEMAC`, `UEMOA`) until they are removed in the next MAJOR release. Replacement
  queries: `list_has_all(blocktype, ['economic', 'currency'])` and
  `list_has_all(blocktype, ['customs', 'currency'])`.

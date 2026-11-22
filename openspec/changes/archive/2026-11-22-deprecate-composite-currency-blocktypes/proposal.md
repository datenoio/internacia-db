# Change: Deprecate the composite currency blocktypes `eccurr` and `cuscurr`

## Why

`eccurr` (Economic and Currency Union) and `cuscurr` (Customs and Currency Union) are
the least used blocktypes. One record carries `eccurr` (`OECS`, as its primary
blocktype). Two records carry `cuscurr` (`CEMAC`, `UEMOA`, as a secondary tag). The
types have not gained a record since the initial release, and in v1.4.0 their other
record (`CMA`) moved to `currency/`.

The types do not work as blocktypes:

- **They are combinations of other blocktypes.** `blocktype` is a list, so "customs
  union that shares a currency" is already `[customs, currency]`, and "economic union
  that shares a currency" is `[economic, currency]`. Other records already use such
  lists (`EAEU` `[economic, customs]`, `CCASG` `[economic, customs, political]`, `ECB`
  `[bank, currency, ...]`). A composite key duplicates two keys and splits the
  query: `list_contains(blocktype, 'currency')` misses `OECS`, `CEMAC` and `UEMOA`.
- **They encode a stage of economic integration, not a domain.** The stages (PTA,
  FTA, customs union, common market, economic union, monetary union) are a judgment
  about how far a bloc has integrated. The current values contradict each other:
  `UEMOA` and `CEMAC` are by name economic and monetary unions but carry `cuscurr`;
  `OECS` carries `eccurr`, although its currency union is the separate record `ECCU`
  and Montserrat did not ratify the economic union; the European Union, the largest
  economic and monetary union, carries neither.
- **The currency layer is already modelled.** Currency unions are their own records in
  `currency/` (`CFAWEST` has the `UEMOA` roster, `CFACENTRAL` the `CEMAC` roster,
  `ECCU` is `partof: OECS`), and their central banks are `bank/` records with `partof`
  (`BCEAO`, `BEAC`, `ECCBCB`). A country's currency union membership is a join on the
  `currency/` record, not a tag on the regional organization.

The review also found gaps in the currency and customs layers:

- **The euro area has no `currency/` record.** Only `ECB` (a bank) and `wbgroup/EMU`
  (a World Bank aggregate) list its members, and `EMU` still lists 20 members, without
  Bulgaria, which adopted the euro on 1 January 2026.
- **`SCHENGENAREA` is filed under `customs/`.** Schengen abolishes internal border
  checks and sets a common visa policy. It is not a customs union: Iceland, Norway,
  Switzerland and Liechtenstein are in Schengen but outside the EU customs union.
- **`UNASUR` carries `customs`.** UNASUR never created a customs union.

## What Changes

- Mark `eccurr` deprecated with replacements `[economic, currency]` and `cuscurr`
  deprecated with replacements `[customs, currency]`, removal in the next MAJOR. Add
  both to `data/schemas/deprecated_blocktypes_baseline.yaml` (`eccurr`: `OECS`;
  `cuscurr`: `CEMAC`, `UEMOA`), so the existing deprecation gates apply.
- State the rule that a blocktype never combines two other blocktypes, and the rule for
  a secondary `currency` tag on an organization (design D3). Update the scope notes of
  `currency`, `customs`, `eccurr` and `cuscurr`.
- Migrate the baseline records: move `OECS` from `eccurr/` to `economic/` as
  `[economic, political, currency, eccurr]`; set `CEMAC` and `UEMOA` to
  `[customs, currency, cuscurr]`.
- Add the record `currency/EUROAREA` (euro area, 21 members, `partof: EU`, Wikidata
  `Q8268`). Add Bulgaria to `wbgroup/EMU`, as the World Bank API now lists it.
- Move `SCHENGENAREA` from `customs/` to `travel/`. Remove `customs` from `UNASUR`.
- **BREAKING (next MAJOR, v5.0.0):** remove `eccurr` and `cuscurr` from the three
  records and from the taxonomy, together with `intorg`.

## Impact

- **Affected specs:** `intblocks-data-quality`, `dataset-release`.
- **Affected source data:** `data/blocktypes/blocktypes.yaml`;
  `data/schemas/deprecated_blocktypes_baseline.yaml`;
  `data/schemas/intblocks_completeness.yaml` (shared Wikidata id `Q8268`); records
  `OECS`, `CEMAC`, `UEMOA`, `SCHENGENAREA`, `UNASUR`, `EMU`; new record `EUROAREA`.
- **Affected code:** none. `internacia_builder/contract.py` already lists every
  deprecated blocktype, and the ratchet and primary-blocktype gates already read the
  baseline file.
- **Affected docs and tests:** `docs/intblock-inclusion-policy.md`,
  `docs/data-contract.md`, `docs/ai-consumers.md`, `docs/agents/contribute.md`;
  `tests/test_include_labels_and_statuses.py` (contract deprecation entries) and any
  cookbook count the new record changes.
- **Consumers:**
  - MINOR (4.x): `OECS` and `SCHENGENAREA` change folder (IDs do not change, so no
    alias is needed). `list_contains(blocktype, 'currency')` now also returns `OECS`,
    `CEMAC`, `UEMOA` and `EUROAREA`. `list_contains(blocktype, 'customs')` no longer
    returns `SCHENGENAREA` or `UNASUR`. Queries on `eccurr` and `cuscurr` return the
    same rows as before.
  - MAJOR (5.0.0): `eccurr` and `cuscurr` return no rows. Replacement queries:
    `list_has_all(blocktype, ['economic', 'currency'])` and
    `list_has_all(blocktype, ['customs', 'currency'])`.

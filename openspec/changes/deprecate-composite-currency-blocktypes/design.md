# Design: deprecate-composite-currency-blocktypes

## Context

The blocktype taxonomy has `currency`, `customs` and `economic`, plus two composite keys
from the initial release: `eccurr` (economic union with a shared currency) and `cuscurr`
(customs union with a shared currency). Those keys follow the textbook stages of
economic integration. Since `blocktype` became a list, every combination of domains can
be written with the domain keys themselves.

`reorganize-intorg-blocktype` added the deprecation mechanism: a `deprecated` marker in
`blocktypes.yaml`, a reviewed baseline of record IDs in
`data/schemas/deprecated_blocktypes_baseline.yaml`, the `DEPRECATED_PRIMARY_BLOCKTYPE`
and `DEPRECATED_BLOCKTYPE_RATCHET` gates, and `contract.json` `deprecated` entries.
This change reuses that mechanism without code changes.

## Goals / Non-goals

- Goals: one way to say "this bloc also shares a currency"; a complete set of currency
  union records for current unions; customs records that are customs unions.
- Non-goals: an attribute for the stage of economic integration (common market,
  economic union). The stage is a judgment that needs its own sourcing rules; propose
  it separately if consumers ask for it. Historical currency unions (Latin Monetary
  Union, Scandinavian Monetary Union) are discovery work, not part of this change.

## Decisions

### D1. Deprecate in a MINOR release, remove in the next MAJOR

Removing a blocktype value changes query results, so it follows the `intorg` path:
deprecate now, keep the value as the last blocktype of its baseline records, remove it
in v5.0.0. The baselines are small (one and two records), but consumers may still filter
on the value, and the gates already exist.

Alternative considered: remove now in a MAJOR release of its own. Rejected: v5.0.0
already removes `intorg`, and one breaking release is cheaper for consumers than two.

### D2. Replacements

| Deprecated | Replacements | Replacement query |
|---|---|---|
| `eccurr` | `economic`, `currency` | `list_has_all(blocktype, ['economic', 'currency'])` |
| `cuscurr` | `customs`, `currency` | `list_has_all(blocktype, ['customs', 'currency'])` |

### D3. When an organization carries `currency`

A currency union or shared-currency area is its own record in `currency/`. Its
`includes` list is the authoritative roster for "countries that share this currency".

An organization in another folder carries `currency` as a secondary blocktype only when
its own founding instruments establish or administer the shared currency and every
full member uses it:

| Record | Instrument | Full members using the currency | `currency` |
|---|---|---|---|
| `UEMOA` | UEMOA Treaty (1994) with the UMOA Treaty; BCEAO | 8 of 8 (XOF) | yes |
| `CEMAC` | CEMAC Treaty with the UMAC Convention; BEAC | 6 of 6 (XAF) | yes |
| `OECS` | Revised Treaty of Basseterre (monetary policy competence) and ECCB Agreement (1983) | 7 of 7 (XCD) | yes |
| `EU` | TFEU, economic and monetary union; ECB | 21 of 27 (EUR) | no; `EUROAREA` holds the roster |
| `SACU` | SACU Agreement (customs only) | not applicable | no; `CMA` is a separate instrument |

Central banks (`bank/`) keep `bank` as their domain. `ECB` keeps its existing
`currency` tag.

### D4. Target blocktypes for the baseline records

- `OECS` moves to `economic/` as `[economic, political, currency, eccurr]`. The Revised
  Treaty of Basseterre creates an economic union, so `economic` is primary, as for
  `SADC` and `EU` (`[economic, political]`). `political` covers its foreign-policy and
  security coordination (`institutional_design.mandate: general`).
- `CEMAC` and `UEMOA` stay in `customs/` as `[customs, currency, cuscurr]`. Their common
  external tariff makes them customs unions; their primary blocktype does not change.

The deprecated value stays last, as the ratchet requires.

### D5. Euro area record

`currency/EUROAREA` is the euro area as a currency union: the 21 EU member states that
use the euro (ECB roster), with `joined` on the 1 January of the adoption year,
`partof: EU`, `legal_status: monetary_union` and `scope_category:
reference_enumeration`, like `ECCU`. Non-EU users are not members: Andorra, Monaco, San
Marino and Vatican City use the euro by monetary agreement (already the `MICEU` record),
and Montenegro and Kosovo use it unilaterally. Those are noted in `notes`, not
`includes`.

Wikidata has one item for the euro area, `Q8268`, already used by `wbgroup/EMU`. Add it
to `references.wikidata_duplicate_allowlist`, as `Q458` is shared by `EU` and its World
Bank mirror `EUU`. The ID `EUROAREA` follows the ECB and Eurostat term; `EA` is listed
as an acronym.

`wbgroup/EMU` is the World Bank aggregate, not derived from country fields, so it is
edited by hand. The World Bank API (`/v2/region/EMU/country`) lists 21 economies
including Bulgaria.

### D6. Customs folder corrections

- `SCHENGENAREA` moves to `travel/` ("travel-document and visa regimes") as `[travel]`.
- `UNASUR` drops `customs` and stays `[political]`.

### D7. Gaps reviewed and not added

- Switzerland–Liechtenstein (Customs Treaty 1923, Currency Treaty 1980): the inclusion
  policy skips untitled bilateral `Country A – Country B` pairs.
- Monaco, San Marino and Andorra with the EU customs union: already in `EUCU` `includes`
  (Monaco as a member of the customs territory, Andorra and San Marino as `associated`).
- SACU with CMA: two records already exist, one per instrument.

## Risks / Trade-offs

- `list_contains(blocktype, 'currency')` returns both a currency union record and the
  organization that administers it (`CFAWEST` and `UEMOA`). Consumers counting currency
  unions should filter on the `currency/` folder (primary blocktype `currency`).
  `docs/ai-consumers.md` states this.
- Folder moves change source paths, not IDs. Consumers that read YAML by path are not
  supported (the exports are the contract).

## Migration

MINOR: no consumer action. MAJOR (v5.0.0):

```sql
-- before
SELECT id FROM intblocks WHERE list_contains(blocktype, 'cuscurr');
-- after
SELECT id FROM intblocks WHERE list_has_all(blocktype, ['customs', 'currency']);
```

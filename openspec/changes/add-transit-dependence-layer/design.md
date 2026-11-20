# Design: Transit dependence layer

## Context

`add-intblock-institutional-design` added the authority axis of influence, and left capacity (population, GDP, military spending) to recipes and external data. Trade adds a third channel of influence, and it has two parts:

- **Bilateral dependence.** How much of A's trade is with B, compared with how much of B's trade is with A. Hirschman (1945) located leverage on the side for which the trade matters less. This is a time series from trade statistics, so it stays downstream, like GDP.
- **Transit dependence.** Whose territory A's trade must cross. For a landlocked country this can matter more than trade volume. The structure of transit is partly reference data: land borders, coastlines, the countries a pipeline crosses, and whether a border can be crossed.

The repository has the following inputs today:

| Input | Where | State |
|---|---|---|
| Land borders | `countries.borders` (alpha-3) | Complete; reciprocity checked |
| Sea access | `countries.landlocked` | 44 official countries landlocked; Caspian littoral states count as landlocked |
| Gas pipelines | 25 intblocks with blocktype `gaspipeline` | 68 country entries, all `status: member`; no role |
| Transport corridors | TRACECA, ASIANHIGHWAY, TARAGREEMENT, AGC, CKURAILWAY, LANDLOCKEDTRANSIT, TIR1975 | Rosters of treaty parties, not positions on a route |
| Border crossing status | none | — |
| `includes[].role` | Arrow export and `clean.py` | Exported as an always-null column; not declared in the JSON Schema |

A prototype breadth-first search over `borders`, with `landlocked` marking the sea, gives the following results:

- **Single direct coastal neighbour:** KG (CHN), LS (ZAF), SM (ITA), TJ (CHN), TM (IRN), VA (ITA).
- **Doubly landlocked:** LI and UZ, two borders from a coast.
- **Armenia:** Georgia, Iran and Türkiye are direct coastal neighbours, and Azerbaijan is two borders from a coast. With the Türkiye and Azerbaijan borders treated as closed, only Georgia and Iran remain.

## Goals / Non-Goals

The goals are:

- Record which countries supply, carry and receive gas on each pipeline, from sources.
- Record which land borders are closed or restricted to regular traffic, with dates and sources.
- Give consumers a tested recipe for sea-access gateways over crossable borders.
- Document how to measure bilateral and in-bloc trade dependence with external data.

The non-goals are:

- **Trade data.** No trade values, shares, balances or product flows are stored, and no external trade dataset is mirrored.
- **Flows and capacity.** No transit volumes, port throughput, route capacity, cost or travel time.
- **Other infrastructure in this change.** Roles on oil pipelines or transport corridors, maritime chokepoints, air and sea connectivity.
- **Political judgement.** No ruling on sanctions, embargoes, or the legitimacy of a border or a closure.
- **Scores.** No composite transit, dependence or influence score, and no ranking.
- **Countries schema.** No new field on country records.

## Decisions

### Decision 1: Function goes in `includes[].role`, not in `status`

`status` says how a country relates to the record (member, observer, participant). On a pipeline, every country with a segment is a participant in the same sense. What differs is its function along the route, so that belongs in a separate field. `role` already exists in the Arrow schema and in `clean.py`; this change declares it and gives it a catalog, `data/schemas/include_roles.yaml`:

| Role | Meaning |
|---|---|
| `origin` | The route starts here: gas enters the pipeline in this country |
| `transit` | The route crosses this country and continues into another |
| `destination` | The route ends here |

Offtake along the route is not recorded; a country that takes gas and passes the rest on is `transit`. A route that starts and ends in the same country (an export loop) is not expected among the 25 records; if one appears, it is deferred.

`role` is allowed only on records whose blocktype includes `gaspipeline` in this change. Once any country entry of a record has a role, every current country entry of that record must have one, and the record needs at least one `origin` and one `destination`. Every role assignment needs a provenance entry with `field: includes`. The role enum is open in `contract.json`.

### Decision 2: Border status is an edge dataset, not a country field

A border belongs to two countries. Storing its status on country records would duplicate every value and add a reciprocity problem. It would also put a time-varying, politically sensitive fact on the reference records that the guardrail keeps minimal. The status therefore lives in its own source file, `data/borders/border_status.yaml`, validated by `data/schemas/border_status.schema.json`:

```yaml
- countries: [ARM, TUR]        # unordered pair of iso3code values; stored sorted
  status: closed               # closed | restricted
  since: '1993'                # YYYY, YYYY-MM or YYYY-MM-DD
  until: null                  # set when the crossing reopens; the entry is kept as history
  note: >-
    Land crossings closed to regular traffic; illustrative, values set from sources at backfill.
  last_verified: '2026-11-20'
  provenance:
    - source: <government or intergovernmental source>
      url: <url>
      retrieved_at: '2026-11-20'
```

The status values are defined as follows:

- `closed`: no land crossing on that border is open to regular traffic of goods.
- `restricted`: at least one crossing is closed, or traffic is limited to named categories (for example humanitarian goods, or residents only).

Absence of an entry means that no closure is recorded. It does not mean the border is verified open, and the documentation says so.

Validation rules:

- The pair must be adjacent in `countries.borders`, in both directions.
- Entries for one pair must not overlap in time.
- `since` must not be after `until`.
- Every entry needs at least one provenance entry. Sources are a government, an intergovernmental organization, or an official border or customs authority.

The status describes whether a border can be crossed. It does not judge the legitimacy of the closure, the boundary or the states.

The dataset exports as a `border_status` table, with a primary key on (`country_a`, `country_b`, `since`) and foreign keys to `countries.iso3code`. It also gets a DuckDB view `country_borders`:

```sql
SELECT c.code AS country_code, c.iso3code, b AS neighbor_iso3, s.status AS current_status
FROM countries c, UNNEST(c.borders) AS t(b)
LEFT JOIN border_status s
  ON s.until IS NULL
 AND ((s.country_a = c.iso3code AND s.country_b = b) OR (s.country_b = c.iso3code AND s.country_a = b));
```

### Decision 3: Sea-access gateways are a recipe and a lower bound

The recipe uses the following definitions:

- **Coastal country:** an official country with `landlocked = false`. As with `landlocked` itself, a shore on the Caspian Sea does not count.
- **Crossable border:** a border whose `current_status` is not `closed`. The recipe also returns whether any edge on the path is `restricted`.
- **Gateway:** a first-hop neighbour of a landlocked country that lies on a crossable path to some coastal country. For each gateway the recipe gives the smallest number of borders to a coast. It is a recursive CTE limited to four steps, which covers every current case.
- **Outputs per landlocked country:** the gateways and their distances, the number of direct coastal gateways, and a flag for a single direct coastal gateway.

The documentation states that the result is a structural lower bound. It ignores corridors, capacity, cost and sanctions: for example, it sends Kyrgyzstan to the sea through China, while its rail freight mostly runs through Kazakhstan to Russia. Promoting the recipe to a view is an open question.

### Decision 4: Trade dependence stays downstream, with documented formulas

`docs/ai-consumers.md` documents the measures for a consumer-loaded table `trade(reporter_iso3, partner_iso3, year, exports, imports)`:

- **Partner share:** `dep(A←B)`, the share of A's trade (or of its imports, or its exports) with B.
- **Asymmetry:** `dep(A←B) / dep(B←A)`.
- **Exposure:** A–B trade divided by A's GDP.
- **Partner concentration:** the HHI over A's partner shares.
- **In-bloc leverage:** a member's share of intra-bloc imports, and the mean dependence of the other members on it.

The documentation also covers the direction of leverage:

- import dependence gives leverage to the supplier, and export dependence to the buyer;
- a surplus signals export dependence, not strength.

It lists sources and their terms: IMF IMTS (formerly DOTS), CEPII BACI (Licence Ouverte), UN Comtrade (restricted redistribution). The join pattern runs on `countries.iso3code` and `current_memberships`, and is marked untested because it needs external data.

### Decision 5: Reviewed pilots with provenance

Both backfills follow the safety model of `scripts/backfill_institutional_design.py`: an explicit manifest, a dry run by default, whole-cohort validation, conflict blocking, idempotence and provenance insertion.

- **Roles pilot:** all 25 `gaspipeline` records. Sources are operator, government or intergovernmental pages describing the route.
- **Border status pilot:** candidates are ARM–TUR, ARM–AZE, PRK–KOR, DZA–MAR, RUS–UKR, ISR–LBN and ISR–SYR. A candidate without an official source is deferred, and the manifest records the reason, as in the institutional-design pilot.

## Risks / Trade-offs

- **Political sensitivity of border status.**
  - Mitigation: neutral definitions limited to whether a crossing is open, official sources only, dates and history kept, and no judgement in notes.
  - Mitigation: the maintainer confirmed the scope on 2026-11-20 (task 0.2); every entry still goes through the reviewed pilot manifest.
- **Staleness.** Closures change, sometimes quickly.
  - Mitigation: `last_verified` on every entry, and a reported warning when an entry is older than the intblock freshness threshold.
- **Readers taking the gateway recipe as a route model.**
  - Mitigation: lower-bound wording in the documentation, and the Kyrgyzstan counter-example next to the recipe.
- **Role ambiguity on branching pipelines.**
  - Mitigation: the offtake rule (Decision 1), and deferral of records whose route the sources do not settle.
- **Users expecting trade data in the repository.**
  - Mitigation: the documentation says plainly that trade data is downstream and gives the join pattern.

## Migration Plan

The change is additive:

- `includes[].role` keeps its column and gains values.
- `border_status` and `country_borders` are new.
- The role and status enums are open.

It ships as a MINOR release with CHANGELOG notes. Before release, rollback is a revert. After release, removal follows the deprecation rule: a `deprecated` entry in `contract.json`, then removal no earlier than the next MAJOR release.

## Open Questions

1. **Scope of border status.** Resolved by the maintainer on 2026-11-20: border crossing status is in scope. It is significant reference information about the border graph and likely affects trade volumes between neighbouring countries. Decision 2 stays in this change; the guardrail against socioeconomic fields on country records is unchanged, because status lives in its own edge dataset.
2. **Other infrastructure.** Should roles later extend to transport corridors (positions on a route rather than treaty parties) and to an `oilpipeline` blocktype?
3. **Restricted borders.** Should `restricted` count as crossable in the recipe (the default proposed here), or be excluded?
4. **View.** Should the gateway recipe become a view once both pilots land?
5. **Pilot.** Is the border-closure candidate list the right pilot?

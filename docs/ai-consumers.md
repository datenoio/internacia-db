# AI consumer guide

This document is the **consumption contract** for Internacia Datasets — written for
LLM agents, enrichment pipelines, and programmatic integrators. For installation and
build instructions, see [README.md](../README.md).

## Scope

### In scope

Reference data used for entity linking, geographic classification, and organizational
membership joins:

- ISO 3166-1 identifiers and entity status metadata
- Geography (borders, continents, subregions, coordinates, centroids where present)
- Demographic reference fields (`population`, `area`, `gini`) with source/year
- World Bank-style classifications (`region`, `incomeLevel`, `lendingType`)
- Cultural reference (`languages`, `currencies`, `timezones`, `demonyms`, `flag_emoji`)
- Multilingual names and aliases (`other_names`, `common_names`, `native_names`)
- Wikidata entity links (`wikidata_id`)
- Intergovernmental organizations with membership rosters and taxonomy
- Institutional design of intblocks (`institutional_design`: mandate, decision rule, binding force,
  independent organs, enforcement, mutual defence, asymmetric vetoes) for a reviewed cohort
- Field-level provenance on country records where enriched

### Out of scope

Do **not** infer or expect these fields — they are intentionally absent:

- HDI, GDP, GDP per capita, government type, internet penetration
- Military spending, armed-forces size, or any composite power or influence score
- Vote shares, quotas, or budget contribution scales of organizations
- Bilateral trade values, shares or balances, transit volumes, and route capacity
- Time-series economic or governance indicators
- Real-time membership or political recognition status

Downstream consumers should enrich from separate datasets. See
[openspec/AGENTS.md](../openspec/AGENTS.md) (Dataset Scope).

## Datasets

| Dataset | Records | Primary key | Manifest |
|---------|--------:|-------------|----------|
| `countries` | 256 | `code` (alpha-2) | `data/datasets/countries.manifest.json` |
| `intblocks` | 1500+ | `id` | `data/datasets/intblocks.manifest.json` |
| `blocktypes` | 83 | `id` | `data/datasets/blocktypes.manifest.json` |

All three are bundled in `data/datasets/internacia.duckdb`. Prefer DuckDB or Parquet
over reading individual YAML source files under `data/countries/` and `data/intblocks/`.

**Consistency guarantee.** `scripts/check_generated_artifacts.py` compares cleaned
source content with the full JSON/YAML exports and their declared columnar/CSV
projections. It rejects changed values, duplicate primary keys, changed membership
edges, missing metadata, and incorrect schema hashes. CI rebuilds, checks that the
committed descriptors match the build and that a second build is identical, then
tests the staged build. Within a bundle, manifests,
sidecars, and DuckDB metadata share one build identity. Source-only curation
fields are deliberately absent from columnar exports; consult the generated
[data dictionary](data-dictionary.md) for field availability.

### Tabular and lite exports

For spreadsheet tools and context-constrained agents, each build also publishes:

| Artifact | Use |
|----------|-----|
| `countries.csv.zst` / `intblocks.csv.zst` | Flattened scalar columns (structs expanded to `population_value`, `hq_city`, etc.); decompress with `zstd -d` |
| `countries-lite.parquet` | ~12 columns: `code`, `name`, `iso3code`, `wikidata_id`, `entity_type`, `code_status`, `un_status`, `independent`, `region_id`, `subregion`, `ioc_code`, `fifa_code` |
| `intblocks-lite.parquet` | ~9 columns: `id`, `name`, `status`, `wikidata_id`, `geographic_scope`, `scope_category`, `blocktype`, `membership_count`, `legal_status` |
| `countries.json.zst` / `intblocks.json.zst` | Single JSON arrays (same records as JSONL), zstd-compressed |
| `datapackage.json` | Frictionless Data Package resource index |

Lite variants share primary keys with full exports — join on `code` or `id` to hydrate heavy fields.

## Versioning and stability

Every build writes a manifest with:

- `version` — semver (matches git tag on releases)
- `schema_hash` — SHA-256 of the table's canonical column list; changes whenever the declared export schema changes; inspect the migration report to assess compatibility
- `contract_version` — `MAJOR.MINOR` of the dataset version; pin the MAJOR
- `files` — `sha256` and `bytes` of each file of the dataset
- `build_date`, `git_commit`, `row_count`, `data_license`

`contract.json` describes every table (columns, logical types, nullability, keys), the
open enum values, and `min_duckdb`; `SHA256SUMS` covers every file. See
[data-contract.md](data-contract.md).

Query version from DuckDB:

```sql
SELECT dataset, version, schema_hash, build_date FROM _meta;
```

Before upgrading:

1. Compare `schema_hash` in your cached manifest vs the new release
2. Read [CHANGELOG.md](../CHANGELOG.md) for migration notes
3. Apply intblock alias remaps from `intblocks_aliases.json` if joining on intblock `id`
4. Apply country code remaps from `countries_aliases.json` if joining on country `code` (e.g. legacy `KV` → `XK`)

Dataset SemVer (what is MAJOR vs MINOR vs PATCH for this data product), alias retention,
and API posture are defined in [versioning-policy.md](versioning-policy.md).

**Stable join keys:** country `code` and intblock `id`. When an intblock id is renamed,
the old id appears in `intblocks_aliases.json`:

```python
import json

aliases = {
    a["alias"]: a["target"]
    for a in json.load(open("data/datasets/intblocks_aliases.json"))
}
resolved = aliases.get("ASF", "ASF")  # -> "FSA"
```

A `reason` of `disambiguated` means the alias string now refers to a **different**
entity (not just a rename).

A `reason` of `retired` means the ID was removed without a replacement and its
`target` is null: drop rows keyed on it instead of remapping. `TELESUR` (a
commercial operator, not an intblock) is the first such entry. The lookup above
returns `None` for it. See [retired intblock IDs](retired-intblock-ids.md) before
resolving historical IDs.

## Entity model

### Countries

256 country and territory records including 249 current ISO 3166-1 assignments plus
7 non-standard entries with explicit `code_status`. See
[country-code-policy.md](country-code-policy.md).

Key classification fields:

| Field | Use |
|-------|-----|
| `code_status` | `official_iso3166_1`, `user_assigned`, `obsolete`, `exceptionally_reserved` |
| `entity_type` | `sovereign_state`, `dependent_territory`, `disputed_territory`, etc. |
| `un_member`, `un_status`, `independent` | UN participation (`member` / `observer` / `non_member`) plus booleans |
| `recognition_status` | Optional struct for dispute/recognition metadata |

**Filter current ISO countries (249 records):**

```python
df[df["code_status"] == "official_iso3166_1"]
```

### Intblocks

Organizations, treaties, alliances, federations, and similar groupings. Each record has:

- `id` — stable uppercase identifier (join key)
- `blocktype` — list of domain taxonomy keys (e.g. `fisheries`, `trade`, `military`); the first is the primary domain. Entity form (IGO, treaty, forum, NGO) is `scope_category`, not a blocktype. `intorg` is deprecated: filter IGOs with `scope_category = 'igo'`. `eccurr` and `cuscurr` are deprecated: use `list_has_all(blocktype, ['economic', 'currency'])` or `['customs', 'currency']`. Currency union rosters are the records whose primary blocktype is `currency` (`blocktype[1] = 'currency'`). These also include dissolved unions and currency boards such as `LMU` and `EACB`, so add `status != 'historical'` to get current unions only. `currency` as a secondary value also marks organizations that administer a currency (`UEMOA`, `OECS`) and central banks such as `ECB`
- `includes` — typed membership/participation list when applicable; **`includes[].id` is authoritative** for joins
- `status`, `founded`, `dissolved`, `predecessor`, `successor` — lifecycle
- `wikidata_id`, `description`, `tags`, `topics` — linking and discovery
- `partof` — parent organization ids

Member entry shape: `{id, name, type, status, joined, left, role, note}`.
Use `id` for joins. For `type: country` entries the export sets `name` to the country's `name`; other types keep their source label.
`left` is the departure date (ISO string) when the member left.

### Membership status (`includes[].status`)

Canonical catalog: [`data/schemas/includes_status.yaml`](../data/schemas/includes_status.yaml).

| Status | Meaning |
|--------|---------|
| `member` / `founding_member` | Current (or founding) full member |
| `observer` | Observer seat |
| `associate_member` | Associate membership, as the organization's instrument names it |
| `associated` | Association that the instrument does not call membership (associated countries/nations) |
| `associate` / `associated_observer` | **Deprecated** (`contract.json` `deprecated[]`); removed in the next MAJOR. Read them as `associate_member` / `observer` until then |
| `former_member` | Left; prefer `left` date when known |
| `participant` / `partner` / `cooperating` | Non-member participation |
| `recipient` / `contributor` / `funder` | Program / funding roles |
| `represented` / `validation` / `extension` | Special coverage statuses |

### Current full membership

Use an explicit status set for full membership:

```sql
SELECT intblock_id, country_code
FROM memberships
WHERE status IN ('member', 'founding_member');
```

Partners, observers, participants, and funding relationships are broader
participation, not full membership. Include those statuses explicitly when that
is the question. No `includes` plus `membership_applicability:
not_applicable` means there is no meaningful country-level roster to join.
Historical organizations still have historical rosters; edge
status alone does not establish that an organization is currently active.

### Historical membership joins

Country and territory edges join to `countries.code`. Historical-country edges
can instead reference the explicit `historical_entities` registry in
[`countries_completeness.yaml`](../data/schemas/countries_completeness.yaml).
For example, `SU` denotes the Soviet Union and is absent from the current-country
dimension. Preserve it with a left join; never remap it to `RU`:

```sql
SELECT m.*, c.name AS current_country_name
FROM memberships m
LEFT JOIN countries c ON c.code = m.country_code;
```

A missing country row on a known historical edge is expected. Unknown historical
identifiers fail validation. Full JSON/YAML retains curation notes and applicability
markers omitted from Parquet/DuckDB; the data dictionary lists that availability.

### Intblock `scope_category`

Optional entity-kind taxonomy (`igo`, `treaty_body`, `policy_forum`,
`reference_enumeration`, `intergovernmental_body`, `non_state_organization`).
`reference_enumeration` covers named geographic/set groupings (e.g. SIDS), **not** country
attribute partitions (those live on countries — see below).
`intergovernmental_body` covers standing subsidiary commissions/offices and
multilateral funds or two-fund partnerships without independent IGO personality;
it does **not** imply a
country-member roster. `non_state_organization` covers NGOs and industry or
professional associations whose members may be organizations or individuals.
Closed-enum clients must recognize both new values; do not silently coerce them
to `igo`. For the 2026-09 scope migration, country-member rows were removed
from entities where they represented beneficiaries, donors, parent-organization
members, or member organizations' locations rather than actual membership.
`AFDF` is independently constituted (`igo`) and has 29 State Participants in
the 2025-09-30 ADF statement; it is not a regional-beneficiary set. `CIF` denotes
the two-fund partnership (`intergovernmental_body`), not its 15 dated donor
countries. `TAR` denotes an ESCAP cooperation platform (`policy_forum`) whose
28-country *geographic coverage* is not a `member` roster. Its 22-party treaty
is a **different ID**, `TARAGREEMENT` (`treaty_body`); treaty accession dates
belong there. None of CIF, TAR, or TELESUR should be joined as a list of member
states, and `includes IS NULL` in DuckDB represents absence of a country roster.
See [intblock-inclusion-policy.md](intblock-inclusion-policy.md).
How to search catalogues and improve records: [discovery.md](discovery.md).
Catalogues searched and roster authorities used to compile membership:
[intblock-sources.md](intblock-sources.md).

```sql
SELECT id, name FROM intblocks WHERE scope_category = 'igo' ORDER BY id;
```

### Intblock `institutional_design`

Optional, sourced facts about what an organization's founding instrument lets it decide and
enforce. Values are defined in
[`data/schemas/institutional_design.yaml`](../data/schemas/institutional_design.yaml). An absent
object or subfield means **unknown**, never "none"; an explicit `[none]` list means the instrument
provides none. Only a reviewed pilot cohort carries it (see
`data/schemas/institutional_design_pilot.yaml`), and every populated record has a `provenance`
entry with `field: institutional_design`.

- `mandate`: `general`, `security`, `economic`, `sectoral`, `technical`
- `decision_rule` and `decision_force`: the default rule and binding force of the principal
  decision-making organ (the organ of member-state representatives that adopts the main acts)
- `independent_organs[]`, `enforcement[]`, `mutual_defence`
- `veto_holders[]`: treaty-granted vetoes other members lack (UNSC permanent members); consensus
  bodies have none, and de-facto vetoes from voting weight are not recorded

The field never appears on `reference_enumeration` or `non_state_organization` records. Flat CSV
exports carry it as `design_*` columns. Derive an authority level, and read it next to member
capacity, with the recipes in [query-examples.md](query-examples.md#authority-and-capacity).

#### Capacity indicators are downstream

Influence needs both authority and capacity. Population is in scope (`countries.population`);
GDP, military spending and similar indicators are not shipped. Load them from an external source
(for example World Bank WDI or SIPRI) and join on `countries.iso3code`:

```sql
-- gdp(iso3 VARCHAR, year INTEGER, value DOUBLE) is a table you load yourself.
SELECT cm.intblock_id, sum(g.value) AS members_gdp
FROM current_memberships cm
JOIN countries c ON c.code = cm.country_code
JOIN gdp g ON g.iso3 = c.iso3code AND g.year = 2024
WHERE cm.intblock_id = 'EU' AND cm.status IN ('member', 'founding_member')
GROUP BY cm.intblock_id;
```

### Transit: route roles and border crossing status

Two structural layers describe transit dependence (OpenSpec change `add-transit-dependence-layer`):

- **Route roles.** `includes[].role` gives a country's function on an infrastructure route, defined
  in [`data/schemas/include_roles.yaml`](../data/schemas/include_roles.yaml). Pipelines
  (`gaspipeline`, `oilpipeline`) use `origin`, `transit` and `destination`; linear transport
  corridors (`corridor`) use `terminal` and `transit`. Roles appear only on those records, and only
  on a reviewed cohort; elsewhere `role` is NULL. The `role` column of `memberships` and
  `current_memberships` carries the same value.
- **Border crossing status.** The `border_status` table lists land borders that are `closed` (no
  crossing open to regular traffic of goods) or `restricted` (some crossings closed, or traffic
  limited to named categories), with `since`, `until` and official sources. The `country_borders`
  view joins it to `countries.borders`. A NULL status means that **no closure is recorded**, not
  that the border is verified open. The status describes whether crossings are open; it does not
  judge the legitimacy of a closure, a boundary or a state.
- **Evidence limit.** Most entries come from official travel advice, which describes crossings for
  travellers. A border marked `closed` can still carry some freight (for example rail freight), so
  for goods-traffic analysis treat `closed` as "closed to regular crossings" and check freight
  separately. Entries are corrected to `restricted` when a customs, border or transport authority
  states that goods still cross; a 2026-11-21 re-check could not read such sources (they returned
  403 or a bot check), so no entry was changed.

The sea-access gateway recipe in [query-examples.md](query-examples.md#transit-and-borders)
combines both with `landlocked`. It is a structural lower bound, not a route model.

#### Trade dependence is downstream

Trade influence is asymmetric dependence, not volume or balance. Internacia does not ship trade
values, shares, balances, transit volumes or route capacity. Load bilateral trade yourself, for
example from IMF IMTS (formerly DOTS), CEPII BACI (product level, Licence Ouverte) or UN Comtrade
(check its redistribution terms), into a table such as
`trade(reporter_iso3, partner_iso3, year, exports, imports)`, and compute:

| Measure | Definition |
|---|---|
| Partner share `dep(A←B)` | A's trade with B divided by A's total trade (or imports, or exports, separately) |
| Asymmetry | `dep(A←B) / dep(B←A)` |
| Exposure | A–B trade divided by A's GDP (from your own GDP table) |
| Partner concentration | HHI of A's partner shares |
| In-bloc leverage | A member's share of intra-bloc imports, and the mean dependence of the other members on it |

Import dependence gives leverage to the supplier; export dependence gives leverage to the buyer.
A surplus with a partner signals export dependence on that partner's market, not strength.

```sql
-- trade(reporter_iso3, partner_iso3, year, exports, imports) is a table you load yourself.
WITH t AS (
  SELECT reporter_iso3, partner_iso3, exports + imports AS total
  FROM trade WHERE year = 2024
),
shares AS (
  SELECT reporter_iso3, partner_iso3, total / sum(total) OVER (PARTITION BY reporter_iso3) AS dep
  FROM t
)
SELECT a.reporter_iso3 AS a, a.partner_iso3 AS b, a.dep AS dep_a_on_b, b.dep AS dep_b_on_a,
       a.dep / nullif(b.dep, 0) AS asymmetry
FROM shares a
JOIN shares b ON b.reporter_iso3 = a.partner_iso3 AND b.partner_iso3 = a.reporter_iso3
JOIN countries ca ON ca.iso3code = a.reporter_iso3
JOIN current_memberships m ON m.country_code = ca.code AND m.intblock_id = 'EAEU'
ORDER BY asymmetry DESC;
```

### Trade agreements registry

Every free trade agreement, customs union, partial-scope or preferential agreement and
non-reciprocal preference scheme has a row in `trade_agreements`, bilateral ones included
(OpenSpec change `add-trade-agreements-registry`). The registry is reference data: parties,
`status`, `signed` / `in_force` / `ended` dates, `wto_rta_id`, `aric_id`, `gptad_id`, `dta_id`,
links to the agreement text (`links[].type = 'treaty_text'`) and provenance. It ships no trade
values, tariff lines, preference margins, depth scores or rankings. To study the content of an
agreement, join the World Bank Deep Trade Agreements files on `dta_id` (their `WB ID` column).

- **Two-party agreements** (`USKR`, `CETA`, `EUJP`, `CHAFTA` and the ADB ARIC bilaterals) are
  only in the registry. In 5.0.0 the 34 two-party FTA intblocks left `intblocks` and
  `memberships`; `intblocks_aliases` lists them with `reason = moved` and
  `target_dataset = trade_agreements`, under the same id.
- **Agreements with three or more parties** that are signed or in force are also intblocks
  (`RCEP`, `CPTPP`, `AGADIR`): `trade_agreements.intblock_id` names the intblock, and the
  parties are read from its `includes`, so the two never disagree.
- **Investment treaties** (bilateral investment treaties, Canada's FIPAs) are rows with
  `agreement_type = 'investment'` and ids ending in `-BIT` (`AMCA-BIT`); a further treaty
  between the same parties adds its year of signature (`CARO-BIT-1996`). A treaty that an FTA
  suspended or replaced is `superseded` by that FTA (`CAPA-BIT` by `CAPA`). Plurilateral
  investment treaties keep their intblock id (`ACIA`, `OICIA`). Belgium and Luxembourg sign
  investment treaties as one party, the `BLEU` intblock, which `country_trade_agreements`
  expands with `via = 'BLEU'`. Filter on `agreement_type` when you count trade agreements
  only.
- **`verification`** is `official` when parties and dates were checked against the treaty
  text, a depositary or a party government, and `catalogue` when they come from WTO RTA-IS, the
  WTO PTA Database or ADB ARIC only. ARIC rows are catalogue-level: its index lists only ADB-member parties and
  its statuses lag, so check a catalogue record before relying on a date.
- **Preference schemes** (OpenSpec change `add-preference-scheme-rosters`) are the
  non-reciprocal GSP schemes, LDC-only schemes and programmes such as `AGOA` that the WTO
  Preferential Trade Arrangements Database lists (`wto_pta_ids`). Each party has a `role`:
  `grantor` or `beneficiary` (every other agreement has `role = 'party'`). `parent` links a
  sub-scheme to its scheme and a national scheme to the `GSP` framework: `GSP` → `EU-GSP` →
  `EU-GSP-EBA` and `GSPPLUS`. Most beneficiary lists are catalogue-level and dated: the notes
  give the PTA Database version they come from (the EU GSP list is of 2017).
- **Beneficiary history** (OpenSpec change `add-preference-scheme-beneficiary-history`) comes
  from the PTA Database versions, whose beneficiary lists start around 2011. A beneficiary has
  `in_force` when a later version first lists it, and `left` when a version drops it. Countries
  that graduated or were removed are `former_party` rows in `trade_agreement_parties`. These
  are no-later-than dates, not designation dates. A country listed since the earliest list has
  no `in_force`, and earlier spells of a returning country are in the party `note`.
- **Provisional application.** `in_force` is the definitive entry into force.
  `provisional_application` is the date an agreement began to apply provisionally; an
  agreement applied only provisionally has `status = 'in_force'` and an empty `in_force`.
  To ask since when an agreement applies, use `coalesce(provisional_application, in_force)`.
  Catalogue records may still hold a provisional date in `in_force`, because WTO RTA-IS and
  ARIC do not tell the two apart.
- **`country_trade_agreements`** gives one row per country and agreement. A bloc party (the
  EU) expands to its current members with `via = 'EU'`; the United Kingdom is therefore not a
  party to `EUKR` in this view. Coverage is current, not historical.

```sql
-- In-force agreements that link two countries, directly or through a bloc.
SELECT a.agreement_id, t.name, a.via AS via_a, b.via AS via_b
FROM country_trade_agreements a
JOIN country_trade_agreements b USING (agreement_id)
JOIN trade_agreements t ON t.id = a.agreement_id
WHERE a.country_code = 'FR' AND b.country_code = 'JP' AND t.status = 'in_force'
  AND t.agreement_type <> 'preference_scheme';
```

A `preference_scheme` row (GSP, AGOA) lists the grantors and the beneficiaries as parties;
two grantors of the same scheme are not trading partners under it, so leave schemes out of
pair queries, as above (or keep `role = 'party'`). To list who grants a country preferences:

```sql
-- Non-reciprocal preference schemes in force that Bangladesh benefits from, and their grantors.
SELECT t.id, t.name, g.party_id AS grantor, t.parent
FROM country_trade_agreements c
JOIN trade_agreements t ON t.id = c.agreement_id
JOIN trade_agreement_parties g ON g.agreement_id = t.id AND g.role = 'grantor'
WHERE c.country_code = 'BD' AND c.role = 'beneficiary' AND t.status = 'in_force'
ORDER BY t.id;
```

```sql
-- Beneficiaries a scheme lost, with the version date by which each left.
SELECT p.party_id, p."left", p.note
FROM trade_agreement_parties p
WHERE p.agreement_id = 'EU-GSP' AND p.role = 'beneficiary' AND p.status = 'former_party'
ORDER BY p."left", p.party_id;
```

- **`trade_agreement_instruments`** lists what amended or added to an agreement after
  signature: upgrade and amending protocols, CEPA Supplements, supplementary agreements,
  early harvest arrangements and Joint Committee decisions (`kind`), each with its own
  `status` and dates. The agreement's row in `trade_agreements` keeps the agreement's own
  `status` and dates: `CNPE` stays `in_force = '2010-03-01'` after its Optimization
  Protocol entered into force in 2026. Most agreements have no instruments recorded yet, so
  an empty result means none recorded, not none exist. Many Joint Committee decisions only
  update annexes; filter on `kind` when you want treaty-level upgrades.

```sql
-- Agreements upgraded by a protocol in force since 2024, latest first.
SELECT i.agreement_id, t.name, i.name AS instrument, i.in_force
FROM trade_agreement_instruments i
JOIN trade_agreements t ON t.id = i.agreement_id
WHERE i.kind = 'amending_protocol' AND i.status = 'in_force' AND i.in_force >= '2024'
ORDER BY i.in_force DESC;
```

`trade_relations` rows are agreements that grant most-favoured-nation or normal trade
relations treatment without preferences (`AMUS-TRA`; OpenSpec change
`add-investment-and-trade-relations-types`). Their ids carry the suffix `-TRA`, so the bare
pair id stays free for a trade agreement. They come from the treaty databases of the United
States (the ITA's former TARA database and Treaties in Force), Australia, Canada, the
Netherlands and Switzerland, with their status, and from the UN Treaty Series for agreements
concluded since 2000 that no national database covers (`verification: catalogue`, with
`unts_registration`; OpenSpec `add-trade-relations-walk`). Agreements the Netherlands signed
with Belgium and Luxembourg have the `BENELUX` intblock as one party. Coverage is uneven: an
agreement between two countries without a walked treaty database appears only when it was
concluded after 2000 and registered with the UN. The U.S. investment
treaties from trade.gov are `investment` rows like the Canadian ones (`ALUS-BIT`). Beyond the
United States and Canada, `investment` covers the world through the UNCTAD IIA Navigator BITs
(`verification: catalogue`, with `unctad_iia_id`; OpenSpec `add-unctad-bit-walk`). Leave both
types out when you count trade agreements per country:

```sql
SELECT country_code, count(*) AS agreements
FROM country_trade_agreements
WHERE agreement_type NOT IN ('investment', 'trade_relations', 'preference_scheme')
GROUP BY country_code ORDER BY agreements DESC;
```

### Country attribute fields (former attribute intblocks)

Driving side, scripts, DVD region, broadcast standards, legal traditions, and rail gauges
are country columns. Remap retired intblock ids with
`data/datasets/attribute_intblock_migrations.json`.

```sql
-- Was: members of RHTRAFFIC / LHTRAFFIC
SELECT code, name FROM countries WHERE car_side = 'left' ORDER BY code;

SELECT code, name, dvd_region FROM countries WHERE dvd_region = 1;

-- List-of-struct attributes: unnest and filter on id
SELECT c.code, c.name
FROM countries c, UNNEST(c.writing_directions) AS t(d)
WHERE d.id = 'rtl';

SELECT c.code, c.name, g.gauge_mm
FROM countries c, UNNEST(c.rail_gauges) AS t(g)
WHERE g.id = 'russian' AND g."primary" = true;
```

Vocab catalogs: `data/vocabs/`. Coverage is sparse for some fields (migrated from
attribute-partition intblocks). Government-form typology is vocab-only
(`government_forms.yaml`) and is **not** assigned on country records. Verified
recipes: [query-examples.md](query-examples.md).

### Country crosswalk ids

Optional join aids: `geonames_id`, `ioc_code`, `fifa_code`, `fips_code`, and `bbox`.
Coverage uses source-specific eligibility rather than all 256 records as a denominator:

- `geonames_id` covers every current official ISO 3166-1 record; non-standard records
  may lack a GeoNames entity;
- `ioc_code` and `fifa_code` apply only when the entity has a corresponding National
  Olympic Committee or FIFA Member Association;
- `fips_code` is a legacy FIPS 10-4-compatible identifier. FIPS 10-4 was withdrawn in
  2008; use it only to join legacy systems, not as a current geographic standard.

Every populated crosswalk value has field-level provenance. Source snapshots and
machine-readable null reasons are recorded in
`data/schemas/country_crosswalk_sources.yaml` and
`data/schemas/country_crosswalk_exclusions.yaml`.

```sql
SELECT code, name, ioc_code, fifa_code FROM countries
WHERE code_status = 'official_iso3166_1' AND ioc_code IS NOT NULL;
```

### OpenAI-style tool schemas

Tool definitions are generated by the internacia SDK from its own signatures, so they cannot
drift from the query layer: `internacia.tools.openai_tools(client)` returns one tool per SDK
query method plus `country_lookup` and `intblock_lookup`, with enum lists taken from the
connected data version, and `internacia.tools.call_tool()` executes the calls (SDK 0.4+).

**Deprecated:** the hand-written
[`data/schemas/country_lookup.openai.json`](../data/schemas/country_lookup.openai.json) and
[`data/schemas/intblock_lookup.openai.json`](../data/schemas/intblock_lookup.openai.json) remain
for one more MINOR release after the SDK release that ships `internacia.tools`, then they are
removed. Their parameters are not kept in sync with the data.

### Schema migration files

When a release changes JSON Schema properties, `data/datasets/migration.vX.Y.Z.json`
lists added/removed/type-changed fields per dataset. Compare against your cached
`schema_hash` before upgrading.

### Blocktypes

Taxonomy definitions for intblock categories. Join `intblocks.blocktype` values to
`blocktypes.id`.

## Field semantics (countries)

### Structured metrics

`population`, `area`, and `gini` are structs, not plain numbers:

```
{value: number, year: integer|null, source: string, source_id: string}
```

- Use `.value` for the numeric field
- `year` is `null` when the source year is unknown (never `0`)

```python
import pandas as pd

# .struct requires ArrowDtype-backed columns
df = pd.read_parquet("data/datasets/countries.parquet", dtype_backend="pyarrow")
pop = df["population"].struct.field("value")
year = df["population"].struct.field("year")

# default backend: struct columns are Python dicts
df = pd.read_parquet("data/datasets/countries.parquet")
pop = df["population"].apply(lambda v: v["value"] if v is not None else None)
```

### World Bank classifications

`region`, `adminregion`, `incomeLevel`, `lendingType` are `{id, value}` structs.
Values are the World Bank's current ids and labels (refreshed by
`scripts/enrich_countries.py refresh-classifications`). Filter on the stable `id`, not on
`value` — the Bank renames regions (in 2025 `MEA` became *Middle East, North Africa,
Afghanistan & Pakistan*). `region`/`incomeLevel`/`lendingType` are absent for 8 entities the
World Bank does not classify (overseas territories, special statistical areas, non-standard
codes); `adminregion` is absent for 119 records (those 8 plus 111 high-income economies)
because it only covers low- and middle-income economies. Do not treat missing values as data
errors. Another 31 entities the Bank does not classify carry inferred values: their provenance
source is `UN M49 inference` or `World Bank (historical classification)`, never `World Bank`.
The `wbgroup` intblocks (`HIC`, `LMC`, `SAS`, …) list exactly the economies whose
Bank-published field puts them in the group.

### Borders

`borders` is a list of **ISO 3166-1 alpha-3** land-neighbor codes (e.g. `CAN`, `MEX`),
not alpha-2. Island nations may have empty borders.

### Names and aliases

| Field | Purpose |
|-------|---------|
| `name` | World Bank-style English short name (may lag official short-form renames) |
| `official_name` | Formal long-form state name |
| `common_names` | Modern short forms and aliases for fuzzy matching |
| `other_names` | Translations `{id, name}` |
| `native_names` | Names in the entity's own `languages[]`: lang code → `{official, common}`, either may be absent (DE has only `de`) |

For entity linking, search across `name`, `common_names`, `other_names`, `native_names`, and codes.
Exonyms ("Allemagne", "Германия") are in `other_names`; `native_names` holds only endonyms.

### Provenance

Country records may include `provenance`: list of `{field, source, retrieved_at, url, license}`.
Use this to assess data freshness and attribute upstream sources. See [ATTRIBUTION.md](../ATTRIBUTION.md).

## Field semantics (intblocks)

| Field | Notes |
|-------|-------|
| `includes[].id` | Authoritative member identifier (usually country `code`) |
| `includes[].type` | Member type (`country`, `organization`, etc.) |
| `includes[].status` | Catalogued in [`includes_status.yaml`](../data/schemas/includes_status.yaml) — see table above |
| `includes[].joined` / `includes[].left` | ISO dates; `left` is exported on JSONL, Parquet, DuckDB, and `memberships` |
| `membership_count` | Declared count; compared to the country roster unless `membership_count_type` is set |
| `membership_count_type` | Unit of the count (`countries` default; `companies`, `individuals`, …) |
| `headquarters` | `{city, country, coordinates}` — optional; coverage varies |
| `legal_status`, `geographic_scope` | Optional free text / enum; `legal_status` is not a controlled vocabulary |

## Query recipes

Full catalog with verified row counts: [query-examples.md](query-examples.md).

**DuckDB struct lists:** `UNNEST(column) AS t(row)` then `row.field` (e.g.
`UNNEST(i.includes) AS t(m)` → `m.id`).

### DuckDB: UN members

```sql
SELECT code, name
FROM countries
WHERE un_member = true
ORDER BY name;
```

### DuckDB: land neighbors of Thailand

`borders` stores alpha-3 codes — join on `iso3code`, not `code`.

```sql
SELECT n.code, n.name
FROM countries th,
     UNNEST(th.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE th.code = 'TH'
ORDER BY n.name;
```

### DuckDB: organizations that include Laos

Join on `includes[].id`, not `includes[].name`.

```sql
SELECT i.id, i.name, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA' AND m.type = 'country'
ORDER BY i.name;
```

### DuckDB: org members (NATO)

```sql
SELECT i.id, i.name, m.id AS member_code, m.name AS member_label
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country';
```

### DuckDB: countries in a World Bank region

```sql
SELECT code, name, region.id AS region_id
FROM countries
WHERE region.id = 'ECS'
  AND code_status = 'official_iso3166_1';
```

### Pandas: resolve intblock alias before join

```python
import json
import pandas as pd

aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/intblocks_aliases.json"))}
blocks = pd.read_parquet("data/datasets/intblocks.parquet")
blocks["id"] = blocks["id"].map(lambda x: aliases.get(x, x))
```

## Access paths

| Method | When to use |
|--------|-------------|
| `internacia.duckdb` | SQL analytics, multi-table joins, version check via `_meta` |
| Parquet | Pandas/Polars/Arrow pipelines |
| JSONL.zst | Streaming, language-agnostic JSON consumers |
| [internacia-python](https://github.com/datenoio/internacia-python) | Typed lookups and filters; 0.2.x predates data v3 and its fuzzy search fails — see [SDK status](llm-scenarios.md#sdk-status) |
| [internacia-api](https://github.com/datenoio/internacia-api) | **In development**, self-host only — no installable release and no public hosted Internacia HTTP API |
| Source YAML | **Maintainers only** — editing and validation |

Decompress zstd: `zstd -d data/datasets/countries.jsonl.zst`

## Licensing and attribution

Internacia is part of the [Dateno](https://dateno.io) open-source project.

- **Data and documentation:** CC BY 4.0 — see [DATA_LICENSE](../DATA_LICENSE)
- **Code:** MIT — see [LICENSE](../LICENSE)
- **Upstream:** World Bank (CC BY 4.0), Wikidata (CC0), IANA tzdata (public domain),
  mledoze/countries (ODbL-1.0, `centroid` field only — see the compatibility note in ATTRIBUTION.md)
- **DOI:** [10.5281/zenodo.20706176](https://doi.org/10.5281/zenodo.20706176) (Zenodo concept DOI,
  always resolves to the latest version); machine-readable metadata in [CITATION.cff](../CITATION.cff)

When redistributing or citing, cite the DOI plus the version from the manifest, and credit
upstream sources per [ATTRIBUTION.md](../ATTRIBUTION.md).

## Common mistakes

1. **Parsing YAML sources** instead of exported datasets — slower, may miss build-time normalization
2. **Joining intblocks on `includes[].name`** — use `includes[].id`
3. **Using alpha-2 in borders joins** — borders are alpha-3; join on `iso3code`
4. **Treating missing World Bank fields as errors** — expected for territories outside WB taxonomy
5. **Assuming all 256 codes are ISO official** — filter on `code_status`
6. **Ignoring `schema_hash` on upgrade** — structured fields and types change between releases
8. **Assuming internacia-api is a hosted service** — it is self-host only; use local DuckDB or the Python SDK

## Related documentation

- [docs/agents/query.md](agents/query.md) — query and join workflow (all platforms)
- [docs/agents/zh/query.md](agents/zh/query.md) — 中文查询工作流
- [docs/query-examples.zh.md](query-examples.zh.md) — 已验证中文 DuckDB 示例
- [llms.zh.txt](../llms.zh.txt) — 中文紧凑索引
- [AGENTS.zh.md](../AGENTS.zh.md) — 中文智能体入口
- [query-examples.md](query-examples.md) — verified DuckDB and Pandas query cookbook
- [query-examples-polars.md](query-examples-polars.md) — verified Polars / Parquet query cookbook
- [query-examples-r.md](query-examples-r.md) — verified R / dplyr / Parquet query cookbook
- [query-examples-observable.md](query-examples-observable.md) — Observable Framework / Plot cookbook
- [llms.txt](../llms.txt) — compact index for LLM context windows
- [llms-full.txt](../llms-full.txt) — extended index for crawlers
- [AGENTS.md](../AGENTS.md) — root routing hub
- [README.md](../README.md) — full schema tables and build pipeline
- [country-code-policy.md](country-code-policy.md) — non-standard codes and filtering
- [enrichment.md](enrichment.md) — how profile fields are sourced (maintainers)
- [intblock-sources.md](intblock-sources.md) — intblock catalogues and roster authorities
- [discovery.md](discovery.md) — how to search and improve country / intblock records
- [versioning-policy.md](versioning-policy.md) — dataset SemVer, aliases, API posture
- [CHANGELOG.md](../CHANGELOG.md) — breaking changes and migration notes
- [data/schemas/countries.schema.json](../data/schemas/countries.schema.json) — field descriptions for countries
- [data/schemas/intblocks.schema.json](../data/schemas/intblocks.schema.json) — field descriptions for intblocks

## Migration evidence and distribution resources

Release migrations compare nested source JSON Schemas and exported Arrow contracts
against an explicitly identified previous release tag. `baseline.status` records
`available`, `partial`, or `unavailable`; `schema_changed: null` means no usable
baseline, so it does not establish compatibility. Changes include nested field
paths, array items, required fields, enums, and other constraints in
`constraints_changed`, plus a separate `exports` section for columnar contracts.

Data package resource names identify a physical table and format, such as
`countries-parquet`, `countries-csv`, or `countries-lite-parquet`; `table` retains
the logical table name. GitHub releases include every descriptor path. Partial
mirrors have their own descriptor and may place tables in subdirectories.

The retired IDs `COMMLEARN`, `ABCZNZ`, and `USAN` resolve to `COL`, `ABCANZ`, and
`UNASUR` through the alias artifact. The 3.0.0 catalogue had 1269 records after
these duplicate consolidations; the catalogue then had 1275 after adding seven
treaty records and retiring `TELESUR`. Aliases preserve joins from older releases.

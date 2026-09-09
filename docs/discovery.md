# Discovering and improving Internacia records

Three different jobs:

| Job | What you want | Where to go |
|-----|----------------|-------------|
| Look up countries, borders, or org membership **already in the dataset** | Filter by code, `id`, Wikidata, or roster | [agents/query.md](agents/query.md), [query-examples.md](query-examples.md) |
| Find **missing intblocks**, or **improve** existing country / intblock YAML | New treaties, IGOs, FTAs; roster and metadata repair | This page, then [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Change schema, blocktypes, or export shape | New fields or breaking keys | [agents/openspec-quickstart.md](agents/openspec-quickstart.md) |

This page is the second job: locating real-world organizations, treaties, and named
groupings that belong in Internacia, checking they are not duplicates, compiling
membership from an official roster, and raising the quality of records already
here. Coding agents should follow the shorter checklist in
[agents/discover.md](agents/discover.md).

Internacia records **join targets** (countries and intblocks). It does not store
treaty full text, time-series indicators, or socioeconomic country profiles.
Do not add HDI, GDP, government type, or similar fields to countries.

## Guides

| Guide | Use when |
|-------|----------|
| [intblock-sources.md](intblock-sources.md) | Which catalogues were already walked, and which roster authorities to trust |
| [intblock-inclusion-policy.md](intblock-inclusion-policy.md) | Whether a candidate belongs; `id`, directory, `scope_category` |
| [country-code-policy.md](country-code-policy.md) | Whether a new country code is allowed (join-resolution only) |
| [enrichment.md](enrichment.md) | World Bank / Wikidata refresh, `last_verified` SLA, provenance depth |
| [agents/add-intblock-example.md](agents/add-intblock-example.md) | Worked add-a-record YAML walkthrough |
| [agents/contribute.md](agents/contribute.md) | Validation, completeness, and PR checklist after a find |

## Before you search

1. Confirm the candidate is a **stable join target**: a standing IGO, an in-force
   treaty with a states-parties roster, a durable forum, or a named geographic /
   set grouping. Ad-hoc news coalitions, untitled bilateral deals, and
   socioeconomic rankings are out of scope
   ([intblock-inclusion-policy.md](intblock-inclusion-policy.md)).
2. Duplicate-check **exports** (`data/datasets/internacia.duckdb` or Parquet), then
   `data/datasets/intblocks_aliases.json`. Match on `id`, official acronym, and
   English name — not on a fuzzy Wikipedia title alone.
3. Check whether the candidate is the **constitutive instrument** of an org already
   recorded (UN Charter, WHO Constitution, EU treaties). Those stay notes on the
   parent; they are not a second intblock.
4. Prefer a **named catalogue row** over an unscoped web search. Catalogues already
   walked, and what was kept, live in [intblock-sources.md](intblock-sources.md).
   Re-walking a catalogue listed there with the same retrieval date is done —
   report 0 missing and stop unless a new chapter or notification appeared.

Duplicate check against the DuckDB export:

```sql
SELECT id, name, status, scope_category, blocktype
FROM intblocks
WHERE id = 'AGADIR'
   OR lower(name) LIKE '%agadir%';
```

Alias remaps (retired or disambiguated ids):

```sql
SELECT alias, target, reason
FROM read_json('data/datasets/intblocks_aliases.json')
WHERE alias = 'AGADIR' OR target = 'AGADIR';
```

Country lookup (do this before minting a user-assigned code):

```sql
SELECT code, name, iso3code, code_status, entity_type
FROM countries
WHERE code = 'XK' OR iso3code = 'XKX' OR lower(name) LIKE '%kosovo%';
```

Do not walk every YAML file under `data/intblocks/` or `data/countries/` unless
you are editing a specific record. If DuckDB is locked, use
`data/datasets/intblocks.parquet` / `countries.parquet`.

## Hunt patterns \{#hunt-patterns\}

Recent Internacia sessions (through 9 September 2026) produced records when they
followed a **named catalogue, a sibling-record repair, or a completeness gap**,
not an unscoped “missing IGOs in the world” search. Copy these prompts; inclusion
bars live in [intblock-inclusion-policy.md](intblock-inclusion-policy.md).

| Hunt | Prompt that works | Start from | Accept | Reject |
|------|-------------------|------------|--------|--------|
| UN multilateral treaty | `Which UNTC instruments are missing?` | [UN Treaty Collection](https://treaties.un.org/) chapter list | Named, in-force treaty with a durable parties roster distinct from an existing IGO | Constitutive acts of orgs already recorded; not-in-force instruments; commodity-era pacts; a protocol whose parties equal the parent |
| Regional trade agreement | `Which WTO RTA-IS agreements are missing?` | [WTO RTA-IS](https://rtais.wto.org/UI/publicPreDefRepByRTAType.aspx) | Named plurilaterals, ASEAN+1, bloc-to-bloc deals, named mega-deals, historical predecessors that complete a lineage | Untitled `Country A – Country B` pairs; UK continuity copies of EU EPAs; services-only EIA rows of an FTA already recorded |
| Preferential trade arrangement | `Which WTO PTA Database schemes are missing?` | [WTO PTA Database](https://ptadb.wto.org/ptaList.aspx) | Named waiver programmes (`AGOA`, `CBERA`, `CARIBCAN`); named GSP **arrangements** whose roster is not `LDC` (`GSPPLUS`) | National GSP ID cards; LDC-only DFQF schemes; untitled one-country preferences |
| Plurilateral investment treaty | `Which UNCTAD IIA Navigator groupings are missing?` | [UNCTAD IIA by country grouping](https://investmentpolicy.unctad.org/international-investment-agreements/by-country-grouping) | Named plurilateral MITs whose ratifiers are not the parent IGO (`OICIA`, `ACIA`, `CJKIA`) | Bilateral BITs; FTA investment chapters of a record already present; not-in-force protocols; TIFAs |
| Standing IGO | `Which Wikipedia .int organizations are missing?` | [`.int` organizations list](https://en.wikipedia.org/wiki/List_of_organizations_with_.int_domain_names) | Standing IGOs compiled from each org’s **official** membership page | Dissolved or non-IGO `.int` holders; organs whose membership is identical to a parent already recorded |
| Geographic / set grouping | `Which UN M49 or named regions are missing?` | [UNSD M49](https://unstats.un.org/unsd/methodology/m49/) | Named regions used as join targets (`scope_category: reference_enumeration`) | Attribute partitions (driving side, scripts, DVD region — those are country fields); ad-hoc news coalitions |
| Single-record repair | `Update metadata for data/intblocks/{category}/{ID}.yaml` | Official membership page + a sibling YAML in the same directory | Sourced `includes`, ≥4 `provenance` entries, stamped `last_verified` | Invented membership; Wikipedia as the roster source of truth |
| Country enrichment | `Enrich / fix country {CODE}` | `python scripts/enrich_countries.py check` then official WB / Wikidata / IANA | Structs with `year`/`source`, borders as alpha-3, provenance | New socioeconomic fields; a new country code with no intblock that needs it |

Do more of: bounded catalogue walks, official-roster repairs on existing YAML,
completeness gaps (`includes`, `wikidata_id`, `provenance`, `last_verified`).
Do less of: Google for “international organizations not in the dataset”,
importing a catalogue wholesale, repeating a hunt already logged in
[intblock-sources.md](intblock-sources.md) for the same retrieval date.

A hunt that finds **0 missing** records is complete — report that and stop.
Agent recipes: [agents/discover.md](agents/discover.md).

## How to walk a catalogue

1. Scope to **one** catalogue (or one UNTC chapter, one RTA type, one `.int`
   slice). Unscoped queries produce more noise than this repository can review.
2. For each named, in-force instrument or standing body, duplicate-check `id`,
   name, and aliases as above. Constitutive texts of a parent IGO stay off the
   list.
3. Apply the inclusion bar for that catalogue
   ([intblock-inclusion-policy.md](intblock-inclusion-policy.md) has RTA, PTA,
   and IIA tables). When unsure, skip rather than invent an `id`.
4. Compile `includes` from the **official roster or treaty status page**, not
   from the catalogue index card. WTO and UNCTAD warn that accessions and
   withdrawals are under-notified; signatories are not the same as ratifiers.
5. Stamp `last_verified` (today’s `YYYY-MM-DD`) and at least four `provenance`
   entries (catalogue + roster authority + any Wikidata / official site fields).
   Hand off YAML authoring to [agents/contribute.md](agents/contribute.md).

Worked add walkthrough: [agents/add-intblock-example.md](agents/add-intblock-example.md).
Roster authorities by kind: [intblock-sources.md](intblock-sources.md#roster-authorities).

**Wikidata** and **English Wikipedia** are for entity linking (`wikidata_id`) and
names, not for membership when an official roster exists.

## Improving existing intblocks \{#improve-intblocks\}

Most Internacia edit sessions are **one-file repairs**, not new ids. Typical
prompt: `Update record metadata for data/intblocks/{category}/{ID}.yaml`.

Work the record in this order:

1. **Roster first.** Fetch the official membership / states-parties page. Diff
   `includes[].id` against that list. Common repairs: drop dependent territories
   that are not parties; add missing parties (`CK`, `NU`, `PS`, `EU` where the
   treaty allows); move leavers to `former_member` with `left`; quote `'NO'` for
   Norway.
2. **Sibling pattern.** Open one recently enriched YAML in the same directory
   (same `blocktype`) and match field shape: `scope_category`, `founded` /
   `dissolved`, `headquarters`, `languages`, `partof`, `topics`, `links`.
3. **Identity.** Confirm `wikidata_id` is unique (or listed in
   `references.wikidata_duplicate_allowlist`). Replace templated descriptions
   (`"international organization focused on…"`) with a sourced sentence.
4. **Lineage.** If `predecessor` / `successor` / `suborganizations` point at
   another record, add the inverse (`successor` ↔ `predecessor`, parent
   `suborganizations` ↔ child `partof`).
5. **Provenance and SLA.** Append `{field, source, retrieved_at}` entries until
   there are at least four. Set `last_verified` to the roster-check date
   (12-month advisory SLA; `STALE_LAST_VERIFIED` warns).
6. **Validate.** `python scripts/validate_intblocks.py --json` — fix every
   `errors[]` item; warnings such as `INSUFFICIENT_PROVENANCE` are worth clearing
   while you are in the file.

Bulk Wikidata backfill (descriptions, `other_names`, `wikidata_id`,
headquarters, founded) is `python scripts/enrich_intblocks.py enrich` — see
[enrichment.md](enrichment.md). That script does **not** compile membership;
rosters stay manual.

Completeness priorities (`data/schemas/intblocks_completeness.yaml`): high
`includes`; medium `wikidata_id` and a non-templated `description`; low
`languages`, `headquarters`, `regions`, `other_names`, `provenance`, `links`.

Find records that still need a roster or a freshness pass (12-month SLA). Empty
`includes` in exports may be intentional (`membership_applicability: not_applicable`
in YAML) or a real gap — check the source file before filling:

```sql
SELECT id, name, last_verified,
       len(includes) AS n_includes,
       len(provenance) AS n_provenance
FROM intblocks
WHERE last_verified IS NULL
   OR last_verified < '2025-09-09'
   OR len(includes) = 0
ORDER BY last_verified NULLS FIRST, id
LIMIT 40;
```

## Improving country records \{#improve-countries\}

The countries dataset is a **closed reference list** (256 records, 249 current
ISO). Improvement is enrichment and repair, not a hunt for new states.

| Do | Do not |
|----|--------|
| Refresh `population` / `area` / `gini` / World Bank classifications via `python scripts/enrich_countries.py enrich` | Add HDI, GDP, government type, internet penetration, or similar profile fields |
| Fix `borders` to alpha-3 `iso3code` values and keep lists reciprocal (allowlist in `countries_completeness.yaml`) | Treat missing World Bank `region` / `incomeLevel` on 8 unclassified entities, or missing `adminregion` on high-income economies, as errors |
| Repair swapped `capital_city` coordinates (`CAPITAL_FAR_FROM_CENTROID`) | Use `year: 0` when a year is unknown — use `year: null` |
| Add `provenance` on every enriched field (minimum four entries per record) | Mint a new alpha-2 because a territory exists in the news. User-assigned codes exist **only** when an intblock needs a join target ([country-code-policy.md](country-code-policy.md#disputed-territory-inclusion-rule)) |
| Keep `name` in World Bank short-name style; put modern short forms in `common_names` | “Correct” display names to journalist-style labels without a sourced update |

Maintainer commands: [enrichment.md](enrichment.md). Quality analyzer:

```bash
python scripts/enrich_countries.py check          # stale provenance, missing targets
python scripts/validate_countries.py --json
python scripts/builder.py analyze-quality         # CRITICAL/IMPORTANT fail CI
```

Attribute partitions (driving side, scripts, DVD region, broadcast/legal
systems, rail gauges) are **country fields**, not intblocks. Remap retired ids
with `data/datasets/attribute_intblock_migrations.json`.

## After a find

1. Choose `id` (uppercase official acronym), directory / primary `blocktype`,
   and `scope_category`. Filename stem must match `id`.
2. Write YAML following [agents/contribute.md](agents/contribute.md). Do not
   invent `includes`. If membership is intentionally absent, set
   `membership_applicability: not_applicable`.
3. Validate (`validate_intblocks.py --json`, `validate_countries.py --json`,
   `pytest tests/`). Do not hand-edit `data/datasets/`.
4. Cite the official roster in the PR description. Add a `[Unreleased]` line in
   `CHANGELOG.md` for new intblocks or consumer-visible repairs.
5. If the catalogue walk is new, append a row to
   [intblock-sources.md](intblock-sources.md) (catalogue, URL, retrieved date,
   what was searched, what was kept).

## Conduct

- Public treaty status pages, official membership lists, and catalogue indexes
  only. Respect `robots.txt` and site terms.
- Space out requests; do not scrape UNTC or WTO as a bulk dump into YAML.
- Do not collect personal data or non-public documents.
- Do not write internet-wide scanners in this repository. Named catalogues,
  official org sites, and targeted duplicate-checks are enough.

## Related

- [agents/discover.md](agents/discover.md) — agent checklist
- [intblock-sources.md](intblock-sources.md) — catalogues searched and roster authorities
- [intblock-inclusion-policy.md](intblock-inclusion-policy.md) — what belongs
- [agents/contribute.md](agents/contribute.md) — write YAML after a find
- [agents/add-intblock-example.md](agents/add-intblock-example.md) — worked add
- [enrichment.md](enrichment.md) — country and Wikidata refresh
- [country-code-policy.md](country-code-policy.md) — when a new country code is allowed
- [ATTRIBUTION.md](../ATTRIBUTION.md) — upstream licenses

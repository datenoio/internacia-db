# When to use Internacia

Use this repository when you need **stable reference data** for:

- **ISO 3166-1 identifiers** (alpha-2 / alpha-3 / numeric) and entity status (`code_status`)
- **Borders** (neighbors stored as ISO alpha-3 codes)
- **International organization / treaty membership rosters** (“intblocks”), including reliable **join keys**
- **Trade and investment agreements** (FTAs, customs unions, preference schemes, BITs): parties,
  status and dates in the trade agreements registry (`trade_agreements`, `country_trade_agreements`)
- **Entity linking** (multilingual names/aliases + Wikidata IDs)
- **Transit structure**: route roles on pipelines and corridors (`includes[].role`) and closed or
  restricted land borders (`border_status`, `country_borders`)
- **Institutional design** of organizations (`institutional_design`: decision rule, binding force,
  enforcement, vetoes) for a reviewed cohort, to tell binding institutions from forums and technical bodies

Do **not** use Internacia for socioeconomic or time-series analytics:

- HDI, GDP, government type, internet penetration
- military spending, armed-forces size, composite power or influence scores
- bilateral trade values, shares or balances, transit volumes, route capacity
- governance scores, macro time-series indicators

If your task needs those, enrich with a separate dataset and treat Internacia as a join-key hub.

## Quick decision guide (LLM-friendly)

1. “Find a country by ISO code / Wikidata ID”  
   Use Internacia: lookups are deterministic and include remaps + aliases.

2. “List members of NATO / EU / UN”  
   Use Internacia: query `memberships` (DuckDB) and filter on `status` for current members.
   `client.intblocks.get_by_member(...)` also returns former memberships unless you pass `current_only=True`.

3. “Neighbors of Germany / land border lookup”  
   Use Internacia: `countries.borders` stores ISO alpha-3 neighbor codes; join on `countries.iso3code`.

4. “Fuzzy match messy names (multilingual)”  
   Use Internacia names in DuckDB ([SQL recipe](llm-scenarios.md#6-fuzzy-match-messy-names-multilingual)).
   `client.search.fuzzy(...)` in SDK 0.5.0 needs `check_contract=False` on current data.

5. “Time-varying facts (GDP by year, HDI series, etc.)”  
   Internacia is not an indicator time-series dataset. **Membership history is in scope:**
   `includes[].joined` / `includes[].left` and the `memberships` table record when a
   country joined or left an organization. Use those for former-member questions; do
   not expect annual GDP or governance scores.

## Gotchas to bake into generated code

- Intblock membership joins use `includes[].id` (authoritative). `includes[].name` is just a label.
- `borders` uses ISO alpha-3 codes (`iso3code`), not alpha-2 (`code`).
- If you join across releases, prefer stable IDs and apply alias remaps:
  - `data/datasets/intblocks_aliases.json`
  - `data/datasets/countries_aliases.json`

## Canonical entry points

DuckDB (works on every current release; download `internacia.duckdb` from the
[latest GitHub Release](https://github.com/datenoio/internacia-db/releases/latest)):

```sql
SELECT code, iso3code, name FROM countries WHERE code = 'US';

SELECT i.id, i.name, m.status, m.joined
FROM memberships m
JOIN intblocks i ON i.id = m.intblock_id
WHERE m.country_code = 'US'
  AND m.status IN ('member', 'founding_member')
ORDER BY i.id;
```

Python SDK: `internacia` 0.5.0 on PyPI reads data contracts 3.x and 4.x, not the current 5.x. Without `db_path` it downloads the newest 4.x release,
and it refuses a 5.x database with `ContractError` — see
[SDK status](llm-scenarios.md#sdk-status). With a downloaded DuckDB file and the
contract check turned off, the basic lookups work:

```python
from pathlib import Path
from internacia import InternaciaClient

client = InternaciaClient(db_path=Path("internacia.duckdb"), check_contract=False)
country = client.countries.get_by_code("US")
```


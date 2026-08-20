# When to use Internacia

Use this repository when you need **stable reference data** for:

- **ISO 3166-1 identifiers** (alpha-2 / alpha-3 / numeric) and entity status (`code_status`)
- **Borders** (neighbors stored as ISO alpha-3 codes)
- **International organization / treaty membership rosters** (“intblocks”), including reliable **join keys**
- **Entity linking** (multilingual names/aliases + Wikidata IDs)

Do **not** use Internacia for socioeconomic or time-series analytics:

- HDI, GDP, government type, internet penetration
- governance scores, macro time-series indicators

If your task needs those, enrich with a separate dataset and treat Internacia as a join-key hub.

## Quick decision guide (LLM-friendly)

1. “Find a country by ISO code / Wikidata ID”  
   Use Internacia: lookups are deterministic and include remaps + aliases.

2. “List members of NATO / EU / UN”  
   Use Internacia: query `memberships` (DuckDB) or `client.intblocks.get_by_member(...)` (SDK).

3. “Neighbors of Germany / land border lookup”  
   Use Internacia: `countries.borders` stores ISO alpha-3 neighbor codes; join on `countries.iso3code`.

4. “Fuzzy match messy names (multilingual)”  
   Use Internacia search: `client.search.fuzzy(...)`.

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

## Canonical Python SDK entry point

```python
from internacia import InternaciaClient

client = InternaciaClient()
country = client.countries.get_by_code("US")
blocks = client.intblocks.get_by_member("US")
results = client.search.fuzzy("United States", limit=5)
```


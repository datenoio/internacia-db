---
description: Find missing intblocks or improve an existing country/intblock record.
---
<!-- AGENT:START -->
**Goal:** Locate a real-world organization, treaty, or named grouping that belongs
in Internacia, or raise the quality of one existing YAML record, without inventing
membership or importing a catalogue wholesale.

**Read first:** [docs/agents/discover.md](../../docs/agents/discover.md), then
[docs/discovery.md](../../docs/discovery.md) (hunt-pattern table).

**Guardrails**
- Duplicate-check DuckDB / Parquet and `data/datasets/intblocks_aliases.json` before adding an `id`.
- Do not import UNTC, WTO RTA-IS, WTO PTA, UNCTAD IIA, or Wikipedia `.int` wholesale.
- Compile `includes` from the official roster, not from a catalogue index card.
- Constitutive instruments of an org already recorded stay off the intblock list.
- Do not add HDI, GDP, government type, or similar fields to countries.
- New country codes only when an intblock needs a join target.
- Do not hand-edit `data/datasets/`.

**Steps**
1. Identify the hunt type (catalogue walk, single-record repair, or country enrichment) in [docs/agents/discover.md](../../docs/agents/discover.md#hunt-types).
2. If the catalogue is already listed in [docs/intblock-sources.md](../../docs/intblock-sources.md) for the same retrieval date, report 0 missing and stop.
3. Duplicate-check exports:

```sql
SELECT id, name, status FROM intblocks
WHERE id = 'CANDIDATE' OR lower(name) LIKE '%candidate%';
```

4. Apply [docs/intblock-inclusion-policy.md](../../docs/intblock-inclusion-policy.md). Skip when unsure.
5. Compile membership from the official roster. Stamp `last_verified` and at least four `provenance` entries.
6. Write or edit YAML following [docs/agents/contribute.md](../../docs/agents/contribute.md). New records: [docs/agents/add-intblock-example.md](../../docs/agents/add-intblock-example.md).
7. Validate:

```bash
python scripts/validate_intblocks.py --json
python scripts/validate_countries.py --json
```

8. If the catalogue walk is new, append a row to [docs/intblock-sources.md](../../docs/intblock-sources.md). Update `CHANGELOG.md` under `[Unreleased]`.

**Reference**
- Roster authorities: [docs/intblock-sources.md](../../docs/intblock-sources.md)
- Country codes: [docs/country-code-policy.md](../../docs/country-code-policy.md)
- Enrichment: [docs/enrichment.md](../../docs/enrichment.md)
<!-- AGENT:END -->

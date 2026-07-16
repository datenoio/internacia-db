# Change: Deepen intblock profile metadata and add freshness tracking

## Why
Intblock records are broad but shallow: `headquarters` is missing on 53.7% (575/1071), `founded` on 26.3% (282), and `wikidata_id` on 21.8% (233, concentrated in `intorg/`, `energy/`, `fta/`, `wbgroup/`). Freshness is untracked — only 1 of 1,071 records carries `last_verified` — so consumers cannot tell how current a record is.

## What Changes
- Extend `scripts/enrich_intblocks.py` to backfill `headquarters` (`city`, `country`, `coordinates`) and `founded` (Wikidata inception `P571`) for records that already have a `wikidata_id`, writing a `provenance` entry for each filled field.
- Run a `wikidata_id` backfill pass for records missing it, reusing the existing high-confidence matching rule (exact name/acronym match only; ambiguous matches left unset).
- Introduce a `last_verified` policy: enrichment runs and manual verification stamp `last_verified` (ISO 8601 date) on touched records, and validation reports `last_verified` coverage against a configurable threshold in `intblocks_completeness.yaml` (warn mode).

## Impact
- Affected specs: intblocks-data-quality
- Affected code: `scripts/enrich_intblocks.py`, `internacia_builder/validate/intblocks.py`, `data/schemas/intblocks_completeness.yaml`, `data/schemas/intblocks.schema.json` (declare `last_verified` if not present), `data/intblocks/**/*.yaml`

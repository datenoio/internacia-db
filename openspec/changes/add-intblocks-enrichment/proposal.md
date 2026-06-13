# Change: Add intblocks enrichment (wikidata, descriptions, multilingual)

## Why

Intblocks weaken Dateno's entity-linking and search recall: 418/1057 records lack
`wikidata_id`, 455 carry templated descriptions ("International entity focused on…"), and
multilingual coverage (`other_names`, `acronyms`) is sparse. No intblock record has any provenance.
This implements strategy tracks B1–B3.

See [docs/strategy-and-user-needs.md](../../../docs/strategy-and-user-needs.md) §4.5 / Tracks B1–B3.

## What Changes

- Add **field-level provenance** support to intblock records (mirroring countries): optional
  `provenance` list, validated and exported to all formats.
- Add **`scripts/enrich_intblocks.py`** (Typer CLI) that, from Wikidata:
  - **B1** backfills `wikidata_id` for records missing it, using only high-confidence matches
    (existing wikidata link, or normalized exact name/acronym match against search results).
  - **B2** replaces templated descriptions with the entity's Wikidata description.
  - **B3** backfills multilingual `other_names` (UN languages) and acronym aliases.
  - Records `provenance` on every enriched field; supports `--dry-run`, `--force`, `--limit`, `--id`.
- Add **quality checks** to `validate_intblocks.py`: a templated-description rate gate and an
  alias/translation coverage metric, configured in `intblocks_completeness.yaml` (warn-first).
- Ratchet the `wikidata_id` completeness threshold down after backfill.

## Impact

- Affected specs: `intblocks-data-quality` (added)
- Affected code: `scripts/enrich_intblocks.py` (new), `scripts/builder.py` (intblocks schema +
  clean_data provenance), `scripts/validate_intblocks.py`, `data/schemas/intblocks.schema.json`,
  `data/schemas/intblocks_completeness.yaml`, `data/intblocks/**`, tests, README/CHANGELOG
- Breaking: None (additive fields and warn-first gates; enriched content only)

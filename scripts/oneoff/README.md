# One-off scripts

Migrations that were run once and are kept for reference. They are not part of the build,
CI or release pipeline and may not work on the current data model; read the code before
running one.

| Script | Purpose | Used for |
|---|---|---|
| `apply_manus_roadmap.py` | Topics, directory moves and centroids from the 2026-06-15 roadmap | 1.x |
| `annotate_entity_status.py` | Set `entity_type` and `code_status` on countries | 1.x |
| `invert_attribute_intblocks.py` | Turn attribute-partition intblocks into country fields and write `data/attribute_intblock_migrations.yaml` | 2.0.0 |
| `label_scope_category.py` | Suggest `scope_category` values; does not write YAML | 2.x |
| `import_sice.py` | Write hand-checked `data/trade_agreements/` records from OAS SICE snapshots (agreements table, agreement pages, Trade Policy Developments) | 5.x |
| `parse_aric_pages.py`, `import_aric_ftas.py` | Parse a snapshot of ADB ARIC FTA pages and write catalogue-level `data/trade_agreements/` records | 5.0.0 |
| `import_wto_rtais.py` | Walk the WTO RTA-IS XLSX export into `data/trade_agreements/` | 5.0.0 |
| `fetch_gptad.py`, `import_gptad.py` | Save the World Bank GPTAD library and agreement pages; write `gptad_id` and `treaty_text` links to mapped `data/trade_agreements/` records | 5.1.0 |
| `import_dta.py` | Map World Bank Deep Trade Agreements ids (`WB ID`) to `data/trade_agreements/` records as `dta_id` | 5.1.0 |
| `apply_efta_ftn.py` | Apply the EFTA free trade network review (statuses, per-state entry-into-force dates, EFTA provenance) to `data/trade_agreements/` | 5.x |

Maintained tools stay in `scripts/` (see the README's script table).

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
| `match_desta.py`, `import_desta.py` | Match the DESTA list of treaties to `data/trade_agreements/` (report in `docs/history/`) and add missing agreements whose status and dates come from ALADI, a party government or the WTO | 5.1.0 |
| `fetch_aladi.py`, `import_aladi.py` | Save ALADI's agreement records and add the partial-scope agreements missing from `data/trade_agreements/`: current ones, and historical ones with the successor and end date from the ALADI Secretariat's note | 5.1.0 |
| `parse_aric_pages.py`, `import_aric_ftas.py` | Parse a snapshot of ADB ARIC FTA pages and write catalogue-level `data/trade_agreements/` records | 5.0.0 |
| `import_wto_rtais.py` | Walk the WTO RTA-IS XLSX export into `data/trade_agreements/` | 5.0.0 |
| `fetch_gptad.py`, `import_gptad.py` | Save the World Bank GPTAD library and agreement pages; write `gptad_id` and `treaty_text` links to mapped `data/trade_agreements/` records | 5.1.0 |
| `import_dta.py` | Map World Bank Deep Trade Agreements ids (`WB ID`) to `data/trade_agreements/` records as `dta_id` | 5.1.0 |
| `import_mofcom_fta.py` | Add China FTA Network (MOFCOM) agreements, upgrade protocols, early harvest arrangements and links to `data/trade_agreements/` | 5.x |
| `apply_efta_ftn.py` | Apply the EFTA free trade network review (statuses, per-state entry-into-force dates, EFTA provenance) to `data/trade_agreements/` | 5.x |
| `apply_uae_cepa.py` | Apply the UAE CEPA programme walk (UAE Ministry of Foreign Trade, WAM and partner governments) to `data/trade_agreements/`: new CEPAs, statuses, dates and official provenance | 5.x |
| `import_china_africa_frameworks.py` | Add the China–Africa framework agreements on economic partnership for shared development named in MOFCOM releases, MFA bilateral relations pages and Cameroonian state media | 5.x |
| `import_trade_agreement_instruments.py` | Fill `instruments` on registry records from the MOFCOM notes and the WTO RTA-IS `RTA Changes` sheet | 5.x |
| `parse_unctad_pages.py`, `import_unctad_bits.py` | Parse Wayback captures of the UNCTAD IIA Navigator economy pages and write catalogue-level `investment` records with `unctad_iia_id` | 5.x |
| `fetch_edit.py`, `import_edit.py`, `write_edit_report.py` | Save the EDIT treaty list (metadata), match it to `data/trade_agreements/`, add `treaty_text` links, date notes and missing investment treaties, and write the match report and CSVs | 5.x |
| `parse_untc_details.py`, `import_trade_relations.py` | Parse UN Treaty Collection detail pages and import `trade_relations` records from them and from national treaty database walks (Australia, Canada, Netherlands, Switzerland) | 5.x |
| `import_africa_agreements.py` | Apply the African trade agreements walk: AfCFTA and TFTA per-State dates on their intblock rosters (AU status list, SADC Secretariat), the AfCFTA protocols as instruments, the AGOA extensions of 2026, and the bilaterals tralac names that a party government or the WTO dates | 5.x |
| `import_us_tifas.py` | Write the hand-checked U.S. trade and investment framework agreements (USTR TIFA page and texts, State Department Treaties in Force 2026) to `data/trade_agreements/` as `framework` records | 5.x |

Maintained tools stay in `scripts/` (see the README's script table).

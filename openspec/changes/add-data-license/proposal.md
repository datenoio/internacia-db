# Change: Add explicit dataset license and attribution

## Why

The repository ships an **MIT `LICENSE`**, which governs *software* and does not clearly grant
rights to reuse or redistribute the **datasets**. Adopters (including downstream redistribution by
the Dateno search engine) cannot determine whether commercial use is permitted or how to attribute.
Enriched fields derive from **World Bank** (CC-BY-4.0) and **Wikidata** (CC0), which carry their own
obligations that the project must surface.

See [docs/strategy-and-user-needs.md](../../../docs/strategy-and-user-needs.md) §4.1 / Track A1.

## What Changes

- Add an explicit **data license** for the compiled datasets in `data/datasets/` (recommended:
  **CC-BY-4.0**; alternative **CC0-1.0** for maximum reuse) via a `DATA_LICENSE` file, keeping MIT
  for code.
- Add `ATTRIBUTION.md` documenting upstream sources (World Bank CC-BY-4.0, Wikidata CC0, IANA tzdata)
  and a recommended citation.
- Record the data license as **machine-readable metadata** in `countries.manifest.json` and
  `intblocks.manifest.json` (SPDX identifier).
- Add a README "License" section distinguishing code (MIT) from data (data license) and linking
  attribution guidance.

## Impact

- Affected specs: `data-licensing` (new)
- Affected code: `DATA_LICENSE`, `ATTRIBUTION.md`, `README.md`, `scripts/builder.py` (manifest fields)
- Breaking: None (clarifies and broadens reuse rights; no schema change to records)

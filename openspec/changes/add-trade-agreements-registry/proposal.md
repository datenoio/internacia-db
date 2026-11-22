# Change: Add a trade agreements registry

## Why

Internacia keeps trade agreements only as intblocks, and the inclusion policy skips bilateral agreements. The result is neither a group list nor a complete registry. 34 of the 87 `fta`, `pta` and `customs` records have exactly two parties (`USKR`, `EUJP`, `CHAFTA`, `CNEC` and others), while about 190 of the 227 agreements in force in the ADB ARIC database are missing, nearly all of them bilateral. A two-party agreement is a link between two countries, not a country group. It does not fit `memberships`, and leaving it out makes it impossible to compare how countries are connected by trade agreements.

The maintainer decided on 2026-11-22 to collect every free trade and preferential trade agreement in the world, bilateral ones included, in a separate entity. A registry of agreements, parties, status and dates is reference data. It is not an indicator used to rank countries: no trade values, tariff lines or depth scores are stored. This follows the existing rule that Internacia does not ship trade values, shares or balances (`transit-routes`).

## What Changes

- **New dataset `trade_agreements`.** Source files go in `data/trade_agreements/<ID>.yaml`, one per agreement, validated by `data/schemas/trade_agreements.schema.json`. Each record has an `agreement_type` (`fta`, `customs_union`, `pta`, `services`, `digital`, `framework`, `other`), a `status` (`proposed`, `negotiating`, `signed`, `in_force`, `terminated`, `abandoned`, `superseded`), dates, parties, catalogue identifiers (`wto_rta_id`, `aric_id`), `verification` (`official` or `catalogue`), `last_verified` and provenance.
- **Agreements with three or more parties stay intblocks.** Their registry record links to the intblock with `intblock: <id>`. Parties are read from the intblock's `includes` and are not stored twice. Agreements with exactly two parties (a country or a bloc that signs as one party, such as the EU) are stored only in the registry.
- **Exports.** New `trade_agreements` and `trade_agreement_parties` tables, and a `country_trade_agreements` view that expands bloc parties to their member countries. All three are in Parquet, JSONL, DuckDB, `contract.json` and `datapackage.json`.
- **Move the 34 two-party intblocks** (`ANZCERTA`, `AUINDIA`, `AUUAE`, `AUUK`, `CETA`, `CHAFTA`, `CNEC`, `CNKR`, `CNNI`, `CNRS`, `EUCENTRALAFRICAEPA`, `EUJP`, `EUKR`, `EUNZ`, `EUSG`, `EUUA`, `EUUK`, `EUVN`, `INUAE`, `UKIN`, `UKJP`, `UKNZ`, and 12 `US*` FTAs) to the registry, keeping their ids. `USCR` is the US–Costa Rica part of CAFTA-DR, not a separate agreement, so it merges into `CAFTADR`. They are recorded in `intblocks_aliases` with the new reason `moved` and `target_dataset: trade_agreements`. **BREAKING** for consumers who read these ids from `intblocks` or `memberships`. See the migration options in `design.md`.
- **Link the multilateral trade intblocks** (`RCEP`, `CPTPP`, `AFTA`, the ASEAN+1 FTAs, `SAFTA`, `APTA`, `GSTP` and others) to new registry records.
- **Import the ADB ARIC catalogue** (433 rows, snapshot 2026-11-22). Every row becomes a registry record, or is mapped to an existing one, with `aric_id`. Rows with three or more parties that are signed or in force also become intblocks once their rosters are sourced from official texts.
- **Policy.** `docs/intblock-inclusion-policy.md` and `docs/intblock-sources.md` are rewritten: bilateral agreements belong in the registry, and the intblock bar for multilateral agreements stays as it is.
- **Not in scope.** Trade flows, tariff schedules, depth or coverage indices, rankings, and agreement text.

## Impact

- Affected specs: new `trade-agreements` capability.
- Affected source: new `data/trade_agreements/`, `data/schemas/trade_agreements.schema.json`; `data/intblocks/fta/` (34 files moved); `data/intblocks_aliases.yaml` (34 `moved` entries).
- Affected code: `internacia_builder/build.py`, `schemas.py`, `export.py`, `contract.py`, `validate/` (new rules), `scripts/validate_trade_agreements.py`, a one-off ARIC import script under `scripts/oneoff/`.
- Affected exports: three new resources; `intblocks` and `memberships` lose 34 records; `intblocks_aliases` gains a `target_dataset` column and the `moved` reason.
- Affected documentation: inclusion policy, sources log, data contract, query examples, AI-consumer guide, agent shims, current counts, `CHANGELOG.md`.
- Versioning: the new tables are a MINOR change. Removing 34 intblock ids is consumer-affecting, so the release is MINOR with a deprecation step, or MAJOR (see `design.md`, decision 5).
- Related: the Tier 1 multilateral records found in the ARIC walk (`TPSOIC`, `D8PTA`, `ECOTA`, `MSGTA`, `KRCENTRALAMERICA`) are added as intblocks under the current policy, in a separate change before this one.

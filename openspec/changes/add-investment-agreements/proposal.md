# Change: Add investment agreements to the trade agreements registry

## Why

The `trade_agreements` registry covers free trade, preferential and services agreements, but not standalone investment treaties. Bilateral investment treaties (BITs), which Canada calls Foreign Investment Promotion and Protection Agreements (FIPAs), are left out everywhere. `docs/intblock-inclusion-policy.md` skips "untitled bilateral BITs" because they are not country groups. The registry has no `agreement_type` for them, so they are not recorded anywhere.

They are country-to-country legal links of the same kind as bilateral FTAs: parties, status, signature and entry into force dates. Global Affairs Canada lists 59 FIPAs next to Canada's FTAs in one table (checked on 2026-11-23): 33 in force, 2 suspended, 1 superseded, 1 terminated, 1 signed, 8 in negotiation, 3 at the exploratory stage and 10 inactive. The registry has none of them. The six plurilateral investment treaties that are intblocks (`OICIA`, `ACIA`, `UAIA`, `CJKIA`, `PCFI`, `INTRAEUBIT`) also have no registry records. Without them, `country_trade_agreements` cannot answer "which countries have an investment treaty with Canada?"

Investment treaties are reference data under the same rules as trade agreements. Treaty parties, status and dates are recorded. Investment flows, arbitration cases and treaty-content scores are not.

## What Changes

- **New `agreement_type: investment`.** It covers standalone treaties whose main object is the promotion, protection or facilitation of investment: BITs, FIPAs, investment protection agreements, and cooperation and facilitation investment agreements, bilateral or plurilateral. An FTA with an investment chapter keeps its FTA type. The `services` description changes from "services or investment only" to "services only". This is an open enum value, so the change is MINOR.
- **Identifiers.** Investment records always take the suffix `-BIT` (`AMCA-BIT`), so they never collide with an FTA between the same parties (`CACR` and `CACR-BIT`). An additional investment treaty between the same parties adds its year of signature (`-BIT-2009`), and ids are never renamed.
- **Suspended, replaced and renegotiated treaties.** A BIT that an FTA suspends or replaces (Canada–Panama, Canada–Peru, Canada–Ukraine) is `superseded` by that FTA, with `ended` set to the date of suspension. A renegotiation of a treaty in force is recorded in its notes until a new instrument is signed.
- **Bloc parties.** Treaties signed by the Belgium–Luxembourg Economic Union list a new `BLEU` intblock as one party. Treaties signed by the EU list the `EU` intblock, as for trade agreements.
- **New optional catalogue id `unctad_iia_id`.** UNCTAD's IIA Navigator becomes a third catalogue for `verification: catalogue`, after WTO RTA-IS and ADB ARIC.
- **Linked plurilateral treaties.** `OICIA`, `ACIA`, `UAIA`, `CJKIA`, `PCFI` and `INTRAEUBIT` get registry records with `intblock:` links.
- **Pilot import: Canada.** The 59 GAC rows are imported, with signature, entry into force and suspension dates from the Canada Treaty Series (`treaty-accord.gc.ca/details.aspx?id=N`), as `verification: official`.
- **Scope guardrail.** No investment flows or stocks, arbitration (ISDS) case counts, treaty-content mapping (fair and equitable treatment or ISDS clauses), treaty "generations" or scores.
- **Policy.** `docs/intblock-inclusion-policy.md`, `docs/intblock-sources.md` and `docs/discovery.md` say that bilateral investment treaties belong in the registry. The intblock bar for plurilateral investment treaties stays as it is.

## Impact

- Affected specs: `trade-agreements` (requirements added).
- Affected source: `data/schemas/trade_agreements.schema.json` (enum value, `unctad_iia_id`, `services` description); new `data/intblocks/*/BLEU.yaml`; about 65 new files in `data/trade_agreements/` (59 Canada rows and 6 linked plurilateral treaties).
- Affected code: `internacia_builder/validate/trade_agreement_rules.py` (id suffix and type checks), `internacia_builder/contract.py` and the export column for `unctad_iia_id`, and a one-off `scripts/oneoff/import_canada_fipas.py`.
- Affected exports: `trade_agreements`, `trade_agreement_parties` and `country_trade_agreements` gain `investment` rows; `trade_agreements` gains the `unctad_iia_id` column. Consumers who count trade agreements from these tables need to filter on `agreement_type`.
- Affected documentation: inclusion policy, sources log, discovery guide, data contract, AI-consumer guide, query examples, data dictionary, counts, changelog fragment.
- Versioning: MINOR (new open enum value, new optional field, new intblock, new records).
- Out of scope here: walks of other national treaty series (US, Australia) and of the UNCTAD IIA Navigator. They are follow-up changes that use the same rules (see `design.md`).

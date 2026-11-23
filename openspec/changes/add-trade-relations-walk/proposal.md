# Change: Walk the world's bilateral trade relations agreements

## Why

`add-investment-and-trade-relations-types` added `agreement_type: trade_relations` with the U.S. agreements from TARA and the State Department's Treaties in Force. There is no world catalogue of non-preferential trade agreements like the UNCTAD IIA Navigator for investment treaties: the WTO and ADB ARIC list only preferential agreements. The UN Treaty Series registers bilateral trade agreements of every country, but it rarely records terminations, so a UNTS entry does not show whether an agreement of the 1950s is still in force. Several party governments publish treaty databases with the current status.

The maintainer chose on 2026-11-23 to find agreements in the UNTS and take their status from national treaty databases where one exists (Australia, Canada, the Netherlands, Switzerland), importing UNTS-only agreements only when they are recent.

## What Changes

- **New field `unts_registration`** (string, `I-<n>` or `II-<n>`) in `data/schemas/trade_agreements.schema.json` and the `trade_agreements` export, with a duplicate check (it joins the catalogue identifiers that `DUPLICATE_IDENTIFIER` covers). `verification: catalogue` also covers UNTS-only records.
- **Sources.** The UNTC advanced search for bilateral treaties with subject term "Trade" (original agreements), filtered by title to trade agreements, commercial agreements, agreements on trade (and economic cooperation), most-favoured-nation agreements and treaties of commerce; and the national treaty databases of Australia, Canada, the Netherlands and Switzerland.
- **Status policy.** A national database entry gives an `official` record with its status. A UNTS-only agreement is written at `catalogue` level only when concluded in 2000 or later and neither party is a current EU member state; older ones are report candidates.
- **Identifiers.** As for investment treaties: the earliest trade relations agreement of a pair takes `<pair>-TRA`, each further one `<pair>-TRA-<year>`. A bloc party comes first (`BENELUXPH-TRA`). Agreements that the Netherlands concluded together with Belgium and Luxembourg have the `BENELUX` intblock as one party, and those of the Belgium–Luxembourg Economic Union the `BLEU` intblock.
- **Result.** 342 new records: 301 `official` (180 in force, 117 terminated, 4 signed), 41 `catalogue`. 685 older UNTS-only agreements stay report candidates.
- **Not in scope.** Free trade, partnership and association agreements (already in the registry), sectoral commodity agreements, payments and clearing agreements, annual trade protocols, treaties of friendship, commerce and navigation, and agreements with a party that has no country record (the USSR, Czechoslovakia, Yugoslavia, the GDR).

## Impact

- Affected specs: `trade-agreements` (UNTS registration number, walk status policy).
- Affected source: schema, new `data/trade_agreements/*-TRA*.yaml` files, existing U.S. trade relations records (gain `unts_registration`).
- Affected code: `internacia_builder/schemas.py`, `trade_agreements.py`, `validate/trade_agreement_rules.py`, `quality_report.py`; one-off scripts under `scripts/oneoff/`.
- Affected exports: new nullable column `trade_agreements.unts_registration`; new `trade_relations` rows.
- Versioning: MINOR.

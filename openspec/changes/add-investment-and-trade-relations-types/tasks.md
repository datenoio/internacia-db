## 1. Schema

- [x] 1.1 Add `investment` and `trade_relations` to the `agreement_type` enum in `data/schemas/trade_agreements.schema.json` and narrow the `services` description to services only
- [x] 1.2 Rebuild so `contract.json` lists the new values

## 2. Data

- [x] 2.1 Add the 41 U.S. bilateral investment treaties from trade.gov with `-BIT` ids
- [x] 2.2 Add the U.S. trade relations agreements from TARA and Treaties in Force with `-TRA` ids, and the 1881 treaty of commerce with `-1881` ids

- [x] 2.3 Add the WTO plurilaterals `ITA` and `TCA` as intblocks (rosters from the WTO), found through the trade.gov WTO agreements page

## 3. Documentation and checks

- [x] 3.1 Document the new types, the suffix rule and the U.S.-only coverage in `docs/data-contract.md` and `docs/ai-consumers.md`
- [x] 3.2 Log trade.gov and the TARA Wayback snapshot in `docs/intblock-sources.md`
- [x] 3.3 Add a test that a record with `agreement_type: investment` validates and that `agreement_type: bit` is rejected
- [x] 3.4 Add a `changelog.d` fragment
- [x] 3.5 Validate, rebuild with the pinned requirements, and run the tests

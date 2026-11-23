# Change: Add the trade relations type and the U.S. agreements from trade.gov and TARA

## Why

The trade agreements registry links countries through free trade and preferential agreements, and since `add-investment-agreements` through investment treaties. One more kind of bilateral economic treaty connects countries and has official sources with parties and dates: agreements that grant most-favoured-nation or normal trade relations treatment without preferences. The U.S. International Trade Administration's former Trade and Related Agreements Database (TARA) listed the U.S. ones (the 1990s agreements with the former Soviet states, the 2000 bilateral trade agreement with Viet Nam, and others), and the State Department's Treaties in Force gives their dates and status. A non-preferential trade relations agreement is not a `pta`, and WTO RTA-IS and ADB ARIC list none of them.

`add-investment-agreements` names a walk of the U.S. treaty series as a follow-up under its rules. trade.gov publishes the 41 U.S. bilateral investment treaties with signature and entry-into-force dates (https://www.trade.gov/bilateral-investment-treaties).

The maintainer decided on 2026-11-23 to add both.

## What Changes

- **New `agreement_type` value `trade_relations`**: a bilateral agreement or treaty that grants most-favoured-nation or normal trade relations treatment without preferential tariff commitments (trade relations agreements, bilateral trade agreements, treaties of commerce).
- **Identifiers.** A `trade_relations` record takes the sorted alpha-2 pair and the suffix `-TRA` (`AMUS-TRA`, `USVN-TRA`), or the year of signature for an older treaty of commerce (`RSUS-1881`), as in the existing `EUSI-1996`, so the bare pair id stays free for a trade agreement.
- **Trade relations data.** 27 U.S. records: the agreements on trade relations that TARA lists (the former Soviet states, Albania, Bulgaria, Cambodia, Latvia, Laos, Mongolia, Romania, Viet Nam), the 1979 agreement with China from Treaties in Force 2026, and the 1881 treaty of commerce with Serbia, which the United States applies to the six successor states of Yugoslavia (one record each). The agreements with Russia and Belarus stay `in_force`: Public Law 117-110 suspended normal trade relations tariff treatment in 2022 but did not terminate them.
- **Investment data** under the `add-investment-agreements` rules: the 41 U.S. BITs from trade.gov as `verification: official` records (`ALUS-BIT` … `USUY-BIT`), including the two that ended (Bolivia in 2012, Ecuador in 2018). The Morocco treaty stays in force; only its dispute settlement articles were suspended in 2016 under the U.S.–Morocco FTA. The 1991 treaty with the Czech and Slovak Federal Republic is recorded as two bilateral records (`CZUS-BIT`, `SKUS-BIT`), because the registry has no Czechoslovakia country record and trade.gov lists the two successor relationships separately.
- **Related intblocks.** The trade.gov WTO agreements page lists two plurilaterals that had no intblock: `ITA` (Information Technology Agreement) and `TCA` (Agreement on Trade in Civil Aircraft). Both are added under the current intblock policy, with rosters from the WTO.
- **Not in scope.** Treaties of friendship, commerce and navigation, sectoral market-access arrangements and AD/CVD suspension agreements. A world walk of trade relations agreements is a follow-up change.

## Impact

- Affected specs: `trade-agreements` (trade relations type and identifiers).
- Affected source: `data/schemas/trade_agreements.schema.json` (enum value), new files in `data/trade_agreements/`, `data/intblocks/trade/ITA.yaml`, `data/intblocks/trade/TCA.yaml`.
- Affected exports: `trade_agreements.agreement_type` and `country_trade_agreements.agreement_type` gain `trade_relations` in `contract.json`; both enums are open.
- Affected documentation: `docs/data-contract.md`, `docs/ai-consumers.md`, `docs/intblock-sources.md`.
- Versioning: a new value in an open enum and new rows ship as a MINOR release.

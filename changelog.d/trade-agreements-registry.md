### Added

- Trade agreements registry (OpenSpec `add-trade-agreements-registry`). Source files are in
  `data/trade_agreements/<ID>.yaml` and follow `data/schemas/trade_agreements.schema.json`.
  The build exports them as new `trade_agreements` and `trade_agreement_parties` tables
  (Parquet, JSONL, DuckDB) and a new `country_trade_agreements` view. In the view, a bloc
  party such as the EU expands to its current member countries, with `via` set to the bloc id.
  The registry records parties, status, dates, `wto_rta_id`, `aric_id` and provenance only.
  It has no trade values, tariff lines or depth scores.
- Every multilateral `fta`, `pta` and `customs` intblock, plus `TFTA`, `PACER` and `EAEU`, has a
  registry record linked to the intblock with `intblock:`. The record reads its parties from the
  intblock's `includes`.
- The ADB ARIC FTA database (snapshot of 2026-11-22) is imported. Rows that matched existing
  records got `aric_id`; the other rows are new `verification: catalogue` records. ARIC's
  proposed and negotiating agreements are imported as well, with their status.
- Twelve multilateral agreements from the ARIC walk that are in force now have intblocks in
  `data/intblocks/fta/`, with party-by-party dates from official sources. Each is linked from its
  registry record:
  - EFTA agreements, dated from the Swiss Fedlex scope tables and EFTA partner pages: `EFTASG`,
    `EFTAKR`, `EFTAHK`, `EFTAPH`, `EFTAID`, `EFTAGE` and `EFTATR` (the modernised 2018
    agreement).
  - EAEU agreements, from Eurasian Economic Commission texts: `EAEUVN`, `EAEURS` and `EAEUIR`
    (the 2023 agreement). The Union itself is a party alongside its member states.
  - `GCCSG`, the GCC–Singapore FTA. The six GCC states are parties individually.
  - `UKPACIFICEPA`, the UK–Pacific States interim EPA. It is applied provisionally from 1 January
    2021; Samoa and Solomon Islands acceded on 31 March 2022.
- The eight ARIC candidates marked as signed but not in force were checked against official
  sources, because ARIC's statuses were out of date:
  - `MERCOSURSG`, `PACALLSG` (Pacific Alliance–Singapore), `EAEUCN` (EAEU–China, a
    non-preferential agreement) and `AZTMTR` (Azerbaijan–Türkiye–Turkmenistan cooperation) are
    in force. Each now has an intblock, with per-party dates.
  - `EAEUSG` (EAEU–Singapore) is signed but not yet in force. It now has an intblock with no
    `active_period`.
  - `GCCKR`, `GCCNZ` and `GCCPK` were only concluded, never signed. Their registry status is now
    `negotiating`, and they have no intblock.
  - ARIC lists Australia, New Zealand and Canada as parties to the Pacific Alliance agreement.
    None of them signed it.
- Two earlier agreements are registry records with status `superseded`: `EFTATR-1991`, the
  EFTA–Turkey agreement of 1991, and `EAEUIR-2018`, the EAEU–Iran interim agreement of 2018.
- New validator rules for the registry: schema, ids shared with intblocks, party and intblock
  resolution, status and date consistency, and freshness. The quality report now lists
  multilateral catalogue records that have no intblock yet.

### Changed

- `intblocks_aliases` has a new `target_dataset` column and a new reason, `moved`.
  `countries_aliases` keeps its old columns.
- `docs/intblock-inclusion-policy.md`: bilateral trade agreements belong in the registry.
  The bar for an intblock still applies to agreements with three or more parties.

### Removed

- **Breaking, needs a MAJOR release (5.0.0).** 34 two-party trade agreements left `intblocks`
  and `memberships` and moved to `trade_agreements` under the same ids:
  `ANZCERTA`, `AUINDIA`, `AUUAE`, `AUUK`, `CETA`, `CHAFTA`, `CNEC`, `CNKR`, `CNNI`, `CNRS`,
  `EUCENTRALAFRICAEPA`, `EUJP`, `EUKR`, `EUNZ`, `EUSG`, `EUUA`, `EUUK`, `EUVN`, `INUAE`,
  `UKIN`, `UKJP`, `UKNZ`, `USAU`, `USBH`, `USCL`, `USCO`, `USIL`, `USJO`, `USKR`, `USMA`,
  `USOM`, `USPA`, `USPE` and `USSG`. Each has an alias with `reason: moved` and
  `target_dataset: trade_agreements`. `USCR` was the US–Costa Rica part of CAFTA-DR, so it is
  merged into `CAFTADR`. To find the agreements a country is party to, query the view:

  ```sql
  SELECT agreement_id, via FROM country_trade_agreements WHERE country_code = 'KR';
  ```

### Added

- Two `agreement_type` values in the trade agreements registry (OpenSpec
  `add-investment-and-trade-relations-types`): `investment` for bilateral investment
  treaties and `trade_relations` for agreements that grant most-favoured-nation or normal
  trade relations treatment without preferences. Both cover the United States only so far.
- 41 U.S. bilateral investment treaties from trade.gov (`ALUS-BIT` … `USUY-BIT`), checked on
  2026-11-23, including the terminated treaties with Bolivia and Ecuador.
- 27 U.S. trade relations records from the ITA's former TARA database and the State
  Department's Treaties in Force 2026: 21 agreements on trade relations (`-TRA` ids, among
  them `RUUS-TRA`, `USVN-TRA`, `CNUS-TRA`) and the 1881 treaty of commerce with Serbia as
  applied to the six successor states of Yugoslavia (`-1881` ids).
- `ITA` (Information Technology Agreement, 56 participants) and `TCA` (Agreement on Trade in
  Civil Aircraft, 33 Signatories), WTO plurilaterals with rosters from the WTO.

### Changed

- `services` in `agreement_type` now means trade in services only.
- `CAFTADR` notes give the entry-into-force date for each signatory and the 2006 amendment
  to Article 22.5; `USBH` notes the 2009 First Protocol of Amendment; `USAU`, `USCO`,
  `USKR`, `USPA`, `USSG` and `CAFTADR` cite trade.gov for `in_force`; `USMCA` links trade.gov.

### Added

- `trade_agreements.gptad_id`: the agreement id in the World Bank Global Preferential Trade
  Agreements Database (GPTAD), on the registry records that GPTAD lists, mapped by
  `scripts/oneoff/import_gptad.py` from pages saved by `scripts/oneoff/fetch_gptad.py` on
  2026-11-23 (OpenSpec change `add-gptad-catalogue-links`).
- `treaty_text` link type in `trade_agreements.links`: a URL of the full text of the
  agreement. Mapped records link the GPTAD PDF. The registry stores the URL, not the text.

### Changed

- A trade agreement record linked to an intblock may list its own `links`; the export puts
  them after the intblock's links instead of dropping them.
- The validator reports a `wto_rta_id`, `aric_id` or `gptad_id` set on two records as
  `DUPLICATE_IDENTIFIER`.

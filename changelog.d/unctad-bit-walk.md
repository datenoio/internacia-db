### Added

- `unctad_iia_id` in `trade_agreements`: the UNCTAD IIA Navigator treaty identifier that
  `add-investment-agreements` specifies, with a validator check that no two records share it.
- 3,367 bilateral investment treaties from the UNCTAD IIA Navigator (OpenSpec
  `add-unctad-bit-walk`), read from Wayback Machine captures of 2025–2026, as
  `agreement_type: investment` records at `verification: catalogue`. The U.S. BITs from
  trade.gov and the Canadian treaties gain their UNCTAD ids.

### Changed

- `verification: catalogue` also covers records taken only from the UNCTAD IIA Navigator.

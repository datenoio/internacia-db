### Added

- `unctad_iia_id` in `trade_agreements`: the UNCTAD IIA Navigator treaty identifier
  (OpenSpec `add-unctad-bit-walk`), with a validator check that no two records share it.
- 3,409 bilateral investment treaties from the UNCTAD IIA Navigator, read from Wayback
  Machine captures of 2025–2026, as `agreement_type: investment` records at
  `verification: catalogue`. The 41 U.S. BITs checked against trade.gov gain their UNCTAD ids.
- `BLEU` (Belgium–Luxembourg Economic Union), a `customs`/`economic` intblock, the party to
  the investment treaties that Belgium and Luxembourg conclude together.

### Changed

- `verification: catalogue` also covers records taken only from the UNCTAD IIA Navigator.

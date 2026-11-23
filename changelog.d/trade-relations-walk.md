### Added

- `unts_registration` in `trade_agreements`: the UN Treaty Series registration number
  (OpenSpec `add-trade-relations-walk`), with a validator check that no two records share it.
- 342 bilateral trade relations agreements (`agreement_type: trade_relations`): 301 with the
  status from the treaty databases of Australia, Canada, the Netherlands and Switzerland, and
  41 found only in the UN Treaty Series, concluded since 2000 between countries outside the EU
  (`verification: catalogue`). Agreements that the Netherlands concluded with Belgium and
  Luxembourg have the `BENELUX` intblock as one party.

### Changed

- `verification: catalogue` also covers records taken only from the UN Treaty Series.
- `ALUS-TRA` and `CNUS-TRA` give their UN Treaty Series registration numbers.

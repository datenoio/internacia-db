## 1. Schema and validation

- [x] 1.1 Add `provisional_application` to records and parties in `data/schemas/trade_agreements.schema.json`; define `in_force` as definitive entry into force
- [x] 1.2 Accept `provisional_application` for the `in_force` date rule, reject it on `proposed`, `negotiating`, `signed` and `abandoned` records, and check `ended` against it
- [x] 1.3 Tests in `tests/test_trade_agreements.py`

## 2. Build and exports

- [x] 2.1 Export the column in `trade_agreements`, `trade_agreement_parties` and `country_trade_agreements`; derive `joined` from the earlier of the two dates
- [x] 2.2 Keep a linked record's `in_force` from its intblock out when the record sets `provisional_application`
- [x] 2.3 Regenerate `contract.json`; update `scripts/check_generated_artifacts.py`

## 3. Data and documentation

- [x] 3.1 Set `provisional_application` on UK records where a UK Government source gives the date
- [x] 3.2 Document the column in `docs/data-contract.md` and `docs/ai-consumers.md`; changelog fragment

## 4. Verification

- [x] 4.1 Rebuild with the pinned requirements; run the validators, `ruff` and `pytest tests/`

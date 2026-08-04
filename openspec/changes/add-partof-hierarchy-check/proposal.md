# Change: Add automated partof hierarchy validation

## Why
The EU `partof: EEA` error showed that treaty/agreement targets used as parent organizations slip through validation. A systematic check for `partof` links pointing at agreements/treaties rather than parent orgs would catch similar errors.

## What Changes
- Add quality/validation rule flagging intblocks whose `partof.id` resolves to a record with `legal_status: treaty` or `blocktype` containing `agreement`.
- Document UN specialized agency `partof` convention (direct `UN` vs via `ECOSOC`) in `docs/intblock-inclusion-policy.md`.
- Fix EU record as part of Phase 1 factual fixes (outside this change implementation).

## Impact
- Affected specs: intblocks-data-quality, cross-dataset-integrity
- Affected code: `internacia_builder/validate/` or `quality.py`, docs

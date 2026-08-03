## 1. African Union
- [x] 1.1 Add `EH` to `AFUNION.yaml` includes (member since 1984/OAU era) with provenance; set `membership_count: 55`

## 2. Interpol
- [x] 2.1 Rebuild `INTERPOL.yaml` includes from the official member list (196) with entry dates
- [x] 2.2 Represent non-sovereign member territories (`AW`, `CW`, `SX`) consistently with the includes contract (type/note)
- [x] 2.3 Set `geographic_scope: global` and correct `membership_count`

## 3. CIS
- [x] 3.1 Set `GE` to `former_member` with `left: '2009'`, `UA` to `former_member` with `left: '2018'` (note the de jure nuance), `TM` to `associate_member`; annotate `MD` status
- [x] 3.2 Adjust `membership_count` to current full members and add provenance

## 4. United Nations record
- [x] 4.1 Set `geographic_scope: global` and replace `recognition_status: "UN agency"`
- [x] 4.2 Write a substantive description (founding, charter, principal organs)
- [x] 4.3 Add `PS` and `VA` includes entries with `status: observer`
- [x] 4.4 Populate `suborganizations` from the 36 `unagency/` records (or cross-link via `partof` per the UN organ linkage requirement)

## 5. AIIB
- [x] 5.1 Complete the includes roster toward the ~110 approved members from aiib.org, or document why the roster is partial and align `membership_count`

## 6. ICC (cricket)
- [x] 6.1 Reconcile `sports/ICC.yaml` includes (217 rows) against the official ICC member list; fix `membership_count`

## 7. Validation
- [x] 7.1 `python scripts/validate_intblocks.py --json` — zero errors
- [x] 7.2 Rebuild artifacts and run `check_generated_artifacts`
- [x] 7.3 Confirm quality analyzer reports no MEMBERSHIP_COUNT_MISMATCH for the six records

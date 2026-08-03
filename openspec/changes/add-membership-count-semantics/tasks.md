## 1. Schema
- [x] 1.1 Add `membership_count_type` enum to `data/schemas/intblocks.schema.json` with description
- [x] 1.2 Document default semantics (absent = countries) in the schema and `docs/ai-consumers.md`

## 2. Data classification
- [x] 2.1 Re-run the mismatch scan (204 records as of 2026-08-02) and classify each as unit-mismatch vs drift
- [x] 2.2 Set `membership_count_type` on non-country-count records (WNA, IGA, ETSI, WEF, and peers) with provenance for the count
- [x] 2.3 Fix counts or rosters on genuine-drift records — six high-impact rosters fixed in update-intblock-roster-accuracy; the remaining mismatches surface as validator warnings and are tracked as known data gaps

## 3. Validation rule
- [x] 3.1 Update the `MEMBERSHIP_COUNT_MISMATCH` check to exempt non-country `membership_count_type` records from roster comparison
- [x] 3.2 Require a provenance entry for `membership_count` when the type is non-country
- [x] 3.3 Add unit tests for both paths

## 4. Verification
- [x] 4.1 `python scripts/validate_intblocks.py --json` — zero errors
- [x] 4.2 Quality analyzer run shows no unexplained `MEMBERSHIP_COUNT_MISMATCH`

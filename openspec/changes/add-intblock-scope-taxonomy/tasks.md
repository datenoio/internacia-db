## 1. Policy document
- [x] 1.1 Write `docs/intblock-inclusion-policy.md` (IGO vs treaty vs forum vs enumeration boundaries, examples)
- [x] 1.2 Cross-link from `docs/strategy-and-user-needs.md` and README

## 2. Schema and labeling
- [x] 2.1 Add optional `scope_category` enum to `intblocks.schema.json`
- [x] 2.2 Label high-visibility records (UN, NATO, EU, WTO, DVD regions, FATF, etc.)
- [x] 2.3 Extend validation to warn on missing `scope_category` for `status: formal` records (non-blocking initially)

## 3. Consumer documentation
- [x] 3.1 Document filter recipes in `docs/ai-consumers.md` and `docs/query-examples.md`
- [x] 3.2 Update `llms.txt` gotchas with scope_category guidance

## 4. Verification
- [x] 4.1 `validate_intblocks.py --json` green; rebuild artifacts

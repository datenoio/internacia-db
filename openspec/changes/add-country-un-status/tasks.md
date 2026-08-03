## 1. Schema
- [x] 1.1 Add `un_status` enum (`member`, `observer`, `non_member`) to `countries.schema.json` with description
- [x] 1.2 Add a validation rule that `un_status` and `un_member` are consistent (`member` ⇔ `un_member: true`)

## 2. Data
- [x] 2.1 Set `un_status: observer` on `PS` and `VA`; `member` on the 193 UN members; `non_member` on the rest
- [x] 2.2 Set explicit `un_member`, `independent`, `landlocked` on `AN`, `JG`, `KV`, `XA`, `XS`, `XT`, `XN`
- [x] 2.3 Backfill population `year` for `KV`, `XA`, `XS`, `XT`, `XN` with provenance

## 3. Policy documentation
- [x] 3.1 Document the disputed-territory inclusion threshold in `docs/country-code-policy.md` (or decide to add `XL`/`XC` records in a follow-up change)
- [x] 3.2 Add the `JG` double-count warning (JG aggregate population ≠ GG + JE)
- [x] 3.3 Add a note on exceptionally reserved codes (`EU`, `EZ`, `UN`) and point `EU` seekers to the intblock

## 4. Verification
- [x] 4.1 `python scripts/validate_countries.py --json` — zero errors
- [x] 4.2 Verify `SELECT count(*) FROM countries WHERE un_status = 'member'` returns 193 and `observer` returns 2
- [x] 4.3 Update docs (`llms.txt`, `docs/ai-consumers.md`) that describe UN membership semantics

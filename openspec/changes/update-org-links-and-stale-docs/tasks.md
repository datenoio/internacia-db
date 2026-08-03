## 1. Organization link sweep
- [x] 1.1 Replace all `github.com/commondataio/...` self-references with `github.com/datenoio/...` across the 12 affected files, including the README badge
- [x] 1.2 Replace relative sister-repo links (`../internacia-api`, `../internacia-python`) with absolute GitHub URLs
- [x] 1.3 Verify every replaced URL resolves (200) — spot-check with the link validator

## 2. README schema table
- [x] 2.1 Add `centroid` and `parent_entity` rows to the countries schema table
- [x] 2.2 Add `exceptionally_reserved` to the documented `code_status` enum values
- [x] 2.3 List all 7 non-standard codes consistently with `docs/country-code-policy.md`

## 3. Category count
- [x] 3.1 Remove the empty `data/intblocks/tourism/` directory (or land its first record)
- [x] 3.2 Align the category count in `README.md:285`, `openspec/project.md:74`, `docs/improvement-plan.md:45` with the populated-directory count

## 4. llms-full.txt
- [x] 4.1 Rebuild `llms-full.txt` as a strict superset of `llms.txt`, or delete it and remove references
- [x] 4.2 If kept, add a drift check (superset relation) to CI or tests

## 5. Stale planning docs
- [x] 5.1 Add a dated status banner to `docs/improvement-plan.md` (currently claims v1.2.0) marking shipped items
- [x] 5.2 Update `docs/strategy-and-user-needs.md` Track A items (A1 license, A2 alias map, A3 `_meta`) to shipped status; keep genuinely open items (A4 release diff, B4 crosswalks, C1 datapackage, D1 API posture)

## 6. Legacy data warning
- [x] 6.1 Add a warning to `AGENTS.md` and `llms.txt` that `data/_legacy/` is obsolete and not for consumption

## 7. Verification
- [x] 7.1 Run the markdown link checker; zero broken links
- [x] 7.2 `rg commondataio` returns no maintained-doc hits (dev/ research notes excluded)

## 1. Record authoring

- [x] 1.1 Add `UNSC` — UN Security Council (15 members, peace and security mandate)
- [x] 1.2 Add `UNGA` — UN General Assembly (193 member states, deliberative organ)
- [x] 1.3 Add `UNHRC` — UN Human Rights Council (47 members; resolve deferred sourcing from gap backlog)

## 2. Metadata quality

- [x] 2.1 Populate `legal_status`, `geographic_scope`, `headquarters` for all three records
- [x] 2.2 Set `partof: [UN]` and accurate `includes` membership where membership model applies
- [x] 2.3 Add `wikidata_id`, `founded`, `links`, and non-templated descriptions

## 3. Validation and tracking

- [x] 3.1 Run `validate_intblocks.py` and cross-dataset include checks
- [x] 3.2 Mark UNHRC `shipped` in `dev/research/backlog.md` (or gap backlog tracker)
- [x] 3.3 Run `openspec validate add-un-principal-organs --strict`

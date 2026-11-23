# Tasks: add non-reciprocal preference schemes from the WTO PTA Database

## 1. Schema and build

- [x] 1.1 Add the following to `data/schemas/trade_agreements.schema.json`:
  - `parties[].role` (`grantor`, `beneficiary`);
  - `parent` (string);
  - `wto_pta_ids` (array of unique integers ≥ 1);
  - a `catalogue` description that names the WTO PTA Database.
- [x] 1.2 `internacia_builder/trade_agreements.py`:
  - derive `role` (`contributor` → `grantor`, `recipient` → `beneficiary`, `party` for other agreement types);
  - export `parent` and `wto_pta_ids`.
- [x] 1.3 `internacia_builder/schemas.py`:
  - add `role` to `trade_agreement_parties` and `country_trade_agreements`;
  - add `parent` (string) and `wto_pta_ids` (list of int64) to `trade_agreements`.
- [x] 1.4 `internacia_builder/contract.py`:
  - carry `role` through the `country_trade_agreements` SQL, including bloc expansion;
  - register the open `role` enum (`grantor`, `beneficiary`, `party`);
  - add a foreign key from `trade_agreements.parent` to `trade_agreements.id`.
- [x] 1.5 Regenerate the data dictionary and `contract.json`. Update `tests/` for the new columns and the view.

## 2. Validation and quality report

- [x] 2.1 `internacia_builder/validate/trade_agreement_rules.py` gets role rules:
  - every party of a listing preference scheme has a role;
  - at least one grantor;
  - at least one beneficiary unless the record is a parent;
  - no role on other agreement types;
  - a linked preference-scheme intblock uses only `contributor` and `recipient` for its parties.
- [x] 2.2 Parent rules:
  - the parent resolves to a `preference_scheme` record;
  - no cycles;
  - same current grantors as the parent, unless the parent has no beneficiaries;
  - current beneficiaries are a subset of the parent's.
- [x] 2.3 `wto_pta_ids` rule: no id appears in two records.
- [x] 2.4 Exempt `preference_scheme` records from `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`.
- [x] 2.5 Write tests for every rule, using the scenarios in `specs/trade-agreements/spec.md`.

## 3. Roster fixes

- [x] 3.1 `data/intblocks/pta/GSP.yaml`: change the 16 grantors from `participant` to `contributor`, and update the notes.
- [x] 3.2 `data/intblocks/pta/SPARTECA.yaml`: make AU and NZ `contributor` and the 13 Forum Island Countries `recipient`. Keep `joined`, and note the change of status.

## 4. Import

- [x] 4.1 Write `scripts/oneoff/import_wto_ptadb.py`. It reads:
  - the list XLSX export;
  - each scheme card (postback on `ptaList.aspx`);
  - `ptaBeneficiaries.aspx`, with each sub-scheme selected.

  It writes JSON for review. It does not read "Tariffs & Trade".
- [x] 4.2 Commit the WTO numeric code crosswalk: country `numeric_code` and `m49_code`, plus the overrides 899, 893, 892, 888, 736 and 158. Skip 128 and 146 and add a note for each.
- [x] 4.3 Write 29 scheme records and 16 new sub-scheme records with ids following design decision 4. The 4 EAEU rows and their LDC sub-schemes each become one record. The EAEU LDC lists have 49 or 50 entries depending on the notifying member, so reconcile them by hand. Each gets:
  - `verification: catalogue`;
  - provenance with the version date;
  - `superseded_by` where a grantor replaced a scheme;
  - `ended` for ended or lapsed schemes.

  Review every id and every `parent` by hand. China's LDC scheme (PTA 79) is skipped (`SKIP`), because the PTA Database lists no beneficiaries for it.
- [x] 4.4 Existing records:
  - add `wto_pta_ids` to `AGOA` (37), `CBERA` (78), `CARIBCAN` (70) and `SPARTECA` (80);
  - add `parent: EU-GSP` to `GSPPLUS` and `parent: GSP` to each national GSP scheme;
  - check the CBERA (Panama, Curaçao) and AGOA (Gabon) differences against USTR. The registry is right on all three, and the PTA Database lags: Panama moved to `USPA` in 2012, Curaçao is on the USTR CBI list, and Gabon was redesignated for AGOA in May 2026.
- [x] 4.6 Give the existing Lomé Convention records (`LOME-1975`, `LOME-1979`, `LOME-1984`) roles: the EU is the grantor and the ACP States are the beneficiaries.
- [x] 4.5 Run `python scripts/validate_intblocks.py --json` and `python scripts/builder.py build`. Check that `country_trade_agreements` has grantor rows through `EU` and the expected beneficiary rows.

## 5. Documentation and release

- [x] 5.1 `docs/intblock-sources.md`: the PTA Database row now covers registry records. Keep the intblock exclusion for national GSP and LDC-only schemes.
- [x] 5.2 Add a query for the preference schemes a country benefits from. It went into the trade agreements section of `docs/ai-consumers.md`, because `docs/query-examples.md` has no trade agreement recipes, so no recipe counts changed. The existing pair query already leaves out `preference_scheme`.
- [x] 5.3 Update the AI-consumer guide, `llms.txt` and the current counts.
- [x] 5.4 Add a `changelog.d` fragment with the consumer note on `country_trade_agreements` (MINOR).
- [x] 5.5 Run `openspec validate add-preference-scheme-rosters --strict`.

## 6. Follow-up (separate change)

- [x] 6.1 Propose historical beneficiary dates from the PTA Database versions (design decision 10). Proposed and implemented as `add-preference-scheme-beneficiary-history` (PR 216).

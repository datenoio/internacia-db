# Repository Review Report

Review date: 2026-08-02 (supersedes the 2026-07-11 review)
Repository: `internacia-db` @ v1.9.0 (build 2026-08-01, commit `e228586`)
Datasets: 256 countries · 1,078 intblocks · 86 blocktypes

## Executive summary

The repository is in the best shape it has been across all reviews. All 264 tests pass, ruff is clean, the countries validator is fully clean (0 errors, 0 warnings — first time), the intblocks validator has 0 errors, all 169 internal doc links resolve, and the cross-format artifact guard passes with a single build identity. Of the 12 findings from the July review, 7 are fixed, 4 partially fixed, 1 open. The v1.8.0 enrichment campaign (~500 intblock records with sourced rosters and provenance) materially improved content depth: intblock provenance went from ~0% to 99.9% coverage, `wikidata_id` missing dropped from 22% to 10.5%, `headquarters` missing from 54% to 31%.

The most important open items now are:

1. **Intblock membership-count integrity**: 89 records where `membership_count` matches neither the total nor the member-class `includes` — a mix of genuine roster drift (MTCR, CTBTO, MERCOSUR) and orgs whose count includes non-state members (AIIB 111 vs 35 country includes; WNA 3000), which the validator cannot currently distinguish.
2. **~17 never-triaged coverage gaps** among internationally significant formats (Minamata Convention, Aarhus, Escazú, PSI, Three Seas, Lancang-Mekong, Bucharest Nine, Abraham Accords, and others) that appear in no backlog document.
3. **One false claim in `llms.txt`** (schemas do not, in fact, carry per-property descriptions) and stale June planning docs that now misstate current state.
4. **Country display names stale vs official renames**: `MK` "Macedonia, FYR", `SZ` "Swaziland", `CV` "Cape Verde", `TR` "Turkey".

Scope guardrail respected throughout: countries remain reference data only — nothing below proposes socioeconomic profile fields.

## Verification performed (2026-08-02)

- `pytest tests/`: 264 passed (~23 s). `ruff check .`: clean.
- `validate_countries.py --json`: 256 records, 0 errors, **0 warnings**.
- `validate_intblocks.py --json`: 1,078 records, 0 errors, 167 warnings (89 membership_count mismatch, 46 provenance depth, 22 missing includes, 10 shared acronyms).
- `check_generated_artifacts.py`: OK — all formats and sources agree; single build identity 1.9.0/`e228586`.
- `check_markdown_links.py`: 169/169 internal links valid.
- Field-completeness census over all 256 country and 1,078 intblock YAML files; coverage spot-check of ~78 major IGOs/treaties/formats; CI workflow, packaging, OpenSpec, and docs inventory review.

## Status of the 2026-07-11 findings

| # | Finding | Status |
|---|---------|--------|
| 1 | Uncommitted space/ migration + rebuilt datasets | **Fixed** (v1.6.0 committed the consolidation) |
| 2 | `UFM.yaml` filename/id case defect | **Fixed** (renamed to `UfM.yaml`, commit `4f02209`) |
| 3 | Schema/export/docs contract drift; stale 1,070 counts | **Fixed** — `additionalProperties: false` at root, undeclared keys formalized, unused keys removed, `blocktypes.manifest.json` now emitted, all user-facing counts current |
| 4 | Intblock depth gaps (headquarters 54%, founded 26%, wikidata 22%, last_verified ~0%) | **Substantially improved** — now 31% / 11% / 10.5% / 33% missing respectively |
| 5 | Countries: gini/capital warnings, whitespace | **Fixed** — validator fully clean; capital policy documented |
| 6 | dataquality/ split-brain | **Mostly fixed** — `fresh_run/` gone; tracked reports one release behind (2026-07-30 vs 2026-08-01) |
| 7 | CI gaps (no drift check, no analyze-quality) | **Fixed** — artifact guard + quality gate (fails on CRITICAL/IMPORTANT) run on every PR |
| 8 | builder.py monolith | **Partially fixed** — now a 24-line shim, but `internacia_builder/build.py` is 2,035 lines and still contains the whole quality analyzer |
| 9 | Test coverage gaps (export equivalence, manifests) | **Fixed** — `test_export_equivalence.py`, `test_check_artifacts.py`; 264 tests total |
| — | Version 0.0.0 / entry points / .DS_Store / OpenSpec archive | **Fixed** — version 1.9.0, 4 console scripts, 33 changes archived (5 active, all with explicitly deferred tasks) |

---

## 1. Missing country data

Structure is essentially complete: `code`, `name`, `iso3code`, `numeric_code`, `wikidata_id`, `entity_type`, `code_status`, `population`, `area`, `centroid`, `native_names`, `common_names`, `provenance` are 100% populated; borders symmetry passes with zero asymmetric pairs; no `year: 0` values anywhere. Most remaining gaps are policy-expected (the 7 non-ISO entities, uninhabited territories, World Bank unclassified). The genuine gaps:

1. **Stale display names (highest visibility)**: `MK` = "Macedonia, FYR" (North Macedonia since 2019), `SZ` = "Swaziland" (Eswatini since 2018), `CV` = "Cape Verde" (WB: "Cabo Verde"), `TR` = "Turkey" (WB: "Türkiye"). Also review the ~15 comma-style names ("Korea, Rep.") for a documented display-name policy. `SZ`/`CV` additionally lack the modern short forms in `common_names`.
2. **`gini` missing on 86 records (33.6%)**, including 25 sovereign states — New Zealand is a clear miss (World Bank publishes a value); AD, BH, BN, KW, SA, SG have older estimates available. Five present values predate 2010 (TT 1992, GY 1998, TM 1998, AZ 2005, VE 2006) and should be refreshed.
3. **Kosovo (`KV`) is the thinnest widely-used entity** (22 fields, thinner than Transnistria): fillable — `official_name` ("Republic of Kosovo"), `currencies` (EUR), `calling_codes` (+383), `tld` (.xk reserved), `borders` (ALB/MNE/MKD/SRB), `subregion`, `demonyms`, `flag_emoji`.
4. **Wikidata-sourced `population`/`area` lack years on 39–40 territory records** (AI, FK, GG, …) — capture the point-in-time qualifier (P585) during enrichment instead of emitting `year: null`.
5. **`other_names` missing on CO, NI, PT** — three mainstream UN members without multilingual names while 246 other records have them.
6. **`parent_entity` is declared in the schema but used by zero records** — either populate (GL→DK, PR→US, HK/MO→CN, JG constituents) or remove from the schema.
7. Minor defects: currency-symbol whitespace in `LK` ("Rs  රු") and `PE` ("S/ "); `BV` has an empty `demonyms` struct (inconsistent with AQ/HM which omit it); `native_names` on the 6 special entities have ≤1 language vs the 6-language standard elsewhere.
8. **Freshness**: 98.9% of provenance is from a single 2026-06-15 pass (~7 weeks old — fine today, but there is no standing cadence enforcement; `docs/enrichment.md` defines a 12-month threshold that nothing validates).

## 2. Missing intergovernmental organizations

Coverage of classical IGOs is excellent — all major organizations spot-checked are present, and NATO/EU/ASEAN/AFUNION/OPEC rosters are internally consistent. Of ~78 significant organizations/treaties/formats checked, 55 are present and 24 absent. Seven absences are documented backlog decisions (EPC, D10, BRICS+ as separate record, WHO Pandemic Agreement, Global Gateway, PGII, Minerals Security Partnership). **Seventeen have never been triaged**, of which the ranked additions:

1. **Minamata Convention on Mercury** (`environment`) — the one hole in an otherwise complete chemicals/environment treaty set (Basel, Rotterdam, Stockholm, Montreal, Kyoto, Paris all present); ~150 parties with a clean UN Treaty Collection roster.
2. **Aarhus Convention** (~47 parties) and **Escazú Agreement** (LAC counterpart) — environmental-democracy treaties.
3. **Proliferation Security Initiative** (`armscontrol`) — 100+ endorsing states; every other counter-proliferation regime (Wassenaar, MTCR, AG, NSG, Zangger, GICNT) is already covered.
4. **Lancang-Mekong Cooperation** (`forum`) — six fixed members, standing secretariat and fund; passes the backlog's own "standing format" rubric.
5. **Three Seas Initiative** (`forum`) — 13 members plus an investment fund; high analytical demand.
6. **Bucharest Nine** (`political`) — nine fixed NATO members; also disambiguates from the existing `BUCHAREST` (Black Sea environment convention).
7. **Abraham Accords** (`agreement`) — defined signatories; Negev Forum as a linked follow-on.
8. **GCAP** (`military`) — treaty-based since the 2023 GIGO convention (UK/JP/IT).
9. **China-CEEC 14+1** (`forum`) — membership changes (Baltic exits) are exactly what this dataset tracks well.
10. **Micronesian Presidents' Summit** — completes the Pacific sub-regional trio with MSG and PLG (both present).
11. **PROSUR** (as `de-facto`/`historical` — the G5SAHEL precedent exists), **Lublin Triangle**, **Craiova Group**, **Blue Dot Network**; CANZUK arguably out of scope (proposal only).

Data-quality follow-ups in the same area:

- Resolve the **GLOBALGATEWAY/PGII backlog contradiction** (main table says deferred; Batch-1 triage says excluded).
- **Rename via the alias mechanism**: `ACP`→`OACPS` (renamed 2020), `IOR-ARC`→`IORA` (renamed 2013), `WIEMARTRIANGLE`→`WEIMARTRIANGLE` (typo).
- Re-verify **AFUNION at 54 members** (conventionally 55 — SADR omission should at least carry a note) and **OPEC at 11 vs 12**.
- Empty `tourism/` directory (still) and eight categories with ≤3 records (`agriculture` 1, `maritime` 1, `statistics` 1, `digital` 2, …) — populate or document the granularity policy.
- Ship **PANDEMICTREATY** once the party list stabilizes (deferred since June).

## 3. Repository readiness for LLM reuse

**~8/10 — genuinely best-in-class for cold-start agent consumption.** An agent landing on `llms.txt` can query correctly after one file read. Strengths: llms.txt/llms-full.txt/llms.zh.txt with join keys, gotchas, and scope negatives; self-describing artifacts (`_meta` table, manifests, sidecars, all carrying `data_license`); a 987-line query cookbook where every recipe is test-backed (English and Chinese); the id-alias map with reasons; thin platform shims for Claude/Copilot/Kimi/Lingma/Cursor; anti-pattern ("common mistakes") tables in three places; CI-enforced cross-format consistency.

Deductions and gaps:

1. **`llms.txt:29` makes a false claim** — "Each property includes a description field for agents and tooling", but `countries.schema.json` has descriptions on only ~4/40 top-level properties and `intblocks.schema.json` on 16/35. Preferred fix: backfill descriptions on every property (turns the schemas into a real data dictionary); otherwise delete the sentence. This is the only place the docs actively mislead an agent.
2. **Zero external discoverability**: no Hugging Face dataset card, no Croissant JSON-LD, no Frictionless `datapackage.json`, no Zenodo DOI. For LLM training/RAG pipelines that discover data through hubs, the dataset is invisible.
3. **No machine-readable release diff** (`diff-vX.Y.Z.json` as a release asset) — pipeline consumers get prose CHANGELOG only.
4. **API/MCP posture unstated**: `llms.txt` points to internacia-api but there is no hosted instance and no statement of intent; a one-liner ("no hosted API; use local DuckDB or self-host") would stop agents hunting for an endpoint. An MCP server wrapping the DuckDB file would be a natural, cheap addition.
5. **No generated data-dictionary page** — field semantics live in `ai-consumers.md` prose covering ~15 of 40+35 properties.

## 4. General repository, code and data quality

**Engineering: healthy and much improved.** 264 tests pass; ruff clean; pyproject at 1.9.0 with four console entry points; dependencies pinned with Dependabot; 33 OpenSpec changes archived with 5 active (all remaining tasks explicitly deferred, two of which are effectively "decided-not-doing" and could be closed). CI on every PR: ruff → pytest → both validators → link check → artifact drift guard → build → baseline diff → quality analyzer with CRITICAL/IMPORTANT fail gate.

Remaining engineering debt, in priority order:

1. **`internacia_builder/build.py` is a 2,035-line module** mixing Arrow schemas, cleaning, export writers, manifests, CLI, and the entire ~900-line quality analyzer. Split into `schemas.py` / `clean.py` / `export.py` / `manifest.py` / `quality_report.py`.
2. **The quality analyzer duplicates rules that live in `internacia_builder.validate.*`** (borders, indicators, references) — two copies will drift; the dedup task is deferred in `refactor-builder-into-package`.
3. **Tests still reach code via `sys.path` hacks** in `conftest.py` and `import builder` through a wildcard-re-export shim; install the package in CI (`pip install -e .`) and import `internacia_builder` directly.
4. **`release.yml` does not run pytest or ruff** before building release assets — a broken suite would not block a tagged release.
5. Single Python version in CI (3.11) despite `requires-python >=3.11`; no `pip-audit`; `apply_manus_roadmap.py` still uses raw urllib (last unchecked task of `refactor-scripts-package`); nested `additionalProperties: true` remains in both schemas; ruff rule set is modest (consider `SIM`, `C4`, `RUF`, and mypy — the code is already consistently annotated); tracked `dataquality/` reports are one release stale again (either wire the deferred freshness check or stop tracking them, since CI produces the authoritative artifact).

**Data quality: the 167 intblock warnings are the real backlog.**

1. **89 `membership_count` mismatches** split into two populations that need different treatment: (a) genuine roster drift on state-membership IGOs (MTCR 35 vs 39, CTBTO 187 vs 195, MERCOSUR 5 vs 6, IFC 186 vs 195) — reconcile against official rosters; (b) organizations whose count includes non-state/corporate members (AIIB 111, WNA 3000, IGA 10000, GEIDCO 1346, WEF 1000) where the number can never match country `includes` — add a schema escape hatch (e.g. `membership_count_scope: organizations|countries`) so the check distinguishes them.
2. **46 provenance-depth and 22 missing-includes warnings cluster in classification categories** (`dvdregion`, `govform`, `lawsystem`, `railgauge`, `teleregion`, `traffichand`, `travel`, `writingsystem`) where 4-source provenance and membership rosters arguably don't apply — carve out a per-category or per-blocktype exemption instead of leaving permanent warning noise.
3. **`legal_status` is uncontrolled free text**: 120+ distinct values with near-duplicates ("intergovernmental" ×390 vs "intergovernmental organisation" ×3 vs "intergovernmental organization" ×10). Introduce a controlled vocabulary plus an optional free-text detail field.
4. **`last_verified` missing on 33%** of intblocks — big improvement from ~100%, but finish the campaign and add a staleness warning.
5. Five shared-acronym pairs (COL, IAF, ABCANZ, ABCA, G5) to disambiguate or allowlist.

## 5. Documentation quality and gaps

All core consumer docs are fresh at 256/1078/86 and v1.9.0, and all 169 internal links pass. `docs/ai-consumers.md`, `AGENTS.md`, the CHANGELOG discipline, and the test-backed cookbook are exemplary. The problems are concentrated in planning docs and conventions:

1. **`docs/improvement-plan.md` (claims v1.2.0 current) and `docs/strategy-and-user-needs.md` (claims v1.3.0)** are ~7 releases stale and now misstate reality (strategy §4.3 says the `_meta` table doesn't exist; it shipped). Their own "next review" dates are September 2026. Re-baseline both to v1.9.0 marking shipped items, or move them to `dev/docs/` with a historical banner.
2. **Active OpenSpec proposal `enrich-intblock-profile-depth` cites 1,071-era numbers** and a `last_verified` premise that the v1.8.0 campaign has partially overtaken — re-measure before implementing.
3. **Undocumented conventions** that force contributors to guess: category-directory granularity and its relation to `blocktype` (root cause of the July `space/` warnings); intblock `id` naming scheme (`INTTRASPORTFORUM`, `BLASMBL`, `FATFGREYLIST` follow no stated rule); versioning policy (what bumps minor vs major; what a `schema_hash` change guarantees); `membership_count` vs `len(includes)` semantics; intblock freshness SLA (countries have one in `docs/enrichment.md`; intblocks don't).
4. **Schema `description` fields are sparse** (see §3.1) — the highest-leverage single documentation fix.
5. **Add a docs-count CI guard**: assert that counts in README/llms\*.txt/AGENTS\* match manifest `row_count`, ending the recurring 1,070→1,071→1,076→1,078 doc-chasing.
6. **Chinese coverage is real and test-backed** but uneven: the zh cookbook is ~10% of the English one, and `ai-consumers.md` (the consumption contract, where agents actually land) has no zh version.
7. Very old `dev/docs/` analyses ("737 intblocks + 252 countries") need a historical-snapshot banner.

## 6. Usage scenarios by user type

| User type | Scenario | What serves them today | What's missing |
|---|---|---|---|
| **Search/enrichment pipeline** (Dateno — primary consumer) | Entity linking, membership expansion, geo enrichment | Stable ids + alias map, multilingual names, 90% wikidata coverage, DuckDB/Parquet | Machine-readable release diffs; remaining 113 wikidata ids; richer alias/translation coverage for fuzzy recall |
| **LLM agents / RAG builders** | Cold-start querying, joining, fact grounding | llms.txt, test-backed cookbook, self-describing DB, platform shims | Schema descriptions, MCP server, hub presence (HF/Croissant), embeddings for name matching |
| **Data engineers / SDK users** (internacia-python) | Versioned offline reference DB in pipelines | `_meta` table, manifests, pinned releases, semver + migration notes | Release-diff artifact; documented versioning policy; Python version matrix in CI |
| **Analysts / researchers** (IR, political science, trade) | Membership-over-time studies, org density, treaty participation | `includes[].joined/left/status`, historical orgs, former members, verified queries | Citable DOI; data dictionary; broader `founded`/`dissolved` completeness; the 17 untriaged formats (minilateralism research needs Three Seas/B9/LMC-class records) |
| **Journalists / OSINT** | "Who is in what" lookups, sanctions/FATF context | FATF grey/black lists, visa-free blocks, acronym disambiguation | Hosted API or lightweight web explorer; common-name lookup for non-obvious ids (AFUNION, IBRD, ICW) |
| **Compliance / risk teams** | Jurisdiction classification (FATF, treaty adherence, income level) | FATF lists, WB classifications, `code_status` policy | Freshness SLA/`last_verified` completion — compliance uses need to know how current a roster is |
| **GIS-light applications** | Mapping membership, border analysis | Centroids (100%), capitals with coords, borders alpha-3 | Bounding boxes (strategy E1, still open); no country outlines by design |
| **Educators / app builders** | Quizzes, country pickers, reference apps | Flags, demonyms, calling codes, TLDs, currencies, week start | Hosted API; a small JS-friendly JSON export could widen this audience |
| **Contributors** | Adding/fixing records | CONTRIBUTING, agent workflows, validators with fix hints | Category/id conventions doc; a worked "add an intblock" example; issue templates for data-error reports (strategy E2, still open) |

## 7. Project architecture and future development

**Architecture verdict**: the data-as-code pipeline (YAML → validators → builder → multi-format artifacts, all guarded in CI) is sound, proven by three months of incident-free releases (v1.5→v1.9), and does not need structural change. The 2026-06 strategy's Tracks A (consumer contract) and B (enrichment value) are essentially shipped; **Tracks C (distribution) and D (API posture) are the open frontier**, plus the deferred internal refactor.

Recommended development sequence:

**Now (data integrity, days):**
1. Burn down the 89 membership_count mismatches (reconcile the genuine ones; add `membership_count_scope` for corporate-membership orgs) and exempt classification categories from provenance/includes checks — target: 0 warnings, then make warnings a CI gate.
2. Fix stale country display names (MK/SZ/CV/TR) and the small defects (LK/PE whitespace, BV demonyms, CO/NI/PT other_names).
3. Fix `llms.txt` schema claim; add the docs-count CI guard; refresh or archive the two June planning docs and the stale OpenSpec proposal.

**Next (coverage & contract, 1–3 weeks):**
4. Triage the 17 undocumented absent organizations through the backlog rubric; add the top tier (Minamata, Aarhus, Escazú, PSI, LMC, 3SI, B9, Abraham Accords); resolve GLOBALGATEWAY/PGII contradiction; execute the ACP→OACPS, IOR-ARC→IORA, WIEMARTRIANGLE renames through the alias mechanism.
5. Backfill JSON Schema property descriptions and generate a data-dictionary page from them.
6. Ship the machine-readable release diff (`diff-vX.Y.Z.json`) — the last unshipped Track-A item.
7. Kosovo record completion; gini backfill (NZ first); Wikidata year qualifiers; decide `parent_entity`.

**Then (distribution & reach, 3–8 weeks):**
8. Track C: Frictionless `datapackage.json` + Croissant JSON-LD generated at build time; Hugging Face dataset card; Zenodo DOI. This is the highest-leverage unshipped strategy work — it makes the dataset discoverable to exactly the LLM/data-hub audience the project targets.
9. Decide API posture (D1): either host a minimal read-only instance or state "self-host only" everywhere; consider an MCP server over the DuckDB file as the modern agent-facing alternative to REST.
10. Controlled vocabulary for `legal_status`; finish `last_verified` backfill and add staleness warnings; `country legal name` policy doc.

**Ongoing (engineering hygiene):**
11. Split `build.py`; dedupe quality-analyzer rules against `validate.*`; drop `sys.path` test hacks; add pytest+ruff to `release.yml`; Python 3.12/3.13 matrix; migrate `apply_manus_roadmap.py` to the shared HTTP client; archive the two effectively-closed OpenSpec changes.
12. Establish the enrichment cadence as automation: the monthly `enrichment-check.yml` exists — make its report actionable (open an issue on staleness) so the 2026-06-15 provenance corpus doesn't silently age past the documented 12-month threshold.

## Strengths to preserve

- Source-of-truth pipeline with self-describing, cross-format-consistent artifacts, now guarded end-to-end in CI (drift check + quality gate + baseline diff).
- Zero-error validation posture on both datasets and a countries dataset with 100% core-field completeness and symmetric borders.
- Test-backed documentation: every published query recipe (English and Chinese) is executed in CI — rare and valuable.
- Disciplined governance: OpenSpec flow with 33 archived changes, Keep-a-Changelog with migration notes, id-alias map with reasons, research-driven backlog with an explicit triage rubric.
- Genuinely strong multi-platform agent support (llms.txt family, AGENTS routing hub, five platform shims, bilingual coverage).

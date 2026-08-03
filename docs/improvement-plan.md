# Internacia-db Improvement Plan

> **Status: HISTORICAL (2026-08-02).** This plan was written against **v1.2.0** and most of it has
> shipped: intblock schema validation + completeness gates + provenance requirements, pytest test
> suite, pinned dependencies, the `internacia_builder` package refactor, DuckDB export fixes, CI
> enforcement, and the release manifest pipeline are all in place as of v1.9.x. Kept for historical
> context; do not treat the gap analysis below as current. Open work is tracked in
> `openspec/changes/`.

> **Generated:** 2026-06-12 (independent repository analysis)
> **Repository:** internacia-db — reference datasets of countries, intergovernmental organizations, and country groups
> **Current release at time of writing:** v1.2.0 (2026-05-29)
> **Consumers:** Dateno search engine, [internacia-api](https://github.com/datenoio/internacia-api), [internacia-python](https://github.com/datenoio/internacia-python)

This document is a prioritized improvement plan across **features**, **code quality**, and **product quality**, based on a full review of the data layer (1,317 source YAML files), all nine build/validation scripts (~3,070 lines of Python), CI configuration, and project governance. It is intended for periodic review.

---

## Executive Summary

Internacia-db is a mature data-as-code repository with a strong **countries** quality pipeline: JSON Schema validation, completeness gates with per-field null-rate thresholds, field-level provenance, entity status policy, release manifest with schema hash, and CI enforcement on every PR. The countries dataset (256 records) is in good shape — 100% provenance and wikidata coverage, enforced population/area/timezone completeness.

The **intblocks** dataset (1,065 records, 4x larger than countries) has none of that governance: its JSON schema exists but is enforced nowhere, 40% of records lack `wikidata_id`, 38% have boilerplate descriptions, no record has provenance, and the schema itself has drifted from the data (invalid enum values are in active use). On the engineering side there are **no tests at all**, dependencies are unpinned, and the central `builder.py` contains a likely-broken DuckDB export path that CI never exercises.

Top five priorities, in order:

1. **Fix the silent-failure paths in the build** — DuckDB export bug, builds that continue after YAML load errors, validation report that omits cross-reference findings.
2. **Bring intblocks to validation parity with countries** — validator script, completeness config, manifest, CI step.
3. **Add a pytest suite** — the build pipeline guards two downstream consumers and has zero test coverage.
4. **Pin dependencies** — 9 unpinned packages; one upstream pandas/pyarrow release can break every build.
5. **Fix the identified data errors** — `AN.yaml` and `JG.yaml` carry wrong names from bad imports; 72 `year: 0` values in country profile fields.

---

## 1. Current State Assessment

### 1.1 Strengths

- **Multi-format export pipeline** — JSONL.zst, YAML.zst, Parquet (explicit PyArrow schemas), DuckDB from a single `scripts/builder.py` entry point.
- **Countries quality gates** — `scripts/validate_countries.py` enforces `data/schemas/countries.schema.json`, duplicate detection, ISO format checks, and `data/schemas/countries_completeness.yaml` thresholds (population/area/timezones/native_names at 0% null, gini warn at 45%).
- **Provenance and enrichment** — World Bank, Wikidata, and IANA tzdata enrichment with field-level `provenance` entries; 256/256 countries have provenance and `wikidata_id`.
- **Release traceability** — `countries.manifest.json` with version, commit, row count, schema hash; `diff_countries_baseline.py` compares against the main-branch baseline in CI.
- **Working CI** — `.github/workflows/validate.yml` runs validation, a Parquet build, baseline diff, and an include-name audit on every relevant PR.
- **Documented entity policy** — `docs/country-code-policy.md` cleanly explains the 249 + 7 non-standard codes (`AN`, `JG`, `XK`, `XA`, `XS`, `XT`, `XN`) and filtering recipes.
- **Research-driven growth** — gap analyses under `dev/research/` drove the 1,021 → 1,065 intblocks expansion with a documented merge process.

### 1.2 Dataset scale

| Dataset | Records | Source path | Governance |
|---------|--------:|-------------|------------|
| Countries | 256 | `data/countries/*.yaml` | Schema + completeness + CI + manifest |
| Intblocks | 1,037 (54 categories) | `data/intblocks/**/*.yaml` | Schema + completeness + CI + manifest |
| Blocktypes | 78 | `data/blocktypes/blocktypes.yaml` | Taxonomy source; copied to output on build |

### 1.3 Verified defects (found during this analysis)

**Code defects**

1. **DuckDB export is likely broken** — `scripts/builder.py` (lines ~558–569) creates PyArrow tables as Python variables and then runs `CREATE TABLE countries AS SELECT * FROM countries_table` without registering them with the DuckDB connection. CI only runs `--formats parquet`, so this path is never exercised. The committed `internacia.duckdb` may have been produced by an older code path.
2. **Builds continue after YAML load failures** — `load_yaml_files` in `builder.py` (lines ~486–495) logs parse errors and proceeds; a dataset can silently ship with missing records.
3. **Validation report is incomplete** — `validate_countries.py` writes the `--report` JSON (lines ~345–362) *before* running intblock cross-reference checks, so those findings never appear in the CI artifact.
4. **WHO-membership fallback** — `fill_includes_agreement_intorg.py` (lines ~268–270) copies WHO's member list into unrelated organizations as a fallback, a direct data-correctness risk.
5. **Missing `encoding="utf-8"`** on file I/O in `enrich_gap_records.py` (lines 517, 526) and `fill_includes_agreement_intorg.py` (lines 154, 189, 280, 293).
6. **Dead code** — unused `NON_ISO_CODES` (`annotate_entity_status.py:17`), unused `file_errors` and unreachable `return` (`validate_links.py:303, 345`), unused imports (`validate_links.py:10`, `diff_countries_baseline.py:8`).

**Data defects**

7. **`data/countries/AN.yaml`** (Netherlands Antilles, obsolete) — `native_names.en.official` says "Anguilla" and `common_names` includes "Anguilla"; copy-paste bleed from the AI code.
8. **`data/countries/JG.yaml`** (Channel Islands grouping) — `native_names` and `common_names` reference "Urdoma", an unrelated Wikidata entity; bad import.
9. **72 occurrences of `year: 0`** in country `population`/`area` structs (mostly Wikidata-sourced records such as AN, XK) — consumers filtering by year will get garbage.
10. **Intblocks schema/data drift** — `data/schemas/intblocks.schema.json` allows `status: formal|informal|de-facto` but 4 records use `historical` (GATT, CENTO, SEATO, WARSAWPACT); the `includes[].status` enum allows 4 values but 18+ are in use (`former_member`, `founding_member`, `recipient`, `participant`, ...); end-of-life is expressed three ways (`dissolved` × 8, `ended` × 1, `active_period` × 1).

**Governance drift**

11. Four completed OpenSpec changes (`add-countries-validation`, `fill-countries-core-fields`, `add-countries-entity-status`, `add-countries-release-governance`) sit unarchived; `openspec/specs/` is empty.
12. `openspec/project.md` is stale: claims "1021+ organizations across 53+ categories" (actual: 1,065 across 51) and describes `validate_links.py` as the primary testing strategy.
13. README references a typo filename `countries_gaps_manus_20260528.md` and omits `enrich_gap_records.py` / `fill_includes_agreement_intorg.py` from its scripts table; no CI badge.
14. `data/_legacy/` holds 5 Airtable-era JSON dumps referenced by nothing.

---

## 2. Feature Improvements

### 2.1 Intblocks quality pipeline (High)

The single biggest feature gap. Bring intblocks to parity with countries:

- **`scripts/validate_intblocks.py`** enforcing `data/schemas/intblocks.schema.json`, wired into CI and `builder.py` (currently intblocks are exported with zero pre-export validation).
- **Reconcile schema with data first** — decide whether `historical` status and the 18+ `includes[].status` values are legitimate (then widen the enums) or data errors (then fix records). Standardize end-of-life on `dissolved` + `status: historical`; migrate the single `ended` (GATT) and `active_period` usages.
- **`data/schemas/intblocks_completeness.yaml`** — initial thresholds informed by measured baselines: `wikidata_id` 40% missing, `includes` 8% missing, `links` 4.5% missing. Start with warn gates at current levels and ratchet down.
- **`intblocks.manifest.json`** written by the builder, mirroring the countries manifest, plus baseline diff support in `diff_countries_baseline.py` (or a generalized version).
- **Cross-dataset checks** — every `blocktype` value exists in the blocktypes taxonomy; `partof` references resolve to existing intblock IDs; `includes[].id` country references resolve (already warn-only — keep, but include in the report).

### 2.2 Intblocks content enrichment (Medium)

- **Wikidata backfill** — 424 records lack `wikidata_id`, including major organizations (NATO has a wikidata link but no top-level ID). Extend `enrich_countries.py` patterns to intblocks, with provenance.
- **Description quality** — 406 records (38%) have templated descriptions ("International entity focused on..."). Source real descriptions from Wikidata/Wikipedia with provenance; track via a completeness metric.
- **Membership completeness** — 82 records lack `includes`; many are legitimately conceptual (acronyms, govform), so add an explicit marker (e.g. `membership: not_applicable`) to distinguish "no members" from "not yet researched". `dev/research/intblocks_missing_includes_20260528.txt` is the starting backlog.
- **Provenance for intblocks** — 0/1,065 records have any provenance today. Introduce on enriched fields first rather than retroactively everywhere.

### 2.3 Countries data fixes and policy decisions (Medium)

- Fix `AN.yaml` and `JG.yaml` name errors (defects 7–8 above).
- Replace `year: 0` with either a real year or omit the field; add a validator rule rejecting `year: 0`.
- **Resolve CIS2 deferred entities** — `XA`, `XS`, `XT`, `XN` referenced in `data/intblocks/political/CIS2.yaml` with no country records. Pick one of the three policies in `docs/country-code-policy.md`; explicit modeling (user-assigned profiles with `recognition_status`, or a typed allowlist) beats the current indefinite warn-only state.
- **Enrichment refresh cadence** — provenance shows `retrieved_at: 2026-05-29`; define a refresh schedule (e.g. quarterly `enrich_countries.py` run) so World Bank data does not silently age.

### 2.4 Blocktypes as first-class source (Low–Medium)

`data/datasets/blocktypes.yaml` is hand-edited source living in the generated-output directory, and is both input and output of the build. Move it to `data/blocktypes/` (or `data/schemas/`), treat `data/datasets/` as generated-only, and add a small taxonomy validation (unique keys, required name/description).

### 2.5 Link and Wikidata health (Medium)

`scripts/validate_links.py` exists but runs only manually (network-dependent). Add a **scheduled weekly workflow** on `main` producing a report artifact, non-blocking for PRs; optionally make it a release gate. Also fix its two correctness gaps: Wikidata URLs currently bypass HTTP checking entirely, and API errors are swallowed without logging.

### 2.6 Release distribution (Medium)

~5 MB of generated binaries (`.parquet`, `.zst`, `.duckdb`) are committed to git with no tagged-release mechanism. Add a release workflow on `v*` tags that rebuilds all formats and attaches them as GitHub Release assets. Keep manifests in git for diffability; decide (and document) whether binaries stay in-repo for cloning convenience or move to releases-only.

---

## 3. Code Quality Improvements

### 3.1 Testing foundation (High)

No `tests/` directory, no pytest, no test step in CI. Highest-value targets, in order of testability:

1. `validate_countries.py` — schema pass/fail, duplicate detection, completeness warn/error thresholds (pure functions, fixture YAML).
2. `builder.py clean_data()` — the ~225-line normalization function (bool→"yes"/"no", `partof`, indicator structs) is the riskiest pure logic in the repo.
3. Manifest generation — `schema_hash` stability, required fields.
4. Cross-dataset include resolution with the deferred-ID allowlist.
5. End-to-end smoke: build a fixture dataset, assert Parquet row counts and **a working DuckDB export** (this would have caught defect 1).

Suggested layout: `tests/{test_validate_countries,test_clean_data,test_builder_export,test_manifest}.py` + `tests/fixtures/` with minimal country/intblock YAML.

### 3.2 Fix the silent-failure paths (High)

- Register PyArrow tables with the DuckDB connection (or insert via `con.from_arrow`) and cover with a test.
- Make `load_yaml_files` fail the build (or require `--allow-load-errors`) when any source YAML fails to parse.
- Move the `--report` write in `validate_countries.py` after cross-reference checks.
- Remove the WHO-membership fallback in `fill_includes_agreement_intorg.py` or gate it behind an explicit per-record opt-in.

### 3.3 Dependency governance (High)

- Pin all 9 packages in `requirements.txt` (or migrate to `pyproject.toml` + a lockfile such as `uv.lock`).
- Add `.github/dependabot.yml` for pip and GitHub Actions.
- Add pip caching to CI (`actions/setup-python` `cache: pip`).

### 3.4 Consolidate into a package (Medium)

The nine flat scripts share copy-pasted logic with no importable structure:

- Project-root resolution implemented 8 different times (and `validate_links.py` is CWD-relative, unlike all peers).
- Country code→name loading duplicated in 3 scripts; non-ISO policy constants duplicated between `validate_countries.py` and `annotate_entity_status.py` (drift risk).
- Two HTTP stacks (`requests` in `validate_links.py`, `urllib.request` in enrichment scripts) hitting the same Wikidata endpoints with separately-defined rate limits.
- `builder.py` runs validation via `subprocess` instead of an import, with default flags only.

Target: a small `internacia/` package (paths, YAML I/O, policy constants, one HTTP client with retry/backoff, validators) with thin Typer CLI shims. Keep it flat; don't over-abstract.

### 3.5 Tooling and consistency (Medium)

- Add **ruff** (lint + format) and a **pre-commit** config; this immediately flags the dead code and unused imports listed in §1.3.
- Add `from __future__ import annotations` and modern `list`/`dict` annotations to `builder.py` and `validate_links.py` (newer scripts already do this).
- Standardize on `encoding="utf-8"` everywhere (two scripts omit it).
- Give `enrich_gap_records.py` and `fill_includes_agreement_intorg.py` Typer CLIs with `--dry-run`, or move them to `dev/scripts/` as archived one-off migrations.
- Adopt a consistent exit-code convention (0 pass, 1 error, 2 warn-only pass) and document it.

---

## 4. Product Quality Improvements

### 4.1 Quality parity matrix

| Dimension | Countries | Intblocks | Action |
|-----------|-----------|-----------|--------|
| Schema conformance in CI | Yes | No | §2.1 validator |
| Completeness gates | Yes | No | §2.1 completeness config |
| Provenance | 100% | 0% | §2.2 enrichment-first |
| Manifest / baseline diff | Yes | No | §2.1 manifest |
| Entity/status taxonomy | Documented policy | Enum drift | §2.1 reconciliation |
| External link health | n/a | Manual only | §2.5 scheduled workflow |

### 4.2 Consumer experience

- **CONTRIBUTING.md** — YAML authoring guide, how to run validation locally, PR checklist (currently a contributor has no guidance at all).
- **CI badge** in README; fix the typo filename reference; add the two missing scripts to the README table.
- **Filter recipes** — extend `docs/country-code-policy.md` with common queries (UN members, EU members via intblocks join, current-ISO-only).
- **Schema-diff notes per release** — the manifest already carries `schema_hash`; document field-level changes in CHANGELOG whenever it changes (done well for v1.2.0; make it a release checklist item).
- Clarify or delete `data/_legacy/`.

### 4.3 Governance hygiene

- Archive the four completed OpenSpec changes and populate `openspec/specs/` so specs become canonical truth (the `archive-completed-openspec-changes` change already exists for this).
- Update `openspec/project.md`: record counts, current validation strategy, testing approach.
- Keep using `dev/research/` gap reports, but add review dates to the "Still Deferred" backlog (EPC, D10, BRICSPLUS, G5SAHEL-style historical records, PANDEMICTREATY sourcing, P2 verification items).

---

## 5. Prioritized Roadmap

### Phase 0 — Correctness and quick wins (days)

- [ ] Fix DuckDB export registration bug in `builder.py`; verify `--formats duckdb` locally
- [ ] Make YAML load failures fatal in `builder.py`
- [ ] Move report writing after cross-ref checks in `validate_countries.py`
- [ ] Fix `AN.yaml` / `JG.yaml` name errors; clean `year: 0` values
- [ ] Pin `requirements.txt`; add pip cache to CI
- [ ] Fix README typo and scripts table; add CI badge
- [ ] Archive completed OpenSpec changes; update `openspec/project.md`

### Phase 1 — Foundation (1–2 weeks)

- [ ] `tests/` with pytest covering validation, `clean_data`, manifest, DuckDB export; add CI step
- [ ] ruff + pre-commit; remove dead code; fix encoding gaps
- [ ] Reconcile `intblocks.schema.json` enums with data; standardize `dissolved`/`historical`
- [ ] `scripts/validate_intblocks.py` + CI step
- [ ] `intblocks_completeness.yaml` with warn-level baselines
- [ ] CONTRIBUTING.md

### Phase 2 — Intblocks parity (2–4 weeks)

- [ ] `intblocks.manifest.json` + baseline diff
- [ ] Wikidata ID backfill (424 records) with provenance
- [ ] Description quality campaign (406 templated records), measurable via completeness gate
- [ ] `membership: not_applicable` marker; triage the 82 no-`includes` records
- [ ] Resolve CIS2 deferred entity policy (`XA`/`XS`/`XT`/`XN`)

### Phase 3 — Operations (2–3 weeks)

- [ ] Scheduled weekly link/Wikidata validation workflow (fix `validate_links.py` gaps first)
- [ ] GitHub Releases workflow on `v*` tags with dataset assets
- [ ] Dependabot
- [ ] Enrichment refresh runbook and cadence

### Phase 4 — Architecture (optional)

- [ ] Refactor scripts into an `internacia/` package; drop subprocess validation
- [ ] Single HTTP client with retry/backoff
- [ ] Move blocktypes source out of `data/datasets/`
- [ ] Retire or relocate one-off migration scripts

---

## 6. Success Metrics

| Metric | Baseline (2026-06-12) | Target |
|--------|----------------------|--------|
| Automated tests | 0 | ≥ 30, in CI |
| DuckDB export verified | Never (not in CI) | Every build via test |
| Pinned dependencies | 0/9 | 9/9 |
| Intblocks schema enforcement | 0% | 100% in CI |
| Intblocks with `wikidata_id` | 60% (641/1,065) | ≥ 90% |
| Intblocks with non-templated description | 62% (659/1,065) | ≥ 85% |
| Intblocks with `includes` or explicit n/a marker | 92% | 100% |
| Known country data errors (AN, JG, `year: 0`) | 2 records + 72 values | 0, with validator rule |
| OpenSpec completed changes archived | 0/4 | 4/4; `openspec/specs/` populated |
| Link validation cadence | Manual | Weekly automated report |

---

## 7. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Unpinned deps break builds silently | High | Phase 0 pinning + Dependabot |
| DuckDB artifact shipped broken/stale | High | Phase 0 fix + Phase 1 test |
| Intblocks edits regress without validation | High | Phase 1 validator before any large backfill |
| Schema enum-widening breaks consumers | Medium | Manifest `schema_hash` + CHANGELOG migration notes |
| Wikidata/World Bank rate limits during backfill | Medium | Shared client with retry/backoff; batch runs |
| Description backfill introduces unsourced text | Medium | Require provenance on every enriched field |
| Scope creep (GeoJSON, history arrays) | Low | Defer until intblocks parity is reached |

---

## 8. References

| Resource | Path |
|----------|------|
| CI workflow | `.github/workflows/validate.yml` |
| Countries schema / completeness | `data/schemas/countries.schema.json`, `data/schemas/countries_completeness.yaml` |
| Intblocks schema (unenforced) | `data/schemas/intblocks.schema.json` |
| Entity code policy | `docs/country-code-policy.md` |
| Build manifest | `data/datasets/countries.manifest.json` |
| Gap research | `dev/research/gaps_merged_20260528.md`, `dev/research/intblocks_missing_includes_20260528.txt` |
| OpenSpec changes | `openspec/changes/` (17 active; 4 completed-unarchived) |

---

## Review Log

| Date | Notes |
|------|-------|
| 2026-06-12 | Fresh independent analysis; supersedes prior plan version. Verified defects listed in §1.3 with file/line references. |

*Next review: after Phase 1 completion or 2026-09-12, whichever comes first.*

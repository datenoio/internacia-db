# Deep Review: `datenoio/internacia-db`

**Repository:** https://github.com/datenoio/internacia-db
**Reviewed state:** v1.9.0 (2026-08-01, commit `e228586`)
**Review date:** 2026-08-03
**Scope:** 256 country records, 1,078 intblocks (IGOs, country groups, agreements) in 62 categories, 86 blocktypes; multi-format exports (JSONL/YAML/Parquet/DuckDB, zstd-22); Python build/validation package; 15 test files; 4 CI workflows; extensive agent-facing documentation.

**Method:** Four parallel independent audits — (1) data completeness with programmatic scans of all 1,334 YAML records plus web verification against official sources (opec.org, au.int, interpol.int, FAO/WHO); (2) code & data quality with full test-suite execution and export re-computation; (3) LLM-reuse readiness with execution of documented queries; (4) documentation & architecture with claim-by-claim verification. Every number below was independently recomputed.

---

## Executive summary

**This is an unusually well-governed open data repository** — far above the typical "CSV in a git repo" standard. It has schema validation, completeness gates, a 62-rule quality analyzer, field-level provenance, a frozen build identity across all export formats, an alias map for ID stability, spec-driven development (OpenSpec), and agent-facing docs whose example queries are backed by real tests. Country coverage is complete (all 249 official ISO 3166-1 codes + 7 documented non-standard codes). Headline IGOs are essentially all present with verified-correct rosters (UN=193, NATO=32, EU=27, WTO=166, ASEAN=11).

The problems found are specific, fixable, and concentrated in four areas:

1. **A handful of verified factual roster errors** (OPEC missing UAE, African Union missing SADR, Interpol's list is wrong, CIS membership statuses stale) and systematic `membership_count` semantic drift (89+ records).
2. **Broken org identity** — the README badge and ~15 files link to `commondataio/*` repos that don't exist there; everything lives under `datenoio`. The project's front door 404s.
3. **Three false documented claims that will burn LLM agents** — a WB-region query example returning 0 rows, pandas `.struct.field()` examples that crash with default pandas, and a wrong "~33 missing classifications" figure — plus an ODbL attribution gap (mledoze/countries) in a CC-BY-4.0 dataset.
4. **Doc/process drift** — two stale planning docs presenting shipped work as open gaps, an "extended" `llms-full.txt` that is smaller than `llms.txt`, and 3 implemented-but-unarchived OpenSpec changes.

### Scorecard

| Dimension | Score | One-line verdict |
|---|---|---|
| Country data completeness | ★★★★★ | 249/249 ISO codes; gaps are peripheral (gini 66%, Somaliland/TRNC policy) |
| IGO completeness | ★★★★☆ | All headline orgs present; Codex, BCBS, CJEU, WADA missing; `court/` thin |
| Data factual accuracy | ★★★★☆ | Mostly excellent, but OPEC/AU/Interpol/CIS rosters need fixes |
| Code quality | ★★★★☆ | Strong package + shared rule engine; 2,035-line build.py monolith remains |
| Export integrity | ★★★★★ | Byte-consistent across 5 formats; verified independently |
| Tests & CI | ★★★★☆ | 62 quality rules in CI; 4 documented queries OOM-crash; no coverage tracking |
| LLM readiness | ★★★★☆ | Best-in-class agent docs, but 3 false examples + ODbL attribution gap |
| Documentation | ★★★★☆ | ai-consumers.md is excellent; badge/links broken; 2 planning docs stale |
| Architecture | ★★★★☆ | Sound pipeline; roster denormalization is the scaling pain point |

---

## 1. Missing country data

### 1.1 Coverage is complete at the ISO level — no missing codes

- **All 249 officially assigned ISO 3166-1 alpha-2 codes are present.** Zero gaps (verified programmatically).
- **All 7 non-standard records are present and accurately documented** in `docs/country-code-policy.md`: `AN` (obsolete, Netherlands Antilles), `JG` (Channel Islands grouping), `KV` (Kosovo), `XA`/`XS`/`XT`/`XN` (Abkhazia, South Ossetia, Transnistria, Artsakh — with `recognition_status` notes; XN correctly marked `historical_entity` after 2023 dissolution).
- **UN membership is exactly right:** 193 `un_member: true` after the v1.9.0 Guinea-Bissau fix; Vatican City is correctly the sole independent non-member.

### 1.2 Actual gaps and inconsistencies

| Gap | Detail | Suggestion |
|---|---|---|
| **Disputed-territory threshold is inconsistent** | Somaliland (30+ years de facto autonomy) and Northern Cyprus are absent, while less-recognized Abkhazia/South Ossetia/Transnistria are included | Add user-assigned records (e.g. `XL`, `XC`) **or** document the exclusion rule in `country-code-policy.md` |
| **No UN observer status** | `VA` and `PS` are just `un_member: false` — "193 + 2 observers" is not representable | Add `un_status: member/observer/non-member` field |
| **Missing explicit values on 7 non-standard codes** | `un_member`, `independent`, `landlocked` absent rather than `false`; `KV` lacks `un_member` entirely | Set explicit values; absence is ambiguous to consumers |
| **`gini` only 66% filled** (86 nulls) | Missing for NZ, SG, SA, KW, HK, MO, OM, TW — several fillable from World Bank/national stats | Backfill the ~10 major-economy cases; document why the rest are null |
| **`adminregion` missing for ~39 entities** | Includes US, GB, DE, FR, JP, CA, AU… (major economies) | Backfill or drop the field — current state reads as arbitrary |
| **Missing `year` on populations** | KV, XA, XN, XS, XT population entries lack `year` (Wikidata-sourced) | Add retrieval year |
| **JG double-count trap** | Channel Islands aggregate population ≠ GG+JE sum; consumers summing double-count | Note in policy doc |
| Minor: exceptionally reserved codes (`EU`, `EZ`, `UN`) unmentioned | Fine to exclude from countries, but `economic/EU.yaml` exists as an intblock | One-line note in policy doc |

### 1.3 Field fill-rate summary (n=256)

Core identity fields (`code`, `name`, `iso3code`, `numeric_code`, `area`, `population`, `centroid`, `wikidata_id`, `provenance`, names) are at **100%** — enforced by CI gates. `capital_city` 98% (only documented exclusions: AQ/BV/HM uninhabited, JG grouping, XN dissolved). `borders` 64% — legitimately empty for island nations. The weak fields are `gini` (66%), `adminregion` (85%), and recognition metadata (by design).

---

## 2. Missing intergovernmental organizations

### 2.1 What is present (verified by entity record, not just mention)

All **15 UN specialized agencies** (World Bank Group as 5 entities in `bank/`); UN principal organs except the Secretariat (UNGA/UNSC/ECOSOC/ICJ present); all major funds and programmes (UNDP, UNICEF, WFP, UNHCR, UNFPA, UNEP, UN Women, UNODC, UN-Habitat, UNRWA, UNAIDS, UNCTAD, ITC, UNOPS, OHCHR, UNHRC); 5 UN regional commissions; and verified-correct rosters for UN (193), NATO (32), EU (27), WTO (166, incl. 2024 accessions), ASEAN (11, incl. Timor-Leste), OSCE (57), Commonwealth (56), IEA (32), EAEU (5), GCC (6). Also present: OECD, OPEC, IMF, World Bank, Interpol, Europol, ICC, ICJ, ITLOS, PCA, ECHR, BIS, FSB, FATF, IOSCO, WCO, ISO, IEC, OPCW, CTBTO, IAEA, all major MDBs (ADB/AfDB/IADB/EBRD/EIB/AIIB/NDB/IsDB…), all major FTAs (RCEP/CPTPP/USMCA/AfCFTA/EFTA…), arms-control regimes, environmental conventions (UNFCCC/UNCCD/CBD/CITES/Ramsar/Kyoto/Paris/Montreal/Basel/Stockholm), G7/G20/G77/BRICS/NAM/SCO/APEC/OAS/OIC/Arab League/AU/CIS/EAEU/Mercosur/ECOWAS/SADC/CARICOM/PIF, CERN/ESO/EMBL, IOC/FIFA, Five Eyes/CSTO/AUKUS, and hundreds of niche bodies.

### 2.2 Missing organizations (prioritized)

**High priority:**
1. **Codex Alimentarius Commission** — 189 members, the global food-standards body referenced by WTO SPS. The biggest outright miss (web-verified absent).
2. **Basel Committee on Banking Supervision (BCBS)** — global bank-capital standard setter; only a mention inside `bank/BIS.yaml`.
3. **Court of Justice of the EU (CJEU)** — the `court/` category has only 4 records total.
4. **Inter-American Court of Human Rights** and **African Court on Human and Peoples' Rights** — ECHR's two regional peers.
5. **WADA** (World Anti-Doping Agency) — sports/ has IOC/FIFA but not the anti-doping regulator.
6. **UN Secretariat** — the UN's executive organ, while three other principal organs exist.

**Medium priority:** UNITAR, UN University, UNDRR, UN Global Compact; **ICANN** (critical internet governance; the niche IGF exists, ICANN doesn't); Caribbean Court of Justice, ECOWAS Court, Andean Tribunal; IADI and IFRS Foundation/IASB (completes the standard-setter set); **Minamata Convention** (the one major missing environmental convention); International Coffee/Cocoa Organizations; UNESCO World Heritage Centre & Institute for Statistics; UNICRI/UNIDIR/UNRISD (low).

**Naming/placement issues (not absences):** the International **Criminal Court** hides under the opaque slug `court/ICW.yaml` while `sports/ICC.yaml` is cricket — an entity-resolution trap (add alias `ICC_CRIMINAL` via the existing aliases mechanism); Arab League sits in `cultural/LAS.yaml`; OPEC Fund record name may be stale (now OPEC Fund for International Development).

### 2.3 Verified factual errors in existing records (web-checked)

| # | Record | Error | Official fact |
|---|---|---|---|
| 1 | `energy/OPEC.yaml` | 11 members, **UAE missing** | OPEC = **12** members post-Angola exit (opec.org) |
| 2 | `political/AFUNION.yaml` | 54 members, **SADR/EH missing** | AU = **55** incl. SADR (au.int); EH exists in countries/ — just not linked |
| 3 | `police/INTERPOL.yaml` | count 206; wrongly includes FM/PW; misses member territories BM/PR/AS; `geographic_scope: regional` | **196** members (interpol.int); scope global |
| 4 | `political/CIS.yaml` | Georgia & Ukraine plain `member`; Turkmenistan `member`; Moldova unflagged | GE withdrew 2009, UA 2018, MD suspending, TM is associate — schema already supports `former_member`/`left` |
| 5 | `political/UN.yaml` | `geographic_scope: regional`; `recognition_status: "UN agency"` (self-referential); no observers; stub description; `suborganizations` = 2 of 36 unagency records | Global; 193 members ✓ + 2 observers (PS, VA) |
| 6 | `bank/AIIB.yaml` | `includes` lists **35 of ~110** approved members | AIIB ≈ 110 members |
| 7 | `sports/ICC.yaml` | `membership_count: 110` vs **217 rows** in includes | Polluted/duplicated roster |
| 8 | **89–200 of 1,078 intblocks** | `membership_count` ≠ roster count; mixed units — country counts vs corporate/individual (WNA=3,000 companies, IGA=10,000, ETSI=900, WEF=1,000) | Needs `membership_count_type` qualifier + CI rule |
| 9 | `political/UN.yaml` et al. | ~406 templated boilerplate descriptions remain (per repo's own strategy doc) | Description-quality campaign needed |

**UN cross-linking gap:** `political/UN.yaml` `suborganizations` lists only WIPO and IMF although 36 `unagency/` records exist — the UN-system graph is mostly unlinked.

---

## 3. Repository readiness for LLM reuse

**Verdict: strongly above average — with a short list of traps to fix.** The repo is one of the rare data projects that treats LLMs as first-class consumers: a root `AGENTS.md` routing hub (with an intent table and "Do not" column), `llms.txt` / `llms.zh.txt`, a consumption contract (`docs/ai-consumers.md`), a ~50-recipe query cookbook **backed by a real test file** (`tests/test_documented_queries.py`, plus a Chinese twin with its own test), thin per-platform shims (Claude, Copilot, Kimi, Cursor, Lingma) that link back instead of duplicating, stable IDs with an alias map, and self-describing artifacts (`_meta` table inside DuckDB, manifests with `schema_hash`, `data_license` embedded).

**Verified TRUE for agents** (queries executed): all record counts, 193 UN members, alpha-3 `borders` join semantics, NATO=32, landlocked=44, CN=16/RU=14 border counts, the 7 non-standard codes, ASF→FSA alias remap, `_meta`↔manifest build identity, DuckDB auto-decompressing `.jsonl.zst`, and the documented `includes[].left` omission gotcha. The advanced recipes (Russia's former memberships = 11 rows) reproduce exactly.

### 3.1 Verified false claims — agents will be burned

1. **The World Bank region example returns 0 rows.** `WHERE region.value = 'Europe & Central Asia'` (in `query-examples.md` and `ai-consumers.md`) matches nothing — the real value is `'Europe & Central Asia (all income levels)'` (61 rows). Notably this example has **no "Expected:" count and no test coverage** — the test gap let it rot.
2. **The pandas `.struct.field()` examples crash with default pandas** (`AttributeError` — parquet structs load as object dicts). Appears in 4 docs including README. Works only with `dtype_backend="pyarrow"`; otherwise use `df["population"].str["value"]`.
3. **"~33 entities missing WB classifications" is wrong** (actual: 8 missing region/incomeLevel/lendingType; 39 missing adminregion) — repeated in llms.txt, AGENTS.md, ai-consumers.md, query-examples.md.
4. **"Each schema property includes a description" is false** — 4/40 (countries) and 16/35 (intblocks); core fields (`code`, `code_status`, `includes`, `blocktype`) have none.
5. **`llms-full.txt` is billed as the "extended" index but is *shorter* than llms.txt** (2.7 KB vs 4.5 KB) and ~80% duplicate — a crawler preferring it gets strictly less.

### 3.2 Licensing — one real gap

The MIT (code) / CC-BY-4.0 (data) split is clean, SPDX-tagged, and machine-readable in manifests. **But `mledoze/countries` (ODbL-1.0, share-alike, largely Wikipedia-derived) is missing from `ATTRIBUTION.md`** despite being cited in the per-record provenance of essentially every country record. Redistributing ODbL-derived fields inside a CC-BY-4.0 compilation is a genuine compatibility question; at minimum the attribution table is incomplete. **P1 fix.**

### 3.3 Format & friction gaps for LLM pipelines

- **JSONL exists only zstd-compressed** — no plain JSONL/JSON/CSV anywhere. Agents in restricted sandboxes (no zstd, no pip) are stuck; DuckDB mitigates but requires DuckDB. Files are small (~600 KB compressed) — ship uncompressed too.
- **YAML export is asymmetric**: `blocktypes.yaml` committed plain; `countries.yaml`/`intblocks.yaml` zstd-only.
- **No flattened membership export** — all roster analytics require UNNEST/explode of nested lists; a `memberships` edge table (intblock_id, country_code, status, joined, left) in Parquet/CSV would make the data CSV-agent-friendly.
- **JSON Schemas have no published `$id`/stable URL**; no concrete `releases/download/vX.Y.Z/...` URL pattern documented.
- **`data/_legacy/` (6.5 MB of stale Airtable-era JSON dumps) is an unflagged crawler trap** — nothing in AGENTS.md/llms.txt warns agents away from obsolete data.
- **`acronyms[].lang` tags are noisy** (e.g., '나토' tagged `en`) — lang-filtered matching misfires.
- RAG: corpus is small enough for whole-dataset-in-context; a plain-JSONL dump suffices — no embeddings needed.

### 3.4 Agent-surface consistency

The hub-and-spoke design is genuinely good — all 8 platform shims verified as thin links with no conflicting instructions; scope guardrails ("no HDI/GDP — out of scope") are uniform; the OpenSpec block in AGENTS.md is machine-refreshed. Drift is concentrated in the copy-pasted join-key/gotcha blocks across llms.txt ↔ llms-full.txt ↔ ai-consumers.md ↔ query.md ↔ README — exactly where the false examples live. **Single-source those blocks** (template or generated) to eliminate the drift class.

**LLM-readiness priorities:** P0 fix the 3 false examples + add them to tests; P1 add mledoze ODbL attribution; P2 ship plain JSONL + flattened memberships export + fix/delete llms-full.txt + quarantine `_legacy/`; P3 backfill schema descriptions, publish schemas at URLs, clean acronym lang tags, normalize `includes[].status` enum docs.

---

## 4. General repository, code and data quality

### 4.1 Export integrity — excellent (independently recomputed)

- Row counts **256 / 1,078 / 86 identical across YAML sources, JSONL.zst, YAML.zst, Parquet, DuckDB, manifests, and `_meta`**; primary-key sets equal across all formats; single frozen build identity (v1.9.0, `e228586`) everywhere; aliases JSON == Parquet; repo artifact checker and both validators pass with 0 errors.
- Issues: **Parquet/DuckDB silently drop 11 intblock fields** including `includes[].left` (329 departure dates — the *former-membership* data!), `active_period` (469 files), `last_verified` (726). Intentional per a test comment, but undocumented in README — and it undercuts the flagship "former members" query recipes on the Parquet path. Either export these fields or document the divergence prominently. Manifest `schema_hash` hashes the pre-write schema (not reproducible from the artifact); `parent_entity` is a dead Arrow field.

### 4.2 Data/schema quality

- **Countries:** perfectly uniform core schema, provenance on all 256 records, zero referential-integrity failures (borders reciprocal, flags/wikidata/tlds clean). Nits: camelCase `incomeLevel`/`lendingType` amid snake_case; `numeric_code` duplicates `m49_code`; inconsistent `id` vs `lang` keys for languages.
- **Intblocks:** filename==id 100%, directory↔blocktype alignment 100%, no duplicate ids, all 46,536 country references in `includes` resolve. Issues: `partof` polymorphic (str/dict/list/None); `founded` has ~50 non-standard values ("1990s", YYYY-MM); `membership_count` semantics ambiguous in 89+ records (see §2.3 #8); noisy acronym lang tags; 424 records still lack `wikidata_id` and ~406 descriptions are boilerplate (repo's own backlog).
- **Blocktypes taxonomy:** coherent (86 entries, all used values defined) except an unused near-duplicate `unregionalgroup`; docs say "63 categories", actual **62** directories.

### 4.3 Code quality

- Well-structured `internacia_builder` package with a **shared rule engine** (62 rules, 52 check functions) used identically by CLI validators and the quality analyzer; explicit schemas; loud failures; pinned deps + uv.lock.
- Issues: **`build.py` is still a 2,035-line monolith** containing the entire quality analyzer (`quality.py` is a 24-line shim — the package refactor is half-done); substantive programs still in `scripts/` (enrich 768+586 LOC, `validate_links.py` 336 LOC using `requests` while the package HTTP client is urllib-based — **two HTTP stacks**); `scripts/validate_*.py` shims crash without `pip install -e .` (no sys.path bootstrap, unlike `builder.py`); `requirements.txt` duplicates pyproject pins; a 520-line one-off (`apply_manus_roadmap.py`) sits undocumented in `scripts/`.

### 4.4 Tests & CI

- Suite executed: **13/14 test files fully green.** `test_documented_queries.py` is 34/38 — the **4 failures are real OOMs**: documented `countries JOIN intblocks ON TRUE` cross-join recipes get SIGKILLed even with a 2 GB memory limit (reproduced outside pytest). These need "UNNEST first, join second" rewrites — both for the tests and because agents will copy these recipes.
- CI is strong: ruff → pytest → both validators → markdown links (169 links pass) → artifact-consistency guard → fresh-build parity → baseline diff → quality analyzer gating on CRITICAL/IMPORTANT; weekly link validation + monthly enrichment check (scheduled); Dependabot; tagged releases attach all assets.
- Gaps: no coverage measurement; release workflow doesn't run pytest; single Python version (3.11); committed `dataquality/` snapshot predates the latest release (lifecycle rule not enforced).

### 4.5 Hygiene

Committed generated binaries (4.8 MB in git, 19 artifacts rebuilt and recommitted on every data edit); 253 committed per-country quality `.txt` reports; `data/_legacy/` 6.5 MB stale dumps; dated `dev/research/` notes; heavy multi-agent config surface (.agent/.cursor/.kimi/.lingma — justified for this project's agent-first stance, but adds maintenance surface).

---

## 5. Documentation quality and gaps

### 5.1 Per-file verdict

- **`docs/ai-consumers.md` — the best doc in the repo.** Consumption contract, scope boundaries, versioning workflow, field semantics, recipes, common-mistakes table. Verified accurate (only stale org links).
- **README.md** — unusually complete (features, install, quick start, all 19 output files, schema tables, versioning/ID-stability policy, scripts table). All commands and counts verified. Defects below.
- **CHANGELOG.md** — exemplary Keep-a-Changelog + SemVer with BREAKING markers and migration notes; current at v1.9.0.
- **CONTRIBUTING.md, enrichment.md, country-code-policy.md, topic-taxonomy.md, docs/agents/*** — accurate; every referenced command/config verified to exist.
- **`docs/improvement-plan.md` — stale** (says "current release v1.2.0", describes a repo with no tests/unpinned deps/no intblocks validation — all long shipped; "next review 2026-09-12").
- **`docs/strategy-and-user-needs.md` — half-stale** (v1.3.0 era; its Track A items A1 license / A2 alias map / A3 `_meta` table are all shipped but still presented as open gaps; A4 release diff, B4 crosswalks, C1 datapackage, D1 API posture remain validly open).

### 5.2 Verified inaccuracies (each independently confirmed)

1. **Broken org identity (biggest issue):** README badge + ~15 files link `github.com/commondataio/internacia-*`. Externally confirmed: `commondataio` is a Dateno *archive* account with no internacia repos; all repos live under **`datenoio`**. Badge and all API/SDK links are **404**.
2. "63 domain categories" (README, openspec/project.md, improvement-plan) — actual **62**.
3. README: "one-off migration scripts live in `dev/scripts/`" — directory doesn't exist; the actual 520-line one-off sits undocumented in `scripts/`.
4. README countries schema table omits `centroid`, `parent_entity`, and the `exceptionally_reserved` enum value; lists 3 non-standard codes vs actual 7 (its own policy doc says 7).
5. Stale planning docs (#improvement-plan, #strategy) and 3 implemented-but-unarchived OpenSpec changes (artifact-consistency guard, quality-report lifecycle, builder refactor).
6. `llms-full.txt` smaller than `llms.txt`; committed `dataquality/` report predates v1.9.0; LICENSE year 2025; zh query-examples is an unlabeled 8-section subset of the 67-section English cookbook, not a translation.
7. Relative `../internacia-api` links in "Related projects" break when viewed on GitHub.

**Undocumented positive:** a **Zenodo DOI already exists** (10.5281/zenodo.21452328, v1.7.0) — no badge, no `CITATION.cff`, and the strategy doc still lists it as a to-do.

### 5.3 Documentation gaps

1. **No generated data dictionary / full schema reference** (README tables are partial and already drifted; JSON Schemas carry descriptions for only some properties).
2. **No versioning/release policy doc** — SemVer asserted but data-release semantics unwritten (what is MAJOR for a dataset? alias retention? asset retention?); no tag↔version↔CHANGELOG release gate.
3. **No machine-readable per-release diff** (strategy A4 open) and no doc describing one.
4. **No architecture doc / ADRs** — pipeline knowledge scattered across openspec/project.md, README, AGENTS.md.
5. Citation/discoverability: DOI undocumented, no `CITATION.cff`, no Frictionless `datapackage.json`.
6. **API posture undocumented** — hosted vs self-host unanswered, API links 404, no OpenAPI pointer.
7. No "report a data error" path (no issue templates); validator exit-code conventions undocumented; zh/en parity policy unstated; intblock enrichment cadence manual/implicit.

---

## 6. Possible usage scenarios by user type

| User type | Scenario | Fit today | Key friction |
|---|---|---|---|
| **Search-engine enrichment pipeline (Dateno — primary consumer)** | Entity linking of datasets/organizations to countries, orgs, blocs; multilingual name/alias matching; geo filtering by region/income/bloc membership | ★★★★☆ Strong: aliases table, multilingual names, Wikidata Q-ids, stable joins, fuzzy-search-oriented SDK | 424 intblocks without `wikidata_id`; boilerplate descriptions; thin alias map (3 entries); acronym lang-tag noise |
| **LLM/agent developers** | Grounding country/org facts; verified query recipes; tool-use via DuckDB; whole-dataset-in-context (corpus is small) | ★★★★☆ Best-in-class agent docs + test-backed cookbook | 3 false examples (§3.1); zstd-only JSONL; `_legacy/` trap; no flattened membership table |
| **Researchers / economists / political scientists** | Reference data for country classifications (WB region/income), bloc membership over time, treaty rosters, "who is in what" analytics | ★★★★☆ Rich roster data incl. join/leave dates, provenance for citation; Zenodo DOI exists | DOI undocumented; no `CITATION.cff`; no datapackage.json; `includes[].left` missing from Parquet/DuckDB (former-membership analysis broken outside JSONL!) |
| **App developers** | Country pickers, dropdowns, flag/currency/timezone/calling-code data via SDK or DuckDB | ★★★★☆ Complete ISO set, flag emoji, TLD, timezones, demonyms; offline DuckDB | No hosted API (posture undecided); API/SDK links 404 |
| **Data engineers / catalog builders** | Crosswalking between identifier systems (ISO ↔ M49 ↔ WB ↔ Wikidata); importing into catalogs | ★★★☆☆ Good 4-system crosswalk today | Missing GeoNames/FIPS/IOC/FIFA/ROR crosswalks; no flattened edges export |
| **Journalists / OSINT / policy analysts** | Sanctions lists (FATF black/grey), membership verification, bloc timelines, "near-universal orgs a country avoids" queries | ★★★★☆ Verified recipes for exactly these (former members, departure dates, coverage gaps) | Doc examples must be trustworthy (see §3.1); OOM-prone cross-join recipes |
| **Open-data community / contributors** | Reuse as reference hub; contribute corrections | ★★★☆☆ CC-BY-4.0 clear, CONTRIBUTING solid, spec-driven | No data-error reporting path; ODbL attribution gap; no data-hub presence |

**Positioning note:** the project's deliberately-declared scope boundaries (no HDI/GDP/time-series/full geometry) are *good* for LLM reuse — agents are explicitly told what not to expect. Keep enforcing them in docs.

---

## 7. Project architecture and future development

### 7.1 Architecture assessment

```
data/countries/*.yaml (256)  data/intblocks/<62 cats>/*.yaml (1,078)  data/blocktypes/blocktypes.yaml (86)
        │  JSON Schema + completeness gates + shared 62-rule quality layer (internacia_builder/validate/*)
        ▼
internacia_builder.build  →  JSONL.zst / YAML.zst / Parquet / DuckDB + manifests + _meta + aliases
        │  check_generated_artifacts.py (cross-format parity + build-identity guard, in CI + release)
        ▼
data/datasets/ (19 artifacts, committed)  +  GitHub Releases (tag v* → rebuild + assets)
        ├── internacia-api (REST, sister repo)   └── internacia-python (SDK, DuckDB-based)
```

**Strengths:** governance depth exceptional for a data repo (schema + completeness + quality rules + per-field provenance with freshness thresholds + frozen build identity + alias-based ID-stability contract); spec-driven development is real (14 capability specs, 30 archived OpenSpec changes); self-describing artifacts; reproducible builds (pinned deps, uv.lock, fresh-build parity in CI); agent-first documentation ahead of common practice.

**Weaknesses:**
1. **Roster denormalization is the core scaling pain.** Membership is copy-pasted into each intblock record (e.g., the 193-member UNESCO roster duplicated into UIL/IIEP/IBE); a roster change touches N files (the v1.8.0 ~500-record bulk sync shows the cost). No normalized membership/edge form exists.
2. **Half-finished package refactor** — 2,035-line build.py still hosts the analyzer; two HTTP stacks; one-off scripts in `scripts/`.
3. **Data+code coupling / committed artifacts** — 4.8 MB binaries in git, monotonically growing diff noise; strategy doc already flags the repo-size budget question.
4. **Schemas not published/versioned as artifacts** (schema_hash detects change but consumers can't fetch schemas); no release-diff artifact; stale committed quality reports.
5. **Scalability ceiling is distant** — ~1,334 entities is small; the design comfortably holds 10–50×. Binding constraints are roster duplication, provenance maintenance cost, and CI build time — not YAML file count. One-file-per-entity YAML is the right curation format; keep it.

### 7.2 Future development — prioritized roadmap

**P0 — fix consumer-facing breakage (hours):**
1. Org-link sweep `commondataio → datenoio` across ~15 files incl. README badge; replace relative sister-repo links with absolute ones.
2. Fix the 3 false doc examples (WB region string + Expected count + test; pandas struct examples + smoke test; "~33" figure) and the schema-descriptions claim.
3. Correct "63 → 62 categories" (3 files); complete README schema table (`centroid`, `parent_entity`, `exceptionally_reserved`, 7 non-standard codes).
4. Add Zenodo DOI badge + `CITATION.cff`; add mledoze/countries (ODbL) to ATTRIBUTION.md with a compatibility rationale.
5. **Data fixes:** OPEC+UAE, AU+SADR, Interpol roster rebuild (196), CIS statuses, UN record (scope/observers/description/suborganizations), sports/ICC includes.

**P1 — consumer-contract hardening (days):**
6. Add missing high-value orgs: Codex Alimentarius, BCBS, CJEU + Inter-American/African human-rights courts, WADA, UN Secretariat; expand `court/` 4 → ~12.
7. Resolve `membership_count` semantics: add `membership_count_type`, fix AIIB (110)/GATT/worst rosters, CI rule for count-vs-list with an allow-list.
8. Export `includes[].left` (+ ideally `active_period`, `last_verified`) to Parquet/DuckDB, or document the divergence loudly.
9. Fix the 4 OOM cross-join cookbook queries ("UNNEST first, join second").
10. Generated data dictionary from JSON Schemas (drift-gated in CI, same pattern as the artifact checker); publish versioned schemas with `$id` URLs.
11. Machine-readable release diff (`diff-vX.Y.Z.json`) + versioning-policy doc + tag/version/CHANGELOG release gate; refresh/banner the two stale planning docs; archive the 3 shipped OpenSpec changes.
12. Ship plain JSONL + flattened `memberships` edge export; fix or delete llms-full.txt; quarantine `data/_legacy/`; add issue templates for data-error reports; `datapackage.json`.

**P2 — data-model evolution (weeks):**
13. Membership-as-edges build target (source YAML stays denormalized; build emits normalized table + optional graph view with `member_of`/`partof`/`predecessor_of` edges).
14. Delta/changelog feed per release; automated intblock enrichment cadence (mirror monthly countries check) + Wikidata drift report (merged/hijacked Q-ids have already bitten: FIPIC, ARF).
15. Quality dashboard on GitHub Pages with per-release trends (replaces stale committed reports).
16. New lightweight entity classes for recurring deferrals (`summit_meeting`/`initiative` — EPC, D10, BRICS+, Global Gateway backlog); formalize treaty semantics (parties vs members, ratification vs accession) in `includes_status.yaml`.
17. Add `un_status` field to countries; decide/document the disputed-territory inclusion threshold (Somaliland, Northern Cyprus); backfill gini/adminregion.

**P3 — platform & distribution (strategic):**
18. Decide and document API posture (hosted read-only vs self-host-only); restore API/SDK links; OpenAPI pointer.
19. Artifacts-out-of-git decision for v2.0 (manifests + aliases stay; binaries → Releases-only) or state a repo-size budget explicitly.
20. Finish the package refactor (analyzer → `internacia_builder/quality/`, one HTTP stack, retire one-off scripts to `dev/scripts/`).
21. Crosswalks: GeoNames, FIPS 10-4, IOC/FIFA (countries), ROR (orgs), each with provenance behind completeness gates.

**Explicitly defer** (consistent with the repo's own, correct, scope stance): full GeoJSON geometry, time-series indicators, socioeconomic fields (HDI/GDP).

---

## Appendix: audit trail

- Four independent review reports (completeness, code/data quality, LLM readiness, docs/architecture) were produced by parallel auditors against a local mirror at commit `e228586`; all headline numbers were recomputed programmatically; roster claims were web-verified against opec.org, au.int, interpol.int, FAO/WHO Codex, and official NATO/EU/WTO/ASEAN/OSCE counts.
- Test suite executed locally: 13/14 files green; 4 OOM failures in `test_documented_queries.py` reproduced.
- Documented agent queries executed against `internacia.duckdb` / Parquet / JSONL.zst; true/false results listed in §3.

*Review prepared 2026-08-03.*

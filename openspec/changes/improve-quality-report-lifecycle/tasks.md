## 1. Quality analysis in CI
- [x] 1.1 Add a CI step running `builder.py analyze-quality` and uploading the report as an artifact
- [x] 1.2 Fail the step only on CRITICAL/IMPORTANT issues, with the threshold configurable
- [x] 1.3 Document the CI quality gate in CONTRIBUTING

## 2. De-noise duplicate-link rule
- [x] 2.1 Remove the country `tld` → `http://.tld` pseudo-URL conversion from the analyzer
- [x] 2.2 Classify duplicate-link findings by link type and allow expected shared domains / parent-child relationships
- [x] 2.3 Separate "possible duplicate entity" from "shared external citation" in the report output

## 3. Report lifecycle
- [x] 3.1 Decide and document whether `dataquality/` is generated-on-release or CI-artifact-only
- [x] 3.2 Remove the parallel `dataquality/fresh_run/` directory
- [ ] 3.3 If any report remains tracked, add a freshness check comparing header counts to current source counts — deferred: CONTRIBUTING now designates the CI-generated report as authoritative; a standalone freshness comparator is not yet added

## 4. Validate
- [x] 4.1 Run the analyzer locally and confirm reduced duplicate-link noise
- [x] 4.2 Run `openspec validate improve-quality-report-lifecycle --strict`

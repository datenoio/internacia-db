# Change: One rule registry for the validators and analyze-quality

## Why
Rule logic already lives in `internacia_builder.validate.*`, but `validate_countries`,
`validate_intblocks` and `analyze-quality` each kept their own list of which rules to run and
how to configure them (issue #21). The lists drifted:

- `analyze-quality` did not run three rules the validators enforce as errors: migrated attribute
  fields (`INVALID_ATTRIBUTE_FIELD`), the intblock `wikidata_id` requirement
  (`MISSING_WIKIDATA_ID`) and `partof` targets (`INVALID_PARTOF_TARGET`).
- Eight issue types of validator errors (crosswalk provenance and policy, attribute fields and
  migrations) were missing from the report's priority map, so the quality gate filed them as
  MEDIUM and did not fail on them.
- `validate_intblocks` did not check intblock provenance integrity or freshness.

## What Changes
- `internacia_builder/validate/registry.py` lists every rule once with its dataset and validator
  severity (`error`, `warning`, or report-only), loads the inputs once (`load_context`) and runs
  the rules (`run_rules`). The validators and `analyze-quality` both run it.
- Repository-state gates (identifier stability, changed records, tier-1 roster) and the
  validators' aggregate summaries stay with their consumer.
- Every emitted issue type is classified and described; issue types of validator errors are
  CRITICAL or IMPORTANT. A test checks both.
- `MISSING_TOPICS` replaces the validator-only "missing topics" message so it reaches the report.
- YAML sources are parsed with libyaml when available (same results, about 7x faster).

## Impact
- Affected specs: data-quality-analysis, intblocks-data-quality
- Affected code: `internacia_builder/build.py` (`analyze_quality`),
  `internacia_builder/validate/{countries,intblocks,registry}.py`, `quality_report.py`
- On the current data, validator output and the quality report are unchanged.

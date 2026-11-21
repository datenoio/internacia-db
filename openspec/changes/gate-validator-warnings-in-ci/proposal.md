# Change: Validator warnings fail CI

## Why

Issue #18 asked for the intblocks validator warnings to be burned down and then gated in CI,
so that drift cannot return silently. Warnings went from 167 (August 2026) to 114 (September)
to 0 (2026-11-21, when the last deprecated `associate` statuses were recoded). Both validators
now report 0 errors and 0 warnings, but CI still passes with any number of warnings.

Four warning rules compare a recorded date with today: intblock `last_verified` age
(`STALE_LAST_VERIFIED`), country and intblock provenance age (`STALE_PROVENANCE`) and border
status age. They start firing as the calendar advances, with no change to the data. The oldest
country provenance date (2026-06-15) becomes stale on 2027-07-01 and the oldest intblock
`last_verified` (2026-07-12) on 2027-08-01. A gate that counted them would then fail every pull
request, including ones that touch no data. The `last_verified` KPI in the CI job summary already
tracks these dates.

## What Changes

- A registry rule can be marked `dated`. The four freshness rules above are dated.
- `--fail-on-warning` fails on every warning except those from dated rules. Dated warnings are
  still printed, counted in `warning_count` and written to `--report` and `--json` output.
- The `Validate countries` and `Validate intblocks` steps of `.github/workflows/validate.yml`
  run with `--fail-on-warning`.

## Impact

- Affected specs: `dev-tooling` (validator warnings gate CI).
- Affected code: `internacia_builder/validate/registry.py` (`Rule.dated`,
  `validator_messages` returns dated warnings separately), `internacia_builder/validate/countries.py`,
  `internacia_builder/validate/intblocks.py`, `.github/workflows/validate.yml`.
- Affected docs: `CONTRIBUTING.md`, `docs/agents/contribute.md`.
- Contributors: a pull request that adds a warning now fails CI. Fix the cause, or add an
  allowlist entry where the completeness schemas provide one.
- Consumers: no export changes.
- Approval: the maintainer chose this design in the session of 2026-11-21 (gate both validators,
  keep the dated freshness warnings advisory).

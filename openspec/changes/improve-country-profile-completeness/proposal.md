# Change: Improve country capital coverage and right-size the completeness gates

## Why
`capital_city` is missing on 15/256 records (5.9%, above the 5% warn threshold), but several of those entities have a de-facto capital or seat of government (Taiwan → Taipei, Palestine → Ramallah, Hong Kong, Macao, Gibraltar, Vatican, Israel). `gini` is missing on 86/256 (33.6%, above the 33% threshold) but is structurally unavailable for many territories, so the flat gate does not reflect reality. This keeps the build permanently in a warning state that hides real regressions.

Scope guardrail: `capital_city`, `gini`, and `borders` are already-in-scope reference fields; this change adds no new socioeconomic profile fields.

## What Changes
- Fill `capital_city` (name and coordinates) with provenance for eligible entities that have a de-facto capital or seat of government, and document the genuinely capital-less entities (uninhabited territories) so they are expected exclusions.
- Re-scope or re-threshold the `gini` completeness gate with documented rationale — for example scoping the denominator to sovereign ISO entities where a value can exist — so the warn budget reflects data reality rather than being permanently exceeded.
- Document the `borders` alpha-3 contract consistently in the README schema table and consumer docs (data is already alpha-3).

## Impact
- Affected specs: countries-data-quality
- Affected code: `data/countries/*.yaml` (eligible capitals), `data/schemas/countries_completeness.yaml`, `README.md`, `docs/country-code-policy.md`

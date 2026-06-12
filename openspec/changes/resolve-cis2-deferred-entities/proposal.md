# Change: Resolve CIS2 deferred entity references

## Why

`data/intblocks/political/CIS2.yaml` references country codes `XA`, `XS`, `XT`, `XN` (Abkhazia, South Ossetia, Transnistria, Artsakh) that do not exist in the countries dataset. Validation currently warn-only; policy options are documented but not decided in `docs/country-code-policy.md`.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §1.3.

## What Changes

- Decide and implement one policy: (A) add user-assigned country profiles, (B) change include types with allowlist, or (C) permanent deferred allowlist with explicit documentation.
- Update `docs/country-code-policy.md` with the chosen policy and filtering examples.
- Update validation allowlists and completeness config accordingly.
- Document consumer impact in CHANGELOG if country records are added.

**Recommended:** Option A or B for explicit modeling.

## Impact

- Affected specs: `countries-entity-model` (modified), `cross-dataset-integrity` (modified)
- Affected code: `data/countries/`, `data/intblocks/political/CIS2.yaml`, `data/schemas/*_completeness.yaml`, `docs/country-code-policy.md`
- Breaking: Possible if new country records change row counts or cross-reference behavior

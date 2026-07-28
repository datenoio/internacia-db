## MODIFIED Requirements

### Requirement: Intblock country include cross-reference

When an intblock `includes` entry has `type: country`, its `id` SHALL resolve to an existing file `data/countries/{id}.yaml` unless the id is listed in a configured allowlist. Unresolved references SHALL be reported according to completeness config. CIS2 entity codes (`XA`, `XS`, `XT`, `XN`) SHALL follow the policy documented in `docs/country-code-policy.md`—either as country records, allowlisted alternate types, or explicitly documented permanent deferrals—not silent warn-only behavior.

#### Scenario: CIS2 includes pass under chosen policy

- **WHEN** CIS2 includes reference `XA`, `XS`, `XT`, or `XN` after policy implementation
- **THEN** cross-reference validation behaves per documented policy without undocumented warnings

#### Scenario: Valid country include resolves

- **WHEN** an intblock includes `{id: FR, type: country}` and `data/countries/FR.yaml` exists
- **THEN** cross-reference validation passes for that include

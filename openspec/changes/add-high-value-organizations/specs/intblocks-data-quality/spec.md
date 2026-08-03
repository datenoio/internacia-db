## ADDED Requirements

### Requirement: High-value organization coverage from 2026-08 audit

The intblocks dataset SHALL include records for the following bodies identified as verified coverage gaps: Codex Alimentarius Commission, Basel Committee on Banking Supervision, Court of Justice of the European Union, Inter-American Court of Human Rights, African Court on Human and Peoples' Rights, World Anti-Doping Agency, and the UN Secretariat. Each record SHALL meet the existing completeness gates and carry provenance for enriched fields.

#### Scenario: Codex Alimentarius record exists

- **WHEN** a consumer searches intblocks for the global food-standards body
- **THEN** a `CODEX` record exists with its member roster and FAO/WHO parentage

#### Scenario: Regional human-rights courts present

- **WHEN** a consumer lists records in the `court/` category
- **THEN** the Court of Justice of the EU, the Inter-American Court of Human Rights, and the African Court on Human and Peoples' Rights are present alongside ECHR

#### Scenario: UN Secretariat completes principal organs

- **WHEN** a consumer queries intblocks with `partof` containing `UN`
- **THEN** a UN Secretariat record appears alongside UNGA, UNSC, and UNHRC

### Requirement: Criminal court alias disambiguation

The intblock alias map SHALL document that the International Criminal Court is stored under id `ICW`, distinguishing it from the cricket body stored under `ICC`.

#### Scenario: Agent resolves ICC ambiguity

- **WHEN** an agent looks up "ICC" via the aliases artifact
- **THEN** it finds guidance that the criminal court is `ICW` and `ICC` is the International Cricket Council

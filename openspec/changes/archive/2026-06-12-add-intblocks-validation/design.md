## Context

Countries validation shipped in v1.2.0. Intblocks grew to 1,065 records with 85 blocktypes but remain unvalidated at build time. Gap analysis (`dev/research/gaps_merged_20260528.md`) added 44 records; membership and metadata quality varies by category.

## Goals / Non-Goals

- Goals:
  - Fail builds on intblock schema violations, duplicate IDs, and invalid blocktype references.
  - Establish completeness thresholds with warn-then-error rollout (mirror countries pattern).
  - Emit intblocks build manifest for consumer upgrade checks.
  - Validate cross-dataset `includes` and `partof` integrity.
- Non-Goals:
  - Populating all missing `includes` in one change (warn-first, backlog tracked separately).
  - Field-level provenance for intblocks (future change).
  - Resolving CIS2 deferred entities (see `resolve-cis2-deferred-entities`).

## Decisions

### Decision: Completeness rollout

Start `includes`, `wikidata_id`, and `description` in `warn` mode. Switch to `error` after backlog remediation in `add-intblocks-gap-backlog` or a follow-up.

### Decision: Blocktype validation

Every value in a record's `blocktype` list MUST exist as an `id` in `data/datasets/blocktypes.yaml` (or future source path after `add-blocktypes-source`).

### Decision: Historical entity fields

Validator SHALL warn when `status: historical` or `dissolved` is set but `dissolved` date is missing; error mode deferred.

## Risks / Trade-offs

- Strict schema may surface hundreds of warnings on first run → mitigated by warn mode and incremental tightening.
- `intblocks.schema.json` currently allows `additionalProperties: true` → tighten in 1.1 if safe, else document as intentional flexibility.

## Migration Plan

1. Run validator in report-only mode; fix schema errors in source YAML.
2. Enable builder integration (non-zero exit on schema/identifier errors only).
3. Tighten completeness to error mode per field after remediation.

## Open Questions

- Should `agreement` and `intorg` categories require non-empty `includes` in error mode, or only a high null-rate threshold?

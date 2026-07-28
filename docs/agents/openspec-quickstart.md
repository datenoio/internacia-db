# OpenSpec quickstart for agents

Short guide for schema changes and breaking exports. Full reference: [openspec/AGENTS.md](../../openspec/AGENTS.md).

## When to create a proposal

**Do propose** for: new capabilities, breaking schema/export changes, architecture shifts.

**Skip proposal** for: bug fixes restoring spec behavior, typos, non-breaking dependency updates, tests for existing behavior.

## Checklist

1. Run `openspec list` and `openspec list --specs` — check for conflicts.
2. Pick a unique verb-led `change-id` (e.g. `add-field-catalog`, `update-borders-policy`).
3. Scaffold under `openspec/changes/<change-id>/`:
   - `proposal.md` — why, what, impact
   - `tasks.md` — implementation checklist
   - `design.md` — only if cross-cutting or ambiguous
   - `specs/<capability>/spec.md` — deltas with `## ADDED|MODIFIED|REMOVED Requirements`
4. Every requirement needs at least one `#### Scenario:` block.
5. Run `openspec validate <change-id> --strict` and fix all issues.
6. **Do not implement until the proposal is approved.**

## Scenario format (required)

```markdown
#### Scenario: Descriptive name
- **WHEN** condition
- **THEN** expected outcome
```

Use `#### Scenario:` (four hashes). Bullets or `### Scenario:` will fail validation.

## MODIFIED requirements pitfall

When modifying an existing requirement, copy the **full** requirement block from `openspec/specs/<capability>/spec.md` into the delta and edit it. Partial MODIFIED deltas drop detail at archive time.

## Dataset scope

Countries are **reference data only**. Do not propose socioeconomic profile fields (HDI, GDP, government type, internet penetration).

## CLI essentials

```bash
openspec list                  # active changes
openspec list --specs          # capabilities
openspec show <id> --json --deltas-only
openspec validate <change-id> --strict
openspec archive <change-id> --yes   # after deployment
```

## Workflows

- `.agent/workflows/openspec-proposal.md` — scaffold a change
- `.agent/workflows/openspec-apply.md` — implement an approved change
- `.agent/workflows/openspec-archive.md` — archive after deployment

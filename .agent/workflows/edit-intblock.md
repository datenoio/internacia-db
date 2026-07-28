---
description: Edit an intblock YAML record safely with validation.
---
<!-- AGENT:START -->
**Goal:** Modify a record under `data/intblocks/<category>/*.yaml` without breaking validation or exports.

**Read first:** [docs/agents/contribute.md](../../docs/agents/contribute.md) (intblocks checklist).

**Guardrails**
- Filename stem must match record `id` exactly (case-sensitive).
- Every `blocktype` value must exist in `data/blocktypes/blocktypes.yaml`.
- Quote YAML boolean lookalikes: `'NO'` (Norway), `'no'` (Norwegian).
- Do not hand-edit `data/datasets/`.
- Do not invent membership for dissolved orgs; use `status: historical` + `dissolved` date.
- Records without `includes` need `membership_applicability: not_applicable` when membership is intentionally absent.

**Steps**
1. Locate the file: `data/intblocks/<category>/{ID}.yaml`.
2. Apply edits following the intblocks checklist in [docs/agents/contribute.md](../../docs/agents/contribute.md).
3. Validate with structured output:

```bash
python scripts/validate_intblocks.py --json
```

4. Fix any `errors` in the JSON output; use `fix_hint` when present.
5. If the change affects schema or exports, stop and create an OpenSpec proposal ([docs/agents/openspec-quickstart.md](../../docs/agents/openspec-quickstart.md)).
6. Run full contributor checks before PR:

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
pytest tests/
ruff check internacia_builder/ scripts/ tests/
python scripts/builder.py build --formats parquet,duckdb
```

7. Update `CHANGELOG.md` under `[Unreleased]` for consumer-visible changes.

**Reference**
- `includes[].status` values: `data/schemas/includes_status.yaml`
- Completeness config: `data/schemas/intblocks_completeness.yaml`
- OpenSpec apply workflow: `.agent/workflows/openspec-apply.md`
<!-- AGENT:END -->

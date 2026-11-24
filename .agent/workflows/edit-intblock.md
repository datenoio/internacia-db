---
description: Edit an intblock YAML record safely with validation.
---
<!-- Generated from templates/agent-shims/.agent/workflows/edit-intblock.md by scripts/generate_agent_shims.py; edit the template and rerun. -->
<!-- AGENT:START -->
**Goal:** Modify a record under `data/intblocks/<category>/*.yaml` without breaking validation or exports.

**Read first:** [docs/agents/contribute.md](../../docs/agents/contribute.md) (intblocks checklist).
For catalogue hunts or completeness repairs, start at
[docs/agents/discover.md](../../docs/agents/discover.md).

**Guardrails**
- Filename stem must match record `id` exactly (case-sensitive).
- Every `blocktype` value must exist in `data/blocktypes/blocktypes.yaml`.
- Quote YAML boolean lookalikes: `'NO'` (Norway), `'no'` (Norwegian).
- Do not hand-edit `data/datasets/`.
- Set `last_verified` to the date you checked the roster against its `provenance` source; validation requires it on new or changed records.
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
python scripts/builder.py build
python scripts/check_generated_artifacts.py
pytest tests/
ruff check internacia_builder/ scripts/ tests/
python scripts/check_doc_counts.py
python scripts/check_markdown_links.py
```

7. Run the full build. Build manifests and `datapackage.json` are build outputs that git ignores, so a data change normally leaves `data/datasets/` clean; commit only the descriptors git still tracks there (`contract.json`, dataset card, alias JSON, `border_status.json`) when the build changes them. CI rebuilds and checks that the descriptors match. Add a `changelog.d/<slug>.md` fragment instead of editing `CHANGELOG.md`. Update cookbook expectations when
   query results change; the intblock count in docs is rounded down to the hundred
   (1304 records are written `1300+`), so update it only when
   `scripts/check_doc_counts.py` asks.

**Reference**
- Worked add example: [docs/agents/add-intblock-example.md](../../docs/agents/add-intblock-example.md)
- `includes[].status` values: `data/schemas/includes_status.yaml`
- Completeness config: `data/schemas/intblocks_completeness.yaml`
- OpenSpec apply workflow: `.agent/workflows/openspec-apply.md`
<!-- AGENT:END -->

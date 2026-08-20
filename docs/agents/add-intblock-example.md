# Worked example: add an intblock

This walkthrough shows how to add a new organization record. Use it together
with the checklist in [contribute.md](contribute.md). A compact real record to
copy from is [`data/intblocks/military/AUKUS.yaml`](../../data/intblocks/military/AUKUS.yaml)
(3 members, sourced description, provenance, `last_verified`).

Do **not** invent membership. If the official roster is not in hand, stop and
leave `includes` empty only when you also set
`membership_applicability: not_applicable`.

## 1. Confirm it belongs

Read [intblock-inclusion-policy.md](../intblock-inclusion-policy.md). Standing
IGOs, treaties with parties, durable forums, and named geographic sets are in
scope. Ad-hoc news coalitions and socioeconomic rankings are not.

Pick:

- **`id`** — uppercase official acronym (`AUKUS`, `NATO`). See id rules in the
  inclusion policy. Filename stem must match `id` exactly.
- **Directory** — `data/intblocks/<primary-blocktype>/`. The folder name is the
  primary `blocktype` and must already exist in
  `data/blocktypes/blocktypes.yaml`. Additional types go in the `blocktype` list.
- **`scope_category`** — `igo` | `treaty_body` | `policy_forum` |
  `reference_enumeration`.

## 2. Create the YAML

```text
data/intblocks/military/AUKUS.yaml
```

Minimum fields: `id`, `name`, `blocktype`, `status`. Then add:

| Field | Why |
|-------|-----|
| `includes[].id` | Authoritative country alpha-2 (quote `'NO'` for Norway) |
| `includes[].status` | Key from `data/schemas/includes_status.yaml` |
| `includes[].joined` / `left` | ISO dates when known |
| `membership_count` | Country-member count unless `membership_count_type` says otherwise |
| `wikidata_id` | Or an exclusion entry in `data/schemas/wikidata_exclusions.yaml` |
| `topics` | Keys from `data/schemas/topics.yaml` |
| `provenance` | At least four field-level entries |
| `last_verified` | `YYYY-MM-DD` of the source check (12-month advisory SLA) |

## 3. Validate

```bash
python scripts/validate_intblocks.py --json
```

Exit codes: `0` = no errors (warnings allowed); `1` = errors, or warnings with
`--fail-on-warning`. Fix every `errors[]` item; use `fix_hint` when present.

Also run:

```bash
python scripts/validate_countries.py --json
pytest tests/
ruff check internacia_builder/ scripts/ tests/
```

## 4. Changelog and PR

Add a line under `[Unreleased]` in `CHANGELOG.md` (new intblock = MINOR when
released). In the PR: cite the official membership source, do not hand-edit
`data/datasets/`. Maintainers rebuild exports.

If the change needs a new `blocktype`, a schema field, or an id rename, stop and
open an OpenSpec proposal first ([openspec-quickstart.md](openspec-quickstart.md)).

## Related

- [contribute.md](contribute.md) — full checklist
- `.agent/workflows/edit-intblock.md` — edit an existing record
- [intblock-inclusion-policy.md](../intblock-inclusion-policy.md) — id and category rules

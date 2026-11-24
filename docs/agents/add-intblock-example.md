# Worked example: add an intblock

This walkthrough shows how to add a new organization record. Use it together
with the checklist in [contribute.md](contribute.md). A compact real record to
copy from is [`data/intblocks/water/SCHELDTCOM.yaml`](../../data/intblocks/water/SCHELDTCOM.yaml):
a treaty-based commission with 3 members whose roster, founding and entry-into-force dates
come from a treaty database, field-level `provenance`, `last_verified`, and `notes` that
explain the id choice (`ISC` already belongs to another organization) and how sub-national
parties were recorded.

Do **not** invent membership. If the official roster is not in hand, stop: do not
add the record yet. Leave `includes` empty only when the entity has no country
roster by design (a subsidiary office, a fund, an organization of NGOs), and then set
`membership_applicability: not_applicable`; an empty `includes` without it is a
validation warning, which fails CI.

## 1. Confirm it belongs

Read [intblock-inclusion-policy.md](../intblock-inclusion-policy.md). Standing
IGOs, treaties with parties, durable forums, and named geographic sets are in
scope. Ad-hoc news coalitions and socioeconomic rankings are not. Discovery
catalogues and roster authorities are listed in
[intblock-sources.md](../intblock-sources.md) — do not invent membership.
How to search and improve records: [discovery.md](../discovery.md).

Pick:

- **`id`** — uppercase official acronym (`AUKUS`, `NATO`). See id rules in the
  inclusion policy. Filename stem must match `id` exactly.
- **Directory** — `data/intblocks/<primary-blocktype>/`. The folder name is the
  primary `blocktype` and must already exist in
  `data/blocktypes/blocktypes.yaml`. Additional types go in the `blocktype` list.
- **`scope_category`** — `igo` | `treaty_body` | `policy_forum` |
  `reference_enumeration` | `intergovernmental_body` | `non_state_organization`.
  The category describes the entity, not a country's role in `includes`.

## 2. Create the YAML

```text
data/intblocks/water/SCHELDTCOM.yaml
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
| `last_verified` | `YYYY-MM-DD` of the source check; required on new records (advisory SLA: 12 months, 6 for tier-1 organizations in `data/watch/rosters.yaml`) |

## 3. Validate

```bash
python scripts/validate_intblocks.py --json
```

Exit codes: `0` = no errors (warnings allowed); `1` = errors, or warnings with
`--fail-on-warning`. CI runs with `--fail-on-warning`, so fix every `errors[]` and
`warnings[]` item; use `fix_hint` when present. Only the date-based staleness warnings
(`last_verified` and provenance age) do not fail it.

Also run:

```bash
python scripts/validate_countries.py --json
python scripts/builder.py build
python scripts/check_generated_artifacts.py
pytest tests/
ruff check internacia_builder/ scripts/ tests/
python scripts/check_doc_counts.py
python scripts/check_markdown_links.py
```

Update current-count documentation and affected cookbook expectations for the
new record so those checks pass.

## 4. Changelog and PR

Add a `changelog.d/<slug>.md` fragment with an `### Added` entry (new intblock = MINOR
when released); do not edit `CHANGELOG.md` and do not write running totals such as
"(1304 intblocks)" (see [changelog.d/README.md](../../changelog.d/README.md)). In the PR:
cite the official membership source and do not hand-edit `data/datasets/`. Run the full
build; a new record normally leaves `data/datasets/` clean, because build manifests and
`datapackage.json` are not committed. CI rebuilds and checks the committed descriptors
against its own staging directory.

If the change needs a new `blocktype`, add it to `data/blocktypes/blocktypes.yaml`
first, with a `description` (see [contribute.md](contribute.md)); a new blocktype is a
MINOR change and needs no proposal. A new schema field or an id rename needs an OpenSpec
proposal first ([openspec-quickstart.md](openspec-quickstart.md)).

## Related

- [contribute.md](contribute.md) — full checklist
- [discover.md](discover.md) — find missing records / improve existing YAML
- `.agent/workflows/edit-intblock.md` — edit an existing record
- [intblock-inclusion-policy.md](../intblock-inclusion-policy.md) — id and category rules
- [discovery.md](../discovery.md) — hunt patterns and improvement loops
- [intblock-sources.md](../intblock-sources.md) — catalogues searched and roster authorities

# Change: Add the `artificial_intelligence` blocktype

## Why

Internacia has a growing set of artificial intelligence bodies, but no way to select them. `WAICO`, `PAXSILICA`, `CHIP4` and `GPAI` sit in two directories (`digital`, `forum`) and share only the broad `digital` or `technology` keys. Before this change, `list_contains(blocktype, 'digital')` returned 8 records: five of them are not AI bodies (`DEPA`, `DN`, `FOCONLINE`, `GFCE`, `UNIGF`), and `GPAI` is not among them. The `digital` scope note names artificial intelligence, so a contributor has no narrower key to choose. Several AI instruments with official rosters were also missing: the network of government AI safety institutes, the Hiroshima AI Process Friends Group, the OECD AI Principles, the US-led declaration on military AI, and the Council of Europe AI convention.

The taxonomy already uses secondary domain tags for this case. `cybersecurity` ("usually a secondary tag with digital") marks cyber bodies without moving them out of their primary directory.

## What Changes

- **New blocktype.** Add `artificial_intelligence` to `data/blocktypes/blocktypes.yaml`. Its scope note covers AI governance, safety and cooperation, including partnerships on AI compute and semiconductor supply chains, and says it is usually a secondary tag with `digital`. The `digital` scope note points AI bodies to the new key. The taxonomy grows from 82 to 83 blocktypes.
- **Retag four records.** `WAICO`, `PAXSILICA`, `CHIP4` and `GPAI` take `artificial_intelligence` as an additional blocktype. No record changes directory or primary blocktype, and `WAICO` keeps the deprecated `intorg` as its last value.
- **Add five sourced records** (1285 to 1290 intblocks after the main-branch additions `NCTTCA`, `ARABMASHREQROADS` and `EWEC`), each with `artificial_intelligence`, `last_verified` and field-level provenance:

  | id | Directory | `scope_category` | Roster |
  |---|---|---|---|
  | `NAAIMES` | `digital` | `policy_forum` | 9 countries and the EU, from NIST and the UK government |
  | `HAIPFRIENDS` | `digital` | `policy_forum` | 69 countries and the EU, from Japan's Ministry of Internal Affairs and Communications |
  | `OECDAIPRINCIPLES` | `digital` | `treaty_body` | 51 adherents, from the OECD Legal Instruments database |
  | `MILITARYAIDECLARATION` | `armscontrol` | `treaty_body` | 58 endorsing states, from the U.S. Department of State |
  | `COEAICONVENTION` | `agreement` | `treaty_body` | 2 parties (EU, BA), from the Netherlands treaty database |

- **Defer** the UN Group of Friends for International Cooperation on AI Capacity-building, because it publishes no member list.

## Impact

Under the versioning policy this ships as a MINOR release: one new taxonomy row, new records and new values in an existing list column.

- Affected specs: `intblocks-data-quality` (new requirement for the AI blocktype).
- Affected source:
  - `data/blocktypes/blocktypes.yaml`
  - `data/intblocks/digital/{WAICO,PAXSILICA,CHIP4}.yaml` and `data/intblocks/forum/GPAI.yaml`
  - five new records under `data/intblocks/{digital,armscontrol,agreement}/`
  - `data/schemas/wikidata_exclusions.yaml` (`NAAIMES`, `HAIPFRIENDS`)
- Affected documentation:
  - current-count files (`README.md`, `AGENTS.md`, `AGENTS.zh.md`, `llms.txt`, `llms.zh.txt`, `llms-full.txt`, `docs/ai-consumers.md`, `docs/architecture.md`, `docs/getting-started.md`, `docs/publishing-huggingface.md`, `data/datasets/README.md`)
  - `docs/query-examples.md` with `tests/test_documented_queries.py` (the `human_rights` topic recipe now returns 55 rows)
  - `CHANGELOG.md`
- Affected exports: `blocktypes` gains one row; `intblocks` and `memberships` gain the new records; `intblocks.blocktype` gains a value.
- Not breaking: no column is removed or retyped, no identifier changes, and no record changes its primary blocktype.
- Process note: the blocktype and the records were implemented on 2026-11-21 at the maintainer's direct request, before this proposal. Approval of this proposal confirms or reverses that work.

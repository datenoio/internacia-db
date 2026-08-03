# Change: Repair broken organization links and de-stale planning docs

## Why
The repository's canonical home is `github.com/datenoio/internacia-db` (confirmed by `git remote`), but 12 maintained files — including the README CI badge on line 3 — still link to `github.com/commondataio/internacia-*` URLs that return 404 (externally verified). The project's front door is broken for every consumer following the badge or the API/SDK links. In addition, `llms-full.txt` (2.7 KB) is billed as the extended index but is smaller than `llms.txt` (4.5 KB), `docs/improvement-plan.md` still says "Current release: v1.2.0" while the repo is at v1.9.0, `docs/strategy-and-user-needs.md` presents shipped Track A items (license, alias map, `_meta` table) as open gaps, `data/_legacy/` (6.5 MB of stale Airtable-era dumps) carries no warning for crawlers/agents, and the intblock category count claim ("63 categories") is misleading because one of the 63 directories (`data/intblocks/tourism/`) is empty — 62 categories actually contain records.

## What Changes
- Sweep `commondataio` → `datenoio` across the 12 affected files (`AGENTS.md`, `AGENTS.zh.md`, `ATTRIBUTION.md`, `README.md`, `docs/agents/query.md`, `docs/agents/zh/query.md`, `docs/ai-consumers.md`, `docs/improvement-plan.md`, `docs/query-examples.md`, `llms-full.txt`, `llms.txt`, `llms.zh.txt`), including the README badge; replace relative sister-repo links (`../internacia-api`) with absolute URLs.
- Complete the README countries schema table: add `centroid` and `parent_entity`, the `exceptionally_reserved` enum value, and list all 7 non-standard codes (its own policy doc already says 7).
- Resolve the category count: remove the empty `data/intblocks/tourism/` directory (or add its first record) and align the "categories" figure in `README.md`, `openspec/project.md`, and `docs/improvement-plan.md` with the populated-directory count.
- Fix `llms-full.txt` so it is a genuine superset of `llms.txt`, or remove it and drop references to it.
- Add prominent status banners to (or refresh) `docs/improvement-plan.md` and `docs/strategy-and-user-needs.md` so shipped work is not presented as open gaps.
- Add a one-line warning in `AGENTS.md` and `llms.txt` that `data/_legacy/` is obsolete and must not be consumed.

## Impact
- Affected specs: contributor-docs
- Affected code: `README.md`, `AGENTS.md`, `AGENTS.zh.md`, `ATTRIBUTION.md`, `llms.txt`, `llms-full.txt`, `llms.zh.txt`, `docs/agents/query.md`, `docs/agents/zh/query.md`, `docs/ai-consumers.md`, `docs/improvement-plan.md`, `docs/strategy-and-user-needs.md`, `docs/query-examples.md`, `openspec/project.md`, `data/intblocks/tourism/`

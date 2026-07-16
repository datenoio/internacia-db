# Change: Refresh stale documentation counts and fix repository hygiene

## Why
Documentation drifted from the data: README, `llms.txt`, and `docs/ai-consumers.md` still say 1,070 intblocks (actual 1,071); `openspec/project.md`, `docs/improvement-plan.md`, and `docs/strategy-and-user-needs.md` still say 252 countries / 1,057 intblocks / 51 categories. README claims only countries validation runs before export (both validators run), and `llms.txt` lists a `blocktypes.manifest.json` that is not produced. `dev/.DS_Store` and `dev/research/.DS_Store` are tracked with no `.DS_Store` ignore rule, and `.cursor/skills/internacia-contribute/SKILL.md` is untracked although README links to it. There is no internal-link checking, so these rot silently.

## What Changes
- Update all stated record/category counts across README, `llms.txt`, `docs/ai-consumers.md`, `openspec/project.md`, `docs/improvement-plan.md`, `docs/strategy-and-user-needs.md`, and `docs/enrichment.md` to current values (256 countries, 1,071 intblocks, 63 categories, 86 blocktypes).
- Correct the README build description to state that both country and intblock validation run before export, and reconcile the `llms.txt` `blocktypes.manifest.json` reference with actual build artifacts.
- Track `.cursor/skills/internacia-contribute/SKILL.md` (referenced by README).
- Add `.DS_Store` to `.gitignore` and untrack `dev/.DS_Store` and `dev/research/.DS_Store`.
- Fix leading/trailing whitespace in `region.value` for `CW`, `MF`, `SS`, `SX`, `VG` source files.
- Add a lightweight internal Markdown link checker to CI.

## Impact
- Affected specs: contributor-docs, dev-tooling
- Affected code: `README.md`, `llms.txt`, `docs/*.md`, `openspec/project.md`, `.gitignore`, `.github/workflows/`, `data/countries/{CW,MF,SS,SX,VG}.yaml`, `.cursor/skills/internacia-contribute/SKILL.md`

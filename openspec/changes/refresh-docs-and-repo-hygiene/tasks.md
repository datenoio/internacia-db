## 1. Refresh counts and descriptions
- [x] 1.1 Update intblock/country/category/blocktype counts in README, `llms.txt`, `docs/ai-consumers.md`
- [x] 1.2 Update counts in `openspec/project.md`, `docs/improvement-plan.md`, `docs/strategy-and-user-needs.md`, `docs/enrichment.md`
- [x] 1.3 Correct README to state both validators run before export
- [x] 1.4 Reconcile `llms.txt` `blocktypes.manifest.json` reference with actual artifacts

## 2. Repository hygiene
- [x] 2.1 Add `.DS_Store` to `.gitignore`
- [x] 2.2 `git rm --cached dev/.DS_Store dev/research/.DS_Store`
- [x] 2.3 Track `.cursor/skills/internacia-contribute/SKILL.md`
- [x] 2.4 Fix `region.value` whitespace in `data/countries/{CW,MF,SS,SX,VG}.yaml`

## 3. Link checking
- [x] 3.1 Add a lightweight internal Markdown link checker script or action
- [x] 3.2 Wire it into CI to fail on broken internal links

## 4. Validate
- [x] 4.1 Run `validate_countries.py` to confirm whitespace warnings cleared
- [x] 4.2 Run `openspec validate refresh-docs-and-repo-hygiene --strict`

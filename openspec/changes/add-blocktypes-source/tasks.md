## 1. Source relocation

- [ ] 1.1 Create `data/blocktypes/blocktypes.yaml` from current `data/datasets/blocktypes.yaml`
- [ ] 1.2 Update builder to read source and export derived blocktypes artifacts only
- [ ] 1.3 Add README note distinguishing source YAML from generated datasets

## 2. Validator and CI updates

- [ ] 2.1 Point blocktype taxonomy validation to source path
- [ ] 2.2 Ensure CI path filters include `data/blocktypes/**` if added

## 3. Migration

- [ ] 3.1 Remove or git-ignore duplicate hand-edits in `data/datasets/blocktypes.yaml` if generated-only
- [ ] 3.2 CHANGELOG entry for contributor path change
- [ ] 3.3 Run `openspec validate add-blocktypes-source --strict`

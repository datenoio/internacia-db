## 1. Governance and alias map

- [x] 1.1 Create `docs/topic-taxonomy.md` with governance rules (add, merge, deprecate) per report §3.2
- [x] 1.2 Add `data/schemas/topic_aliases.yaml` mapping the 11 synonym groups to canonical keys from report §3.2
- [x] 1.3 Document sports consolidation rule: `sports` primary, `sports_governance` for federations

## 2. Synonym consolidation (Critical)

- [x] 2.1 Migrate `climate` / `climate_change` → `climate_change` (23 records)
- [x] 2.2 Migrate `armscontrol` / `arms_control` → `arms_control` (21 records)
- [x] 2.3 Migrate humanitarian variants → `humanitarian` (7 records)
- [x] 2.4 Migrate `economy` / `economic` / `economic_cooperation` → `economy` (267 records)
- [x] 2.5 Migrate `law` / `legal` / `legal_development` → `law` (68 records)
- [x] 2.6 Migrate counter-terrorism variants → `counter_terrorism` (5 records)
- [x] 2.7 Migrate disaster variants → `disaster_relief` (5 records)
- [x] 2.8 Migrate `science` / `scientific_research` → `science` (49 records)
- [x] 2.9 Migrate `transport` / `transportation` → `transport` (61 records)
- [x] 2.10 Migrate sustainability variants → `sustainable_development` (6 records)
- [x] 2.11 Migrate cooperation variants → `regional_cooperation` where appropriate (3 records)

## 3. Sports and empty topics (Medium)

- [x] 3.1 Consolidate 19 sport-specific topic keys under `sports` / `sports_governance`
- [x] 3.2 Assign topics to 69 records with empty `topics` (prioritize 21 `acronym` records)
- [x] 3.3 Add validator warn for deprecated topic keys and empty `topics` list

## 4. Validation

- [x] 4.1 Run `validate_intblocks.py` and rebuild datasets
- [x] 4.2 Update CHANGELOG with topic migration table
- [x] 4.3 Run `openspec validate consolidate-topic-taxonomy --strict`

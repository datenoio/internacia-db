# Change: Add missing high-value intergovernmental organizations

## Why
A verified gap scan (dev/internacia-db-review.md, re-checked 2026-08-02 against the current source tree) confirmed the following bodies have no intblock record despite clear inclusion criteria being met by peer records: Codex Alimentarius Commission (189 members, the global food-standards body referenced by the WTO SPS agreement), Basel Committee on Banking Supervision (only a mention inside `bank/BIS.yaml`), Court of Justice of the EU, Inter-American Court of Human Rights and African Court on Human and Peoples' Rights (ECHR's two regional peers — `court/` has only 4 records), WADA (sports/ has IOC and FIFA but not the anti-doping regulator), and the UN Secretariat (three other principal organs exist). Separately, the International Criminal Court hides under the opaque slug `court/ICW.yaml` while `sports/ICC.yaml` is cricket — an entity-resolution trap the existing aliases mechanism can mitigate.

## What Changes
- Add new intblock records: `CODEX` (Codex Alimentarius Commission), `BCBS` (Basel Committee on Banking Supervision), `CJEU` (Court of Justice of the European Union), `IACTHR` (Inter-American Court of Human Rights), `ACTHPR` (African Court on Human and Peoples' Rights), `WADA` (World Anti-Doping Agency), and a UN Secretariat record with `partof: [UN]`.
- Each record ships with roster (where membership applies), wikidata_id, description, links, blocktype/topics, and provenance, meeting existing completeness gates.
- Add an `ICC_CRIMINAL → ICW` entry to the intblock aliases map (documentation-level alias, no id rename) to defuse the ICC entity-resolution trap.

## Impact
- Affected specs: intblocks-data-quality
- Affected code: new YAML under `data/intblocks/{unagency,bank,court,sports}/`, `data/datasets/intblocks_aliases.json` (via build), regenerated `data/datasets/`

## 1. New records
- [x] 1.1 `CODEX` — Codex Alimentarius Commission (FAO/WHO, 189 members) with roster and provenance
- [x] 1.2 `BCBS` — Basel Committee on Banking Supervision (45 members from 28 jurisdictions; document count semantics)
- [x] 1.3 `CJEU` — Court of Justice of the European Union in `court/`
- [x] 1.4 `IACTHR` — Inter-American Court of Human Rights in `court/`
- [x] 1.5 `ACTHPR` — African Court on Human and Peoples' Rights in `court/`
- [x] 1.6 `WADA` — World Anti-Doping Agency in `sports/`
- [x] 1.7 UN Secretariat record with `partof: [UN]`

## 2. Entity resolution
- [x] 2.1 Add `ICC_CRIMINAL → ICW` alias documentation via the aliases mechanism, with a note distinguishing cricket `ICC`

## 3. Validation
- [x] 3.1 `python scripts/validate_intblocks.py --json` — zero errors, completeness gates pass
- [x] 3.2 Rebuild artifacts and confirm counts updated across manifests and docs

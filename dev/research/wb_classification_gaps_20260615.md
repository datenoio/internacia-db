# World Bank classification gaps (2026-06-15)

Thirty-three entities lack World Bank `region` / `incomeLevel` / `lendingType` in the raw World Bank API because the Bank does not classify them. After M49 inference enrichment (`scripts/enrich_countries.py`), **247/252** records have `region`; the five Antarctic/uninhabited exceptions below remain intentionally unclassified.

## Unclassified (expected)

| Code | Name | Reason |
|---|---|---|
| AQ | Antarctica | Uninhabited continent |
| BV | Bouvet Island | Uninhabited territory |
| GS | South Georgia | Uninhabited territory |
| HM | Heard Island | Uninhabited territory |
| TF | French Southern Territories | Uninhabited territory |

## Previously missing (now inferred via subregion/continent)

AI, AX, BL, BQ, CC, CK, CX, EH, FK, GF, GG, GP, IO, JE, MQ, MS, NF, NU, PM, PN, RE, SH, SJ, TK, TW, UM, VA, WF — and similar territories.

Sourcing: UN M49 macro-region mapping in `infer_wb_classification()` with provenance `UN M49 inference`.

Reference: `dev/research/report_manus_20260615.md` §1.1

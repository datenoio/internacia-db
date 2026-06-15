# Intblocks gap backlog

Status values: `deferred`, `in_review`, `ready`, `shipped`, `excluded`

| ID | Name | Status | Notes |
|---|---|---|---|
| UNHRC | UN Human Rights Council | shipped | `data/intblocks/unagency/UNHRC.yaml` |
| UNSC | UN Security Council | shipped | `data/intblocks/political/UNSC.yaml` |
| UNGA | UN General Assembly | shipped | `data/intblocks/political/UNGA.yaml` |
| CHIP4 | Chip 4 Alliance | shipped | `data/intblocks/digital/CHIP4.yaml` |
| DEPA | Digital Economy Partnership Agreement | shipped | `data/intblocks/agreement/DEPA.yaml` |
| PEPFAR | US PEPFAR | shipped | `data/intblocks/health/PEPFAR.yaml` |
| MSF | Médecins Sans Frontières | shipped | `data/intblocks/humanitarian/MSF.yaml` |
| UNCITRAL | UN Commission on International Trade Law | shipped | `data/intblocks/unagency/UNCITRAL.yaml` |
| UNCLOS | UN Convention on the Law of the Sea | shipped | `data/intblocks/agreement/UNCLOS.yaml` |
| EPC | European Political Community | deferred | Scope review — initiative vs bloc |
| D10 | Democracies 10 | deferred | Scope review |
| BRICSPLUS | BRICS+ expanded | deferred | Post-2024 membership dynamics |
| G5SAHEL | G5 Sahel | shipped | `data/intblocks/military/G5SAHEL.yaml` (historical, dissolved 2023) |
| PANDEMICTREATY | WHO Pandemic Accord | deferred | Await finalized party list from WHO/UN Treaty Collection |
| GLOBALGATEWAY | EU Global Gateway | deferred | Initiative scope |
| PGII | Partnership for Global Infrastructure | deferred | Initiative scope |
| MSP | Mineral Security Partnership | excluded | Initiative; no stable membership model (2026-06 triage) |
| EPLO | European Public Law Organization | shipped | `data/intblocks/legal/EPLO.yaml` |
| FILAC | Fund for the Development of the Indigenous Peoples of Latin America and the Caribbean | shipped | `data/intblocks/intorg/FILAC.yaml` |

### Batch 1 triage (2026-06-15)

| ID | Decision | Rationale |
|---|---|---|
| EPC | deferred | Summit format; membership mirrors participating states — not a standing bloc |
| D10 | deferred | Informal democracy coalition; membership fluid |
| BRICSPLUS | deferred | Expanded BRICS format evolving post-2024 |
| GLOBALGATEWAY | excluded | EU program, not a membership organization |
| PGII | excluded | G7 infrastructure initiative, not a standing bloc |
| MSP | excluded | Mineral partnership initiative without fixed roster in source data |

### Batch 2 triage (2026-06-15)

| ID | Decision | Rationale |
|---|---|---|
| G5SAHEL | shipped | Historical record with `status: historical`, `dissolved: 2023-12-06`; see AES for successor track |

### Batch 3 triage (2026-06-15)

| ID | Decision | Rationale |
|---|---|---|
| PANDEMICTREATY | deferred | Treaty adopted 2025 but party sourcing needs UN Treaty Collection pass before YAML record |

Sourcing criteria template:

- **Standing IGO/bloc**: fixed membership list from official source, `status: formal`, `includes` required
- **Treaty**: parties from UN Treaty Collection, `blocktype: agreement`
- **Program/initiative**: document as `excluded` if no stable membership model

Reference: `dev/research/report_manus_20260615.md`, `dev/research/gaps_merged_20260528.md`

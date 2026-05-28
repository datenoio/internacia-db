# Merged Gap Report: Manus + Perplexity (2026-05-28)

## Sources

- `dev/research/gaps_manus_20260528`
- `dev/research/gaps_perplexity_20260528`

## Merge Approach

- Built a union of candidate records from both reports.
- Screened candidate IDs against existing files in `data/intblocks/**/*.yaml`.
- Classified each candidate as:
  - `ready_to_add`
  - `needs_review`
  - `update_existing`
  - `exclude`

## Immediate ID Conflicts Found

The following candidates already exist by ID and are **not new records**:

| Candidate ID | Existing file | Action |
| --- | --- | --- |
| `IGF` | `data/intblocks/intorg/IGF.yaml` | update existing if needed |
| `CEPI` | `data/intblocks/intorg/CEPI.yaml` | update existing tags/blocktypes if needed |
| `EAS` | `data/intblocks/wbgroup/EAS.yaml` | avoid ID reuse; use distinct ID for East Asia Summit |

## Batch 1 — Ready To Add (Implemented)

| ID | Name | Origin | Notes |
| --- | --- | --- | --- |
| `AMRO` | ASEAN+3 Macroeconomic Research Office | Manus | New IGO and financial cooperation body |
| `IPBES` | Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services | Manus | Strong fit for environment/science gap |
| `GGGI` | Global Green Growth Institute | Manus | Treaty-based intergovernmental organization |
| `ICCROM` | International Centre for the Study of the Preservation and Restoration of Cultural Property | Manus | Intergovernmental cultural organization |
| `UNIDROIT` | International Institute for the Unification of Private Law | Manus | Intergovernmental legal harmonization body |
| `ESM` | European Stability Mechanism | Manus | Euro-area intergovernmental financial institution |
| `ASEANPLUS3` | ASEAN Plus Three | Perplexity | Major East Asian regional framework |
| `WARSAWPACT` | Warsaw Pact | Perplexity | Historical Cold War military alliance |
| `SEATO` | Southeast Asia Treaty Organization | Perplexity | Historical military alliance |
| `CENTO` | Central Treaty Organization (Baghdad Pact) | Perplexity | Historical military alliance |
| `IPEF` | Indo-Pacific Economic Framework | Perplexity | Contemporary Indo-Pacific economic framework |

## Batch 2 — Second Pass (Implemented)

| ID | Name | Category |
| --- | --- | --- |
| `DANUBECOM` | Danube Commission | Manus (`DC` alias avoided) |
| `PERSGA` | Regional Organization for the Conservation of the Environment of the Red Sea and Gulf of Aden | Manus |
| `SACEP` | South Asia Co-operative Environment Programme | Manus |
| `NDPHS` | Northern Dimension Partnership in Public Health and Social Well-being | Manus |
| `AACB` | African Association of Central Banks | Manus |
| `SEACEN` | South East Asian Central Banks Research and Training Centre | Manus |
| `CILSS` | Permanent Interstate Committee for Drought Control in the Sahel | Manus |
| `LCBC` | Lake Chad Basin Commission | Manus |
| `CICOS` | International Commission of the Congo-Oubangui-Sangha Basin | Manus |
| `OMVG` | Gambia River Basin Development Organization | Manus |
| `OMVS` | Organisation for the Development of the Senegal River | Manus |
| `OKACOM` | Permanent Okavango River Basin Water Commission | Manus |
| `VBA` | Volta Basin Authority | Manus |
| `ZAMCOM` | Zambezi Watercourse Commission | Manus |
| `MGC` | Mekong-Ganga Cooperation | Manus |
| `C5PLUS1` | C5+1 Diplomatic Platform | Manus |
| `BBNJ` | BBNJ / High Seas Treaty | Manus |
| `EASTASIASUMMIT` | East Asia Summit | Perplexity (`EAS` ID conflict avoided) |
| `FIPIC` | Forum for India-Pacific Islands Cooperation | Perplexity |
| `V20` | Vulnerable Twenty Group | Perplexity |
| `SIDS` | Small Island Developing States | Perplexity |
| `COVAX` | COVAX | Perplexity |
| `AFRICACDC` | Africa Centres for Disease Control and Prevention | Perplexity |
| `GHSA` | Global Health Security Agenda | Perplexity |
| `ATT` | Arms Trade Treaty | Perplexity |
| `CCM` | Convention on Cluster Munitions | Perplexity |
| `BUDCONV` | Budapest Convention on Cybercrime | Perplexity |
| `JCPOA` | Joint Comprehensive Plan of Action | Perplexity |
| `OPENSKY` | Treaty on Open Skies | Perplexity |
| `GPAI` | Global Partnership on Artificial Intelligence | Perplexity |
| `FOCONLINE` | Freedom Online Coalition | Perplexity |
| `GFCE` | Global Forum on Cyber Expertise | Perplexity |
| `UNIGF` | Internet Governance Forum | Perplexity (`IGF` used by mining forum) |

### Batch 2 Updates To Existing Records

| ID | Change |
| --- | --- |
| `CEPI` | Added `humanitarian` blocktype (health-related coverage) |

## Still Deferred (Needs Review)

| ID | Reason |
| --- | --- |
| `EPC`, `EPC2022`, `D10`, `BRICSPLUS`, `MSP`, `GLOBALGATEWAY`, `PGII` | Initiative/project vs standing bloc scope |
| `PANDEMICTREATY` | Very recent treaty; party list and status need dedicated sourcing pass |
| `G5SAHEL` | Historical/dissolved status requires explicit modeling decision |
| `EPC`, `EPLO`, `FILAC`, `UNHRC`, `CIGEPS`, `BIC`, `NSMC`, `BLEU`, `C4`, `MOI` | Manus P2 scope/membership verification pending |

## Existing/Update Candidates (Not New Records)

| Candidate | Existing ID / treatment |
| --- | --- |
| Gulf Cooperation Council | already represented as `CCASG` |
| Energy Community | already represented as `ECSEE` |
| Indian Ocean Commission | already represented as `COI` |
| International Seabed Authority | already represented as `ISA_SEABED` |
| ICESCO / ISESCO | rename/alias update, not a new block |
| D-8 | already represented as `D8` |
| Community of Sahel-Saharan States | already represented as `CENSAD` |
| ITLOS | already represented as `ITLOS` |

## Exclusions

Candidates considered out of strict country/member-state block scope:

- `ICLEI`
- `CILC`
- `ICANN`
- `ILC`
- `UNISDR`/`UNDRR`
- Regional program initiatives without fixed country membership blocks

## Reconciliation Outcome

- Batch 1 added: **11 new records**
- Batch 2 added: **33 new records** + **1 existing record update** (`CEPI`)
- Total new records from gap implementation: **44**
- Still deferred: see **Still Deferred** section above
- Duplicate/alias items retained as update suggestions: **yes**

## Metadata And Taxonomy Pass (2026-05-28)

- Extended [`data/datasets/blocktypes.yaml`](data/datasets/blocktypes.yaml) with **34** blocktypes previously used in data but undefined (including `health`, `water`, `ocean`, `transport`, `cybersecurity`, `digital`, `climate`, and others).
- Enriched all **44** gap-added records with:
  - `wikidata_id` and wikidata `links`
  - `languages`, `headquarters` (where applicable), `acronyms`, `legal_status`, `topics`
  - aligned `blocktype` tags (e.g. `health`, `biodiversity`, `digital`, `cybersecurity`)
- Enrichment script: [`scripts/enrich_gap_records.py`](scripts/enrich_gap_records.py)

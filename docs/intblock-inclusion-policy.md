# Intblock inclusion policy

Defines what belongs in the intblocks dataset and how to classify records with
`scope_category`.

## Inclusion criteria

An intblock is included when it is useful as a **stable join target** for
membership, hierarchy (`partof`), or named reference sets used by other
records in this repository.

| Kind | Include? | Examples |
|------|----------|----------|
| Intergovernmental organization (IGO) | Yes | UN, NATO, AU, ASEAN |
| Treaty / convention with parties roster | Yes | UNFCCC, CBD, UNCLOS |
| Standing policy forum / process | Yes | G7, G20, ARF, FATF |
| Named geographic / set groupings | Yes, labeled `reference_enumeration` | SIDS, Maghreb, Caribbean |
| Country attribute partitions | **No** — use country fields | Traffic hand, DVD region, scripts, legal tradition, rail gauge, broadcast systems |
| Ad-hoc news coalitions / one-off summits | Usually no | Unless membership is durable and sourced |
| Socioeconomic rankings / indices | No | HDI lists, GDP leagues (out of country & intblock scope) |
| Government form / regime typology | No on countries; not as intblock membership | Optional vocab only: `data/vocabs/government_forms.yaml` |

### Attribute partitions → country fields

These classifications were previously inverted as intblocks and are now country
properties (with controlled vocabs under `data/vocabs/`):

| Former blocktype | Country field |
|------------------|---------------|
| `traffichand` | `car_side` (`left` \| `right`) |
| `writingdirection` | `writing_directions` |
| `writingsystem` | `writing_systems` |
| `dvdregion` | `dvd_region` |
| `teleregion` | `broadcast_systems` |
| `lawsystem` | `legal_systems` |
| `railgauge` | `rail_gauges` |
| `govform` | *(retired; vocab-only, not on countries)* |

Retired intblock ids map via `data/attribute_intblock_migrations.yaml`
(exported as `data/datasets/attribute_intblock_migrations.json`).

## `scope_category` values

| Value | Meaning |
|-------|---------|
| `igo` | Standing intergovernmental organization with secretariat/HQ |
| `treaty_body` | Treaty, protocol, or convention (parties are members) |
| `policy_forum` | Forum, process, or club without full IGO personality |
| `reference_enumeration` | Named geographic or set grouping (not attribute partitions) |

Optional field; high-visibility and `status: formal` records should set it.
Validation warns (non-blocking) when `status: formal` and `scope_category` is missing.

## Boundaries vs treaties in `partof`

`partof` expresses **organizational hierarchy**, not “established by treaty X”.
Treaty nesting (protocol → convention) is allowed. Organization → pure treaty
links should be described in text instead (see `partof` hierarchy validation).

Specialized UN agencies prefer `partof: UN` (not ECOSOC alone).

## Related

- [entity-classification-policy.md](entity-classification-policy.md)
- [ai-consumers.md](ai-consumers.md)
- [topic-taxonomy.md](topic-taxonomy.md)
- [enrichment.md](enrichment.md) — Wikidata completeness exclusions

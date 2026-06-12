## Context

Change 1 establishes validation and documents that `borders` uses alpha-3. This change fills the highest-impact empty profile fields identified in the Manus audit.

## Goals / Non-Goals

- Goals:
  - Non-zero population, area, timezones, and native_names for all entities where authoritative sources exist.
  - Structured indicators with year and source for reproducibility.
  - Enable strict completeness gates for former 100%-null fields.
- Non-Goals:
  - `entity_type` / `code_status` (Change 3).
  - HDI, GDP, or full `indicators` module (future change).
  - Adding disputed-entity profiles `XA`–`XN`.

## Decisions

### Decision: Structured indicator shape

```yaml
population:
  value: 331893745
  year: 2023
  source: World Bank
  source_id: SP.POP.TOTL
area:
  value: 9833517.0
  year: 2021
  source: World Bank
gini:
  value: 41.5
  year: 2020
  source: World Bank
```

PyArrow: struct with `value` (float64 for area; int64 for population), `year` (int64), `source` (string), optional `source_id` (string).

**Alternatives:** Bare integers (rejected—no provenance).

### Decision: Data sources

| Field | Primary source | Fallback |
|-------|----------------|----------|
| population | World Bank `SP.POP.TOTL` | Wikidata P1082 |
| area | World Bank / Wikidata P2046 | Manual for gaps |
| gini | World Bank `SI.POV.GINI` | Omit where unavailable |
| timezones | IANA tzdata country mapping | `timezone_status: not_applicable` |
| native_names | Wikidata labels by language | `other_names` where present |

Rate limiting: 0.1s between Wikidata API calls (match `validate_links.py`).

### Decision: Uninhabited territories

For `BV`, `HM`, `AQ` and similar: `timezones: []` with `timezone_status: not_applicable`; `borders: []` (not null) for islands without land borders.

### Decision: Gini sparsity

Gini MAY remain null for territories without World Bank coverage; completeness rule uses `max_null_rate` allowing partial coverage (e.g. 40%) with `mode: warn` for gini only.

## Risks / Trade-offs

- Parquet schema change breaks downstream consumers → migration note in CHANGELOG.
- Wikidata load → batch enrichment script with caching to JSON sidecar optional.

## Migration Plan

1. Update PyArrow schema and builder `clean_data()` for structs.
2. Run enrichment script with `--dry-run` review.
3. Flip completeness config to `error` for population, area, timezones, native_names.
4. Regenerate all dataset formats.

## Open Questions

- Cache Wikidata responses under `dev/cache/` or inline only in YAML?

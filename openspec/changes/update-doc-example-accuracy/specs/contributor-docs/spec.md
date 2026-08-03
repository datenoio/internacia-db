## ADDED Requirements

### Requirement: Documented example execution accuracy

Every executable example in maintained consumer documentation (`README.md`, `llms.txt`, `docs/query-examples.md`, `docs/query-examples.zh.md`, `docs/ai-consumers.md`, `docs/agents/query.md`) SHALL execute successfully against the current committed artifacts and return the documented result. Examples that filter on stored field values SHALL use the exact stored strings, and examples with deterministic results SHALL state an expected count that is asserted by a test.

#### Scenario: World Bank region example returns rows

- **WHEN** a consumer runs the documented World Bank region filter from `docs/query-examples.md` against `internacia.duckdb`
- **THEN** the query returns the documented non-zero row count

#### Scenario: Pandas example runs on a default install

- **WHEN** a consumer runs the documented pandas parquet snippet with a default `pip install pandas pyarrow` environment
- **THEN** the snippet executes without raising and yields the documented values

#### Scenario: Documented classification-gap figures match data

- **WHEN** documentation states how many entities lack World Bank `region`/`incomeLevel` or `adminregion` values
- **THEN** the stated figures equal the counts computed from the current countries artifact

### Requirement: Memory-bounded query recipes

Documented DuckDB query recipes SHALL execute within a bounded memory budget enforced by the documented-queries test suite, and SHALL NOT use unconstrained cross joins (`JOIN ... ON TRUE`) where an UNNEST-first rewrite produces the same result.

#### Scenario: Recipe completes under memory limit

- **WHEN** the documented-queries test suite runs every cookbook recipe with an explicit DuckDB `memory_limit`
- **THEN** every recipe completes without an out-of-memory error

#### Scenario: Cross-join recipe rewritten

- **WHEN** a membership-coverage recipe needs to combine `countries` with `intblocks.includes`
- **THEN** the documented form unnests `includes` before joining to `countries` instead of cross-joining whole tables

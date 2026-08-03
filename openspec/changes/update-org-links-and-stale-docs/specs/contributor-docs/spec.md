## ADDED Requirements

### Requirement: Canonical organization link integrity

All self-referential repository links in maintained documentation (README badge, API/SDK sister-repo links, agent indexes) SHALL point to the canonical GitHub organization of the repository's `origin` remote, and sister-repository links SHALL use absolute URLs that resolve when viewed on GitHub.

#### Scenario: README badge resolves

- **WHEN** a reader clicks the CI badge at the top of `README.md`
- **THEN** it opens the validate workflow of the canonical repository without a 404

#### Scenario: Sister repository links resolve

- **WHEN** a reader follows an API or SDK link from any maintained doc
- **THEN** the absolute URL resolves to the canonical `datenoio` repository

### Requirement: Agent index superset consistency

If an extended agent index (`llms-full.txt`) is published alongside `llms.txt`, it SHALL contain all information present in `llms.txt` plus additional detail; otherwise it SHALL NOT be published.

#### Scenario: Extended index is a superset

- **WHEN** a crawler prefers `llms-full.txt` over `llms.txt`
- **THEN** it receives at least all facts, counts, and gotchas present in `llms.txt`

### Requirement: Planning document freshness

Planning documents under `docs/` that describe roadmap state (`improvement-plan.md`, `strategy-and-user-needs.md`) SHALL carry a dated status header identifying the release they were written against, and items shipped in later releases SHALL be marked as shipped rather than presented as open gaps.

#### Scenario: Shipped item marked

- **WHEN** a reader consults a planning doc for an item that has since shipped (e.g. the alias map)
- **THEN** the item is marked shipped with a reference to the release or change that delivered it

### Requirement: Legacy data quarantine notice

Agent-facing indexes (`AGENTS.md`, `llms.txt`) SHALL warn that `data/_legacy/` contains obsolete pre-pipeline dumps that MUST NOT be consumed.

#### Scenario: Agent warned away from legacy dumps

- **WHEN** an agent reads `AGENTS.md` or `llms.txt` to locate data
- **THEN** it finds an explicit instruction not to read `data/_legacy/`

## Context

Nine Python scripts (~3,000 lines) operate as standalone files. Countries validation shipped with subprocess integration. Further quality work (intblocks validator, tests, enrichment) benefits from importable modules.

## Goals / Non-Goals

- Goals:
  - Importable validation and build modules for tests and CI.
  - Single HTTP client with consistent rate limiting.
  - Preserve existing CLI commands via shims during transition.
- Non-Goals:
  - Publishing to PyPI in this change.
  - Deep abstraction layers or plugin architecture.

## Decisions

### Decision: Package name

Use `internacia_builder` internally to avoid collision with `internacia-python` SDK, unless aligned with sibling project naming.

### Decision: Backward compatibility

Retain `python scripts/builder.py` via one-line shim importing package CLI for at least one release cycle.

## Risks / Trade-offs

- Large refactor touch surface → implement after `add-automated-tests` provides safety net.
- Duplicate `pyproject.toml` work with other changes → coordinate merges.

## Open Questions

- Final package name alignment with `internacia-python` maintainers?

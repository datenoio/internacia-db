# Change: Add blocktypes as first-class source

## Why

The blocktypes taxonomy lives in `data/datasets/blocktypes.yaml` alongside generated artifacts. Source and output are conflated; validators reference an output path that is also edited manually.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §1.5.

## What Changes

- Move blocktypes source to `data/blocktypes/blocktypes.yaml` (or `data/schemas/blocktypes.yaml`).
- Update `scripts/builder.py` to read from source path and write to `data/datasets/`.
- Update intblocks validator blocktype checks to reference source path.
- Document source vs generated layout in README and CONTRIBUTING.

## Impact

- Affected specs: `intblocks-data-quality` (modified), `intblocks-build` (modified)
- Affected code: `data/blocktypes/`, `data/datasets/`, `scripts/builder.py`, validators
- Breaking: Path change for contributors editing blocktypes (document in CHANGELOG)

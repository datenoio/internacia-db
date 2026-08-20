# Blocktypes taxonomy

Authoritative list of valid `blocktype` values for intblock records.

The **directory name** under `data/intblocks/` is the record's primary `blocktype`.
The YAML `blocktype` list may include extra keys. Do not add a folder without a
matching taxonomy entry.

Edit `blocktypes.yaml` in this directory, then run validation and rebuild:

```bash
python scripts/validate_intblocks.py
python scripts/builder.py build
```

The build copies this file to `data/datasets/blocktypes.yaml` and exports compressed artifacts (`blocktypes.parquet`, `blocktypes.yaml.zst`, etc.).

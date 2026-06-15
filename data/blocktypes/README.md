# Blocktypes taxonomy

Authoritative list of valid `blocktype` values for intblock records.

Edit `blocktypes.yaml` in this directory, then run validation and rebuild:

```bash
python scripts/validate_intblocks.py
python scripts/builder.py build
```

The build copies this file to `data/datasets/blocktypes.yaml` and exports compressed artifacts (`blocktypes.parquet`, `blocktypes.yaml.zst`, etc.).

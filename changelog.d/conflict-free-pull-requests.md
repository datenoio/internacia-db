### Changed

- Build manifests (`*.manifest.json`) and `datapackage.json` are no longer committed under
  `data/datasets/`. The build still writes them, and every GitHub Release still ships them:
  read them from the latest release or run `python scripts/builder.py build`. They carried
  per-build checksums, sizes, row counts and build identity, so every pair of open data pull
  requests conflicted on them. `contract.json`, the alias files, `border_status.json` and
  `attribute_intblock_migrations.json` stay committed.
- Documentation states the intblock count rounded down to the hundred (`1300+`);
  `scripts/check_doc_counts.py` reads the built manifests and checks that figure.
- Changelog entries go in `changelog.d/<slug>.md` fragments, which the release train merges
  into the release section (see `changelog.d/README.md`).
- `scripts/diff_countries_baseline.py` compares the built manifests with the baseline ref's
  source record counts and committed `contract.json` schema hashes.

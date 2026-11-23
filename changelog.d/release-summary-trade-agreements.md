### Fixed

- The release data-change summary and the `data` section of `migration.vX.Y.Z.json` now count
  trade agreement records: ids added, removed and changed since the previous release. Before, the
  release train did not read `data/trade_agreements/`. The release level rules are unchanged.

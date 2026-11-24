### Added

- Observers and partners on 11 intblocks, taken from each organization's own observers or partners
  page and checked on 2026-11-24: `ASEAN` (27 Dialogue, Sectoral Dialogue and Development
  Partners), `OAS` (75 Permanent Observers), `OSCE` (12 Asian and Mediterranean Partners for
  Co-operation, including Qatar from 22 October 2026), `PIF` (21 Forum Dialogue Partners and 9 Forum
  Observers), `SAARC` (9 Observers), `ALADI` (29 Observers), `CPLP` (35 Associate Observers),
  `IOR-ARC` (12 Dialogue Partners), `BEACST` (9 Observers), `EITI` (10 supporting countries) and
  `IDEA` (Japan, the only Observer). They use `status: observer` or `status: partner`, give the
  organization's category in `note`, and do not count towards `membership_count`.

### Changed

- `EITI` adds Solomon Islands, readmitted as an implementing country on 16 September 2026
  (56 implementing countries).
- `BEACST` lists Finland as a `former_member`: the Finnish Government announced in November 2024
  that it would leave after 2025, and barents-council.org no longer lists it. Russia's withdrawal
  is dated 18 September 2023.
- The ASEAN roster recipes in `docs/query-examples.md`, `docs/query-examples-polars.md` and
  `docs/query-examples-r.md` filter on `status = 'member'`, since the record now also lists
  partners.

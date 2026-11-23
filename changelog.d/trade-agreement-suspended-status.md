### Added

- `suspended` value for trade agreement `status` (and `country_trade_agreements.agreement_status`):
  negotiations that were launched and then suspended, paused or put on hold without being
  formally ended. A `suspended` record has no `in_force` or `provisional_application` date and
  is not an intblock candidate. An agreement in force whose application is suspended keeps
  `in_force`. Both enums are open, so this is a MINOR contract change with no `schema_hash`
  change; consumers that filter `status = 'negotiating'` for live talks no longer get frozen
  ones. OpenSpec change `add-suspended-trade-agreement-status`.

### Changed

- `EFTATSOUZ` (EFTA-Russia/Belarus/Kazakhstan, suspended after 11 rounds since 2011) and
  `EFTADZ` (EFTA-Algeria, on hold since 2008) move from `negotiating` to `suspended`.
  `EFTATSOUZ` now cites the EFTA page for its status and parties and moves from `catalogue` to
  `official` verification.

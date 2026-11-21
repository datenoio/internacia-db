### Changed

- The `last_verified` rule for changed rosters now accepts a record that keeps the base's
  `last_verified` when that date is today. A pull request that re-verified a roster on the same day
  another merge stamped it (for example after the tier-1 `joined` backfill) had no later true date
  to set, so validation failed. A roster change on any later day must still update the date.

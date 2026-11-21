### Changed

- CI fails on validator warnings: both validation steps run with `--fail-on-warning`. The
  date-based staleness warnings (`last_verified` age, provenance age, border status age) are
  still reported but do not fail it, because they appear as time passes without any change
  to the data.

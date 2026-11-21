### Changed

- The `validate` workflow runs the test suite in parallel with `pytest-xdist` (`-n auto`;
  `pytest-xdist` is pinned in `requirements-dev.txt`). Python 3.11, 3.12 and 3.13 still
  each build and test their own artifacts, but only 3.12 runs the second build for the
  reproducibility check and measures coverage against the `fail_under` gate.

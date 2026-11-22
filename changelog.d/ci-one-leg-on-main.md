### Changed

- A push to `main` runs the `validate` workflow on Python 3.13 only, the leg with the data
  checks and the uploaded reports. Its pull request already passed all three legs.
- A pull request that changes only `openspec/`, `dev/` or `website/` skips the build, the
  tests and the data checks in `validate`. It still runs the Markdown link check, and its
  `validate (3.11/3.12/3.13)` legs still report as required checks.
- The `validate` workflow installs dependencies with `uv pip install` instead of `pip`,
  which saves 15–25 seconds per leg.

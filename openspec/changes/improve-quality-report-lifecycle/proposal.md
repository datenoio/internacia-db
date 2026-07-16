# Change: Run quality analysis in CI, de-noise it, and fix report lifecycle

## Why
The quality analyzer exists but never runs in CI, so regressions are invisible. Its `DUPLICATE_LINK` rule is noisy: `scripts/builder.py` converts country TLDs like `.fr` into `http://.fr` pseudo-URLs that are then flagged as duplicate links, burying real duplicate-entity signals. Checked-in `dataquality/` reports are stale (2026-06-14, 245 issues) while a fresh run (2026-07-09, 93 issues) sits untracked in `dataquality/fresh_run/`, so readers cannot tell which is authoritative.

## What Changes
- Run `scripts/builder.py analyze-quality` in CI, publish the report as a workflow artifact, and fail only on CRITICAL/IMPORTANT priority issues (configurable).
- Fix the duplicate-link rule: stop injecting country `tld` values as pseudo-URLs, classify duplicate links by link type, allow expected shared domains and parent/child relationships, and separate "possible duplicate entity" from "shared external citation" in the output.
- Define the `dataquality/` lifecycle: reports are regenerated on release or published as CI artifacts rather than accumulating stale tracked copies; if any report stays tracked, a freshness check validates its header counts against current source counts. Remove the parallel `fresh_run/` directory.

## Impact
- Affected specs: countries-data-quality, intblocks-data-quality
- Affected code: `scripts/builder.py` (analyzer + duplicate-link rule), `.github/workflows/validate.yml`, `dataquality/`

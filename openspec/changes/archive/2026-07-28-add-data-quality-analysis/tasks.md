## 1. Implementation

- [x] 1.1 Implement quality check rules/functions in `scripts/builder.py` for country data.
- [x] 1.2 Implement quality check rules/functions in `scripts/builder.py` for intblocks data.
- [x] 1.3 Implement command execution structure, walking both datasets and collecting issues.
- [x] 1.4 Implement report formatting and file generation logic (full report, JSONL, priority, country, and rule groupings).
- [x] 1.5 Add `--check-http` and `--check-wikidata` flags to the command to support optional deep validation.

## 2. Verification

- [x] 2.1 Manually verify reports generated under default `dataquality/` directory.
- [x] 2.2 Verify custom output directory behavior with `--output` parameter.
- [x] 2.3 Run strict OpenSpec validation via CLI.
- [x] 2.4 Verify all unit tests continue to pass and build output is correct.

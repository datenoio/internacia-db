# Intblock topic taxonomy governance

This document defines how topic keys on intblock records are added, merged, and deprecated.

## Principles

1. **Canonical keys** — Use stable snake_case keys (`economy`, `climate_change`, `human_rights`).
2. **Avoid synonyms** — Do not introduce near-duplicates (`economic` vs `economy`). Check `data/schemas/topic_aliases.yaml` first.
3. **Minimum assignment** — Every intblock record must have at least one topic, including acronyms and government-form groupings.
4. **Sports** — Use `sports` for sport/event records; use `sports_governance` for federations and leagues.

## Adding a topic

1. Search existing keys in `data/intblocks/**/*.yaml` and `topic_aliases.yaml`.
2. Prefer reusing a canonical key over creating a new one.
3. Add the key as `{key, name}` on records; `name` is a human-readable label.
4. If the key is genuinely new, document it in a PR description.

## Merging / deprecating

1. Add a mapping in `data/schemas/topic_aliases.yaml` (`deprecated → canonical`).
2. Migrate all YAML sources in one PR.
3. Keep deprecated keys in the alias file for one release cycle; `validate_intblocks.py` warns on deprecated usage.

## Validation

- Empty `topics` lists emit warnings (ratcheting to error per completeness config).
- Deprecated keys emit warnings referencing the canonical replacement.

## References

- Manus data-quality report: `dev/research/report_manus_20260615.md` §3.2
- OpenSpec change: `consolidate-topic-taxonomy`

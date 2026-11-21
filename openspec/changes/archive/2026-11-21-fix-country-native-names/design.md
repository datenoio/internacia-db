# Design: native_names from each entity's own languages

## Context
`native_names` was filled once from Wikidata labels and aliases in English and the UN languages
(see proposal). The type `map<string, struct<official, common>>` is part of the data contract and is
read by `internacia-python` (`NativeName` TypedDict with both fields optional; `search` matches
`native.common`). This change keeps the type and redefines the content.

## Goals / Non-Goals
- Goals: endonyms only; a clear source for each variant; deterministic selection; one script per
  language per entity; exonyms only in `other_names`.
- Non-Goals: transliterations, historical names, regional or minority-language names that are not
  in `languages[]`, and fixing `languages[]` itself (except where noted under Migration).

## Decisions

### Keys follow `languages[]`, not Wikidata P37
`languages[]` is the dataset's own reference list, and 87 records differ from Wikidata P37
(official language). P37 also lists sign languages (`asq` for AT, `asf` for AU, `bzs` for BR),
which have no written names. No `languages[]` entry is flagged `official` (all 413 leave it
unset), so every listed language qualifies.

Alternatives considered:
- **Keep the UN-language keys and only fix official/common.** This is less churn, but the field
  stays misnamed and duplicates `other_names`. Wikidata rarely has P1448 in a foreign language, so
  most `official` values would be null.
- **Key by Wikidata P37.** This adds sign languages and disagrees with `languages[]` on 87 records.

### Value selection (per entity, per language L)
1. Wikidata language codes for L come from `data/vocabs/language_codes.yaml`, tried in order (for
   example `nor` → `nb`, `nn`, `no`). For `zh`, the entity decides: CN `zh-hans`, `zh-cn`; SG
   `zh-hans`, `zh-sg`; TW `zh-tw`, `zh-hant`; HK `zh-hk`, `zh-hant`; MO `zh-mo`, `zh-hant`; others
   `zh-hans`, then `zh`.
2. `official`: the P1448 statements in those codes, skipping deprecated statements and any with an
   end time (P582), ordered by code, then preferred rank first, then statement order. Take the
   first value that differs from `common`, or the first value if all are equal.
3. `common`: the Wikidata label in the first code that has one. If it equals `official`, use the
   first P1705 value in those codes that differs from `official` (CN 中华人民共和国 → 中国, TW
   中華民國 → 臺灣).
4. Omit a missing value, and the entry when both are missing. Values are stored verbatim (US
   P1448 is "the United States of America"; see Open Questions). Keys are sorted.

### Empty maps
Completeness keeps `native_names` at `mode: error`. `is_null_field` accepts `{}` when `languages[]`
is empty, mirroring `timezone_status: not_applicable`. A record with languages but no entries
remains an error and needs either data or a vocabulary fix.

## Dry run (Wikidata, 2026-11-19, before vocabulary overrides)
- 245 of 256 records get at least one entry; 370 entries in total (now 1504).
- 57 entries have no P1448, so `official` is null (for example IN `ta`). 5 have no label.
- `en` is kept for 91 records.
- 11 records come out empty. AN, AQ, JG, XA, XK, XN, XS and XT have no `languages[]`. RO, SJ and BV
  fail on the code collisions that the vocabulary fixes.
- 34 language entries use codes with no Wikidata P220 match (for example `ber`, `smi`, `kon`, `lin`,
  `gsw`, `fil`). The vocabulary maps or excludes each one explicitly.

Samples: DE `de` {Bundesrepublik Deutschland, Deutschland}; CH `fr`/`it`/`rm` {Confédération suisse,
Suisse}, {Confederazione svizzera, Svizzera}, {Confederaziun svizra, Svizra}; BY `be` and `ru`; BE
`de`, `fr`, `nl`; HK `en` and `zh` (traditional).

## Result (applied 2026-11-19)
After the vocabulary and the `languages[]` fixes (ES `glg`, BZ `bzj`, NA `naq`, GG `nrf`; CH adds
`deu`, XK adds `sqi` and `srp`): 249 of 256 records have entries, 388 in total. 68 entries have no
`official` and 3 have no `common`. `en` is kept for 91 records. The 7 empty maps are the records
with no `languages[]` (AN, AQ, JG, XA, XN, XS, XT). The vocabulary has 153 codes; 10 yield no
names (collective codes `ber`, `khi`, `smi`; `arc`; sign languages `nzs`, `zib`; `bwg`, `kwn`,
`ndc`, `zdj`, which Wikidata has no label language for).

## Risks / Trade-offs
- Consumers lose exonym lookups through `native_names`. Mitigation: `other_names` already carries
  them, the SDK `search` is extended first, and the change ships in a MAJOR with migration notes.
- Wikidata P1448 coverage is uneven. Mitigation: null `official` is allowed and reported by the
  completeness report, not hidden.
- `languages[]` has its own gaps (CH lists `gsw` but not `deu`; XK has none). These surface
  directly in `native_names`. Mitigation: fix them as separate, sourced data changes.

## Migration
1. Merge the SDK change that adds `other_names` to `search`.
2. Land the vocabulary, the enricher and the rule; regenerate all 256 records in one PR with a
   per-record diff summary.
3. Add `languages[]` for XK (`sqi`, `srp`) and review CH (`deu`) in the same PR, with sources.
4. Release as part of the next MAJOR; document the change in CHANGELOG and `docs/data-contract.md`.

## Open Questions
- Strip a leading English article from P1448 ("the United States of America")? Values stay
  verbatim for now.
- Keys stay sorted, as before; ordering by `languages[]` was not adopted.

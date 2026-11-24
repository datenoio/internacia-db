### Fixed

- Documentation: the Python SDK status now describes `internacia` 0.5.0 on PyPI, which reads
  data contracts 3.x and 4.x and refuses a 5.x database unless `check_contract=False`; the
  snippets that open a downloaded `internacia.duckdb` pass that flag.
- Documentation: README, the architecture page, getting started, the agent query guide,
  `llms.txt` and the LLM scenarios (new scenario 29) cover the trade agreements registry, and
  CONTRIBUTING has editing rules for `data/trade_agreements/` and
  `data/borders/border_status.yaml`.
- Documentation: the R cookbook runs again (`tidyr::unnest` instead of
  `unnest_longer() |> hoist()`, no `list_contains`, aliases filtered on `reason`), and stale
  expected counts in the DuckDB, R, Observable and Chinese cookbooks match the current data.
- Documentation: contributor instructions that failed validation are corrected (`year` is
  omitted, not `null`; topic keys come from `data/schemas/topics.yaml`; an empty `includes`
  needs `membership_applicability: not_applicable`), and the release and Hugging Face guides
  describe the release train, the `CITATION.cff` check and the MAJOR release path.
- Documentation: the discovery checklists say which rejected agreements belong in the trade
  agreements registry, the AI consumer guide lists every dataset and says which ones `_meta`
  covers, the `last_verified` SLA names the 6-month tier-1 window, a new blocktype and the
  changelog fragment rule read the same in every guide, the website guide describes the
  Pages workflow, and the worked example copies `SCHELDTCOM` instead of `AUKUS`.

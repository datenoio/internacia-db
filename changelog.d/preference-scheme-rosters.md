### Added

- 45 preference schemes from the WTO Preferential Trade Arrangements Database (walked
  2026-11-23) in `trade_agreements`, all `verification: catalogue`:
  - 29 schemes: the national GSP schemes (`EU-GSP`, `JP-GSP`, `US-GSP`, `GB-DCTS`, `EAEU-GSP`
    and others), the LDC-only schemes (`IN-DFTP`, `KR-LDC`, `CL-LDC` and others), and 6 other
    programmes (`EU-ATM-WB`, `US-ATPA`, `US-NTPP` and others);
  - 16 sub-schemes, such as `EU-GSP-EBA`, `NO-GSP-ZERO`, `CA-GSP-LDCT` and `AGOA-APPAREL`.

  Each record lists its grantor and the beneficiaries of the scheme's latest version. Its
  provenance gives that version's date: some lists are old, the EU GSP list is from 2017-06-29.
  China's LDC scheme is not added, because the database lists no beneficiaries for it.
  (OpenSpec `add-preference-scheme-rosters`.)
- Party roles:
  - `parties[].role` (`grantor`, `beneficiary`) on preference schemes;
  - a `role` column in `trade_agreement_parties` and `country_trade_agreements`, which is
    `party` on every reciprocal agreement.
- `parent` in `trade_agreements`: it links a sub-scheme to its scheme, and a national scheme
  to the `GSP` framework (`GSP` → `EU-GSP` → `EU-GSP-EBA`, `GSPPLUS`).
- `wto_pta_ids` in `trade_agreements`: the PTA Database ids, a list. `AGOA`, `CBERA`,
  `CARIBCAN` and `SPARTECA` have theirs now.
- Validation:
  - `TRADE_AGREEMENT_PARTY_ROLE`: a preference scheme needs a grantor and a beneficiary, and
    a linked preference-scheme intblock may use only `contributor` and `recipient`;
  - `TRADE_AGREEMENT_PARENT`: a sub-scheme has the parent's grantors and a subset of its
    beneficiaries;
  - `DUPLICATE_WTO_PTA_ID`.

### Changed

- `country_trade_agreements` has about 2,800 more beneficiary rows and grantor rows (EU
  schemes expand to the 27 member states). Queries that count reciprocal trade links between
  countries should filter on `role = 'party'` or `agreement_type <> 'preference_scheme'`.
- `GSP` and `SPARTECA` intblocks:
  - the 16 GSP grantors are `contributor` instead of `participant`;
  - in SPARTECA, Australia and New Zealand are `contributor` and the 13 Forum Island Countries
    `recipient`, instead of `founding_member` and `member`.

  `memberships` shows the new statuses.
- The Lomé Conventions (`LOME-1975`, `LOME-1979`, `LOME-1984`) give the EU the role `grantor`
  and the ACP States the role `beneficiary`.
- Preference schemes are no longer reported as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`.

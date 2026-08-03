# Change: Correct verified roster errors in audited intblock records

## Why
An independent audit (dev/internacia-db-review.md) flagged factual roster errors; re-verification on 2026-08-02 against the current YAML and official sources confirmed six records need correction:

1. `political/AFUNION.yaml` — 54 members; the African Union has **55** including SADR (au.int). `EH` exists in `data/countries/` but is not linked.
2. `police/INTERPOL.yaml` — `membership_count: 206` with a 206-entry roster; Interpol has **196** members (interpol.int), including territory members Aruba, Curaçao, and Sint Maarten; `geographic_scope: regional` is wrong for a global body. (The audit's sub-claim that FM/PW are non-members is incorrect — both joined in 1986; current non-members are KP, TV, Kosovo, Taiwan, and SADR. Bermuda/Puerto Rico/American Samoa are sub-bureaus, not members.)
3. `political/CIS.yaml` — Georgia (withdrew 2009), Ukraine (ceased participation 2018), Moldova (withdrawing), and Turkmenistan (associate) are all listed as plain `member`, although the schema already supports `former_member` and `associate_member`.
4. `political/UN.yaml` — `geographic_scope: regional`, self-referential `recognition_status: "UN agency"`, stub description, no observer entries for PS/VA, and `suborganizations` lists only 2 entities although 36 `unagency/` records exist.
5. `bank/AIIB.yaml` — `membership_count: 111` but only 35 `includes` rows.
6. `sports/ICC.yaml` (cricket) — `membership_count: 110` versus 217 unique `includes` rows.

The audit's OPEC claim ("UAE missing, should be 12") was re-verified and is **stale**: the UAE left OPEC on 2026-05-01 and the current 11-member roster in `energy/OPEC.yaml` matches the official list, so OPEC is intentionally excluded from this change (adding AE/AO as `former_member` entries is optional enrichment).

## What Changes
- `AFUNION`: add `EH` (SADR) as member with joined date; set `membership_count: 55`.
- `INTERPOL`: rebuild roster to the 196 official members with entry dates; represent territory members (`AW`, `CW`, `SX`) per the includes contract; set `geographic_scope: global`; fix `membership_count`.
- `CIS`: set `GE` and `UA` to `former_member` with `left` dates, `TM` to `associate_member`, and annotate `MD`'s withdrawal process; adjust `membership_count`.
- `UN`: set `geographic_scope: global`; replace the self-referential `recognition_status`; write a substantive description; add `PS` and `VA` with `status: observer`; link `suborganizations` to the existing `unagency/` records (36) per the UN organ hierarchical linkage requirement.
- `AIIB`: complete the roster to the ~110 approved members (or set `membership_count` to the roster the record actually carries with a documented rationale).
- `sports/ICC`: reconcile roster and count against the official ICC membership list (12 full members + associates); remove entries that are not members.
- Add provenance entries (source + retrieved_at) for every corrected field.

## Impact
- Affected specs: intblocks-data-quality
- Affected code: `data/intblocks/political/AFUNION.yaml`, `data/intblocks/police/INTERPOL.yaml`, `data/intblocks/political/CIS.yaml`, `data/intblocks/political/UN.yaml`, `data/intblocks/bank/AIIB.yaml`, `data/intblocks/sports/ICC.yaml`, regenerated `data/datasets/`

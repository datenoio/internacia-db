### Added

- `includes[].joined` dates for 21 tier-1 organizations (`data/watch/rosters.yaml`) that had
  none: 891 entries, checked on 2026-11-21. Affected organizations: UN, EU, NATO, AFUNION,
  ECOWAS, OECD, WTO, COMMONWEALTH, OIC, G-20, G7, SCO, CIS, LAS, CELAC, SAARC, APEC, OAS,
  CARICOM, SADC and COE. Each date comes from the organization's official member list and
  keeps the precision of that list. Where the official list could not be read, the date comes
  from an archived copy of the organization's own page (OAS, LAS) or from government treaty
  registers (OECD). Four entries stay undated because their official sources conflict: AFUNION
  KE and AO, and CIS AZ and MD. The reviewed values are in `data/schemas/includes_joined_tier1.yaml`.
  `scripts/backfill_includes_joined.py` applies them. It runs as a dry run by default and
  stops on any conflict. It adds provenance and sets `last_verified`.

### Fixed

- `ECOWAS` was missing Mauritania (`MR`), one of the 15 signatories of the 1975 Treaty of Lagos.
  It is now listed as `former_member`, joined 1975-05-28 and left 2000-12, per the ECOWAS
  Creation (History) page. The page also says Mauritania signed an associate-membership
  agreement in August 2017. That agreement is kept in the entry's note, because it is not
  membership.

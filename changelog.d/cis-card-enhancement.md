### Changed

- `CIS` (Commonwealth of Independent States) checked on 2026-11-21 against the CIS Charter, the
  CIS portal, Wikidata and news on Moldova's withdrawal. The roster keeps nine members, `TM` as
  `associate_member` and `GE` and `UA` as `former_member`, with `joined` dates for all twelve:
  8 December 1991 for `BY`, `RU` and `UA`, 21 December 1991 (Alma-Ata Protocol) for the other
  signatories, and 3 December 1993 for `GE`.
  - `MD` stays `member` with a note: it deposited its withdrawal notifications on 8 April 2026,
    so under Charter Article 9 it leaves on 8 April 2027.
  - `UA` now has `left: 2018-05-19`, the decree that ended its participation in the statutory
    bodies (was `2018`).
  - `GE` is removed from `founding_members`: it joined in 1993, after the Alma-Ata Protocol.
    The eleven Alma-Ata signatories remain.
  - The headquarters is now the Executive Committee at 17 Kirova Street, Minsk, with
    coordinates. The website moves to `https://cis.minsk.by/`, and the CIS portal, the Russian
    Wikipedia article and Wikidata are linked.
  - Acronyms gain their language tags from Wikidata P1813, and the `ru` entry `CIS` is
    dropped. Two traditional Chinese duplicates are dropped too. The French name is capitalized.
  - New fields: `geographic_scope`, `regions`, `headquarters`, `secretariat` (with the Moscow
    branch), `suborganizations` (IACIS, ECCIS, CISSTAT, IAC, EASC, IFESCCO), `legal_status`,
    `recognition_status` (UN General Assembly observer, resolution 48/237), `official_documents`,
    a full `description` and `notes`, 21 `other_names` languages, and the `security` and
    `trade` topics. Field-level `provenance` is added for each.
  - The documented query count of `former_member` rows with `joined` rises by two (`UA` and
    `GE` gain `joined`); the `membership_count` mismatch count is unchanged.

### Changed

- `ITU` checked on 2026-11-21 against the ITU Member States directory. The 194 Member States
  are unchanged.
  - Every member has `joined` set to its ITU "Member Since" date. Estonia, Latvia and Lithuania
    use the date their membership resumed in 1991-1992, with the interwar year in a `note`.
  - Palestine (`PS`) is an `observer` under Plenipotentiary Resolution 99 (Rev. Dubai, 2018).
  - The record also gets the founding date 1865-05-17 (International Telegraph Convention),
    `active_period` from 1866-01-01 and `previous_names` (International Telegraph Union). The 20
    signatories of 1865 are listed as 16 present-day `founding_members`, mapped as ITU's
    history portal does. It also gets `secretariat`, `recognition_status` (UN agreement of 1947,
    in force 1949), the six official languages, the Constitution, Convention, Radio Regulations
    and International Telecommunication Regulations as `official_documents`, `social_media`,
    `notes` and source-backed `provenance`.
  - `telecommunications`, `standardization` and `connectivity` are added to `topics`.
- Documented recipe expectations in `docs/query-examples.md` now reflect these changes:
  `PS` reaches five observer seats in "Countries with many observer seats", and the UPU and
  ITU rosters now differ from their `membership_count` in "Declared vs actual roster size".

### Fixed

- `UPU` checked on 2026-11-21 against the UPU member countries list and its 192 member pages.
  - Cook Islands (`CK`) and Niue (`NU`) were listed as members. The UPU covers them under New
    Zealand's membership, so they are now `represented`. `AW` is added as the coded `member` for
    the joint member "Aruba, Curaçao and Sint Maarten". The roster still has 190 sovereign-state
    members.
  - 42 territories that UPU member pages list under another member (Constitution art. 23) are
    `represented`. They include the UK Overseas Territories, which form one UPU member without a
    single ISO code. `membership_count` stays 192, with `membership_count_type: mixed`.
  - Palestine (`PS`) is an `observer` (since 1999).
  - Every member has `joined` set to its UPU date of entry.
  - The record also gets the founding date 1874-10-09 (Treaty of Bern), `active_period`,
    `previous_names` (General Postal Union), the 22 Treaty of Bern signatories as
    `founding_members`, `secretariat`, `recognition_status`, named `official_documents`, `notes`
    and source-backed `provenance`. Mislabelled acronym languages are fixed.
  - Off-topic tags and topics (`regional_cooperation`, `telecommunications`) are replaced with
    `standardization` and `trade_facilitation`.

### Added

- Four intblocks with Armenia as a member, from each body's official roster:
  - `MONEYVAL` (Council of Europe Committee of Experts on the Evaluation of Anti-Money
    Laundering Measures and the Financing of Terrorism, Wikidata Q971908): 35 member
    jurisdictions, Russia as a former member from 2022-03-16, and four observer states.
  - `INTERSTATEBANK` (Interstate Bank of the CIS states, Wikidata Q4288089): eight
    participants with the date the 1993 Agreement entered into force for each; Uzbekistan
    and Ukraine as former participants.
  - `EPCCIS` (Electric Power Council of the CIS): nine members; Moldova and Ukraine as
    former members.
  - `ICAPCIS` (CIS Interstate Council on Antimonopoly Policy): the eight states at its 2024
    and 2025 meetings.
- `AMSG` (Armenia-Singapore) and `KZSG` (Kazakhstan-Singapore) services and investment
  agreements in `trade_agreements`, in force since 2021-02-01 and 2025-03-01, from Enterprise
  Singapore.

### Changed

- `AMTM` notes the Armenian Ministry of Foreign Affairs dates that differ from the treaty
  text, which gives entry into force on 1996-07-07.
- The `wikidata_id` completeness gate allows 19% missing (was 18%); every record without one
  is listed in `wikidata_exclusions.yaml`, now with `ICAPCIS` and `EPCCIS`.

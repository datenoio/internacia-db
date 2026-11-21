### Fixed

- `ITER` checked on 2026-11-21 against the ITER Agreement and iter.org. `name` is now the
  Article 1 name, "ITER International Fusion Energy Organization". `founded` moves from
  2006 (the signing year) to 2007-10-24, the date the Organization was established, and
  `active_period` starts on the same day. `headquarters` gains `country: FR` and the
  Saint-Paul-lez-Durance site coordinates, replacing the CEA Cadarache point. `languages`
  is now `en` only, because English is the working language. The seven Members gain
  `joined` 2007-10-24 and become `founding_members`: CN, IN, JP, KR, RU and US, since
  Euratom has no country code. New `includes` entries: CH (`participant` through Fusion for
  Energy, from 2026-01-01) and the non-Member cooperation partners AU, KZ and CA
  (`cooperating`). `membership_count` stays 7. The record also gains `institutional_design`,
  `legal_status`, `recognition_status`, `official_documents`, `social_media`, `secretariat`,
  `notes`, a rewritten `description`, the topics energy, nuclear and physics, and 19
  provenance entries. A second Wikidata link points to the organization item Q101069148;
  `wikidata_id` stays Q191788. ITER joins the reviewed `institutional_design` cohort, and
  it now appears in the declared vs actual roster recipe, because it lists 11 entries
  against its 7 Members.
- `CERN` checked on 2026-11-21 against home.cern and the CERN Convention (English text on
  the Dutch government treaty database). `founded` moves from 1954 to 1954-09-29, the date
  the Convention entered into force, and `active_period` starts on the same day. All 25
  Member States and 11 Associate Member States gain `joined` years from CERN's timeline,
  and the 11 founders still members become `founding_members`. Yugoslavia, the twelfth
  founder, left in 1961 and has no country record. The observers JP, US, EU and UNESCO are
  added as `observer`. `membership_count` stays 36 (Member States plus Associate Member
  States). `previous_names` records the provisional Conseil Européen pour la Recherche
  Nucléaire (1952-1954). Also changed: the website becomes https://home.cern/, the
  headquarters coordinates come from Wikidata, and `description` is rewritten.
  The record also gains `institutional_design`, `legal_status`, `recognition_status`,
  `official_documents`, `social_media`, `secretariat`, `notes`, `geographic_scope`
  (regional, Europe), the topic physics and 19 provenance entries. CERN joins the reviewed
  `institutional_design` cohort, and it now appears in the declared vs actual roster
  recipe, because it lists 40 entries, observers included, against a count of 36.
- `ESO` checked on 2026-11-21 against eso.org and the ESO Convention (Dutch authentic text on
  the Dutch government treaty database). `founded` moves from 1962 to 1962-10-05, the date of
  signature, and `active_period` starts on 1964-01-17, when the Convention took effect. The
  16 Member States gain `joined` dates from ESO's Member States table and timeline. The five
  signatories (BE, DE, FR, NL, SE) become `founding_members`. Chile, the host and partner
  country, and Australia, a Strategic Partner since 2017, are added as `partner`.
  `membership_count` stays 16. `languages` gains `fr` and `de`. The website moves to
  https://www.eso.org/, the headquarters coordinates come from Wikidata, and `description` is
  rewritten. The record also gains `institutional_design`, `legal_status`,
  `recognition_status`, `official_documents`, `social_media`, `secretariat`, `notes`,
  `geographic_scope` (regional, Europe), the topic astronomy and 18 provenance entries. ESO
  joins the reviewed `institutional_design` cohort, and it now appears in the declared vs
  actual roster recipe, because it lists 18 entries against 16 Member States.
- With ITER, CERN and ESO, the reviewed `institutional_design` cohort in
  `data/schemas/institutional_design_pilot.yaml` becomes `reviewed_111`. The documented
  authority-level and declared vs actual roster recipes, and their tests, are updated.

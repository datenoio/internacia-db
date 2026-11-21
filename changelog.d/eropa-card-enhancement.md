### Fixed

- `EROPA` checked on 2026-11-21 against the EROPA website (history, constitution, secretariat,
  centers): `headquarters.city` is now Quezon City (it held the college name), and admission
  dates come from the official history, so Nepal joined in December 1980, not 1983. Founding
  members carry `joined: 1960-12-05`, which adds one row (`AU`) to the documented
  former-members-with-dates recipe. `legal_status` now describes the hybrid
  State/Group/Individual membership. The record gains `social_media`, the constitution in
  `official_documents`, `secretariat.organization`, notes on PRC and SRV seat successions, and
  three topics. `scope_category` stays `igo` pending review.
- `CAPAM` is now `non_state_organization` and no longer lists 55 country members. It was a
  Canadian federal not-for-profit corporation whose members were individuals and organisations,
  including government ministries and departments, not states (Corporations Canada; Jamaica
  Information Service, 2008). The old roster copied the Commonwealth's, without the UK and with
  Gabon and Togo, which joined the Commonwealth in 2022. The record drops `partof: COMMONWEALTH`
  and sets `membership_applicability: not_applicable`, as `ACU` does, and leaves
  `scope_category.igo_legal_status_allowlist`. `memberships` loses CAPAM's 55 rows, and the
  documented dissolved-with-roster recipe loses one row. The record also gains the last
  registered office, the 2019 dissolution vote and reasons, the 1998 start of the Innovations
  Awards (not 1997), conference examples and three topics.
- `CREDAF` checked on 2026-11-21 against credaf.org. `headquarters` is now Paris (86, allée de
  Bercy), where the secretariat sits, not Yaoundé, where the statutes were drawn up in 1982.
  The 15 founding administrations, Gabon among them, are in `founding_members` and marked
  `founding_member` (`joined: 1982`) in `includes`. The English name in `other_names` is the one
  the site uses, and the pre-2018 name is in `previous_names`. `legal_status` now records the
  self-described non-governmental form and the membership of national tax administrations.
  The record also gains `secretariat`, the Executive Bureau, conferences from 2012 to 2026,
  cooperation agreements and two topics. `scope_category` stays `igo`, as for its NTO peers.

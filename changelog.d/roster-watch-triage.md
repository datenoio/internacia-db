### Fixed

- The roster watch no longer reports Denmark as missing from Wikidata for the UN and the OECD.
  Wikidata records those memberships on the Kingdom of Denmark (Q756617), which has no
  ISO 3166-1 code. The Denmark mapping pointed at Q35, which already has the code.
- The roster watch no longer opens a new `roster-drift` issue for differences that a person
  closed as not planned (internacia-db is right). It reports them again only when the
  differences change. Before, closing such an issue brought it back as a new issue the next
  Monday.

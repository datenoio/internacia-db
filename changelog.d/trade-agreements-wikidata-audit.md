### Fixed

- Trade agreement Wikidata id audit (22 November 2026): the 26 `wikidata_id` values set on
  `data/trade_agreements/` records, and the 54 that linked records read from their
  intblocks, were fetched from Wikidata and checked against each record's name, parties and
  type. Every id points to the right agreement item except `AUUK`: Q107271797 does not
  exist, and its correction to Q97356844 is listed under the intblock Wikidata id audit. No
  record had names or descriptions copied from a wrong item.
- `EUJP` (EU-Japan Economic Partnership Agreement) now links to the English Wikipedia
  article on the agreement, the enwiki sitelink of Q30749427, instead of the article on
  Japan–European Union relations.

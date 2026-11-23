# Design: investment agreements in the trade agreements registry

## Context

The registry (`add-trade-agreements-registry`) records one file per legal instrument, with parties, status, dates, catalogue ids and provenance. Its `agreement_type` enum has no value for standalone investment treaties. `services` is described as "services or investment only", but no investment treaty is recorded under it. The five `services` records (`ATISA`, `BYCN`, `CISFTASERVICES`, `EUAM`, `EUSI-1996`) all cover trade in services or combine it with establishment.

The Global Affairs Canada (GAC) agreements table, checked on 2026-11-23 (`https://international.canada.ca/en/services/business/trade/agreements-negotiations/investment-agreements`), is one static HTML table with 118 rows, 59 of them FIPAs. It gives a status from "1. Exploratory discussions" to "11. Superseded" and an entry into force date. Its links point to Canada Treaty Series texts (30 rows) or to international.gc.ca background pages (29 rows). The Canada Treaty Series details page, `https://treaty-accord.gc.ca/details.aspx?id=N`, gives the subject ("Investment protection"), the signature lines with dates, the entry into force date, a "Suspended" date where one applies, and the CTS citation. Plain curl reads both sites. The CTS search form (an ASP.NET postback) returned HTTP 500 to a script and hung in a browser.

## Decisions

### 1. One registry, new type `investment`

Investment treaties go into `trade_agreements` with `agreement_type: investment`.

- `investment` covers standalone treaties whose main object is the promotion, protection or facilitation of investment: BITs, FIPAs, investment protection agreements (the EU's IPAs), cooperation and facilitation investment agreements (Brazil's CFIAs), and plurilateral investment treaties.
- An FTA, EPA or CEPA with an investment chapter keeps its FTA type, and a TIFA stays `framework`.
- A treaty that terminates investment treaties, such as the intra-EU termination agreement (`INTRAEUBIT`), is `other`: it does not protect investment.
- The `services` description becomes "services only". No existing record changes type.

Alternatives considered:

- A separate `investment_agreements` dataset would need its own tables, view, contract entries and validators for the same shape of data.
- Renaming the dataset to something like `economic_agreements` would be a MAJOR change for no gain in meaning.

The documentation describes the dataset as "trade and investment agreements", as GAC's table does.

### 2. Identifiers

- **Bilateral treaties.** An investment record's id is the two alpha-2 codes in alphabetical order plus `-BIT` (`AMCA-BIT`). For a bloc party, the bloc id comes first (`BLEUCA-BIT`, `EUSG-BIT`).
- **Always a suffix.** The suffix is used even when the parties have no FTA, so an FTA recorded later never collides (`CACR` and `CACR-BIT`). This also avoids renaming any record.
- **More treaties between the same parties.** An additional investment treaty between the same parties adds its year of signature (`-BIT-2009`). The first one recorded keeps the bare id, and ids are never renamed, as with `CAUA` and `CAUA-2016`.
- **Plurilateral treaties linked to an intblock** keep the intblock id (`ACIA`, `OICIA`).

The validator checks two things: an `investment` record that is not linked has an id ending in `-BIT` or `-BIT-YYYY`, and an id with that suffix has `agreement_type: investment`.

### 3. Status mapping and lifecycle

GAC statuses map to registry statuses as follows:

| GAC status | Registry status | Note |
|---|---|---|
| 1. Exploratory discussions | `proposed` | |
| 2. In negotiations | `negotiating` | If CTS shows an older treaty in force between the parties, it is an `in_force` record (decision 5) |
| 3. Concluded negotiations | `negotiating` | Conclusion date in `notes` |
| 4. Signed, 5. Ratification | `signed` | |
| 6. In force | `in_force` | |
| 7. Terminated | `terminated` | `ended` is the date of termination, and any survival (sunset) period is in `notes` |
| 8. Inactive | `abandoned` | As for FTAs (`AEAU`, `CAJP`), with "8. Inactive" quoted in `notes` |
| 9. Suspended, 11. Superseded | `superseded` | `superseded_by` is the agreement that took over; `ended` is the CTS "Suspended" date |
| 10. Provisional application | `in_force` | "Provisional application" in `notes`, as for `CETA` |

**Suspension.** When an FTA's investment chapter suspends a FIPA, the FIPA is `superseded` by the FTA and `ended` is the date of suspension:

- Canada–Panama: suspended on 2013-04-01, superseded by `CAPA`.
- Canada–Peru: suspended on 2009-08-01, superseded by `CAPE`.
- Canada–Ukraine: suspended on 2024-07-01, superseded by `CAUA`.

The notes say the treaty is suspended, not terminated, and quote any clause that keeps it applying to existing investments. A new `suspended` status was considered. It would be one more open value that consumers must handle, for a state that behaves like replacement in every case found so far. It stays an open question for the maintainer.

### 4. Bloc parties

- **BLEU.** Belgium and Luxembourg sign investment treaties as the Belgium–Luxembourg Economic Union (BLEU, convention of 1921). A new intblock `BLEU` with members `BE` and `LU` holds that party, as `EU` does for EU agreements. `country_trade_agreements` expands it to Belgium and Luxembourg with `via = 'BLEU'`.
  - Listing `BE` and `LU` as two country parties would make each BLEU treaty a three-party agreement. The quality report would then list it as an intblock candidate.
- **EU.** Investment protection agreements of the EU (EU–Singapore IPA, EU–Viet Nam IPA) list the `EU` intblock, following the existing convention for mixed trade agreements.

### 5. Succession, renegotiation and replacement

- **Successor states.** A party is the state that the party government or the depositary records as the current party. The Canada Treaty Series records the 1989 FIPA as signed with the U.S.S.R., while GAC's table lists it under Russia. It is recorded with `RU`, and the notes name the original signatory. A treaty that two successor states continue gets one record with both successors and a note.
- **Renegotiation.** GAC lists Argentina and Uruguay as "2. In negotiations". The Canada Treaty Series shows their 1991 and 1997 FIPAs in force since 1993-04-29 and 1999-06-02. The records are `in_force`, and the renegotiation is in `notes`. A new record is added only when a new instrument is signed. That record then `supersedes` the old one.
- **Replacement by a new treaty.** When a new treaty replaces an earlier one between the same parties, the earlier treaty is `superseded`, and the new one gets the year suffix of decision 2 if the earlier one already has the bare id.

### 6. Catalogue identifier and verification

- **New field.** `unctad_iia_id` (integer, optional, unique) records the UNCTAD IIA Navigator treaty id.
- **Catalogue verification.** `verification: catalogue` extends to records taken only from WTO RTA-IS, ADB ARIC or the UNCTAD IIA Navigator.
- **Official verification.** Records checked against a party's treaty series (the Canada Treaty Series, the US State Department's Treaties in Force, the Australian Treaty Series) or the treaty text are `official`.
- **Treaty text links.** Once datenoio/internacia-db#209 adds the `treaty_text` link type, CTS text pages go there. Until then they are cited in `provenance`.

### 7. Scope guardrail

The schema keeps `additionalProperties: false`. The registry does not record:

- investment flows or stocks;
- the number or outcome of investor–state arbitration cases;
- UNCTAD's treaty-content mapping (fair and equitable treatment, ISDS, umbrella clauses);
- treaty "generations";
- any score.

`notes` hold legal facts only: suspension, termination, survival clauses, succession and renegotiation.

## Rollout

1. Schema, validator, contract and documentation.
2. The `BLEU` intblock and linked records for the six plurilateral investment intblocks.
3. Canada pilot: import the 59 GAC rows with CTS dates (`scripts/oneoff/import_canada_fipas.py`), then add any instrument of the CTS subject "Investment protection" that the GAC table omits, such as earlier treaties with predecessor states.
4. Follow-up changes, each from a party government source:
   - the United States: 41 BITs on `trade.gov/bilateral-investment-treaties`, with signature and entry into force lines and termination notes;
   - Australia: the DFAT Australian Treaties Database, which already feeds the registry;
   - the EU and EFTA investment protection agreements.
5. Later: a catalogue walk of the UNCTAD IIA Navigator. It lists about 2,800 BITs and 450 other treaties with investment provisions, and would roughly quadruple the registry.

## Risks

- **UNCTAD access.** On 2026-11-23 `investmentpolicy.unctad.org` answered both curl and the browser pane with a Cloudflare challenge page (HTTP 403). A catalogue walk needs an export obtained by the maintainer, or another access path. Automated tools will not bypass the challenge.
- **Volume.** A full walk adds about 3,000 files. The build and validators read every file, so CI time grows in proportion. The Canada pilot adds about 65 files.
- **Consumers counting trade agreements.** Queries that count rows of `country_trade_agreements` start to include investment treaties. Documented queries and counts get an `agreement_type` filter, and the changelog says so.
- **GAC table quality.** The table mixes renegotiations with treaties in force (Argentina, Uruguay) and gives no signature dates. Each row is checked against the Canada Treaty Series, and conflicts go in `notes`.

## Open questions

1. Is a separate `suspended` status needed (decision 3), or is `superseded` with a note enough?
2. Should GAC's "1. Exploratory discussions" rows be imported as `proposed` records, or left out until negotiations are launched?
3. Is a `BLEU` intblock acceptable as a bloc party (decision 4)?

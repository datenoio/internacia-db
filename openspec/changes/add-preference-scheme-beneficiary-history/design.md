# Design: beneficiary history from PTA Database versions

## Context

The WTO PTA Database stores one version per notified change of a scheme. Each version has an "As of" date and its own beneficiary list, and its own sub-scheme lists. The beneficiary page (`ptaBeneficiaries.aspx`) serves the list of any version when that version's id is posted in the `DropDownList1` field. ASP.NET event validation accepts a posted id only if the page rendered it in the dropdown.

The dropdown is cached on the server across sessions, so a page often renders the versions of another scheme. `add-preference-scheme-rosters` design decision 10 describes this. The walk therefore reloads the scheme's card until the dropdown contains the scheme's latest version id, which the list's hidden column gives. That dropdown is then the scheme's full version list. In the probe it took one or two tries.

The first versions of older schemes, such as AGOA (2000-05-18) and the EU GSP (1971-07-01), list no beneficiaries. Lists start with the first notification under the Transparency Mechanism for PTAs (WT/L/806), from 2011.

## Goals and non-goals

Goals:

- When the versions show that a beneficiary joined or left, its party gets a date.
- Countries that used to benefit are recorded as former beneficiaries.
- No date is made up for a period the database does not cover.

Non-goals:

- Exact designation or graduation dates from the grantors' legal acts. A record moves to `official` in a normal data PR.
- Editing the official rosters of linked intblocks.
- Reasons for a change (graduation, suspension, income threshold). A note may name the reason when an official source gives it.

## Decisions

### 1. Populated versions only

The walk compares versions that list at least one beneficiary. They are called populated versions here.

- The earliest populated version is the baseline. A beneficiary in the baseline gets no `in_force`, because the database does not say when it joined. The exception is a baseline that is also the scheme's first version, as for `GB-DCTS` (2023-06-19) and `EAEU-GSP` (2016-10-10). Then the beneficiary's `in_force` is that version's date.
- A beneficiary that appears in a later populated version gets that version's "As of" date as `in_force`.
- A beneficiary missing from a later populated version gets that version's date as `left`.

A version date is the date from which that version applies. The registry cannot tell whether every change was notified, so the notes call these dates "no later than" dates. They mean that the change happened by this date. They are not exact designation dates.

### 2. One party entry, latest spell

The registry allows one party entry per id. A country can leave and come back, as AGOA suspensions and reinstatements show. Its entry carries its latest spell:

- `in_force` is the start of the spell;
- `left` is the end of the spell, if it has ended.

Earlier spells go in the party `note`, for example `Also a beneficiary from 2011-10-25 to 2015-01-01.`. A structured `periods` list would need a schema change. It can be proposed later if consumers need to query earlier spells.

### 3. Former beneficiaries

A country that is in some populated version but not in the latest one becomes a party with `role: beneficiary` and a `left` date. The export marks it `former_party`. `party_count`, `country_trade_agreements` and the sub-scheme subset rule read current parties only, so they do not change.

### 4. Sub-schemes

The walk reads each version's sub-scheme lists as well. Two things change:

- A sub-scheme beneficiary gets dates by decision 1, within the sub-scheme.
- A sub-scheme's `in_force` becomes the date of the earliest populated version that lists the sub-scheme. If the sub-scheme's legal basis gives a date (EBA 2001-03-05), that date is kept.

A sub-scheme can be renamed, or be split, between versions. The walk matches sub-schemes by label and reports any label it cannot match for hand review.

### 5. Validation

The new rule `TRADE_AGREEMENT_PARTY_DATE` is an error. It compares dates at their shared precision, as `TRADE_AGREEMENT_STATUS_DATE` does, and checks three things:

- a party's `in_force` is not earlier than the agreement's `in_force`;
- a party's `left` is not later than the agreement's `ended`;
- a party's `left` is later than its own `in_force`.

The rule applies to every agreement, not only to preference schemes. Existing records that break it are fixed in this change, or the rule is limited to preference schemes. The dry run decides which, before the rule is turned on.

### 6. Provenance and notes

The `parties` provenance entry names the range of versions read, for example `WTO Preferential Trade Arrangements Database, versions as of 2011-12-09 to 2017-06-29`. The record notes say:

- which version is the baseline;
- that beneficiary dates are "no later than" dates;
- how many former beneficiaries were added.

### 7. Linked intblocks

The official rosters of `AGOA`, `CBERA`, `CARIBCAN`, `SPARTECA` and `GSPPLUS` are not edited. The walk writes a TSV report, outside the repository, for each of them. It lists the `joined` and `left` dates the versions suggest, and the countries that are in the versions but not in `includes`, or the other way round. A person checks them against the cited official sources (USTR, the Federal Register, the European Commission) and edits the intblock in a separate PR.

The AGOA record now leaves out countries that are not designated "because designation history is incomplete in a single official list", and the report gives that history. Whether the record should list them as former members is decided in that PR.

### 8. Request volume

The walk reads about 200 versions. Each takes one post for the beneficiaries and up to three for sub-schemes, so the full walk is about 400 requests. With a one-second pause between requests it takes about 10 minutes. The snapshot stays outside the repository, as the current one does.

## Risks

- **Changes that were never notified.** Some dates are "no later than" dates that can be years late. Mitigation: no `in_force` for baseline beneficiaries, and the notes say what the dates mean.
- **Version ids of the wrong scheme.** The dropdown cache can give another scheme's version list. Mitigation: a version list is accepted only if it contains the scheme's latest version id, and every beneficiary page's scheme title is checked.
- **Bigger records.** EU GSP gains about 90 former beneficiaries. Mitigation: one party entry per country, and spells in `note`.
- **Re-entries counted as gaps.** A version that lists no beneficiaries after populated ones would make everyone leave. Mitigation: only populated versions are compared (decision 1), and a drop of more than half of the beneficiaries between two versions is reported for hand review.

## Open questions

1. Should earlier spells get a structured `periods` list on parties, rather than a note? The default is no, until a consumer asks for it.
2. Should the AGOA intblock list non-designated countries as former members with `left` dates? The default is to decide in the intblock review PR (decision 7).

# Roster watch

Membership rosters are the core of internacia-db and change when countries join, leave, are
suspended or expelled. The roster watch looks for such changes every week without editing data:
a person verifies each finding.

## What it compares

For every tier-1 organization in `data/watch/rosters.yaml`, `scripts/roster_watch.py` compares:

- **internacia-db:** current full members — `includes` entries of type `country` with status
  `member` or `founding_member` and no `left` date;
- **Wikidata:** countries that are current members of the organization's `wikidata_id` —
  `member of` (P463) on the country or `has part(s)` (P527) on the organization, without an end
  time (P582) and not deprecated, mapped to ISO 3166-1 alpha-2 (P297).

When less than half of our members are confirmed by Wikidata, the report flags **low overlap**:
the `wikidata_id` or Wikidata's modelling is then the likelier problem.

## Issues

`.github/workflows/roster-watch.yml` runs on Mondays (and on demand). It keeps one open issue
labelled `roster-drift` per organization with differences, updates it only when the differences
change, and closes it when the rosters agree. The report is also in the job summary and the
`roster-watch` artifact.

To resolve an issue, check the official member list cited in the record's `provenance`, then
either fix `includes` and set `last_verified`, or, if internacia-db is right, close the issue as
**not planned** with a comment naming the official source. The watch remembers the differences
of an issue closed as not planned and does not open a new issue for them. It opens one again
when the differences change, for example when a country joins or leaves, or when Wikidata adds
or removes a member. Issues closed as completed (by the watch, or after a fix) do not have this
effect.

## Running it locally

```bash
python scripts/roster_watch.py --markdown          # all tier-1 organizations
python scripts/roster_watch.py NATO EU --markdown  # selected ids
```

Add an organization to the watch by adding its id to `data/watch/rosters.yaml`; it then also
gets the 6-month `last_verified` window.

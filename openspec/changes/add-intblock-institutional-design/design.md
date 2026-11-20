# Design: Institutional design facts on intblocks

## Context

Consumers ask two related questions that Internacia cannot answer today:

1. Which organizations are influential, and which play a mainly technical role?
2. How much weight does a given country carry inside a given organization?

Neither question has a single measure. Each combines two independent axes:

- **Authority**: what an organization can decide and enforce. The political-science reference is the Measure of International Authority (MIA) by Hooghe, Marks, Lenz and colleagues. MIA scores *delegation* (powers given to bodies that do not represent states) and *pooling* (majority voting and binding decisions).
- **Capacity**: the resources its members hold, such as population, output, and military spending.

Authority is a property of the founding instrument and its rules of procedure. It changes only through treaty reform, can be cited to a primary source, and fits the repository's reference-data scope. Capacity is a time series. Population is already in scope on countries (`countries.population`, with `value` and `year`). GDP, military spending, armed-forces size, and similar indicators are explicitly out of scope (`AGENTS.md`, `docs/when-to-use-internacia.md`, `openspec/project.md`).

A sample computation on the current DuckDB, using only population, shows why both axes matter:

| Intblock | Members | World population share | Largest member (share) | Effective members (1/HHI) |
|---|---|---|---|---|
| UPU | 192 | 99.4% | IN (17.9%) | 13.9 |
| BRICS | 11 | 48.5% | IN (36.7%) | 3.6 |
| NATO | 32 | 12.0% | US (34.7%) | 6.4 |
| EU | 27 | 5.5% | DE (18.5%) | 9.9 |
| EAEU | 5 | 2.3% | RU (78.2%) | 1.6 |

UPU is the largest by capacity yet has a technical mandate. BRICS is large but is a non-binding forum. The EU is small by population but has a high authority level. Capacity alone ranks these the wrong way.

## Goals / Non-Goals

The goals are:

- Record the authority axis as optional, sourced, reviewable facts on intblock records.
- Define every value precisely enough that two reviewers assign the same value from the same founding instrument.
- Give consumers a tested recipe to derive an authority level and a tested recipe to compute capacity concentration from data already in scope.
- Cover a pilot cohort of 36 high-profile records that spans both strategic and technical organizations.

The non-goals are:

- Adding GDP, military spending, armed-forces size, nuclear status, or any other indicator to countries.
- Storing a composite influence score, index, or ranking. The inclusion policy already excludes socioeconomic rankings and indices.
- Storing time-varying weights: vote shares, IMF/World Bank quotas, budget contribution scales, or seat allocations.
- Importing MIA scores or any other external index.
- Requiring `institutional_design` on every record, or adding a completeness error gate in this change.
- Inferring values from `blocktype`, directory, or `topics`.

## Decisions

### Decision 1: One optional object, seven subfields

The new field is an optional object `institutional_design` on intblock records. Absence means *unknown*, never *none*. Every subfield is optional, so a reviewer may record only what the source supports.

```yaml
institutional_design:
  mandate: general
  decision_rule: qualified_majority
  decision_force: binding
  independent_organs: [executive, court, parliament, central_bank]
  enforcement: [sanctions, suspension]
  mutual_defence: true
  veto_holders: []          # omit when there are no asymmetric vetoes
```

The values above are illustrative only. Pilot values are set from primary sources during backfill, not from this document.

### Decision 2: Describe the principal decision-making organ

`decision_rule` and `decision_force` describe the **principal decision-making organ**: the organ of member-state representatives that adopts the organization's main acts. Examples are a council of ministers, an assembly of states parties, or a summit of heads of state. When the instrument sets different rules for different areas, record the **default** rule for the main acts. Use `mixed` only when the instrument sets no default.

This rule keeps one value per record. A reviewer does not have to aggregate across organs.

### Decision 3: Value definitions

The catalog `data/schemas/institutional_design.yaml` holds the normative definitions. The summary is:

**`mandate`** (one value, the primary policy domain):

| Value | Meaning |
|---|---|
| `general` | General-purpose or multi-domain organization with significant mandates in at least two of: security, economic integration, political cooperation |
| `security` | Defence, collective security, or arms control |
| `economic` | Trade, customs, monetary policy, finance, development lending, or commodity producers |
| `sectoral` | One non-economic policy field, such as health, environment, labour, human rights, education, or migration |
| `technical` | Coordination of standards, networks, or registries with limited policy discretion, such as post, telecommunications, meteorology, aviation, or intellectual-property registration |

**`decision_rule`** (one value):

| Value | Meaning |
|---|---|
| `consensus` | Adoption without formal objection, with no vote. Every member can block. |
| `unanimity` | A formal vote that requires every member. Every member can block. |
| `simple_majority` | More than half of the votes cast or of the members |
| `qualified_majority` | A threshold above a simple majority, or a double majority |
| `weighted_voting` | Votes weighted by quota, shares, contribution, or population |
| `mixed` | The instrument sets different rules for different areas and no default |

**`decision_force`** (one value):

| Value | Meaning |
|---|---|
| `binding` | The organ's main acts bind members without each member's separate ratification |
| `partly_binding` | Some categories of main acts bind, or acts bind only after each member ratifies or accepts them |
| `non_binding` | Recommendations, declarations, or communiqués only |

**`independent_organs`** (list, or `[none]`): `executive` (an executive organ with its own right of initiative or implementation, whose members do not take instructions from states), `court` (a standing judicial body whose rulings bind members), `dispute_panel` (non-standing panels or arbitration with binding outcomes), `parliament` (an elected assembly with legislative or budgetary powers), `central_bank` (an independent monetary authority). A general secretariat does not count, because almost every organization has one.

**`enforcement`** (list, or `[none]`): `sanctions` (measures the organization decides against a member), `suspension` (of membership or voting rights), `expulsion`, `conditionality` (access to financing conditioned on policy commitments).

**`mutual_defence`** (boolean): `true` only when an instrument binding all members of this record obliges assistance against an armed attack on a member.

**`veto_holders`** (list of country alpha-2 codes): members with a treaty-granted veto that other members lack, such as permanent Security Council members. Consensus and unanimity do not create veto holders, because every member can block. De-facto vetoes from voting weight (for example a quota share above a supermajority threshold) are excluded, because they depend on time-varying weights.

### Decision 4: `mandate` is curated, not inferred

`mandate` overlaps with `blocktype` and `topics`, but it cannot be derived from them. `blocktype: unagency` covers both IMF and UPU. `topics` is multi-valued and not tiered. The scope-taxonomy change (`complete-intblock-scope-taxonomy`) already showed that directory and blocktype inference produce false labels. `mandate` is therefore assigned from the purposes article of the founding instrument and listed in the reviewed pilot manifest.

### Decision 5: Excluded entity kinds

`institutional_design` describes intergovernmental authority. It is forbidden on `scope_category: reference_enumeration`, because a named set of countries has no organs. It is forbidden on `non_state_organization`, because states do not take its decisions. It is allowed on `igo`, `treaty_body`, `policy_forum`, and `intergovernmental_body`. On a historical record it describes the design at dissolution.

### Decision 6: Derived levels live in recipes, not in exports

The authority level is a convention derived from facts, not a fact. Shipping it as a column would make it look authoritative and would move the repository toward the rankings that the inclusion policy excludes. This change publishes it as a documented, tested DuckDB recipe:

| Level | Rule |
|---|---|
| `none` | `scope_category = 'reference_enumeration'` |
| NULL | `institutional_design.decision_force` is absent |
| `low` | `decision_force = 'non_binding'` |
| `high` | `decision_force = 'binding'` and at least one of: a majority or weighted `decision_rule`; an `executive` or `court` organ; `sanctions` or `conditionality` enforcement |
| `medium` | Any other `binding` or `partly_binding` record |

Consumers can change the rule without waiting for a release. Promoting it to a view is an open question for after the pilot.

### Decision 7: Capacity recipe uses only in-scope data

The capacity recipe computes, per intblock and from current `member` and `founding_member` country rows:

- the bloc's share of the world population, with official ISO countries as the denominator;
- the largest member and its share of the bloc's population;
- the Herfindahl–Hirschman index (HHI) of member population shares;
- the effective number of members (1/HHI);
- the minimum and maximum `population.year` used, because years differ by country.

The documentation states that population concentration is not power. It shows, as an untested pattern, how a consumer loads an external indicator table (for example World Bank WDI GDP or SIPRI military expenditure) and joins it on `countries.iso3code`. No external data ships.

### Decision 8: Reviewed pilot manifest

The pilot uses an explicit manifest `data/schemas/institutional_design_pilot.yaml`. The manifest lists each ID with its values and source URL. It follows the safety model of `scripts/backfill_scope_category.py`:

- dry run by default;
- the whole cohort is validated before any write;
- an existing different value blocks the whole apply;
- a matching value is idempotent;
- provenance is inserted with each value.

The 36 pilot IDs are:

- General: `UN`, `UNSC`, `EU`, `AFUNION`, `ASEAN`, `OAS`, `COE`, `LAS`, `OIC`, `CIS`, `CCASG`, `SADC`, `ECOWAS`, `CARICOM`
- Security: `NATO`, `CSTO`, `SCO`
- Economic: `EAEU`, `MERCOSUR`, `EFTA`, `WTO`, `IMF`, `WB`, `OECD`, `OPEC`, `APEC`
- Forums: `G7`, `G-20`, `BRICS`
- Sectoral and technical: `WHO`, `IAEA`, `UPU`, `ITU`, `WMO`, `ICAO`, `WIPO`

The grouping above is a sampling plan, not the `mandate` assignment. The backfill review sets each record's `mandate` from its sources.

## Risks / Trade-offs

- **Reviewer judgement on `mandate` and `decision_force`.** Mitigation: normative definitions with boundary examples, a reviewed manifest, and mandatory provenance.
- **Consumers read the authority level as an influence ranking.** Mitigation: the documentation presents authority and capacity as separate axes, and places both recipes next to each other.
- **Treaty reform changes the design.** For example, the Lisbon Treaty moved many EU areas to qualified majority. Mitigation: values describe the instrument in force at `last_verified`, and corrections ship as PATCH value changes.
- **Sparse coverage (36 of 1275).** Mitigation: absent means unknown, recipes return NULL, and the completeness report tracks coverage. No gate fails on missing values.
- **One more struct column for flat consumers.** Mitigation: the flattened CSV and lite exports follow the existing `headquarters` flattening pattern.

## Migration Plan

The change is additive. The new column and its open enums ship in a MINOR release with CHANGELOG notes and updated consumer examples. Before release, rollback is a revert of the PR. After release, removing the column requires a `deprecated` entry in `contract.json` in a MINOR release and removal no earlier than the next MAJOR release.

## Open Questions

1. Field name: `institutional_design` or the shorter `authority`?
2. Is a five-value `mandate` enough, or should `political` be separate from `general`?
3. Should `includes[]` later gain other structural rights, such as a permanent seat or host-state status?
4. After the pilot, should the authority recipe become a DuckDB view?
5. Should records carry an MIA crosswalk identifier, once MIA's licence and identifier stability are confirmed?
6. Is the 36-record pilot the right size and mix?

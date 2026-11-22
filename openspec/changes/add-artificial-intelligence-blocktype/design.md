# Design: `artificial_intelligence` blocktype

## Context

The blocktype taxonomy has two kinds of keys. Directory keys (`digital`, `forum`, `agreement`) are the primary blocktype of the records in `data/intblocks/<key>/`. Secondary keys (`cybersecurity`, `nuclear`, `security`) have no directory and say "usually a secondary tag". A record's directory is its first blocktype, and consumers filter on `list_contains(blocktype, ...)` or on `blocktype[1]`.

## Decisions

### Secondary tag, not a directory

`artificial_intelligence` is added as a secondary key. Records keep their current directory.

- Moving `WAICO` (a purpose-built AI IGO) to an `artificial_intelligence/` directory would be accurate, but it changes `blocktype[1]` from `digital` and drops the record from existing `digital` queries.
- The other AI records have a different primary domain: `GPAI` is a `forum`, `MILITARYAIDECLARATION` is `armscontrol`, `COEAICONVENTION` is an `agreement`.

A later change can promote the key to a directory if the AI set grows.

### Key name

The key is `artificial_intelligence`, not `ai`. Lowercase `ai` reads like the alpha-2 code `AI` (Anguilla), which appears in `includes[].id`. The full form follows `counter_terrorism` and `human_rights`.

### Scope boundary

The key applies when artificial intelligence is the record's main subject. It includes compute and semiconductor supply-chain partnerships (`CHIP4`, `PAXSILICA`), because their stated purpose is the hardware base of AI. It does not apply to records that list AI as one topic among many: `AUKUS` (Pillar II covers AI among other advanced capabilities) and `DEPA` (an AI module in a digital trade agreement) are not tagged.

### Non-binding instruments

`OECDAIPRINCIPLES` (a Council Recommendation) and `MILITARYAIDECLARATION` (a political declaration) are recorded as `treaty_body` with `status: formal` and a non-binding `legal_status`, following `ARTEMISACCORDS`. Adherents and endorsing states are the members.

### Convention not in force

`COEAICONVENTION` lists only the parties that have expressed consent to be bound (the EU and Bosnia and Herzegovina). Signature-only states are named in `notes`, not in `includes`, as for `BBNJ` and `TPNW` and as the inclusion policy prescribes for UNTC records. `CTBT` lists signatories, but it is a long-standing exception for a treaty that may never enter into force.

### Members that are institutes

`NAAIMES` members are government institutes or offices. They are recorded by the country or organization they represent, and `notes` says so (Kenya is represented by the presidential envoy for technology; the EU by the Commission's AI Office).

## Risks

- **Stale rosters.** The `COEAICONVENTION` roster was first taken from the Netherlands treaty database (last changed 2026-11-06), because the Council of Europe Treaty Office chart sits behind a bot check. It was then checked against the chart in a browser on 2026-11-21 and matches it. The military AI declaration list has not changed since 2024-11-27.
- **Scope creep.** A broad scope note could pull in every digital body. The boundary above limits the key to records whose main subject is AI.

## Open Questions

- Should the key become a directory now, with `WAICO` and `NAAIMES` as primary records?
- Should the topic catalog gain a matching `artificial_intelligence` topic key?

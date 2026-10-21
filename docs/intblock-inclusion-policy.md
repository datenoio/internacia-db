# Intblock inclusion policy

Defines what belongs in the intblocks dataset and how to classify records with
`scope_category`.

## Inclusion criteria

An intblock is included when it is useful as a **stable join target** for
membership, hierarchy (`partof`), or named reference sets used by other
records in this repository.

| Kind | Include? | Examples |
|------|----------|----------|
| Intergovernmental organization (IGO) | Yes | UN, NATO, AU, ASEAN |
| Treaty / convention with parties roster | Yes | UNFCCC, CBD, UNCLOS |
| Standing policy forum / process | Yes | G7, G20, ARF, FATF |
| Named geographic / set groupings | Yes, labeled `reference_enumeration` | SIDS, Maghreb, Caribbean |
| Country attribute partitions | **No** — use country fields | Traffic hand, DVD region, scripts, legal tradition, rail gauge, broadcast systems |
| Ad-hoc news coalitions / one-off summits | Usually no | Unless membership is durable and sourced |
| Socioeconomic rankings / indices | No | HDI lists, GDP leagues (out of country & intblock scope) |
| Government form / regime typology | No on countries; not as intblock membership | Optional vocab only: `data/vocabs/government_forms.yaml` |

### Regional trade agreements (WTO RTA-IS)

The WTO RTA Information System lists hundreds of notified RTAs (FTAs, customs
unions, partial-scope PTAs, and services EIAs). Internacia does **not** import
that catalogue. Include an RTA only when it is a **named, durable join target**:

| Include | Skip |
|---------|------|
| Named plurilateral FTAs with an official acronym and a roster distinct from an existing IGO (`AGADIR`, `PICTA`, ASEAN+1) | Untitled bilateral `Country A – Country B` pairs |
| Bloc-to-bloc deals whose extra parties make a distinct roster (`EFTAGCC`, `EFTASACU`) | Accession or enlargement notifications (update `includes` on the parent) |
| Named mega-deals commonly cited under their own acronym (`CETA`, `USMCA`, `RCEP`) | UK continuity copies of EU EPAs; services-only EIA rows of an FTA already recorded |
| Historical predecessors that complete a lineage already in the dataset (`TPSEP` → `TPP` → `CPTPP`) | Constitutive instruments of an IGO already recorded (`EU`, `EAEU`, `CCASG`, `MERCOSUR`, `SACU`) |

One intblock per legal instrument: WTO often lists goods (FTA) and services (EIA)
separately; Internacia keeps a single `fta` (or `pta` / `customs`) record. Source
rosters from the official treaty text, not only the WTO ID card (the Secretariat
warns that accessions and withdrawals are under-notified).

### Preferential trade arrangements (WTO PTA Database)

The WTO PTA Database lists **non-reciprocal** schemes (national GSP, LDC-only
DFQF, and waiver programmes). These are distinct from RTAs. Internacia does **not**
import that catalogue. Include a PTA only when it is a **named, durable join
target** with a roster distinct from `GSP` (grantors) and `LDC`:

| Include | Skip |
|---------|------|
| Named waiver programmes with an official acronym and a distinct beneficiary roster (`AGOA`, `CBERA`, `CARIBCAN`) | National GSP ID cards (`GSP – Japan`, `GSP – Armenia`, …) — already the `GSP` grantor record |
| Named GSP **arrangements** whose beneficiary list is not the UN LDC list (`GSPPLUS`) | LDC-only DFQF schemes (India DFTP, Chile/Korea/Morocco/Taipei DFQF, …) — roster ≈ `LDC` |
| Historical predecessors that complete a lineage already in the dataset (`ATPA` → `USPE`/`USCO`) | Untitled or one-country preferences (US–Nepal, EU–Pakistan 2012–13, EU–Moldova 2008–15) |
| | GSP successors already noted on `GSP` (`UK DCTS`); Everything But Arms (join via `LDC`) |
| | Constitutive or political instruments that are not this PTA (`COFA` vs “Former Trust Territory of the Pacific Islands”) |

One intblock per legal instrument: CBERA and CBTPA stay one `CBERA` record; EU
GSP+ is one `GSPPLUS` record, not a split of `GSP`. Source rosters from the
grantor’s official list (USTR, Canada/WTO waiver, EU GSP regulation). Eligibility
on these schemes is reviewed annually and is under-notified in the Secretariat
database.

### International investment agreements (UNCTAD IIA Navigator)

UNCTAD’s IIA Navigator lists thousands of bilateral investment treaties (BITs)
and treaties with investment provisions (TIPs), including a [by-country-grouping](https://investmentpolicy.unctad.org/international-investment-agreements/by-country-grouping)
index. Internacia does **not** import that catalogue. Include an IIA only when
it is a **named, durable join target** whose parties roster is distinct from an
existing IGO or FTA:

| Include | Skip |
|---------|------|
| Named plurilateral investment treaties with an official short title and a ratifiers list that is not the parent IGO (`OICIA`, `ACIA`, `UAIA`, `CJKIA`) | Untitled bilateral `Country A – Country B` BITs, including BLEU’s Belgium–Luxembourg BIT programme |
| Named CIS/REC services-and-investment instruments whose extra or missing parties make a distinct roster (`CISFTASERVICES`, `PCFI`) | FTA investment chapters of an FTA already recorded (`RCEP`, `CETA`, `ACFTA`/`AHKIA`, EU and EFTA extra-regional deals) |
| Plurilateral termination or reform instruments whose parties are a subset of an IGO (`INTRAEUBIT`) | Community acts whose roster equals the parent IGO (ECOWAS Supplementary Act A/SA.3/12/08; SADC FIP after Comoros accession) — note on the parent |
| Historical predecessors that complete a lineage already in the dataset | Constitutive instruments of an IGO already recorded (COMESA Treaty, ECOWAS Treaty, Revised Treaty of Chaguaramas) |
| | Framework / TIFA rows and UNCTAD TIP type-3 cooperation mandates |
| | Not-in-force protocols (`AfCFTA` Investment Protocol until 22 ratifications; COMESA CCIA; MERCOSUR Protocol of Colonia) and non-binding models (Pan-African Investment Code) |

One intblock per legal instrument: ASEAN+1 investment agreements stay notes on
the parent FTA (`ACFTA`, `AHKFTA`, `AKFTA`, `AIFTA`). Source rosters from the
depositary (OIC General Secretariat / COMCEC annex, ASEAN Secretariat, League of
Arab States, CIS Executive Committee, Council of the EU treaty office, Chinese MFA
treaty texts, Paraguay MFA for MERCOSUR protocols), not only the UNCTAD grouping card
(signatories are often listed alongside ratifiers). Signature-only participants
are omitted, as with UNTC records.

ICSID, MIGA, the New York Convention, the Mauritius Transparency Convention, and
the Energy Charter Treaty are already recorded as `ICSID`, `MIGA`, `NYC`,
`MAURITIUS`, and `ECT`.

### Attribute partitions → country fields

These classifications were previously inverted as intblocks and are now country
properties (with controlled vocabs under `data/vocabs/`):

| Former blocktype | Country field |
|------------------|---------------|
| `traffichand` | `car_side` (`left` \| `right`) |
| `writingdirection` | `writing_directions` |
| `writingsystem` | `writing_systems` |
| `dvdregion` | `dvd_region` |
| `teleregion` | `broadcast_systems` |
| `lawsystem` | `legal_systems` |
| `railgauge` | `rail_gauges` |
| `govform` | *(retired; vocab-only, not on countries)* |

Retired intblock ids map via `data/attribute_intblock_migrations.yaml`
(exported as `data/datasets/attribute_intblock_migrations.json`).

## `scope_category` values

| Value | Meaning |
|-------|---------|
| `igo` | Standing intergovernmental organization with independent institutional identity or juridical personality |
| `treaty_body` | Treaty, protocol, or convention (parties are members) |
| `policy_forum` | Ongoing forum, process, club, or intergovernmental implementation/cooperation platform without independent IGO personality |
| `reference_enumeration` | Named geographic or set grouping (not attribute partitions) |
| `intergovernmental_body` | Standing subsidiary/intergovernmental organ, commission, office, fund, or joint multilateral fund partnership without independent IGO status |
| `non_state_organization` | International NGO, professional/industry association, or federation not constituted by states as an IGO |

Source JSON Schema keeps this field optional for non-formal historical/de-facto records;
**every `status: formal` intblock must set it**. The CLI validator and quality analyzer
now treat a missing formal category as a blocking error/IMPORTANT issue.

`scope_category` classifies the **record's entity**, not the role or nationality of
entries in `includes`. An independent treaty-established institution with its
own juridical personality remains `igo` even if affiliated with a larger group
(e.g. African Development Fund, `AFDF`). A dependent commission established by
a FAO Article XIV agreement may be `intergovernmental_body` when the record is
the **commission**, not the agreement (e.g. `APFIC`). FAO Article VI commissions,
the joint FAO/WHO Codex Commission, and the GCC Secretariat's Patent Office are
other examples. The Asian Development Fund (`ADF`) and Adaptation Fund (`AF`)
are funds without their own country-member rosters, not independent IGOs.

The legally independent African Development Fund (`AFDF`) is instead an `igo`:
its 29 dated State Participants must not be confused with the 82 mixed country
links previously ascribed to the Fund or with financing recipients. The Climate Investment Funds (`CIF`) are a standing
two-fund partnership, not a third IGO and not an enumeration of their 15
contributors. CIF is an `intergovernmental_body` with no country-member roster.
The ESCAP Trans-Asian Railway Network (`TAR`) is a cooperation platform and
`policy_forum`; its geographic coverage of 28 countries is not membership.
Its **separate** Intergovernmental Agreement (`TARAGREEMENT`) is a `treaty_body`
with 22 parties. Do not attach treaty accession dates to the network or infer
that a country served by a railway is a party to the treaty.

For an NGO such as MSF or an industry association such as CANTO, offices and
member organizations' locations are **not** countries that belong to the NGO.
Where an entity has no meaningful country-level membership list, omit `includes`
and `membership_count`, and set `membership_applicability: not_applicable`.
Do not turn a parent organization's country members (GCC), funding beneficiaries
(ADF), donors (AF), or representatives' countries (RDR) into member states of a
subsidiary. Retain documented `participant` links only when the country itself
participates; subnational members are not their entire parent countries.

**Compatibility:** these two additional enum values are additive for open-string
consumers but potentially breaking for SDKs or queries with a closed four-value
enum. Extend downstream parsers and regenerate data exports together; do not
interpret `intergovernmental_body` as a synonym of `igo` or as proof that
`includes` contains a complete country roster.

An out-of-scope corporate media operator cannot acquire a false category merely
to satisfy validation. `TELESUR` was retired from intblocks after its legal form
was confirmed; see [retired intblock IDs](retired-intblock-ids.md). No alias maps
this retired company to an unrelated intblock.

World Bank regional, income, lending, and analytical aggregates under the `wbgroup`
blocktype are always `reference_enumeration`, even when their source is formal and
their `status` is `formal`. They are published classification sets, not organizations.
World Bank institutions such as `WB` and `IBRD` remain `igo` records.

## Boundaries vs treaties in `partof`

`partof` expresses **organizational hierarchy**, not “established by treaty X”.
Treaty nesting (protocol → convention) is allowed. Organization → pure treaty
links should be described in text instead (see `partof` hierarchy validation).

Specialized UN agencies prefer `partof: UN` (not ECOSOC alone).

## Intblock `id` naming

- **Uppercase ASCII** letters and digits only. Filename stem must match `id` exactly
  (case-sensitive).
- Prefer the **official acronym** the organization uses (`NATO`, `OECD`, `AUKUS`).
- No hyphens or spaces: drop punctuation (`NORTHSEASUMMIT`, `FATFGREYLIST`).
- If two bodies share an acronym, keep the well-known id and disambiguate the other
  (`sports/ICC` vs criminal-court alias) via `intblocks_aliases.json` — do not silently
  reuse an id.
- Do not invent nonce abbreviations that the organization itself does not use.
- Typos in existing ids are fixed through the alias mechanism (rename + alias), not
  by leaving a misspelled primary key.

## Directory vs `blocktype`

- The **directory** under `data/intblocks/` is the **primary** `blocktype` and must
  exist in `data/blocktypes/blocktypes.yaml`.
- The YAML `blocktype` list may include additional keys (`military` + `political`).
- Thin categories (few records) are allowed; **empty directories should be removed**.
- Do not create a new category folder without adding the blocktype to the taxonomy in
  the same PR.

## Discovery catalogues

Gap-finding lists (UN Treaty Collection, WTO RTA-IS, WTO PTA Database, UNCTAD IIA
Navigator, Wikipedia `.int` organizations) and the roster authorities used to
compile membership are documented in [intblock-sources.md](intblock-sources.md).
How to search those catalogues and improve existing records:
[discovery.md](discovery.md). Do not import those catalogues wholesale; every
candidate still has to meet the inclusion criteria above.

## Related

- [discovery.md](discovery.md) — how to search catalogues and improve records
- [intblock-sources.md](intblock-sources.md) — catalogues searched and roster authorities
- [entity-classification-policy.md](entity-classification-policy.md)
- [ai-consumers.md](ai-consumers.md)
- [agents/add-intblock-example.md](agents/add-intblock-example.md) — worked add-a-record walkthrough
- [enrichment.md](enrichment.md) — Wikidata completeness exclusions

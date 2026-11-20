# Review: the `intorg` (International Organization) blocktype

Date: 2026-11-20. Data: v4.0.0 build from commit `88a0a27f`.
Status: research note and proposal. Nothing in this note is implemented yet.
Schema-level steps need an OpenSpec change before implementation. The proposal is
[`openspec/changes/reorganize-intorg-blocktype/`](../../openspec/changes/reorganize-intorg-blocktype/proposal.md).

## 1. Findings

| Metric | Value |
|--------|-------|
| Records with `intorg` anywhere in `blocktype` | 358 |
| Records in `data/intblocks/intorg/` (primary `intorg`) | 147 |
| Records with `intorg` as a secondary tag in another folder | 211 |
| Records whose only blocktype is `intorg` | 72 |
| `intorg` records with `scope_category: igo` | 350 of 358 |
| `scope_category: igo` records **without** `intorg` | 362 of 712 |

1. **`intorg` describes the form of an entity, not its domain.** Every other
   blocktype answers "what does it do" (`fisheries`, `standards`, `bank`).
   `intorg` answers "what is it", and `scope_category` already answers that.
   350 of the 358 `intorg` records are `igo`.
2. **As an IGO marker it is inconsistent.** 362 IGOs do not carry it. Examples:
   `political` 50, `energy` 42, `military` 38, `bank` 35, `unagency` 34.
   A consumer who filters `list_contains(blocktype, 'intorg')` gets about half the
   IGOs and some non-IGOs. The correct filter is `scope_category = 'igo'`.
3. **The `intorg` folder holds the records that were never given a domain.**
   Most of its 147 records have a clear domain. Many of those domains already
   exist in the taxonomy but have no folder:

   | Taxonomy key without a folder | Uses as a secondary tag | Fits from `intorg/` |
   |---|---|---|
   | `fisheries` | 4 | 17 regional fisheries bodies (RFMOs) |
   | `financial` | 11 | 13 (FATF and its regional bodies, FSB, IOSCO, IAIS) |
   | `development` | 6 | 12 |
   | `tourism` | 1 | 4 |
   | `labor` | 1 | 4 |
   | `disaster` | 7 | 2 |

4. **`scope_category` is wrong for many `intorg` records.** The one-off labeller
   `scripts/oneoff/label_scope_category.py` maps `intorg` to `igo`
   (`ORG_DIRS`, line 64, and the blocktype set, line 104). Because of this,
   NGOs, industry associations, trade unions, partnerships and trust funds are
   labelled `igo`. About 70 `intorg` records have a `legal_status` that
   contradicts `igo`. Examples: `BIMCO` (industry association,
   `membership_count: 2100`), `IATA` (trade association), `WFTU` and
   `ITFTRANSPORT` (union federations), `ISO` and `CEN` (non-governmental),
   and about 20 scientific unions and societies.
5. **Fisheries bodies are split across two folders.** 17 are in `intorg/` and
   17 are in `food/` (`APFIC`, `CCAMLR`, `CCSBT`, `CECAF`, `CIFAA`, `COPESCAALC`,
   `CRFM`, `EIFAAC`, `GFCM`, `GLFC`, `IOTC`, `OLDEPESCA`, `OSPESCA`, `RECOFI`,
   `SWIOFC`, `WCPFC`, `WECAFC`).
6. **Multipurpose regional organizations are spread out.** ASEAN, AU, CBSS and
   OAS are in `political/`. Similar bodies in `intorg/` (`BEACST`, `NCM`, `MSG`,
   `PLG`, `COI`, `ICGLR`, `CICA`) have no domain.

## 2. Target model

- `blocktype` holds the **domain or function** only. The folder is the main
  domain.
- `scope_category` holds the **entity form**: `igo`, `non_state_organization`,
  `policy_forum`, and so on.
- `intorg` is retired. Its meaning moves to `scope_category = 'igo'`.
- Each blocktype in `blocktypes.yaml` gets a `description` (scope note).
  This is most important for keys that overlap: `maritime`, `ocean` and
  `fisheries`; `research` and `scientific`; `legal` and `court`;
  `bank`, `fund` and `financial`; `political` and `forum`.

## 3. Taxonomy changes

**Existing keys that get a folder:** `fisheries`, `financial`, `development`,
`tourism`, `labor`, `disaster`. These are MINOR changes. The keys already exist.

**New keys** (MINOR, new enum values):

| Key | Name | Scope | Records from `intorg/` | Candidates elsewhere |
|-----|------|-------|------------------------|----------------------|
| `governance` | Governance and Public Administration | Public administration, federalism, elections, anti-corruption, transparency | `CAPAM`, `EROPA`, `FORUMOFFEDERATIONS`, `IDEA`, `IACA`, `RAI`, `EITI` | `CAFRAD`, `RESPA` (now `education/`) |
| `commodity` | International Commodity Body | Producer and consumer commodity organizations and study groups | `ICSG`, `ILZSG`, `INSG`, `OIV`, `CPOPC`, `ITTO` | `IGC` (`food/`), `COMMONFUND` (`fund/`). Gaps: ICO, ICCO, ISO (sugar), ICAC, IRSG, IOC (olive) |

Option without `commodity`: use the existing key `mining` for `ICSG`, `ILZSG`,
`INSG`, `EITI` and `IGF`. Put `OIV` and `CPOPC` in `agriculture` and `ITTO` in
`environment`. This option adds fewer keys, but it splits one class of IGO
across three folders.

**Deprecated key:** `intorg`. Mark it deprecated in a MINOR release and remove it
in the next MAJOR release (see `docs/versioning-policy.md`).

## 4. Target folder for each of the 147 records in `intorg/`

`*` means a taxonomy key that exists but has no folder yet.
`**` means a new key.

| Target folder | n | Records |
|---|---|---|
| `fisheries`* | 17 | FFA, IATTC, ICCAT, IPHC, IWC, LVFO, NASCO, NEAFC, NPAFC, NPFC, PSC, SEAFDEC, SEAFO, SIOFA, SPRFMO, EUROFISH, NAFO |
| `financial`* | 13 | FATF, APG, CFATF, EAG, ESAAMLG, GAFISUD, GIABA, MENAFATF, FSB, IOSCO, IAIS, GIFCS, AMRO |
| `development`* | 12 | APO, ACBF, NEPAD, PPD, SOUTHCENTRE, CIRDAP, JDTJUBA, MEKONGINSTITUTE, AAGC, SPC, FILAC, IGF |
| `environment` | 10 | ACTO, INBAR, MOUNTPART, RAINCOALITION, GGGI, SPREP, IPBES, HELCOM, AFOCO, CBFP (secondary `forestry` on AFOCO, CBFP, INBAR) |
| `political` | 9 | BEACST, NCM, MSG, PLG, PBP, COI, ICGLR, CICA, LMDC |
| `governance`** | 7 | CAPAM, EROPA, FORUMOFFEDERATIONS, IDEA, IACA, RAI, EITI |
| `standards` | 7 | CEN, CENELEC, COPANT, EASC, IEC, IAF, AFSEC |
| `commodity`** | 6 | ICSG, ILZSG, INSG, OIV, CPOPC, ITTO |
| `scientific` | 6 | IAU, ICES, ANZLIC, EUROGEOGRAPHICS, ICACI, SOPAC |
| `health` | 5 | GLOBALFUND, UNITAID, CEPI, CARPHA, IIMSAM |
| `agriculture` | 5 | WOAH, EPPO, IPPC, IFDC, IFOAM |
| `maritime` | 5 | IALA, BIMCO, IAPH, GLOBALMARITIMEFORUM, ISA_SEABED |
| `tourism`* | 4 | CTO, ETC, ISTO, PATA |
| `labor`* | 4 | ISSA, OISS, WFTU, ITFTRANSPORT |
| `fund` | 4 | GEF, PROFOR, CGIARFUND, CFTC |
| `legal` | 4 | UNIDROIT, IOMED, IDLO, CMI |
| `transport` | 3 | AFUNIONRAIL, CCRZKR, IRU |
| `research` | 3 | COMSATS, CISRI, D8TTEN |
| `digital` | 3 | DN, GFCE, WAICO |
| `disaster`* | 2 | CDRI, GFDRR |
| `armscontrol` | 2 | OPCW, CTBTO |
| `cultural` | 2 | CF, COMMONWEALTHINSTITUTE |
| `education` | 2 | CAMES, EUCLID |
| `economic` | 2 | ICDT, PBEC |
| one each | 10 | `aviation` IAC; `military` SICOFAA; `court` ITLOS; `humanitarian` ICRC; `meteorology` ECMWF; `patent` NPI; `trade` WCO; `energy` GBEP; `climate` GMI; `telecom` EBU |

Total: 147. A script checked that the table covers each record once.

**Moves from other folders** (optional, same change):

- `food/` to `fisheries/`: the 17 records listed in finding 5.
- `education/` to `governance/`: `CAFRAD`, `RESPA`.
- `food/` to `commodity/`: `IGC`. `fund/` to `commodity/`: `COMMONFUND`.
- `climate/` to `disaster/`: `ADPC`.
- `standards/` to `financial/`: `BCBS`.

## 5. `scope_category` corrections

This work is independent of the blocktype change. Do it first, because the
current `intorg` to `igo` heuristic caused these errors. Each correction is a
PATCH, but the set of records returned by `scope_category = 'igo'` changes.
Record that in `CHANGELOG.md`.

| Proposed value | Records in `intorg/` | Records with an `intorg` tag in other folders |
|---|---|---|
| `non_state_organization` | BIMCO, CAPAM, CEN, CENELEC, COPANT, CMI, COMMONWEALTHINSTITUTE, EBU, EROPA, ETC, EUROGEOGRAPHICS, FORUMOFFEDERATIONS, GLOBALMARITIMEFORUM, IAF, IAPH, IAU, ICACI, IEC, IFOAM, IRU, ISTO, ITFTRANSPORT, PATA, PBEC, WFTU | IATA, UIC, IRF, ISO, ETSI, IFRC, CREDAF, INTERPORTPOLICE, ISC, ICSU, IUPAC, IUPAP, IMU, IUBMB, IUBS, IUCr, IUGG, IUGS, EMS, EUCHEMS, FACS, HUGO, IBRO, WMA, SCAR, SCOR, POGO, IASC, COSPAR, IAF_ASTRO, AAU, ACU, EUA, IAU_UNIV |
| `policy_forum` | GBEP, MOUNTPART, CBFP, JDTJUBA, IGF, GMI, GIFCS, PLG, D8TTEN | GICNT, PASC, EUMETNET |
| `intergovernmental_body` | PROFOR, GFDRR, UNITAID, CFTC, NEPAD, EASC, SOPAC, CGIARFUND | BCBS, IOC_UNESCO |
| `igo` (now `treaty_body`) | ISA_SEABED | — |
| Needs a policy decision | FSB, IAIS, IOSCO, ISSA, CEPI, GLOBALFUND, EITI, ICRC | GAVI, INTOSAI and 7 regional audit bodies, tax-administration associations, CGIAR centres (AVRDC, CIMMYT, ICARDA) |

**Membership roster.** For each record that becomes `non_state_organization`,
check `includes` against `docs/intblock-inclusion-policy.md`. The countries of
member companies or associations are not member states. Examples: `IATA` has
194 includes, and `BIMCO` has `membership_count: 2100` (member companies).
Where no country roster applies, set `membership_applicability: not_applicable`.

**Open policy question.** The six `scope_category` values have no clear place for
two kinds of entity:

- Transgovernmental networks of regulators or agencies (IOSCO, IAIS, INTOSAI,
  the tax-administration associations). Their members are agencies, not states.
- Public-private partnerships (GAVI, Global Fund, CEPI).

Decide whether to use the existing values with a written rule, or to add one new
value (MINOR).

## 6. Phased plan

1. **OpenSpec change** (for example `reorganize-intorg-blocktype`). It covers
   the target model, the new keys `governance` and `commodity`, blocktype
   descriptions, and the deprecation of `intorg`.
2. **Fix `scope_category`** (section 5). Remove `intorg` from `ORG_DIRS` and from
   the blocktype set in `scripts/oneoff/label_scope_category.py`. Add a
   validator warning when `igo` appears with a non-governmental `legal_status`.
3. **Add keys and folders.** Add `governance` and `commodity` to
   `data/blocktypes/blocktypes.yaml` with `description` and translations.
   Create the folders from section 3.
4. **Move the 147 records** (section 4) with `git mv`. Put the target folder
   first in `blocktype`. Keep the other domain tags.
5. **Remove `intorg` as a secondary tag** from the 211 records in other folders.
   After this step, no record uses `intorg`.
6. **Deprecate `intorg` (MINOR).** Mark it deprecated in `blocktypes.yaml` and
   `contract.json`. Add the migration SQL to `CHANGELOG.md`:

   ```sql
   -- before
   SELECT * FROM intblocks WHERE list_contains(blocktype, 'intorg');
   -- after (all IGOs, 712 records instead of 358)
   SELECT * FROM intblocks WHERE scope_category = 'igo';
   ```

7. **Remove `intorg` (MAJOR, v5).** Delete the key and the empty folder.
8. **Update docs and tests:**
   - `docs/llm-scenarios.md` section 11 (example "trade / intorg").
   - `docs/query-examples.md`, around line 1067 (`PICES` expected output),
     together with `tests/test_documented_queries.py:486`.
   - `ORG_PARENT_BLOCKTYPES` in `internacia_builder/validate/cross_rules.py:255`.
   - The test fixtures that use `intorg` as a sample value: `test_builder_export`,
     `test_cross_dataset`, `test_clean_data`, `test_check_artifacts`,
     `test_label_scope_category`, `test_quality_rules`, `test_partof_hierarchy`,
     `test_validate_intblocks`.

## 7. Side findings (not about `intorg`)

- **Export bug in `partof`.** `internacia_builder/clean.py:70-73` converts the
  object form `partof: {id: X, name: Y}` to `list(partof.keys())`, so the value
  becomes `['id', 'name']`. 48 records in `intblocks.parquet` and DuckDB are
  affected, for example `FSB`, `CAPAM`, `ITLOS`, `OPCW` and `LVFO`. The correct
  value is `[partof['id']]`. A list of objects has a similar problem:
  `str(p)` turns each object into a string.
- **Folder does not match the primary blocktype.** The policy says the folder is
  the primary blocktype. In 26 `space/` records, `blocktype[0]` is not `space`
  (for example `intorg|space`, `agreement|space`). The validator only checks
  that the folder name is somewhere in the list.
- **Discovery gaps.** The new folders show missing records: international
  commodity bodies (ICO, ICCO, ISO, ICAC, IRSG, IOC olive), and labour bodies
  (ARLO, OATUU, ITUC).

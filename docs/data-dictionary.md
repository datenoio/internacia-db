# Data dictionary

Field reference generated from JSON Schemas under `data/schemas/`.
For consumption contracts and join keys, see [ai-consumers.md](ai-consumers.md).

## countries

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | yes | ISO 3166-1 alpha-2 country code (primary key). Seven non-standard codes exist; filter code_status = 'official_iso3166_1' for current ISO entries only. |
| `name` | string | yes | Country name in World Bank style (e.g. 'Egypt, Arab Rep.'). English common names are in other_names (id 'en') and common_names. |
| `iso3code` | string | yes | ISO 3166-1 alpha-3 code. Join key for the borders field, which stores alpha-3 neighbor codes. |
| `numeric_code` | string | yes | ISO 3166-1 numeric code as a zero-padded string (e.g. '004'). |
| `capital_city` | object |  | Capital or de facto seat of government with name and optional lat/lng coordinates. Absent by design for uninhabited territories and groupings. |
| `region` | object |  | World Bank region as \{id, value\} (e.g. id 'ECS'). Filter on id: value labels are inconsistent upstream (some carry an '(all income levels)' suffix). Absent for 8 entities the World Bank does not classify. |
| `adminregion` | object |  | World Bank administrative region as \{id, value\}. Only covers low- and middle-income economies; absence for high-income economies is expected. |
| `incomeLevel` | object |  | World Bank income classification as \{id, value\} (e.g. id 'HIC', value 'High income'). Absent for 8 unclassified entities. |
| `lendingType` | object |  | World Bank lending category as \{id, value\} (e.g. IBRD, IDA, Blend). Absent for 8 unclassified entities. |
| `wikidata_id` | string |  | Wikidata entity id (Q-number) for cross-referencing and entity linking. |
| `geonames_id` | string |  | GeoNames integer feature id for the country/territory (as string). |
| `ioc_code` | string |  | International Olympic Committee three-letter country code when assigned. |
| `fifa_code` | string |  | FIFA three-letter association code when assigned. |
| `fips_code` | string |  | Legacy FIPS 10-4 two-letter code when known (US government geospatial). |
| `bbox` | object |  | Optional geographic bounding box \{west, east, north, south\} in WGS84 degrees. |
| `official_name` | string |  | Official long-form state name (e.g. 'Arab Republic of Egypt'). |
| `languages` | array |  | Spoken/official languages as a list of \{code, name, official\} objects. |
| `currencies` | array |  | Circulating currencies as a list of \{code, name, symbol\} objects with ISO 4217 codes. |
| `un_member` | boolean |  | True when the entity is a United Nations member state. See un_status for the three-way member/observer/non_member distinction. |
| `un_status` | string |  | United Nations participation status: member (UN member state), observer (permanent observer state: PS, VA), or non_member. Must be consistent with un_member (member `<=>` un_member: true). Values: `member`, `observer`, `non_member`. |
| `independent` | boolean |  | True when the entity is a widely recognized sovereign state. Explicitly false on non-standard-code records (disputed territories, groupings). |
| `subregion` | string |  | UN M49 subregion label (e.g. 'South-Eastern Asia'). Statistical convenience only; implies no political affiliation. |
| `continents` | array |  | Continent names the entity belongs to (list; transcontinental states list several). |
| `borders` | array |  | Land border neighbors as ISO 3166-1 alpha-3 codes (e.g. CAN, MEX) |
| `population` | object | null |  | Population indicator struct \{value, year, source, source_id\}. Use .value for the number; year is null when the reference year is unknown (never 0). |
| `area` | object | null |  | Land area indicator struct \{value, year, source, source_id\} in square kilometres. Use .value for the number. |
| `gini` | object | null |  | Gini income-inequality index struct \{value, year, source, source_id\}. Sparse: roughly a third of records have no value. |
| `centroid` | object |  | Geographic centroid as \{lat, lng\}. |
| `native_names` | object |  | Native-language names keyed by language code, each with official and common variants. |
| `landlocked` | boolean |  | True when the entity has no coastline. Non-ISO records may be landlocked with an empty borders list (borders holds alpha-3 codes only). |
| `timezones` | array |  | IANA/UTC timezone offsets covering the territory. Empty for uninhabited territories (see timezone_status). |
| `timezone_status` | string |  | Marker explaining an empty timezones list, e.g. 'not_applicable' for uninhabited territories. Values: `not_applicable`. |
| `tld` | string |  | Country-code top-level internet domain (e.g. '.th'). |
| `calling_codes` | array |  | International telephone calling codes (list of strings). |
| `flag_emoji` | string |  | Unicode flag emoji for the country code. |
| `car_side` | string |  | Driving side: 'left' or 'right'. Values: `left`, `right`. |
| `writing_directions` | array |  | Writing direction(s) in use; ids from data/vocabs/writing_directions.yaml (ltr, rtl, ttb). |
| `writing_systems` | array |  | Writing system(s) in use; ids from data/vocabs/writing_systems.yaml. |
| `dvd_region` | integer |  | Commercial DVD region code (1-6) when assigned. |
| `broadcast_systems` | array |  | Television/broadcast standard(s); ids from data/vocabs/broadcast_systems.yaml. |
| `legal_systems` | array |  | Legal tradition(s); ids from data/vocabs/legal_systems.yaml. Not government form. |
| `rail_gauges` | array |  | Railway track gauge(s); ids from data/vocabs/rail_gauges.yaml. |
| `start_of_week` | string |  | First day of the working week (e.g. 'monday', 'sunday'). Values: `monday`, `saturday`, `sunday`. |
| `demonyms` | object |  | Demonyms as \{female, male\} strings in English. |
| `other_names` | array |  | Names in multiple languages (UN official languages) |
| `common_names` | array |  | Common English names and alternative names for the country |
| `m49_code` | string |  | UN M49 numeric code (3-digit code for countries) |
| `entity_type` | string | yes | Entity classification: sovereign_state, dependent_territory, special_administrative_region, disputed_territory, historical_entity, supranational_grouping, or statistical_area. Values: `sovereign_state`, `dependent_territory`, `special_administrative_region`, `disputed_territory`, `historical_entity`, `supranational_grouping`, `statistical_area`. |
| `code_status` | string | yes | Code assignment status: official_iso3166_1 (249 records), user_assigned, obsolete, or exceptionally_reserved. See docs/country-code-policy.md. Values: `official_iso3166_1`, `user_assigned`, `obsolete`, `exceptionally_reserved`. |
| `recognition_status` | object |  | Recognition metadata for non-standard entities: \{status, un_member, notes\} explaining disputed, dissolved, or collective-grouping records. |
| `parent_entity` | object |  | Parent state \{code, name\} for dependent territories and special administrative regions. |
| `provenance` | array |  | Field-level sourcing entries \{field, source, url, retrieved_at, license\} documenting where enriched values came from. |

## intblocks

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Stable uppercase identifier (primary key), e.g. EU, NATO, UN. Renames are tracked in data/datasets/intblocks_aliases.json. |
| `name` | string | yes | Official English name of the organization, group, or agreement. |
| `blocktype` | array | yes | Taxonomy keys from the blocktypes dataset (list). The record's directory under data/intblocks/ matches the primary blocktype. |
| `status` | string | yes | Formality of the entity: e.g. 'formal' (treaty-based organization) or informal grouping. Values: `formal`, `informal`, `de-facto`, `historical`. |
| `languages` | array |  | Official/working languages as ISO 639-1 codes. |
| `links` | array |  | Related URLs as \{url, type\} where type is website, wikipedia, or wikidata. |
| `includes` | array |  | Membership roster. Join on includes[].id (country code or intblock id per type); includes[].name is a display label only. status captures member/observer/former_member etc.; joined/left are ISO dates. |
| `founded` | string |  | Foundation date (YYYY, YYYY-MM, YYYY-MM-DD) or decade (e.g. 1950s) when only decade precision is known |
| `dissolved` | string |  | Dissolution date (ISO string) for defunct entities. |
| `active_period` | object |  | Operational period as \{start, end\} ISO date strings; end is absent for active entities. |
| `headquarters` | object |  | Seat of the organization as \{city, country, coordinates\{lat,lng\}\} with an alpha-2 country code. |
| `geographic_scope` | string |  | Coverage of the membership: 'global' or 'regional'. Values: `global`, `regional`, `sub-regional`, `bilateral`. |
| `scope_category` | string |  | Inclusion taxonomy: igo, treaty_body, policy_forum, or reference_enumeration. See docs/intblock-inclusion-policy.md. Values: `igo`, `treaty_body`, `policy_forum`, `reference_enumeration`. |
| `regions` | array |  | Region labels covered by the entity (e.g. 'worldwide', 'europe', 'africa'). |
| `partof` | any |  | Parent organization id(s) for suborganizations (string or list in source; normalized to a list in exports). |
| `suborganizations` | array |  | Child entities as \{id, name\} references to other intblock records. |
| `acronyms` | array |  | Known acronyms as \{lang, value\} pairs. |
| `wikidata_id` | string |  | Wikidata entity id (Q-number) for cross-referencing and entity linking. |
| `membership_count` | integer |  | Officially stated member count. Interpreted as country members unless membership_count_type says otherwise; compared against the includes roster by validation. |
| `membership_count_type` | string |  | Unit of membership_count. When absent, the count is interpreted as country members and is compared against the includes roster. Non-country counts (companies, individual experts, national governing bodies, etc.) are exempt from roster comparison but require provenance for membership_count. Values: `countries`, `organizations`, `companies`, `individuals`, `mixed`. |
| `membership_applicability` | string |  | When not_applicable, an empty includes list is intentional (conceptual entities, acronyms, etc.) Values: `not_applicable`. |
| `founding_members` | array |  | Country codes of founding members (list). |
| `last_verified` | string |  | Date (YYYY-MM-DD) the record was last checked against official sources. |
| `description` | string |  | Short text summarizing what the entity is for |
| `tags` | array |  | List of keywords for the entity |
| `topics` | array |  | List of topics with which this entity is associated |
| `other_names` | array |  | Names in multiple languages (UN official languages) |
| `notes` | string |  | Additional notes or historical information about the entity |
| `provenance` | array |  | Field-level sourcing for enriched fields |
| `legal_status` | string |  | Legal character of the entity (e.g. intergovernmental, treaty, non-binding) |
| `recognition_status` | string |  | How the entity is recognized within a broader system (e.g. UN specialized agency) |
| `predecessor` | string |  | Id of the entity this one succeeded |
| `successor` | string |  | Id of the entity that succeeded this one |
| `previous_names` | array |  | Former names with the period they were used |
| `official_documents` | array |  | Links to founding or official documents |
| `social_media` | object |  | Social media handles keyed by platform |
| `secretariat` | object |  | Secretariat location and host organization |

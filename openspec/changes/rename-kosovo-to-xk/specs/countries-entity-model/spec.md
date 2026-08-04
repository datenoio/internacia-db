## MODIFIED Requirements

### Requirement: Kosovo user-assigned status

Record `XK` SHALL have `entity_type: disputed_territory`, `code_status: user_assigned`, and `recognition_status` indicating disputed or partially recognized status. The retired alpha-2 code `KV` and alpha-3 code `KSV` SHALL appear in `countries_aliases.json` mapping to `XK` and `XKX` respectively.

#### Scenario: XK is the primary Kosovo code

- **WHEN** a consumer loads `data/countries/XK.yaml` or queries countries by `code = 'XK'`
- **THEN** the Kosovo record is returned with complete profile fields

#### Scenario: Legacy KV resolves via alias

- **WHEN** a consumer looks up country code `KV` in `countries_aliases.json`
- **THEN** the alias resolves to `XK`

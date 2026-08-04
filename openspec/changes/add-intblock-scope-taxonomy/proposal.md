# Change: Add intblock inclusion policy and scope_category field

## Why
The intblock dataset mixes core IGOs, treaties, policy forums, and reference enumerations (e.g., DVD regions) without an explicit taxonomy. Consumers and LLMs cannot filter by entity kind. The deep review recommends `docs/intblock-inclusion-policy.md` and an optional `scope_category` schema field.

## What Changes
- Add `docs/intblock-inclusion-policy.md` defining inclusion criteria and scope categories.
- Add optional `scope_category` to `intblocks.schema.json` (enum: `igo`, `treaty_body`, `policy_forum`, `reference_enumeration`, or documented set).
- Label existing records in a batch pass (at minimum flagship IGOs and obvious enumerations).
- Document in `docs/ai-consumers.md` and `llms.txt`.

## Impact
- Affected specs: intblocks-data-quality, contributor-docs
- Affected code: `data/schemas/intblocks.schema.json`, `data/intblocks/**/*.yaml`, docs

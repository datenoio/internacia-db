## 1. License decision and files

- [x] 1.1 Confirm data license choice with maintainers (chosen: **CC-BY-4.0**; revisit if CC0 preferred)
- [x] 1.2 Add `DATA_LICENSE` with the chosen license statement and canonical link
- [x] 1.3 Add `ATTRIBUTION.md` listing World Bank (CC-BY-4.0), Wikidata (CC0), IANA tzdata, and a recommended citation

## 2. Machine-readable metadata

- [x] 2.1 Add `data_license` SPDX identifier to `countries.manifest.json` written by `scripts/builder.py`
- [x] 2.2 Add `data_license` SPDX identifier to `intblocks.manifest.json`
- [x] 2.3 Add/extend a test asserting manifests carry a non-empty `data_license`

## 3. Documentation

- [x] 3.1 Add a README "License" section separating code (MIT) from data license, linking `ATTRIBUTION.md`
- [x] 3.2 CHANGELOG entry under Added noting the explicit data license and attribution
- [x] 3.3 Run `openspec validate add-data-license --strict`

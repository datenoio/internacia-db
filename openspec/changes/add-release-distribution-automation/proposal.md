# Change: Automate Hugging Face and Zenodo release distribution

## Why
Zenodo DOI and README badge exist (`add-citation-and-odbl-attribution`), but release deposits are manual. The deep review recommends Hugging Face Datasets mirroring and automated Zenodo archiving on tagged releases.

## What Changes
- Add CI step in `.github/workflows/release.yml` to upload Parquet (and lite/CSV when available) to Hugging Face Datasets.
- Add Zenodo API deposit step for release artifacts (or document token-based manual trigger if API setup is deferred).
- Update README and `ATTRIBUTION.md` with HF dataset URL.

## Impact
- Affected specs: dataset-release, data-licensing
- Affected code: `.github/workflows/release.yml`, README, ATTRIBUTION.md

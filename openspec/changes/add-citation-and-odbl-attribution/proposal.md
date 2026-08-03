# Change: Add citation metadata and close the ODbL attribution gap

## Why
A Zenodo DOI for the dataset already exists (10.5281/zenodo.21452328, deposited at v1.7.0, verified live) but is undocumented — no README badge, no `CITATION.cff` — and the strategy doc still lists a DOI as a to-do. Separately, `mledoze/countries` (ODbL-1.0, share-alike) is cited in the per-record `provenance` of 252 of 256 country YAML files yet is absent from `ATTRIBUTION.md`; redistributing ODbL-derived fields inside a CC-BY-4.0 compilation is a genuine license-compatibility question that at minimum requires attribution and a documented rationale.

## What Changes
- Add `CITATION.cff` at the repository root referencing the Zenodo concept DOI so GitHub renders a "Cite this repository" widget.
- Add a Zenodo DOI badge to `README.md` and mention the DOI in `docs/ai-consumers.md` / `ATTRIBUTION.md` citation guidance.
- Add `mledoze/countries` (ODbL-1.0) to the `ATTRIBUTION.md` source table with a short compatibility rationale covering which fields derive from it and why redistribution under CC-BY-4.0 is (or is not) tenable; adjust the data-license statement if the rationale requires it.
- Mark the strategy doc's "publish DOI" item as shipped.

## Impact
- Affected specs: data-licensing
- Affected code: `CITATION.cff` (new), `README.md`, `ATTRIBUTION.md`, `docs/ai-consumers.md`, `docs/strategy-and-user-needs.md`

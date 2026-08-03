# Attribution

The Internacia datasets are a curated compilation. The compilation and the
hand-authored source records are licensed under **CC BY 4.0** (see
[`DATA_LICENSE`](DATA_LICENSE)). Some fields are enriched from third-party
sources that carry their own licenses and attribution requirements, listed below.

## Upstream data sources

| Source | Fields / use | License | Link |
|--------|--------------|---------|------|
| **World Bank** | `population`, `area`, `gini`, `region`, `incomeLevel`, `lendingType` and related classifications | CC BY 4.0 | https://data.worldbank.org/ |
| **Wikidata** | entity linking (`wikidata_id`), `native_names`, multilingual labels, fallbacks | CC0 1.0 (public domain) | https://www.wikidata.org/ |
| **IANA Time Zone Database (tzdata)** | `timezones` mapping (`scripts/data/zone1970.tab`) | Public domain | https://data.iana.org/time-zones/ |
| **mledoze/countries** | `centroid` (geographic centroid `{lat, lng}`, 252 records) | ODbL-1.0 | https://github.com/mledoze/countries |

Per-field provenance (source, retrieval date, and source license) is recorded in
the `provenance` list on individual country records where applicable.

### ODbL compatibility note (mledoze/countries)

The `centroid` field on 252 country records is extracted from
[mledoze/countries](https://github.com/mledoze/countries), which is licensed
under the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
ODbL is a share-alike license, so this single column — considered as a database
extract in its own right — remains available under **ODbL-1.0**, notwithstanding
the CC-BY-4.0 license on the rest of the compilation. In practice:

- If you redistribute or adapt the `centroid` values as a dataset, comply with
  ODbL-1.0 (attribute mledoze/countries and share derived databases alike).
- All other fields, and the compilation as a whole minus `centroid`, are
  CC-BY-4.0 as stated in [`DATA_LICENSE`](DATA_LICENSE).
- Per-record `provenance` entries identify exactly which records carry
  mledoze-derived centroids.

If field-level mixed licensing is unworkable for your use case, drop the
`centroid` column or re-derive centroids from a CC-compatible source.

## How to attribute

When redistributing or building on these datasets, include a credit such as:

> Contains data from Internacia Datasets (https://github.com/datenoio/internacia-db),
> licensed under CC BY 4.0, incorporating data from the World Bank (CC BY 4.0),
> Wikidata (CC0), the IANA Time Zone Database (public domain), and
> mledoze/countries (ODbL-1.0, `centroid` field only).

## Recommended citation

> Common Data Index / Dateno. *Internacia Datasets: reference data of countries,
> intergovernmental organizations, and country groups.* Version <X.Y.Z>.
> https://doi.org/10.5281/zenodo.21452328

Replace `<X.Y.Z>` with the release version you used (see the `version` field in
`data/datasets/countries.manifest.json`). The DOI `10.5281/zenodo.21452328` is
the Zenodo concept DOI and always resolves to the latest deposited version.
Machine-readable citation metadata is in [`CITATION.cff`](CITATION.cff).

## Distribution channels

| Channel | Notes |
|---------|-------|
| GitHub Releases | Primary; Parquet/JSONL/DuckDB assets on each `v*` tag |
| Zenodo | Concept DOI [10.5281/zenodo.21452328](https://doi.org/10.5281/zenodo.21452328) |
| Hugging Face Datasets | Optional mirror when `HF_TOKEN` is configured (see [docs/release-distribution.md](docs/release-distribution.md)) |

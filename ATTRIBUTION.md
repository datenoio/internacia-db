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

Per-field provenance (source, retrieval date, and source license) is recorded in
the `provenance` list on individual country records where applicable.

## How to attribute

When redistributing or building on these datasets, include a credit such as:

> Contains data from Internacia Datasets (https://github.com/commondataio/internacia-db),
> licensed under CC BY 4.0, incorporating data from the World Bank (CC BY 4.0),
> Wikidata (CC0), and the IANA Time Zone Database.

## Recommended citation

> Common Data Index / Dateno. *Internacia Datasets: reference data of countries,
> intergovernmental organizations, and country groups.* Version <X.Y.Z>.
> https://github.com/commondataio/internacia-db

Replace `<X.Y.Z>` with the release version you used (see the `version` field in
`data/datasets/countries.manifest.json`).

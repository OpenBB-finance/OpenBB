# OpenBB EIA Provider Extension

This module integrates the [EIA](https://eia.gov) data provider into the OpenBB Platform,
exposing the [EIA Open Data APIv2](https://www.eia.gov/opendata/) as a set of typed router
endpoints under `obb.eia`, plus the Weekly Petroleum Status Report and Short Term Energy
Outlook models.

## Installation

### PyPI

```sh
pip install openbb-us-eia
```

### From Source

After cloning the main repository, navigate into this folder and enter:

```sh
pip install .
```

To install in editable mode:

```sh
pip install -e .
```

## Authorization

Functions calling the EIA's API require free registration and an API key, obtained [here](https://www.eia.gov/opendata/register.php).


### `user_settings.json`

Add it to the credentials section of `~/.openbb_platform/user_settings.json`

```json
{
    "credentials": {
        "eia_api_key": "REPLACE_WITH_YOUR_KEY"
    }
}
```

### Current Python Session

The credential can be added for the current session only, after importing the OpenBB package.

```python
from openbb import obb

obb.user.credentials.eia_api_key = "REPLACE_WITH_YOUR_KEY"
```

## Coverage

### API Dataset Endpoints

Every dataset published through the EIA APIv2 browser is one command, mirroring the API
browser's route hierarchy: sub-router menus per source, EIA category sub-menus for
petroleum and natural gas, and one parameterized command per dataset. Each command
exposes only that dataset's frequencies, data columns, and filter (facet) parameters;
filter values are validated against the dataset's vocabulary with the valid `code = label`
choices listed on error. Requests paginate automatically until every matching row is
returned; use `limit` to cap the row count.

- `obb.eia.coal.*` - 13 datasets, e.g. `coal.receipts`, `coal.exports_imports_quantity_price`
- `obb.eia.petroleum.<category>.*` - 105 datasets in 7 categories, e.g. `petroleum.prices.spot_prices`
- `obb.eia.natural_gas.<category>.*` - 53 datasets in 7 categories, e.g. `natural_gas.storage.weekly_working_gas_in_underground_storage`
- `obb.eia.electricity.*` - 4 power operations, generator, and retail sales datasets
- `obb.eia.electricity_grid.*` - hourly/daily grid monitor: demand, generation, interchange
- `obb.eia.state_electricity_profiles.*` - 7 annual state profile datasets
- `obb.eia.densified_biomass.*` - 8 wood pellet datasets
- `obb.eia.nuclear_outages.*` - 3 daily outage datasets
- `obb.eia.crude_oil_imports` - imports by origin, destination, and grade
- `obb.eia.international` - country/region energy statistics
- `obb.eia.seds` - State Energy Data System annual estimates
- `obb.eia.total_energy` - Monthly Energy Review series by MSN mnemonic
- `obb.eia.aeo` / `obb.eia.ieo` - Annual and International Energy Outlook projections by release
- `obb.eia.data_browser` - query any APIv2 route directly by path with raw facet filters

### Discovery Endpoints

- `obb.eia.datasets` - the full dataset catalog: routes, frequencies, data columns, and filters
- `obb.eia.facet_options` - valid values for one filter of a dataset, fetched live

### Reports

- `petroleum_status_report` (API key not required) and `short_term_energy_outlook` are
  exposed under `obb.commodity` when `openbb-commodity` is installed, and under `obb.eia`
  otherwise.

## The Metadata Cache and Generated Models

The metadata cache (`openbb_us_eia/assets/eia_catalog.json.xz`) is gitignored and
materialized during the package build by the `hatch_build.py` hook, so wheels and sdists
ship a self-contained artifact - just like the other provider caches. The build hook
reuses an existing local cache; set `OPENBB_EIA_FORCE_CATALOG_REBUILD=1` to force a fresh
crawl at build time. The crawl needs an API key from `EIA_API_KEY` or the OpenBB
`eia_api_key` credential.

The per-dataset model modules (`openbb_us_eia/models/<group>/`) and the fetcher registry
(`openbb_us_eia/models/registry.py`) are checked-in source built from the same metadata
tree: every dataset is one complete model module with readable value slugs, Literal
types, a fully-declared data model with typed columns and units, and a standard Fetcher.
To refresh everything after EIA publishes new routes or facets:

```sh
generate-eia-catalog
```

The command crawls the API, rewrites the cache and model source deterministically,
and gates its own output: emitted modules are passed through `ruff check --fix` and
`ruff format`, and the package is verified with `ty check` before the run reports
success. Pass `--tree path/to/crawl.json` to rebuild from a saved crawl, or
`--asset-only` to rewrite just the cache (what the build hook does).

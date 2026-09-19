# FRED Provider Extension for the OpenBB Platform

`openbb-fred` integrates **Federal Reserve Economic Data**, the database maintained by the
Research division of the Federal Reserve Bank of St. Louis, into the Open Data Platform by
OpenBB. It reads three St. Louis Fed APIs:

- **FRED v1** — `https://api.stlouisfed.org/fred` — series metadata and observations,
  series and release search, and the published release tables.
- **FRED v2** — `https://api.stlouisfed.org/fred/v2` — the cursor-paged
  `release/observations` endpoint, which returns every series on a release together with its
  observations in one call. The key is sent as a bearer token here.
- **GeoFRED** — `https://api.stlouisfed.org/geofred` — series groups and regional data.

The extension ships 36 fetchers, a `fred` router that publishes each of them whenever the
namespace extension that would otherwise own it is not installed, a packaged map of FRED
releases and their tables, and an OpenBB Workspace dashboard.

## Installation

From PyPI:

```console
pip install openbb-fred
```

For local development from a clone of the OpenBB monorepo, run from this folder:

```console
pip install -e .
```

Then build the Python static assets so the `fred` router is registered:

```console
openbb-build
```

## Authentication

A **FRED API key** is required. Get one at <https://fred.stlouisfed.org/docs/api/api_key.html>:
go to <https://fred.stlouisfed.org>, click "My Account", create an account or sign in, select
"API Keys", then "Request API Key" and describe your use case.

The credential is named `fred_api_key`. Set it in any of three ways.

At runtime, for the session:

```python
from openbb import obb

obb.user.credentials.fred_api_key = "YOUR_KEY"
```

In the user settings file, `~/.openbb_platform/user_settings.json`:

```json
{
    "credentials": {
        "fred_api_key": "YOUR_KEY"
    }
}
```

As an environment variable, matched case-insensitively against the credential name:

```console
export FRED_API_KEY=YOUR_KEY
```

The variable is `FRED_API_KEY` — credentials are not read under an `OPENBB_` prefix, so
`OPENBB_FRED_API_KEY` does not set this credential.

The provider records `API_FRED_KEY` as the deprecated alias of `fred_api_key`, for users
carrying settings forward from older releases.

## Quick Start

The fastest way to get started is by connecting to the OpenBB Workspace as a custom backend.

### Start Server

```console
openbb-api
```

This starts the FastAPI server over localhost on port 6900.

### Add to Workspace

See the documentation [here](https://docs.openbb.co/python/quickstart/workspace) for more details.

### Click to Open App

The extension serves a bundled dashboard template at `/api/v1/fred/apps.json`. It is a single
app, **FRED**, with three tabs:

| Tab | Contents |
| --- | --- |
| Search & Series | The series search and the series chart |
| Release Tables | Search, the release-table presentation widget, and the series chart |
| Interest Rates | Yield curve, TIPS yields, EFFR, SOFR, IORB, discount window, ECB rates, mortgage indices, commercial paper, HQM, spot rates, bond indices, and TCM |

The three widgets on the first two tabs are joined by a `symbol` param group, defaulting to
`RSAFS`, so clicking a series id in search or in a release table drives the chart.

Widget ids in the packaged template are written for an installation that has `openbb-economy`,
`openbb-fixedincome`, and `openbb-commodity` present. When one of those is absent its commands
move under `/fred/…`, so the endpoint serving `apps.json` prefixes the affected ids with
`fred_` on the way out — `economy_fred_search_fred_obb` is served as
`fred_economy_fred_search_fred_obb`. The app therefore works either way.

## Coverage

Most of these datasets are served through the Platform's standard models. A standard model is
owned by a namespace extension — `openbb-economy`, `openbb-fixedincome`, or `openbb-commodity`
— and when that extension is installed, the FRED fetcher registers under the standard model
name and answers on that extension's command, selected with `provider="fred"`.

When the owning extension is **absent**, the same fetcher registers under the standard model
name prefixed with `Fred` — `SOFR` becomes `FredSOFR`, `BalanceOfPayments` becomes
`FredBalanceOfPayments` — and this extension's own router publishes an equivalent command
under `/fred/…`, mirroring the standard command name and sub-path. Installing `openbb-fred` on
its own therefore still exposes every dataset below.

Four models are FRED-native and have no standard-model owner, so they always keep their
`Fred` prefix: **`FredSearch`**, **`FredSeries`**, **`FredReleaseTable`**, and
**`FredRegional`**. When `openbb-economy` is installed it hosts them itself, at
`obb.economy.fred_search`, `obb.economy.fred_series`, `obb.economy.fred_release_table`, and
`obb.economy.fred_regional`; when it is absent this router publishes them under
`obb.fred.economy.…`.

The tables below name each command's **standard** model. Except for those four, add the `Fred`
prefix to read the name the model registers under in a standalone installation.

### Economy — owned by `openbb-economy`

Installed: `obb.economy.<command>(provider="fred")`. Standalone: `obb.fred.economy.<command>`,
REST `GET /api/v1/fred/economy/<command>`.

| Command | Model |
| --- | --- |
| `balance_of_payments` | `BalanceOfPayments` |
| `calendar` | `EconomicCalendar` |
| `cpi` | `ConsumerPriceIndex` |
| `pce` | `PersonalConsumptionExpenditures` |
| `retail_prices` | `RetailPrices` |
| `fred_search` | `FredSearch` (native, never re-prefixed) |
| `fred_series` | `FredSeries` (native, never re-prefixed) |
| `fred_release_table` | `FredReleaseTable` (native, never re-prefixed) |
| `fred_regional` | `FredRegional` (native, never re-prefixed) |

### Economy surveys — owned by `openbb-economy`

Installed: `obb.economy.survey.<command>(provider="fred")`. Standalone:
`obb.fred.economy.survey.<command>`.

| Command | Model |
| --- | --- |
| `economic_conditions_chicago` | `SurveyOfEconomicConditionsChicago` |
| `manufacturing_outlook_ny` | `ManufacturingOutlookNY` |
| `manufacturing_outlook_texas` | `ManufacturingOutlookTexas` |
| `nonfarm_payrolls` | `NonFarmPayrolls` |
| `sloos` | `SeniorLoanOfficerSurvey` |
| `university_of_michigan` | `UniversityOfMichigan` |

### Fixed Income — owned by `openbb-fixedincome`

Installed: `obb.fixedincome.<path>(provider="fred")`. Standalone: `obb.fred.fixedincome.<path>`.

| Command | Model |
| --- | --- |
| `bond_indices` | `BondIndices` |
| `mortgage_indices` | `MortgageIndices` |
| `corporate.commercial_paper` | `CommercialPaper` |
| `corporate.hqm` | `HighQualityMarketCorporateBond` |
| `corporate.spot_rates` | `SpotRate` |
| `government.tips_yields` | `TipsYields` |
| `government.yield_curve` | `YieldCurve` |
| `rate.ameribor` | `Ameribor` |
| `rate.dpcredit` | `DiscountWindowPrimaryCreditRate` |
| `rate.ecb` | `EuropeanCentralBankInterestRates` |
| `rate.effr` | `FederalFundsRate` |
| `rate.effr_forecast` | `PROJECTIONS` |
| `rate.estr` | `EuroShortTermRate` |
| `rate.iorb` | `IORB` |
| `rate.overnight_bank_funding` | `OvernightBankFundingRate` |
| `rate.sofr` | `SOFR` |
| `rate.sonia` | `SONIA` |
| `spreads.tcm` | `TreasuryConstantMaturity` |
| `spreads.tcm_effr` | `SelectedTreasuryConstantMaturity` |
| `spreads.treasury_effr` | `SelectedTreasuryBill` |

### Commodity — owned by `openbb-commodity`

Installed: `obb.commodity.price.spot(provider="fred")`. Standalone:
`obb.fred.commodity.price.spot`.

| Command | Model |
| --- | --- |
| `price.spot` | `CommoditySpotPrices` |

### Release table presentation

One command is not model-backed and is **always registered**, whichever namespace extensions
are installed: `obb.fred.economy.release_table`, REST
`GET /api/v1/fred/economy/release_table`. It reads its API key from the user settings
directly.

Where `fred_release_table` returns the release's line items as long-form records, this command
renders a published table the way the release prints it: one row per line, in the release's own
line order, indented to its level, with the periods across the columns, newest first. Each row
carries `series`, `symbol`, `units`, and a `trend` sparkline of the last 36 observations,
followed by one dated column per period. Headings left with nothing under them are dropped, and
lines the hierarchy cannot otherwise tell apart are named by their units or seasonal adjustment.

| Parameter | Default | Description |
| --- | --- | --- |
| `release_id` | `"9"` | The economic release to present |
| `element_id` | `None` | The table within the release; without one, the first table offered is used |
| `frequency` | `None` | `annual`, `quarterly`, `monthly`, `weekly`, or `daily`; without one, the interval the table mostly publishes at |
| `limit` | `8` | How many periods to present |
| `symbol` | `None` | Carried for cross-widget grouping, not read |
| `use_cache` | `True` | Whether to read and write the FRED response cache |

Three companion endpoints back the Workspace pickers and are excluded from the OpenAPI schema:
`release_choices` (every release in the packaged map), `element_choices` (the tables under one
release, indented by depth), and `frequency_choices` (the frequencies one table actually
carries). They drive, in order, the **Release**, **Table**, and **Frequency** dropdowns on the
release-table widget.

## Caching and Rate Limiting

Every FRED request goes through one throttled, retrying, two-tier-cached transport.

- A process-wide throttle holds a minimum gap between successive requests.
- An HTTP 429, or a payload reporting one, is retried with exponential backoff, honouring a
  `Retry-After` header when the response carries one. Past the retry budget the request raises
  an `OpenBBError`.
- Concurrent cacheable requests for the same URL on the same event loop are collapsed into one
  in-flight fetch, and the result is shared.
- **Tier one** is an in-memory LRU cache of deep-copied payloads with a flat lifetime.
- **Tier two** is an on-disk store with a per-endpoint lifetime, backed by `diskcache` — a hard
  dependency of this package. A disk hit is promoted into the memory tier. Empty payloads are
  never written to either tier.
- The API key is stripped from the URL before it is used as a cache key, so no key is written
  to disk.

Every one of the 36 models, and the `release_table` command, takes a per-request `use_cache`
parameter (default `True`). Setting `use_cache=False` bypasses **both** tiers — the response is
neither read from nor written to the memory or disk cache.

On-disk lifetimes, before the multiplier is applied:

| Endpoint path | Lifetime |
| --- | --- |
| `/fred/category`, `/geofred/series/group` | 7 days |
| `/fred/series`, `/fred/series/search`, `/fred/release/series`, `/fred/releases`, `/geofred/series/data`, `/geofred/regional/data` | 1 day |
| `/fred/release/tables` | 6 hours |
| `/fred/series/observations` | 4 hours |
| `/fred/series/updates`, and anything unlisted | 1 hour |

### Environment variables

Disk cache, read on each access:

| Variable | Default | Effect |
| --- | --- | --- |
| `OPENBB_FRED_DISK_CACHE` | `1` | Disk caching is off when set to `0`, `false`, or `False` |
| `OPENBB_FRED_DISK_CACHE_DIR` | `<cache_directory>/fred` | Where the store lives. `cache_directory` is the OpenBB user preference, itself defaulting to `~/OpenBBUserData/cache` |
| `OPENBB_FRED_DISK_CACHE_SIZE` | `536870912` | Size the store is held to, in bytes (`512 * 1024 * 1024`) |
| `OPENBB_FRED_DISK_TTL_MULTIPLIER` | `1.0` | Factor every lifetime above is scaled by |

Throttle, retry, and the in-memory cache, read once when `openbb_fred.utils.rate_limiter` is
first imported — set these before the process starts:

| Variable | Default | Effect |
| --- | --- | --- |
| `OPENBB_FRED_MIN_INTERVAL` | `0.6` | Minimum gap between successive requests, in seconds |
| `OPENBB_FRED_MAX_RETRIES` | `4` | How many times a rate-limited request is retried |
| `OPENBB_FRED_BACKOFF` | `2.0` | Base backoff, in seconds, doubled per attempt |
| `OPENBB_FRED_MAX_BACKOFF` | `30.0` | Ceiling on the computed backoff, in seconds |
| `OPENBB_FRED_CACHE_TTL` | `300.0` | In-memory entry lifetime, in seconds. At `0` or below the memory tier is off |
| `OPENBB_FRED_CACHE_SIZE` | `512` | Maximum in-memory entries. At `0` or below the memory tier is off |

## Maintenance: the release map

`openbb_fred/assets/release_map.json` is a packaged map of every FRED release that is still
publishing, each with the tree of sections and tables beneath it, walked down to depth 2. It is
what `release_choices` and `element_choices` serve, and what the release-table commands fall
back to when a table is asked for that a release does not offer.

The package declares a console script to rebuild it:

```console
generate-fred-release-map
```

Equivalently, without relying on the script being on `PATH`:

```console
python -m openbb_fred.utils.generate_release_map
```

It lists every release, drops the ones whose series are all discontinued or stale, walks the
remaining releases' element trees, and rewrites the asset. It **requires a FRED API key** in the
user settings and exits with an error without one. That is why the generated file is committed
to the repository: a user installing the package cannot rebuild it without a key of their own.

## Usage

The examples below are written for an installation that has the namespace extensions present.
The standalone equivalents are at the end of this section.

**Search for a series id.** `fred_search` runs a full-text search by default, ordered by
`observation_end` so the most recently observed series come first.

```python
from openbb import obb

obb.economy.fred_search(
    query="retail sales",
    search_type="full_text",
    order_by="observation_end",
    sort_order="desc",
    limit=25,
    provider="fred",
).to_df()
```

Passing a `release_id` switches the search to that release and lists every series on it.

```python
obb.economy.fred_search(release_id=9, provider="fred").to_df()
```

**Read observations by series id.** `symbol` takes a comma-separated list, and the FRED-side
`transform`, `frequency`, and `aggregation_method` parameters are applied by the API.

```python
obb.economy.fred_series(
    symbol="GDP,GDPC1",
    start_date="2015-01-01",
    transform="pc1",
    frequency="q",
    aggregation_method="eop",
    provider="fred",
).to_df()
```

**Read a release table.** `fred_release_table` returns the line items as long-form records.
Release 50 is the Employment Situation, and element 462 is its Table A-1.

```python
obb.economy.fred_release_table(
    release_id="50",
    element_id="462",
    provider="fred",
).to_df()
```

The `release_table` presentation command renders a table the way the release publishes it,
with the periods across the columns. Release 9 is the advance monthly retail sales report, and
element 201241 is its seasonally adjusted sales-by-kind-of-business table.

```python
obb.fred.economy.release_table(
    release_id="9",
    element_id="201241",
    frequency="monthly",
    limit=8,
)
```

**Read regional data.** Given a series id, `fred_regional` returns that series alone.

```python
obb.economy.fred_regional(symbol="NYUR", provider="fred").to_df()
```

To read every region at once, look up the series group the series belongs to — not every FRED
series has geographical data — and query that instead. With `is_series_group=True`, the
`frequency`, `region_type`, and `units` parameters are all required.

```python
groups = obb.economy.fred_search(series_id="NYUR", provider="fred").to_df()

obb.economy.fred_regional(
    symbol=groups.series_group[0],
    is_series_group=True,
    region_type=groups.region_type[0],
    units=groups.units[0],
    frequency="a",
    season="nsa",
    provider="fred",
).to_df()
```

**Standard models, answered by FRED.**

```python
obb.economy.cpi(country="united_states", transform="yoy", provider="fred").to_df()
obb.fixedincome.rate.sofr(provider="fred").to_df()
obb.commodity.price.spot(provider="fred").to_df()
```

**Bypass the cache** for one request, reading neither the memory nor the disk tier.

```python
obb.economy.fred_series(symbol="IORB", use_cache=False, provider="fred").to_df()
```

With `openbb-economy`, `openbb-fixedincome`, and `openbb-commodity` absent, the same calls read:

```python
obb.fred.economy.fred_search(query="retail sales", provider="fred").to_df()
obb.fred.economy.fred_series(symbol="GDP,GDPC1", provider="fred").to_df()
obb.fred.economy.fred_release_table(release_id="50", provider="fred").to_df()
obb.fred.economy.fred_regional(symbol="NYUR", provider="fred").to_df()
obb.fred.economy.cpi(country="united_states", provider="fred").to_df()
obb.fred.fixedincome.rate.sofr(provider="fred").to_df()
obb.fred.commodity.price.spot(provider="fred").to_df()
```

`obb.fred.economy.release_table(...)` is unchanged either way.

Documentation for the OpenBB Platform is available at <https://docs.openbb.co/platform>.

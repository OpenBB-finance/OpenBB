# BLS Provider Extension for the OpenBB Platform

`openbb-bls` integrates the U.S. **Bureau of Labor Statistics** into the OpenBB
Platform. It combines three data paths:

- **BLS Public Data API v2** — point-in-time time series by series ID (the only
  endpoint that can use an API key).
- **Published release files** — News Release tables, supplemental XLSX files,
  and the news-release chart packages, parsed directly from `bls.gov`.
- **A bundled series catalog** — a local, partitioned cache of ~1.1M BLS series
  (14 survey families) so the catalog search works offline with no API calls.

A bundled OpenBB Workspace dashboard (`apps.json`) ships five apps: a BLS home
app plus dedicated Employment Situation, CPI, PPI, and Productivity apps.

## Installation

From PyPI:

```console
pip install openbb-bls
```

For local development from a clone of the OpenBB monorepo, run from this folder:

```console
pip install -e .
```

## Authentication

No key is required. Every News-Release table, supplemental table, and chart
endpoint is parsed from published files and works with no credentials.

An (optional) **BLS registration key** only affects the `series` endpoint, where
it raises the per-request limits — 50 symbols / 20-year window / 500 requests
per day (registered) vs. 25 / 10 years / 25 per day (unregistered). Get one at
<https://data.bls.gov/registrationEngine/> and set it as `bls_api_key`:

```python
from openbb import obb

obb.user.credentials.bls_api_key = "YOUR_KEY"
```

## Coverage

Python commands are `obb.bls.<group>.<command>(...)`; the equivalent REST route
is `GET /api/v1/bls/<group>/<command>`. Every group also exposes a `documents`
command listing the release PDFs/files for that program.

### Consumer Price Index — `bls.cpi`

| Command | Description |
| --- | --- |
| `t1_expenditure_category` … `t7_12m_analysis` | News Release tables 1–7 (expenditure category, detailed, special aggregates, selected areas, chained vs. CPI-U, 1-month and 12-month analyses) |
| `relative_importance` | Relative-importance / weights (U.S. city average and selected local areas) |
| `seasonal_factors` | Revised seasonally-adjusted indexes and seasonal factors |
| `supplemental_tables` | C-CPI-U, CPI-W, historical CPI-U, and other supplemental XLSX tables |
| `average_prices`, `by_category`, `by_category_line`, `by_metro`, `by_region` | News-release chart package |

### Employment Situation — `bls.employment_situation`

| Command | Description |
| --- | --- |
| `summary_household`, `summary_establishment` | Summary Tables A (CPS) and B (CES) |
| `t1_employment_changes` … `t7_peak_trough`, `confidence_intervals` | CES analytical tables |
| `civilian_unemployment_rate`, `civilian_unemployment`, `civilian_employment`, `employment_population_ratio`, `labor_force_participation_rate`, `labor_underutilization`, `duration_of_unemployment`, `reasons_for_unemployment`, `unemployment_by_education`, `unemployment_by_veteran_status`, `long_term_unemployed_share`, `not_in_labor_force_indicators`, `not_in_labor_force_want_a_job` | Household-survey (CPS) chart package |
| `employment_levels_by_industry`, `average_weekly_hours_production`, `employment_change_by_industry_ci`, `employment_by_industry_monthly_changes`, `employment_and_hourly_earnings_by_industry`, `employment_and_weekly_earnings_by_industry` | Establishment-survey (CES) chart package |

### Producer Price Index — `bls.ppi`

| Command | Description |
| --- | --- |
| `detailed_report` | Monthly Detailed Report tables (XLSX) |
| `relative_importance`, `seasonal_factors` | Relative importance and seasonal factors |
| `final_demand_1m` / `_12m`, `final_demand_components_1m` / `_12m`, `intermediate_processed_1m` / `_12m`, `intermediate_services_1m` / `_12m`, `intermediate_unprocessed_1m` / `_12m` | Final- and intermediate-demand chart package |

### JOLTS — `bls.jolts`

| Command | Description |
| --- | --- |
| `change_analysis`, `revisions` | Over-the-month change analysis and SA/NSA revisions |
| `beveridge_curve`, `unemp_per_opening`, `openings_by_industry`, `hires_seps_rates`, `openings_hires_seps_levels`, `openings_hires_seps_rates`, `openings_hires_seps_by_region` | Job openings, hires, and separations chart package |

### Productivity & Costs — `bls.productivity`

| Command | Description |
| --- | --- |
| `tables` | Long-form major-sector / total-economy productivity datasets |
| `by_sector`, `nonfarm_business_productivity` / `_indexes` / `_labor_costs`, `manufacturing_productivity` / `_indexes` / `_labor_costs`, `nonfinancial_corporations_indexes` | Major-sector productivity & costs charts |
| `tfp_output_and_inputs`, `tfp_combined_inputs_output`, `tfp_contributions`, `tfp_percent_change`, `tfp_ict_trends`, `tfp_fire_trends` | Total Factor Productivity |
| `wr_productivity_change` / `_by_period`, `wr_1yr_change`, `wr_longterm_change`, `wr_indexes_by_sector`, `wr_labor_cost_by_sector`, `wr_lp_by_industry` | Wholesale & Retail Trade productivity |
| `mm_productivity_change` / `_by_period`, `mm_1yr_change`, `mm_longterm_change`, `mm_indexes_by_industry`, `mm_labor_cost_by_industry` | Mining & Manufacturing productivity |

### Import / Export Price Indexes — `bls.import_export`

| Command | Description |
| --- | --- |
| `price_indexes` | U.S. import and export price indexes |
| `imports_by_category`, `exports_by_category`, `imports_by_origin`, `exports_by_grains`, `air_passenger_fares` | Import/export chart package |

### Real Earnings — `bls.real_earnings`

| Command | Description |
| --- | --- |
| `documents` | Real Earnings news-release archive |

### Search, Series & Calendar

These cross-survey commands fetch live or cached data by series ID:

| Command | Description |
| --- | --- |
| `search` | Search the bundled ~1.1M-series catalog by category, keyword, or code (offline, no API call) |
| `series` | Fetch one or more time series by symbol from the BLS Public Data API (optional `bls_api_key`) |
| `calendar` | BLS data-release schedule |

When `openbb-economy` is installed these register under the Economy `survey`
namespace (e.g. `obb.economy.survey.bls_search(...)`, and the release calendar as
`obb.economy.calendar(provider="bls")`); otherwise they are available standalone
as `obb.bls.search(...)`, `obb.bls.series(...)`, and `obb.bls.calendar(...)`.

## Usage

```python
from openbb import obb

# Latest CPI-U expenditure-category table (no key required)
obb.bls.cpi.t1_expenditure_category(provider="bls").to_df()

# A specific time series from the BLS Public Data API
obb.bls.series(symbol="CUUR0000SA0", provider="bls").to_df()

# Find series in the local catalog, then chart one
obb.bls.search(category="cpi", query="urban", provider="bls").to_df()
```

Documentation for the OpenBB Platform is available at
<https://docs.openbb.co/platform>.

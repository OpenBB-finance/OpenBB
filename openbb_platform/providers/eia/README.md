# OpenBB EIA Provider Extension

This module integrates the [EIA](https://eia.gov) data provider into the OpenBB Platform.

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

### OpenBB Hub

Add the key as "eia_api_key" in the OpenBB Hub Credentials page, [here](https://my.openbb.co/app/platform/credentials)

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

### Endpoints

- `obb.commodity.petroleum_status_report` (API key not required.)
- `obb.commodity.short_term_energy_outlook` (API key required.)

### Weekly Petroluem Status Report

The WPSR is comprised of thirteen (excludes discontinued series) high-level categories with each containing a subset of tables. Data is from the static Excel files published [here](https://www.eia.gov/petroleum/supply/weekly/), and each file represents a single category.

All data from a single category is returned by supplying "all" to the `table` parameter of the WPSR endpoint.

Tables from the WPSR are returned in a flat format in the same order as presented in the Excel files. The response is suitable for pivot tables and SQL storage.

Category choices are defined as:

    balance_sheet
    inputs_and_production
    refiner_and_blender_net_production
    crude_petroleum_stocks
    gasoline_fuel_stocks
    total_gasoline_by_sub_padd
    distillate_fuel_oil_stocks
    imports
    imports_by_country
    weekly_estimates
    spot_prices_crude_gas_heating
    spot_prices_diesel_jet_fuel_propane
    retail_prices

### Short Term Energy Outlook

The Short Term Energy Outlook (STEO) is curated by table, and relies on the EIA V2 API. Tables are defined by their alphanumeric code, and return in the same format as the WPSR tables.

    01: US Energy Markets Summary
    02: Nominal Energy Prices
    03a: World Petroleum and Other Liquid Fuels Production, Consumption, and Inventories
    03b: Non-OPEC Petroleum and Other Liquid Fuels Production
    03c: World Petroleum and Other Liquid Fuels Production
    03d: World Crude Oil Production
    03e: World Petroleum and Other Liquid Fuels Consumption
    04a: US Petroleum and Other Liquid Fuels Supply, Consumption, and Inventories
    04b: US Hydrocarbon Gas Liquids (HGL) and Petroleum Refinery Balances
    04c: US Regional Motor Gasoline Prices and Inventories
    04d: US Biofuel Supply, Consumption, and Inventories
    05a: US Natural Gas Supply, Consumption, and Inventories
    05b: US Regional Natural Gas Prices
    06: US Coal Supply, Consumption, and Inventories
    07a: US Electricity Industry Overview
    07b: US Regional Electricity Retail Sales
    07c: US Regional Electricity Prices
    07d1: US Regional Electricity Generation, Electric Power Sector
    07d2: US Regional Electricity Generation, Electric Power Sector, continued
    07e: US Electricity Generating Capacity
    08: US Renewable Energy Consumption
    09a: US Macroeconomic Indicators and CO2 Emissions
    09b: US Regional Macroeconomic Data
    09c: US Regional Weather Data
    10a: Drilling Productivity Metrics
    10b: Crude Oil and Natural Gas Production from Shale and Tight Formations

    A "symbol" parameter allows lookup by individual series ID(s) within the dataset.
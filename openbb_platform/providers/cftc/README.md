# CFTC Provider Extension

This package provides full access to the CFTC Commitment of Traders database.
Reports are fetched by CFTC Code (e.g. `13874+`) and returns the full history of the contract.

## Installation

Install into a Python environment (3.10 - 3.14) from PyPI with:

```sh
pip install openbb-cftc
```

Then build the Python static assets:

```sh
openbb-build
```

## Credentials

Credentials are not required, but your IP address may be subject to throttling limits.

API requests made using an application token are not throttled.

Create a free account here: https://evergreen.data.socrata.com/signup

Then, generate the app_token by signing in with the credentials here: https://publicreporting.cftc.gov/profile/edit/developer_settings.

### Credentials Key

If adding a token, use `cftc_app_token` as the key in the `user_settings.json` file. The value expected value is the app_token and not the `secret` or `api_key`.

The token can be set as an environment variable:

```env
CFTC_APP_TOKEN
```

## Coverage

This extension provides a dedicated router module with two endpoints, and one OpenBB Workspace application.

- `obb.cftc.cot`
- `obb.cftc.cot_search`

## Usage

The package can be used as a Python module, or a REST API.

### REST API

Start the server over localhost with:

```sh
openbb-api
```

### Python

```python
from openbb import obb

search_results = obb.cftc.cot_search(query="gold")

print(search_results.to_df())
```

| code        | name               | category          | subcategory     | commodity_name   | contract_units                 |
|:------------|:-------------------|:------------------|:----------------|:-----------------|:-------------------------------|
| CFTC_088691 | GOLD               | NATURAL RESOURCES | PRECIOUS METALS | GOLD             | (CONTRACTS OF 100 TROY OUNCES) |
| CFTC_088LM1 | GOLD -1 TROY OUNCE | NATURAL RESOURCES | PRECIOUS METALS | GOLD             | (1 troy ounce x $2,300)        |
| CFTC_088695 | MICRO GOLD         | NATURAL RESOURCES | PRECIOUS METALS | GOLD             | (CONTRACTS OF 10 TROY OUNCES)  |

```python
report = obb.cftc.cot(code="CFTC_088695", measure="percent_of_oi", limit=4)
print(report.to_df().T)
```

|                                             |   2026-03-03 |   2026-03-10 |   2026-03-17 |   2026-03-24 |
|:--------------------------------------------|-------------:|-------------:|-------------:|-------------:|
| open_interest_all                           |    60933     |    58119     |    64124     |    71998     |
| open_interest_pct_all                       |        1     |        1     |        1     |        1     |
| open_interest_pct_non_commercial_long_all   |        0.186 |        0.18  |        0.168 |        0.285 |
| open_interest_pct_non_commercial_short_all  |        0.527 |        0.546 |        0.555 |        0.515 |
| open_interest_pct_non_commercial_spread     |        0.058 |        0.06  |        0.078 |        0.124 |
| open_interest_pct_commercial_long_all       |        0.088 |        0.095 |        0.091 |        0.083 |
| open_interest_pct_commercial_short_all      |        0     |        0     |        0     |        0     |
| open_interest_pct_total_reportable_long_all |        0.333 |        0.335 |        0.336 |        0.492 |
| open_interest_pct_total_reportable_short    |        0.585 |        0.606 |        0.632 |        0.64  |
| open_interest_pct_non_reportable_long_all   |        0.667 |        0.665 |        0.664 |        0.508 |
| open_interest_pct_non_reportable_short_all  |        0.415 |        0.394 |        0.368 |        0.36  |

## Report Types

Reports can be filtered by measure, or include all reported fields. Report types come as 'Futures Only', or 'Combined' (futures and options combined positions), selectable by setting the `futures_only` boolean parameter.

### Legacy

The Legacy report is broken down by exchange with reported open interest further broken down into three trader classifications: commercial, non-commercial and non-reportable.

### Disaggregated

The Disaggregated reports are broken down by Agriculture and Natural Resource contracts. The Disaggregated reports break down reportable open interest positions into four classifications: Producer/Merchant, Swap Dealers, Managed Money and Other Reportables.

### Financial

The Traders in Financial Futures (TFF) report includes financial contracts. The TFF report breaks down the reported open interest into five classifications: Dealer, Asset Manager, Leveraged Money, Other Reportables and Non-Reportables.

### Supplemental

The Supplemental report includes 13 select agricultural commodity contracts for combined futures and options positions. Supplemental reports break down the reportable open interest positions into three trader classifications: non-commercial, commercial, and index traders.

Visit the CFTC [website](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) for detailed descriptions of reports and classification methodology.

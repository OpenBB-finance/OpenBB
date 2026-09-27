# openbb-arkleon

OpenBB Platform provider extension that serves SEC filing facts from Arkleon /v1 as the `arkleon` provider.

## Install

Requires Python 3.10 or later, below 4. The package depends on `openbb-core` (>=1.6.10,<3) and registers the entry point `arkleon` in the `openbb_provider_extension` group.

The package is not yet on PyPI. Install it from GitHub, then rebuild the OpenBB Python interface as the OpenBB docs require after installing a provider extension:

```
pip install git+https://github.com/jushuea/openbb-arkleon
openbb-build
```

## Credentials

Set the `ARKLEON_API_KEY` environment variable to an issued Arkleon `ak_` key:

```
export ARKLEON_API_KEY=ak_...
```

Or set it from Python:

```python
obb.user.credentials.arkleon_api_key = "ak_..."
```

Requests go to `https://arkleon.com/v1/facts` with the header `Authorization: Bearer <key>`.

## Example

```python
from openbb import obb
# ARKLEON_API_KEY is set in the environment
obb.equity.fundamental.balance(symbol="320193", provider="arkleon", as_of="2020-01-01")
```

This returns balance sheet records for CIK 320193 from filings filed on or before 2020-01-01. The `as_of` date filters on the filing date, never on the period a fact describes, so a period ending in 2019 whose 10-K was filed after 2020-01-01 is not included.

## Commands

The provider serves 3 commands, each with `provider="arkleon"`:

- `obb.equity.fundamental.balance`
- `obb.equity.fundamental.income`
- `obb.equity.fundamental.cash`

## Parameters

| Parameter | Commands | Description |
|---|---|---|
| `symbol` | all | The company's SEC CIK, digits only. Arkleon /v1 does not serve tickers. |
| `as_of` | all | Required, no default. Format `YYYY-MM-DD`. Only facts from filings filed on or before this date are returned. Filters on the filing date, never on the period end. |
| `limit` | all | Keeps the most recent N distinct period end dates. Every filing for those dates is kept. |
| `period` | `income`, `cash` | `"annual"` returns 4-quarter durations. `"quarter"` returns 1-quarter durations. Values are exactly as filed. Year-to-date values are not converted into quarters. |

`balance` does not take `period`. Balance sheet facts are instantaneous.

## What each record contains

Each record is 1 (filing, period end) pair. Every record carries:

- `period_ending`
- `accession_id`
- `form`
- `filed`
- `source_url`
- `duration_quarters`
- the mapped fields for the statement, listed in the tables below

A period end appears in 1 record for each filing that reported it. A value first filed in a 10-K and reported again as a prior-year comparative in the next year's 10-K appears as 2 records, each with its own `filed` date.

Only consolidated facts are used. Segment and co-registrant rows are excluded.

Where a field lists 2 tags, the first tag the filing reports is used. A field the filing did not report is empty. Nothing is summed, derived, or synthesized.

## Field maps

The listed tags are `us-gaap` element names. Requests match on the element name alone and do not filter on taxonomy, so a company extension element with the same name would also be returned.

### Balance sheet

Instantaneous facts, unit USD.

| Field | Tags |
|---|---|
| `total_assets` | `Assets` |
| `total_current_assets` | `AssetsCurrent` |
| `cash_and_cash_equivalents` | `CashAndCashEquivalentsAtCarryingValue` |
| `total_liabilities` | `Liabilities` |
| `total_current_liabilities` | `LiabilitiesCurrent` |
| `long_term_debt` | `LongTermDebtNoncurrent` |
| `total_equity` | `StockholdersEquity` |
| `total_liabilities_and_equity` | `LiabilitiesAndStockholdersEquity` |

### Income statement

Unit USD. The `eps_basic` and `eps_diluted` fields are USD/shares. Where 2 tags are listed, they are tried in order.

| Field | Tags |
|---|---|
| `revenue` | `RevenueFromContractWithCustomerExcludingAssessedTax`, `Revenues` |
| `cost_of_revenue` | `CostOfGoodsAndServicesSold`, `CostOfRevenue` |
| `gross_profit` | `GrossProfit` |
| `operating_income` | `OperatingIncomeLoss` |
| `net_income` | `NetIncomeLoss` |
| `eps_basic` | `EarningsPerShareBasic` |
| `eps_diluted` | `EarningsPerShareDiluted` |

### Cash flow statement

Unit USD.

| Field | Tags |
|---|---|
| `net_cash_from_operating_activities` | `NetCashProvidedByUsedInOperatingActivities` |
| `net_cash_from_investing_activities` | `NetCashProvidedByUsedInInvestingActivities` |
| `net_cash_from_financing_activities` | `NetCashProvidedByUsedInFinancingActivities` |
| `capital_expenditure` | `PaymentsToAcquirePropertyPlantAndEquipment` |

## Tests

The tests run offline:

```
pytest
```

Fixtures are built by `tests/build_fixtures.py` from a SEC EDGAR companyfacts recording for CIK 320193, reshaped to the `/v1/facts` response shape. They are not recorded /v1 responses.

## License

MIT.

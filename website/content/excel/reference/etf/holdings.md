<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the holdings for an individual ETF.

```excel wordwrap
=OBB.ETF.HOLDINGS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. (ETF) | false |
| provider | string | Options: fmp | true |
| date | string | A specific date to get data for. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. (provider: fmp) | true |
| cik | string | The CIK of the filing entity. Overrides symbol. (provider: fmp) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (ETF)  |
| name | Name of the ETF holding.  |
| lei | The LEI of the holding. (provider: fmp) |
| title | The title of the holding. (provider: fmp) |
| cusip | The CUSIP of the holding. (provider: fmp) |
| isin | The ISIN of the holding. (provider: fmp) |
| balance | The balance of the holding. (provider: fmp) |
| units | The units of the holding. (provider: fmp) |
| currency | The currency of the holding. (provider: fmp) |
| value | The value of the holding in USD. (provider: fmp) |
| weight | The weight of the holding in ETF in %. (provider: fmp) |
| payoff_profile | The payoff profile of the holding. (provider: fmp) |
| asset_category | The asset category of the holding. (provider: fmp) |
| issuer_category | The issuer category of the holding. (provider: fmp) |
| country | The country of the holding. (provider: fmp) |
| is_restricted | Whether the holding is restricted. (provider: fmp) |
| fair_value_level | The fair value level of the holding. (provider: fmp) |
| is_cash_collateral | Whether the holding is cash collateral. (provider: fmp) |
| is_non_cash_collateral | Whether the holding is non-cash collateral. (provider: fmp) |
| is_loan_by_fund | Whether the holding is loan by fund. (provider: fmp) |
| cik | The CIK of the filing. (provider: fmp) |
| acceptance_datetime | The acceptance datetime of the filing. (provider: fmp) |

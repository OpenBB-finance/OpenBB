---
title: major_holders
description: Get detailed information about equity ownership and stock ownership,
  including investment data, security data, market value data, shares data, performance
  data, and ownership data. Use the equity ownership API to retrieve equity ownership
  details, and explore various stock ownership parameters and returns. Access company
  ownership data, investor data, filing data, industry data, and more.
keywords:
- equity ownership
- company ownership
- equity ownership API
- equity ownership data
- equity ownership parameters
- equity ownership returns
- equity ownership data fields
- stock ownership
- stock ownership data
- stock ownership API
- stock ownership parameters
- stock ownership returns
- stock ownership data fields
- investment data
- security data
- market value data
- shares data
- performance data
- ownership data
- equity ownership details
- stock ownership details
- equity ownership information
- stock ownership information
- company ownership data
- investor data
- filing data
- industry data
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Equity Ownership. Information about the company ownership.

```python wordwrap
obb.equity.ownership.major_holders(symbol: Union[str, List[str]], date: date = None, page: int = 0, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| date | date | A specific date to get data for. | None | True |
| page | int | Page number of the data to fetch. | 0 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquityOwnership]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| cik | int | Cik of the stock ownership. |
| filing_date | date | Filing date of the stock ownership. |
| investor_name | str | Investor name of the stock ownership. |
| symbol | str | Symbol representing the entity requested in the data. |
| security_name | str | Security name of the stock ownership. |
| type_of_security | str | Type of security of the stock ownership. |
| security_cusip | str | Security cusip of the stock ownership. |
| shares_type | str | Shares type of the stock ownership. |
| put_call_share | str | Put call share of the stock ownership. |
| investment_discretion | str | Investment discretion of the stock ownership. |
| industry_title | str | Industry title of the stock ownership. |
| weight | float | Weight of the stock ownership. |
| last_weight | float | Last weight of the stock ownership. |
| change_in_weight | float | Change in weight of the stock ownership. |
| change_in_weight_percentage | float | Change in weight percentage of the stock ownership. |
| market_value | int | Market value of the stock ownership. |
| last_market_value | int | Last market value of the stock ownership. |
| change_in_market_value | int | Change in market value of the stock ownership. |
| change_in_market_value_percentage | float | Change in market value percentage of the stock ownership. |
| shares_number | int | Shares number of the stock ownership. |
| last_shares_number | int | Last shares number of the stock ownership. |
| change_in_shares_number | float | Change in shares number of the stock ownership. |
| change_in_shares_number_percentage | float | Change in shares number percentage of the stock ownership. |
| quarter_end_price | float | Quarter end price of the stock ownership. |
| avg_price_paid | float | Average price paid of the stock ownership. |
| is_new | bool | Is the stock ownership new. |
| is_sold_out | bool | Is the stock ownership sold out. |
| ownership | float | How much is the ownership. |
| last_ownership | float | Last ownership amount. |
| change_in_ownership | float | Change in ownership amount. |
| change_in_ownership_percentage | float | Change in ownership percentage. |
| holding_period | int | Holding period of the stock ownership. |
| first_added | date | First added date of the stock ownership. |
| performance | float | Performance of the stock ownership. |
| performance_percentage | float | Performance percentage of the stock ownership. |
| last_performance | float | Last performance of the stock ownership. |
| change_in_performance | float | Change in performance of the stock ownership. |
| is_counted_for_performance | bool | Is the stock ownership counted for performance. |
</TabItem>

</Tabs>


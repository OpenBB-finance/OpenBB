---
title: holdings
description: Learn how to get the holdings data for an individual ETF using the `obb.etf.holdings`
  method. Understand the parameters like symbol, provider, date, and CIK. Explore
  the returns, results, warnings, chart, and metadata. Dive into the data fields like
  symbol, name, LEI, title, CUSIP, ISIN, balance, units, currency, value, weight,
  payoff profile, asset category, issuer category, country, and more.
keywords:
- ETF holdings
- individual ETF holdings
- holdings data for ETF
- symbol
- provider
- date
- CIK
- returns
- results
- warnings
- chart
- metadata
- data
- name
- LEI
- title
- CUSIP
- ISIN
- balance
- units
- currency
- value
- weight
- payoff profile
- asset category
- issuer category
- country
- is restricted
- fair value level
- is cash collateral
- is non-cash collateral
- is loan by fund
- acceptance datetime
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the holdings for an individual ETF.

```python wordwrap
obb.etf.holdings(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| date | Union[str, date] | A specific date to get data for. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. | None | True |
| cik | str | The CIK of the filing entity. Overrides symbol. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EtfHoldings]
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
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF holding. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF holding. |
| lei | str | The LEI of the holding. |
| title | str | The title of the holding. |
| cusip | str | The CUSIP of the holding. |
| isin | str | The ISIN of the holding. |
| balance | float | The balance of the holding. |
| units | Union[str, float] | The units of the holding. |
| currency | str | The currency of the holding. |
| value | float | The value of the holding in USD. |
| weight | float | The weight of the holding in ETF in %. |
| payoff_profile | str | The payoff profile of the holding. |
| asset_category | str | The asset category of the holding. |
| issuer_category | str | The issuer category of the holding. |
| country | str | The country of the holding. |
| is_restricted | str | Whether the holding is restricted. |
| fair_value_level | int | The fair value level of the holding. |
| is_cash_collateral | str | Whether the holding is cash collateral. |
| is_non_cash_collateral | str | Whether the holding is non-cash collateral. |
| is_loan_by_fund | str | Whether the holding is loan by fund. |
| cik | str | The CIK of the filing. |
| acceptance_datetime | str | The acceptance datetime of the filing. |
</TabItem>

</Tabs>


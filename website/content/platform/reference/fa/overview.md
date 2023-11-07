---
title: overview
description: This page provides information about the functionality of the 'company
  overview' feature, detailing its parameters, returns, and data types. It extensively
  discusses attributes like symbol, provider, market capitalization, beta, volume
  average, dividends, and more. It's a comprehensive guide for understanding the data
  this function outputs.
keywords:
- company overview
- data
- provider
- symbol
- parameters
- returns
- data types
- fmp
- market capitalization
- beta
- volume average
- dividend
- changes
- cik
- isin
- exchange
- industry
- ceo
- sector
- country
- full time employees
- phone number
- address
- discounted cash flow
- ipo date
- trading
- fund
- etf
- adr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.overview - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Company Overview. General information about a company.

```python wordwrap
overview(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CompanyOverview]
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
| symbol | str | Symbol to get data for. |
| price | float | Price of the company. |
| beta | float | Beta of the company. |
| vol_avg | int | Volume average of the company. |
| mkt_cap | int | Market capitalization of the company. |
| last_div | float | Last dividend of the company. |
| range | str | Range of the company. |
| changes | float | Changes of the company. |
| company_name | str | Company name of the company. |
| currency | str | Currency of the company. |
| cik | str | CIK of the company. |
| isin | str | ISIN of the company. |
| cusip | str | CUSIP of the company. |
| exchange | str | Exchange of the company. |
| exchange_short_name | str | Exchange short name of the company. |
| industry | str | Industry of the company. |
| website | str | Website of the company. |
| description | str | Description of the company. |
| ceo | str | CEO of the company. |
| sector | str | Sector of the company. |
| country | str | Country of the company. |
| full_time_employees | str | Full time employees of the company. |
| phone | str | Phone of the company. |
| address | str | Address of the company. |
| city | str | City of the company. |
| state | str | State of the company. |
| zip | str | Zip of the company. |
| dcf_diff | float | Discounted cash flow difference of the company. |
| dcf | float | Discounted cash flow of the company. |
| image | str | Image of the company. |
| ipo_date | date | IPO date of the company. |
| default_image | bool | If the image is the default image. |
| is_etf | bool | If the company is an ETF. |
| is_actively_trading | bool | If the company is actively trading. |
| is_adr | bool | If the company is an ADR. |
| is_fund | bool | If the company is a fund. |
</TabItem>

</Tabs>

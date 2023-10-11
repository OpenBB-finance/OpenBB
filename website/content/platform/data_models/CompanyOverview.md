---
title: Company Overview
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CompanyOverview` | `CompanyOverviewQueryParams` | `CompanyOverviewData` |

### Import Statement

```python
from openbb_provider.standard_models.company_overview import (
CompanyOverviewData,
CompanyOverviewQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| price | Union[float] | Price of the company. |
| beta | Union[float] | Beta of the company. |
| vol_avg | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Volume average of the company. |
| mkt_cap | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Market capitalization of the company. |
| last_div | Union[float] | Last dividend of the company. |
| range | Union[str] | Range of the company. |
| changes | Union[float] | Changes of the company. |
| company_name | Union[str] | Company name of the company. |
| currency | Union[str] | Currency of the company. |
| cik | Union[str] | CIK of the company. |
| isin | Union[str] | ISIN of the company. |
| cusip | Union[str] | CUSIP of the company. |
| exchange | Union[str] | Exchange of the company. |
| exchange_short_name | Union[str] | Exchange short name of the company. |
| industry | Union[str] | Industry of the company. |
| website | Union[str] | Website of the company. |
| description | Union[str] | Description of the company. |
| ceo | Union[str] | CEO of the company. |
| sector | Union[str] | Sector of the company. |
| country | Union[str] | Country of the company. |
| full_time_employees | Union[str] | Full time employees of the company. |
| phone | Union[str] | Phone of the company. |
| address | Union[str] | Address of the company. |
| city | Union[str] | City of the company. |
| state | Union[str] | State of the company. |
| zip | Union[str] | Zip of the company. |
| dcf_diff | Union[float] | Discounted cash flow difference of the company. |
| dcf | Union[float] | Discounted cash flow of the company. |
| image | Union[str] | Image of the company. |
| ipo_date | Union[date] | IPO date of the company. |
| default_image | bool | If the image is the default image. |
| is_etf | bool | If the company is an ETF. |
| is_actively_trading | bool | If the company is actively trading. |
| is_adr | bool | If the company is an ADR. |
| is_fund | bool | If the company is a fund. |
</TabItem>

</Tabs>


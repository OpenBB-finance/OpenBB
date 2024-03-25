---
title: "share_statistics"
description: "Learn how to retrieve and analyze share statistics for a given company  using the obb.equity.ownership.share_statistics API endpoint. This documentation  provides details on the parameters, return values, and data structure."
keywords:
- share statistics
- company statistics
- equity ownership
- symbol
- provider
- data
- free float
- float shares
- outstanding shares
- source
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/ownership/share_statistics - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get data about share float for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.ownership.share_statistics(symbol='AAPL', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : ShareStatistics
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'yfinance']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
| adjusted_outstanding_shares | float | Total number of shares of a publicly-traded company, adjusted for splits. |
| public_float | float | Aggregate market value of the shares of a publicly-traded company. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
| implied_shares_outstanding | int | Implied Shares Outstanding of common equity, assuming the conversion of all convertible subsidiary equity into common. |
| short_interest | int | Number of shares that are reported short. |
| short_percent_of_float | float | Percentage of shares that are reported short, as a normalized percent. |
| days_to_cover | float | Number of days to repurchase the shares as a ratio of average daily volume |
| short_interest_prev_month | int | Number of shares that were reported short in the previous month. |
| short_interest_prev_date | date | Date of the previous month's report. |
| insider_ownership | float | Percentage of shares held by insiders, as a normalized percent. |
| institution_ownership | float | Percentage of shares held by institutions, as a normalized percent. |
| institution_float_ownership | float | Percentage of float held by institutions, as a normalized percent. |
| institutions_count | int | Number of institutions holding shares. |
</TabItem>

</Tabs>


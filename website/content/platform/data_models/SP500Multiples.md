---
title: S&P 500 Multiples
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `SP500Multiples` | `SP500MultiplesQueryParams` | `SP500MultiplesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.sp500_multiples import (
SP500MultiplesData,
SP500MultiplesQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| series_name | Literal['Shiller PE Ratio by Month', 'Shiller PE Ratio by Year', 'PE Ratio by Year', 'PE Ratio by Month', 'Dividend by Year', 'Dividend by Month', 'Dividend Growth by Quarter', 'Dividend Growth by Year', 'Dividend Yield by Year', 'Dividend Yield by Month', 'Earnings by Year', 'Earnings by Month', 'Earnings Growth by Year', 'Earnings Growth by Quarter', 'Real Earnings Growth by Year', 'Real Earnings Growth by Quarter', 'Earnings Yield by Year', 'Earnings Yield by Month', 'Real Price by Year', 'Real Price by Month', 'Inflation Adjusted Price by Year', 'Inflation Adjusted Price by Month', 'Sales by Year', 'Sales by Quarter', 'Sales Growth by Year', 'Sales Growth by Quarter', 'Real Sales by Year', 'Real Sales by Quarter', 'Real Sales Growth by Year', 'Real Sales Growth by Quarter', 'Price to Sales Ratio by Year', 'Price to Sales Ratio by Quarter', 'Price to Book Value Ratio by Year', 'Price to Book Value Ratio by Quarter', 'Book Value per Share by Year', 'Book Value per Share by Quarter'] | The name of the series. Defaults to 'PE Ratio by Month'. | PE Ratio by Month | True |
| start_date | str | Start date of the data, in YYYY-MM-DD format. |  | True |
| end_date | str | End date of the data, in YYYY-MM-DD format. |  | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| series_name | Literal['Shiller PE Ratio by Month', 'Shiller PE Ratio by Year', 'PE Ratio by Year', 'PE Ratio by Month', 'Dividend by Year', 'Dividend by Month', 'Dividend Growth by Quarter', 'Dividend Growth by Year', 'Dividend Yield by Year', 'Dividend Yield by Month', 'Earnings by Year', 'Earnings by Month', 'Earnings Growth by Year', 'Earnings Growth by Quarter', 'Real Earnings Growth by Year', 'Real Earnings Growth by Quarter', 'Earnings Yield by Year', 'Earnings Yield by Month', 'Real Price by Year', 'Real Price by Month', 'Inflation Adjusted Price by Year', 'Inflation Adjusted Price by Month', 'Sales by Year', 'Sales by Quarter', 'Sales Growth by Year', 'Sales Growth by Quarter', 'Real Sales by Year', 'Real Sales by Quarter', 'Real Sales Growth by Year', 'Real Sales Growth by Quarter', 'Price to Sales Ratio by Year', 'Price to Sales Ratio by Quarter', 'Price to Book Value Ratio by Year', 'Price to Book Value Ratio by Quarter', 'Book Value per Share by Year', 'Book Value per Share by Quarter'] | The name of the series. Defaults to 'PE Ratio by Month'. | PE Ratio by Month | True |
| start_date | str | Start date of the data, in YYYY-MM-DD format. |  | True |
| end_date | str | End date of the data, in YYYY-MM-DD format. |  | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | monthly | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | The transformation of the time series. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>

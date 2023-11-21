---
title: sp500_multiples
description: Learn about S&P 500 multiples and Shiller PE ratios. Use the `index.sp500_multiples`
  query to retrieve historical data on various financial metrics such as PE Ratio,
  Dividend, Earnings, Inflation Adjusted Price, Sales, Price to Sales Ratio, and Book
  Value per Share. Specify query parameters such as start date, end date, and provider.
  Collapse the frequency or transform the time series. Get results, charts, metadata,
  and more.
keywords:
- S&P 500 multiples
- Shiller PE ratios
- SP500Multiples
- index.sp500_multiples
- historical data
- PE Ratio
- Dividend
- Earnings
- Inflation Adjusted Price
- Sales
- Price to Sales Ratio
- Book Value per Share
- query parameters
- start date
- end date
- provider
- collapse
- transform
- results
- chart
- metadata
- data
- date
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

S&P 500 Multiples. Historical S&P 500 multiples and Shiller PE ratios.

```python wordwrap
obb.index.sp500_multiples(series_name: Literal[str] = PE Ratio by Month, start_date: str, end_date: str, provider: Literal[str] = nasdaq)
```

---

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

---

## Returns

```python wordwrap
OBBject
    results : List[SP500Multiples]
        Serializable results.

    provider : Optional[Literal['nasdaq']]
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
</TabItem>

</Tabs>


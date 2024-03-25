---
title: "sp500_multiples"
description: "Learn about S&P 500 multiples and Shiller PE ratios. Use the `index.sp500_multiples`  query to retrieve historical data on various financial metrics such as PE Ratio,  Dividend, Earnings, Inflation Adjusted Price, Sales, Price to Sales Ratio, and Book  Value per Share. Specify query parameters such as start date, end date, and provider.  Collapse the frequency or transform the time series. Get results, charts, metadata,  and more."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="index/sp500_multiples - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical S&P 500 multiples and Shiller PE ratios.


Examples
--------

```python
from openbb import obb
obb.index.sp500_multiples(provider='nasdaq')
obb.index.sp500_multiples(series_name='shiller_pe_year', provider='nasdaq')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| series_name | Literal['shiller_pe_month', 'shiller_pe_year', 'pe_year', 'pe_month', 'dividend_year', 'dividend_month', 'dividend_growth_quarter', 'dividend_growth_year', 'dividend_yield_year', 'dividend_yield_month', 'earnings_year', 'earnings_month', 'earnings_growth_year', 'earnings_growth_quarter', 'real_earnings_growth_year', 'real_earnings_growth_quarter', 'earnings_yield_year', 'earnings_yield_month', 'real_price_year', 'real_price_month', 'inflation_adjusted_price_year', 'inflation_adjusted_price_month', 'sales_year', 'sales_quarter', 'sales_growth_year', 'sales_growth_quarter', 'real_sales_year', 'real_sales_quarter', 'real_sales_growth_year', 'real_sales_growth_quarter', 'price_to_sales_year', 'price_to_sales_quarter', 'price_to_book_value_year', 'price_to_book_value_quarter', 'book_value_year', 'book_value_quarter'] | The name of the series. Defaults to 'pe_month'. | pe_month | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| series_name | Literal['shiller_pe_month', 'shiller_pe_year', 'pe_year', 'pe_month', 'dividend_year', 'dividend_month', 'dividend_growth_quarter', 'dividend_growth_year', 'dividend_yield_year', 'dividend_yield_month', 'earnings_year', 'earnings_month', 'earnings_growth_year', 'earnings_growth_quarter', 'real_earnings_growth_year', 'real_earnings_growth_quarter', 'earnings_yield_year', 'earnings_yield_month', 'real_price_year', 'real_price_month', 'inflation_adjusted_price_year', 'inflation_adjusted_price_month', 'sales_year', 'sales_quarter', 'sales_growth_year', 'sales_growth_quarter', 'real_sales_year', 'real_sales_quarter', 'real_sales_growth_year', 'real_sales_growth_quarter', 'price_to_sales_year', 'price_to_sales_quarter', 'price_to_book_value_year', 'price_to_book_value_quarter', 'book_value_year', 'book_value_quarter'] | The name of the series. Defaults to 'pe_month'. | pe_month | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SP500Multiples
        Serializable results.
    provider : Literal['nasdaq']
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
| date | date | The date of the data. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>


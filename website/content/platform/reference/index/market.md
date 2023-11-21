---
title: market
description: Learn how to retrieve historical market indices data using various data
  providers and query parameters. Understand the available parameters and return values,
  such as symbol, start date, end date, provider, interval, timeseries, timespan,
  sort order, limit, adjusted, multiplier, chart, metadata, date, open price, high
  price, low price, close price, volume, calls volume, puts volume, options volume,
  adjusted close price, unadjusted volume, change, change percent, label, change over
  time, and transactions.
keywords:
- Historical Market Indices
- market data
- symbol
- start date
- end date
- data provider
- query
- interval
- timeseries
- timespan
- sort order
- limit
- adjusted
- multiplier
- chart
- metadata
- date
- open price
- high price
- low price
- close price
- volume
- calls volume
- puts volume
- options volume
- adjusted close price
- unadjusted volume
- change
- change percent
- label
- change over time
- transactions
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Market Indices.

```python wordwrap
obb.index.market(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe', 'fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe', 'fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| interval | Literal['1m', '1d'] | Use interval, 1m, for intraday prices during the most recent trading period. | 1d | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe', 'fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| timeseries | int | Number of days to look back. | None | True |
| interval | Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'] | Data granularity. | 1day | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe', 'fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| timespan | Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'] | Timespan of the data. | day | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. | desc | True |
| limit | int | The number of data entries to return. | 49999 | True |
| adjusted | bool | Whether the data is adjusted. | True | True |
| multiplier | int | Multiplier of the timespan. | 1 | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe', 'fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| interval | Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'] | Data granularity. | 1d | True |
| period | Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'] | Time period of the data to return. | max | True |
| prepost | bool | Include Pre and Post market data. | True | True |
| rounding | bool | Round prices to two decimals? | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[MarketIndices]
        Serializable results.

    provider : Optional[Literal['cboe', 'fmp', 'polygon', 'yfinance']]
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
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| calls_volume | float | Number of calls traded during the most recent trading period. Only valid if interval is 1m. |
| puts_volume | float | Number of puts traded during the most recent trading period. Only valid if interval is 1m. |
| total_options_volume | float | Total number of options traded during the most recent trading period. Only valid if interval is 1m. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| adj_close | float | Adjusted Close Price of the symbol. |
| unadjusted_volume | float | Unadjusted volume of the symbol. |
| change | float | Change in the price of the symbol from the previous day. |
| change_percent | float | Change % in the price of the symbol. |
| label | str | Human readable format of the date. |
| change_over_time | float | Change % in the price of the symbol over a period of time. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| transactions | int | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>


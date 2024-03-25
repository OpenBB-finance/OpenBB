---
title: "historical"
description: "Learn how to use the `obb.equity.price.historical` function to load historical  price data for a specific stock ticker. Find out about the available parameters  and providers, as well as the structure of the returned data and the columns it  contains."
keywords:
- equity historical price
- load stock data
- specific ticker
- python function
- equity data parameters
- alpha vantage provider
- fmp provider
- intrinio provider
- polygon provider
- yfinance provider
- equity historical data returns
- equity data columns
- alpha vantage data columns
- cboe data columns
- fmp data columns
- intrinio data columns
- polygon data columns
- yfinance data columns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="currency/price/historical - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Currency Historical Price. Currency historical data.

Currency historical prices refer to the past exchange rates of one currency against
another over a specific period.
This data provides insight into the fluctuations and trends in the foreign exchange market,
helping analysts, traders, and economists understand currency performance,
evaluate economic health, and make predictions about future movements.


Examples
--------

```python
from openbb import obb
obb.currency.price.historical(symbol='EURUSD', provider='fmp')
# Filter historical data with specific start and end date.
obb.currency.price.historical(symbol='EURUSD', start_date='2023-01-01', end_date='2023-12-31', provider='fmp')
# Get data with different granularity.
obb.currency.price.historical(symbol='EURUSD', provider='polygon', interval=15m)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed for provider(s): fmp, polygon, tiingo, yfinance. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon', 'tiingo', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed for provider(s): fmp, polygon, tiingo, yfinance. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon', 'tiingo', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| interval | Literal['1m', '5m', '15m', '30m', '1h', '4h', '1d'] | Time interval of the data to return. | 1d | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed for provider(s): fmp, polygon, tiingo, yfinance. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon', 'tiingo', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| interval | str | Time interval of the data to return. The numeric portion of the interval can be any positive integer. The letter portion can be one of the following: s, m, h, d, W, M, Q, Y | 1d | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date. | asc | True |
| limit | int | The number of data entries to return. | 49999 | True |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed for provider(s): fmp, polygon, tiingo, yfinance. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon', 'tiingo', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| interval | Literal['1m', '5m', '15m', '30m', '1h', '4h', '1d'] | Time interval of the data to return. | 1d | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed for provider(s): fmp, polygon, tiingo, yfinance. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon', 'tiingo', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| interval | Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1W', '1M', '1Q'] | Time interval of the data to return. | 1d | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CurrencyHistorical
        Serializable results.
    provider : Literal['fmp', 'polygon', 'tiingo', 'yfinance']
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
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
| vwap | float, Gt(gt=0) | Volume Weighted Average Price over the period. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
| vwap | float, Gt(gt=0) | Volume Weighted Average Price over the period. |
| adj_close | float | The adjusted close price. |
| change | float | Change in the price from the previous close. |
| change_percent | float | Change in the price from the previous close, as a normalized percent. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
| vwap | float, Gt(gt=0) | Volume Weighted Average Price over the period. |
| transactions | int, Gt(gt=0) | Number of transactions for the symbol in the time period. |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
| vwap | float, Gt(gt=0) | Volume Weighted Average Price over the period. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
| vwap | float, Gt(gt=0) | Volume Weighted Average Price over the period. |
</TabItem>

</Tabs>


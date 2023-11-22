---
title: Equity Historical price
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
| `EquityHistorical` | `EquityHistoricalQueryParams` | `EquityHistoricalData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_historical import (
EquityHistoricalData,
EquityHistoricalQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| adjusted | bool | Output time series is adjusted by historical split and dividend events. | False | True |
| extended_hours | bool | Extended trading hours during pre-market and after-hours.Only available for intraday data. | False | True |
| month | str | Query a specific month in history (in YYYY-MM format). | None | True |
| output_size | Literal['compact', 'full'] | Compact returns only the latest 100 data points in the intraday time series; full returns trailing 30 days of the most recent intraday data if the month parameter is not specified, or the full intraday data for aspecific month in history if the month parameter is specified. | full | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| limit | int | Number of days to look back (Only for interval 1d). | None | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| start_time | datetime.time | Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. | None | True |
| end_time | datetime.time | Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. | None | True |
| timezone | str | Timezone of the data, in the IANA format (Continent/City). | UTC | True |
| source | Literal['realtime', 'delayed', 'nasdaq_basic'] | The source of the data. | realtime | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. | desc | True |
| limit | int | The number of data entries to return. | 49999 | True |
| adjusted | bool | Output time series is adjusted by historical split and dividend events. | True | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| prepost | bool | Include Pre and Post market data. | False | True |
| include | bool | Include Dividends and Stock Splits in results. | True | True |
| adjusted | bool | Adjust all OHLC data automatically. | False | True |
| back_adjust | bool | Attempt to adjust all the data automatically. | False | True |
| ignore_tz | bool | When combining from different timezones, ignore that part of datetime. | True | True |
</TabItem>

</Tabs>

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
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| adj_close | float | The adjusted close price. |
| dividend_amount | float | Dividend amount paid for the corresponding date. |
| split_coefficient | float | Split coefficient for the corresponding date. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
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
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| label | str | Human readable format of the date. |
| adj_close | float | Adjusted Close Price of the symbol. |
| unadjusted_volume | float | Unadjusted volume of the symbol. |
| change | float | Change in the price of the symbol from the previous day. |
| change_percent | float | Change % in the price of the symbol. |
| change_over_time | float | Change % in the price of the symbol over a period of time. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| close_time | datetime | The timestamp that represents the end of the interval span. |
| interval | str | The data time frequency. |
| average | float | Average trade price of an individual equity during the interval. |
| change | float | Change in the price of the symbol from the previous day. |
| intra_period | bool | If true, the equity price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period |
| adj_open | float | Adjusted open price during the period. |
| adj_high | float | Adjusted high price during the period. |
| adj_low | float | Adjusted low price during the period. |
| adj_close | float | Adjusted closing price during the period. |
| adj_volume | float | Adjusted volume during the period. |
| factor | float | factor by which to multiply equity prices before this date, in order to calculate historically-adjusted equity prices. |
| split_ratio | float | Ratio of the equity split, if a equity split occurred. |
| dividend | float | Dividend amount, if a dividend was paid. |
| percent_change | float | Percent change in the price of the symbol from the previous day. |
| fifty_two_week_high | float | 52 week high price for the symbol. |
| fifty_two_week_low | float | 52 week low price for the symbol. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| transactions | int | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>

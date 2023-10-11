---
title: Major Indices Historical
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `MajorIndicesHistorical` | `MajorIndicesHistoricalQueryParams` | `MajorIndicesHistoricalData` |

### Import Statement

```python
from openbb_provider.standard_models.major_indices_historical import (
MajorIndicesHistoricalData,
MajorIndicesHistoricalQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Union[Literal['cboe', 'fmp', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Union[Literal['cboe', 'fmp', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| interval | Union[Literal['1d', '1m']] | Use interval, 1m, for intraday prices during the most recent trading period. | 1d | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Union[Literal['cboe', 'fmp', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| timeseries | Union[typing_extensions.Annotated[int, Ge(ge=0)]] | Number of days to look back. | None | True |
| interval | Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'] | Data granularity. | 1day | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Union[Literal['cboe', 'fmp', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
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
| provider | Union[Literal['cboe', 'fmp', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| interval | Union[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']] | Data granularity. | 1d | True |
| period | Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']] | Period of the data to return. | max | True |
| prepost | bool | Include Pre and Post market data. | True | True |
| rounding | bool | Round prices to two decimals? | True | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | The volume of the symbol. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | The volume of the symbol. |
| calls_volume | Union[float] | Number of calls traded during the most recent trading period. Only valid if interval is 1m. |
| puts_volume | Union[float] | Number of puts traded during the most recent trading period. Only valid if interval is 1m. |
| total_options_volume | Union[float] | Total number of options traded during the most recent trading period. Only valid if interval is 1m. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | The volume of the symbol. |
| adj_close | Union[float] | Adjusted Close Price of the symbol. |
| unadjusted_volume | Union[float] | Unadjusted volume of the symbol. |
| change | Union[float] | Change in the price of the symbol from the previous day. |
| change_percent | Union[float] | Change % in the price of the symbol. |
| label | Union[str] | Human readable format of the date. |
| change_over_time | Union[float] | Change % in the price of the symbol over a period of time. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | The volume of the symbol. |
| transactions | Union[typing_extensions.Annotated[int, Gt(gt=0)]] | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>


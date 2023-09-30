---
title: load
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# load

Crypto Historical Price.

```python wordwrap
load(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
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
| provider | Literal['fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| timeseries | NonNegativeInt | Number of days to look back. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| timespan | Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'] | Timespan of the data. | day | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. | desc | True |
| limit | PositiveInt | The number of data entries to return. | 49999 | True |
| adjusted | bool | Whether the data is adjusted. | True | True |
| multiplier | PositiveInt | Multiplier of the timespan. | 1 | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'] | Data granularity. | 1d | True |
| period | Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'] | Period of the data to return. | None | True |
| prepost | bool | Include Pre and Post market data. | False | True |
| adjust | bool | Adjust all the data automatically. | True | True |
| back_adjust | bool | Back-adjusted data to mimic true historical prices. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CryptoHistorical]
        Serializable results.

    provider : Optional[Literal['fmp', 'polygon', 'yfinance']]
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
| open | PositiveFloat | The open price of the symbol. |
| high | PositiveFloat | The high price of the symbol. |
| low | PositiveFloat | The low price of the symbol. |
| close | PositiveFloat | The close price of the symbol. |
| volume | PositiveFloat | The volume of the symbol. |
| vwap | PositiveFloat | Volume Weighted Average Price of the symbol. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| adjClose | float | Adjusted Close Price of the symbol. |
| unadjustedVolume | float | Unadjusted volume of the symbol. |
| change | float | Change in the price of the symbol from the previous day. |
| changePercent | float | Change \% in the price of the symbol. |
| label | str | Human readable format of the date. |
| changeOverTime | float | Change \% in the price of the symbol over a period of time. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| n | PositiveInt | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>


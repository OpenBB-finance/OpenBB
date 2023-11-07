---
title: Forex Historical Price
description: This documentation presents implementation details and usage of Forex
  Historical Data and Query Parameters class in Python. It provides an overview of
  parameters and data attributes used for Forex Historical queries. The guide includes
  specifics as per different providers such as Standard, FMP, and Polygon.
keywords:
- Forex Historical Data
- Python
- Forex Historical Query Parameters
- Data Class and Model
- Implementation Details
- Parameters
- Data
- Standard Models
- FMP
- Polygon
- Openbb Provider
- Symbol Pair
- Start date
- End date
- Provider
- Interval
- Multiplier
- Timespan
- Sort order
- Data Entries
- Adjusted Data
- Date
- Open Price
- High Price
- Low Price
- Close Price
- Volume
- VWAP
- Transactions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Forex Historical Price - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `ForexHistorical` | `ForexHistoricalQueryParams` | `ForexHistoricalData` |

### Import Statement

```python
from openbb_provider.standard_models.forex_historical import (
ForexHistoricalData,
ForexHistoricalQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol Pair to get data for in CURR1-CURR2 or CURR1CURR2 format. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol Pair to get data for in CURR1-CURR2 or CURR1CURR2 format. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| interval | Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'] | Data granularity. | 1day | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol Pair to get data for in CURR1-CURR2 or CURR1CURR2 format. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| multiplier | int | Multiplier of the timespan. | 1 | True |
| timespan | Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'] | Timespan of the data. | day | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. | desc | True |
| limit | int | The number of data entries to return. | 49999 | True |
| adjusted | bool | Whether the data is adjusted. | True | True |
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
| volume | float | The volume of the symbol. |
| vwap | float | Volume Weighted Average Price of the symbol. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | float | The volume of the symbol. |
| vwap | float | Volume Weighted Average Price of the symbol. |
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
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | float | The volume of the symbol. |
| vwap | float | Volume Weighted Average Price of the symbol. |
| transactions | int | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>

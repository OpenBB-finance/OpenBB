---
title: load
description: Learn how to load and retrieve historical futures price and data using
  the 'load' function. Understand the parameters, providers, and data structure. Explore
  the returns, chart, and metadata included in the fetched data.
keywords:
- futures historical price
- futures historical data
- load futures data
- get futures data
- futures data parameters
- futures data provider
- futures data interval
- futures data period
- futures data prepost
- futures data adjust
- futures data back-adjust
- futures data returns
- futures data chart
- futures data metadata
- futures data date
- futures data open price
- futures data high price
- futures data low price
- futures data close price
- futures data volume
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Futures Historical Price. Futures historical data.

```python wordwrap
obb.futures.load(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, expiration: str = None, provider: Literal[str] = yfinance)
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
| expiration | str | Future expiry date with format YYYY-MM | None | True |
| provider | Literal['yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'yfinance' if there is no default. | yfinance | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| expiration | str | Future expiry date with format YYYY-MM | None | True |
| provider | Literal['yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'yfinance' if there is no default. | yfinance | True |
| interval | Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'] | Data granularity. | 1d | True |
| period | Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'] | Time period of the data to return. | None | True |
| prepost | bool | Include Pre and Post market data. | False | True |
| adjust | bool | Adjust all the data automatically. | True | True |
| back_adjust | bool | Back-adjusted data to mimic true historical prices. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FuturesHistorical]
        Serializable results.

    provider : Optional[Literal['yfinance']]
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
| volume | float | The trading volume. |
</TabItem>

</Tabs>


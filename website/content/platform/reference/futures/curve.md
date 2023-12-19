---
title: curve
description: Learn about fetching historical futures price data using Python and an
  API. Understand the available parameters, such as symbol, date, and provider. Explore
  the returned results, including FuturesCurve, warnings, chart, and metadata. Analyze
  the data, including expiration, close price, and trading symbol.
keywords:
- futures historical price
- futures historical data
- Python
- API
- symbol
- date
- provider
- cboe
- yfinance
- results
- FuturesCurve
- warnings
- Chart
- Metadata
- expiration
- close price
- trading symbol
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Futures Historical Price. Futures historical data.

```python wordwrap
obb.futures.curve(symbol: Union[str, List[str]], date: date = None, provider: Literal[str] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| date | date | A specific date to get data for. | None | True |
| provider | Literal['cboe', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FuturesCurve]
        Serializable results.

    provider : Optional[Literal['cboe', 'yfinance']]
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
| expiration | str | Futures expiration month. |
| price | float | The close price. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| expiration | str | Futures expiration month. |
| price | float | The close price. |
| symbol | str | The trading symbol for the tenor of future. |
</TabItem>

</Tabs>


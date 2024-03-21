---
title: "curve"
description: "Learn about fetching historical futures price data using Python and an  API. Understand the available parameters, such as symbol, date, and provider. Explore  the returned results, including FuturesCurve, warnings, chart, and metadata. Analyze  the data, including expiration, close price, and trading symbol."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="derivatives/futures/curve - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Futures Term Structure, current or historical.


Examples
--------

```python
from openbb import obb
obb.derivatives.futures.curve(symbol='VX', provider='cboe')
# Enter a date to get the term structure from a historical date.
obb.derivatives.futures.curve(symbol='NG', provider='yfinance', date='2023-01-01')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| date | Union[date, str] | A specific date to get data for. | None | True |
| provider | Literal['cboe', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| date | Union[date, str] | A specific date to get data for. | None | True |
| provider | Literal['cboe', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| date | Union[date, str] | A specific date to get data for. | None | True |
| provider | Literal['cboe', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : FuturesCurve
        Serializable results.
    provider : Literal['cboe', 'yfinance']
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

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| expiration | str | Futures expiration month. |
| price | float | The close price. |
</TabItem>

</Tabs>


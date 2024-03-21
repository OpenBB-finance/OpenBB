---
title: "trailing_dividend_yield"
description: "Trailing 1yr dividend yield"
keywords:
- equity
- fundamental
- trailing_dividend_yield
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/trailing_dividend_yield - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the 1 year trailing dividend yield for a given company over time.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.trailing_dividend_yield(symbol='AAPL', provider='tiingo')
obb.equity.fundamental.trailing_dividend_yield(symbol='AAPL', limit=252, provider='tiingo')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. Default is 252, the number of trading days in a year. | 252 | True |
| provider | Literal['tiingo'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tiingo' if there is no default. | tiingo | True |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. Default is 252, the number of trading days in a year. | 252 | True |
| provider | Literal['tiingo'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tiingo' if there is no default. | tiingo | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : TrailingDividendYield
        Serializable results.
    provider : Literal['tiingo']
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
| trailing_dividend_yield | float | Trailing dividend yield. |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| trailing_dividend_yield | float | Trailing dividend yield. |
</TabItem>

</Tabs>


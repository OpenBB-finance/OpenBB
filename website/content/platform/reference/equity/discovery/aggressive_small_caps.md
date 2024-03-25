---
title: "aggressive_small_caps"
description: "Learn how to get aggressive small cap equities with the equity discovery  API. Understand the parameters, returns, and data format."
keywords:
- equities
- aggressive small caps
- equity discovery
- parameter
- sort order
- provider
- returns
- data
- symbol
- name
- price
- change
- percent change
- volume
- market cap
- average volume
- PE ratio
- documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/discovery/aggressive_small_caps - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get top small cap stocks based on earnings growth.


Examples
--------

```python
from openbb import obb
obb.equity.discovery.aggressive_small_caps(provider='yfinance')
obb.equity.discovery.aggressive_small_caps(sort='desc', provider='yfinance')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | Literal['asc', 'desc'] | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| provider | Literal['yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'yfinance' if there is no default. | yfinance | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | Literal['asc', 'desc'] | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| provider | Literal['yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'yfinance' if there is no default. | yfinance | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EquityAggressiveSmallCaps
        Serializable results.
    provider : Literal['yfinance']
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
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| price | float | Last price. |
| change | float | Change in price value. |
| percent_change | float | Percent change. |
| volume | float | The trading volume. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| price | float | Last price. |
| change | float | Change in price value. |
| percent_change | float | Percent change. |
| volume | float | The trading volume. |
| market_cap | float | Market Cap. |
| avg_volume_3_months | float | Average volume over the last 3 months in millions. |
| pe_ratio_ttm | float | PE Ratio (TTM). |
</TabItem>

</Tabs>


---
title: "gainers"
description: "Learn how to get the top ETF gainers using Python code. This documentation  includes details about the parameters, return values, and data format."
keywords:
- ETF gainers
- ETFGainers
- Python code
- parameters
- sort order
- limit
- provider
- returns
- results
- warnings
- chart
- metadata
- data
- symbol
- name
- last price
- percent change
- net change
- trading volume
- date
- bluegrass channel
- country
- mantissa
- type
- formatted price
- formatted volume
- formatted price change
- formatted percent change
- url
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/discovery/gainers - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the top price gainers in the stock market.


Examples
--------

```python
from openbb import obb
obb.equity.discovery.gainers(provider='yfinance')
obb.equity.discovery.gainers(sort='desc', provider='yfinance')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | Literal['asc', 'desc'] | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| provider | Literal['tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | Literal['asc', 'desc'] | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| provider | Literal['tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
| category | Literal['dividend', 'energy', 'healthcare', 'industrials', 'price_performer', 'rising_stars', 'real_estate', 'tech', 'utilities', '52w_high', 'volume'] | The category of list to retrieve. Defaults to `price_performer`. | price_performer | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | Literal['asc', 'desc'] | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| provider | Literal['tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EquityGainers
        Serializable results.
    provider : Literal['tmx', 'yfinance']
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

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| price | float | Last price. |
| change | float | Change in price value. |
| percent_change | float | Percent change. |
| volume | float | The trading volume. |
| rank | int | The rank of the stock in the list. |
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


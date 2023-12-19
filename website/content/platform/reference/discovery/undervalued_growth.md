---
title: undervalued_growth
description: Learn how to get undervalued growth equities using the equity discovery
  feature, and understand the various parameters, returns, and data available in the
  results.
keywords:
- undervalued growth equities
- equity discovery
- sort order
- provider
- results
- warnings
- chart
- metadata
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
- TTM
- trading volume
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get undervalued growth Equities.

```python wordwrap
obb.equity.discovery.undervalued_growth(sort: str = desc, provider: Literal[str] = yfinance)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | str | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| provider | Literal['yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'yfinance' if there is no default. | yfinance | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquityUndervaluedGrowth]
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
| market_cap | str | Market Cap. |
| avg_volume_3_months | float | Average volume over the last 3 months in millions. |
| pe_ratio_ttm | float | PE Ratio (TTM). |
</TabItem>

</Tabs>


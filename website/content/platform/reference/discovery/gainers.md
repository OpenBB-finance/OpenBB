---
title: gainers
description: Learn how to get the top ETF gainers using Python code. This documentation
  includes details about the parameters, return values, and data format.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the top ETF gainers.

```python wordwrap
obb.etf.discovery.gainers(sort: str = desc, limit: int = 10, provider: Literal[str] = wsj)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | str | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| limit | int | The number of data entries to return. | 10 | True |
| provider | Literal['wsj'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'wsj' if there is no default. | wsj | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ETFGainers]
        Serializable results.

    provider : Optional[Literal['wsj']]
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
| last_price | float | Last price. |
| percent_change | float | Percent change. |
| net_change | float | Net change. |
| volume | float | The trading volume. |
| date | date | The date of the data. |
</TabItem>

<TabItem value='wsj' label='wsj'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| last_price | float | Last price. |
| percent_change | float | Percent change. |
| net_change | float | Net change. |
| volume | float | The trading volume. |
| date | date | The date of the data. |
| bluegrass_channel | str | Bluegrass channel. |
| country | str | Country of the entity. |
| mantissa | int | Mantissa. |
| type | str | Type of the entity. |
| formatted_price | str | Formatted price. |
| formatted_volume | str | Formatted volume. |
| formatted_price_change | str | Formatted price change. |
| formatted_percent_change | str | Formatted percent change. |
| url | str | The source url. |
</TabItem>

</Tabs>


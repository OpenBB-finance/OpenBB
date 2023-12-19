---
title: active
description: Learn how to get the most active ETFs using the ETF discovery API. This
  page provides documentation for the parameters, returns, and data associated with
  the API endpoint. Understand how to use the sorting, limiting, and provider parameters
  and explore the returned results, chart object, and metadata. Find details about
  the data fields including symbol, name, last price, percent change, net change,
  volume, date, country, mantissa, type, and formatted values. Retrieve the source
  url for additional information.
keywords:
- ETFs
- most active ETFs
- ETF discovery
- sort order
- limit parameter
- provider parameter
- results
- chart object
- metadata
- symbol
- name
- last price
- percent change
- net change
- volume
- date
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

Get the most active ETFs.

```python wordwrap
obb.etf.discovery.active(sort: str = desc, limit: int = 10, provider: Literal[str] = wsj)
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
    results : List[ETFActive]
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


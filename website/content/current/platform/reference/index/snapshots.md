---
title: snapshots
description: Index Snapshots documentation page with information on current levels
  for all indices from a specific provider, and details on parameters, query, returns,
  and data.
keywords:
- index snapshots
- current levels
- provider
- parameters
- region
- query
- returns
- data
- symbol
- name
- currency
- price
- open
- high
- low
- close
- prev close
- change
- change percent
- isin code
- last trade timestamp
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Index Snapshots. Current levels for all indices from a provider.

```python wordwrap
obb.index.snapshots(region: Literal[str] = US, provider: Literal[str] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| region | Literal['US', 'EU'] | The region to return. Currently supports US and EU. | US | True |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[IndexSnapshots]
        Serializable results.

    provider : Optional[Literal['cboe']]
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
| name | str | Name of the index. |
| currency | str | Currency of the index. |
| price | float | Current price of the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| prev_close | float | Previous closing price of the index. |
| change | float | Change of the index. |
| change_percent | float | Change percent of the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the index. |
| currency | str | Currency of the index. |
| price | float | Current price of the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| prev_close | float | Previous closing price of the index. |
| change | float | Change of the index. |
| change_percent | float | Change percent of the index. |
| isin | str | ISIN code for the index. Valid only for European indices. |
| last_trade_timestamp | datetime | Last trade timestamp for the index. |
</TabItem>

</Tabs>


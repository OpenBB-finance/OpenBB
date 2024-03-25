---
title: "holdings_date"
description: "Learn how to retrieve the holdings filing date for an individual ETF  using the OBB.etf.holdings_date API. Explore the available parameters, such as symbol  and provider, and understand the returned results like results list, chart object,  and metadata info."
keywords:
- ETF holdings filing date
- get ETF holdings filing date
- ETF holdings date API
- symbol parameter
- provider parameter
- fmp provider
- cik parameter
- returns
- results
- warnings
- chart object
- metadata info
- data parameter
- date field
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/holdings_date - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Use this function to get the holdings dates, if available.


Examples
--------

```python
from openbb import obb
obb.etf.holdings_date(symbol='XLK', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| cik | str | The CIK of the filing entity. Overrides symbol. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EtfHoldingsDate
        Serializable results.
    provider : Literal['fmp']
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
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>


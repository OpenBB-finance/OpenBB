---
title: "transcript"
description: "Learn how to retrieve earnings call transcripts for a given company using  Python obb.equity.fundamental.transcript. Understand the data parameters, returns,  symbol, year, quarter, and metadata associated with the transcripts."
keywords:
- earnings call transcript
- python obb.equity.fundamental.transcript
- data parameters
- returns
- symbols
- year
- quar
- content
- metadata
- provider
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/transcript - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get earnings call transcripts for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.transcript(symbol='AAPL', year=2020, provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| year | int | Year of the earnings call transcript. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| year | int | Year of the earnings call transcript. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EarningsCallTranscript
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
| symbol | str | Symbol representing the entity requested in the data. |
| quarter | int | Quarter of the earnings call transcript. |
| year | int | Year of the earnings call transcript. |
| date | datetime | The date of the data. |
| content | str | Content of the earnings call transcript. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| quarter | int | Quarter of the earnings call transcript. |
| year | int | Year of the earnings call transcript. |
| date | datetime | The date of the data. |
| content | str | Content of the earnings call transcript. |
</TabItem>

</Tabs>


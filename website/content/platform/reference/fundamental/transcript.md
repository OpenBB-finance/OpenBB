---
title: transcript
description: Learn how to retrieve earnings call transcripts for a given company using
  Python obb.equity.fundamental.transcript. Understand the data parameters, returns,
  symbol, year, quarter, and metadata associated with the transcripts.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Earnings Call Transcript. Earnings call transcript for a given company.

```python wordwrap
obb.equity.fundamental.transcript(symbol: Union[str, List[str]], year: int, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| year | int | Year of the earnings call transcript. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EarningsCallTranscript]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| quarter | int | Quarter of the earnings call transcript. |
| year | int | Year of the earnings call transcript. |
| date | datetime | The date of the data. |
| content | str | Content of the earnings call transcript. |
</TabItem>

</Tabs>


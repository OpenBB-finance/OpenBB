---
title: revseg
description: Metadata for revseg page - a revenue business line data page. Describes
  parameters like symbol, period, structure and provider for data querying. Also provides
  info on returned data.
keywords:
- revseg
- revenue business line data
- business line revenue
- data query
- parameters
- symbol
- period
- structure
- provider
- returned data
- warnings
- metadata
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="revseg - Fa - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# revseg

Revenue Business Line. Business line revenue data.

```python wordwrap
revseg(symbol: Union[str, List[str]], period: Literal[str] = annual, structure: Literal[str] = flat, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Period of the data to return. | annual | True |
| structure | Literal['hierarchical', 'flat'] | Structure of the returned data. | flat | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[RevenueBusinessLine]
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
| date | date | The date of the data. |
| business_line | Dict[str, int] | Day level data containing the revenue of the business line. |
</TabItem>

</Tabs>

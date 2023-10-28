---
title: revgeo
description: The revgeo page provides information about the Revenue Geographic, a
  function that returns geographic revenue data. Parameters, returns and data structure
  are covered in details.
keywords:
- revgeo
- Revenue Geographic
- geographic revenue data
- data query
- Docusaurus documentation
- provider
- period
- structure
- symbol
- geographic segment
- Revenue from the America
- Revenue from Europe
- Revenue from Greater China
- Revenue from Japan
- Revenue from Rest of Asia Pacific
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.revgeo - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# revgeo

Revenue Geographic. Geographic revenue data.

```python wordwrap
revgeo(symbol: Union[str, List[str]], period: Literal[str] = annual, structure: Literal[str] = flat, provider: Literal[str] = fmp)
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
    results : List[RevenueGeographic]
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
| geographic_segment | Dict[str, int] | Day level data containing the revenue of the geographic segment. |
| americas | int | Revenue from the the American segment. |
| europe | int | Revenue from the the European segment. |
| greater_china | int | Revenue from the the Greater China segment. |
| japan | int | Revenue from the the Japan segment. |
| rest_of_asia_pacific | int | Revenue from the the Rest of Asia Pacific segment. |
</TabItem>

</Tabs>

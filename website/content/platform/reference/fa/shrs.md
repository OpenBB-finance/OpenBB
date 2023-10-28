---
title: shrs
description: This page provides detailed information about the 'shrs' functionality.
  It allows users to share statistics of a specific company utilizing specified parameters.
  It also details the process of fetching and interpreting data, understanding parameters
  such as symbols, data, and share types.
keywords:
- shrs
- share Statistics
- symbol
- Macroaxis
- OBBject
- Chart object
- Metadata
- Data
- free_float
- float_shares
- outstanding_shares
- source
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.shrs - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# shrs

Share Statistics. Share statistics for a given company.

```python wordwrap
shrs(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ShareStatistics]
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
| symbol | str | Symbol to get data for. |
| date | date | A specific date to get data for. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
</TabItem>

</Tabs>

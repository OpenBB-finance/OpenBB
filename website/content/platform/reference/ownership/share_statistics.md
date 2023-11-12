---
title: share_statistics
description: Learn how to retrieve and analyze share statistics for a given company
  using the obb.equity.ownership.share_statistics API endpoint. This documentation
  provides details on the parameters, return values, and data structure.
keywords:
- share statistics
- company statistics
- equity ownership
- symbol
- provider
- data
- free float
- float shares
- outstanding shares
- source
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Share Statistics. Share statistics for a given company.

```python wordwrap
obb.equity.ownership.share_statistics(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
</TabItem>

</Tabs>


---
title: shrs
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# shrs

Share Statistics.

```python wordwrap
shrs(symbol: Union[str, List[str]], provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ShareStatistics]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fmp'], NoneType]]
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
| date | Union[date] | A specific date to get data for. |
| free_float | Union[float] | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | Union[float] | Number of shares available for trading by the general public. |
| outstanding_shares | Union[float] | Total number of shares of a publicly-traded company. |
| source | Union[str] | Source of the received data. |
</TabItem>

</Tabs>


---
title: ycrv
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ycrv

Get United States yield curve.

```python wordwrap
ycrv(date: Union[date] = None, inflation_adjusted: Union[bool] = False, provider: Union[Literal[str]] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date] | Date to get Yield Curve data.  Defaults to the most recent FRED entry. | None | True |
| inflation_adjusted | Union[bool] | Get inflation adjusted rates. | False | True |
| provider | Union[Literal['fred']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[USYieldCurve]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fred'], NoneType]]
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
| maturity | float | Maturity of the treasury rate in years. |
| rate | float | Associated rate given in decimal form (0.05 is 5%) |
</TabItem>

</Tabs>


---
title: tmc_effr
description: Learn how to select Treasury Constant Maturity and access data for it
  using the obb.fixedincome.spreads.tmc_effr function. Understand constant maturity,
  Treasury yield curve, bid-yields, and Treasury securities. Explore the parameters
  and data returned by the function.
keywords:
- Treasury Constant Maturity
- data for Treasury Constant Maturity
- constant maturity
- U.S. Treasury
- Treasury yield curve
- yield curve interpolation
- bid-yields
- Treasury securities
- obb.fixedincome.spreads.tmc_effr
- start_date
- end_date
- maturity
- provider
- results
- warnings
- chart
- metadata
- date
- rate
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Select Treasury Constant Maturity.

Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate
Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

```python wordwrap
obb.fixedincome.spreads.tmc_effr(start_date: Union[date, str] = None, end_date: Union[date, str] = None, maturity: Literal[str] = 10y, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Literal['10y', '5y', '1y', '6m', '3m'] | The maturity | 10y | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[SelectedTreasuryConstantMaturity]
        Serializable results.

    provider : Optional[Literal['fred']]
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
| rate | float | Selected Treasury Constant Maturity Rate. |
</TabItem>

</Tabs>


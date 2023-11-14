---
title: tmc
description: Learn about Treasury Constant Maturity and how to get data for it. Understand
  constant maturity calculation and the use of Treasury yield curve and Treasury securities.
  Explore parameters like start date, end date, maturity, and provider. Get a list
  of results, warnings, and metadata along with a chart depicting the Treasury Constant
  Maturity rate.
keywords:
- Treasury Constant Maturity
- data
- U.S. Treasury
- yield curve
- Treasury securities
- start date
- end date
- maturity
- provider
- results
- warnings
- chart
- metadata
- rate
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Treasury Constant Maturity.

Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.
Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

```python wordwrap
obb.fixedincome.spreads.tmc(start_date: Union[date, str] = None, end_date: Union[date, str] = None, maturity: Literal[str] = 3m, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Literal['3m', '2y'] | The maturity | 3m | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[TreasuryConstantMaturity]
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
| rate | float | TreasuryConstantMaturity Rate. |
</TabItem>

</Tabs>


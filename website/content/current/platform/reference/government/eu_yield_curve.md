---
title: eu_yield_curve
description: Learn about the Euro Area Yield Curve, its definition, and how to access
  ECB yield curve data. Understand the factors influencing yield curve shape and rate
  expectations. Explore parameters, types, and providers for yield curve data, as
  well as the returned results, chart object, and metadata.
keywords:
- Euro Area Yield Curve
- ECB yield curve data
- yield curve definition
- bond yield curve
- Treasury market
- credit quality
- yield curve shape
- rate expectations
- pure expectations hypothesis
- bond pricing
- debt market
- yield curve parameters
- yield curve types
- yield curve provider
- yield curve data
- yield curve ratings
- OBBject
- EUYieldCurve
- results
- chart
- metadata
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Euro Area Yield Curve.

Gets euro area yield curve data from ECB.

The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
and setting yields in other sectors of the debt market.

It is clear that the market’s expectations of future rate changes are one important determinant of the
yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
activity of risk-neutral traders removes all expected return differentials across bonds.

```python wordwrap
obb.fixedincome.government.eu_yield_curve(date: date = None, yield_curve_type: Literal[str] = spot_rate, provider: Literal[str] = ecb)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | date | A specific date to get data for. | None | True |
| yield_curve_type | Literal['spot_rate', 'instantaneous_forward', 'par_yield'] | The yield curve type. | spot_rate | True |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | date | A specific date to get data for. | None | True |
| yield_curve_type | Literal['spot_rate', 'instantaneous_forward', 'par_yield'] | The yield curve type. | spot_rate | True |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
| rating | Literal['A', 'C'] | The rating type. | A | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EUYieldCurve]
        Serializable results.

    provider : Optional[Literal['ecb']]
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
| maturity | str | Yield curve rate maturity. |
| rate | float | Yield curve rate. |
</TabItem>

</Tabs>


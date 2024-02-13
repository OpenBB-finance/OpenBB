---
title: ecbycrv
description: Generate euro area yield curve from ECB
keywords:
- fixedincome
- ecbycrv
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /ecbycrv - Reference | OpenBB Terminal Docs" />

Generate euro area yield curve from ECB. The yield curve shows the bond ratesat different maturities. The graphic depiction of the relationship between the yield on bonds of the same credit quality but different maturities is known as the yield curve. In the past, most market participants have constructed yield curves from the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First, Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds and setting yields in other sectors of the debt market. It is clear that the market’s expectations of future rate changes are one important determinant of the yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking activity of risk-neutral traders removes all expected return differentials across bonds.

### Usage

```python wordwrap
ecbycrv [-d DATE] [-p {spot_rate,instantaneous_forward,par_yield}] [--detailed] [--any-rating]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| date | -d  --date | Date to get data from ECB. If not supplied, the most recent entry will be used. | None | True | None |
| parameter | -p  --parameter | Selected type of yield curve | spot_rate | True | spot_rate, instantaneous_forward, par_yield |
| detailed | --detailed | If True, returns detailed data. Note that this is very slow. | False | True | None |
| any_rating | --any-rating | If False, it only returns rates for AAA rated bonds. If True, it returns rates for all bonds. | False | True | None |

---

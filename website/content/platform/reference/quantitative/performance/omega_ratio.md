---
title: "omega_ratio"
description: "Calculate the Omega Ratio"
keywords:
- quantitative
- performance
- omega_ratio
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/performance/omega_ratio - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Omega Ratio.

 The Omega Ratio is a sophisticated metric that goes beyond traditional performance measures by considering the
 probability of achieving returns above a given threshold. It offers a more nuanced view of risk and reward,
 focusing on the likelihood of success rather than just average outcomes.


Examples
--------

```python
from openbb import obb
# Get Omega Ratio.
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
returns = stock_data["close"].pct_change().dropna()
obb.quantitative.performance.omega_ratio(data=returns, target="close")
obb.quantitative.performance.omega_ratio(target='close', data=[{'date': '2023-01-02', 'close': 0.05}, {'date': '2023-01-03', 'close': 0.08}, {'date': '2023-01-04', 'close': 0.07}, {'date': '2023-01-05', 'close': 0.06}, {'date': '2023-01-06', 'close': 0.06}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. |  | False |
| target | str | Target column name. |  | False |
| threshold_start | float, optional | Start threshold, by default 0.0 |  | False |
| threshold_end | float, optional | End threshold, by default 1.5 |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[OmegaModel]
        Omega ratios.
```


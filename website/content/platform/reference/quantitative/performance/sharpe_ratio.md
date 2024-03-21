---
title: "sharpe_ratio"
description: "Get Rolling Sharpe Ratio"
keywords:
- quantitative
- performance
- sharpe_ratio
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/performance/sharpe_ratio - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Rolling Sharpe Ratio.

 This function calculates the Sharpe Ratio, a metric used to assess the return of an investment compared to its risk.
 By factoring in the risk-free rate, it helps you understand how much extra return you're getting for the extra
 volatility that you endure by holding a riskier asset. The Sharpe Ratio is essential for investors looking to
 compare the efficiency of different investments, providing a clear picture of potential rewards in relation to their
 risks over a specified period. Ideal for gauging the effectiveness of investment strategies, it offers insights into
 optimizing your portfolio for maximum return on risk.


Examples
--------

```python
from openbb import obb
# Get Rolling Sharpe Ratio.
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
returns = stock_data["close"].pct_change().dropna()
obb.quantitative.performance.sharpe_ratio(data=returns, target="close")
obb.quantitative.performance.sharpe_ratio(target='close', window=2, data=[{'date': '2023-01-02', 'close': 0.05}, {'date': '2023-01-03', 'close': 0.08}, {'date': '2023-01-04', 'close': 0.07}, {'date': '2023-01-05', 'close': 0.06}, {'date': '2023-01-06', 'close': 0.06}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. |  | False |
| target | str | Target column name. |  | False |
| rfr | float, optional | Risk-free rate, by default 0.0 |  | False |
| window | PositiveInt, optional | Window size, by default 252 |  | False |
| index | str, optional | Returns |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        Sharpe ratio.
```


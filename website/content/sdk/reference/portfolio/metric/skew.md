---
title: skew
description: Understand how to calculate portfolio and benchmark skewness with the
  OpenBBTerminal. Explore source code examples demonstrating how to harness Python
  for financial metric calculations.
keywords:
- portfolio skewness
- benchmark skewness
- OpenBB finance
- financial metrics
- portfolio metrics
- Python financial analysis
- skew function
- OpenBBTerminal examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.skew - Reference | OpenBB SDK Docs" />

Get skewness for portfolio and benchmark selected

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L987)]

```python
openbb.portfolio.metric.skew(portfolio_engine: portfolio_engine.PortfolioEngine)
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with skewness for portfolio and benchmark for different periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.skew(p)
```

---

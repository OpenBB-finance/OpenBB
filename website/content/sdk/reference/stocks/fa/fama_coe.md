---
title: fama_coe
description: Learn how to use Fama and French to determine the cost of equity for
  a company with our Fama_Coe tool. Find the Python source code and understand its
  parameters and returns.
keywords:
- Fama and French
- cost of equity
- company financial analysis
- Python source code
- Fama_Coe tool
- OpenBB stocks
- ticker symbol analysis
- stock's Fama French coefficient
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.fama_coe - Reference | OpenBB SDK Docs" />

Use Fama and French to get the cost of equity for a company

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/dcf_model.py#L300)]

```python
openbb.stocks.fa.fama_coe(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to be analyzed | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| float | The stock's Fama French coefficient |
---

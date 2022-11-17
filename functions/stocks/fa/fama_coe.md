---
title: fama_coe
description: OpenBB SDK Function
---

# fama_coe

## stocks_fa_dcf_model.get_fama_coe

```python title='openbb_terminal/stocks/fundamental_analysis/dcf_model.py'
def get_fama_coe(symbol: str) -> float:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/dcf_model.py#L300)

Description: Use Fama and French to get the cost of equity for a company

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to be analyzed | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| float | The stock's Fama French coefficient |

## Examples


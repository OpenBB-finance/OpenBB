---
title: fraud
description: OpenBB SDK Function
---

# fraud

## stocks_fa_av_model.get_fraud_ratios

```python title='openbb_terminal/stocks/fundamental_analysis/av_model.py'
def get_fraud_ratios(symbol: str, detail: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L594)

Description: Get fraud ratios based on fundamentals

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| detail | bool | Whether to provide extra m-score details | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The fraud ratios |

## Examples


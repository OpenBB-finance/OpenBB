---
title: historical_5
description: OpenBB SDK Function
---

# historical_5

## stocks_qa_factors_model.get_historical_5

```python title='openbb_terminal/stocks/quantitative_analysis/factors_model.py'
def get_historical_5(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/quantitative_analysis/factors_model.py#L58)

Description: Get 5 year monthly historical performance for a ticker with dividends filtered

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | A ticker symbol in string form | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe with historical information |

## Examples


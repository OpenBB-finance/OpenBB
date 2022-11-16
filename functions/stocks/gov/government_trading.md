---
title: government_trading
description: OpenBB SDK Function
---

# government_trading

## stocks_gov_quiverquant_model.get_government_trading

```python title='openbb_terminal/stocks/government/quiverquant_model.py'
def get_government_trading(gov_type: str, symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L25)

Description: Returns the most recent transactions by members of government

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| gov_type | str | Type of government data between:
'congress', 'senate', 'house', 'contracts', 'quarter-contracts' and 'corporate-lobbying' | None | False |
| symbol | str | Ticker symbol to get congress trading data from | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most recent transactions by members of U.S. Congress |

## Examples


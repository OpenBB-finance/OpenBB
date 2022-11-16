---
title: mgmt
description: OpenBB SDK Function
---

# mgmt

## stocks_fa_business_insider_model.get_management

```python title='openbb_terminal/stocks/fundamental_analysis/business_insider_model.py'
def get_management(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/business_insider_model.py#L19)

Description: Get company managers from Business Insider

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of managers |

## Examples


---
title: similar_dfs
description: OpenBB SDK Function
---

# similar_dfs

## stocks_fa_dcf_model.get_similar_dfs

```python title='openbb_terminal/stocks/fundamental_analysis/dcf_model.py'
def get_similar_dfs(symbol: str, info: Dict[str, Any], n: int, no_filter: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/dcf_model.py#L468)

Description: Get dataframes for similar companies

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to create a dataframe for | None | False |
| into | Dict[str,Any] | The dictionary produced from the yfinance.info function | None | False |
| n | int | The number of similar companies to produce | None | False |
| no_filter | bool | True means that we do not filter based on market cap | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| List[str, pd.DataFrame] | A list of similar companies |

## Examples


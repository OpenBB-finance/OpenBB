---
title: finviz_peers
description: OpenBB SDK Function
---

# finviz_peers

## stocks_ca_finviz_compare_model.get_similar_companies

```python title='openbb_terminal/stocks/comparison_analysis/finviz_compare_model.py'
def get_similar_companies(symbol: str, compare_list: List[str]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finviz_compare_model.py#L25)

Description: Get similar companies from Finviz

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to find comparisons for | None | False |
| compare_list | List[str] | List of fields to compare, ["Sector", "Industry", "Country"] | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| List[str] | List of similar companies |

## Examples


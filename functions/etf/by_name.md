---
title: by_name
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# by_name

<Tabs>
<TabItem value="model" label="Model" default>

## etf_stockanalysis_model.get_etfs_by_name

```python title='openbb_terminal/etf/stockanalysis_model.py'
def get_etfs_by_name(name_to_search: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L134)

Description: Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name_to_search | str | ETF name to match | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with symbols and names |

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_stockanalysis_view.display_etf_by_name

```python title='openbb_terminal/etf/stockanalysis_view.py'
def display_etf_by_name(name: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_view.py#L99)

Description: Display ETFs matching search string. [Source: StockAnalysis]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | String being matched | None | False |
| limit | int | Limit of ETFs to display | None | False |
| export | str | Export to given file type | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
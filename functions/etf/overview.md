---
title: overview
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# overview

<Tabs>
<TabItem value="model" label="Model" default>

## etf_stockanalysis_model.get_etf_overview

```python title='openbb_terminal/etf/stockanalysis_model.py'
def get_etf_overview(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L50)

Description: Get overview data for selected etf

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| etf_symbol | str | Etf symbol to get overview for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of stock overview data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_stockanalysis_view.view_overview

```python title='openbb_terminal/etf/stockanalysis_view.py'
def view_overview(symbol: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_view.py#L17)

Description: Print etf overview information

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ETF symbols to display overview for | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
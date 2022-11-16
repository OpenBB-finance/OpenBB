---
title: holdings
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# holdings

<Tabs>
<TabItem value="model" label="Model" default>

## etf_stockanalysis_model.get_etf_holdings

```python title='openbb_terminal/etf/stockanalysis_model.py'
def get_etf_holdings(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L84)

Description: Get ETF holdings

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get holdings for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of holdings |

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_stockanalysis_view.view_holdings

```python title='openbb_terminal/etf/stockanalysis_view.py'
def view_holdings(symbol: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_view.py#L45)

Description: None

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ETF symbol to show holdings for | None | False |
| limit | int | Number of holdings to show | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
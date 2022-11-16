---
title: mover
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mover

<Tabs>
<TabItem value="model" label="Model" default>

## etf_disc_wsj_model.etf_movers

```python title='openbb_terminal/etf/discovery/wsj_model.py'
def etf_movers(sort_type: str, export: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/discovery/wsj_model.py#L15)

Description: Scrape data for top etf movers.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort_type | str | Data to get. Can be "gainers", "decliners" or "active" | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Datafame containing the name, price, change and the volume of the etf |

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_disc_wsj_view.show_top_mover

```python title='openbb_terminal/etf/discovery/wsj_view.py'
def show_top_mover(sort_type: str, limit: int, export: Any) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/discovery/wsj_view.py#L16)

Description: Show top ETF movers from wsj.com

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort_type | str | What to show. Either Gainers, Decliners or Activity | None | False |
| limit | int | Number of etfs to show | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
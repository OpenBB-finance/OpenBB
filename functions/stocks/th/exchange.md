---
title: exchange
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# exchange

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_th_bursa_model.get_bursa

```python title='openbb_terminal/stocks/tradinghours/bursa_model.py'
def get_bursa(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_model.py#L20)

Description: Get current exchange open hours.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Exchange symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Exchange info |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_th_bursa_view.display_exchange

```python title='openbb_terminal/stocks/tradinghours/bursa_view.py'
def display_exchange(symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_view.py#L15)

Description: Display current exchange trading hours.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Exchange symbol | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
---
title: dtvl
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# dtvl

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_llama_model.get_defi_protocol

```python title='openbb_terminal/cryptocurrency/defi/llama_model.py'
def get_defi_protocol(protocol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_model.py#L124)

Description: Returns information about historical tvl of a defi protocol.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Historical tvl |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_llama_view.display_historical_tvl

```python title='openbb_terminal/cryptocurrency/defi/llama_view.py'
def display_historical_tvl(dapps: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_view.py#L131)

Description: Displays historical TVL of different dApps

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dapps | str | dApps to search historical TVL. Should be split by , e.g.: anchor,sushiswap,pancakeswap | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
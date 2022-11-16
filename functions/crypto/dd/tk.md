---
title: tk
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# tk

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_tokenomics

```python title='openbb_terminal/decorators.py'
def get_tokenomics() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L272)

Description: Returns coin tokenomics

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check tokenomics | None | False |
| coingecko_id | str | ID from coingecko | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Metric Value tokenomics |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_tokenomics

```python title='openbb_terminal/decorators.py'
def display_tokenomics() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L374)

Description: Display coin tokenomics

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check tokenomics | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
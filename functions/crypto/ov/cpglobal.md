---
title: cpglobal
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpglobal

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_coinpaprika_model.get_global_market

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_model.py'
def get_global_market() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L72)

Description: Return data frame with most important global crypto statistics like:

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most important global crypto statistics
Metric, Value |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_coinpaprika_view.display_global_market

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_view.py'
def display_global_market(export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L74)

Description: Return data frame with most important global crypto statistics like:

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
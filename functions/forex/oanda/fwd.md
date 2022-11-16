---
title: fwd
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fwd

<Tabs>
<TabItem value="model" label="Model" default>

## forex_fxempire_model.get_forward_rates

```python title='openbb_terminal/forex/fxempire_model.py'
def get_forward_rates(to_symbol: str, from_symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/fxempire_model.py#L14)

Description: Gets forward rates from fxempire

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To currency | None | False |
| from_symbol | str | From currency | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | None |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_fxempire_view.display_forward_rates

```python title='openbb_terminal/forex/fxempire_view.py'
def display_forward_rates(to_symbol: str, from_symbol: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/fxempire_view.py#L14)

Description: Display forward rates for currency pairs

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To currency | None | False |
| from_symbol | str | From currency | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
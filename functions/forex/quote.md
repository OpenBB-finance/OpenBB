---
title: quote
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# quote

<Tabs>
<TabItem value="model" label="Model" default>

## forex_av_model.get_quote

```python title='openbb_terminal/forex/av_model.py'
def get_quote(to_symbol: str, from_symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/av_model.py#L56)

Description: Get current exchange rate quote from alpha vantage.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To forex symbol | None | False |
| from_symbol | str | From forex symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary of exchange rate |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_av_view.display_quote

```python title='openbb_terminal/decorators.py'
def display_quote() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L18)

Description: Display current forex pair exchange rate.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To symbol | None | False |
| from_symbol | str | From forex symbol | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
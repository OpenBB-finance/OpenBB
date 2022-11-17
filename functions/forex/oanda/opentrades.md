---
title: opentrades
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# opentrades

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.open_trades_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def open_trades_request(accountID: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L470)

Description: Request open trades data.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | cfg.OANDA_ACCOUNT | True |

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Open trades data or False |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.get_open_trades

```python title='openbb_terminal/decorators.py'
def get_open_trades() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L260)

Description: View open trades.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
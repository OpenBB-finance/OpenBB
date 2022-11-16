---
title: pending
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pending

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.pending_orders_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def pending_orders_request(accountID: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L421)

Description: Request information on pending orders.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | cfg.OANDA_ACCOUNT | True |

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Pending orders data or False |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.get_pending_orders

```python title='openbb_terminal/decorators.py'
def get_pending_orders() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L240)

Description: Get information about pending orders.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
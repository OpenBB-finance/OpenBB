---
title: listorders
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# listorders

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.order_history_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def order_history_request(order_state: str, order_count: int, accountID: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L225)

Description: Request the orders list from Oanda.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| order_state | str | Filter orders by a specific state ("PENDING", "CANCELLED", etc.) | None | False |
| order_count | int | Limit the number of orders to retrieve | None | False |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | cfg.OANDA_ACCOUNT | True |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.list_orders

```python title='openbb_terminal/decorators.py'
def list_orders() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L156)

Description: List order history.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| order_state | str | Filter orders by a specific state ("PENDING", "CANCELLED", etc.) | None | False |
| order_count | int | Limit the number of orders to retrieve | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
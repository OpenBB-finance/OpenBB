---
title: cancel
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cancel

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.cancel_pending_order_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def cancel_pending_order_request(orderID: str, accountID: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L346)

Description: Request cancellation of a pending order.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| orderID | str | The pending order ID to cancel. | None | False |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | cfg.OANDA_ACCOUNT | True |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.cancel_pending_order

```python title='openbb_terminal/decorators.py'
def cancel_pending_order() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L202)

Description: Cancel a Pending Order.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| orderID | str | The pending order ID to cancel. | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
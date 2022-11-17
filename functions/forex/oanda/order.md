---
title: order
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# order

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.create_order_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def create_order_request(price: int, units: int, instrument: Optional[str], accountID: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L270)

Description: Request creation of buy/sell trade order.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | Union[str, None] | The loaded currency pair, by default None | None | False |
| price | int | The price to set for the limit order. | None | False |
| units | int | The number of units to place in the order request. | None | False |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | cfg.OANDA_ACCOUNT | True |

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Orders data or False |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.create_order

```python title='openbb_terminal/decorators.py'
def create_order() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L178)

Description: Create a buy/sell order.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| instrument | str | The loaded currency pair | None | False |
| price | int | The price to set for the limit order. | None | False |
| units | int | The number of units to place in the order request. | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
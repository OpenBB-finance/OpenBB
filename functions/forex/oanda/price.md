---
title: price
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# price

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.fx_price_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def fx_price_request(accountID: str, instrument: Optional[str]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L36)

Description: Request price for a forex pair.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | cfg.OANDA_ACCOUNT | True |
| instrument | Union[str, None] | The loaded currency pair, by default None | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Union[Dict[str, str], bool] | The currency pair price or False |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.get_fx_price

```python title='openbb_terminal/decorators.py'
def get_fx_price() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L40)

Description: View price for loaded currency pair.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID | None | False |
| instrument | Union[str, None] | Instrument code or None | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
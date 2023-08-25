---
title: order
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# order

<Tabs>
<TabItem value="model" label="Model" default>

Request creation of buy/sell trade order.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L270)]

```python
openbb.forex.oanda.order(price: int = 0, units: int = 0, instrument: Optional[str] = None, accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | Union[str, None] | The loaded currency pair, by default None | None | True |
| price | int | The price to set for the limit order. | 0 | True |
| units | int | The number of units to place in the order request. | 0 | True |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Orders data or False |
---



</TabItem>
<TabItem value="view" label="Chart">

Create a buy/sell order.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L174)]

```python
openbb.forex.oanda.order_chart(accountID: str, instrument: str = "", price: int = 0, units: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| instrument | str | The loaded currency pair |  | True |
| price | int | The price to set for the limit order. | 0 | True |
| units | int | The number of units to place in the order request. | 0 | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
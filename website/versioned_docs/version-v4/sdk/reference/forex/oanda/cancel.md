---
title: cancel
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cancel

<Tabs>
<TabItem value="model" label="Model" default>

Request cancellation of a pending order.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L346)]

```python
openbb.forex.oanda.cancel(orderID: str, accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| orderID | str | The pending order ID to cancel. | None | False |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

This function does not return anything

---



</TabItem>
<TabItem value="view" label="Chart">

Cancel a Pending Order.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L197)]

```python
openbb.forex.oanda.cancel_chart(accountID: str, orderID: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| orderID | str | The pending order ID to cancel. |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
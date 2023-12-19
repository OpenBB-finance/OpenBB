---
title: cancel
description: This page describes two methods to cancel a pending order in OpenBB's
  forex trading system using Oanda. It includes Python functions to cancel an order
  by ID from either the model or chart view.
keywords:
- cancel pending order
- Oanda
- forex
- python function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.oanda.cancel - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

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

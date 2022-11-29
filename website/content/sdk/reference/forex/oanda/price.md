---
title: price
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# price

<Tabs>
<TabItem value="model" label="Model" default>

Request price for a forex pair.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L36)]

```python
openbb.forex.oanda.price(accountID: str = "REPLACE_ME", instrument: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |
| instrument | Union[str, None] | The loaded currency pair, by default None | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[Dict[str, str], bool] | The currency pair price or False |
---



</TabItem>
<TabItem value="view" label="Chart">

View price for loaded currency pair.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L40)]

```python
openbb.forex.oanda.price_chart(account: str, instrument: Optional[str] = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID | None | True |
| instrument | Union[str, None] | Instrument code or None |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
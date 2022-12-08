---
title: close
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# close

<Tabs>
<TabItem value="model" label="Model" default>

Close a trade.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L526)]

```python
openbb.forex.oanda.close(orderID: str, units: Optional[int] = 0, accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| orderID | str | ID of the order to close | None | False |
| units | Union[int, None] | Number of units to close. If empty default to all. | 0 | True |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Close trades data or False |
---



</TabItem>
<TabItem value="view" label="Chart">

Close a trade.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L271)]

```python
openbb.forex.oanda.close_chart(accountID: str, orderID: str = "", units: Optional[int] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| orderID | str | ID of the order to close |  | True |
| units | Union[int, None] | Number of units to close. If empty default to all. | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
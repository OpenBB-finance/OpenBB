---
title: pending
description: This page explains how to get information on pending orders using the
  OpenBB Terminal. The documentation includes specific source code for the Forex market
  with OANDA, detailing parameters and returns including the AccountID. The page also
  provides a link to the relevant source code on GitHub.
keywords:
- Forex
- OANDA
- AccountID
- Pending orders
- OpenBB Forex OANDA Pending
- Source Code
- Pending chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.oanda.pending - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Request information on pending orders.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L421)]

```python
openbb.forex.oanda.pending(accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Pending orders data or False |
---

</TabItem>
<TabItem value="view" label="Chart">

Get information about pending orders.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L233)]

```python
openbb.forex.oanda.pending_chart(accountID: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

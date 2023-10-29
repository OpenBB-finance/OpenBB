---
title: openpositions
description: This documentation page provides details about the OpenBB 'open positions'
  function in forex trading with Oanda. Learn about the parameters including account
  ID and review the source code in Python.
keywords:
- open positions
- forex
- Oanda
- account ID
- function parameters
- python code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.oanda.openpositions - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Request information on open positions.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L378)]

```python
openbb.forex.oanda.openpositions(accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

This function does not return anything

---

</TabItem>
<TabItem value="view" label="Chart">

Get information about open positions.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L216)]

```python
openbb.forex.oanda.openpositions_chart(accountID: str)
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

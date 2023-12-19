---
title: closed
description: The page provides information on the two functions `openbb.stocks.th.closed()`
  and `openbb.stocks.th.closed_chart()`. The first function is for getting currently
  closed exchanges which returns a pd.DataFrame. The second function is for displaying
  closed exchanges but does not return anything.
keywords:
- closed exchanges
- Stocks
- Trading hours
- openbb.stocks.th.closed()
- openbb.stocks.th.closed_chart()
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.th.closed - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get closed exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_model.py#L76)]

```python
openbb.stocks.th.closed()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Currently closed exchanges |
---

</TabItem>
<TabItem value="view" label="Chart">

Display closed exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_view.py#L64)]

```python
openbb.stocks.th.closed_chart()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

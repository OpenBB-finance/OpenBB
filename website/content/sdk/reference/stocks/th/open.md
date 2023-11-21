---
title: open
description: Documentation page offering extensive details on how 'open' feature functions
  in OpenBB finance and their source code. This feature showcases open exchanges and
  how to display them.
keywords:
- Finance Software
- Open
- Exchanges
- Trading hours
- Documentation
- Source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.th.open - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get open exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_model.py#L54)]

```python
openbb.stocks.th.open()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Currently open exchanges |
---

</TabItem>
<TabItem value="view" label="Chart">

Display open exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_view.py#L44)]

```python
openbb.stocks.th.open_chart()
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

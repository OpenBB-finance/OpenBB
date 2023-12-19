---
title: all
description: Documentation detail of OpenBB's all exchanges and chart display functions.
  OpenBB provides functionalities to fetch all available exchanges and display them
  in a chart format.
keywords:
- OpenBB Documentation
- OpenBB Exchanges API
- OpenBB Chart Display
- Python scripts
- API Documentation
- Open source financial tools
- OpenBB Source Code
- Stock Exchange Data
- Extracting Exchange Data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.th.all - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get all exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_model.py#L98)]

```python
openbb.stocks.th.all()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All available exchanges |
---

</TabItem>
<TabItem value="view" label="Chart">

Display all exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_view.py#L84)]

```python
openbb.stocks.th.all_chart()
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
